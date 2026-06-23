"""Repositorios multitenant.

Cada módulo expone funciones puras que reciben `Session` y `user_id` explícitos.
Esto permite componer múltiples ops en una transacción y facilita tests con
fixtures de sesión.

Uso típico:

    from memory.database import session_scope
    from memory.repositories import users, runner_profile

    with session_scope() as s:
        users.ensure(s, "firebase_uid_xyz")
        runner_profile.upsert(s, "firebase_uid_xyz", name="José", age=36, ...)
"""

from memory.repositories import (
    body_composition,
    hrv,
    nutrition,
    runner_profile,
    science_cache,
    users,
    weekly,
    weight,
)

__all__ = [
    "body_composition",
    "hrv",
    "nutrition",
    "runner_profile",
    "science_cache",
    "users",
    "weekly",
    "weight",
]
