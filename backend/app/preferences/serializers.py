from rest_framework import serializers

from .models import JobPreference


class JobPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPreference
        fields = [
            'id',
            'job_title',
            'location',
            'work_type',
            'seniority',
        ]
        read_only_fields = ['id']
