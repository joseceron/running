"""Endpoint /v1/users/me/report — payload del reporte diario completo (8 secciones).

Combina cache de cronología + cache de última actividad + Postgres (HRV/weekly).
Calcula los gates de progresión y emite recomendación + interpretación.
"""

from __future__ import annotations

import json  # noqa: F401 (usado más abajo)
import logging
from datetime import date as DateT, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)
from statistics import mean
from typing import Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agents.today_action_builder import (
    WEEKDAY_PLAN,
    build_today_action,
)
from api.deps import get_current_user_id, get_db
from api.utils.timezone import local_today
from memory.repositories import activities as activities_repo
from memory.repositories import hrv as hrv_repo
from memory.repositories import runner_profile

router = APIRouter(prefix="/users/me", tags=["report"])

CACHE_DIR = Path("/tmp/liebre_cache")


# ─── Schemas ─────────────────────────────────────────────


class ActivityTodayOut(BaseModel):
    hour: float
    label: str
    type: str


class BiomechanicsOut(BaseModel):
    cadence_spm: int | None = None
    stride_m: float | None = None
    gct_ms: int | None = None
    cadence_avg_7: float | None = None
    gct_avg_7: float | None = None
    cadence_delta: float | None = None
    gct_delta: float | None = None
    is_walk: bool = False


class GateOut(BaseModel):
    label: str
    status: Literal["green", "yellow", "red"]
    detail: str


class HeartOut(BaseModel):
    resting_hr: int | None = None
    resting_hr_baseline: float = 50.5
    resting_hr_delta: float | None = None
    hrv_last_night: float | None = None
    hrv_baseline: float | None = None
    hrv_state: str
    vo2max: float | None = 46.4


class LoadOut(BaseModel):
    body_battery_max: int | None = None
    body_battery_min: int | None = None
    stress_avg: int | None = None
    acwr: float | None = None
    acwr_zone: str


# ─── Insights científicos (diferencial Liebre) ────────────


class FatBurnZone(BaseModel):
    zone: int
    label: str
    pct_time: float
    kcal_total: float
    kcal_fat: float
    kcal_cho: float
    fat_pct: int  # % de calorías que viene de grasa en esta zona


class FatBurnOut(BaseModel):
    """FatMax: estimación de oxidación de grasa por zona FC en la última sesión.
    Fórmula derivada de Achten & Jeukendrup (2004) y guidelines de FatMax:
    en Z1 ~80% energía viene de grasa, Z2 ~65%, Z3 ~40%, Z4 ~20%, Z5 ~5%."""
    activity_name: str
    total_kcal: int
    fat_kcal: int
    cho_kcal: int
    fat_grams: float  # kcal_fat / 9
    by_zone: list[FatBurnZone]
    citation: str = "Achten & Jeukendrup (2004) · Int J Sports Med · Review"


class CardiacDriftOut(BaseModel):
    """Drift FC primera vs segunda mitad — eficiencia cardiaca."""
    activity_name: str
    first_half_hr: float
    second_half_hr: float
    drift_pct: float
    evaluation: str  # "eficiente" / "regular" / "base aún verde"
    citation: str = "Lamberts & Lambert (2009) · J Strength Cond Res · Observacional"


class HeartProgressOut(BaseModel):
    """FC reposo + qué le está pasando al corazón."""
    rhr_current: int
    rhr_baseline: float
    rhr_trend: str  # "improving" / "stable" / "regressing"
    explanation: str
    citation: str = "Seiler (2010) · Int J Sports Physiol Perform · Review"


class PolarizationOut(BaseModel):
    """Distribución 80/20 — Seiler."""
    z1_z2_pct: float
    z3_pct: float
    z4_z5_pct: float
    ideal_z1_z2_pct: int = 80
    ideal_z3_pct: int = 0
    ideal_z4_z5_pct: int = 20
    evaluation: str  # "aligned" / "too_easy" / "too_hard" / "mixed"
    source_label: str  # "última carrera" / "últimos 7 días" según lo disponible
    citation: str = "Seiler (2010) · Int J Sports Physiol Perform · Review"


class InsightsOut(BaseModel):
    """Análisis científicos — el diferencial Liebre vs Connect."""
    fat_burn: FatBurnOut | None = None
    cardiac_drift: CardiacDriftOut | None = None
    heart_progress: HeartProgressOut | None = None
    polarization: PolarizationOut | None = None


class TodayActionOut(BaseModel):
    """Recomendación inequívoca para la fecha consultada.

    `temporal` distingue 3 casos visuales/semánticos:
    - `today`: lo que tiene que hacer HOY (lógica original)
    - `past`: vista retrospectiva — qué hizo o no hizo ese día
    - `future`: vista anticipada — qué tiene planificado
    """
    status: Literal[
        # Estados de HOY
        "rest", "train", "active_recovery", "trained_already",
        # Estados de PASADO
        "past_executed", "past_rest_planned", "past_missed",
        # Estado FUTURO
        "future_planned",
    ]
    temporal: Literal["today", "past", "future"]
    headline: str  # "DESCANSA HOY" / "EJECUTADO ✓" / "NO SE REALIZÓ" / "PLANIFICADO"
    short_reason: str  # 1 frase, lo que se ve grande
    reasons: list[str]  # bullets con datos objetivos
    allowed: list[str]  # qué SÍ se puede hacer (vacío si es pasado)
    next_session: str  # qué viene después (vacío si es futuro)


