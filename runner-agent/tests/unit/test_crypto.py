"""Tests del módulo de cifrado de credenciales sensibles."""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet, InvalidToken

from security import crypto


@pytest.fixture(autouse=True)
def _reset_crypto_cache():
    crypto.reset_for_tests()
    yield
    crypto.reset_for_tests()


def test_round_trip_simple(monkeypatch):
    key = Fernet.generate_key().decode()
    monkeypatch.setenv(crypto._ENV_VAR, key)
    plain = "mi-password-secreta-2026"
    enc = crypto.encrypt(plain)
    assert enc != plain.encode()
    assert isinstance(enc, bytes)
    assert crypto.decrypt(enc) == plain


def test_round_trip_unicode(monkeypatch):
    monkeypatch.setenv(crypto._ENV_VAR, Fernet.generate_key().decode())
    plain = "contraseña-con-ñ-y-emoji-🏃‍♂️"
    assert crypto.decrypt(crypto.encrypt(plain)) == plain


def test_dos_encryptions_del_mismo_input_no_son_iguales(monkeypatch):
    """Fernet incluye IV aleatorio → mismo plaintext da blobs distintos."""
    monkeypatch.setenv(crypto._ENV_VAR, Fernet.generate_key().decode())
    a = crypto.encrypt("igual")
    b = crypto.encrypt("igual")
    assert a != b
    assert crypto.decrypt(a) == crypto.decrypt(b) == "igual"


def test_sin_key_lanza_crypto_config_error(monkeypatch):
    monkeypatch.delenv(crypto._ENV_VAR, raising=False)
    with pytest.raises(crypto.CryptoConfigError) as exc_info:
        crypto.encrypt("algo")
    assert "no está definida" in str(exc_info.value)


def test_key_malformada_lanza_crypto_config_error(monkeypatch):
    monkeypatch.setenv(crypto._ENV_VAR, "no-es-una-key-fernet-valida")
    with pytest.raises(crypto.CryptoConfigError):
        crypto.encrypt("algo")


def test_blob_corrupto_lanza_invalid_token(monkeypatch):
    monkeypatch.setenv(crypto._ENV_VAR, Fernet.generate_key().decode())
    with pytest.raises(InvalidToken):
        crypto.decrypt(b"basura-no-fernet")


def test_blob_cifrado_con_otra_key_no_descifra(monkeypatch):
    """Si rotamos la key sin migrar blobs, descifrado debe fallar (no devolver basura)."""
    monkeypatch.setenv(crypto._ENV_VAR, Fernet.generate_key().decode())
    blob = crypto.encrypt("secreto")

    monkeypatch.setenv(crypto._ENV_VAR, Fernet.generate_key().decode())
    crypto.reset_for_tests()
    with pytest.raises(InvalidToken):
        crypto.decrypt(blob)


def test_plaintext_no_string_lanza_type_error(monkeypatch):
    monkeypatch.setenv(crypto._ENV_VAR, Fernet.generate_key().decode())
    with pytest.raises(TypeError):
        crypto.encrypt(b"bytes-no")  # type: ignore[arg-type]


def test_memoryview_de_postgres_se_acepta(monkeypatch):
    """Psycopg2 a veces devuelve memoryview para BYTEA — el decrypt debe aceptarlo."""
    monkeypatch.setenv(crypto._ENV_VAR, Fernet.generate_key().decode())
    blob = crypto.encrypt("test")
    mv = memoryview(blob)
    assert crypto.decrypt(mv) == "test"
