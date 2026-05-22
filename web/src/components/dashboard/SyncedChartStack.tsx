/**
 * SyncedChartStack — stack vertical de gráficos sincronizados.
 * Formato corregido: ritmo siempre como mm:ss, "prom/mín/máx" en español.
 */

"use client";

import { useRef, useState } from "react";
import type { ActivitySample } from "@/lib/api";
import { Term } from "./Term";

const W = 760;
const PLOT_H = 110;
const PAD = { l: 56, r: 16, t: 10, b: 22 };

type Series = {
  key: "hr" | "pace" | "elevation" | "cadence" | "power";
  label: string;
  termKey?: "ritmo" | "cadencia" | "ppm";
  unit: string;
  color: string;
  fillColor: string;
  format: (v: number) => string;
  invert?: boolean;
  scatter?: boolean;
};

const fmtNum = (v: number) => String(Math.round(v));
const fmtFloat1 = (v: number) => v.toFixed(1);
const fmtPace = (v: number) => {
  const s = Math.max(0, Math.round(v));
  return `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, "0")}`;
};

const SERIES: Series[] = [
  {
    key: "elevation",
    label: "Altura",
    unit: "m",
    color: "var(--chart-altitude-line)",
    fillColor: "var(--chart-altitude-fill)",
    format: fmtNum,
  },
  {
    key: "pace",
    label: "Ritmo",
    termKey: "ritmo",
    unit: "min/km",
    color: "var(--chart-pace-line)",
    fillColor: "var(--chart-pace-fill)",
    invert: true,
    format: fmtPace,
  },
  {
    key: "hr",
    label: "Frecuencia cardíaca",
    termKey: "ppm",
    unit: "ppm",
    color: "var(--chart-hr-line)",
    fillColor: "var(--chart-hr-fill)",
    format: fmtNum,
  },
  {
    key: "cadence",
    label: "Cadencia",
    termKey: "cadencia",
    unit: "spm",
    color: "var(--chart-cadence-mid)",
    fillColor: "transparent",
    format: fmtNum,
    scatter: true,
  },
  {
    key: "power",
    label: "Potencia",
    unit: "W",
    color: "var(--chart-power-line)",
    fillColor: "var(--chart-power-fill)",
    format: fmtNum,
  },
];

function getValue(sample: ActivitySample, key: Series["key"]): number | null {
  if (key === "elevation") return sample.elevation_m;
  if (key === "hr") return sample.hr;
  if (key === "cadence") return sample.cadence;
  if (key === "power") return sample.power_w;
  if (key === "pace") return sample.pace_secs_per_km;
  return null;
}

