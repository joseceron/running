"""Sub-agente de técnica de carrera: cadencia, GCT, oscilación, degradación de forma."""
from typing import Optional


CADENCE_TARGET_LOW = 170
CADENCE_TARGET_HIGH = 180
GCT_ASYMMETRY_THRESHOLD = 52.0  # % del lado más cargado
FORM_DEGRADATION_CADENCE_PCT = 5.0
FORM_DEGRADATION_OSCILLATION_PCT = 10.0
WEEKLY_CADENCE_IMPROVEMENT_MIN = 3.0  # spm
WEEKLY_VR_DETERIORATION_MIN = 0.5  # puntos porcentuales


def _pct_change(before: float, after: float) -> float:
    if before == 0:
        return 0.0
    return ((after - before) / before) * 100


def analyze_session(activity: dict) -> dict:
    """
    Analiza métricas de running dynamics de una sesión.

    activity: dict con campos de garmin_client.get_last_run_dynamics()
    """
    alerts = []
    observations = []

    cadence = activity.get("cadence_avg")
    oscillation = activity.get("vertical_oscillation_cm")
    vertical_ratio = activity.get("vertical_ratio_pct")
    gct_avg = activity.get("gct_avg_ms")
    gct_balance_left = activity.get("gct_balance_left_pct")
    stride_length = activity.get("stride_length_m")
    splits = activity.get("splits") or []

    # Evaluación de cadencia
    cadence_eval = None
    if cadence is not None:
        if cadence < CADENCE_TARGET_LOW:
            diff = CADENCE_TARGET_LOW - cadence
            cadence_eval = "below_target"
            alerts.append(
                f"Cadencia {cadence:.0f} spm — {diff:.0f} spm por debajo del objetivo "
                f"({CADENCE_TARGET_LOW}–{CADENCE_TARGET_HIGH} spm)"
            )
        elif cadence > CADENCE_TARGET_HIGH:
            cadence_eval = "above_target"
            observations.append(f"Cadencia {cadence:.0f} spm — dentro o sobre rango óptimo")
        else:
            cadence_eval = "optimal"
            observations.append(f"Cadencia {cadence:.0f} spm — rango óptimo ✓")

    # Asimetría GCT
    gct_asymmetry = None
    if gct_balance_left is not None:
        right_pct = 100 - gct_balance_left
        dominant_pct = max(gct_balance_left, right_pct)
        if dominant_pct > GCT_ASYMMETRY_THRESHOLD:
            side = "izquierdo" if gct_balance_left > right_pct else "derecho"
            gct_asymmetry = dominant_pct
            alerts.append(
                f"⚠️  Asimetría GCT: {gct_balance_left:.1f}% izq / {right_pct:.1f}% der "
                f"— lado {side} dominante ({dominant_pct:.1f}%). Posible compensación o lesión latente."
            )

    # Detección de degradación de forma (primeros vs últimos 3 km)
    form_degradation = _detect_form_degradation(splits)

    return {
        "activity_id": activity.get("activity_id"),
        "date": activity.get("date"),
        "cadence_avg": cadence,
        "cadence_eval": cadence_eval,
        "vertical_oscillation_cm": oscillation,
        "vertical_ratio_pct": vertical_ratio,
        "gct_avg_ms": gct_avg,
        "gct_balance_left_pct": gct_balance_left,
        "gct_asymmetry_pct": gct_asymmetry,
        "stride_length_m": stride_length,
        "form_degradation": form_degradation,
        "alerts": alerts,
        "observations": observations,
    }


def _detect_form_degradation(splits: list[dict]) -> dict:
    """Compara primeros vs últimos 3 km de la sesión."""
    if len(splits) < 6:
        return {"detected": False, "reason": "Sesión demasiado corta para análisis de degradación"}

    first_3 = splits[:3]
    last_3 = splits[-3:]

    def avg_field(segment, field):
        vals = [s.get(field) for s in segment if s.get(field) is not None]
        return sum(vals) / len(vals) if vals else None

    cadence_first = avg_field(first_3, "cadence")
    cadence_last = avg_field(last_3, "cadence")

    degradation_detected = False
    details = []

    if cadence_first and cadence_last:
        change_pct = _pct_change(cadence_first, cadence_last)
        if change_pct <= -FORM_DEGRADATION_CADENCE_PCT:
            degradation_detected = True
            details.append(
                f"Cadencia cayó {abs(change_pct):.1f}% en los últimos 3 km "
                f"({cadence_first:.0f} → {cadence_last:.0f} spm)"
            )
        else:
            details.append(f"Cadencia estable ({change_pct:+.1f}%)")

    if degradation_detected:
        return {
            "detected": True,
            "message": "Degradación de forma detectada — " + "; ".join(details),
            "details": details,
        }
    else:
        return {
            "detected": False,
            "message": "Forma técnica mantenida durante la sesión ✓",
            "details": details,
        }


def get_weekly_technique_trend(
    current_week_sessions: list[dict],
    previous_week_sessions: list[dict],
) -> dict:
    """
    Compara promedios de técnica semana actual vs semana anterior.

    Cada sesión es el resultado de analyze_session().
    """

    def session_avg(sessions, field):
        vals = [s.get(field) for s in sessions if s.get(field) is not None]
        return sum(vals) / len(vals) if vals else None

    metrics = [
        "cadence_avg",
        "vertical_oscillation_cm",
        "vertical_ratio_pct",
        "gct_avg_ms",
    ]

    trend = {}
    insights = []

    for metric in metrics:
        curr = session_avg(current_week_sessions, metric)
        prev = session_avg(previous_week_sessions, metric)
        change = None
        direction = None
        if curr is not None and prev is not None:
            change = curr - prev
            direction = "up" if change > 0 else "down" if change < 0 else "stable"

        trend[metric] = {"current": curr, "previous": prev, "change": change, "direction": direction}

    # Insights específicos
    cadence_change = trend["cadence_avg"].get("change")
    if cadence_change is not None and cadence_change >= WEEKLY_CADENCE_IMPROVEMENT_MIN:
        insights.append(
            f"✓ Mejora sostenida de cadencia: +{cadence_change:.1f} spm respecto a la semana anterior"
        )

    vr_change = trend["vertical_ratio_pct"].get("change")
    if vr_change is not None and vr_change >= WEEKLY_VR_DETERIORATION_MIN:
        insights.append(
            f"⚠️  Deterioro de economía: Vertical Ratio aumentó {vr_change:.2f}pp — revisar técnica"
        )

    return {"trend": trend, "insights": insights}