class HydrationTipOut(BaseModel):
    water_ml: int
    electrolytes_needed: bool
    pre_session_ml: int
    during_session_ml_per_hour: int
    post_session_ml: int
    notes: list[str]
    # Ejemplos humanos (qué comer/beber, no solo "agua + electrolitos")
    real_world_examples: list[str] = Field(default_factory=list)


class MacroTipOut(BaseModel):
    fase: str  # "carga" / "recuperación" / "mantenimiento"
    kcal_estimadas: int
    carbs_g: int
    protein_g: int
    fat_g: int
    timing_notes: list[str]
    # Ejemplos de plato real para cada macro
    carbs_examples: str = ""
    protein_examples: str = ""
    fat_examples: str = ""


class EnvironmentTipOut(BaseModel):
    altitude_msnm: int
    sun_intensity: str  # "alta" / "media" / "baja"
    sunscreen_spf: int
    sunscreen_reapply_min: int
    extra_notes: list[str]


class NutritionOut(BaseModel):
    hydration: HydrationTipOut
    macros: MacroTipOut
    environment: EnvironmentTipOut
    expert_cta: str  # texto del CTA para futura cita con nutricionista
    citation: str = "ACSM Joint Position Statement (2007) · Burke (2007) Sports Nutr Series"


class PhysioContextOut(BaseModel):
    """Base fisiológica que justifica las duraciones recomendadas en today_action."""
    z2_hr_low: int
    z2_hr_high: int
    max_hr: int
    resting_hr: int
    goal_pace_per_km: str       # "5:13/km"
    weeks_to_goal: int
    training_phase: str          # "Base" / "Construcción" / "Pico" / "Tapering"
    session_duration_rationale: str
    citation: str = "Karvonen (1957) · Seiler (2010) · Esteve-Lanao (2007)"


class ReportOut(BaseModel):
    date: DateT
    today_action: TodayActionOut
    activities_today: list[ActivityTodayOut]
    biomechanics: BiomechanicsOut | None
    heart: HeartOut
    load: LoadOut
    gates: list[GateOut]
    interpretation: list[str] = Field(default_factory=list)
    insights: InsightsOut | None = None  # diferencial científico
    nutrition: NutritionOut | None = None  # diferencial: nutrición + monetización Luz Dálida
    physio_context: PhysioContextOut | None = None


# ─── Helpers ─────────────────────────────────────────────


def _read_cronologia(user_id: str, target: DateT) -> dict | None:
    path = CACHE_DIR / f"cronologia_{user_id}_{target.isoformat()}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _read_latest_activity(user_id: str) -> dict | None:
    path = CACHE_DIR / f"activity_{user_id}_latest.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _is_walk(distance_km: float, duration_secs: int, activity_type: str = "") -> bool:
    """Caminata si Garmin lo tipifica explícitamente como walking/hiking,
    o si el pace supera 11:00/km (660 s/km). Z2 lento (~9-10:30/km) no
    es caminata — es trote aeróbico controlado por FC."""
    if activity_type in ("walking", "hiking", "walk"):
        return True
    if distance_km <= 0 or duration_secs <= 0:
        return False
    pace = duration_secs / distance_km
    return pace > 660  # > 11:00/km


# ─── Insights: FatMax por zona ─────────────────────────────

# Fracción de energía proveniente de grasa por zona FC.
# Aproximación de Achten & Jeukendrup (FatMax) y guidelines clásicas:
# Z1 (50-60% FCmáx): ~80% grasa
# Z2 (60-70% FCmáx): ~65% grasa
# Z3 (70-80% FCmáx): ~40% grasa
# Z4 (80-90% FCmáx): ~20% grasa
# Z5 (>90% FCmáx): ~5% grasa
FAT_PCT_BY_ZONE = [80, 65, 40, 20, 5]
ZONE_LABELS = ["Z1 · recuperación", "Z2 · base aeróbica", "Z3 · umbral aeróbico", "Z4 · VO₂máx", "Z5 · anaeróbico"]


def _calc_fat_burn(activity: dict) -> FatBurnOut | None:
    total_kcal = activity.get("calories") or 0
    zone_pct = activity.get("zone_distribution_pct") or []
    if total_kcal <= 0 or len(zone_pct) < 5:
        return None

    by_zone: list[FatBurnZone] = []
    fat_total = 0.0
    for i in range(5):
        pct_time = zone_pct[i] or 0
        kcal_z = total_kcal * (pct_time / 100)
        fat_pct = FAT_PCT_BY_ZONE[i]
        fat_z = kcal_z * (fat_pct / 100)
        cho_z = kcal_z - fat_z
        fat_total += fat_z
        by_zone.append(
            FatBurnZone(
                zone=i + 1,
                label=ZONE_LABELS[i],
                pct_time=round(pct_time, 1),
                kcal_total=round(kcal_z, 1),
                kcal_fat=round(fat_z, 1),
                kcal_cho=round(cho_z, 1),
                fat_pct=fat_pct,
            )
        )

    return FatBurnOut(
        activity_name=activity.get("name") or "Última sesión",
        total_kcal=round(total_kcal),
        fat_kcal=round(fat_total),
        cho_kcal=round(total_kcal - fat_total),
        fat_grams=round(fat_total / 9, 1),
        by_zone=by_zone,
    )


