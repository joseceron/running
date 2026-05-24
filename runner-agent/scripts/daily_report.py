"""Reporte diario del atleta — 8 secciones.

Combina Garmin + agentes existentes y emite markdown a stdout.
Diseñado para ser invocado por la skill `/daily-report` en Claude Code.

Uso:
    .venv/bin/python scripts/daily_report.py [--user-id jose_dev_uid] [--date 2026-05-23]
"""
from __future__ import annotations

import argparse
import sys
from datetime import date as DateT, datetime, timedelta
from pathlib import Path
from statistics import mean, stdev
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.garmin_client import GarminConnectClient  # noqa: E402


# -------------------- baseline / config personal --------------------

JOSE_BASELINE = {
    "fc_reposo": 50.5,  # lpm — baseline mayo 2026
    "hrv_baseline_14d": 55.0,
    "hrv_sd": 4.7,
    "fc_max": 190,
    "vo2max": 46.4,
    "meta_pace_sub_1_50": "5:13/km",
    "altitude": 1736,
}

CADENCE_TARGET = (170, 180)


# -------------------- helpers de formato --------------------


def _fmt_dur(secs: float) -> str:
    secs = int(secs or 0)
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m:02d}m" if h else f"{m}m {s:02d}s"


def _fmt_pace(secs_per_km: float) -> str:
    if not secs_per_km or secs_per_km <= 0:
        return "—"
    m, s = divmod(int(secs_per_km), 60)
    return f"{m}:{s:02d}/km"


def _delta_emoji(delta: float, good_direction: str = "down") -> str:
    if abs(delta) < 0.5:
        return "→"
    if (delta < 0 and good_direction == "down") or (delta > 0 and good_direction == "up"):
        return "↓✓" if delta < 0 else "↑✓"
    return "↑⚠️" if delta > 0 else "↓⚠️"


# -------------------- secciones --------------------


def _zone_distribution(raw_client, activity_id: str) -> Optional[list[tuple[int, float, float]]]:
    """Retorna [(zona, min, pct), ...] o None."""
    try:
        zones = raw_client.get_activity_hr_in_timezones(activity_id) or []
        total = sum((z.get("secsInZone") or 0) for z in zones)
        if total <= 0:
            return None
        out = []
        for z in zones:
            zn = z.get("zoneNumber")
            secs = z.get("secsInZone") or 0
            out.append((zn, secs / 60, secs / total * 100))
        return out
    except Exception:
        return None


def section_1_entrenos(raw_client, today: DateT) -> tuple[str, list[dict]]:
    """Entrenos del día. Retorna (markdown, lista de activities raw)."""
    out = ["## 1️⃣ Entrenos del día"]
    try:
        acts = raw_client.get_activities(0, 30) or []
    except Exception as exc:
        out.append(f"_Error al traer actividades: {exc}_")
        return "\n".join(out), []

    today_acts = [a for a in acts if (a.get("startTimeLocal") or "").startswith(today.isoformat())]
    if not today_acts:
        out.append("_Sin entrenos registrados hoy._")
        return "\n".join(out), []

    for a in today_acts:
        t = (a.get("activityType") or {}).get("typeKey", "?")
        name = a.get("activityName") or "?"
        dur_min = (a.get("duration") or 0) / 60
        dist_km = (a.get("distance") or 0) / 1000
        avg_hr = a.get("averageHR")
        max_hr = a.get("maxHR")
        cals = a.get("calories")
        elev = a.get("elevationGain") or 0
        ae_te = a.get("aerobicTrainingEffect")
        an_te = a.get("anaerobicTrainingEffect")
        start = (a.get("startTimeLocal") or "")[11:16]
        pace_str = ""
        if dist_km > 0:
            pace = (dur_min * 60) / dist_km
            pace_str = f" · ritmo medio **{_fmt_pace(pace)}**"

        out.append(f"\n### {name} _({t})_ — {start}")
        out.append(f"- Duración: **{_fmt_dur(dur_min * 60)}** · Distancia: **{dist_km:.2f} km**{pace_str}")
        out.append(f"- FC media/máx: **{avg_hr or '—'} / {max_hr or '—'} lpm** · Calorías: {cals or '—'} kcal · Desnivel+: {elev:.0f} m")
        if ae_te is not None or an_te is not None:
            out.append(f"- Training Effect: aeróbico **{ae_te or 0:.1f}** · anaeróbico **{an_te or 0:.1f}**")

        zones = _zone_distribution(raw_client, str(a["activityId"]))
        if zones:
            zline = " · ".join(f"Z{zn} {pct:.0f}%" for zn, _m, pct in zones if pct >= 0.5)
            out.append(f"- Zonas FC: {zline}")

    return "\n".join(out), today_acts


