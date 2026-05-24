"""Repositorio de `garmin_credentials` — password cifrado por usuario.

Toda escritura cifra antes de persistir. Toda lectura descifra. Si la master
key falla, propaga `CryptoConfigError`; si el blob está corrupto (rotación de
key sin migrar), propaga `InvalidToken`. Nunca devolver el blob crudo.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from memory.models import GarminCredentials
from security import crypto


def upsert(
    session: Session,
    user_id: str,
    *,
    email: str,
    password_plain: str,
) -> GarminCredentials:
    """Crea o reemplaza las credenciales Garmin del usuario.

    El password viene en claro y se cifra aquí. Si el row ya existía, también
    se resetea `last_error` (el usuario está intentando con creds nuevas).
    """
    enc = crypto.encrypt(password_plain)
    creds = session.get(GarminCredentials, user_id)
    if creds is None:
        creds = GarminCredentials(
            user_id=user_id,
            email=email,
            password_encrypted=enc,
        )
        session.add(creds)
    else:
        creds.email = email
        creds.password_encrypted = enc
        creds.last_error = None
    session.flush()
    return creds


def get_decrypted(session: Session, user_id: str) -> tuple[str, str] | None:
    """Devuelve `(email, password_plain)` o None si no hay credenciales."""
    creds = session.get(GarminCredentials, user_id)
    if creds is None:
        return None
    return (creds.email, crypto.decrypt(creds.password_encrypted))


def get(session: Session, user_id: str) -> GarminCredentials | None:
    """Devuelve el row sin descifrar (para chequear existencia/metadata)."""
    return session.get(GarminCredentials, user_id)


def mark_login_ok(session: Session, user_id: str) -> None:
    creds = session.get(GarminCredentials, user_id)
    if creds is None:
        return
    creds.last_login_at = datetime.now(tz=timezone.utc)
    creds.last_error = None


def mark_login_failed(session: Session, user_id: str, error: str) -> None:
    creds = session.get(GarminCredentials, user_id)
    if creds is None:
        return
    # Truncar para no llenar la columna con stack traces gigantes.
    creds.last_error = error[:500]


def delete(session: Session, user_id: str) -> None:
    creds = session.get(GarminCredentials, user_id)
    if creds is not None:
        session.delete(creds)
