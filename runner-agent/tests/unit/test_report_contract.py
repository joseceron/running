"""Contract tests para `/v1/users/me/report`.

OBJETIVO: garantizar que el shape del response NO se rompa silenciosamente,
porque cuando un campo desaparece el frontend renderiza `undefined.length`
y crashea con 500 en SSR (ya pasó 2026-05-24 — ver project_deploy_proceso.md).

ESTRATEGIA: testeamos las funciones puras de cálculo (sin DB) verificando
que devuelven Pydantic models válidos con TODOS los campos que el frontend
consume. Si añades un field nuevo al modelo backend, añadirlo aquí también.
"""

from __future__ import annotations

from datetime import date, timedelta

from api.routers.report import (
    ActivityTodayOut,
    FatBurnOut,
    HeartProgressOut,
    HydrationTipOut,
    MacroTipOut,
    NutritionOut,
    PolarizationOut,
    TodayActionOut,
    _build_heart_progress,
    _build_nutrition,
    _build_polarization,
    _build_today_action,
    _calc_fat_burn,
)


# ─── TodayAction: contract para los 4 escenarios principales ──────────


class TestTodayActionContract:
    """El frontend (TodayActionCard.tsx) consume: status, temporal, headline,
    short_reason, reasons[], allowed[], next_session. Todos deben venir."""

    def _assert_full_shape(self, ta: TodayActionOut) -> None:
        assert isinstance(ta, TodayActionOut)
        # Todos los campos requeridos del frontend
        assert ta.status in {
            "rest", "train", "active_recovery", "trained_already",
            "past_executed", "past_rest_planned", "past_missed",
            "future_planned",
        }, f"status inválido: {ta.status}"
        assert ta.temporal in {"today", "past", "future"}
        assert isinstance(ta.headline, str) and ta.headline, "headline vacío"
        assert isinstance(ta.short_reason, str) and ta.short_reason
        assert isinstance(ta.reasons, list)  # puede ser []
        assert isinstance(ta.allowed, list)
        assert isinstance(ta.next_session, str)  # "" para pasado/futuro está OK

    def _today_with_weekday(self, target_wd: int) -> date:
        """Devuelve la fecha más cercana a hoy cuyo weekday sea target_wd,
        usando freezegun-style — pero NO movemos el reloj real. Como la lógica
        decide pasado/hoy/futuro contra date.today(), tenemos que usar
        date.today() directo y pasar un weekday que coincida. Para tests
        deterministas usamos siempre `date.today()`."""
        return date.today()

    def test_hoy_se_clasifica_como_today_y_no_pasado(self) -> None:
        # Independiente del weekday, hoy SIEMPRE es temporal=today
        today = date.today()
        ta = _build_today_action(today, [], acwr=1.05, hrv_today=53.0, hrv_baseline=55.0)
        self._assert_full_shape(ta)
        assert ta.temporal == "today"

    def test_hoy_ya_entreno(self) -> None:
        today = date.today()
        acts = [ActivityTodayOut(hour=7.6, label="Caminata · 5.77 km", type="run")]
        ta = _build_today_action(today, acts, acwr=1.0, hrv_today=55.0, hrv_baseline=55.0)
        self._assert_full_shape(ta)
        assert ta.status == "trained_already"
        assert ta.temporal == "today"

    def test_hoy_acwr_alto_y_plan_train_fuerza_recuperacion(self) -> None:
        # Solo aplica si HOY el plan dice train. Si hoy es domingo (rest),
        # entonces ACWR alto + rest queda como rest. Cubrimos ambos casos.
        today = date.today()
        ta = _build_today_action(today, [], acwr=1.6, hrv_today=55.0, hrv_baseline=55.0)
        self._assert_full_shape(ta)
        # Si hoy es día de descanso programado, ACWR alto no fuerza recovery
        # (descanso ya es suficiente). Si hoy es día de train, sí.
        assert ta.status in {"active_recovery", "rest"}
        assert ta.temporal == "today"

    def test_hoy_hrv_suprimido_fuerza_descanso(self) -> None:
        today = date.today()
        # HRV muy por debajo de baseline (>1 SD) → siempre rest
        ta = _build_today_action(today, [], acwr=1.0, hrv_today=45.0, hrv_baseline=55.0)
        self._assert_full_shape(ta)
        assert ta.status == "rest"
        assert ta.temporal == "today"

    def test_pasado_ejecutado(self) -> None:
        # Día antes de hoy con actividades
        yesterday = date.today() - timedelta(days=1)
        acts = [ActivityTodayOut(hour=7.5, label="Carrera · 5km", type="run")]
        ta = _build_today_action(yesterday, acts, acwr=1.1, hrv_today=55.0, hrv_baseline=55.0)
        self._assert_full_shape(ta)
        assert ta.temporal == "past"
        assert ta.status == "past_executed"
        assert ta.next_session == ""  # pasado no muestra next

    def test_pasado_descanso_programado(self) -> None:
        # Domingo pasado, sin actividades — plan dice rest
        many_days_ago = date.today() - timedelta(days=14)
        # Asegurar que ese día es domingo (weekday=6); si no, ajustar
        while many_days_ago.weekday() != 6:
            many_days_ago = many_days_ago - timedelta(days=1)
        ta = _build_today_action(many_days_ago, [], None, None, None)
        self._assert_full_shape(ta)
        assert ta.status == "past_rest_planned"

    def test_futuro_planificado(self) -> None:
        tomorrow = date.today() + timedelta(days=2)
        ta = _build_today_action(tomorrow, [], None, None, None)
        self._assert_full_shape(ta)
        assert ta.temporal == "future"
        assert ta.status == "future_planned"

    def test_wrapper_acepta_weekday_plan_kwarg(self) -> None:
        """Regresión: report.py:945 llama al wrapper con weekday_plan=... .
        Si el wrapper no acepta ese kwarg, /report devuelve 500."""
        today = date.today()
        custom = {
            "0": ["rest", "Override lunes"],
            "1": ["train", "Override martes"],
            "2": ["rest", "Override miércoles"],
            "3": ["train", "Override jueves"],
            "4": ["train", "Override viernes"],
            "5": ["train", "Override sábado"],
            "6": ["rest", "Override domingo"],
        }
        # Llamada exacta como en report.py
        ta = _build_today_action(
            target=today,
            activities_today=[],
            acwr=1.0,
            hrv_today=55.0,
            hrv_baseline=55.0,
            weekday_plan=custom,
        )
        self._assert_full_shape(ta)
        # Y también con None (cuando profile.weekly_plan no está seteado)
        ta_default = _build_today_action(
            target=today,
            activities_today=[],
            acwr=1.0,
            hrv_today=55.0,
            hrv_baseline=55.0,
            weekday_plan=None,
        )
        self._assert_full_shape(ta_default)


