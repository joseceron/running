"""Sub-agente de fatiga y carga: HRV vs baseline personal + ACWR."""
import sqlite3
from datetime import date, timedelta
from typing import Optional

from memory.db import get_connection
from memory.runner_profile import get_hrv_baseline


def _get_hrv_for_date(target_date: str) -> Optional[float]:
    conn = get_connection()
    row = conn.execute(
        "SELECT hrv_rmssd FROM hrv_log WHERE date = ?", (target_date,)
    ).fetchone()
    conn.close()
    return row["hrv_rmssd"] if row else None


def _get_body_battery_for_date(target_date: str) -> Optional[float]:
    """Busca el body_battery máximo del día en weekly_history (cacheado por garmin_client)."""
    # En la integración completa esto viene de garmin_client;
    # aquí leemos de la tabla hrv_log si se almacenó junto con el log diario.
    return None  # se inyecta desde el orquestador


def classify_hrv_state(hrv_today: float, baseline: float) -> str:
    """Clasifica estado HRV: optimal / reduced / suppressed."""
    ratio = hrv_today / baseline
    if ratio >= 1.0:
        return "optimal"
    elif ratio >= 0.85:
        return "reduced"
    else:
        return "suppressed"


def _load_proxy(distance_m: float, avg_hr: int, max_hr: int) -> float:
    """Proxy de carga: distancia(km) × intensidad relativa zona FC."""
    intensity = avg_hr / max_hr
    return (distance_m / 1000) * intensity


def _get_recent_loads(days: int) -> list[float]:
    """Obtiene cargas de los últimos N días desde weekly_history + actividades."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT executed_km, acwr FROM weekly_history
        WHERE week_start NOT LIKE 'injury-%'
        ORDER BY week_start DESC
        LIMIT 5
        """
    ).fetchall()
    conn.close()
    # Aproximación: usamos executed_km como proxy de carga relativa
    loads = [r["executed_km"] for r in rows if r["executed_km"] is not None]
    return loads


def calculate_acwr(recent_activities: list[dict], max_hr: int) -> dict:
    """
    Calcula ACWR usando lista de actividades [{distance_m, avg_hr, date}].
    Retorna {'acwr': float, 'acute': float, 'chronic': float, 'confidence': str}
    """
    today = date.today()

    acute_loads = []
    chronic_loads = []

    for act in recent_activities:
        act_date = date.fromisoformat(act["date"])
        days_ago = (today - act_date).days
        load = _load_proxy(act.get("distance_m", 0), act.get("avg_hr", 140), max_hr)
        if days_ago < 7:
            acute_loads.append(load)
        if days_ago < 28:
            chronic_loads.append(load)

    acute = sum(acute_loads)
    chronic_avg = sum(chronic_loads) / 4 if chronic_loads else 0

    confidence = "high" if len(chronic_loads) >= 16 else "low"

    acwr = round(acute / chronic_avg, 2) if chronic_avg > 0 else None

    return {
        "acwr": acwr,
        "acute_load": round(acute, 2),
        "chronic_load_avg": round(chronic_avg, 2),
        "confidence": confidence,
    }


def check_acwr_alert(acwr: Optional[float]) -> Optional[str]:
    if acwr is None:
        return None
    if acwr > 1.5:
        return (
            f"⚠️  ACWR {acwr:.2f} — RIESGO DE LESIÓN: carga aguda muy superior a la crónica. "
            "Reduce volumen o intensidad los próximos días."
        )
    return None


def recommend_day_type(
    hrv_state: Optional[str],
    body_battery: Optional[float],
    acwr: Optional[float],
) -> dict:
    """Genera recomendación del día: load / active_recovery / rest."""
    alerts = []
    recommendation = "load"

    if hrv_state == "suppressed":
        recommendation = "rest"
        alerts.append("HRV suprimido (< 85% del baseline personal)")
    elif body_battery is not None and body_battery < 40:
        recommendation = "rest"
        alerts.append(f"Body Battery muy bajo ({body_battery:.0f})")
    elif acwr is not None and acwr > 1.5:
        recommendation = "rest"
        alerts.append(f"ACWR > 1.5 ({acwr:.2f}) — riesgo de sobreentrenamiento")
    elif (
        hrv_state == "reduced"
        or (body_battery is not None and 40 <= body_battery < 60)
        or (acwr is not None and 1.3 <= acwr <= 1.5)
    ):
        recommendation = "active_recovery"
        if hrv_state == "reduced":
            alerts.append("HRV reducido (85–99% del baseline)")
        if body_battery is not None and 40 <= body_battery < 60:
            alerts.append(f"Body Battery moderado ({body_battery:.0f})")
        if acwr is not None and 1.3 <= acwr <= 1.5:
            alerts.append(f"ACWR en zona de precaución ({acwr:.2f})")

    return {
        "recommendation": recommendation,
        "alerts": alerts,
    }


def analyze_day(
    target_date: date,
    body_battery: Optional[float] = None,
    recent_activities: Optional[list[dict]] = None,
    max_hr: int = 190,
) -> dict:
    """
    Análisis completo del día: HRV vs baseline + ACWR + recomendación.

    Args:
        target_date: fecha a analizar
        body_battery: valor de Body Battery del día (inyectado desde garmin_client)
        recent_activities: lista de actividades [{date, distance_m, avg_hr}] últimos 28 días
        max_hr: FC máxima del corredor
    """
    date_str = target_date.isoformat()

    hrv_today = _get_hrv_for_date(date_str)
    baseline = get_hrv_baseline()

    if hrv_today is not None and baseline is not None:
        hrv_state = classify_hrv_state(hrv_today, baseline)
    elif baseline is None:
        hrv_state = None
    else:
        hrv_state = None

    acwr_data = calculate_acwr(recent_activities or [], max_hr)
    acwr = acwr_data["acwr"]

    day_rec = recommend_day_type(hrv_state, body_battery, acwr)

    return {
        "date": date_str,
        "hrv_today": hrv_today,
        "hrv_baseline": baseline,
        "hrv_state": hrv_state,
        "body_battery": body_battery,
        "acwr": acwr_data,
        "recommendation": day_rec["recommendation"],
        "alerts": day_rec["alerts"],
        "acwr_alert": check_acwr_alert(acwr),
    }


def update_acwr(activity: dict, max_hr: int = 190) -> dict:
    """Recalcula ACWR tras registrar nueva sesión. activity: {date, distance_m, avg_hr}."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT week_start, executed_km FROM weekly_history
        WHERE week_start NOT LIKE 'injury-%'
        ORDER BY week_start DESC LIMIT 28
        """
    ).fetchall()
    conn.close()

    existing = [
        {"date": r["week_start"], "distance_m": (r["executed_km"] or 0) * 1000, "avg_hr": 150}
        for r in rows
    ]
    existing.append(activity)

    return calculate_acwr(existing, max_hr)
