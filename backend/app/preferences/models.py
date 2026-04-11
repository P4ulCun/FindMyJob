from django.conf import settings
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

    class Meta:
        db_table = 'job_preferences'

    def __str__(self):
        return f'JobPreference – {self.user}'