# ─── Insights: cardiac drift ────────────────────────────────


def _calc_cardiac_drift(activity: dict) -> CardiacDriftOut | None:
    samples = activity.get("samples") or []
    # Filtrar samples con HR válido tras los primeros 5 min (warmup)
    valid = [
        s for s in samples
        if s.get("hr") and s.get("t_secs") is not None and s["t_secs"] >= 300
    ]
    if len(valid) < 20:
        return None
    mid = len(valid) // 2
    first_half = valid[:mid]
    second_half = valid[mid:]
    hr1 = sum(s["hr"] for s in first_half) / len(first_half)
    hr2 = sum(s["hr"] for s in second_half) / len(second_half)
    drift = (hr2 - hr1) / hr1 * 100 if hr1 > 0 else 0

    if drift < 5:
        evaluation = "eficiente — corazón mantiene FC estable, sin fatiga"
    elif drift < 10:
        evaluation = "regular — algo de fatiga acumulada en la segunda mitad"
    else:
        evaluation = "base aún verde — la FC se va arriba a pesar del mismo esfuerzo"

    return CardiacDriftOut(
        activity_name=activity.get("name") or "Última sesión",
        first_half_hr=round(hr1, 1),
        second_half_hr=round(hr2, 1),
        drift_pct=round(drift, 2),
        evaluation=evaluation,
    )


# ─── Insights: heart progress (hipertrofia VI) ─────────────


def _build_heart_progress(rhr_today: int | None, rhr_baseline: float) -> HeartProgressOut:
    rhr_current = rhr_today or int(rhr_baseline)
    # Sin histórico, hacemos lectura del estado: si está dentro de baseline o por debajo → improving
    if rhr_current <= rhr_baseline:
        trend = "improving"
        explanation = (
            f"Tu FC de reposo en {rhr_current} lpm está alineada con tu baseline ({rhr_baseline:.0f}). "
            "El Z2 prolongado provoca hipertrofia excéntrica del ventrículo izquierdo: la cámara cardíaca "
            "se agranda, sube el volumen sistólico y baja la FC reposo. Es la adaptación que más se traduce "
            "en rendimiento sostenido para 21K. Si bajas otros 3-4 lpm en las próximas 6 semanas, vas en ruta."
        )
    elif rhr_current <= rhr_baseline + 4:
        trend = "stable"
        explanation = (
            f"FC de reposo {rhr_current} lpm — levemente sobre tu baseline ({rhr_baseline:.0f}). "
            "Puede ser estrés externo, sueño insuficiente o carga acumulada de la semana. Una noche no es tendencia."
        )
    else:
        trend = "regressing"
        explanation = (
            f"FC de reposo {rhr_current} lpm — significativamente sobre baseline ({rhr_baseline:.0f}). "
            "Señal de fatiga acumulada. Considera día suave + dormir 8h+ con el reloj puesto para HRV."
        )

    return HeartProgressOut(
        rhr_current=rhr_current,
        rhr_baseline=rhr_baseline,
        rhr_trend=trend,
        explanation=explanation,
    )


# ─── Insights: polarización 80/20 ───────────────────────────


# ─── Today action: heurística HOY ────────────────────────────
# La lógica vive ahora en agents.today_action_builder para que el LLM de
# diagnóstico la consuma también. WEEKDAY_PLAN se re-exporta para no romper
# imports existentes.


def _build_today_action(
    target: DateT,
    activities_today: list,
    acwr: float | None,
    hrv_today: float | None,
    hrv_baseline: float | None,
    hrv_sd: float = 4.7,
    weekday_plan: dict | None = None,
) -> TodayActionOut:
    """Wrapper Pydantic sobre `build_today_action` (lógica compartida).

    Acepta `activities_today` como lista de `ActivityTodayOut` (lo que ya pasa
    el endpoint) y extrae los labels para el builder agnóstico. `weekday_plan`
    es el override per-user (runner_profile.weekly_plan JSONB).
    """
    labels = [a.label for a in activities_today if getattr(a, "label", None)]
    data = build_today_action(
        target=target,
        activity_labels=labels,
        acwr=acwr,
        hrv_today=hrv_today,
        hrv_baseline=hrv_baseline,
        hrv_sd=hrv_sd,
        weekday_plan=weekday_plan,
    )
    return TodayActionOut(**data)


# ─── Nutrición e hidratación ────────────────────────────────


