import argparse
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.signing import Signer

from users.models import User
from preferences.models import JobPreference
from jobs.ai_agent import JobScoringAgent
from jobs.job_fetcher import fetch_arbeitnow, fetch_adzuna, fetch_hn_hiring, fetch_remoteok


class Command(BaseCommand):
    help = 'Sends periodic email digest with top job matches'

    def add_arguments(self, parser):
        parser.add_argument(
            '--frequency',
            type=str,
            choices=['daily', 'weekly'],
            default='daily',
            help='Frequency of the digest to send (daily or weekly)',
        )

    def handle(self, *args, **options):
        frequency = options['frequency']
        self.stdout.write(f"Sending {frequency} job digests...")

        users_with_prefs = User.objects.filter(
            job_preference__digest_frequency=frequency
        ).select_related('job_preference')

        if not users_with_prefs.exists():
            self.stdout.write("No users found with this frequency setting.")
            return

        signer = Signer()
        agent = JobScoringAgent()
        base_api_url = getattr(settings, 'BASE_API_URL', 'http://localhost:8000')

        count = 0
        for user in users_with_prefs:
            prefs = user.job_preference
            
            # Fetch CV data
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
                self.stdout.write(f"No jobs fetched for user {user.email}.")
                continue

            results = []
            for job in all_jobs:
                scored = agent.score_job(job, cv_data)
                results.append({
                    **job,
                    'score': scored.get('score', 0),
                    'summary': scored.get('summary', ''),
                })

            results.sort(key=lambda x: x['score'], reverse=True)
            top_jobs = results[:5]

            # Prepare Unsubscribe Link
            token = signer.sign(user.id)
            unsubscribe_link = f"{base_api_url}/api/preferences/unsubscribe/{token}/"

            # Render Email
            context = {
                'user': user,
                'jobs': top_jobs,
                'unsubscribe_link': unsubscribe_link,
            }
            html_message = render_to_string('emails/job_digest.html', context)
            plain_message = strip_tags(html_message)

            send_mail(
                subject=f'Your {frequency.capitalize()} Job Matches Digest',
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@findmyjob.local'),
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            count += 1
            self.stdout.write(f"Sent email to {user.email} with {len(top_jobs)} matches.")

        self.stdout.write(self.style.SUCCESS(f"Successfully sent {count} {frequency} digests."))
