/**
 * UpcomingTrainingsCard — los próximos entrenos planificados, con tipo,
 * duración, zona objetivo, distancia y rationale del porqué (capa Liebre).
 *
 * Cada sesión muestra un dot del color de la zona objetivo.
 */

import type { UpcomingTraining, UpcomingTrainings } from "@/lib/api";

const ZONE_COLOR: Record<UpcomingTraining["zone_target"], string> = {
  Z1: "var(--zone-1)",
  Z2: "var(--zone-2)",
  Z3: "var(--zone-3)",
  Z4: "var(--zone-4)",
  Z5: "var(--zone-5)",
  "—": "var(--ink-tertiary)",
};

const TYPE_ICON: Record<UpcomingTraining["type"], string> = {
  "Rodaje Z2": "🏃",
  "Rodaje largo Z2": "🏃",
  "Tempo Z3": "⚡",
  "Series Z4": "⚡",
  Fuerza: "💪",
  Movilidad: "🧘",
  Descanso: "🌙",
};

export function UpcomingTrainingsCard({
  upcoming,
}: {
  upcoming: UpcomingTrainings;
}) {
  return (
    <div className="card md:col-span-2">
      <div className="mb-3.5">
        <span className="label-uppercase">Próximos Entrenos</span>
        <p className="text-[11px] text-ink-tertiary mt-1">
          Plan adaptado a tu HRV actual — Liebre genera cada sesión con su razón.
        </p>
      </div>

      <ul className="flex flex-col gap-2">
        {upcoming.sessions.map((s) => (
          <li
            key={s.relative_days}
            className="rounded-md"
            style={{
              background: "var(--bg-card-subtle)",
              padding: "12px 14px",
              borderLeft: `3px solid ${ZONE_COLOR[s.zone_target]}`,
            }}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-base leading-none">
                    {TYPE_ICON[s.type]}
                  </span>
                  <span className="text-[13px] font-semibold text-ink-primary">
                    {s.type}
                  </span>
                  {s.zone_target !== "—" && (
                    <span
                      className="text-[10px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wide"
                      style={{
                        background: ZONE_COLOR[s.zone_target] + "22",
                        color: ZONE_COLOR[s.zone_target],
                      }}
                    >
                      {s.zone_target}
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-ink-tertiary mt-1 capitalize">
                  {s.day_label} ·{" "}
                  <span className="tnum">{s.duration_min} min</span>
                  {s.distance_km && (
                    <>
                      {" · "}
                      <span className="tnum">{s.distance_km} km</span>
                    </>
                  )}
                </p>
                <p className="text-xs text-ink-secondary mt-1.5 leading-relaxed">
                  {s.rationale}
                </p>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
