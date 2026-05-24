"""FastAPI dependencies — DB session + current_user.

En `dev`, el current_user_id se resuelve al `settings.dev_user_id` sin validar
token. En `staging`/`prod`, se valida el Firebase ID Token via firebase-admin.
"""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session

from api.settings import settings
from memory.database import get_sessionmaker


def get_db() -> Iterator[Session]:
    """Sesión por request (commitea al final si no hubo excepción)."""
    SessionLocal = get_sessionmaker()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_current_user_id(
    authorization: str | None = Header(default=None),
) -> str:
    """Resuelve el user_id de la request.

    - dev: retorna `settings.dev_user_id` sin verificar token (bypass)
    - prod/staging: verifica `Authorization: Bearer <firebase_id_token>` con
      firebase-admin y retorna `decoded["uid"]`.
    """
    if settings.is_dev:
        return settings.dev_user_id

    if not authorization or not authorization.startswith("Bearer "):
        import os

        demo_uid = os.environ.get("DEMO_FALLBACK_USER_ID")
        if demo_uid:
            return demo_uid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
        )
    token = authorization.removeprefix("Bearer ").strip()

    # Lazy import para que dev no necesite firebase-admin cargado en cold start
    import firebase_admin
    from firebase_admin import auth as firebase_auth

    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded["uid"]
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase ID token: {exc}",
        ) from exc
