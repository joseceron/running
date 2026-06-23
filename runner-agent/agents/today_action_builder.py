"""Builder compartido de `today_action`.

Decide inequívocamente qué hacer hoy (descanso / recuperación activa / entrenar
/ ya entrenó) combinando plan semanal + ACWR + HRV + actividades ejecutadas.

Históricamente esta lógica vivía dentro de `api/routers/report.py`, pero el LLM
del diagnóstico (`agents/diagnostic_v2.py`) no la veía — así que podía
recomendar "ejecuta 45 min de rodaje" un día marcado como descanso. Al
extraerla aquí, ambos consumidores (report.py y diagnostic_v2.py) parten de la
misma fuente de verdad.

La función retorna un dict simple (no Pydantic) para evitar acoplar este módulo
al esquema HTTP. Cada consumidor lo envuelve en su propio modelo si necesita.
"""

from __future__ import annotations

from datetime import date as DateT, timedelta
from typing import TypedDict

from api.utils.timezone import local_today


# Plan semanal genérico (polarizado 80/20 aeróbico, neutro a cualquier corredor).
# 0 = lunes, 6 = domingo. Cada user puede sobreescribir esto desde
# runner_profile.weekly_plan (JSONB) y se inyecta via param `weekday_plan`
# en build_today_action().
DEFAULT_WEEKDAY_PLAN: dict[int, tuple[str, str]] = {
    0: ("train", "Fuerza + Pliometría · 50 min"),
    1: ("train", "Trote suave Z2 · 55-65 min"),
    2: ("rest", "Descanso o movilidad"),
    3: ("train", "Fuerza + Pliometría · 50 min"),
    4: ("train", "Trote suave Z2 · 55-65 min"),
    5: ("train", "Rodaje largo Z2 · 75-90 min"),
    6: ("rest", "Descanso programado"),
}

# Alias retro-compatible — los tests existentes y código viejo importan este
# nombre. Apunta al default genérico, no al plan de José.
WEEKDAY_PLAN = DEFAULT_WEEKDAY_PLAN


def _coerce_plan(plan: dict | None) -> dict[int, tuple[str, str]]:
    """Acepta dict[int, (status, label)] o dict[str, [status, label]] (JSONB)
    y normaliza a la forma int → tuple. Si llega None, devuelve el default."""
    if not plan:
        return DEFAULT_WEEKDAY_PLAN
    normalized: dict[int, tuple[str, str]] = {}
    for k, v in plan.items():
        idx = int(k) if isinstance(k, str) else k
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            normalized[idx] = (str(v[0]), str(v[1]))
    # Si vino incompleto, rellenar con el default
    for idx, default_v in DEFAULT_WEEKDAY_PLAN.items():
        normalized.setdefault(idx, default_v)
    return normalized


_DAY_NAMES = [
    "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo",
]


class TodayActionData(TypedDict):
    status: str
    temporal: str
    headline: str
    short_reason: str
    reasons: list[str]
    allowed: list[str]
    next_session: str


