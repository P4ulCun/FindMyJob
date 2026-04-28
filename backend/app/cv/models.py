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


class TailoredCV(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tailored_cvs',
    )
    original_cv = models.ForeignKey(
        CV,
        on_delete=models.CASCADE,
        related_name='tailored_versions',
    )
    job_title = models.CharField(max_length=255)
    job_company = models.CharField(max_length=255, blank=True, default='')
    job_description = models.TextField()
    original_skills = models.JSONField(default=list)
    original_experience = models.JSONField(default=list)
    original_education = models.JSONField(default=list)
    change_set = models.JSONField(default=dict)
    tailored_skills = models.JSONField(default=list)
    tailored_experience = models.JSONField(default=list)
    tailored_education = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tailored_cvs'
        ordering = ['-created_at']

    def __str__(self):
        return f'TailoredCV #{self.pk} for "{self.job_title}" – {self.user}'


class CoverLetter(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cover_letters',
    )
    original_cv = models.ForeignKey(
        CV,
        on_delete=models.CASCADE,
        related_name='cover_letters',
    )
    job_title = models.CharField(max_length=255)
    job_company = models.CharField(max_length=255, blank=True, default='')
    job_description = models.TextField()
    body = models.TextField(help_text='Generated cover letter text (editable by user)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cover_letters'
        ordering = ['-created_at']

    def __str__(self):
        return f'CoverLetter #{self.pk} for "{self.job_title}" – {self.user}'
