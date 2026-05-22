"""Siembra datos conocidos de José en Postgres para tener un dashboard demo.

Los datos vienen de la memoria del proyecto: HRV de 8 noches de mayo 2026,
semanas con plan/ejecutado, perfil con goal.

Uso:
    DATABASE_URL=... python scripts/seed_jose_known_data.py --user-id jose_dev_uid

Es idempotente — se puede correr varias veces sin duplicar.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.database import session_scope  # noqa: E402
from memory.repositories import hrv, runner_profile, users, weekly, weight  # noqa: E402

# Datos del baseline HRV provisional (memoria del proyecto al 2026-05-21)
HRV_NOCHES = [
    (date(2026, 5, 11), 53.0),  # inicio
    (date(2026, 5, 13), 54.0),
    (date(2026, 5, 15), 58.0),  # mejor — tras descanso
    (date(2026, 5, 16), 48.0),  # ↓ post-carrera May 15
    (date(2026, 5, 17), 51.0),  # recuperando
    (date(2026, 5, 19), 63.0),  # ↑↑ máximo — tras descanso completo May 18
    (date(2026, 5, 20), 60.0),  # ↓ leve post-carrera May 19
    (date(2026, 5, 21), 52.0),  # ↓ post-carrera May 21
]

# Semanas con plan vs ejecución
SEMANAS = [
    {
        "week_start": date(2026, 5, 11),
        "plan_km": 25.0,
        "executed_km": 19.94,
        "avg_hrv": 53.5,
        "avg_body_battery": 70.0,
        "acwr": 0.95,
        "agent_notes": "Semana 1 con corrección a Z2. Z4 bajó de 33% a 0.6%.",
    },
    {
        "week_start": date(2026, 5, 18),
        "plan_km": 28.0,
        "executed_km": 10.05,  # parcial hasta el 21-may
        "avg_hrv": 56.5,
        "avg_body_battery": 85.0,
        "acwr": 1.05,
        "agent_notes": "Semana en curso. FC reposo bajando de 56 a 50 lpm.",
    },
]

PESOS = [
    (date(2026, 5, 11), 68.5),
    (date(2026, 5, 18), 68.0),
    (date(2026, 5, 21), 67.8),
]


def main(user_id: str) -> None:
    with session_scope() as s:
        users.ensure(s, user_id)

        # Perfil: actualizar con datos consolidados
        runner_profile.upsert(
            s,
            user_id,
            name="José Luis Cerón",
            age=36,
            height_cm=170.0,
            weight_kg=68.0,
            max_hr=190,
            resting_hr=51,
            goal_event="21K",
            goal_date=date(2026, 10, 1),
            goal_time_secs=6600,  # 1h50
        )
        print(f"✓ perfil de {user_id} sembrado")

        # HRV nocturno
        for hrv_date, value in HRV_NOCHES:
            hrv.log(s, user_id, hrv_date, value)
        print(f"✓ {len(HRV_NOCHES)} noches HRV sembradas")

        # Semanas
        for w in SEMANAS:
            weekly.upsert(s, user_id, **w)
        print(f"✓ {len(SEMANAS)} semanas históricas sembradas")

        # Peso histórico (también actualiza profile.weight_kg al último)
        from datetime import datetime, time, timezone

        for d, kg in PESOS:
            weight.record(
                s,
                user_id,
                kg,
                recorded_at=datetime.combine(d, time(7, 0), tzinfo=timezone.utc),
            )
        print(f"✓ {len(PESOS)} pesos sembrados")

        users.mark_garmin_connected(s, user_id)
        print(f"✓ {user_id} marcado con Garmin conectado")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", default="jose_dev_uid")
    args = parser.parse_args()
    main(args.user_id)
    print("\n✅ Seed completado.")
