/**
 * ActivityHeader — barra de KPIs principales de una actividad.
 * Replica el patrón Connect: 5-6 KPIs grandes en fila con separadores.
 */

import type { ActivityDetail } from "@/lib/api";
import { ZoneBar } from "./ZoneBar";

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
  const kpis: Array<[string, string]> = [
    ["Distancia", `${activity.distance_km.toFixed(2)} km`],
    ["Tiempo", fmtDuration(activity.duration_secs)],
    ["Ritmo medio", `${activity.avg_pace} /km`],
    ["FC media", `${activity.avg_hr} lpm`],
    ["Ascenso", `${activity.elevation_gain_m} m`],
    ["Calorías", `${activity.calories}`],
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
          <p className="label-uppercase">Training effect</p>
          <p className="metric-display text-3xl mt-1 text-ink-primary">
            {activity.training_effect_aerobic.toFixed(1)}
          </p>
          <p className="text-[11px] text-ink-tertiary">
            Base aeróbica · Mantenimiento
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 md:grid-cols-6 gap-4 pb-4 border-b border-rule/40">
        {kpis.map(([label, value]) => (
          <div key={label}>
            <p className="label-uppercase">{label}</p>
            <p className="metric-display text-xl mt-1 text-ink-primary">
              {value}
            </p>
          </div>
        ))}
      </div>

      <div className="mt-4">
        <p className="label-uppercase mb-2">Distribución por zonas FC</p>
        <ZoneBar
          values={activity.zone_distribution_pct as [number, number, number, number, number]}
        />
      </div>

      <div className="mt-4 grid md:grid-cols-3 gap-3 text-xs">
        <Stat label="Cadencia media" value={`${activity.avg_cadence} spm`} />
        <Stat label="Longitud zancada" value={`${activity.avg_stride_m.toFixed(2)} m`} />
        <Stat label="GCT medio" value={`${activity.avg_gct_ms} ms`} />
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div
      className="rounded-md px-3 py-2"
      style={{ background: "var(--bg-card-subtle)" }}
    >
      <p className="text-[10px] text-ink-tertiary uppercase tracking-wider">
        {label}
      </p>
      <p className="tnum font-semibold text-ink-primary mt-0.5">{value}</p>
    </div>
  );
}
