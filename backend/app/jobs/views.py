import hashlib
import os
from datetime import timedelta

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from preferences.models import JobPreference
from .ai_agent import JobScoringAgent
from .job_fetcher import fetch_arbeitnow, fetch_hn_hiring, fetch_remoteok
from .models import CachedJobSearch, JobInteraction

CACHE_TTL_HOURS = int(os.environ.get('JOB_CACHE_TTL_HOURS', 6))


def _source_cache_key(job_title: str, location: str, source: str) -> str:
    raw = f"{job_title.lower().strip()}|{location.lower().strip()}|{source}"
    return hashlib.md5(raw.encode()).hexdigest()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_jobs(request):
    user = request.user

    try:
        prefs = user.job_preference
    except JobPreference.DoesNotExist:
        return Response(
            {'error': 'Please set your job preferences first.'},
            status=400,
        )

    cv = user.cvs.first()
    if not cv:
        return Response(
            {'error': 'Please upload a CV before searching for jobs.'},
            status=400,
        )

    cv_data = {
        'skills': cv.extracted_skills or [],
        'experience': cv.extracted_experience or [],
        'education': cv.extracted_education or [],
    }

    job_title = prefs.job_title
    location = prefs.location

    enabled_sources = {
        'remoteok': prefs.source_remoteok,
        'arbeitnow': prefs.source_arbeitnow,
        'hn': prefs.source_hn,
    }

    all_jobs = []
    for source_name, enabled in enabled_sources.items():
        if not enabled:
            continue

        key = _source_cache_key(job_title, location, source_name)
        cached = CachedJobSearch.objects.filter(cache_key=key).first()

        if cached and cached.is_valid():
            all_jobs.extend(cached.results)
            continue

        if source_name == 'remoteok':
            jobs = fetch_remoteok(job_title)
        elif source_name == 'arbeitnow':
            jobs = fetch_arbeitnow(job_title, location)
        elif source_name == 'hn':
            jobs = fetch_hn_hiring(job_title)
        else:
            jobs = []

        if jobs:
            CachedJobSearch.objects.update_or_create(
                cache_key=key,
                defaults={
                    'job_title': job_title,
                    'location': location,
                    'results': jobs,
                    'expires_at': timezone.now() + timedelta(hours=CACHE_TTL_HOURS),
                },
            )
        all_jobs.extend(jobs)

    if not all_jobs:
        return Response({
            'jobs': [],
            'message': 'No jobs found. Try adjusting your preferences.',
        })

    agent = JobScoringAgent()

    interactions = JobInteraction.objects.filter(user=user)
    interaction_map = {i.job_url: i.status for i in interactions}

    results = []
    for job in all_jobs[:10]:
        scored = agent.score_job(job, cv_data)
        job_url = job.get('url', '')
        status = interaction_map.get(job_url)
        results.append({
            **job,
            'score': scored.get('score', 0),
            'summary': scored.get('summary', ''),
            'status': status,
        })

    results.sort(key=lambda x: x['score'], reverse=True)

    return Response({'jobs': results})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def job_interactions(request):
    user = request.user

    if request.method == 'GET':
        interactions = JobInteraction.objects.filter(user=user).order_by('-updated_at')
        data = [
            {
                'id': i.id,
                'job_url': i.job_url,
                'job_title': i.job_title,
                'job_company': i.job_company,
                'job_location': i.job_location,
                'job_source': i.job_source,
                'status': i.status,
                'updated_at': i.updated_at.isoformat(),
            }
            for i in interactions
        ]
        return Response({'interactions': data})

    elif request.method == 'POST':
        job_url = request.data.get('job_url')
        status = request.data.get('status')

        if not job_url or not status:
            return Response(
                {'error': 'job_url and status are required.'},
                status=400
            )

        if status not in dict(JobInteraction.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status.'},
                status=400
            )

        interaction, created = JobInteraction.objects.update_or_create(
            user=user,
            job_url=job_url,
            defaults={
                'job_title': request.data.get('job_title', ''),
                'job_company': request.data.get('job_company', ''),
                'job_location': request.data.get('job_location', ''),
                'job_source': request.data.get('job_source', ''),
                'status': status,
            }
        )

        return Response({
            'message': 'Interaction saved.',
            'interaction': {
                'id': interaction.id,
                'job_url': interaction.job_url,
                'status': interaction.status,
            }
        })
