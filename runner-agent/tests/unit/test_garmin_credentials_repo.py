"""Tests del repositorio de credenciales Garmin.

Verifica cifrado at rest + aislamiento cross-user + idempotencia del upsert.
Usa Postgres real via testcontainers (fixture `db_session` del conftest).
"""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet

from memory.repositories import garmin_credentials as creds_repo
from security import crypto


@pytest.fixture(autouse=True)
def _set_fernet_key(monkeypatch):
    monkeypatch.setenv(crypto._ENV_VAR, Fernet.generate_key().decode())
    crypto.reset_for_tests()
    yield
    crypto.reset_for_tests()


def test_upsert_cifra_el_password(db_session, user_a):
    creds_repo.upsert(
        db_session,
        user_a,
        email="user_a@garmin.com",
        password_plain="super-secreto-123",
    )
    db_session.flush()

    # Leer el blob crudo y verificar que no contiene el plaintext
    raw = creds_repo.get(db_session, user_a)
    assert raw is not None
    assert b"super-secreto-123" not in bytes(raw.password_encrypted)
    assert len(bytes(raw.password_encrypted)) > 10

    # Descifrado devuelve el original
    decrypted = creds_repo.get_decrypted(db_session, user_a)
    assert decrypted == ("user_a@garmin.com", "super-secreto-123")


def test_upsert_reemplaza_credenciales_existentes(db_session, user_a):
    creds_repo.upsert(db_session, user_a, email="old@x.com", password_plain="old-pw")
    creds_repo.upsert(db_session, user_a, email="new@x.com", password_plain="new-pw")
    db_session.flush()

    assert creds_repo.get_decrypted(db_session, user_a) == ("new@x.com", "new-pw")


def test_aislamiento_cross_user(db_session, user_a, user_b):
    """user_a no puede leer creds de user_b ni viceversa."""
    creds_repo.upsert(db_session, user_a, email="a@x.com", password_plain="a-pw")
    creds_repo.upsert(db_session, user_b, email="b@x.com", password_plain="b-pw")
    db_session.flush()

    assert creds_repo.get_decrypted(db_session, user_a) == ("a@x.com", "a-pw")
    assert creds_repo.get_decrypted(db_session, user_b) == ("b@x.com", "b-pw")


def test_get_devuelve_none_si_no_existe(db_session, user_a):
    assert creds_repo.get(db_session, user_a) is None
    assert creds_repo.get_decrypted(db_session, user_a) is None


def test_mark_login_ok_limpia_error(db_session, user_a):
    creds_repo.upsert(db_session, user_a, email="x@x.com", password_plain="p")
    creds_repo.mark_login_failed(db_session, user_a, "Garmin 403")
    db_session.flush()
    assert creds_repo.get(db_session, user_a).last_error == "Garmin 403"

    creds_repo.mark_login_ok(db_session, user_a)
    db_session.flush()
    row = creds_repo.get(db_session, user_a)
    assert row.last_error is None
    assert row.last_login_at is not None


def test_mark_login_failed_trunca_a_500_chars(db_session, user_a):
    creds_repo.upsert(db_session, user_a, email="x@x.com", password_plain="p")
    big_error = "E" * 5000
    creds_repo.mark_login_failed(db_session, user_a, big_error)
    db_session.flush()
    assert len(creds_repo.get(db_session, user_a).last_error) == 500


def test_upsert_resetea_last_error_al_cambiar_pw(db_session, user_a):
    """Cuando user mete nueva password, el error viejo se limpia (puede que con
    la nueva sí logre login)."""
    creds_repo.upsert(db_session, user_a, email="x@x.com", password_plain="vieja")
    creds_repo.mark_login_failed(db_session, user_a, "auth failed")
    db_session.flush()

    creds_repo.upsert(db_session, user_a, email="x@x.com", password_plain="nueva")
    db_session.flush()
    assert creds_repo.get(db_session, user_a).last_error is None


def test_delete_remueve_la_fila(db_session, user_a):
    creds_repo.upsert(db_session, user_a, email="x@x.com", password_plain="p")
    creds_repo.delete(db_session, user_a)
    db_session.flush()
    assert creds_repo.get(db_session, user_a) is None


def test_cascade_delete_de_user_borra_credenciales(db_session, user_a):
    """Al borrar el User (hard_delete), las credenciales deben caer con CASCADE."""
    from memory.repositories import users as users_repo

    creds_repo.upsert(db_session, user_a, email="x@x.com", password_plain="p")
    db_session.flush()

    users_repo.hard_delete(db_session, user_a)
    db_session.flush()
    assert creds_repo.get(db_session, user_a) is None