function fmtTime(t: number): string {
  const m = Math.floor(t / 60);
  const s = t % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function ChartOne({
  series,
  samples,
  totalSecs,
  hoverT,
  setHoverT,
}: {
  series: Series;
  samples: ActivitySample[];
  totalSecs: number;
  hoverT: number | null;
  setHoverT: (t: number | null) => void;
}) {
  const validSamples = samples.filter((s) => getValue(s, series.key) !== null);
  if (validSamples.length < 2) return null;

  const values = validSamples.map((s) => getValue(s, series.key)!);

  // Filtrar outliers extremos de ritmo (ej: caminata muy lenta)
  const sorted = [...values].sort((a, b) => a - b);
  const p5 = sorted[Math.floor(sorted.length * 0.05)];
  const p95 = sorted[Math.floor(sorted.length * 0.95)];
  let min = series.key === "pace" ? p5 : Math.min(...values);
  let max = series.key === "pace" ? p95 : Math.max(...values);

  const realMin = Math.min(...values);
  const realMax = Math.max(...values);
  const padR = (max - min) * 0.12 || 1;
  min = Math.max(0, min - padR);
  max += padR;
  const avg = values.reduce((acc, v) => acc + v, 0) / values.length;

  const x = (t: number) => PAD.l + (t / totalSecs) * (W - PAD.l - PAD.r);
  const y = (v: number) => {
    const clamped = Math.max(min, Math.min(max, v));
    const norm = (clamped - min) / (max - min);
    return series.invert
      ? PAD.t + norm * PLOT_H
      : PAD.t + (1 - norm) * PLOT_H;
  };

  const pts = validSamples
    .map((s) => `${x(s.t_secs).toFixed(1)},${y(getValue(s, series.key)!).toFixed(1)}`)
    .join(" ");

  const baselineY = PAD.t + PLOT_H;
  const areaPath = `M ${x(validSamples[0].t_secs).toFixed(1)},${baselineY} L ${pts.split(" ").join(" L ")} L ${x(validSamples[validSamples.length - 1].t_secs).toFixed(1)},${baselineY} Z`;

  const totalH = PLOT_H + PAD.t + PAD.b;
  const hoverSample =
    hoverT !== null
      ? validSamples.reduce((prev, curr) =>
          Math.abs(curr.t_secs - hoverT) < Math.abs(prev.t_secs - hoverT)
            ? curr
            : prev
        )
      : null;

  return (
    <div>
      <div className="flex items-baseline justify-between text-xs px-1 mb-1.5 gap-2">
        <div className="flex items-center gap-2">
          <span
            className="w-2.5 h-2.5 rounded-full shrink-0"
            style={{ background: series.color }}
          />
          <span className="font-semibold text-ink-primary">
            {series.termKey ? (
              <Term k={series.termKey}>{series.label}</Term>
            ) : (
              series.label
            )}
          </span>
          <span className="text-ink-tertiary text-[10px]">{series.unit}</span>
        </div>
        <div className="flex items-center gap-3 text-[10px] text-ink-tertiary tnum">
          <span>
            mín{" "}
            <span className="text-ink-secondary font-medium">
              {series.format(realMin)}
            </span>
          </span>
          <span>
            prom{" "}
            <span className="font-semibold" style={{ color: series.color }}>
              {series.format(avg)}
            </span>
          </span>
          <span>
            máx{" "}
            <span className="text-ink-secondary font-medium">
              {series.format(realMax)}
            </span>
          </span>
          {hoverSample && (
            <span className="ml-2 pl-2 border-l border-rule/60">
              ahora{" "}
              <span className="font-bold" style={{ color: series.color }}>
                {series.format(getValue(hoverSample, series.key)!)}
              </span>
            </span>
          )}
        </div>
      </div>

      <svg
        viewBox={`0 0 ${W} ${totalH}`}
        className="w-full h-auto block"
        style={{ cursor: "crosshair" }}
        onMouseMove={(e) => {
          const svg = e.currentTarget;
          const rect = svg.getBoundingClientRect();
          const mx = ((e.clientX - rect.left) / rect.width) * W;
          if (mx >= PAD.l && mx <= W - PAD.r) {
            const t = ((mx - PAD.l) / (W - PAD.l - PAD.r)) * totalSecs;
            setHoverT(t);
          }
        }}
        onMouseLeave={() => setHoverT(null)}
      >
        {/* Etiquetas eje Y */}
        {[
          { v: max, label: series.format(max) },
          { v: avg, label: `prom ${series.format(avg)}` },
          { v: min, label: series.format(min) },
        ].map((item, i) => (
          <text
            key={i}
            x={PAD.l - 6}
            y={y(item.v) + 3}
            textAnchor="end"
            fontSize={9}
            fill={i === 1 ? series.color : "var(--ink-tertiary)"}
            fontFamily="Inter"
            fontWeight={i === 1 ? 600 : 400}
            style={{ fontVariantNumeric: "tabular-nums" }}
          >
            {item.label}
          </text>
        ))}

        <line
          x1={PAD.l}
          y1={y(avg)}
          x2={W - PAD.r}
          y2={y(avg)}
          stroke={series.color}
          strokeDasharray="3 3"
          strokeWidth={1}
          opacity={0.4}
        />

        {series.scatter ? (
          validSamples.map((s, i) => {
            const v = getValue(s, series.key)!;
            const c =
              v >= 160
                ? "var(--chart-cadence-good)"
                : v >= 130
                  ? "var(--chart-cadence-mid)"
                  : "var(--chart-cadence-low)";
            return (
              <circle key={i} cx={x(s.t_secs)} cy={y(v)} r={2} fill={c} />
            );
          })
        ) : (
          <>
            <path d={areaPath} fill={series.fillColor} fillOpacity={0.7} />
            <polyline
              points={pts}
              fill="none"
              stroke={series.color}
              strokeWidth={1.8}
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          </>
        )}

        {hoverT !== null && (
          <>
            <line
              x1={x(hoverT)}
              y1={PAD.t}
              x2={x(hoverT)}
              y2={PAD.t + PLOT_H}
              stroke="var(--accent-brand)"
              strokeWidth={1.4}
              strokeDasharray="3 3"
              opacity={0.7}
            />
            {hoverSample && (
              <circle
                cx={x(hoverSample.t_secs)}
                cy={y(getValue(hoverSample, series.key)!)}
                r={4}
                fill="var(--bg-card)"
                stroke={series.color}
                strokeWidth={2}
              />
            )}
          </>
        )}
      </svg>
    </div>
  );
}

export function SyncedChartStack({ samples }: { samples: ActivitySample[] }) {
  const [hoverT, setHoverT] = useState<number | null>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const totalSecs = samples[samples.length - 1]?.t_secs ?? 1;

  const hoverSample =
    hoverT !== null
      ? samples.reduce((prev, curr) =>
          Math.abs(curr.t_secs - hoverT) < Math.abs(prev.t_secs - hoverT)
            ? curr
            : prev
        )
      : null;

  return (
    <div className="card relative" ref={wrapperRef}>
      <div className="flex items-baseline justify-between mb-4">
        <div>
          <span className="label-uppercase">Gráficas sincronizadas</span>
          <p className="text-[11px] text-ink-tertiary mt-1">
            Pasa el cursor sobre cualquier gráfico — el crosshair y los valores
            se sincronizan en todos
          </p>
        </div>
        {hoverSample && (
          <div className="text-right">
            <p className="label-uppercase" style={{ fontSize: 9 }}>
              Tiempo · distancia
            </p>
            <p
              className="text-sm font-bold text-accent-brand mt-0.5"
              style={{ fontVariantNumeric: "tabular-nums" }}
            >
              {fmtTime(hoverSample.t_secs)} ·{" "}
              {hoverSample.distance_km.toFixed(2)} km
            </p>
          </div>
        )}
      </div>

      <div className="space-y-3">
        {SERIES.map((s) => (
          <ChartOne
            key={s.key}
            series={s}
            samples={samples}
            totalSecs={totalSecs}
            hoverT={hoverT}
            setHoverT={setHoverT}
          />
        ))}
      </div>
    </div>
  );
}