# ─── Nutrition: el frontend usa real_world_examples + *_examples ──────


class TestNutritionContract:
    """Estos campos son los que rompieron prod el 2026-05-24 al faltar.
    NO eliminar este test sin un ADR explícito."""

    def test_nutrition_full_shape(self) -> None:
        n = _build_nutrition(
            weight_kg=68.0,
            activities_today=[],
            latest_activity=None,
            altitude_msnm=1736,
            is_today=True,
        )
        assert isinstance(n, NutritionOut)
        assert isinstance(n.hydration, HydrationTipOut)
        assert isinstance(n.macros, MacroTipOut)
        # CAMPOS QUE EL FRONTEND CONSUME (NutritionCard.tsx)
        assert isinstance(n.hydration.real_world_examples, list), \
            "Frontend espera real_world_examples (lista). Si lo cambias, actualiza NutritionCard.tsx"
        assert len(n.hydration.real_world_examples) >= 1
        assert isinstance(n.macros.carbs_examples, str), \
            "Frontend usa carbs_examples (string)"
        assert n.macros.carbs_examples != "" or n.macros.kcal_estimadas == 0
        assert isinstance(n.macros.protein_examples, str)
        assert isinstance(n.macros.fat_examples, str)
        # Citation y CTA
        assert n.citation and "ACSM" in n.citation
        assert "Luz Dálida" in n.expert_cta

    def test_nutrition_con_actividad_intensa_pide_electrolitos(self) -> None:
        latest = {
            "duration_secs": 3900,  # 65 min
            "zone_distribution_pct": [10, 40, 20, 20, 10],  # Z4+Z5 = 30%
        }
        n = _build_nutrition(
            weight_kg=68.0,
            activities_today=[ActivityTodayOut(hour=7.0, label="x", type="run")],
            latest_activity=latest,
            altitude_msnm=1736,
            is_today=True,
        )
        assert n.hydration.electrolytes_needed is True
        # Debe haber ejemplos prácticos de bebida con electrolitos
        joined = " ".join(n.hydration.real_world_examples).lower()
        assert "sal" in joined or "electrolitos" in joined or "suero" in joined


# ─── Insights científicos ──────────────────────────────────────────────


class TestInsightsContract:
    def test_fat_burn_breakdown(self) -> None:
        activity = {
            "name": "Test",
            "calories": 343,
            "zone_distribution_pct": [66, 33, 1, 0, 0],
        }
        fb = _calc_fat_burn(activity)
        assert isinstance(fb, FatBurnOut)
        # Frontend (FatBurnCard) consume:
        assert fb.activity_name == "Test"
        assert fb.total_kcal == 343
        assert fb.fat_kcal > 0
        assert fb.fat_grams > 0
        assert len(fb.by_zone) == 5
        for z in fb.by_zone:
            # Each zone object debe tener todos los campos del frontend
            assert z.zone in {1, 2, 3, 4, 5}
            assert z.label
            assert z.fat_pct in {80, 65, 40, 20, 5}

    def test_fat_burn_sin_zonas_retorna_none(self) -> None:
        # Sin zone_distribution → None, no excepción
        assert _calc_fat_burn({"calories": 100}) is None
        assert _calc_fat_burn({"calories": 0, "zone_distribution_pct": [50, 50, 0, 0, 0]}) is None

    def test_polarization_aligned(self) -> None:
        # 80% Z1-Z2 + 20% Z4-Z5 = alineado con Seiler
        activity = {"zone_distribution_pct": [40, 40, 0, 15, 5]}
        p = _build_polarization(activity)
        assert isinstance(p, PolarizationOut)
        assert p.evaluation == "aligned"

    def test_polarization_too_easy(self) -> None:
        # 99% Z1-Z2, sin calidad
        activity = {"zone_distribution_pct": [66, 33, 1, 0, 0]}
        p = _build_polarization(activity)
        assert p.evaluation == "too_easy"

    def test_heart_progress_improving(self) -> None:
        hp = _build_heart_progress(rhr_today=50, rhr_baseline=51.0)
        assert isinstance(hp, HeartProgressOut)
        assert hp.rhr_trend == "improving"
        # Frontend espera estos campos exactos
        assert hp.explanation
        assert hp.citation
