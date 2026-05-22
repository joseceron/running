import type { HRV } from "@/lib/api";

const STATUS_LABEL: Record<HRV["status"], string> = {
  optimal: "Óptimo",
  reduced: "Reducido",
  suppressed: "Suprimido — descanso",
  building_baseline: "Construyendo baseline",
};

function Sparkline({ values }: { values: number[] }) {
  if (values.length < 2) return null;
  const w = 240;
  const h = 60;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const step = w / (values.length - 1);
  const points = values
    .map((v, i) => {
      const x = i * step;
      const y = h - ((v - min) / range) * h;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  return (
    <svg
      width={w}
      height={h}
      viewBox={`0 0 ${w} ${h}`}
      className="overflow-visible"
    >
      <polyline
        points={points}
        fill="none"
        stroke="var(--accent-deep)"
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {values.map((v, i) => {
        const x = i * step;
        const y = h - ((v - min) / range) * h;
        return (
          <circle
            key={i}
            cx={x}
            cy={y}
            r={i === values.length - 1 ? 4 : 2}
            fill="var(--accent-deep)"
          />
        );
      })}
    </svg>
  );
}

export function HRVCard({ hrv }: { hrv: HRV }) {
  // Sparkline va en orden cronológico (más antiguo a más reciente)
  const chronological = [...hrv.nights].reverse();
  const sparkValues = chronological.map((n) => n.hrv_rmssd);
  const progress = (hrv.days_recorded / hrv.days_required) * 100;

  return (
    <div className="rounded-2xl border border-rule bg-paper p-6 col-span-2">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-xs uppercase tracking-widest text-muted mb-2">
            HRV nocturno
          </p>
          <div className="flex items-baseline gap-3">
            <p className="metric text-6xl">{hrv.latest_value?.toFixed(0) ?? "—"}</p>
            <p className="text-sm text-muted">ms · última noche</p>
          </div>
        </div>
        <span className={`status-pill ${hrv.status}`}>
          {hrv.status === "optimal" && <span className="pulse-dot text-accent">●</span>}
          {STATUS_LABEL[hrv.status]}
        </span>
      </div>

      <div className="my-4">
        <Sparkline values={sparkValues} />
      </div>

      <div className="grid grid-cols-3 gap-4 text-sm pt-4 border-t border-rule/60">
        <div>
          <p className="text-xs text-muted">Baseline personal</p>
          <p className="tnum font-medium">
            {hrv.baseline_ms ? `${hrv.baseline_ms} ms` : "—"}
          </p>
        </div>
        <div>
          <p className="text-xs text-muted">Delta vs baseline</p>
          <p className="tnum font-medium">
            {hrv.latest_delta_pct !== null ? `${hrv.latest_delta_pct}%` : "—"}
          </p>
        </div>
        <div>
          <p className="text-xs text-muted">Días recolectados</p>
          <p className="tnum font-medium">
            {hrv.days_recorded} / {hrv.days_required}
          </p>
        </div>
      </div>

      {hrv.status === "building_baseline" && (
        <div className="mt-4">
          <div className="h-1.5 rounded-full bg-rule/50 overflow-hidden">
            <div
              className="h-full bg-accent-deep transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-muted mt-2">
            Faltan {hrv.days_required - hrv.days_recorded} noches para activar
            las recomendaciones de carga basadas en HRV.
          </p>
        </div>
      )}

      <details className="mt-4">
        <summary className="text-xs text-muted cursor-pointer hover:text-ink">
          Ver las {hrv.nights.length} noches registradas
        </summary>
        <ul className="mt-3 grid grid-cols-2 gap-2 text-sm">
          {hrv.nights.map((n) => (
            <li
              key={n.date}
              className="flex items-baseline justify-between tnum"
            >
              <span className="text-muted">{n.date}</span>
              <span className="font-medium">{n.hrv_rmssd} ms</span>
            </li>
          ))}
        </ul>
      </details>
    </div>
  );
}
