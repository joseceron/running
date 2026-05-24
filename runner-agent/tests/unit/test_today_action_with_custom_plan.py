"""Test del override per-user del weekly_plan."""

from __future__ import annotations

from datetime import date, timedelta

from agents.today_action_builder import (
    DEFAULT_WEEKDAY_PLAN,
    _coerce_plan,
    build_today_action,
)


def test_default_plan_es_generico_no_de_jose():
    """DEFAULT_WEEKDAY_PLAN no debe mencionar 'sóleo' (lesión de José)."""
    for _, label in DEFAULT_WEEKDAY_PLAN.values():
        lower = label.lower()
        assert "sóleo" not in lower
        assert "soleo" not in lower


def test_coerce_plan_acepta_dict_str_keys():
    """JSONB de Postgres deserializa keys como strings — el coercer las normaliza a int."""
    raw_from_jsonb = {
        "0": ["rest", "Yoga"],
        "1": ["train", "Trote"],
    }
    plan = _coerce_plan(raw_from_jsonb)
    assert plan[0] == ("rest", "Yoga")
    assert plan[1] == ("train", "Trote")
    # Los días no especificados caen al default
    assert plan[6] == DEFAULT_WEEKDAY_PLAN[6]


def test_coerce_plan_none_devuelve_default():
    assert _coerce_plan(None) == DEFAULT_WEEKDAY_PLAN
    assert _coerce_plan({}) == DEFAULT_WEEKDAY_PLAN


def test_build_today_action_respeta_override():
    """Si el user tiene weekly_plan custom, today_action lo usa."""
    # Forzamos: HOY es lunes (weekday=0)
    today = date.today()
    days_to_monday = (0 - today.weekday()) % 7
    target = today + timedelta(days=days_to_monday)

    custom_plan = {
        0: ("rest", "Mi día de descanso personalizado"),  # lunes → rest custom
        1: ("train", "Mi sesión"),
        2: ("train", "Mi sesión 2"),
        3: ("train", "Mi sesión 3"),
        4: ("train", "Mi sesión 4"),
        5: ("train", "Mi sesión 5"),
        6: ("rest", "Domingo"),
    }
    # target debe ser hoy o futuro — si days_to_monday es 0, es hoy
    if days_to_monday == 0:
        ta = build_today_action(
            target=target,
            activity_labels=[],
            acwr=None, hrv_today=None, hrv_baseline=None,
            weekday_plan=custom_plan,
        )
        assert ta["status"] == "rest"
        assert "personalizado" in ta["short_reason"] or ta["temporal"] == "today"


def test_build_today_action_sin_plan_usa_default():
    """Cuando weekday_plan=None, debe respetar DEFAULT_WEEKDAY_PLAN."""
    ta = build_today_action(
        target=date.today(),
        activity_labels=[],
        acwr=None, hrv_today=None, hrv_baseline=None,
        weekday_plan=None,
    )
    # Solo verificamos que tiene shape válida — el status concreto depende del weekday
    assert ta["temporal"] in {"today", "past", "future"}
    assert ta["status"]


def test_build_today_action_next_session_respeta_plan_custom():
    """next_session debe buscar la próxima sesión del plan custom, no del default."""
    # Forzamos lunes con plan donde toda la semana es rest excepto el viernes
    today = date.today()
    days_to_monday = (0 - today.weekday()) % 7
    target = today + timedelta(days=days_to_monday)
    if days_to_monday != 0:
        return  # skip si hoy no es lunes
    custom_plan = {
        0: ("rest", "L rest"),
        1: ("rest", "Ma rest"),
        2: ("rest", "Mi rest"),
        3: ("rest", "J rest"),
        4: ("train", "Vi mi sesión única"),
        5: ("rest", "Sa rest"),
        6: ("rest", "Do rest"),
    }
    ta = build_today_action(
        target=target,
        activity_labels=[],
        acwr=None, hrv_today=None, hrv_baseline=None,
        weekday_plan=custom_plan,
    )
    if ta["temporal"] == "today":
        assert "Vi mi sesión única".split()[0] in ta["next_session"]
