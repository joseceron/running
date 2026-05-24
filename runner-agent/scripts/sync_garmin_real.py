"""Sincroniza datos reales de Garmin → Postgres + cache de archivos.

Estrategia v1 (pragmática, single-user):
- HRV → tabla hrv_log con user_id (upsert, persistente).
- Body Battery + Stress del día → cache JSON en /tmp/liebre_cache.
- Última actividad con dynamics + splits → cache JSON en /tmp/liebre_cache.

Los endpoints /cronologia y /activities/* leen del cache si existe, fallback al mock.

Uso:
    DATABASE_URL=... python scripts/sync_garmin_real.py --user-id jose_dev_uid
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date as DateT, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.garmin_client import GarminConnectClient  # noqa: E402
from memory.database import session_scope  # noqa: E402
from memory.repositories import activities as activities_repo  # noqa: E402
from memory.repositories import hrv as hrv_repo  # noqa: E402
from memory.repositories import users  # noqa: E402

CACHE_DIR = Path("/tmp/liebre_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path(kind: str, user_id: str, suffix: str = "") -> Path:
    name = f"{kind}_{user_id}{('_' + suffix) if suffix else ''}.json"
    return CACHE_DIR / name


def _sync_hrv(client: GarminConnectClient, user_id: str) -> int:
    """HRV → tabla hrv_log."""
    records = client.get_hrv_history(days=14)
    if not records:
        print("⚠️  Sin registros HRV — Garmin devolvió vacío")
        return 0
    with session_scope() as s:
        users.ensure(s, user_id)
        for r in records:
            d = DateT.fromisoformat(r["date"])
            hrv_repo.log(s, user_id, d, float(r["hrv_rmssd"]))
    print(f"✓ {len(records)} noches HRV sincronizadas")
    return len(records)


def _sync_cronologia(client: GarminConnectClient, user_id: str) -> bool:
    """Body Battery + Stress del día → cache JSON."""
    today = DateT.today()
    raw_client = client.get_raw_client()
    points: list[dict] = []
    activities_markers: list[dict] = []
    sleep_windows: list[list[float]] = []

    # ---- Body Battery ----
    try:
        bb_raw = raw_client.get_body_battery(today.isoformat())
        if bb_raw and isinstance(bb_raw, list):
            arr = bb_raw[0].get("bodyBatteryValuesArray", []) or []
            for entry in arr:
                if len(entry) < 2 or entry[1] is None:
                    continue
                ts_ms = entry[0]
                value = entry[1]
                dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).astimezone()
                hour = dt.hour + dt.minute / 60
                points.append(
                    {
                        "hour": round(hour, 3),
                        "body_battery": int(value),
                        "stress": None,
                        "is_sleeping": False,
                        "is_active": False,
                    }
                )
    except Exception as exc:
        print(f"⚠️  Body Battery falló: {exc}")

    # ---- Stress (merge por hora) ----
    try:
        stress_raw = raw_client.get_stress_data(today.isoformat())
        if stress_raw:
            stress_values = stress_raw.get("stressValuesArray") or []
            # Map por timestamp para hacer merge
            by_hour: dict[float, int] = {}
            for entry in stress_values:
                if len(entry) < 2 or entry[1] is None:
                    continue
                ts_ms, value = entry[0], entry[1]
                dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).astimezone()
                hour = round(dt.hour + dt.minute / 60, 1)
                # value -1 = sleep, -2 = no data
                if value == -1:
                    if not any(h[0] <= hour <= h[1] for h in sleep_windows):
                        sleep_windows.append([hour - 0.05, hour + 0.05])
                elif value >= 0:
                    by_hour[hour] = max(by_hour.get(hour, 0), value)
            # Asignar a los puntos existentes
            for p in points:
                key = round(p["hour"], 1)
                if key in by_hour:
                    p["stress"] = by_hour[key]
    except Exception as exc:
        print(f"⚠️  Stress falló: {exc}")

    # ---- Sleep windows desde sleep data ----
    try:
        sleep = raw_client.get_sleep_data(today.isoformat())
        if sleep and sleep.get("dailySleepDTO"):
            d = sleep["dailySleepDTO"]
            start_ms = d.get("sleepStartTimestampGMT")
            end_ms = d.get("sleepEndTimestampGMT")
            if start_ms and end_ms:
                st = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc).astimezone()
                en = datetime.fromtimestamp(end_ms / 1000, tz=timezone.utc).astimezone()
                # Si el sueño cruza medianoche, mostrar desde el día de hoy
                start_hour = st.hour + st.minute / 60
                end_hour = en.hour + en.minute / 60
                if st.date() < today:
                    # Empezó ayer, parte visible es 0 -> end_hour
                    sleep_windows = [[0, end_hour]]
                else:
                    sleep_windows = [[start_hour, end_hour]]
                # Marcar puntos como sleeping
                for p in points:
                    for s_, e_ in sleep_windows:
                        if s_ <= p["hour"] <= e_:
                            p["is_sleeping"] = True
                            break
    except Exception as exc:
        print(f"⚠️  Sleep windows fallaron: {exc}")

    # ---- Marcador de última actividad del día ----
    try:
        acts = raw_client.get_activities(0, 5)
        for act in acts or []:
            start_local = act.get("startTimeLocal", "")
            if not start_local.startswith(today.isoformat()):
                continue
            dt = datetime.fromisoformat(start_local)
            hour = dt.hour + dt.minute / 60 + dt.second / 3600
            duration_min = (act.get("duration") or 0) / 60
            label = act.get("activityName") or "Entreno"
            distance_km = (act.get("distance") or 0) / 1000
            if distance_km:
                label = f"{label} · {distance_km:.2f} km"
            activities_markers.append(
                {
                    "hour": round(hour, 3),
                    "label": label,
                    "type": (act.get("activityType") or {}).get("typeKey", "run"),
                }
            )
            # Marcar puntos como activos durante la actividad
            for p in points:
                if hour <= p["hour"] <= hour + duration_min / 60:
                    p["is_active"] = True
    except Exception as exc:
        print(f"⚠️  Activities markers fallaron: {exc}")

    # Si no hay puntos de cronología (BB/stress vacíos) pero SÍ hay activities,
    # guardamos un cache mínimo para que /report y la UI puedan leer las actividades.
    if not points and not activities_markers:
        print("⚠️  Sin puntos ni actividades — cache no generado")
        return False

    if not points:
        print(
            f"⚠️  Sin puntos de cronología (BB/stress vacíos) — guardando cache "
            f"con {len(activities_markers)} actividad(es) únicamente"
        )

    # Summary
    bb_values = [p["body_battery"] for p in points if p["body_battery"] is not None]
    stress_values = [p["stress"] for p in points if p["stress"] is not None]
    sleep_min = int(sum((e - s) * 60 for s, e in sleep_windows))

    payload = {
        "fetched_at": datetime.now(tz=timezone.utc).isoformat(),
        "date": today.isoformat(),
        "points": points,
        "activities": activities_markers,
        "summary": {
            "body_battery_start": bb_values[0] if bb_values else 0,
            "body_battery_end": bb_values[-1] if bb_values else 0,
            "body_battery_max": max(bb_values) if bb_values else 0,
            "body_battery_min": min(bb_values) if bb_values else 0,
            "stress_avg": int(sum(stress_values) / len(stress_values)) if stress_values else 0,
            "stress_max": max(stress_values) if stress_values else 0,
            "sleep_duration_min": sleep_min,
        },
    }

    path = _cache_path("cronologia", user_id, today.isoformat())
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(
        f"✓ Cronología {len(points)} puntos · {len(activities_markers)} actividades · "
        f"{len(sleep_windows)} ventanas de sueño · cache → {path}"
    )
    return True


def _sync_activities_to_db(client: GarminConnectClient, user_id: str, lookback: int = 50) -> int:
    """Sincroniza últimas N actividades (de cualquier tipo) a la tabla `activities`.

    Para cada actividad: trae zone distribution (1 llamada extra) y hace UPSERT.
    Costo: ~50 calls extras, pero garantiza histórico sin depender de cache /tmp.
    """
    raw_client = client.get_raw_client()
    try:
        acts = raw_client.get_activities(0, lookback) or []
    except Exception as exc:
        print(f"⚠️  No pude listar actividades para persistir: {exc}")
        return 0

    if not acts:
        return 0

    saved = 0
    with session_scope() as s:
        users.ensure(s, user_id)
        for act in acts:
            try:
                aid = str(act["activityId"])
                # Zone distribution opcional (mejor effort)
                try:
                    zones = raw_client.get_activity_hr_in_timezones(aid) or []
                    total = sum((z.get("secsInZone") or 0) for z in zones)
                    if total > 0:
                        zone_pct = [0.0] * 5
                        for z in zones:
                            zn = z.get("zoneNumber")
                            if zn and 1 <= zn <= 5:
                                zone_pct[zn - 1] = round(((z.get("secsInZone") or 0) / total) * 100, 1)
                        act["zone_distribution_pct"] = zone_pct
                except Exception:
                    pass
                activities_repo.upsert(s, user_id, act)
                saved += 1
            except Exception as exc:
                print(f"⚠️  Actividad {act.get('activityId')} falló: {exc}")

    print(f"✓ {saved} actividades persistidas en BD (últimas {lookback})")
    return saved


def _sync_last_activity(client: GarminConnectClient, user_id: str) -> bool:
    """Última actividad de RUNNING con dynamics → cache JSON formato ActivityDetailOut.

    Esto es solo para la vista de detalle (samples + splits). El histórico
    completo va a la tabla `activities` vía `_sync_activities_to_db`.
    """
    raw_client = client.get_raw_client()

    try:
        acts = raw_client.get_activities(0, 10)
    except Exception as exc:
        print(f"⚠️  No pude listar actividades: {exc}")
        return False

    run_activity = None
    for act in acts or []:
        type_key = (act.get("activityType") or {}).get("typeKey", "")
        if "running" in type_key.lower():
            run_activity = act
            break

    if not run_activity:
        print("⚠️  Sin actividades de running recientes")
        return False

    activity_id = str(run_activity["activityId"])

    # Detalle con samples
    try:
        details = raw_client.get_activity_details(activity_id, maxchart=2000)
    except Exception as exc:
        print(f"⚠️  Detalle actividad falló: {exc}")
        return False

    metrics_map = {m["metricsIndex"]: m["key"] for m in details.get("metricDescriptors", [])}
    raw_metrics = details.get("activityDetailMetrics", [])

    def idx(key: str) -> int | None:
        for i, k in metrics_map.items():
            if k == key:
                return i
        return None

    i_t = idx("sumDuration")
    i_dist = idx("sumDistance")
    i_pace = idx("directSpeed")
    i_hr = idx("directHeartRate")
    # directDoubleCadence = total steps por minuto (ambos pies).
    # directRunCadence = pasos por pie (la mitad del valor que esperamos mostrar).
    # Preferimos el primero para que la cadencia salga en el rango 140-180 spm habitual.
    i_cad = idx("directDoubleCadence") or idx("directRunCadence")
    i_elev = idx("directElevation")
    i_pow = idx("directPower")

    samples = []
    for m in raw_metrics:
        vals = m.get("metrics", [])
        t_sec = vals[i_t] if i_t is not None and i_t < len(vals) and vals[i_t] is not None else None
        if t_sec is None:
            continue
        dist_m = vals[i_dist] if i_dist is not None and i_dist < len(vals) else None
        speed_mps = vals[i_pace] if i_pace is not None and i_pace < len(vals) else None
        pace_secs_per_km = int(1000 / speed_mps) if speed_mps and speed_mps > 0 else None
        hr = vals[i_hr] if i_hr is not None and i_hr < len(vals) and vals[i_hr] else None
        cad = vals[i_cad] if i_cad is not None and i_cad < len(vals) and vals[i_cad] else None
        elev = vals[i_elev] if i_elev is not None and i_elev < len(vals) and vals[i_elev] else None
        pw = vals[i_pow] if i_pow is not None and i_pow < len(vals) and vals[i_pow] else None
        samples.append(
            {
                "t_secs": int(t_sec),
                "distance_km": round((dist_m or 0) / 1000, 3),
                "pace_secs_per_km": pace_secs_per_km,
                "hr": int(hr) if hr else None,
                "cadence": int(cad) if cad else None,
                "elevation_m": int(elev) if elev else None,
                "power_w": int(pw) if pw else None,
            }
        )

    # Submuestreo si vienen >300 puntos (para no saturar el SVG)
    if len(samples) > 300:
        stride = len(samples) // 300
        samples = samples[::stride]

    # Splits
    splits = []
    try:
        split_data = raw_client.get_activity_splits(activity_id)
        for s_ in split_data.get("lapDTOs", []):
            avg_speed = s_.get("averageSpeed") or 0
            pace_secs = int(1000 / avg_speed) if avg_speed > 0 else 0
            splits.append(
                {
                    "km": s_.get("lapIndex"),
                    "time_secs": int(s_.get("duration") or 0),
                    "pace": f"{pace_secs // 60}:{(pace_secs % 60):02d}" if pace_secs else "—",
                    "avg_hr": int(s_.get("averageHR") or 0),
                    "max_hr": int(s_.get("maxHR") or 0),
                    "cadence": int(s_.get("averageRunCadence") or 0),
                    "stride_m": round((s_.get("strideLength") or 0) / 100, 2),
                    "gct_ms": int(s_.get("groundContactTime") or 0),
                    "elevation_gain_m": round(s_.get("elevationGain") or 0, 1),
                }
            )
    except Exception as exc:
        print(f"⚠️  Splits fallaron: {exc}")

    # Zone distribution
    zone_dist = [0.0, 0.0, 0.0, 0.0, 0.0]
    total_zone_secs = 0
    try:
        zones = raw_client.get_activity_hr_in_timezones(activity_id) or []
        total_zone_secs = sum((z.get("secsInZone") or 0) for z in zones)
        for z in zones:
            zn = z.get("zoneNumber")
            if zn and 1 <= zn <= 5 and total_zone_secs > 0:
                zone_dist[zn - 1] = round(((z.get("secsInZone") or 0) / total_zone_secs) * 100, 1)
    except Exception:
        pass

    duration_secs = int(run_activity.get("duration") or 0)
    distance_km = round((run_activity.get("distance") or 0) / 1000, 2)
    avg_pace_secs = int(duration_secs / distance_km / 1) if distance_km else 0
    avg_pace_per_km = int(duration_secs / distance_km) if distance_km else 0

    payload = {
        "activity_id": activity_id,
        "name": run_activity.get("activityName") or "Carrera",
        "started_at": run_activity.get("startTimeLocal", "")[:19],
        "type": "run",
        "distance_km": distance_km,
        "duration_secs": duration_secs,
        "avg_pace": f"{avg_pace_per_km // 60}:{(avg_pace_per_km % 60):02d}" if avg_pace_per_km else "—",
        "avg_hr": int(run_activity.get("averageHR") or 0),
        "max_hr": int(run_activity.get("maxHR") or 0),
        "elevation_gain_m": int(run_activity.get("elevationGain") or 0),
        "calories": int(run_activity.get("calories") or 0),
        "avg_cadence": int(run_activity.get("averageRunningCadenceInStepsPerMinute") or 0),
        "avg_stride_m": round(((run_activity.get("strideLength") or 0) / 100), 2),
        "avg_gct_ms": int(run_activity.get("groundContactTime") or 0),
        "training_effect_aerobic": round(run_activity.get("aerobicTrainingEffect") or 0, 1),
        "zone_distribution_pct": zone_dist,
        "samples": samples,
        "splits": splits,
    }

    path = _cache_path("activity", user_id, "latest")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(
        f"✓ Actividad '{payload['name']}' · {distance_km}km · "
        f"{len(samples)} samples · {len(splits)} splits · cache → {path}"
    )
    return True


def main(user_id: str) -> None:
    print(f"=== Sync Garmin real para user_id={user_id} ===\n")
    print("→ Login a Garmin Connect...")
    client = GarminConnectClient()
    print("✓ Login OK\n")

    print("→ Sincronizando HRV (14 noches)...")
    _sync_hrv(client, user_id)

    print("\n→ Sincronizando Cronología 24h (Body Battery + Stress + Sleep)...")
    _sync_cronologia(client, user_id)

    print("\n→ Persistiendo últimas 50 actividades en BD (histórico)...")
    _sync_activities_to_db(client, user_id, lookback=50)

    print("\n→ Sincronizando última actividad de running (detalle con samples)...")
    _sync_last_activity(client, user_id)

    print(f"\n✅ Sync completado. Cache en {CACHE_DIR}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", default="jose_dev_uid")
    args = parser.parse_args()
    main(args.user_id)