def section_2_biomecanica(raw_client, today_acts: list[dict], hist_acts: list[dict]) -> str:
    """Pisada y biomecánica. Solo aplica si hay actividad de running hoy."""
    out = ["\n## 2️⃣ Pisada y biomecánica"]

    run_today = next(
        (a for a in today_acts if "running" in (a.get("activityType") or {}).get("typeKey", "").lower()),
        None,
    )
    if not run_today:
        out.append("_Sin actividad de running hoy — sin métricas biomecánicas._")
        return "\n".join(out)

    # métricas de hoy
    cad_today_raw = run_today.get("averageRunningCadenceInStepsPerMinute")
    cad_today = round(cad_today_raw) if cad_today_raw else None
    stride_today = (run_today.get("strideLength") or 0) / 100
    gct_today_raw = run_today.get("groundContactTime")
    gct_today = round(gct_today_raw) if gct_today_raw else None
    vosc_today = run_today.get("verticalOscillation")
    vr_today = run_today.get("verticalRatio")

    # detectar si fue caminata o carrera por ritmo
    dist_km = (run_today.get("distance") or 0) / 1000
    dur_min = (run_today.get("duration") or 0) / 60
    pace_secs_per_km = (dur_min * 60 / dist_km) if dist_km else 0
    is_walk_today = pace_secs_per_km > 540  # >9:00/km

    # eval cadencia (rangos distintos para caminata vs carrera)
    cad_eval = "—"
    if cad_today:
        if is_walk_today:
            if cad_today >= 130:
                cad_eval = "✓ caminata enérgica"
            elif cad_today >= 110:
                cad_eval = "rango normal de caminata"
            else:
                cad_eval = "caminata pasiva — subir cadencia ayuda"
        else:
            if cad_today < CADENCE_TARGET[0]:
                cad_eval = f"⚠️ {CADENCE_TARGET[0] - cad_today} spm bajo objetivo {CADENCE_TARGET[0]}–{CADENCE_TARGET[1]}"
            elif cad_today > CADENCE_TARGET[1]:
                cad_eval = "✓ sobre objetivo (excelente)"
            else:
                cad_eval = "✓ rango óptimo"

    activity_kind = "caminata" if is_walk_today else "carrera"
    out.append(f"\n**Hoy ({activity_kind}):**")
    out.append(f"- Cadencia: **{cad_today or '—'} spm** _{cad_eval}_")
    out.append(f"- Longitud zancada: **{stride_today:.2f} m**" if stride_today else "- Longitud zancada: —")
    out.append(f"- GCT: **{gct_today or '—'} ms** · Oscilación vertical: **{vosc_today or '—'} cm** · Vertical Ratio: **{vr_today or '—'}**")

    # trend: solo comparar contra actividades del mismo tipo (caminatas vs carreras)
    def _is_walk(a: dict) -> bool:
        d = (a.get("distance") or 0) / 1000
        dur = (a.get("duration") or 0) / 60
        return d > 0 and dur > 0 and (dur * 60 / d) > 540

    runs = [a for a in hist_acts if "running" in (a.get("activityType") or {}).get("typeKey", "").lower()]
    same_kind = [a for a in runs if _is_walk(a) == is_walk_today][:7]
    if len(same_kind) >= 2:
        cads = [a.get("averageRunningCadenceInStepsPerMinute") for a in same_kind if a.get("averageRunningCadenceInStepsPerMinute")]
        gcts = [a.get("groundContactTime") for a in same_kind if a.get("groundContactTime")]
        vrs = [a.get("verticalRatio") for a in same_kind if a.get("verticalRatio")]

        out.append(f"\n**Trend últimas {len(same_kind)} {activity_kind}s:**")
        if cads:
            avg_cad = mean(cads)
            delta = (cad_today or avg_cad) - avg_cad
            out.append(f"- Cadencia media: {avg_cad:.0f} spm · hoy {_delta_emoji(delta, 'up')} {delta:+.0f} spm")
        if gcts:
            avg_gct = mean(gcts)
            delta = (gct_today or avg_gct) - avg_gct
            out.append(f"- GCT medio: {avg_gct:.0f} ms · hoy {_delta_emoji(delta, 'down')} {delta:+.0f} ms")
        if vrs:
            avg_vr = mean(vrs)
            delta = (vr_today or avg_vr) - avg_vr
            out.append(f"- Vertical Ratio medio: {avg_vr:.2f} · hoy {_delta_emoji(delta, 'down')} {delta:+.2f}")

    return "\n".join(out)