def build_today_action(
    target: DateT,
    activity_labels: list[str],
    acwr: float | None,
    hrv_today: float | None,
    hrv_baseline: float | None,
    hrv_sd: float = 4.7,
    weekday_plan: dict | None = None,
) -> TodayActionData:
    """Devuelve la decisión inequívoca para `target`.

    `activity_labels` es la lista de labels (strings) de las actividades
    ejecutadas en `target`. Aceptamos strings — no objetos — para no acoplar
    este módulo a `ActivityTodayOut` ni a otros DTOs.

    `weekday_plan` permite override per-user (vino de runner_profile.weekly_plan
    JSONB). Si None, se usa DEFAULT_WEEKDAY_PLAN.
    """
    plan = _coerce_plan(weekday_plan)
    weekday = target.weekday()
    planned_status, planned_session = plan[weekday]
    today_real = local_today()

    # ─── PASADO ─────────────────────────────────────────────
    if target < today_real:
        date_label = _DAY_NAMES[weekday] + " " + target.strftime("%d %b").lower()
        if activity_labels:
            labels = ", ".join(
                lbl.split(" · ")[0] for lbl in activity_labels[:3]
            )
            n = len(activity_labels)
            return TodayActionData(
                status="past_executed",
                temporal="past",
                headline="EJECUTADO ✓",
                short_reason=(
                    f"{date_label}: {n} sesión"
                    f"{'es' if n > 1 else ''} registrada"
                    f"{'s' if n > 1 else ''} — {labels}."
                ),
                reasons=[
                    f"Plan original del día: {planned_session}",
                    "Ver detalle en sección de entrenos del día abajo",
                ],
                allowed=[],
                next_session="",
            )
        if planned_status == "rest":
            return TodayActionData(
                status="past_rest_planned",
                temporal="past",
                headline="DESCANSO PROGRAMADO ✓",
                short_reason=f"{date_label}: día de descanso del plan semanal.",
                reasons=[
                    "No requería actividad — recuperación parte del plan polarizado",
                ],
                allowed=[],
                next_session="",
            )
        return TodayActionData(
            status="past_missed",
            temporal="past",
            headline="SESIÓN NO REALIZADA",
            short_reason=(
                f"{date_label}: planificada {planned_session.lower()} pero sin registro."
            ),
            reasons=[
                f"Plan original del día: {planned_session}",
                "Saltarse sesiones programadas afecta el ACWR y rompe el ritmo de adaptación",
            ],
            allowed=[],
            next_session="",
        )

    # ─── FUTURO ─────────────────────────────────────────────
    if target > today_real:
        date_label = _DAY_NAMES[weekday] + " " + target.strftime("%d %b").lower()
        if planned_status == "rest":
            return TodayActionData(
                status="future_planned",
                temporal="future",
                headline="DESCANSO PLANIFICADO",
                short_reason=f"{date_label}: día de descanso del plan semanal.",
                reasons=["Recuperación programada — sin sesión prevista"],
                allowed=[],
                next_session="",
            )
        return TodayActionData(
            status="future_planned",
            temporal="future",
            headline=f"PLANIFICADO: {planned_session}",
            short_reason=f"{date_label}: sesión prevista del plan polarizado.",
            reasons=[
                f"Plan semanal de ese día: {planned_session}",
                "La recomendación final dependerá de HRV/ACWR esa mañana",
            ],
            allowed=[],
            next_session="",
        )

    # ─── HOY ────────────────────────────────────────────────

    # Próxima sesión (día siguiente que toque entrenar) — usa el mismo plan
    # que ya resolvimos arriba, no el global, para respetar overrides per-user.
    next_session = ""
    for offset in range(1, 8):
        d = target + timedelta(days=offset)
        st, sess = plan[d.weekday()]
        if st == "train":
            label = "Mañana" if offset == 1 else _DAY_NAMES[d.weekday()].capitalize()
            next_session = f"{label}: {sess}"
            break

    # Caso 1: ya entrenó hoy
    if activity_labels:
        labels = ", ".join(lbl.split(" · ")[0] for lbl in activity_labels[:3])
        n = len(activity_labels)
        return TodayActionData(
            status="trained_already",
            temporal="today",
            headline="HOY YA ENTRENASTE",
            short_reason=(
                f"{n} sesión{'es' if n > 1 else ''} registrada"
                f"{'s' if n > 1 else ''}: {labels}."
            ),
            reasons=[
                "Carga de hoy ya absorbida — no agregar más sesiones",
                "Si quieres complemento: movilidad, estiramientos o caminata corta (sin reloj)",
            ],
            allowed=[
                "Estiramientos / foam roller (15-20 min)",
                "Movilidad articular o yoga ligero",
                "Caminata corta de paseo (≤30 min, conversacional)",
            ],
            next_session=next_session,
        )

    # Señales de alerta para forzar descanso aunque el plan diga entrenar
    high_acwr = acwr is not None and acwr > 1.3
    suppressed_hrv = (
        hrv_today is not None
        and hrv_baseline is not None
        and hrv_today < hrv_baseline - hrv_sd
    )
    reduced_hrv = (
        hrv_today is not None
        and hrv_baseline is not None
        and hrv_today < hrv_baseline
        and not suppressed_hrv
    )

    # Caso 2: HRV muy suprimido → descanso aunque toque entrenar
    if suppressed_hrv:
        assert hrv_today is not None and hrv_baseline is not None
        return TodayActionData(
            status="rest",
            temporal="today",
            headline="DESCANSA HOY",
            short_reason=(
                f"Tu HRV ({hrv_today:.0f} ms) está suprimido vs baseline "
                f"({hrv_baseline:.0f}). Sistema nervioso pidiendo recuperación."
            ),
            reasons=[
                f"HRV {hrv_today:.0f} ms = {hrv_today - hrv_baseline:+.0f} ms vs baseline (zona suprimida)",
                "Entrenar con HRV deprimido aumenta riesgo de sobreuso y no genera adaptación",
            ],
            allowed=[
                "Movilidad articular suave",
                "Caminata de paseo conversacional (≤30 min)",
                "Acuéstate temprano para subir HRV de mañana",
            ],
            next_session=next_session,
        )

    # Caso 3: ACWR alto → recuperación activa (solo si el plan decía entrenar)
    if high_acwr and planned_status == "train":
        assert acwr is not None
        return TodayActionData(
            status="active_recovery",
            temporal="today",
            headline="RECUPERACIÓN ACTIVA HOY",
            short_reason=(
                f"Tu ACWR ({acwr:.2f}) está sobre el umbral seguro (1.3). "
                "Carga aguda muy por encima de la crónica."
            ),
            reasons=[
                f"ACWR {acwr:.2f} > 1.3 — riesgo de sobreuso elevado (Gabbett 2016)",
                f"Plan original de hoy: {planned_session}",
                "Recuperación activa baja ACWR a zona segura para retomar mañana",
            ],
            allowed=[
                "Movilidad 20-30 min",
                "Caminata muy ligera Z1 (≤30 min, sin contar como sesión)",
                "Estiramientos largos / foam roller",
            ],
            next_session=next_session,
        )

    # Caso 4: día de descanso programado
    if planned_status == "rest":
        extra: list[str] = []
        if acwr is not None and acwr > 1.0:
            extra.append(
                f"Tu ACWR es {acwr:.2f} — el descanso de hoy lo baja a zona óptima para mañana"
            )
        if reduced_hrv and hrv_today is not None and hrv_baseline is not None:
            extra.append(
                f"HRV {hrv_today:.0f} ms está {hrv_today - hrv_baseline:+.0f} vs baseline — descanso ayuda a normalizar"
            )
        if not extra:
            extra.append(
                "Tu plan polarizado contempla este descanso — sin descanso no hay adaptación"
            )
        return TodayActionData(
            status="rest",
            temporal="today",
            headline="DESCANSA HOY",
            short_reason="Día de descanso programado por el plan semanal.",
            reasons=extra,
            allowed=[
                "Movilidad / estiramientos",
                "Caminata de paseo conversacional (sin reloj)",
                "Foam roller, sauna, baño caliente",
            ],
            next_session=next_session,
        )

    # Caso 5: día normal de entrenamiento, sin alertas
    return TodayActionData(
        status="train",
        temporal="today",
        headline=f"ENTRENA HOY: {planned_session}",
        short_reason="Día de entrenamiento programado y sin contraindicaciones (ACWR y HRV en rango).",
        reasons=[
            f"Plan semanal de hoy: {planned_session}",
            f"ACWR {acwr:.2f}" if acwr else "ACWR sin datos",
            f"HRV {hrv_today:.0f} ms en rango" if hrv_today else "HRV de anoche sin registro",
        ],
        allowed=[
            "Calentamiento progresivo 8-10 min antes",
            "Cadencia objetivo ≥170 spm si toca trote",
            "Hidratación + 30g de carbohidratos pre-sesión si vas a Z3+",
        ],
        next_session=next_session,
    )
