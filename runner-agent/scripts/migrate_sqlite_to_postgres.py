"""Importa el SQLite del sistema personal de José al Postgres multitenant.

Uso:
    python scripts/migrate_sqlite_to_postgres.py \\
        --sqlite ./runner_agent.db \\
        --user-id <firebase_uid_real_o_placeholder>

Notas:
- Idempotente para HRV / weekly / nutrition (usa upsert).
- `runner_profile` y `body_weight_history` se replican tal cual.
- Si pasas un placeholder y luego el usuario real se loguea con otro UID,
  corre `scripts/reassign_user_id.py` para mover los datos.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

# Permitir imports del paquete cuando se corre como script
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.database import session_scope  # noqa: E402
from memory.repositories import (  # noqa: E402
    hrv,
    nutrition,
    runner_profile,
    users,
    weekly,
    weight,
)


def _parse_date(s: str | None) -> date | None:
    if not s:
        return None
    # SQLite guarda fechas como TEXT (varios formatos posibles)
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"No pude parsear fecha: {s!r}")


def _parse_datetime(s: str | None) -> datetime | None:
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"No pude parsear datetime: {s!r}")


def migrate(sqlite_path: Path, user_id: str) -> None:
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row

    with session_scope() as s:
        users.ensure(s, user_id)

        # runner_profile
        prof = conn.execute("SELECT * FROM runner_profile LIMIT 1").fetchone()
        if prof:
            runner_profile.upsert(
                s,
                user_id,
                name=prof["name"],
                age=prof["age"],
                height_cm=prof["height_cm"],
                weight_kg=prof["weight_kg"],
                max_hr=prof["max_hr"],
                resting_hr=prof["resting_hr"],
                goal_event=prof["goal_event"],
                goal_date=_parse_date(prof["goal_date"]),
                goal_time_secs=prof["goal_time_secs"],
            )
            print(f"✓ runner_profile importado para {user_id}")

        # body_weight_history
        weight_rows = conn.execute(
            "SELECT * FROM body_weight_history ORDER BY recorded_at"
        ).fetchall()
        for row in weight_rows:
            weight.record(
                s,
                user_id,
                weight_kg=row["weight_kg"],
                recorded_at=_parse_datetime(row["recorded_at"]),
            )
        print(f"✓ {len(weight_rows)} pesos históricos importados")

        # hrv_log
        hrv_rows = conn.execute("SELECT * FROM hrv_log").fetchall()
        for row in hrv_rows:
            hrv.log(s, user_id, _parse_date(row["date"]), row["hrv_rmssd"])
        print(f"✓ {len(hrv_rows)} registros HRV importados")

        # weekly_history: el sistema legacy usaba este campo como cajón polivalente
        # con prefijos 'injury-', 'run-', 'health-' además de semanas reales (date).
        # Solo importamos las semanas reales (week_start parseable como fecha).
        weekly_rows = conn.execute("SELECT * FROM weekly_history").fetchall()
        imported = skipped = 0
        for row in weekly_rows:
            try:
                week_dt = _parse_date(row["week_start"])
            except ValueError:
                skipped += 1
                continue
            weekly.upsert(
                s,
                user_id,
                week_start=week_dt,
                plan_km=row["plan_km"],
                executed_km=row["executed_km"],
                avg_hrv=row["avg_hrv"],
                avg_body_battery=row["avg_body_battery"],
                acwr=row["acwr"],
                agent_notes=row["agent_notes"],
            )
            imported += 1
        print(
            f"✓ {imported} semanas históricas importadas "
            f"(omitidas {skipped} entradas tipo run-/injury-/health-)"
        )

        # nutrition_log
        nut_rows = conn.execute("SELECT * FROM nutrition_log").fetchall()
        for row in nut_rows:
            nutrition.log_intake(
                s,
                user_id,
                _parse_date(row["date"]),
                kcal=row["kcal"],
                protein_g=row["protein_g"],
            )
        print(f"✓ {len(nut_rows)} registros de nutrición importados")

        # Marca Garmin como conectado (José ya tiene tokens válidos)
        users.mark_garmin_connected(s, user_id)
        print(f"✓ user {user_id} marcado con Garmin conectado")

    conn.close()
    print("\n✅ Migración completada.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sqlite",
        type=Path,
        default=Path("runner_agent.db"),
        help="Ruta al SQLite del sistema viejo",
    )
    parser.add_argument(
        "--user-id",
        required=True,
        help="Firebase UID destino (o placeholder hasta que se reasigne)",
    )
    args = parser.parse_args()
    if not args.sqlite.exists():
        sys.exit(f"❌ SQLite no encontrado: {args.sqlite}")
    migrate(args.sqlite, args.user_id)