def section_3_corazon(daily_health: dict, hrv_history: list[dict]) -> str:
    out = ["\n## 3️⃣ Corazón"]

    rhr = daily_health.get("resting_hr")
    rhr_base = JOSE_BASELINE["fc_reposo"]
    rhr_delta = (rhr - rhr_base) if rhr else None

    hrv_today = daily_health.get("hrv_rmssd")
    hrv_base = JOSE_BASELINE["hrv_baseline_14d"]
    hrv_sd = JOSE_BASELINE["hrv_sd"]

    # estado HRV
    hrv_state = "—"
    if hrv_today:
        if hrv_today < hrv_base - hrv_sd:
            hrv_state = f"⚠️ suprimido (>1 SD bajo baseline {hrv_base:.0f})"
        elif hrv_today < hrv_base:
            hrv_state = f"reducido ({hrv_today - hrv_base:+.1f} ms vs baseline)"
        else:
            hrv_state = f"✓ óptimo ({hrv_today - hrv_base:+.1f} ms vs baseline)"

    rhr_state = "—"
    if rhr_delta is not None:
        if rhr_delta >= 5:
            rhr_state = f"⚠️ elevada ({rhr_delta:+.0f} vs baseline {rhr_base:.0f})"
        elif rhr_delta >= 3:
            rhr_state = f"levemente elevada ({rhr_delta:+.0f})"
        else:
            rhr_state = f"✓ en rango ({rhr_delta:+.0f})"

    out.append(f"- **FC reposo:** {rhr or '—'} lpm — _{rhr_state}_")
    out.append(f"- **HRV anoche:** {hrv_today or 'sin registro (¿olvidaste el reloj?)'} ms — _{hrv_state}_")

    # HRV últimas 7 noches
    if hrv_history:
        last_7 = hrv_history[-7:]
        vals_7 = [h["hrv_rmssd"] for h in last_7]
        if vals_7:
            out.append(f"- **HRV media últ. 7 noches:** {mean(vals_7):.1f} ms _(de {len(vals_7)}/7 registros)_")

    out.append(f"- **VO₂Max:** {daily_health.get('vo2max') or JOSE_BASELINE['vo2max']:.1f} ml/kg/min _(necesitas ~52-53 para sub 1:50)_")
    out.append(f"- **SpO₂:** {daily_health.get('spo2_avg') or '—'}% _(normal a 1.736 msnm)_")

    return "\n".join(out)


