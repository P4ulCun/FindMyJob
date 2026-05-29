import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db
User = get_user_model()


class TestUserModel:
    def test_create_user_normalizeaza_si_hashuieste_parola(self):
        u = User.objects.create_user(
            email="ana@example.com", password="Secret123", full_name="Ana Pop"
        )
        assert u.email == "ana@example.com"
        assert u.full_name == "Ana Pop"
        # parola NU e stocată în clar
        assert u.password != "Secret123"
        assert u.check_password("Secret123")

    def test_email_este_obligatoriu(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email="", password="x", full_name="No Email")


class TestAuthViews:
    def test_login_intoarce_tokenuri(self, api_client, user):
        resp = api_client.post(
            reverse("auth-login"),
            {"email": "test@example.com", "password": "StrongPass123"},
            format="json",
        )
        assert resp.status_code == 200
        assert "access" in resp.data["tokens"]
        assert resp.data["user"]["email"] == "test@example.com"

    def test_me_necesita_autentificare(self, api_client):
        assert api_client.get(reverse("auth-me")).status_code == 401

    def test_me_intoarce_profilul_userului_logat(self, auth_client):
        resp = auth_client.get(reverse("auth-me"))
        assert resp.status_code == 200
        assert resp.data["email"] == "test@example.com"