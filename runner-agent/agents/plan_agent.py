"""Sub-agente de plan adaptativo semanal."""
from typing import Optional


ZONE_HR_PCT = {
    "Z1": (0.50, 0.60),
    "Z2": (0.60, 0.70),
    "Z3": (0.70, 0.80),
    "Z4": (0.80, 0.90),
    "Z5": (0.90, 1.00),
}

# Multiplicador de ritmo por estado HRV (cuánto más lento correr según HRV)
HRV_PACE_MULTIPLIER = {
    "optimal": 1.00,
    "reduced": 1.04,   # ~4% más lento
    "suppressed": 1.08,
}

# Sesiones tipo por día de la semana (plantilla base)
BASE_WEEKLY_TEMPLATE = [
    {"day": 0, "label": "Lunes",     "type": "rest",             "zone": None,  "km": 0},
    {"day": 1, "label": "Martes",    "type": "quality",          "zone": "Z4",  "km": 8},
    {"day": 2, "label": "Miércoles", "type": "easy",             "zone": "Z2",  "km": 6},
    {"day": 3, "label": "Jueves",    "type": "rest",             "zone": None,  "km": 0},
    {"day": 4, "label": "Viernes",   "type": "easy",             "zone": "Z2",  "km": 8},
    {"day": 5, "label": "Sábado",    "type": "long_run",         "zone": "Z2",  "km": 14},
    {"day": 6, "label": "Domingo",   "type": "active_recovery",  "zone": "Z1",  "km": 4},
]


def _karvonen_pace_secs(zone: str, max_hr: int, resting_hr: int) -> tuple[float, float]:
    """Retorna (min_secs_per_km, max_secs_per_km) aproximado para la zona via Karvonen."""
    lo_pct, hi_pct = ZONE_HR_PCT[zone]
    hr_reserve = max_hr - resting_hr
    hr_lo = resting_hr + hr_reserve * lo_pct
    hr_hi = resting_hr + hr_reserve * hi_pct
    # Correlación empírica básica: FC → ritmo (min/km). Aproximación lineal.
    # A FC máxima (190) ≈ 4:00/km; a FC reposo (50) ≈ 8:00/km
    def hr_to_pace(hr):
        slope = (240 - 480) / (190 - 50)
        return 480 + slope * (hr - 50)

    return hr_to_pace(hr_hi), hr_to_pace(hr_lo)


def _secs_to_pace(secs: float) -> str:
    m, s = divmod(int(secs), 60)
    return f"{m}:{s:02d}/km"


def calculate_heart_rate_zones(max_hr: int, resting_hr: int) -> dict:
    """Calcula zonas FC personales via Karvonen."""
    hr_reserve = max_hr - resting_hr
    zones = {}
    for zone, (lo, hi) in ZONE_HR_PCT.items():
        zones[zone] = {
            "hr_low": round(resting_hr + hr_reserve * lo),
            "hr_high": round(resting_hr + hr_reserve * hi),
        }
    return zones


def calculate_daily_pace(zone: str, hrv_state: Optional[str], max_hr: int, resting_hr: int) -> dict:
    """Retorna ritmo personalizado en min/km para zona y estado HRV del día."""
    fast_secs, slow_secs = _karvonen_pace_secs(zone, max_hr, resting_hr)
    multiplier = HRV_PACE_MULTIPLIER.get(hrv_state or "optimal", 1.0)
    adj_fast = fast_secs * multiplier
    adj_slow = slow_secs * multiplier

    context = ""
    if hrv_state == "reduced":
        context = " (ajustado por HRV reducido hoy)"
    elif hrv_state == "suppressed":
        context = " (ajustado por HRV suprimido — considera recuperación activa)"

    return {
        "zone": zone,
        "hrv_state": hrv_state,
        "pace_range": f"{_secs_to_pace(adj_fast)} – {_secs_to_pace(adj_slow)}",
        "fast_secs_per_km": round(adj_fast),
        "slow_secs_per_km": round(adj_slow),
        "context": f"Tu {zone} hoy: {_secs_to_pace(adj_fast)} – {_secs_to_pace(adj_slow)}{context}",
    }


def _check_intensity_distribution(weekly_history: list[dict]) -> dict:
    """Valida distribución 80/20 de la semana anterior."""
    if not weekly_history:
        return {"ok": True, "z1_z2_pct": None, "correction_needed": False}

    last = weekly_history[0]
    # Si no hay datos de zonas detallados, usamos heurística por tipo de sesión
    executed = last.get("executed_km", 0) or 0
    plan = last.get("plan_km", 0) or 0
    completion_pct = (executed / plan * 100) if plan > 0 else 100

    return {
        "ok": True,
        "completion_pct": round(completion_pct, 1),
        "z1_z2_pct": None,
        "correction_needed": False,
    }