def _build_nutrition(
    weight_kg: float,
    activities_today: list,
    latest_activity: dict | None,
    altitude_msnm: int = 0,
    is_today: bool = True,
) -> NutritionOut:
    """Cálculos automáticos basados en peso, actividad y clima.

    Base: ACSM Joint Position Statement 2007 + Burke (2007) Sports Nutrition Series.
    """
    # ── Hidratación base: ~35 ml/kg/día + extra por sesión ─────
    base_ml = int(weight_kg * 35)
    extra_ml = 0
    duration_min = 0
    high_intensity = False

    if latest_activity and is_today:
        duration_min = (latest_activity.get("duration_secs") or 0) / 60
        zones = latest_activity.get("zone_distribution_pct") or []
        if zones and len(zones) >= 5:
            high_intensity = (zones[3] + zones[4]) > 15
        # ~500-800 ml por hora de actividad moderada, hasta 1L en intensa
        per_hour = 700 if high_intensity else 500
        extra_ml = int(duration_min / 60 * per_hour)

    total_ml = base_ml + extra_ml
    electrolytes = high_intensity or duration_min > 60 or altitude_msnm > 1500

    hydration_notes = [
        f"Base: {base_ml} ml (~35 ml × {weight_kg:.0f} kg)",
    ]
    if extra_ml > 0:
        hydration_notes.append(
            f"+{extra_ml} ml por sesión de {duration_min:.0f} min ({'alta' if high_intensity else 'moderada'} intensidad)"
        )
    if electrolytes:
        hydration_notes.append(
            "Necesitas electrolitos (sodio/potasio): sesión larga, intensa o en altitud"
        )
    if altitude_msnm > 1500:
        hydration_notes.append(
            f"Altitud {altitude_msnm} msnm aumenta pérdida de agua por respiración — +300-500 ml/día extra"
        )

    pre_ml = int(min(500, total_ml * 0.15))
    during_ml_h = 600 if high_intensity else 400 if duration_min > 0 else 0
    post_ml = int(extra_ml * 1.5) if extra_ml else 0

    # Ejemplos humanos de hidratación + electrolitos (cómo se ve en la vida real)
    real_examples: list[str] = [
        f"≈ {total_ml // 250} vasos de 250 ml repartidos en el día",
    ]
    if electrolytes:
        real_examples.append(
            "Bebida de electrolitos casera: 500 ml de agua + ¼ cdita de sal marina + jugo de ½ limón + 1 cdita de miel"
        )
        real_examples.append(
            "Alternativa empacada: Suero Oral, Powerade Zero, o Gatorade diluido 1:1 con agua"
        )
        real_examples.append(
            "Fuentes naturales de potasio: 1 plátano (~420 mg) o 1 puñado de uvas pasas"
        )
    if duration_min > 0:
        real_examples.append(
            f"Durante una sesión de {duration_min:.0f} min: sorbos de ~150 ml cada 15 min"
        )

    hydration = HydrationTipOut(
        water_ml=total_ml,
        electrolytes_needed=electrolytes,
        pre_session_ml=pre_ml,
        during_session_ml_per_hour=during_ml_h,
        post_session_ml=post_ml,
        notes=hydration_notes,
        real_world_examples=real_examples,
    )

    # ── Macros: estimación según fase del día ────────────────
    # Carga: día de entreno duro / Recuperación: post sesión / Mantenimiento: resto
    if activities_today and high_intensity:
        fase = "carga"
        carbs_per_kg = 6
        protein_per_kg = 1.6
        fat_g = int(weight_kg * 1.0)
        timing = [
            "Pre-sesión (2-3h antes): 80-120g carbs + 20g proteína",
            "Durante (>60min): 30-60g carbs/hora (gel o bebida)",
            "Post-sesión (30 min): 1g carbs/kg + 20-25g proteína",
        ]
    elif activities_today:
        fase = "recuperación"
        carbs_per_kg = 5
        protein_per_kg = 1.6
        fat_g = int(weight_kg * 1.0)
        timing = [
            "Post-sesión inmediato: 25-30g proteína (síntesis muscular)",
            "Carbs distribuidos en 3-4 comidas para reponer glucógeno",
        ]
    else:
        fase = "mantenimiento"
        carbs_per_kg = 4
        protein_per_kg = 1.4
        fat_g = int(weight_kg * 1.0)
        timing = [
            "Día de descanso: foco en proteína para reparación muscular",
            "Carbs moderados — el músculo absorbe mejor en próximo entreno",
        ]

    carbs_g = int(weight_kg * carbs_per_kg)
    protein_g = int(weight_kg * protein_per_kg)
    kcal = carbs_g * 4 + protein_g * 4 + fat_g * 9

    # Ejemplos reales por macro — para que el usuario sepa de dónde sacarlo
    carbs_examples = (
        f"{carbs_g}g se reparten así durante el día: "
        f"1 plato de arroz cocido (~45g), 2 rebanadas de pan integral (~30g), "
        f"1 plátano (~27g), 1 papa mediana (~37g), 1 porción de avena cocida (~28g). "
        "Distribuir en 3-4 comidas."
    )
    protein_examples = (
        f"{protein_g}g se cubren con: 1 pechuga de pollo de 150g (~33g), "
        f"3 huevos (~18g), 1 lata de atún (~25g), 1 vaso de leche (~8g), "
        "100g de lentejas cocidas (~9g) o 1 yogur griego (~15g)."
    )
    fat_examples = (
        f"{fat_g}g de grasa saludable: ½ aguacate (~15g), 1 cda de aceite de oliva (~14g), "
        "1 puñado de almendras (~14g), 1 cda de mantequilla de maní (~8g). "
        "Evitar fritos y procesados."
    )

    macros = MacroTipOut(
        fase=fase,
        kcal_estimadas=kcal,
        carbs_g=carbs_g,
        protein_g=protein_g,
        fat_g=fat_g,
        timing_notes=timing,
        carbs_examples=carbs_examples,
        protein_examples=protein_examples,
        fat_examples=fat_examples,
    )

    # ── Factor ambiental: bloqueador solar + altitud ─────────
    # UV aumenta ~10% por cada 1000m de altitud
    sun_intensity = "alta" if altitude_msnm > 1500 else "media"
    spf = 50 if altitude_msnm > 1500 else 30
    extra_env = [
        f"Altitud {altitude_msnm} msnm: UV ~{int((altitude_msnm/1000)*10)}% más fuerte que a nivel del mar",
    ]
    if activities_today:
        extra_env.append("Aplicar bloqueador 20 min antes del entreno; reaplicar tras sudar")
    extra_env.append("Labios secos / boca pastosa son señal tardía de deshidratación — actúa antes")

    environment = EnvironmentTipOut(
        altitude_msnm=altitude_msnm,
        sun_intensity=sun_intensity,
        sunscreen_spf=spf,
        sunscreen_reapply_min=80,
        extra_notes=extra_env,
    )

    expert_cta = (
        "¿Quieres un plan personalizado por una nutricionista deportiva? "
        "Próximamente: consulta con Luz Dálida, atleta y profesora de nutrición."
    )

    return NutritionOut(
        hydration=hydration,
        macros=macros,
        environment=environment,
        expert_cta=expert_cta,
    )


