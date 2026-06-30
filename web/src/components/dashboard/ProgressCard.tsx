"use client";

/**
 * ProgressCard — curva de adaptación a lo largo de semanas.
 * Muestra 3 sparklines: HRV (noches), volumen semanal, y composición corporal.
 * Botón "Registrar báscula" abre el modal de captura.
 */

import { useState } from "react";
import type { Progress } from "@/lib/api";
import { BodyLogModal } from "./BodyLogModal";

type Props = {
  progress: Progress;
};

/* ── Sparkline SVG genérico ──────────────────────────────────────────────── */

function Sparkline({
  values,
  color,
  height = 40,
  showDots = false,
}: {
  values: number[];
  color: string;
  height?: number;
  showDots?: boolean;
}) {
  if (values.length < 2) {
    return (
      <svg
        width="100%"
        height={height}
        viewBox={`0 0 220 ${height}`}
        className="block max-w-full"
      >
        <circle cx={110} cy={height / 2} r={3} fill={color} opacity={0.7} />
      </svg>
    );
  }

  const w = 220;
  const pad = 4;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  const pts = values.map((v, i) => {
    const x = pad + (i / (values.length - 1)) * (w - pad * 2);
    const y = pad + (1 - (v - min) / range) * (height - pad * 2);
    return { x, y, v };
  });

  const d = pts
    .map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(1)},${p.y.toFixed(1)}`)
    .join(" ");

  return (
    <svg
      width="100%"
      height={height}
      viewBox={`0 0 ${w} ${height}`}
      className="block max-w-full"
    >
      <path d={d} fill="none" stroke={color} strokeWidth={1.5} strokeLinejoin="round" strokeLinecap="round" />
      {showDots &&
        pts.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r={2.5} fill={color} opacity={0.7}>
            <title>{p.v.toFixed(1)}</title>
          </circle>
        ))}
    </svg>
  );
}

/* ── Tarjeta de métrica individual ──────────────────────────────────────── */

function MetricSparkCard({
  label,
  unit,
  values,
  color,
  latest,
  latestLabel,
}: {
  label: string;
  unit: string;
  values: number[];
  color: string;
  latest: number | null;
  latestLabel?: string;
}) {
  const trendVal = values.length >= 4
    ? values[values.length - 1] - values[0]
    : null;

  const trendSign = trendVal === null ? null : trendVal > 0 ? "+" : "";
  const trendColor =
    trendVal === null
      ? "var(--ink-tertiary)"
      : trendVal > 0
      ? "var(--hrv-balanced)"
      : "var(--semantic-warning)";

  return (
    <div className="card p-3 flex flex-col gap-1.5">
      <div className="flex items-baseline justify-between">
        <span className="text-[11px] text-ink-tertiary uppercase tracking-wider">{label}</span>
        {trendVal !== null && (
          <span className="text-[11px] font-semibold" style={{ color: trendColor }}>
            {trendSign}{trendVal.toFixed(1)} {unit}
          </span>
        )}
      </div>
      <div className="flex items-end gap-3">
        <div>
          <p className="text-xl font-bold tnum text-ink-primary">
            {latest !== null ? `${latest.toFixed(1)}` : "—"}
          </p>
          <p className="text-[10px] text-ink-tertiary">{latestLabel ?? unit}</p>
        </div>
        <div className="flex-1 min-w-0 overflow-hidden">
          <Sparkline values={values} color={color} height={36} showDots={values.length <= 10} />
        </div>
      </div>
    </div>
  );
}

/* ── Main component ──────────────────────────────────────────────────────── */

export function ProgressCard({ progress }: Props) {
  const [showModal, setShowModal] = useState(false);

  const hrvValues = [...progress.hrv_nights].reverse().map((n) => n.hrv_ms);
  const kmValues = [...progress.weekly]
    .reverse()
    .map((w) => w.executed_km)
    .filter((v): v is number => v !== null);
  const fatValues = [...progress.body]
    .reverse()
    .map((b) => b.body_fat_pct)
    .filter((v): v is number => v !== null);
  const muscleValues = [...progress.body]
    .reverse()
    .map((b) => b.muscle_mass_kg)
    .filter((v): v is number => v !== null);

  const latestHrv = hrvValues.at(-1) ?? null;
  const latestKm = kmValues.at(-1) ?? null;
  const latestFat = fatValues.at(-1) ?? null;
  const latestMuscle = muscleValues.at(-1) ?? null;

  return (
    <>
      <div className="card md:col-span-3">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[13px]">📈</span>
              <span className="label-uppercase">Curva de Adaptación</span>
            </div>
            <p className="text-[11px] text-ink-tertiary mt-1">
              {progress.hrv_nights.length} noches · {progress.weekly.length} semanas
              {progress.body.length > 0 && ` · ${progress.body.length} mediciones báscula`}
            </p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="text-[11px] px-3 py-1.5 rounded-full font-medium transition-colors"
            style={{
              background: "color-mix(in srgb, var(--accent-brand) 12%, transparent)",
              color: "var(--accent-brand)",
              border: "1px solid color-mix(in srgb, var(--accent-brand) 30%, transparent)",
            }}
          >
            + Registrar báscula
          </button>
        </div>

        {/* Narrativa de adaptación */}
        {progress.summary.narrative && (
          <div
            className="text-[12px] text-ink-secondary leading-relaxed mb-4 px-3 py-2.5 rounded-lg"
            style={{ background: "color-mix(in srgb, var(--accent-brand) 6%, transparent)" }}
          >
            {progress.summary.narrative}
          </div>
        )}

        {/* Sparklines en grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {hrvValues.length >= 2 && (
            <MetricSparkCard
              label="VFC nocturna"
              unit="ms"
              values={hrvValues}
              color="var(--hrv-balanced)"
              latest={latestHrv}
              latestLabel="última noche"
            />
          )}
          {kmValues.length >= 2 && (
            <MetricSparkCard
              label="Volumen semanal"
              unit="km"
              values={kmValues}
              color="var(--accent-brand)"
              latest={latestKm}
              latestLabel="última semana"
            />
          )}
          {latestFat !== null ? (
            <MetricSparkCard
              label="Grasa corporal"
              unit="%"
              values={fatValues}
              color="var(--semantic-warning)"
              latest={latestFat}
              latestLabel={fatValues.length >= 2 ? "última medición" : "punto inicial"}
            />
          ) : (
            <div className="card p-3 flex flex-col gap-1.5 opacity-50 border-dashed">
              <span className="text-[11px] text-ink-tertiary uppercase tracking-wider">Grasa corporal</span>
              <p className="text-[11px] text-ink-tertiary mt-1">Registra tu báscula para ver la curva</p>
            </div>
          )}
          {latestMuscle !== null ? (
            <MetricSparkCard
              label="Masa muscular"
              unit="kg"
              values={muscleValues}
              color="#22d3ee"
              latest={latestMuscle}
              latestLabel={muscleValues.length >= 2 ? "última medición" : "punto inicial"}
            />
          ) : (
            <div className="card p-3 flex flex-col gap-1.5 opacity-50 border-dashed">
              <span className="text-[11px] text-ink-tertiary uppercase tracking-wider">Masa muscular</span>
              <p className="text-[11px] text-ink-tertiary mt-1">Registra tu báscula para ver la curva</p>
            </div>
          )}
        </div>
      </div>

      {showModal && <BodyLogModal onClose={() => setShowModal(false)} />}
    </>
  );
}
