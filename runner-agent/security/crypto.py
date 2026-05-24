"""Cifrado simétrico para credenciales sensibles de usuarios (Garmin password).

Usa `cryptography.fernet` (AES-128-CBC + HMAC-SHA256 con rotación de keys
automática del propio Fernet). La master key se lee de la variable de entorno
`LIEBRE_FERNET_KEY` (32 bytes base64-url-encoded, formato Fernet estándar).

En producción la key vive en Google Secret Manager bajo el nombre
`liebre-fernet-key` y se monta como env var via `--set-secrets` en el deploy
script. En dev se lee del .env. NUNCA hardcodear keys ni hacer fallback a
una key por defecto — preferimos fallar rápido si no está configurada.

Backup operativo: la key se guarda también en el 1Password del founder.
Si la perdemos, todas las credenciales Garmin cifradas se vuelven
irrecuperables y cada usuario debe re-conectar.

Generar una key nueva:
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""

from __future__ import annotations

import os
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

_ENV_VAR = "LIEBRE_FERNET_KEY"


class CryptoConfigError(RuntimeError):
    """Master key ausente o malformada."""


@lru_cache(maxsize=1)
def _fernet() -> Fernet:
    raw = os.environ.get(_ENV_VAR)
    if not raw:
        raise CryptoConfigError(
            f"{_ENV_VAR} no está definida. Genera una con: "
            f"python -c 'from cryptography.fernet import Fernet; "
            f"print(Fernet.generate_key().decode())' y exportala."
        )
    try:
        return Fernet(raw.encode() if isinstance(raw, str) else raw)
    except Exception as exc:
        raise CryptoConfigError(
            f"{_ENV_VAR} tiene formato inválido (debe ser 32 bytes base64-url): {exc}"
        ) from exc


def encrypt(plaintext: str) -> bytes:
    """Cifra un string. Devuelve bytes opacos para guardar en BYTEA."""
    if not isinstance(plaintext, str):
        raise TypeError(f"plaintext debe ser str, got {type(plaintext).__name__}")
    return _fernet().encrypt(plaintext.encode("utf-8"))


def decrypt(blob: bytes) -> str:
    """Descifra. Lanza CryptoConfigError si la key no abre el blob (probablemente
    rotación de key sin migrar). Lanza InvalidToken si el blob está corrupto."""
    if isinstance(blob, memoryview):
        blob = bytes(blob)
    try:
        return _fernet().decrypt(blob).decode("utf-8")
    except InvalidToken:
        raise
    except Exception as exc:
        raise CryptoConfigError(f"No pude descifrar: {exc}") from exc


def reset_for_tests() -> None:
    """Permite a los tests forzar re-lectura de la env var tras monkeypatch."""
    _fernet.cache_clear()
