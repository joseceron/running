/**
 * ActivityHeader — 6 KPIs + Training Effect + ZoneBar + sub-métricas con glosario.
 */

import type { ActivityDetail } from "@/lib/api";
import { ZoneBar } from "./ZoneBar";
import { Term } from "./Term";

function fmtDuration(secs: number): string {
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  const s = secs % 60;
  if (h > 0)
    return `${h}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function fmtDateTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("es-CO", {
    weekday: "long",
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function ActivityHeader({ activity }: { activity: ActivityDetail }) {
  const kpis: Array<[string, string, React.ReactNode]> = [
    ["Distancia", `${activity.distance_km.toFixed(2)} km`, null],
    ["Tiempo", fmtDuration(activity.duration_secs), null],
    ["Ritmo medio", `${activity.avg_pace} /km`, <Term key="r" k="ritmo">Ritmo medio</Term>],
    ["FC media", `${activity.avg_hr} lpm`, null],
    ["Ascenso", `${activity.elevation_gain_m} m`, null],
    ["Calorías", `${activity.calories}`, null],
  ];

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-4 gap-4">
        <div>
          <p className="label-uppercase">
            🏃 Carrera · {activity.activity_id.slice(-6)}
          </p>
          <h1 className="text-2xl font-semibold text-ink-primary mt-1.5 leading-tight">
            {activity.name}
          </h1>
          <p className="text-xs text-ink-secondary mt-1 capitalize">
            {fmtDateTime(activity.started_at)}
          </p>
        </div>
        <div className="text-right shrink-0">
          <p className="label-uppercase">
            <Term k="training_effect">Training effect</Term>
          </p>
          <p className="metric-display text-3xl mt-1 text-ink-primary">
            {activity.training_effect_aerobic.toFixed(1)}
          </p>
          <p className="text-[11px] text-ink-tertiary">
            Base aeróbica · Mantenimiento
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 md:grid-cols-6 gap-4 pb-4 border-b border-rule/40">
        {kpis.map(([label, value, termNode]) => (
          <div key={label}>
            <p className="label-uppercase">{termNode ?? label}</p>
            <p className="metric-display text-xl mt-1 text-ink-primary">
              {value}
            </p>
          </div>
        ))}
      </div>

      <div className="mt-4">
        <p className="label-uppercase mb-2">Distribución por zonas de FC</p>
        <ZoneBar
          values={activity.zone_distribution_pct as [number, number, number, number, number]}
        />
      </div>

      <div className="mt-4 grid md:grid-cols-3 gap-3 text-xs">
        <Stat
          label={<Term k="cadencia">Cadencia media</Term>}
          value={`${activity.avg_cadence} `}
          unit={<Term k="spm">spm</Term>}
        />
        <Stat
          label={<Term k="zancada">Longitud zancada</Term>}
          value={`${activity.avg_stride_m.toFixed(2)} m`}
        />
        <Stat
          label={<Term k="gct">GCT medio</Term>}
          value={`${activity.avg_gct_ms} ms`}
        />
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  unit,
}: {
  label: React.ReactNode;
  value: string;
  unit?: React.ReactNode;
}) {
  return (
    <div
      className="rounded-md px-3 py-2"
      style={{ background: "var(--bg-card-subtle)" }}
    >
      <p className="text-[10px] text-ink-tertiary uppercase tracking-wider">
        {label}
      </p>
      <p className="tnum font-semibold text-ink-primary mt-0.5">
        {value}
        {unit && <span className="ml-1 text-ink-tertiary font-normal">{unit}</span>}
      </p>
    </div>
  );
}
