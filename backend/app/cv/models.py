from django.conf import settings
from django.db import models


class CV(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cvs',
    )
    file = models.FileField(upload_to='cvs/')
    extracted_name = models.TextField(blank=True, default='')
    extracted_skills = models.JSONField(blank=True, default=list)
    extracted_experience = models.JSONField(blank=True, default=list)
    extracted_education = models.JSONField(blank=True, default=list)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cvs'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'CV #{self.pk} – {self.user}'