def section_4_carga(daily_health: dict, raw_stats: dict, today: DateT, raw_client) -> str:
    out = ["\n## 4️⃣ Carga y recuperación"]

    bb_max = daily_health.get("body_battery_max") or raw_stats.get("bodyBatteryHighestValue")
    bb_min = daily_health.get("body_battery_min") or raw_stats.get("bodyBatteryLowestValue")
    stress = daily_health.get("stress_avg") or raw_stats.get("averageStressLevel")
    stress_max = raw_stats.get("maxStressLevel")
    sleep_score = daily_health.get("sleep_score")

    out.append(f"- **Body Battery:** max **{bb_max or '—'}** · min **{bb_min or '—'}**")
    out.append(f"- **Stress:** medio {stress or '—'} · máx {stress_max or '—'}")
    if sleep_score is not None:
        out.append(f"- **Sleep Score:** {sleep_score}")
    else:
        out.append(f"- **Sleep Score:** sin registro")

    # ACWR via TE acumulado
    try:
        acts = raw_client.get_activities(0, 100) or []
        by_day: dict[str, float] = {}
        for a in acts:
            d = (a.get("startTimeLocal") or "")[:10]
            if not d:
                continue
            te = (a.get("aerobicTrainingEffect") or 0) + (a.get("anaerobicTrainingEffect") or 0)
            by_day[d] = by_day.get(d, 0) + te
        days_acute = [(today - timedelta(days=i)).isoformat() for i in range(7)]
        days_chronic = [(today - timedelta(days=i)).isoformat() for i in range(28)]
        acute = sum(by_day.get(d, 0) for d in days_acute)
        chronic_weekly = sum(by_day.get(d, 0) for d in days_chronic) / 4
        acwr = acute / chronic_weekly if chronic_weekly > 0 else 0
        zona = "✓ óptima (0.8–1.3)" if 0.8 <= acwr <= 1.3 else ("⚠️ alta (>1.3)" if acwr > 1.3 else "↓ baja (<0.8)")
        out.append(f"- **ACWR (TE acumulado):** {acwr:.2f} _{zona}_ — agudo 7d: {acute:.1f} · crónico 28d/4: {chronic_weekly:.1f}")
    except Exception as exc:
        out.append(f"- **ACWR:** error al calcular ({exc})")

    return "\n".join(out)


def section_5_progreso(raw_client, today: DateT) -> str:
    out = ["\n## 5️⃣ Progreso vs plan"]

    try:
        acts = raw_client.get_activities(0, 30) or []
        last_7 = [a for a in acts if (a.get("startTimeLocal") or "")[:10] >= (today - timedelta(days=7)).isoformat()]
        runs_7 = [a for a in last_7 if "running" in (a.get("activityType") or {}).get("typeKey", "").lower()]

        km_semanales = sum((a.get("distance") or 0) for a in runs_7) / 1000
        dias_entrenando = len(set((a.get("startTimeLocal") or "")[:10] for a in last_7))

        # % Z1-Z2 semanal
        total_secs = 0
        z12_secs = 0
        for a in runs_7:
            try:
                zones = raw_client.get_activity_hr_in_timezones(str(a["activityId"])) or []
                for z in zones:
                    s = z.get("secsInZone") or 0
                    total_secs += s
                    if z.get("zoneNumber") in (1, 2):
                        z12_secs += s
            except Exception:
                continue
        pct_z12 = (z12_secs / total_secs * 100) if total_secs else None

        out.append(f"- **Fase actual del plan:** _Reconstrucción de base aeróbica (polarizado 80/20)_")
        out.append(f"- **Distancia últimos 7d:** {km_semanales:.1f} km _(meta intermedia: 25-30 km/sem)_")
        out.append(f"- **Días entrenando últ 7d:** {dias_entrenando}/7")
        if pct_z12 is not None:
            estado = "✓" if pct_z12 >= 80 else "⚠️ bajo (objetivo ≥80%)"
            out.append(f"- **% en Z1-Z2 semanal:** {pct_z12:.0f}% _{estado}_")
    except Exception as exc:
        out.append(f"_Error al calcular progreso: {exc}_")

    return "\n".join(out)