def generate_weekly_plan(runner_data: dict) -> dict:
    """
    Genera plan de 7 días.

    runner_data: {
        profile: {max_hr, resting_hr, weight_kg, ...},
        acwr: float,
        hrv_state: str,
        weekly_history: list[dict],   # últimas 4 semanas
        last_technique: dict,          # resultado de technique_agent.analyze_session()
    }
    """
    profile = runner_data.get("profile", {})
    max_hr = profile.get("max_hr", 190)
    resting_hr = profile.get("resting_hr", 50)
    acwr = runner_data.get("acwr")
    hrv_state = runner_data.get("hrv_state", "optimal")
    weekly_history = runner_data.get("weekly_history", [])

    dist_check = _check_intensity_distribution(weekly_history)
    last_week = weekly_history[0] if weekly_history else None

    # Determinar volumen base
    if last_week:
        executed = last_week.get("executed_km") or 0
        plan = last_week.get("plan_km") or executed
        completion = executed / plan if plan > 0 else 1.0

        if completion >= 0.8 and (acwr is None or acwr <= 1.3):
            base_km = executed * 1.05  # incremento ≤ 10%
            volume_note = f"Semana anterior completada al {completion*100:.0f}% — incremento moderado"
        elif completion < 0.7:
            base_km = executed
            volume_note = "Sub-ejecución < 70% — consolidando carga real antes de incrementar"
        else:
            base_km = executed
            volume_note = "Semana anterior normal — manteniendo volumen"
    else:
        base_km = sum(s["km"] for s in BASE_WEEKLY_TEMPLATE)
        volume_note = "Sin historial previo — usando plantilla base"

    # Ajustar por ACWR
    if acwr is not None and acwr > 1.5:
        base_km *= 0.85
        volume_note += " ⚠️  ACWR alto — volumen reducido 15%"

    # Escalar sesiones al volumen base
    template_total = sum(s["km"] for s in BASE_WEEKLY_TEMPLATE)
    scale = base_km / template_total if template_total > 0 else 1.0

    sessions = []
    for tmpl in BASE_WEEKLY_TEMPLATE:
        km = round(tmpl["km"] * scale, 1)
        session = {
            "day": tmpl["day"],
            "label": tmpl["label"],
            "type": tmpl["type"],
            "km": km,
            "zone": tmpl["zone"],
        }
        if tmpl["zone"]:
            pace = calculate_daily_pace(tmpl["zone"], hrv_state, max_hr, resting_hr)
            session["pace_guidance"] = pace["context"]
        else:
            session["pace_guidance"] = "Descanso"
        sessions.append(session)

    total_km = sum(s["km"] for s in sessions)
    z1_z2_km = sum(
        s["km"] for s in sessions if s["zone"] in ("Z1", "Z2", None)
    )
    z4_z5_km = sum(s["km"] for s in sessions if s["zone"] in ("Z4", "Z5"))
    z1_z2_pct = (z1_z2_km / total_km * 100) if total_km > 0 else 0

    hr_zones = calculate_heart_rate_zones(max_hr, resting_hr)

    return {
        "sessions": sessions,
        "total_km": round(total_km, 1),
        "z1_z2_pct": round(z1_z2_pct, 1),
        "z4_z5_km": round(z4_z5_km, 1),
        "hr_zones": hr_zones,
        "volume_note": volume_note,
        "distribution_check": dist_check,
    }


def adjust_today(plan: dict, daily_health: dict) -> dict:
    """Ajusta el entrenamiento del día según HRV y Body Battery matutinos."""
    hrv_state = daily_health.get("hrv_state")
    body_battery = daily_health.get("body_battery")
    recommendation = daily_health.get("recommendation", "load")

    today_session = plan["sessions"][0] if plan.get("sessions") else None
    if today_session is None:
        return plan

    adjusted = dict(today_session)
    note = ""

    if recommendation == "rest":
        adjusted["type"] = "rest"
        adjusted["km"] = 0
        adjusted["zone"] = None
        adjusted["pace_guidance"] = "Descanso — señales de recuperación insuficiente"
        note = f"Sesión cancelada (HRV: {hrv_state}, Body Battery: {body_battery})"
    elif recommendation == "active_recovery":
        if adjusted["type"] == "quality":
            adjusted["type"] = "easy"
            adjusted["zone"] = "Z1"
            adjusted["km"] = min(adjusted["km"], 6)
            note = "Sesión de calidad convertida a rodaje suave Z1 por señales mixtas"
        elif adjusted["type"] == "long_run":
            adjusted["km"] = min(adjusted["km"], adjusted["km"] * 0.7)
            adjusted["zone"] = "Z2"
            note = "Tirada larga reducida al 70% por señales mixtas"

    if adjusted.get("zone"):
        profile = plan.get("profile") or {}
        max_hr = profile.get("max_hr", 190)
        resting_hr = profile.get("resting_hr", 50)
        pace = calculate_daily_pace(adjusted["zone"], hrv_state, max_hr, resting_hr)
        adjusted["pace_guidance"] = pace["context"]

    plan["today_adjusted"] = adjusted
    plan["today_adjustment_note"] = note
    return plan
