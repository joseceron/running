"""Verifica que el payload enviado a Claude para `/diagnosis` incluye el
campo `today_action` con la decisión inequívoca del plan/HRV/ACWR.

Fix del 2026-05-24: el LLM no recibía today_action y podía recomendar
"ejecuta 45 min" un día marcado como DESCANSO. La regla #6 del system prompt
exige consistencia, pero la regla solo sirve si el dato llega — este test
blinda eso.

No usa Docker: mockea repos y el cliente de Anthropic.
"""

from __future__ import annotations

import json
import os
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


# Aseguramos que el módulo crea el cliente solo cuando hay api key.
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-test-fake")


def _stub_profile() -> SimpleNamespace:
    return SimpleNamespace(
        name="Tester",
        age=36,
        height_cm=170.0,
        weight_kg=68.0,
        max_hr=185,
        resting_hr=51,
        city="Bogotá",
        altitude_msnm=2640,
        injury_history=[],
        weekly_plan=None,
        goal_event="Half marathon",
        goal_date=date.today() + timedelta(days=120),
        goal_time_secs=6600,
    )


def _stub_hrv_night(value: float, d: date) -> SimpleNamespace:
    return SimpleNamespace(date=d, hrv_rmssd=value)


@pytest.fixture
def fake_anthropic_response():
    """Construye una respuesta válida de Anthropic con JSON coherente."""
    body = json.dumps({
        "narrative": "Test narrative.",
        "action": "Hidrátate y descansa hoy.",
        "citation": "Buchheit (2014) · Front Physiol · Review",
        "alert_level": "info",
    })
    usage = SimpleNamespace(
        input_tokens=10,
        output_tokens=10,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=0,
    )
    return SimpleNamespace(
        content=[SimpleNamespace(text=body)],
        usage=usage,
    )


def _patch_repos(*, hrv_baseline: float | None, latest_hrv: float | None,
                 days_recorded: int, days_required: int, acwr: float | None):
    """Devuelve los context managers para parchear repos del módulo."""
    profile_patch = patch(
        "agents.diagnostic_v2.runner_profile.get",
        return_value=_stub_profile(),
    )
    baseline_patch = patch(
        "agents.diagnostic_v2.hrv_repo.get_baseline",
        return_value=hrv_baseline,
    )
    progress_patch = patch(
        "agents.diagnostic_v2.hrv_repo.get_baseline_progress",
        return_value=(days_recorded, days_required),
    )
    nights = (
        [_stub_hrv_night(latest_hrv, date.today())] if latest_hrv is not None else []
    )
    recent_patch = patch(
        "agents.diagnostic_v2.hrv_repo.get_recent",
        return_value=nights,
    )
    weekly_patch = patch(
        "agents.diagnostic_v2.weekly_repo.get_history",
        return_value=[
            SimpleNamespace(
                week_start=date.today() - timedelta(days=7),
                plan_km=20.0,
                executed_km=10.0,
                avg_hrv=latest_hrv or 55.0,
                acwr=acwr,
                agent_notes=None,
            )
        ],
    )
    return [profile_patch, baseline_patch, progress_patch, recent_patch, weekly_patch]


def _run_generate(fake_response, *, target: date | None = None) -> str:
    """Ejecuta generate_diagnosis interceptando Anthropic y devuelve el user_message."""
    from agents.diagnostic_v2 import generate_diagnosis

    captured = {}

    def _capture(**kwargs):
        captured["messages"] = kwargs["messages"]
        return fake_response

    fake_client = MagicMock()
    fake_client.messages.create.side_effect = _capture

    with patch("agents.diagnostic_v2.Anthropic", return_value=fake_client):
        generate_diagnosis(session=MagicMock(), user_id="u_test", target_date=target)

    # El user_message va como content del único mensaje
    return captured["messages"][0]["content"]


# ─── Tests ────────────────────────────────────────────────────────────


class TestPayloadIncluyeTodayAction:
    def test_payload_lleva_today_action(self, fake_anthropic_response) -> None:
        """El payload del LLM SIEMPRE debe traer el campo today_action."""
        patches = _patch_repos(
            hrv_baseline=55.0,
            latest_hrv=53.0,
            days_recorded=14,
            days_required=14,
            acwr=1.0,
        )
        for p in patches:
            p.start()
        try:
            msg = _run_generate(fake_anthropic_response)
        finally:
            for p in patches:
                p.stop()

        assert "today_action" in msg
        # El payload está embebido como JSON dentro del string del user_message
        # — verificamos que se puede leer el bloque y que tiene los campos clave.
        json_start = msg.find("{")
        json_end = msg.rfind("}") + 1
        payload = json.loads(msg[json_start:json_end])
        assert "today_action" in payload
        ta = payload["today_action"]
        assert "status" in ta
        assert "headline" in ta
        assert "short_reason" in ta
        assert "reasons" in ta
        assert ta["status"] in {
            "rest", "train", "active_recovery", "trained_already",
            "past_executed", "past_rest_planned", "past_missed",
            "future_planned",
        }

    def test_hrv_suprimido_inyecta_rest_en_payload(self, fake_anthropic_response) -> None:
        """HRV muy bajo → today_action.status='rest' en el payload."""
        patches = _patch_repos(
            hrv_baseline=55.0,
            latest_hrv=40.0,  # bien debajo de baseline - 4.7
            days_recorded=14,
            days_required=14,
            acwr=1.0,
        )
        for p in patches:
            p.start()
        try:
            msg = _run_generate(fake_anthropic_response)
        finally:
            for p in patches:
                p.stop()

        payload = json.loads(msg[msg.find("{"):msg.rfind("}") + 1])
        assert payload["today_action"]["status"] == "rest"
        # Y el system prompt debe estar dándole al LLM la regla #6
        from agents.diagnostic_v2 import SYSTEM_PROMPT
        assert "CONSISTENCIA CON EL PLAN" in SYSTEM_PROMPT
        # La regla debe prohibir mandar a entrenar cuando today_action es rest.
        # Acepta espacios extra porque las continuaciones \ del docstring los introducen.
        normalized = " ".join(SYSTEM_PROMPT.split())
        assert "PROHIBIDO mandar a correr" in normalized

    def test_dia_futuro_inyecta_future_planned(self, fake_anthropic_response) -> None:
        """Si target es futuro, today_action debe estar y ser future_planned."""
        patches = _patch_repos(
            hrv_baseline=55.0,
            latest_hrv=55.0,
            days_recorded=14,
            days_required=14,
            acwr=1.0,
        )
        for p in patches:
            p.start()
        try:
            msg = _run_generate(
                fake_anthropic_response,
                target=date.today() + timedelta(days=3),
            )
        finally:
            for p in patches:
                p.stop()

        payload = json.loads(msg[msg.find("{"):msg.rfind("}") + 1])
        assert payload["today_action"]["status"] == "future_planned"
        assert payload["today_action"]["temporal"] == "future"
