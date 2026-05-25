"""Test del helper de timezone — el bug original era usar `date.today()`
del servidor (UTC en Cloud Run) cuando debíamos usar la fecha de Bogotá.

A las 19:00 hora Bogotá ya es lunes UTC, así que `date.today()` daba lunes
y el plan saltaba a "Fuerza" cuando en Bogotá aún era domingo (descanso).
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from unittest.mock import patch
from zoneinfo import ZoneInfo

from api.utils.timezone import local_today, local_now, DEFAULT_TZ


def test_default_tz_es_bogota():
    assert str(DEFAULT_TZ) == "America/Bogota"


def test_local_today_devuelve_fecha_de_bogota():
    """A las 04:30 UTC del lunes, en Bogotá son las 23:30 del domingo.
    local_today debe devolver el domingo."""
    fake_utc = datetime(2026, 5, 25, 4, 30, tzinfo=timezone.utc)
    with patch("api.utils.timezone.datetime") as mock_dt:
        mock_dt.now.return_value = fake_utc.astimezone(ZoneInfo("America/Bogota"))
        # Forzamos: now() en Bogotá es domingo 23:30
        result = local_today()
        assert result == date(2026, 5, 24)
        assert result.weekday() == 6  # domingo


def test_local_today_consistente_con_local_now():
    assert local_today() == local_now().date()


def test_local_today_no_es_utc_naive():
    """Si el servidor está en UTC y son las 04:30 lun, date.today() retorna
    lunes; local_today() debe retornar domingo (en Bogotá aún es domingo)."""
    # Este test corre en local machine donde TZ del SO ya es Bogotá,
    # entonces date.today() coincide con local_today(). Aquí solo
    # verificamos que el helper SIEMPRE usa Bogotá independiente del SO.
    fake_now = datetime(2026, 5, 25, 4, 30, tzinfo=timezone.utc)
    with patch("api.utils.timezone.datetime") as mock_dt:
        mock_dt.now.side_effect = lambda tz=None: (
            fake_now.astimezone(tz) if tz else fake_now
        )
        assert local_today() == date(2026, 5, 24)
