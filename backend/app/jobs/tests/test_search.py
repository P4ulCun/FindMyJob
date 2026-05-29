import pytest
from django.urls import reverse

from preferences.models import JobPreference
from cv.models import CV

pytestmark = pytest.mark.django_db

FAKE_JOB = {
    "title": "Senior Python Developer",
    "company": "Acme",
    "location": "Remote",
    "description": "Django, DRF, Postgres",
    "url": "https://example.com/jobs/1",
    "source": "RemoteOK",
    "tags": ["python", "django"],
}


@pytest.fixture
def user_ready_to_search(user):
    """User cu preferințe + CV, ca să treacă validările din search_jobs."""
    JobPreference.objects.create(user=user, job_title="Python Developer")
    CV.objects.create(
        user=user,
        extracted_skills=["Python", "Django"],
        extracted_experience=["3 ani backend"],
        extracted_education=["Licență Informatică"],
    )
    return user


def test_search_jobs_mock_llm_si_fetchere(
    mocker, auth_client, user_ready_to_search
):
    # 1. Mock-uim sursele externe — niciun apel real către RemoteOK/Arbeitnow/HN
    mocker.patch("jobs.views.fetch_remoteok", return_value=[FAKE_JOB])
    mocker.patch("jobs.views.fetch_arbeitnow", return_value=[])
    mocker.patch("jobs.views.fetch_hn_hiring", return_value=[])

    # 2. Mock-uim agentul AI — simulăm răspunsul LLM-ului, fără rețea
    mock_agent = mocker.patch("jobs.views.JobScoringAgent").return_value
    mock_agent.score_job.return_value = {
        "score": 88,
        "summary": "Potrivire foarte bună pe skill-urile de backend.",
    }

    resp = auth_client.post(reverse("search_jobs"))

    assert resp.status_code == 200
    jobs = resp.data["jobs"]
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Senior Python Developer"
    assert jobs[0]["score"] == 88
    mock_agent.score_job.assert_called_once()


def test_search_jobs_fara_preferinte_da_400(auth_client, user):
    # user fără JobPreference -> view-ul refuză înainte de orice apel AI
    assert auth_client.post(reverse("search_jobs")).status_code == 400