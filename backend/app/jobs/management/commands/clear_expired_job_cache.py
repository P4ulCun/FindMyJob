from django.core.management.base import BaseCommand
from django.utils import timezone

from jobs.models import CachedJobSearch


class Command(BaseCommand):
    help = 'Delete expired job search cache entries'

    def handle(self, *args, **options):
        deleted, _ = CachedJobSearch.objects.filter(expires_at__lt=timezone.now()).delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} expired cache entries.'))
