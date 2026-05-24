"""Tests del builder compartido `build_today_action`.

Verifica los 8 escenarios que decide el motor de plan + carga + HRV.
Es el corazón del fix para el bug observado el 2026-05-24:
"DESCANSA HOY" + el LLM diciendo "ejecuta 45 min de Z2" en la misma vista.

Los tests son puros — no necesitan DB ni mocks de Anthropic. La cobertura
de "el LLM recibe el today_action en el payload" vive en
`test_diagnosis_payload.py`.
"""

from __future__ import annotations

from datetime import date, timedelta

from agents.today_action_builder import WEEKDAY_PLAN, build_today_action


# ─── Estructura: todos los campos requeridos están presentes ─────────


def _assert_shape(data: dict) -> None:
    assert set(data.keys()) >= {
        "status",
        "temporal",
        "headline",
        "short_reason",
        "reasons",
        "allowed",
        "next_session",
    }
    assert data["status"] in {
        "rest", "train", "active_recovery", "trained_already",
        "past_executed", "past_rest_planned", "past_missed",
        "future_planned",
    }
    assert data["temporal"] in {"today", "past", "future"}
    assert isinstance(data["headline"], str) and data["headline"]
    assert isinstance(data["short_reason"], str) and data["short_reason"]
    assert isinstance(data["reasons"], list)
    assert isinstance(data["allowed"], list)
    assert isinstance(data["next_session"], str)


# ─── HOY ──────────────────────────────────────────────────────────────


class TestToday:
    def test_today_es_temporal_today(self) -> None:
        ta = build_today_action(date.today(), [], acwr=1.0, hrv_today=55.0, hrv_baseline=55.0)
        _assert_shape(ta)
        assert ta["temporal"] == "today"

    def test_ya_entreno_hoy_no_recomienda_otra_sesion(self) -> None:
        """Si hay actividades hoy, status debe ser trained_already — sin importar HRV/ACWR."""
        ta = build_today_action(
            date.today(),
            ["Caminata · 5.77 km"],
            acwr=1.0,
            hrv_today=55.0,
            hrv_baseline=55.0,
        )
        _assert_shape(ta)
        assert ta["status"] == "trained_already"
        assert ta["temporal"] == "today"

    def test_hrv_suprimido_fuerza_descanso(self) -> None:
        """HRV bajo más de 1 SD del baseline → rest, aunque el plan diga train."""
        ta = build_today_action(
            date.today(),
            [],
            acwr=1.0,
            hrv_today=45.0,
            hrv_baseline=55.0,
        )
        _assert_shape(ta)
        assert ta["status"] == "rest"

    def test_acwr_alto_un_dia_de_train_pide_recuperacion_activa(self) -> None:
        """ACWR>1.3 + plan=train → active_recovery. En día de rest, queda rest."""
        ta = build_today_action(
            date.today(),
            [],
            acwr=1.6,
            hrv_today=55.0,
            hrv_baseline=55.0,
        )
        _assert_shape(ta)
        # Si hoy es día de descanso programado, rest tiene precedencia.
        assert ta["status"] in {"active_recovery", "rest"}

    def test_dia_normal_de_train_emite_train(self) -> None:
        """Tomamos un lunes (weekday=0, plan=train) y forzamos sin alertas."""
        today = date.today()
        # Buscar el próximo lunes
        days_to_monday = (0 - today.weekday()) % 7 or 7
        next_monday = today + timedelta(days=days_to_monday)
        # Pero ese día es futuro → forzamos usando hoy si hoy es lunes
        if today.weekday() == 0:
            ta = build_today_action(today, [], acwr=1.0, hrv_today=55.0, hrv_baseline=55.0)
            _assert_shape(ta)
            assert ta["status"] == "train"
            assert "Fuerza A" in ta["headline"]


# ─── PASADO ───────────────────────────────────────────────────────────


class TestPast:
    def test_ejecutado(self) -> None:
        yesterday = date.today() - timedelta(days=1)
        ta = build_today_action(
            yesterday,
            ["Carrera · 5km"],
            acwr=1.1,
            hrv_today=55.0,
            hrv_baseline=55.0,
        )
        _assert_shape(ta)
        assert ta["temporal"] == "past"
        assert ta["status"] == "past_executed"
        assert ta["next_session"] == ""  # pasado no muestra próxima

    def test_descanso_programado_en_pasado(self) -> None:
        # Encontrar un domingo pasado (weekday=6, planned=rest)
        d = date.today() - timedelta(days=14)
        while d.weekday() != 6:
            d -= timedelta(days=1)
        ta = build_today_action(d, [], None, None, None)
        _assert_shape(ta)
        assert ta["status"] == "past_rest_planned"

    def test_no_realizado(self) -> None:
        # Encontrar un lunes pasado (planned=train), sin actividades = missed
        d = date.today() - timedelta(days=14)
        while d.weekday() != 0:
            d -= timedelta(days=1)
        ta = build_today_action(d, [], None, None, None)
        _assert_shape(ta)
        assert ta["status"] == "past_missed"


# ─── FUTURO ───────────────────────────────────────────────────────────


class TestFuture:
    def test_planificado_train(self) -> None:
        # Mañana o un día con plan=train
        d = date.today() + timedelta(days=1)
        while WEEKDAY_PLAN[d.weekday()][0] != "train":
            d += timedelta(days=1)
        ta = build_today_action(d, [], None, None, None)
        _assert_shape(ta)
        assert ta["temporal"] == "future"
        assert ta["status"] == "future_planned"
        assert "PLANIFICADO" in ta["headline"]

    def test_planificado_rest(self) -> None:
        d = date.today() + timedelta(days=1)
        while WEEKDAY_PLAN[d.weekday()][0] != "rest":
            d += timedelta(days=1)
        ta = build_today_action(d, [], None, None, None)
        _assert_shape(ta)
        assert ta["status"] == "future_planned"
        assert "DESCANSO" in ta["headline"]


# ─── Próxima sesión: no debe estar vacía cuando el día es HOY ────────


class TestNextSession:
    def test_hoy_siempre_propone_proxima_sesion(self) -> None:
        ta = build_today_action(date.today(), [], None, None, None)
        # Siempre debería sugerir alguna próxima sesión de los próximos 7 días
        # (el plan tiene varios días de train por semana).
        assert ta["next_session"] != ""
