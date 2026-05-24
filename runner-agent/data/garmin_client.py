"""Cliente Garmin Connect usando python-garminconnect.

Multi-tenant: cada instancia se construye con las credenciales del usuario
(o, en último recurso, las del `.env` legacy). El `token_dir` también se
aísla por hash del email para evitar que dos usuarios compartan tokens en
el filesystem (lo cual romper el login del segundo en Cloud Run).
"""
import hashlib
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from garminconnect import Garmin
from sqlalchemy.orm import Session

load_dotenv()

# Directorio raíz para tokens. En Cloud Run solo /tmp es escribible.
_DEFAULT_TOKEN_ROOT = (
    Path("/tmp/garmin_tokens")
    if Path("/tmp").is_dir() and os.environ.get("K_SERVICE")  # Cloud Run env var
    else Path(__file__).parent.parent / ".garmin_tokens"
)


def _token_dir_for(email: str, root: Path | None = None) -> Path:
    """Subdirectorio único por usuario (hash del email truncado).

    No usamos el user_id porque el token store está conceptualmente atado a
    la cuenta Garmin, no al user_id de Liebre. Si dos users de Liebre por
    error apuntan a la misma cuenta Garmin (no debería pasar, pero...),
    comparten tokens — lo cual está bien.
    """
    h = hashlib.sha256(email.lower().encode("utf-8")).hexdigest()[:16]
    return (root or _DEFAULT_TOKEN_ROOT) / h