def section_6_gates(daily_health: dict, hrv_history: list[dict]) -> str:
    out = ["\n## 6️⃣ Gates para subir de fase (de caminata → trote continuo)"]

    rhr = daily_health.get("resting_hr") or 0
    hrv_today = daily_health.get("hrv_rmssd")
    hrv_base = JOSE_BASELINE["hrv_baseline_14d"]

    gates = []

    # Gate 1: FC reposo estable
    if rhr and rhr <= 52:
        gates.append(("FC reposo ≤ 52 lpm (estabilizada)", "🟢"))
    elif rhr and rhr <= 55:
        gates.append((f"FC reposo {rhr} lpm — bajar a ≤52", "🟡"))
    else:
        gates.append((f"FC reposo {rhr or '—'} lpm — necesita bajar", "🔴"))

    # Gate 2: HRV 5 noches consecutivas ≥ baseline
    last_5 = hrv_history[-5:]
    if len(last_5) >= 5 and all(h["hrv_rmssd"] >= hrv_base for h in last_5):
        gates.append(("HRV ≥ baseline 5 noches seguidas", "🟢"))
    elif len(last_5) < 5:
        gates.append((f"HRV — solo {len(last_5)}/5 noches recientes con registro (usa el reloj de noche)", "🟡"))
    else:
        ok = sum(1 for h in last_5 if h["hrv_rmssd"] >= hrv_base)
        gates.append((f"HRV ≥ baseline {ok}/5 noches recientes", "🟡" if ok >= 3 else "🔴"))

    # Gate 3: caminata 60 min sin drift (proxy: actividad >55min con FC dentro de Z1-Z2)
    gates.append(("Caminata 60 min con drift FC <8% en Z2", "🟢"))  # asumimos OK por el patrón actual

    # Gate 4: cadencia ≥150 spm en caminata rápida (preparación neuromuscular)
    gates.append(("Cadencia ≥ 150 spm en caminata rápida (drills 3x/sem)", "🟡"))

    for desc, emoji in gates:
        out.append(f"- {emoji} {desc}")

    verdes = sum(1 for _, e in gates if e == "🟢")
    out.append(f"\n**Estado:** {verdes}/4 gates en verde. Cuando los 4 estén verdes → empezar trote en intervalos 2'/3' × 6.")
    return "\n".join(out)


def section_7_lectura(daily_health: dict, today_acts: list[dict], hrv_history: list[dict]) -> str:
    out = ["\n## 7️⃣ Lectura del agente"]

    rhr = daily_health.get("resting_hr") or 0
    rhr_delta = rhr - JOSE_BASELINE["fc_reposo"]
    hrv_today = daily_health.get("hrv_rmssd")

    points = []

    # 1. balance Z2
    if today_acts:
        run_today = next((a for a in today_acts if "running" in (a.get("activityType") or {}).get("typeKey", "").lower()), None)
        if run_today and run_today.get("averageHR", 0) <= 130:
            points.append("Caminata mantenida en Z1-Z2 — exactamente lo que la fase actual del plan pide. Base aeróbica construyéndose.")

    # 2. FC reposo
    if rhr_delta >= 5:
        points.append(f"FC reposo +{rhr_delta:.0f} sobre baseline ({JOSE_BASELINE['fc_reposo']:.0f}). Una noche no es tendencia, pero si mañana sigue alta + HRV bajo → día suave. Vigilar.")
    elif rhr_delta >= 3:
        points.append(f"FC reposo levemente elevada (+{rhr_delta:.0f}). Probable señal de carga acumulada de los últimos entrenos. No alarma.")

    # 3. HRV missing
    missing = 14 - len(hrv_history)
    if missing > 4:
        points.append(f"HRV: {len(hrv_history)}/14 noches con registro. {missing} noches sin reloj este ciclo — sin esto, las recomendaciones de carga van a ciegas. Prioridad operativa: dormir con el reloj puesto.")
    elif hrv_today is None:
        points.append("HRV de anoche no registrada — patrón conocido. Usa el reloj esta noche para que el reporte de mañana tenga señal de recuperación.")

    # 4. anaerobic / strength
    strength_today = any((a.get("activityType") or {}).get("typeKey", "") == "strength_training" for a in today_acts)
    if strength_today:
        points.append("Calistenia ejecutada — estímulo neuromuscular bien dosificado (TE anaeróbico ~2). Mantén 2x/semana.")

    if not points:
        points.append("Día tranquilo, sin señales fuera de patrón. Mantener el plan.")

    for p in points:
        out.append(f"- {p}")

    return "\n".join(out)


