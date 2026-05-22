"""Sub-agente de nutrición: balance calórico vs gasto Garmin y alerta proteica."""
from datetime import date, timedelta
from typing import Optional

from memory.db import get_connection
from memory.runner_profile import get_profile

CHRONIC_DEFICIT_THRESHOLD = -500  # kcal
CHRONIC_DEFICIT_DAYS = 3
PROTEIN_MIN_G_PER_KG = 1.6
HIGH_VOLUME_KM_THRESHOLD = 15


def log_intake(kcal: float, protein_g: float, log_date: Optional[str] = None):
    """Persiste ingesta calórica del día."""
    day = log_date or date.today().isoformat()
    conn = get_connection()
    conn.execute(
        """
        INSERT OR REPLACE INTO nutrition_log (date, kcal, protein_g, status)
        VALUES (?, ?, ?, 'logged')
        """,
        (day, kcal, protein_g),
    )
    conn.commit()
    conn.close()


def calculate_daily_balance(target_date: str, garmin_active_kcal: Optional[float] = None) -> dict:
    """
    Calcula balance calórico: ingesta - (BMR + calorías activas Garmin).
    garmin_active_kcal: calorías activas del día según Garmin (inyectado desde garmin_client).
    """
    profile = get_profile()
    if profile is None:
        return {"error": "Perfil no inicializado"}

    weight = profile.get("weight_kg", 70)
    age = profile.get("age", 30)
    height = profile.get("height_cm", 170)

    # BMR via Mifflin-St Jeor (hombre)
    bmr = 10 * weight + 6.25 * height - 5 * age + 5

    conn = get_connection()
    row = conn.execute(
        "SELECT kcal, protein_g, status FROM nutrition_log WHERE date=?",
        (target_date,),
    ).fetchone()
    conn.close()

    if row is None or row["status"] == "no_data":
        return {
            "date": target_date,
            "status": "no_data",
            "balance_kcal": None,
            "bmr": round(bmr),
            "active_kcal": garmin_active_kcal,
        }

    intake = row["kcal"] or 0
    active = garmin_active_kcal or 0
    total_expenditure = bmr + active
    balance = intake - total_expenditure

    return {
        "date": target_date,
        "status": "logged",
        "intake_kcal": intake,
        "protein_g": row["protein_g"],
        "bmr": round(bmr),
        "active_kcal": round(active),
        "total_expenditure": round(total_expenditure),
        "balance_kcal": round(balance),
    }


def check_chronic_deficit() -> Optional[str]:
    """Detecta déficit calórico crónico: balance < -500 kcal por 3+ días consecutivos."""
    today = date.today()
    conn = get_connection()
    consecutive = 0
    for i in range(7):
        d = (today - timedelta(days=i)).isoformat()
        row = conn.execute(
            "SELECT kcal FROM nutrition_log WHERE date=? AND status='logged'",
            (d,),
        ).fetchone()
        if row is None:
            break
        profile = get_profile()
        if profile is None:
            break
        weight = profile.get("weight_kg", 70)
        age = profile.get("age", 30)
        height = profile.get("height_cm", 170)
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
        balance = row["kcal"] - bmr
        if balance < CHRONIC_DEFICIT_THRESHOLD:
            consecutive += 1
        else:
            break
    conn.close()

    if consecutive >= CHRONIC_DEFICIT_DAYS:
        return (
            f"⚠️  Déficit calórico crónico detectado ({consecutive} días consecutivos) "
            "— riesgo de pérdida de masa muscular. Aumenta ingesta calórica y proteica."
        )
    return None


def check_protein_alert(target_date: str, km_run: float) -> Optional[str]:
    """Alerta si proteína < 1.6g/kg en días con > 15 km corridos."""
    if km_run <= HIGH_VOLUME_KM_THRESHOLD:
        return None

    profile = get_profile()
    if profile is None:
        return None

    weight = profile.get("weight_kg", 70)
    min_protein = PROTEIN_MIN_G_PER_KG * weight

    conn = get_connection()
    row = conn.execute(
        "SELECT protein_g FROM nutrition_log WHERE date=? AND status='logged'",
        (target_date,),
    ).fetchone()
    conn.close()

    if row is None:
        return f"Sin datos de ingesta para {target_date} — verifica tu nutrición tras {km_run:.1f} km"

    protein = row["protein_g"] or 0
    if protein < min_protein:
        return (
            f"⚠️  Ingesta proteica insuficiente: {protein:.0f}g reportados, "
            f"mínimo {min_protein:.0f}g para preservar masa muscular "
            f"({PROTEIN_MIN_G_PER_KG}g/kg × {weight:.1f}kg) en días de alto volumen."
        )
    return None
