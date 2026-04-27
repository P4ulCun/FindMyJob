from rest_framework import serializers
from .models import CV, TailoredCV, CoverLetter


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


class TailoredCVSerializer(serializers.ModelSerializer):
    class Meta:
        model = TailoredCV
        fields = [
            'id',
            'original_cv',
            'job_title',
            'job_company',
            'job_description',
            'tailored_skills',
            'tailored_experience',
            'tailored_education',
            'created_at',
        ]
        read_only_fields = fields


class CoverLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverLetter
        fields = [
            'id',
            'original_cv',
            'job_title',
            'job_company',
            'job_description',
            'body',
            'created_at',
        ]
        read_only_fields = ['id', 'original_cv', 'job_title', 'job_company',
                            'job_description', 'created_at']

