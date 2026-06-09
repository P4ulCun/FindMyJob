import json
import pytest
import requests

from jobs.ai_agent import JobScoringAgent

JOB = {
    "title": "Senior Python Developer",
    "company": "Acme",
    "location": "Remote",
    "description": "We need Django, DRF and Postgres expertise.",
}

CV_DATA = {
    "skills": ["Python", "Django", "DRF"],
    "experience": ["3 ani backend la startup"],
    "education": ["Licență Informatică"],
}


def _mock_response(content: str, status_code: int = 200):
    mock = pytest.importorskip("unittest.mock").MagicMock()
    mock.status_code = status_code
    mock.json.return_value = {
        "choices": [{"message": {"content": content}}]
    }
    return mock


class TestJobScoringAgentEvals:
    def test_raspuns_json_valid_returneaza_scor_si_summary(self, mocker):
        payload = json.dumps({"score": 85, "summary": "Potrivire bună pe backend."})
        mocker.patch("requests.post", return_value=_mock_response(payload))

        result = JobScoringAgent().score_job(JOB, CV_DATA)

        assert result["score"] == 85
        assert "backend" in result["summary"].lower()

    def test_json_in_markdown_fence_este_parsat_corect(self, mocker):
        fenced = "```json\n{\"score\": 72, \"summary\": \"Match rezonabil.\"}\n```"
        mocker.patch("requests.post", return_value=_mock_response(fenced))

        result = JobScoringAgent().score_job(JOB, CV_DATA)

        assert result["score"] == 72
        assert result["summary"] == "Match rezonabil."

    def test_json_malformat_foloseste_fallback_regex(self, mocker):
        broken = 'Iată răspunsul: {"score": 91, "summary": "Excelent match'
        mocker.patch("requests.post", return_value=_mock_response(broken))

        result = JobScoringAgent().score_job(JOB, CV_DATA)

        assert result["score"] == 91

    def test_eroare_retea_returneaza_scor_zero(self, mocker):
        mocker.patch("requests.post", side_effect=requests.exceptions.ConnectionError("down"))

        result = JobScoringAgent().score_job(JOB, CV_DATA)

        assert result["score"] == 0
        assert "unavailable" in result["summary"].lower()

    def test_scorul_este_intreg_intre_0_si_100(self, mocker):
        payload = json.dumps({"score": 55, "summary": "Potrivire medie."})
        mocker.patch("requests.post", return_value=_mock_response(payload))

        result = JobScoringAgent().score_job(JOB, CV_DATA)

        assert isinstance(result["score"], int)
        assert 0 <= result["score"] <= 100


CV_REAL = {
    "name": "Ana Pop",
    "skills": ["Python", "Django", "REST APIs", "PostgreSQL"],
    "experience": ["Backend developer la Acme — 3 ani"],
    "education": ["Licență Informatică, UBB"],
}

JOB_PERFECT_MATCH = {
    "title": "Python Backend Engineer",
    "company": "TechCorp",
    "description": "We are looking for a Python developer with Django and PostgreSQL experience. REST APIs are a must.",
}

JOB_POOR_MATCH = {
    "title": "Frontend React Developer",
    "company": "WebUI",
    "description": "Looking for a React developer with deep CSS and UI/UX knowledge. No backend work.",
}


@pytest.mark.llm_eval
class TestJobScoringAgentAntiHallucination:
    def test_scor_mare_pentru_match_perfect(self):
        result = JobScoringAgent().score_job(JOB_PERFECT_MATCH, CV_REAL)
        assert isinstance(result["score"], int)
        assert result["score"] >= 70, f"Expected high score, got {result['score']}"

    def test_scor_mic_pentru_match_slab(self):
        result = JobScoringAgent().score_job(JOB_POOR_MATCH, CV_REAL)
        assert isinstance(result["score"], int)
        assert result["score"] <= 50, f"Expected low score, got {result['score']}"

    def test_summary_fara_markdown(self):
        result = JobScoringAgent().score_job(JOB_PERFECT_MATCH, CV_REAL)
        assert "```" not in result["summary"], "Summary should not contain markdown fences"
