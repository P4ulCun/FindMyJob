from rest_framework import serializers
from .models import CV, TailoredCV, CoverLetter


def _effective_section_items(change_set, section_name, fallback_items):
    section_changes = change_set.get(section_name, []) if isinstance(change_set, dict) else []
    if not section_changes:
        return fallback_items

    items = []
    for change in section_changes:
        if not isinstance(change, dict):
            continue
        status = change.get('status', 'pending')
        items.append(change.get('before') if status == 'rejected' else change.get('after'))

    return items or fallback_items


def _review_summary(change_set):
    counts = {'pending': 0, 'accepted': 0, 'rejected': 0, 'total': 0}
    if not isinstance(change_set, dict):
        return counts

    for section_name in ('skills', 'experience', 'education'):
        for change in change_set.get(section_name, []):
            if not isinstance(change, dict):
                continue
            status = change.get('status', 'pending')
            if status not in counts:
                continue
            counts[status] += 1
            counts['total'] += 1

    return counts


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
    tailored_skills = serializers.SerializerMethodField()
    tailored_experience = serializers.SerializerMethodField()
    tailored_education = serializers.SerializerMethodField()
    review_summary = serializers.SerializerMethodField()

    class Meta:
        model = TailoredCV
        fields = [
            'id',
            'original_cv',
            'job_title',
            'job_company',
            'job_description',
            'original_skills',
            'original_experience',
            'original_education',
            'change_set',
            'tailored_skills',
            'tailored_experience',
            'tailored_education',
            'review_summary',
            'created_at',
        ]
        read_only_fields = fields

    def get_tailored_skills(self, obj):
        return _effective_section_items(obj.change_set, 'skills', obj.tailored_skills)

    def get_tailored_experience(self, obj):
        return _effective_section_items(obj.change_set, 'experience', obj.tailored_experience)

    def get_tailored_education(self, obj):
        return _effective_section_items(obj.change_set, 'education', obj.tailored_education)

    def get_review_summary(self, obj):
        return _review_summary(obj.change_set)


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

