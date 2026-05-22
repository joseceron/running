"""Cliente Garmin Connect usando python-garminconnect."""
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()

# garth guarda tokens en este directorio para evitar re-autenticarse cada vez
TOKENSTORE = str(Path(__file__).parent.parent / ".garmin_tokens")


class GarminConnectClient:
    def __init__(self):
        email = os.environ.get("GARMIN_EMAIL")
        password = os.environ.get("GARMIN_PASSWORD")
        if not email or not password:
            raise ValueError(
                "GARMIN_EMAIL y GARMIN_PASSWORD deben estar definidos en .env"
            )
        self._client = Garmin(email, password)
        self._login()

    def _login(self):
        Path(TOKENSTORE).mkdir(exist_ok=True)
        self._client.login(TOKENSTORE)

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
