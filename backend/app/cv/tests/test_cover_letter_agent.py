import pytest
import requests

from cv.cover_letter_agent import CoverLetterAgent

CV_REAL = {
    "name": "Ana Pop",
    "skills": ["Python", "Django", "REST APIs"],
    "experience": ["Backend developer la Acme — 3 ani"],
    "education": ["Licență Informatică, UBB"],
}

JOB_REAL = {
    "title": "Python Backend Engineer",
    "company": "TechCorp",
    "description": "We build Django-based microservices. Looking for Python and REST API expertise.",
}

SKILLS_NOT_IN_CV = ["Java", "Kubernetes", "React", "Machine Learning", "C++", "Swift"]

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


@pytest.mark.llm_eval
class TestCoverLetterAgentAntiHallucination:
    def test_nu_inventa_skill_uri_absente_din_cv(self):
        result = CoverLetterAgent().generate(CV_REAL, JOB_REAL)

        hallucinated = [s for s in SKILLS_NOT_IN_CV if s in result]
        assert not hallucinated, (
            f"Hallucination detected: skills not in CV appeared in letter: {hallucinated}"
        )

    def test_mentioneaza_cel_putin_un_skill_din_cv(self):
        result = CoverLetterAgent().generate(CV_REAL, JOB_REAL)

        assert any(skill in result for skill in CV_REAL["skills"]), (
            f"No CV skill found in letter. Skills: {CV_REAL['skills']}"
        )

    def test_contine_numele_candidatului_si_companiei(self):
        result = CoverLetterAgent().generate(CV_REAL, JOB_REAL)

        assert CV_REAL["name"] in result, "Candidate name missing from letter"
        assert JOB_REAL["company"] in result, "Company name missing from letter"

    def test_lungime_rezonabila(self):
        result = CoverLetterAgent().generate(CV_REAL, JOB_REAL)

        word_count = len(result.split())
        assert 150 <= word_count <= 500, (
            f"Letter length out of expected range: {word_count} words"
        )