class GarminConnectClient:
    """Wrapper sobre python-garminconnect.

    Construcción:
    - Default (legacy CLI): `GarminConnectClient()` lee del `.env`.
    - Per-user: `GarminConnectClient(email, password)` con credenciales explícitas.
    - Desde BD: `GarminConnectClient.for_user(session, user_id)` lee de
      `garmin_credentials` (cifrado) y construye la instancia.
    """

    def __init__(
        self,
        email: str | None = None,
        password: str | None = None,
        token_dir: Path | str | None = None,
    ):
        if email is None or password is None:
            env_email = os.environ.get("GARMIN_EMAIL")
            env_password = os.environ.get("GARMIN_PASSWORD")
            if not env_email or not env_password:
                raise ValueError(
                    "Sin credenciales: pasa email+password o define "
                    "GARMIN_EMAIL/GARMIN_PASSWORD en el entorno"
                )
            email = email or env_email
            password = password or env_password
        self._email = email
        self._token_dir = Path(token_dir) if token_dir else _token_dir_for(email)
        self._client = Garmin(email, password)
        self._login()

    @classmethod
    def for_user(cls, session: Session, user_id: str) -> "GarminConnectClient":
        """Construye el cliente leyendo credenciales cifradas de la BD."""
        # Import local para evitar ciclo (repos importan models que importan...)
        from memory.repositories import garmin_credentials as creds_repo

        decrypted = creds_repo.get_decrypted(session, user_id)
        if decrypted is None:
            raise LookupError(
                f"user_id={user_id!r} no tiene credenciales Garmin guardadas. "
                "Pídele que las configure en /dashboard/settings."
            )
        email, password = decrypted
        try:
            instance = cls(email=email, password=password)
        except Exception as exc:
            creds_repo.mark_login_failed(session, user_id, str(exc))
            raise
        creds_repo.mark_login_ok(session, user_id)
        return instance

    def _login(self):
        self._token_dir.mkdir(parents=True, exist_ok=True)
        self._client.login(str(self._token_dir))

    def get_raw_client(self):
        """Expone el cliente Garmin subyacente para operaciones de bulk."""
        return self._client

    def get_daily_health(self, target_date: date) -> dict:
        """Retorna HRV, Body Battery, FC reposo, SpO₂, sueño, estrés, VO₂Max para una fecha."""
        date_str = target_date.isoformat()
        result = {
            "date": date_str,
            "hrv_rmssd": None,
            "body_battery_max": None,
            "body_battery_min": None,
            "resting_hr": None,
            "spo2_avg": None,
            "sleep_score": None,
            "sleep_deep_seconds": None,
            "sleep_rem_seconds": None,
            "sleep_light_seconds": None,
            "stress_avg": None,
            "vo2max": None,
        }

        try:
            hrv = self._client.get_hrv_data(date_str)
            if hrv:
                summary = hrv.get("hrvSummary") or {}
                result["hrv_rmssd"] = summary.get("lastNightAvg")
        except Exception:
            pass

        try:
            bb = self._client.get_body_battery(date_str)
            if bb and isinstance(bb, list) and bb[0].get("bodyBatteryValuesArray"):
                values = [entry[1] for entry in bb[0]["bodyBatteryValuesArray"] if len(entry) > 1]
                if values:
                    result["body_battery_max"] = max(values)
                    result["body_battery_min"] = min(values)
        except Exception:
            pass

        try:
            stats = self._client.get_stats(date_str)
            if stats:
                result["resting_hr"] = stats.get("restingHeartRate")
                result["stress_avg"] = stats.get("averageStressLevel")
        except Exception:
            pass

        try:
            max_metrics = self._client.get_max_metrics(date_str)
            if max_metrics and isinstance(max_metrics, list) and max_metrics[0].get("generic"):
                result["vo2max"] = max_metrics[0]["generic"].get("vo2MaxPreciseValue")
        except Exception:
            pass

        try:
            spo2 = self._client.get_spo2_data(date_str)
            if spo2:
                result["spo2_avg"] = spo2.get("averageSpO2")
        except Exception:
            pass

        try:
            sleep = self._client.get_sleep_data(date_str)
            if sleep:
                daily = sleep.get("dailySleepDTO") or {}
                result["sleep_score"] = daily.get("sleepScores", {}).get("overall", {}).get("value")
                result["sleep_deep_seconds"] = daily.get("deepSleepSeconds")
                result["sleep_rem_seconds"] = daily.get("remSleepSeconds")
                result["sleep_light_seconds"] = daily.get("lightSleepSeconds")
        except Exception:
            pass

        return result

    def get_last_run_dynamics(self) -> Optional[dict]:
        """Retorna running dynamics de la última actividad de tipo carrera."""
        try:
            activities = self._client.get_activities(0, 10)
        except Exception as e:
            raise RuntimeError(f"Error al obtener actividades: {e}")

        run_activity = None
        for act in activities:
            act_type = (act.get("activityType") or {}).get("typeKey", "")
            if "running" in act_type.lower():
                run_activity = act
                break

        if run_activity is None:
            return None

        activity_id = run_activity["activityId"]

        try:
            details = self._client.get_activity_details(activity_id)
        except Exception as e:
            raise RuntimeError(f"Error al obtener detalles de actividad {activity_id}: {e}")

        metrics_map = {}
        for m in details.get("metricDescriptors", []):
            metrics_map[m["metricsIndex"]] = m["key"]

        raw_metrics = details.get("activityDetailMetrics", [])

        def avg(key):
            vals = [
                m["metrics"][i]
                for m in raw_metrics
                for i, k in metrics_map.items()
                if k == key and i < len(m["metrics"]) and m["metrics"][i] is not None
            ]
            return sum(vals) / len(vals) if vals else None

        splits = []
        try:
            split_data = self._client.get_activity_splits(activity_id)
            for s in split_data.get("lapDTOs", []):
                splits.append({
                    "km": s.get("lapIndex"),
                    "pace_secs_per_km": s.get("averageSpeed"),
                    "hr": s.get("averageHR"),
                    "cadence": s.get("averageRunCadence"),
                })
        except Exception:
            pass

        hr_zones = []
        try:
            zone_data = self._client.get_activity_hr_in_timezones(activity_id)
            if zone_data:
                for z in zone_data:
                    hr_zones.append({
                        "zone": z.get("zoneNumber"),
                        "seconds_in_zone": z.get("secsInZone"),
                    })
        except Exception:
            pass

        return {
            "activity_id": activity_id,
            "date": run_activity.get("startTimeLocal", "")[:10],
            "distance_m": run_activity.get("distance"),
            "duration_secs": run_activity.get("duration"),
            "avg_hr": run_activity.get("averageHR"),
            "cadence_avg": run_activity.get("averageRunningCadenceInStepsPerMinute"),
            "vertical_oscillation_cm": avg("directVerticalOscillation"),
            "vertical_ratio_pct": avg("directVerticalRatio"),
            "gct_avg_ms": avg("directGroundContactTime"),
            "gct_balance_left_pct": avg("directGroundContactBalance"),
            "stride_length_m": avg("directStrideLength"),
            "splits": splits,
            "hr_zones": hr_zones,
        }

    def get_hrv_history(self, days: int = 14) -> list[dict]:
        """Retorna registros HRV nocturnos de los últimos N días."""
        today = date.today()
        records = []
        for i in range(days):
            d = today - timedelta(days=i)
            date_str = d.isoformat()
            try:
                hrv = self._client.get_hrv_data(date_str)
                if hrv:
                    summary = hrv.get("hrvSummary") or {}
                    rmssd = summary.get("lastNightAvg")
                    if rmssd is not None:
                        records.append({"date": date_str, "hrv_rmssd": rmssd})
            except Exception:
                pass
        return list(reversed(records))