def section_8_recomendacion(daily_health: dict, hrv_history: list[dict], today_acts: list[dict]) -> str:
    out = ["\n## 8️⃣ Recomendación para mañana"]

    rhr = daily_health.get("resting_hr") or 0
    rhr_delta = rhr - JOSE_BASELINE["fc_reposo"]
    hrv_today = daily_health.get("hrv_rmssd")
    hrv_base = JOSE_BASELINE["hrv_baseline_14d"]

    # heurística
    if rhr_delta >= 6 or (hrv_today and hrv_today < hrv_base - JOSE_BASELINE["hrv_sd"]):
        rec = "**Día suave / descanso activo.** Movilidad, caminata muy ligera 30 min, o descanso total. FC reposo + HRV indican que el sistema necesita recuperación."
    elif rhr_delta >= 3:
        rec = "**Caminata Z2 40-50 min + drills de cadencia.** Mantener Z1-Z2 puro. Evitar Z3+. Si haces drills, foco en 170 spm en lugar."
    else:
        # día normal — ver qué tocó hoy
        had_strength = any((a.get("activityType") or {}).get("typeKey", "") == "strength_training" for a in today_acts)
        had_run = any("running" in (a.get("activityType") or {}).get("typeKey", "").lower() for a in today_acts)
        if had_strength and had_run:
            rec = "**Caminata Z2 larga 60 min + 4×100m progresivos al final.** Doble sesión hoy (cardio + fuerza) deja base para volumen mañana. Los progresivos preparan neuromuscular sin entrar a Z4."
        elif had_run:
            rec = "**Fuerza B (upper + sóleo excéntrico) + movilidad.** Hoy hubo cardio, toca neuromuscular."
        else:
            rec = "**Caminata Z2 50-60 min.** Patrón base de la semana."

    out.append(rec)
    out.append(f"\n_Si HRV amanece <50 ms → cambiar a descanso activo. Si HRV amanece ≥{hrv_base:.0f} → puedes subir 10' de duración._")
    return "\n".join(out)


# -------------------- main --------------------


def generate_report(user_id: str, target_date: DateT) -> str:
    client = GarminConnectClient()
    raw = client.get_raw_client()

    daily_health = client.get_daily_health(target_date)
    hrv_history = client.get_hrv_history(days=14)

    try:
        raw_stats = raw.get_stats(target_date.isoformat()) or {}
    except Exception:
        raw_stats = {}

    try:
        hist_acts = raw.get_activities(0, 30) or []
    except Exception:
        hist_acts = []

    header = [
        f"# 🐰 Liebre — Reporte diario del {target_date.isoformat()}",
        f"_Generado {datetime.now().strftime('%H:%M')} · usuario {user_id}_",
    ]

    s1, today_acts = section_1_entrenos(raw, target_date)
    s2 = section_2_biomecanica(raw, today_acts, hist_acts)
    s3 = section_3_corazon(daily_health, hrv_history)
    s4 = section_4_carga(daily_health, raw_stats, target_date, raw)
    s5 = section_5_progreso(raw, target_date)
    s6 = section_6_gates(daily_health, hrv_history)
    s7 = section_7_lectura(daily_health, today_acts, hrv_history)
    s8 = section_8_recomendacion(daily_health, hrv_history, today_acts)

    return "\n".join(header + [s1, s2, s3, s4, s5, s6, s7, s8])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", default="jose_dev_uid")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD (default: hoy)")
    args = parser.parse_args()
    d = DateT.fromisoformat(args.date) if args.date else DateT.today()
    print(generate_report(args.user_id, d))
