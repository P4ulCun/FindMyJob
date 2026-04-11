from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class JobPreference(models.Model):
    WORK_TYPE_CHOICES = [
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
        ('on-site', 'On-site'),
    ]

    SENIORITY_CHOICES = [
        ('junior', 'Junior'),
        ('mid', 'Mid'),
        ('senior', 'Senior'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_preference',
    )
    job_title = models.CharField(max_length=255, blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')
    work_type = models.CharField(
        max_length=10,
        choices=WORK_TYPE_CHOICES,
        blank=True,
        default='',
    )
    seniority = models.CharField(
        max_length=10,
        choices=SENIORITY_CHOICES,
        blank=True,
        default='',
    )

    # Job sources
    source_adzuna = models.BooleanField(default=True)
    source_remoteok = models.BooleanField(default=True)
    source_arbeitnow = models.BooleanField(default=True)
    source_hn = models.BooleanField(default=True)

    SOURCE_FIELDS = [
        'source_adzuna',
        'source_remoteok',
        'source_arbeitnow',
        'source_hn',
    ]

    def clean(self):
        super().clean()
        if not any(getattr(self, f) for f in self.SOURCE_FIELDS):
            raise ValidationError(
                'At least one job source must be enabled.'
            )

    class Meta:
        db_table = 'job_preferences'

    def __str__(self):
        return f'JobPreference – {self.user}'
