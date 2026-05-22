"""Perfil persistente del corredor y baseline HRV."""
import json
from datetime import date, datetime
from typing import Optional

from memory.db import get_connection, init_db


def create_profile(
    name: str,
    age: int,
    height_cm: float,
    weight_kg: float,
    max_hr: Optional[int] = None,
    resting_hr: Optional[int] = None,
    goal_event: Optional[str] = None,
    goal_date: Optional[str] = None,
    goal_time_secs: Optional[int] = None,
) -> dict:
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM runner_profile")
    cur.execute(
        """
        INSERT INTO runner_profile
            (name, age, height_cm, weight_kg, max_hr, resting_hr,
             goal_event, goal_date, goal_time_secs, system_start)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name, age, height_cm, weight_kg, max_hr, resting_hr,
            goal_event, goal_date, goal_time_secs,
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    profile = dict(cur.execute("SELECT * FROM runner_profile").fetchone())
    conn.close()
    return profile


def get_profile() -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM runner_profile LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row else None


def update_weight(weight_kg: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE runner_profile SET weight_kg = ? WHERE id = 1",
        (weight_kg,),
    )
    cur.execute(
        "INSERT INTO body_weight_history (weight_kg, recorded_at) VALUES (?, ?)",
        (weight_kg, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def add_injury(injury_type: str, occurred_on: str, severity: str, recovery_notes: str = ""):
    """Persiste lesión en las notas del perfil (campo agent_notes de weekly_history no existe aquí,
    guardamos como entrada especial en weekly_history con week_start='injury-<date>')."""
    conn = get_connection()
    cur = conn.cursor()
    notes = json.dumps({
        "type": "injury",
        "injury_type": injury_type,
        "occurred_on": occurred_on,
        "severity": severity,
        "recovery_notes": recovery_notes,
    })
    cur.execute(
        """
        INSERT OR REPLACE INTO weekly_history (week_start, agent_notes)
        VALUES (?, ?)
        """,
        (f"injury-{occurred_on}", notes),
    )
    conn.commit()
    conn.close()


def set_goal(event: str, goal_date: str, goal_time_secs: Optional[int] = None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE runner_profile SET goal_event=?, goal_date=?, goal_time_secs=? WHERE id=1",
        (event, goal_date, goal_time_secs),
    )
    conn.commit()
    conn.close()


def log_hrv(hrv_date: str, hrv_rmssd: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO hrv_log (date, hrv_rmssd) VALUES (?, ?)",
        (hrv_date, hrv_rmssd),
    )
    conn.commit()
    conn.close()


def get_hrv_baseline() -> Optional[float]:
    """Media móvil de 7 días sobre los últimos 14 registros. None si < 14 días."""
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT date, hrv_rmssd FROM hrv_log ORDER BY date DESC LIMIT 14"
    ).fetchall()
    conn.close()

    if len(rows) < 14:
        print(
            f"⚠️  Baseline HRV en construcción: {len(rows)}/14 días disponibles"
        )
        return None

    values = [r["hrv_rmssd"] for r in rows[:7]]
    return sum(values) / len(values)


def save_weekly_summary(
    week_start: str,
    plan_km: Optional[float],
    executed_km: Optional[float],
    avg_hrv: Optional[float],
    avg_body_battery: Optional[float],
    acwr: Optional[float],
    agent_notes: str = "",
):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO weekly_history
            (week_start, plan_km, executed_km, avg_hrv, avg_body_battery, acwr, agent_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (week_start, plan_km, executed_km, avg_hrv, avg_body_battery, acwr, agent_notes),
    )
    conn.commit()
    conn.close()


def get_weekly_history(n_weeks: int = 4) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT * FROM weekly_history
        WHERE week_start NOT LIKE 'injury-%'
        ORDER BY week_start DESC
        LIMIT ?
        """,
        (n_weeks,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
