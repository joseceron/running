"""Test de aislamiento cross-user — guardián anti-regresión.

Verifica que los datos de un usuario no se filtran al request de otro. Es la
prueba más importante del multi-tenant: si pasa, podemos abrir signups a
beta testers sin riesgo de privacidad médica.

Estrategia:
1. Crea user_a y user_b con datos completamente distintos en BD.
2. Cada endpoint del API se invoca con el token de user_a y luego con el de user_b.
3. Verifica que cada response contiene SOLO los datos del usuario que hizo la request.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from api import deps
from api.main import app
from memory.models import Activity, HRVLog, WeeklyHistory
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
def seeded(db_session, user_a, user_b):
    """Pobla 2 usuarios con perfiles + HRV + actividades + credenciales muy distintos."""
    today = date.today()

    # User A — perfil "Ana en Bogotá"
    runner_profile.upsert(
        db_session, user_a,
        name="Ana", age=30, weight_kg=60.0, city="Bogotá", altitude_msnm=2640,
        goal_event="10K", goal_date=today + timedelta(days=60),
    )
    creds_repo.upsert(db_session, user_a, email="ana@x.com", password_plain="ana-pw")
    db_session.add(HRVLog(user_id=user_a, date=today, hrv_rmssd=55.0))
    db_session.add(Activity(
        user_id=user_a, activity_id="A-1", date=today, type_key="running",
        name="Carrera de Ana", distance_km=5.0, duration_secs=1800,
    ))
    db_session.add(WeeklyHistory(
        user_id=user_a, week_start=today - timedelta(days=today.weekday()),
        plan_km=25.0, executed_km=22.0, acwr=0.95,
    ))

    # User B — perfil "Bruno en Lima"
    runner_profile.upsert(
        db_session, user_b,
        name="Bruno", age=42, weight_kg=78.0, city="Lima", altitude_msnm=154,
        goal_event="42K", goal_date=today + timedelta(days=180),
    )
    creds_repo.upsert(db_session, user_b, email="bruno@y.com", password_plain="bruno-pw")
    db_session.add(HRVLog(user_id=user_b, date=today, hrv_rmssd=42.0))
    db_session.add(Activity(
        user_id=user_b, activity_id="B-1", date=today, type_key="running",
        name="Carrera de Bruno", distance_km=15.0, duration_secs=5400,
    ))
    db_session.add(WeeklyHistory(
        user_id=user_b, week_start=today - timedelta(days=today.weekday()),
        plan_km=70.0, executed_km=68.0, acwr=1.12,
    ))
    db_session.flush()
    return {"a": user_a, "b": user_b}


def _client_as(uid: str, db_session):
    def _override_db():
        try:
            yield db_session
        finally:
            pass

    def _override_user():
        return uid

    app.dependency_overrides[deps.get_db] = _override_db
    app.dependency_overrides[deps.get_current_user_id] = _override_user
    return TestClient(app)


# ─── Endpoints de perfil ──────────────────────────────────────────────


class TestProfileIsolation:
    def test_get_profile_no_filtra(self, seeded, db_session):
        try:
            client_a = _client_as(seeded["a"], db_session)
            ra = client_a.get("/v1/users/me/profile")
            assert ra.status_code == 200
            assert ra.json()["name"] == "Ana"
            assert ra.json()["city"] == "Bogotá"
            assert "Bruno" not in ra.text
            assert "Lima" not in ra.text
        finally:
            app.dependency_overrides.clear()

        try:
            client_b = _client_as(seeded["b"], db_session)
            rb = client_b.get("/v1/users/me/profile")
            assert rb.status_code == 200
            assert rb.json()["name"] == "Bruno"
            assert "Ana" not in rb.text
            assert "Bogotá" not in rb.text
        finally:
            app.dependency_overrides.clear()


class TestHRVIsolation:
    def test_get_hrv_no_filtra(self, seeded, db_session):
        try:
            ra = _client_as(seeded["a"], db_session).get("/v1/users/me/hrv")
            assert ra.status_code == 200
            assert ra.json()["latest_value"] == 55.0
        finally:
            app.dependency_overrides.clear()

        try:
            rb = _client_as(seeded["b"], db_session).get("/v1/users/me/hrv")
            assert rb.status_code == 200
            assert rb.json()["latest_value"] == 42.0
        finally:
            app.dependency_overrides.clear()


class TestWeeklyIsolation:
    def test_get_weekly_no_filtra(self, seeded, db_session):
        try:
            ra = _client_as(seeded["a"], db_session).get("/v1/users/me/weekly")
            assert ra.status_code == 200
            weeks_a = ra.json()["weeks"]
            assert any(w["executed_km"] == 22.0 for w in weeks_a)
            assert not any(w["executed_km"] == 68.0 for w in weeks_a)
        finally:
            app.dependency_overrides.clear()

        try:
            rb = _client_as(seeded["b"], db_session).get("/v1/users/me/weekly")
            assert rb.status_code == 200
            weeks_b = rb.json()["weeks"]
            assert any(w["executed_km"] == 68.0 for w in weeks_b)
            assert not any(w["executed_km"] == 22.0 for w in weeks_b)
        finally:
            app.dependency_overrides.clear()


# ─── Credenciales Garmin: jamás se devuelven en NINGÚN endpoint ───────


class TestCredentialsNeverLeak:
    def test_credentials_no_aparecen_en_endpoints_publicos(self, seeded, db_session):
        """Ningún endpoint debe filtrar la password (cifrada o en claro)."""
        endpoints = [
            "/v1/users/me/profile",
            "/v1/users/me/hrv",
            "/v1/users/me/weekly",
            "/v1/users/me/dashboard",
        ]
        try:
            client = _client_as(seeded["a"], db_session)
            for ep in endpoints:
                resp = client.get(ep)
                if resp.status_code == 200:
                    text = resp.text
                    assert "ana-pw" not in text, f"PASSWORD filtrada en {ep}"
                    assert "bruno-pw" not in text, f"PASSWORD ajena filtrada en {ep}"
                    assert "password_encrypted" not in text
        finally:
            app.dependency_overrides.clear()


# ─── PATCH de user_a NO afecta perfil de user_b ───────────────────────


class TestWritesAreIsolated:
    def test_patch_de_user_a_no_modifica_user_b(self, seeded, db_session):
        try:
            client_a = _client_as(seeded["a"], db_session)
            r = client_a.patch("/v1/users/me/profile", json={"weight_kg": 55.0})
            assert r.status_code == 200
            assert r.json()["weight_kg"] == 55.0
        finally:
            app.dependency_overrides.clear()

        # Refrescar identity map para asegurar que leemos BD, no caché.
        db_session.expire_all()

        # Verificar en BD que user_b NO cambió
        b_profile = runner_profile.get(db_session, seeded["b"])
        assert b_profile.weight_kg == 78.0  # original
        assert b_profile.name == "Bruno"  # original

    def test_delete_de_user_a_no_borra_user_b(self, seeded, db_session):
        from unittest.mock import patch
        try:
            client_a = _client_as(seeded["a"], db_session)
            with patch("api.routers.users._kickoff_initial_sync"):
                r = client_a.request(
                    "DELETE", "/v1/users/me", json={"confirm": "DELETE"}
                )
            assert r.status_code == 204
        finally:
            app.dependency_overrides.clear()

        # Limpiar identity map para releer de BD (no del cache de la session)
        db_session.expire_all()

        assert users.get(db_session, seeded["a"]) is None
        # User B intacto
        assert users.get(db_session, seeded["b"]) is not None
        assert runner_profile.get(db_session, seeded["b"]).name == "Bruno"
        assert creds_repo.get(db_session, seeded["b"]) is not None
