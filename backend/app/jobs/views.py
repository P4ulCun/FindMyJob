from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from preferences.models import JobPreference
from .ai_agent import JobScoringAgent
from .job_fetcher import fetch_arbeitnow, fetch_adzuna, fetch_hn_hiring, fetch_remoteok
from .models import JobInteraction


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
    cv_data = {}
    if cv:
        cv_data = {
            'skills': cv.extracted_skills or [],
            'experience': cv.extracted_experience or [],
            'education': cv.extracted_education or [],
        }

    job_title = prefs.job_title
    location = prefs.location

    all_jobs = []
    if prefs.source_remoteok:
        all_jobs.extend(fetch_remoteok(job_title))
    if prefs.source_arbeitnow:
        all_jobs.extend(fetch_arbeitnow(job_title, location))
    if prefs.source_hn:
        all_jobs.extend(fetch_hn_hiring(job_title))
    if prefs.source_adzuna:
        all_jobs.extend(fetch_adzuna(job_title, location))

    if not all_jobs:
        return Response({
            'jobs': [],
            'message': 'No jobs found. Try adjusting your preferences.',
        })

    agent = JobScoringAgent()

    interactions = JobInteraction.objects.filter(user=user)
    interaction_map = {i.job_url: i.status for i in interactions}

    results = []
    for job in all_jobs:
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
