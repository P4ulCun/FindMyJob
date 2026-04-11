from rest_framework import serializers
from .models import CV


class CVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = [
            'id',
            'file',
            'extracted_name',
            'extracted_skills',
            'extracted_experience',
            'extracted_education',
            'uploaded_at',
        ]
        read_only_fields = ['id', 'file', 'uploaded_at']
