"""Tests del endpoint POST /v1/users/me/init y PATCH /profile y DELETE /me.

Usa FastAPI TestClient + override de get_db + bypass de get_current_user_id
para no necesitar Firebase ni Garmin reales. La validación de credenciales
Garmin (GarminConnectClient) se mockea — la red está fuera del scope unit.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from api import deps
from api.main import app
from memory.repositories import garmin_credentials as creds_repo
from memory.repositories import runner_profile, users
from security import crypto


@pytest.fixture(autouse=True)
def _set_fernet_key(monkeypatch):
    monkeypatch.setenv(crypto._ENV_VAR, Fernet.generate_key().decode())
    crypto.reset_for_tests()
    yield
    crypto.reset_for_tests()


@pytest.fixture
def client_for_user(db_session):
    """TestClient con get_db override + get_current_user_id forzado a 'user_a_firebase_uid'."""
    def _override_db():
        try:
            yield db_session
        finally:
            pass

    def _override_user():
        return "user_a_firebase_uid"

    app.dependency_overrides[deps.get_db] = _override_db
    app.dependency_overrides[deps.get_current_user_id] = _override_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_for_user_b(db_session):
    def _override_db():
        try:
            yield db_session
        finally:
            pass

    def _override_user():
        return "user_b_firebase_uid"

    app.dependency_overrides[deps.get_db] = _override_db
    app.dependency_overrides[deps.get_current_user_id] = _override_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ─── POST /init ───────────────────────────────────────────────────────


class TestPostInit:
    def test_init_minimo_sin_garmin(self, client_for_user, db_session):
        """Body mínimo (solo name) crea User + Profile sin credenciales Garmin."""
        r = client_for_user.post("/v1/users/me/init", json={"name": "Ana"})
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["name"] == "Ana"
        assert body["user_id"] == "user_a_firebase_uid"
        assert users.get(db_session, "user_a_firebase_uid") is not None
        assert creds_repo.get(db_session, "user_a_firebase_uid") is None

    def test_init_completo_con_garmin(self, client_for_user, db_session):
        with patch("api.routers.users.GarminConnectClient") as MockClient, patch(
            "api.routers.users._kickoff_initial_sync"
        ):
            MockClient.return_value = object()  # login success
            r = client_for_user.post(
                "/v1/users/me/init",
                json={
                    "name": "Ana",
                    "age": 30,
                    "weight_kg": 60.0,
                    "city": "Medellín",
                    "altitude_msnm": 1495,
                    "goal_event": "10K",
                    "goal_date": "2026-12-01",
                    "garmin_email": "ana@test.com",
                    "garmin_password": "pw-secreta",
                },
            )
            assert r.status_code == 200, r.text
            body = r.json()
            assert body["city"] == "Medellín"
            assert body["altitude_msnm"] == 1495
        # Verificar persistencia
        creds = creds_repo.get_decrypted(db_session, "user_a_firebase_uid")
        assert creds == ("ana@test.com", "pw-secreta")

    def test_init_solo_email_o_password_rechaza(self, client_for_user):
        r = client_for_user.post(
            "/v1/users/me/init",
            json={"name": "X", "garmin_email": "a@x.com"},  # password falta
        )
        assert r.status_code == 422

    def test_init_garmin_creds_invalidas_rechaza(self, client_for_user, db_session):
        with patch(
            "api.routers.users.GarminConnectClient",
            side_effect=Exception("Garmin 401"),
        ):
            r = client_for_user.post(
                "/v1/users/me/init",
                json={
                    "name": "X",
                    "garmin_email": "x@x.com",
                    "garmin_password": "wrong",
                },
            )
            assert r.status_code == 422
            assert "Garmin" in r.json()["detail"]
        # NO debe haber persistido el user
        assert users.get(db_session, "user_a_firebase_uid") is None

    def test_init_extra_field_rechaza(self, client_for_user):
        """extra='forbid' previene typos del cliente."""
        r = client_for_user.post(
            "/v1/users/me/init",
            json={"name": "X", "unexpected_field": "value"},
        )
        assert r.status_code == 422

    def test_init_es_idempotente(self, client_for_user):
        """Llamar /init 2 veces actualiza, no duplica."""
        client_for_user.post("/v1/users/me/init", json={"name": "Ana", "age": 30})
        r2 = client_for_user.post(
            "/v1/users/me/init", json={"name": "Ana", "age": 31}
        )
        assert r2.status_code == 200
        assert r2.json()["age"] == 31

    def test_init_email_invalido_rechaza(self, client_for_user):
        r = client_for_user.post(
            "/v1/users/me/init",
            json={
                "name": "X",
                "garmin_email": "no-es-email",
                "garmin_password": "p",
            },
        )
        assert r.status_code == 422


# ─── PATCH /profile ───────────────────────────────────────────────────


class TestPatchProfile:
    def test_patch_sin_perfil_es_404(self, client_for_user):
        r = client_for_user.patch("/v1/users/me/profile", json={"weight_kg": 70.0})
        assert r.status_code == 404

    def test_patch_actualiza_solo_campos_enviados(self, client_for_user, db_session):
        client_for_user.post(
            "/v1/users/me/init",
            json={"name": "Ana", "age": 30, "weight_kg": 60.0},
        )
        r = client_for_user.patch(
            "/v1/users/me/profile",
            json={"weight_kg": 62.5},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["weight_kg"] == 62.5
        assert body["age"] == 30  # preservado
        assert body["name"] == "Ana"  # preservado

    def test_patch_extra_field_rechaza(self, client_for_user):
        client_for_user.post("/v1/users/me/init", json={"name": "Ana"})
        r = client_for_user.patch(
            "/v1/users/me/profile",
            json={"weight_kg": 60.0, "garmin_password": "hackeo"},
        )
        assert r.status_code == 422  # garmin_password no es campo de profile

    def test_patch_weekly_plan_override(self, client_for_user, db_session):
        client_for_user.post("/v1/users/me/init", json={"name": "Ana"})
        plan = {
            "0": ["rest", "Yoga 30 min"],
            "1": ["train", "Trote 30 min"],
            "2": ["rest", "Descanso"],
            "3": ["train", "Series cortas"],
            "4": ["rest", "Descanso"],
            "5": ["train", "Long run 90 min"],
            "6": ["rest", "Descanso"],
        }
        r = client_for_user.patch(
            "/v1/users/me/profile",
            json={"weekly_plan": plan},
        )
        assert r.status_code == 200
        assert r.json()["weekly_plan"] == plan


# ─── PUT /garmin ──────────────────────────────────────────────────────


class TestPutGarmin:
    def test_put_garmin_persiste_cifrado(self, client_for_user, db_session):
        with patch("api.routers.users.GarminConnectClient"):
            r = client_for_user.put(
                "/v1/users/me/garmin",
                json={"email": "x@x.com", "password": "nueva-pw"},
            )
            assert r.status_code == 204
        assert creds_repo.get_decrypted(db_session, "user_a_firebase_uid") == (
            "x@x.com",
            "nueva-pw",
        )

    def test_put_garmin_login_falla_no_persiste(self, client_for_user, db_session):
        with patch(
            "api.routers.users.GarminConnectClient", side_effect=Exception("auth fail")
        ):
            r = client_for_user.put(
                "/v1/users/me/garmin",
                json={"email": "x@x.com", "password": "bad"},
            )
            assert r.status_code == 422
        assert creds_repo.get(db_session, "user_a_firebase_uid") is None


# ─── DELETE /me ───────────────────────────────────────────────────────


class TestDeleteMe:
    def test_delete_sin_confirm_es_422(self, client_for_user):
        client_for_user.post("/v1/users/me/init", json={"name": "Ana"})
        r = client_for_user.delete("/v1/users/me")
        assert r.status_code == 422

    def test_delete_confirm_incorrecto_es_422(self, client_for_user):
        client_for_user.post("/v1/users/me/init", json={"name": "Ana"})
        r = client_for_user.request(
            "DELETE", "/v1/users/me", json={"confirm": "yes"}
        )
        assert r.status_code == 422

    def test_delete_cascade_borra_todo_del_usuario(self, client_for_user, db_session):
        with patch("api.routers.users.GarminConnectClient"), patch(
            "api.routers.users._kickoff_initial_sync"
        ):
            client_for_user.post(
                "/v1/users/me/init",
                json={
                    "name": "Ana",
                    "garmin_email": "a@x.com",
                    "garmin_password": "p",
                },
            )
        r = client_for_user.request(
            "DELETE", "/v1/users/me", json={"confirm": "DELETE"}
        )
        assert r.status_code == 204
        db_session.expire_all()
        assert users.get(db_session, "user_a_firebase_uid") is None
        assert runner_profile.get(db_session, "user_a_firebase_uid") is None
        assert creds_repo.get(db_session, "user_a_firebase_uid") is None
