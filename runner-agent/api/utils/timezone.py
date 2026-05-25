"""Helpers de fecha/hora locales del usuario.

Cloud Run corre en UTC. Si usamos `date.today()` para decidir "hoy" desde
las 19:00 hora Bogotá ya estamos en el día siguiente UTC y el plan diario
salta al día equivocado (ej. "hoy es lunes Fuerza" cuando en Bogotá aún es
domingo Descanso).

Por ahora la TZ es hardcoded a `America/Bogota` (LatAm). En el futuro
debería leerse de `runner_profile.city` → mapa ciudad→TZ, o agregar
columna `timezone` al perfil.
"""

from __future__ import annotations

from datetime import date as DateT, datetime
from zoneinfo import ZoneInfo

DEFAULT_TZ = ZoneInfo("America/Bogota")


def local_today(tz: ZoneInfo = DEFAULT_TZ) -> DateT:
    """Fecha calendario en la zona del usuario.

    Reemplaza `date.today()` en todos los call-sites que deciden "qué hacer
    HOY", "esta semana", "ayer", etc. — donde la respuesta cambia con el TZ.
    """
    return datetime.now(tz=tz).date()


def local_now(tz: ZoneInfo = DEFAULT_TZ) -> datetime:
    return datetime.now(tz=tz)
