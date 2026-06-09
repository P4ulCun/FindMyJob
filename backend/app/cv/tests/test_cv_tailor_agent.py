import json
import pytest
import requests

from cv.cv_tailor_agent import CVTailorAgent

CV_DATA = {
    "skills": ["Python", "Django"],
    "experience": ["Backend developer la Acme"],
    "education": ["Licență Informatică"],
}

JOB = {
    "title": "Python Backend Engineer",
    "company": "TechCorp",
    "description": "We use Django, DRF and PostgreSQL for our backend services.",
}


def _mock_llm(content: str):
    mock = pytest.importorskip("unittest.mock").MagicMock()
    mock.json.return_value = {"choices": [{"message": {"content": content}}]}
    return mock


class TestCVTailorAgentLogicaInterna:
    def setup_method(self):
        self.agent = CVTailorAgent()

    def test_normalize_detecteaza_item_modificat(self):
        original = ["Python developer"]
        raw = [{"after": "Python & Django backend developer", "reason": "Added Django"}]

        changes = self.agent._normalize_section_changes("skills", original, raw)

        assert len(changes) == 1
        assert changes[0]["before"] == "Python developer"
        assert changes[0]["after"] == "Python & Django backend developer"
        assert changes[0]["reason"] == "Added Django"
        assert changes[0]["status"] == "pending"

    def test_normalize_ignora_item_nemodificat(self):
        original = ["Python", "Django"]
        raw = [{"after": "Python", "reason": ""}, {"after": "Django", "reason": ""}]

        changes = self.agent._normalize_section_changes("skills", original, raw)

        assert changes == []

    def test_normalize_fallback_cand_raw_nu_e_lista(self):
        original = ["Python"]
        changes = self.agent._normalize_section_changes("skills", original, None)
        assert changes == []

    def test_resolve_items_returneaza_versiunea_modificata(self):
        original = ["Backend developer la Acme"]
        raw = [{"after": "Senior Backend developer la Acme (Django, DRF)", "reason": "x"}]

        resolved = self.agent._resolve_section_items(original, raw)

        assert resolved == ["Senior Backend developer la Acme (Django, DRF)"]

    def test_resolve_items_pastreaza_originalul_daca_after_lipseste(self):
        original = ["Python"]
        resolved = self.agent._resolve_section_items(original, [{}])
        assert resolved == ["Python"]

    def test_build_result_structura_corecta(self):
        llm_result = {
            "skills": [
                {"after": "Python & Django", "reason": "more specific"},
                {"after": "Django", "reason": ""},
            ],
            "experience": [{"after": "Backend dev at Acme (Django)", "reason": "highlighted"}],
            "education": [{"after": "Licență Informatică", "reason": ""}],
        }

        result = self.agent._build_result(CV_DATA, llm_result)

        assert "change_set" in result
        assert "tailored_skills" in result
        assert "tailored_experience" in result
        assert "tailored_education" in result
        assert result["tailored_skills"] == ["Python & Django", "Django"]
        assert len(result["change_set"]["skills"]) == 1


class TestCVTailorAgentEvals:
    def test_tailor_happy_path_cu_raspuns_llm_valid(self, mocker):
        payload = json.dumps({
            "skills": [{"after": "Python & Django (backend focus)", "reason": "Job emphasises Django"}],
            "experience": [{"after": "Backend developer la Acme — Django, DRF", "reason": "Added stack"}],
            "education": [{"after": "Licență Informatică", "reason": ""}],
        })
        mocker.patch("requests.post", return_value=_mock_llm(payload))

        result = CVTailorAgent().tailor(CV_DATA, JOB)

        assert result["tailored_skills"][0] == "Python & Django (backend focus)"
        assert len(result["change_set"]["skills"]) == 1

    def test_tailor_json_in_markdown_fence(self, mocker):
        inner = json.dumps({
            "skills": [{"after": "Django expert", "reason": "relevant"}],
            "experience": [{"after": "Backend dev", "reason": ""}],
            "education": [{"after": "Licență Informatică", "reason": ""}],
        })
        fenced = f"```json\n{inner}\n```"
        mocker.patch("requests.post", return_value=_mock_llm(fenced))

        result = CVTailorAgent().tailor(CV_DATA, JOB)

        assert result["tailored_skills"][0] == "Django expert"

    def test_tailor_eroare_retea_returneaza_originalul(self, mocker):
        mocker.patch("requests.post", side_effect=requests.exceptions.ConnectionError())

        result = CVTailorAgent().tailor(CV_DATA, JOB)

        assert result["tailored_skills"] == CV_DATA["skills"]
        assert result["tailored_experience"] == CV_DATA["experience"]
        assert result["change_set"]["skills"] == []

    def test_tailor_nu_fabrica_skills_noi(self, mocker):
        payload = json.dumps({
            "skills": [{"after": "Python", "reason": ""}, {"after": "Django", "reason": ""}],
            "experience": [{"after": "Backend developer la Acme", "reason": ""}],
            "education": [{"after": "Licență Informatică", "reason": ""}],
        })
        mocker.patch("requests.post", return_value=_mock_llm(payload))

        result = CVTailorAgent().tailor(CV_DATA, JOB)

        assert len(result["tailored_skills"]) == len(CV_DATA["skills"])


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


@pytest.mark.llm_eval
class TestCVTailorAgentAntiHallucination:
    def test_nu_inventa_skill_uri_absente_din_cv(self):
        result = CVTailorAgent().tailor(CV_REAL, JOB_REAL)
        
        tailored_skills_str = " ".join(result["tailored_skills"]).lower()
        hallucinated = [s for s in SKILLS_NOT_IN_CV if s.lower() in tailored_skills_str]
        
        assert not hallucinated, f"Hallucination detected: {hallucinated}"

    def test_pastreaza_numarul_de_elemente(self):
        result = CVTailorAgent().tailor(CV_REAL, JOB_REAL)
        
        assert len(result["tailored_skills"]) == len(CV_REAL["skills"])
        assert len(result["tailored_experience"]) == len(CV_REAL["experience"])
