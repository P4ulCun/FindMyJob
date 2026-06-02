import pytest
from django.urls import reverse
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

from users.models import User
from cv.models import CV, TailoredCV


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def sample_cv(db, user):
    file_content = b'%PDF-1.4 sample content'
    return CV.objects.create(
        user=user,
        file=SimpleUploadedFile('test.pdf', file_content, content_type='application/pdf'),
        extracted_name='John Doe',
        extracted_skills=['Python', 'Django'],
        extracted_experience=['Dev at X'],
        extracted_education=['BS CS']
    )


@pytest.fixture
def tailored_cv(db, user, sample_cv):
    return TailoredCV.objects.create(
        user=user,
        original_cv=sample_cv,
        job_title='Software Engineer',
        job_company='Tech Corp',
        job_description='We need Python and Django.',
        original_skills=sample_cv.extracted_skills,
        original_experience=sample_cv.extracted_experience,
        original_education=sample_cv.extracted_education,
        change_set={},
        tailored_skills=['Python', 'Django'],
        tailored_experience=['Dev at X'],
        tailored_education=['BS CS']
    )


@pytest.mark.django_db
def test_download_tailored_cv(auth_client, tailored_cv):
    url = reverse('cv-tailored-download', kwargs={'pk': tailored_cv.pk})
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/pdf'
    assert 'attachment;' in response['Content-Disposition']
    assert 'Tailored_CV_Software_Engineer.pdf' in response['Content-Disposition']

    # Check that the response content starts with PDF signature
    assert response.content.startswith(b'%PDF-')


@pytest.mark.django_db
def test_download_tailored_cv_not_found(auth_client):
    url = reverse('cv-tailored-download', kwargs={'pk': 9999})
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
