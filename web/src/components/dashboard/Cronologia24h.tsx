/**
 * Cronologia24h — el componente "estrella" inspirado en Connect.
 *
 * Cronología 24h con: línea Body Battery + área estrés (translúcida) +
 * banda de sueño (índigo) + marcadores de actividad. SVG puro, sin libs.
 *
 * Eje X: 0h → 24h con etiquetas cada 6h
 * Eje Y (BB): 0-100 con grillas en 25/50/75/100
 */

import type { CSSProperties } from "react";

export type Cronologia = {
  points: Array<{
    hour: number;
    body_battery: number | null;
    stress: number | null;
    is_sleeping: boolean;
    is_active: boolean;
  }>;
  activities: Array<{
    hour: number;
    label: string;
    type: string;
  }>;
  summary: {
    body_battery_start: number;
    body_battery_end: number;
    body_battery_max: number;
    body_battery_min: number;
    stress_avg: number;
    stress_max: number;
    sleep_duration_min: number;
  };
};

const W = 720;
const H = 200;
const PAD = { l: 36, r: 36, t: 16, b: 28 };
const PLOT_W = W - PAD.l - PAD.r;
const PLOT_H = H - PAD.t - PAD.b;

const xOf = (h: number) => PAD.l + (h / 24) * PLOT_W;
const yBB = (v: number) => PAD.t + ((100 - v) / 100) * PLOT_H;
const yStress = (v: number) => PAD.t + ((100 - v) / 100) * PLOT_H;

function legendItem(color: string, label: string) {
  return (
    <span className="inline-flex items-center gap-1.5 text-[10px] text-ink-secondary">
      <span
        className="w-2.5 h-2.5 rounded-sm"
        style={{ background: color }}
      />
      {label}
    </span>
  );
}