def _build_polarization(activity: dict) -> PolarizationOut | None:
    zone_pct = activity.get("zone_distribution_pct") or []
    if len(zone_pct) < 5:
        return None
    z12 = (zone_pct[0] or 0) + (zone_pct[1] or 0)
    z3 = zone_pct[2] or 0
    z45 = (zone_pct[3] or 0) + (zone_pct[4] or 0)
    # Evaluación
    if 75 <= z12 <= 85 and z45 >= 10:
        evaluation = "aligned"
    elif z12 > 90 and z45 < 5:
        evaluation = "too_easy"
    elif z45 > 30:
        evaluation = "too_hard"
    elif z3 > 25:
        evaluation = "mixed"  # zona "gris" — ni base ni VO2máx
    else:
        evaluation = "mixed"

    return PolarizationOut(
        z1_z2_pct=round(z12, 1),
        z3_pct=round(z3, 1),
        z4_z5_pct=round(z45, 1),
        evaluation=evaluation,
        source_label="última carrera (próximamente: semanal)",
    )


def _build_physio_context(profile, target: DateT) -> PhysioContextOut | None:
    """Calcula Z2 (Karvonen 60-70% HRR), semanas al objetivo y fase de entrenamiento."""
    if not profile:
        return None
    max_hr = int(profile.max_hr or 190)
    rhr = int(profile.resting_hr or 50)
    hrr = max_hr - rhr
    z2_low = round(rhr + 0.60 * hrr)
    z2_high = round(rhr + 0.70 * hrr)

    # Semanas al objetivo
    goal_date = None
    if profile.goal_date:
        try:
            from datetime import date as _date
            goal_date = _date.fromisoformat(str(profile.goal_date)[:10])
        except Exception:
            pass
    weeks_to_goal = max(0, (goal_date - target).days // 7) if goal_date else 0

    # Pace objetivo: goal_time_secs / 21.1 km
    goal_secs = int(profile.goal_time_secs or 6600)
    pace_secs = goal_secs / 21.1
    pace_min = int(pace_secs // 60)
    pace_sec = int(pace_secs % 60)
    goal_pace = f"{pace_min}:{pace_sec:02d}/km"

    # Fase de entrenamiento según semanas restantes
    if weeks_to_goal >= 16:
        phase = "Base"
        rationale = (
            f"Fase base: {weeks_to_goal} semanas al objetivo. "
            f"Prioridad: construir aeróbico en Z2 ({z2_low}–{z2_high} lpm). "
            "Sesiones Z2 de 55-65 min y rodaje largo de 75-90 min."
        )
    elif weeks_to_goal >= 10:
        phase = "Construcción"
        rationale = (
            f"Fase construcción: {weeks_to_goal} semanas al objetivo. "
            f"Z2 ({z2_low}–{z2_high} lpm) 60-70 min, largo 85-100 min. "
            "Añadir 1 sesión de tempo semanal (20 min a Z3)."
        )
    elif weeks_to_goal >= 4:
        phase = "Pico"
        rationale = (
            f"Fase pico: {weeks_to_goal} semanas al objetivo. "
            f"Z2 ({z2_low}–{z2_high} lpm) 65-75 min, largo 100-110 min. "
            "Simulacros de ritmo objetivo los sábados."
        )
    else:
        phase = "Tapering"
        rationale = (
            f"Tapering: {weeks_to_goal} semana(s) al objetivo. "
            "Reducir volumen 30-40%, mantener intensidad puntual. "
            "Prioridad: piernas frescas el día de la carrera."
        )

    return PhysioContextOut(
        z2_hr_low=z2_low,
        z2_hr_high=z2_high,
        max_hr=max_hr,
        resting_hr=rhr,
        goal_pace_per_km=goal_pace,
        weeks_to_goal=weeks_to_goal,
        training_phase=phase,
        session_duration_rationale=rationale,
    )


# ─── Endpoint ────────────────────────────────────────────


@router.get(
    "/report",
    response_model=ReportOut,
    summary="Reporte diario completo (8 secciones)",
)
def get_report(
    date: DateT | None = Query(default=None, description="YYYY-MM-DD (default: hoy)"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> ReportOut:
    target = date or local_today()

    # 1. Activities del día — FUENTE PRINCIPAL: tabla activities (histórico real)
    crono = _read_cronologia(user_id, target) or {}
    summary = crono.get("summary") or {}

    # Defensivo: si la migration de la tabla `activities` no se ha aplicado en
    # producción, no romper el endpoint — fallback al cache (cronología + latest).
    # IMPORTANTE: hacer rollback para no dejar la transacción abortada (Postgres
    # rechaza queries subsiguientes en una transacción en estado failed).
    try:
        db_activities = activities_repo.get_by_date(db, user_id, target)
    except Exception:
        logger.warning("Tabla activities no disponible, fallback a cache", exc_info=False)
        db.rollback()
        db_activities = []
    activities_out: list[ActivityTodayOut] = []
    for a in db_activities:
        hour_f = 0.0
        if a.started_at:
            hour_f = a.started_at.hour + a.started_at.minute / 60 + a.started_at.second / 3600
        label = a.name or "Actividad"
        if a.distance_km:
            label = f"{label} · {a.distance_km:.2f} km"
        activities_out.append(
            ActivityTodayOut(
                hour=round(hour_f, 3),
                label=label,
                type=a.type_key,
            )
        )

    # 2. Biomecánica — preferir actividad locomotriz (running, walking, hiking)
    # del DÍA CONSULTADO. Si target es hoy y no hay nada del día, fallback a
    # la última actividad guardada en BD. Si target es PASADO sin actividad,
    # NO traer una vieja — el usuario vería datos de otra fecha confusos.
    _LOCOMOTOR_TYPES = ("running", "walking", "hiking")
    biomech_source: dict | None = None
    biomech_db = next(
        (
            a for a in db_activities
            if any(t in (a.type_key or "").lower() for t in _LOCOMOTOR_TYPES)
        ),
        None,
    )
    is_target_today = target == local_today()
    if biomech_db is None and is_target_today:
        # Solo fallback global cuando estamos viendo hoy. Toma la última
        # locomotriz (no solo running) para que caminatas también cuenten
        # hacia los gates de cadencia, polarización, etc.
        try:
            latest_any = None
            for tk in _LOCOMOTOR_TYPES:
                rows = activities_repo.get_latest(db, user_id, type_key=tk, limit=1)
                if rows and (latest_any is None or (rows[0].started_at and (
                    latest_any.started_at is None
                    or rows[0].started_at > latest_any.started_at
                ))):
                    latest_any = rows[0]
            biomech_db = latest_any
        except Exception:
            db.rollback()
            biomech_db = None
    if biomech_db is not None:
        biomech_source = {
            "name": biomech_db.name,
            "calories": biomech_db.calories,
            "distance_km": biomech_db.distance_km,
            "duration_secs": biomech_db.duration_secs,
            "avg_cadence": biomech_db.avg_cadence,
            "avg_stride_m": biomech_db.avg_stride_m,
            "avg_gct_ms": biomech_db.avg_gct_ms,
        }
        if biomech_db.zone_distribution_json:
            try:
                biomech_source["zone_distribution_pct"] = json.loads(
                    biomech_db.zone_distribution_json
                )
            except Exception:
                pass

    # Cache de samples para cardiac drift (datos high-res). Solo es válido
    # si el cache corresponde al DÍA CONSULTADO — antes lo usábamos siempre,
    # lo que causaba que al navegar a días pasados con las flechas, los
    # insights (fat_burn, cardiac_drift) siguieran mostrando la última
    # actividad de hoy en lugar de la del día consultado.
    latest_raw = _read_latest_activity(user_id) or {}
    _latest_date = (latest_raw.get("started_at") or "")[:10]
    latest = latest_raw if _latest_date == target.isoformat() else {}

    # Fallback A: si BD no trajo nada pero la cronología cache tiene activities,
    # úsala (compat hacia atrás antes de que la migration se aplique).
    if not activities_out:
        crono_acts = crono.get("activities") or []
        for a in crono_acts:
            activities_out.append(
                ActivityTodayOut(
                    hour=a.get("hour") or 0,
                    label=a.get("label") or "",
                    type=a.get("type") or "run",
                )
            )

    # Fallback B: si todavía no hay nada y el cache de última actividad coincide
    # con la fecha solicitada, agrégalo.
    if not activities_out and latest:
        started = latest.get("started_at") or ""
        if started.startswith(target.isoformat()):
            try:
                h, m, s = (int(x) for x in started[11:19].split(":"))
                hour_f = h + m / 60 + s / 3600
            except Exception:
                hour_f = 0
            dist_km = latest.get("distance_km") or 0
            name = latest.get("name") or "Actividad"
            label = f"{name} · {dist_km:.2f} km" if dist_km else name
            activities_out.append(
                ActivityTodayOut(
                    hour=round(hour_f, 3),
                    label=label,
                    type=latest.get("type") or "run",
                )
            )

    # Fallback final para biomech_source: si BD vacía pero hay cache latest,
    # úsalo para fat_burn/polarization
    if biomech_source is None and latest:
        biomech_source = {
            "name": latest.get("name"),
            "calories": latest.get("calories"),
            "distance_km": latest.get("distance_km"),
            "duration_secs": latest.get("duration_secs"),
            "avg_cadence": latest.get("avg_cadence"),
            "avg_stride_m": latest.get("avg_stride_m"),
            "avg_gct_ms": latest.get("avg_gct_ms"),
            "zone_distribution_pct": latest.get("zone_distribution_pct"),
            "type_key": latest.get("type_key", ""),
        }

    biomech: BiomechanicsOut | None = None
    if biomech_source:
        is_walk = _is_walk(
            biomech_source.get("distance_km") or 0,
            biomech_source.get("duration_secs") or 0,
            biomech_source.get("type_key", ""),
        )
        biomech = BiomechanicsOut(
            cadence_spm=int(biomech_source["avg_cadence"]) if biomech_source.get("avg_cadence") else None,
            stride_m=biomech_source.get("avg_stride_m"),
            gct_ms=biomech_source.get("avg_gct_ms"),
            is_walk=is_walk,
        )

    # 3. Heart
    profile = runner_profile.get(db, user_id)
    rhr_base = float(profile.resting_hr or 50.5) if profile else 50.5
    nights = hrv_repo.get_recent(db, user_id, days=14)
    baseline = hrv_repo.get_baseline(db, user_id)
    latest_hrv = nights[0].hrv_rmssd if nights else None
    # Garmin registra el HRV de la noche con la fecha del día anterior al despertar.
    # Aceptamos el registro más reciente si es de hoy o de ayer.
    hrv_today = None
    if nights and nights[0].date >= target - timedelta(days=1):
        hrv_today = nights[0].hrv_rmssd

    hrv_state = "sin registro"
    if hrv_today and baseline:
        if hrv_today < baseline - 4.7:
            hrv_state = "suprimido"
        elif hrv_today < baseline:
            hrv_state = "reducido"
        else:
            hrv_state = "óptimo"

    # FC reposo del día — no la guardamos en BD aún, usamos baseline como aproximación
    # En el futuro: extraerla de summary o agregar tabla daily_health
    rhr_today = None
    rhr_delta = None

    heart = HeartOut(
        resting_hr=rhr_today,
        resting_hr_baseline=rhr_base,
        resting_hr_delta=rhr_delta,
        hrv_last_night=hrv_today,
        hrv_baseline=baseline,
        hrv_state=hrv_state,
    )

    # 4. Load
    stress_avg = summary.get("stress_avg") or None
    bb_max = summary.get("body_battery_max") or None
    bb_min = summary.get("body_battery_min") or None

    # ACWR aproximado desde weekly_history
    from memory.repositories import weekly as weekly_repo

    weeks = weekly_repo.get_history(db, user_id, n_weeks=4)
    acwr_val = weeks[0].acwr if weeks and weeks[0].acwr is not None else None
    acwr_zone = "—"
    if acwr_val is not None:
        if 0.8 <= acwr_val <= 1.3:
            acwr_zone = "óptima"
        elif acwr_val > 1.3:
            acwr_zone = "alta"
        else:
            acwr_zone = "baja"

    load = LoadOut(
        body_battery_max=bb_max,
        body_battery_min=bb_min,
        stress_avg=stress_avg,
        acwr=acwr_val,
        acwr_zone=acwr_zone,
    )

    # 5. Gates (4 criterios)
    gates: list[GateOut] = []

    # Gate 1: FC reposo (sin datos por ahora → baseline)
    gates.append(
        GateOut(
            label="FC reposo estabilizada ≤ 52 lpm",
            status="green" if rhr_base <= 52 else "yellow",
            detail=f"Baseline {rhr_base:.0f} lpm",
        )
    )

    # Gate 2: HRV ≥ baseline 5 noches consecutivas
    last_5 = nights[:5]
    if baseline:
        ok_count = sum(1 for n in last_5 if n.hrv_rmssd >= baseline)
        if len(last_5) >= 5 and ok_count >= 5:
            gates.append(
                GateOut(
                    label="HRV ≥ baseline 5 noches consecutivas",
                    status="green",
                    detail=f"{ok_count}/5 noches sobre baseline {baseline:.0f}",
                )
            )
        elif len(last_5) < 5:
            gates.append(
                GateOut(
                    label="HRV — registros nocturnos completos",
                    status="yellow",
                    detail=f"{len(last_5)}/5 noches con registro (usa el reloj de noche)",
                )
            )
        else:
            gates.append(
                GateOut(
                    label="HRV ≥ baseline 5 noches consecutivas",
                    status="yellow" if ok_count >= 3 else "red",
                    detail=f"{ok_count}/5 noches sobre baseline",
                )
            )
    else:
        gates.append(
            GateOut(
                label="HRV baseline en construcción",
                status="yellow",
                detail=f"{len(nights)}/14 noches registradas",
            )
        )

    # Gate 3: caminata 60 min Z2 sin drift
    gates.append(
        GateOut(
            label="Caminata 60 min en Z2 con drift FC <8%",
            status="green",
            detail="Logrado en sesiones recientes",
        )
    )

    # Gate 4: cadencia ≥ 130 spm en caminata enérgica
    cad = biomech.cadence_spm if biomech else None
    if cad and cad >= 130:
        gates.append(
            GateOut(
                label="Cadencia ≥ 130 spm en caminata enérgica",
                status="green",
                detail=f"Cadencia actual {cad} spm",
            )
        )
    elif cad:
        gates.append(
            GateOut(
                label="Cadencia ≥ 130 spm en caminata enérgica",
                status="yellow",
                detail=f"Actual {cad} spm — drills de cadencia 3x/sem ayudan",
            )
        )
    else:
        gates.append(
            GateOut(
                label="Cadencia ≥ 130 spm en caminata enérgica",
                status="yellow",
                detail="Sin medición reciente",
            )
        )

    # 6. Interpretación (3-4 puntos)
    interp: list[str] = []
    if activities_out:
        has_run = any("run" in a.type for a in activities_out)
        if has_run and biomech and biomech.is_walk:
            interp.append(
                "Caminata mantenida en Z1-Z2 — exactamente lo que la fase actual del plan pide."
            )
    if hrv_today and baseline and hrv_today < baseline:
        interp.append(
            f"HRV {hrv_today:.0f} ms vs baseline {baseline:.0f} — leve reducción, vigilar próxima noche."
        )
    missing = 14 - len(nights)
    if missing > 4:
        interp.append(
            f"HRV: {len(nights)}/14 noches con registro. Sin esto las recomendaciones de carga van a ciegas."
        )
    if acwr_val and acwr_val > 1.3:
        interp.append(
            f"ACWR {acwr_val:.2f} — carga aguda elevada. Reducir intensidad próximos días."
        )

    if not interp:
        interp.append("Día sin señales fuera de patrón. Mantener el plan.")

    # 7. (Recomendación textual eliminada — la fuente única ahora es today_action más abajo)

    # 9. Insights científicos (diferencial Liebre)
    # FatBurn/polarization usan datos de BD (biomech_source). Cardiac drift necesita
    # samples high-res, que solo vienen del cache JSON.
    insights: InsightsOut | None = None
    if biomech_source or latest:
        insights = InsightsOut(
            fat_burn=_calc_fat_burn(biomech_source) if biomech_source else None,
            cardiac_drift=_calc_cardiac_drift(latest) if latest else None,
            heart_progress=_build_heart_progress(rhr_today, rhr_base),
            polarization=_build_polarization(biomech_source) if biomech_source else None,
        )

    # 10. Today action — recomendación inequívoca (contextual a la fecha).
    # weekly_plan viene de runner_profile.weekly_plan JSONB (override per-user);
    # si None, build_today_action cae al DEFAULT_WEEKDAY_PLAN genérico.
    today_action = _build_today_action(
        target=target,
        activities_today=activities_out,
        acwr=acwr_val,
        hrv_today=hrv_today,
        hrv_baseline=baseline,
        weekday_plan=getattr(profile, "weekly_plan", None) if profile else None,
    )

    # 11. Nutrición e hidratación (factor ambiental + diferencial)
    is_today = target == local_today()
    weight = float(profile.weight_kg) if profile and profile.weight_kg else 68.0
    # Multi-tenant: altitude por usuario desde el perfil (antes 1736 hardcoded a
    # Popayán). Si el usuario no la registró, 0 = nivel del mar (default safe).
    altitude = (
        int(profile.altitude_msnm)
        if profile and getattr(profile, "altitude_msnm", None)
        else 0
    )
    nutrition = _build_nutrition(
        weight_kg=weight,
        activities_today=activities_out,
        latest_activity=biomech_source if (activities_out and biomech_source) else None,
        altitude_msnm=altitude,
        is_today=is_today,
    )

    physio_context = _build_physio_context(profile, target)

    return ReportOut(
        date=target,
        today_action=today_action,
        activities_today=activities_out,
        biomechanics=biomech,
        heart=heart,
        load=load,
        gates=gates,
        interpretation=interp,
        insights=insights,
        nutrition=nutrition,
        physio_context=physio_context,
    )
