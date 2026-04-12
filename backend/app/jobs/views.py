from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from preferences.models import JobPreference
from .ai_agent import JobScoringAgent
from .job_fetcher import fetch_arbeitnow, fetch_adzuna, fetch_hn_hiring, fetch_remoteok


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
    results = []
    for job in all_jobs:
        scored = agent.score_job(job, cv_data)
        results.append({
            **job,
            'score': scored.get('score', 0),
            'summary': scored.get('summary', ''),
        })

    results.sort(key=lambda x: x['score'], reverse=True)

    return Response({'jobs': results})