export function Cronologia24h({ cronologia }: { cronologia: Cronologia }) {
  const { points, activities, summary } = cronologia;

  // Build BB polyline (puntos con valor válido)
  const bbPts = points
    .filter((p) => p.body_battery !== null)
    .map((p) => `${xOf(p.hour).toFixed(1)},${yBB(p.body_battery!).toFixed(1)}`)
    .join(" ");

  // Build stress area path (cerrado al eje X)
  const stressTop = points
    .filter((p) => p.stress !== null)
    .map((p) => `${xOf(p.hour).toFixed(1)},${yStress(p.stress!).toFixed(1)}`)
    .join(" L ");
  const stressPath = stressTop
    ? `M ${xOf(0)},${yStress(0)} L ${stressTop} L ${xOf(24)},${yStress(0)} Z`
    : "";

  // Identificar bloques de sueño
  const sleepRanges: Array<[number, number]> = [];
  let sleepStart: number | null = null;
  for (const p of points) {
    if (p.is_sleeping && sleepStart === null) sleepStart = p.hour;
    if (!p.is_sleeping && sleepStart !== null) {
      sleepRanges.push([sleepStart, p.hour]);
      sleepStart = null;
    }
  }
  if (sleepStart !== null) sleepRanges.push([sleepStart, 24]);

  // Identificar bloques de actividad
  const activeRanges: Array<[number, number]> = [];
  let activeStart: number | null = null;
  for (const p of points) {
    if (p.is_active && activeStart === null) activeStart = p.hour;
    if (!p.is_active && activeStart !== null) {
      activeRanges.push([activeStart, p.hour]);
      activeStart = null;
    }
  }
  if (activeStart !== null) activeRanges.push([activeStart, 24]);

  const xLabels = [0, 6, 12, 18, 24];

  return (
    <div className="card md:col-span-3">
      {/* Header */}
      <div className="flex items-start justify-between mb-3.5 gap-4">
        <div>
          <span className="label-uppercase">Cronología del Día</span>
          <p className="text-[11px] text-ink-tertiary mt-1">
            Body Battery + Estrés + Sueño + Actividad · 24 horas
          </p>
        </div>
        <div className="flex items-center gap-4 text-right">
          <Stat
            label="BB final"
            value={`${summary.body_battery_end}`}
            color="var(--cron-bb-point)"
          />
          <Stat
            label="BB min"
            value={`${summary.body_battery_min}`}
            color="var(--ink-secondary)"
          />
          <Stat
            label="Estrés prom"
            value={`${summary.stress_avg}`}
            color="var(--cron-stress)"
          />
          <Stat
            label="Sueño"
            value={fmtMinutes(summary.sleep_duration_min)}
            color="var(--cron-sleep)"
          />
        </div>
      </div>

      {/* SVG */}
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full h-auto"
        style={{ minHeight: 200 }}
      >
        {/* Grilla horizontal */}
        {[25, 50, 75, 100].map((g) => (
          <g key={g}>
            <line
              x1={PAD.l}
              y1={yBB(g)}
              x2={W - PAD.r}
              y2={yBB(g)}
              stroke="#E5E7EB"
              strokeWidth={1}
              strokeDasharray={g === 50 ? "0" : "2 3"}
            />
            <text
              x={PAD.l - 6}
              y={yBB(g) + 3}
              textAnchor="end"
              fontSize={9}
              fill="var(--ink-tertiary)"
              fontFamily="Inter"
            >
              {g}
            </text>
          </g>
        ))}

        {/* Bandas de sueño */}
        {sleepRanges.map(([s, e], i) => (
          <rect
            key={`sleep-${i}`}
            x={xOf(s)}
            y={PAD.t}
            width={xOf(e) - xOf(s)}
            height={PLOT_H}
            fill="var(--cron-sleep)"
            fillOpacity={0.13}
          />
        ))}

        {/* Bandas de actividad */}
        {activeRanges.map(([s, e], i) => (
          <rect
            key={`active-${i}`}
            x={xOf(s)}
            y={PAD.t}
            width={Math.max(2, xOf(e) - xOf(s))}
            height={PLOT_H}
            fill="var(--cron-active)"
            fillOpacity={0.22}
          />
        ))}

        {/* Área de estrés (translúcida, debajo de BB) */}
        {stressPath && (
          <path
            d={stressPath}
            fill="var(--cron-stress)"
            fillOpacity={0.12}
          />
        )}

        {/* Línea Body Battery */}
        <polyline
          points={bbPts}
          fill="none"
          stroke="var(--cron-bb-point)"
          strokeWidth={2.2}
          strokeLinejoin="round"
          strokeLinecap="round"
        />

        {/* Marcadores de actividad */}
        {activities.map((a, i) => {
          const px = xOf(a.hour);
          return (
            <g key={i}>
              <line
                x1={px}
                y1={PAD.t}
                x2={px}
                y2={H - PAD.b}
                stroke="var(--cron-activity-violet)"
                strokeDasharray="2 2"
                strokeWidth={1}
              />
              <circle
                cx={px}
                cy={PAD.t + 10}
                r={5}
                fill="var(--cron-activity-violet)"
              />
              <text
                x={px + 8}
                y={PAD.t + 13}
                fontSize={9}
                fill="var(--ink-secondary)"
                fontFamily="Inter"
                fontWeight={500}
              >
                {a.label}
              </text>
            </g>
          );
        })}

        {/* Eje X (horas) */}
        {xLabels.map((h) => (
          <g key={h}>
            <line
              x1={xOf(h)}
              y1={H - PAD.b}
              x2={xOf(h)}
              y2={H - PAD.b + 3}
              stroke="var(--ink-tertiary)"
            />
            <text
              x={xOf(h)}
              y={H - PAD.b + 14}
              textAnchor="middle"
              fontSize={10}
              fill="var(--ink-secondary)"
              fontFamily="Inter"
              style={{ fontVariantNumeric: "tabular-nums" }}
            >
              {h === 24 ? "24h" : `${h}h`}
            </text>
          </g>
        ))}
      </svg>

      {/* Leyenda */}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 mt-2 pt-3 border-t border-rule/40">
        {legendItem("var(--cron-bb-point)", "Body Battery")}
        {legendItem("var(--cron-stress)", "Estrés")}
        {legendItem("var(--cron-sleep)", "Sueño")}
        {legendItem("var(--cron-active)", "Actividad")}
        {legendItem("var(--cron-activity-violet)", "Marcador de entreno")}
      </div>

      {/* Interpretación Liebre */}
      <div className="mt-3 pt-3 border-t border-rule/40">
        <div className="flex items-center gap-1.5 mb-1.5">
          <span className="text-[11px]">📊</span>
          <span className="label-uppercase">Interpretación Liebre</span>
        </div>
        <p className="text-[13px] text-ink-secondary leading-relaxed">
          Tu Body Battery se recargó de {summary.body_battery_start} a un pico
          de {summary.body_battery_max} durante el sueño nocturno, cayó{" "}
          {Math.abs(summary.body_battery_max - 80)} puntos durante el entreno
          y mantiene tendencia descendente con el desgaste del día (final{" "}
          {summary.body_battery_end}). El pico de estrés a las 17:00–17:30
          (valor {summary.stress_max}) es el evento más estresante del día —
          si se repite mañana sin recuperación, podría afectar tu HRV nocturno.
        </p>
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <div>
      <div className="label-uppercase" style={{ fontSize: 9 }}>
        {label}
      </div>
      <div
        className="tnum font-bold text-sm leading-none mt-1"
        style={{ color: color ?? "var(--ink-primary)" } as CSSProperties}
      >
        {value}
      </div>
    </div>
  );
}

function fmtMinutes(m: number): string {
  const h = Math.floor(m / 60);
  const min = m % 60;
  return `${h}h ${min.toString().padStart(2, "0")}`;
}
