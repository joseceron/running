"""
Descarga masiva de datos históricos de Garmin una sola vez.
Ejecutar después de que la autenticación funcione correctamente.

.venv/bin/python sync_historical.py
"""
import json
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from data.garmin_client import GarminConnectClient
from memory.db import init_db, get_connection
from memory.runner_profile import log_hrv

init_db()

print("Conectando a Garmin...")
try:
    g = GarminConnectClient()
    print("✅ Conectado\n")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    print("Ejecuta primero: .venv/bin/python inject_browser_session.py")
    sys.exit(1)


# ── 1. HRV histórico (28 días) ──────────────────────────────────────────────
print("Descargando HRV de los últimos 28 días...")
hrv_records = g.get_hrv_history(28)
inserted = 0
for r in hrv_records:
    try:
        log_hrv(r["date"], r["hrv_rmssd"])
        inserted += 1
    except Exception:
        pass
print(f"  ✅ {inserted} registros HRV guardados\n")


# ── 2. Actividades de carrera (últimas 8 semanas) ──────────────────────────
print("Descargando actividades de carrera...")
try:
    activities = g.get_raw_client().get_activities(0, 50)
    run_activities = [
        a for a in activities
        if "running" in (a.get("activityType") or {}).get("typeKey", "").lower()
    ]
    print(f"  Encontradas {len(run_activities)} carreras")

    conn = get_connection()
    saved = 0
    for act in run_activities:
        act_date = (act.get("startTimeLocal") or "")[:10]
        distance_km = round((act.get("distance") or 0) / 1000, 2)
        avg_hr = act.get("averageHR")
        duration_min = round((act.get("duration") or 0) / 60, 1)
        cadence = act.get("averageRunningCadenceInStepsPerMinute")
        if act_date and distance_km > 0:
            conn.execute("""
                INSERT OR IGNORE INTO weekly_history (week_start, executed_km, avg_hrv, agent_notes)
                VALUES (?, ?, NULL, ?)
            """, (
                f"run-{act_date}-{act.get('activityId')}",
                distance_km,
                json.dumps({
                    "type": "run",
                    "date": act_date,
                    "distance_km": distance_km,
                    "avg_hr": avg_hr,
                    "duration_min": duration_min,
                    "cadence": cadence,
                    "activity_id": act.get("activityId"),
                })
            ))
            saved += 1
    conn.commit()
    conn.close()
    print(f"  ✅ {saved} actividades guardadas\n")
except Exception as e:
    print(f"  ⚠️  Error descargando actividades: {e}\n")


# ── 3. Running Dynamics de la última sesión ─────────────────────────────────
print("Descargando running dynamics de la última sesión...")
try:
    dynamics = g.get_last_run_dynamics()
    if dynamics:
        print(f"  Última carrera: {dynamics.get('date')} — {(dynamics.get('distance_m') or 0)/1000:.1f} km")
        print(f"  Cadencia: {dynamics.get('cadence_avg')} spm")
        print(f"  Oscilación vertical: {dynamics.get('vertical_oscillation_cm')} cm")
        print(f"  Vertical Ratio: {dynamics.get('vertical_ratio_pct')}%")
        print(f"  GCT: {dynamics.get('gct_avg_ms')} ms")
        gct_bal = dynamics.get("gct_balance_left_pct")
        if gct_bal:
            print(f"  Balance GCT: {gct_bal:.1f}% izq / {100-gct_bal:.1f}% der")
        print("  ✅ Running dynamics descargados\n")
    else:
        print("  ⚠️  No se encontró actividad de carrera reciente\n")
except Exception as e:
    print(f"  ⚠️  Error en running dynamics: {e}\n")


# ── 4. Perfil físico actual ─────────────────────────────────────────────────
print("Descargando métricas de hoy...")
try:
    today = date.today()
    health = g.get_daily_health(today)
    print(f"  HRV hoy: {health.get('hrv_rmssd')}")
    print(f"  Body Battery max: {health.get('body_battery_max')}")
    print(f"  FC reposo: {health.get('resting_hr')}")
    print(f"  VO₂Max: {health.get('vo2max')}")
    print(f"  SpO₂: {health.get('spo2_avg')}%")
    print("  ✅ Métricas de hoy descargadas\n")
except Exception as e:
    print(f"  ⚠️  Error en métricas de hoy: {e}\n")


print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"Sincronización completa: {inserted} días HRV descargados")
print("Ahora corre: .venv/bin/python main.py daily")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
