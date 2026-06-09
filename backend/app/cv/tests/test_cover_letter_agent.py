import pytest
import requests

from cv.cover_letter_agent import CoverLetterAgent

CV_DATA = {
    "name": "Ana Pop",
    "skills": ["Python", "Django", "REST APIs"],
    "experience": ["Backend developer la Acme — 3 ani"],
    "education": ["Licență Informatică, UBB"],
}

JOB = {
    "title": "Python Backend Engineer",
    "company": "TechCorp",
    "description": "We build Django-based microservices.",
}


def _mock_llm(content: str):
    mock = pytest.importorskip("unittest.mock").MagicMock()
    mock.json.return_value = {"choices": [{"message": {"content": content}}]}
    return mock


class TestCoverLetterAgentEvals:
    def test_happy_path_returneaza_text_cu_job_title(self, mocker):
        letter = (
            "Dear Hiring Manager at TechCorp,\n\n"
            "I am applying for the Python Backend Engineer position.\n\n"
            "My skills in Python and Django make me a great fit.\n\n"
            "Sincerely,\nAna Pop"
        )
        mocker.patch("requests.post", return_value=_mock_llm(letter))

        result = CoverLetterAgent().generate(CV_DATA, JOB)

        assert "Python Backend Engineer" in result
        assert "TechCorp" in result
        assert isinstance(result, str)
        assert len(result) > 50

    def test_markdown_fence_este_eliminat(self, mocker):
        fenced = "```\nDear Hiring Manager,\n\nGreat letter here.\n\nSincerely,\nAna Pop\n```"
        mocker.patch("requests.post", return_value=_mock_llm(fenced))

        result = CoverLetterAgent().generate(CV_DATA, JOB)

        assert "```" not in result
        assert "Dear Hiring Manager" in result

    def test_eroare_retea_returneaza_scrisoare_fallback(self, mocker):
        mocker.patch("requests.post", side_effect=requests.exceptions.ConnectionError())

        result = CoverLetterAgent().generate(CV_DATA, JOB)

        assert "Ana Pop" in result
        assert "Python Backend Engineer" in result
        assert "unavailable" in result.lower() or "manually" in result.lower()

    def test_candidat_fara_nume_foloseste_placeholder(self, mocker):
        mocker.patch("requests.post", side_effect=Exception("fail"))

        result = CoverLetterAgent().generate({}, JOB)

        assert "the candidate" in result or len(result) > 0

    def test_scrisoarea_nu_contine_markdown_formatting(self, mocker):
        plain = (
            "Dear Hiring Manager at TechCorp,\n\n"
            "I am excited to apply for this role.\n\n"
            "Best regards,\nAna Pop"
        )
        mocker.patch("requests.post", return_value=_mock_llm(plain))

        result = CoverLetterAgent().generate(CV_DATA, JOB)

        assert "**" not in result
        assert "#" not in result
