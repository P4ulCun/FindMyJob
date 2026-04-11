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
            'source_adzuna',
            'source_remoteok',
            'source_arbeitnow',
            'source_hn',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        instance = self.instance
        source_fields = JobPreference.SOURCE_FIELDS

        # Build the final state: start from instance (if updating), overlay with incoming attrs
        values = {}
        for f in source_fields:
            if f in attrs:
                values[f] = attrs[f]
            elif instance is not None:
                values[f] = getattr(instance, f)
            else:
                values[f] = True  # model default

        if not any(values.values()):
            raise serializers.ValidationError(
                'At least one job source must be enabled.'
            )
        return attrs
