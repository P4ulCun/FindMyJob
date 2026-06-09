import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        email="test@example.com",
        password="StrongPass123",
        full_name="Test User",
    )


@pytest.fixture
def auth_client(api_client, user):
    """Client DRF deja autentificat cu un token JWT valid."""
    access = RefreshToken.for_user(user).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return api_client


@pytest.fixture(autouse=True)
def block_external_http(request, monkeypatch):
    """
    Plasă de siguranță: dacă un test uită să mock-uiască un agent AI sau un
    fetcher de joburi, apelul real eșuează zgomotos în loc să lovească rețeaua.
    Testele marcate cu @pytest.mark.llm_eval sunt exceptate — ele rulează modelul real.
    """
    if request.node.get_closest_marker("llm_eval"):
        return

    def _blocked(*args, **kwargs):
        raise RuntimeError(
            "Apel HTTP real blocat în teste. Mock-uiește agentul/fetcher-ul."
        )

    monkeypatch.setattr("requests.post", _blocked)
    monkeypatch.setattr("requests.get", _blocked)
