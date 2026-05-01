from django.conf import settings
from django.db import models


class JobInteraction(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('saved', 'Saved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_interactions'
    )
    job_url = models.URLField(max_length=1000)
    job_title = models.CharField(max_length=500)
    job_company = models.CharField(max_length=500, blank=True, default='')
    job_location = models.CharField(max_length=500, blank=True, default='')
    job_source = models.CharField(max_length=100, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'job_interactions'
        unique_together = ('user', 'job_url')

    def __str__(self):
        return f"{self.user.email} - {self.job_title} - {self.status}"
