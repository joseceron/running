/**
 * HRVCard — versión final alineada con mockup de Claude Design.
 *
 * Layout: header con label + status pill → row de gauge (136px) + grid 2x2 de
 * stats + sparkline → progress bar baseline → bloque Interpretación Liebre.
 */

import { GaugeCircular270 } from "./GaugeCircular270";
import { CiteBadge } from "./CiteBadge";
import type { HRV } from "@/lib/api";

const STATUS_LABEL: Record<HRV["status"], string> = {
  optimal: "Equilibrado",
  reduced: "Reducido",
  suppressed: "Suprimido",
  building_baseline: "Construyendo baseline",
};

const STATUS_CLASS: Record<HRV["status"], string> = {
  optimal: "balanced",
  reduced: "low",
  suppressed: "unbalanced",
  building_baseline: "building",
};

const STATUS_COLOR: Record<HRV["status"], string> = {
  optimal: "var(--hrv-balanced)",
  reduced: "var(--hrv-low)",
  suppressed: "var(--hrv-unbalanced)",
  building_baseline: "var(--accent-brand)",
};

function Sparkline({
  nights,
  baseline,
  color,
}: {
  nights: HRV["nights"];
  baseline: number | null;
  color: string;
}) {
  if (nights.length < 2) return null;
  const chronological = [...nights].reverse();
  const values = chronological.map((n) => n.hrv_rmssd);
  const W = 260;
  const H = 56;
  const pad = { l: 4, r: 4, t: 6, b: 6 };
  const refMin = baseline ? baseline * 0.94 : null;
  const refMax = baseline ? baseline * 1.06 : null;
  const min = Math.min(...values, refMin ?? Infinity) - 1;
  const max = Math.max(...values, refMax ?? -Infinity) + 1;
  const range = max - min || 1;

  const x = (i: number) =>
    pad.l + (i * (W - pad.l - pad.r)) / (values.length - 1);
  const y = (v: number) =>
    H - pad.b - ((v - min) / range) * (H - pad.t - pad.b);

  const points = values.map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");

  return (
    <svg
      width="100%"
      height={H}
      viewBox={`0 0 ${W} ${H}`}
      preserveAspectRatio="none"
      className="block"
    >
      {refMin !== null && refMax !== null && (
        <rect
          x={pad.l}
          y={y(refMax)}
          width={W - pad.l - pad.r}
          height={Math.abs(y(refMin) - y(refMax))}
          fill={color}
          fillOpacity={0.07}
        />
      )}
      {baseline !== null && (
        <line
          x1={pad.l}
          y1={y(baseline)}
          x2={W - pad.r}
          y2={y(baseline)}
          stroke="var(--ink-tertiary)"
          strokeWidth={1}
          strokeDasharray="3 3"
        />
      )}
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth={2}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      {values.map((v, i) => (
        <circle
          key={i}
          cx={x(i)}
          cy={y(v)}
          r={i === values.length - 1 ? 3.5 : 2.5}
          fill={color}
        />
      ))}
    </svg>
  );
}

function StatBlock({
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
      <div className="label-uppercase mb-0.5">{label}</div>
      <div
        className="text-base font-semibold tnum"
        style={{ color: color ?? "var(--ink-primary)" }}
      >
        {value}
      </div>
    </div>
  );
}

export function HRVCard({ hrv }: { hrv: HRV }) {
  const color = STATUS_COLOR[hrv.status];
  const deltaStr =
    hrv.latest_delta_pct !== null
      ? `${hrv.latest_delta_pct > 0 ? "+" : ""}${hrv.latest_delta_pct}%`
      : "—";
  const deltaColor =
    hrv.latest_delta_pct !== null
      ? hrv.latest_delta_pct >= -3
        ? "var(--impact-positive)"
        : "var(--semantic-warning)"
      : undefined;
  const progress = (hrv.days_recorded / hrv.days_required) * 100;

  return (
    <div className="card md:col-span-2">
      {/* Header */}
      <div className="flex items-start justify-between mb-3.5">
        <div>
          <div className="flex items-center gap-1.5">
            <span className="text-[11px]">🔵</span>
            <span className="label-uppercase">VFC Nocturna</span>
          </div>
          <p className="text-[11px] text-ink-tertiary mt-1">
            Media últimos {hrv.days_recorded} días
          </p>
        </div>
        <span className={`status-pill ${STATUS_CLASS[hrv.status]}`}>
          {STATUS_LABEL[hrv.status]}
        </span>
      </div>

      {/* Gauge + stats grid + sparkline */}
      <div className="flex gap-5 items-start">
        <GaugeCircular270
          value={hrv.latest_value ?? 0}
          max={100}
          color={color}
          size={136}
          caption="ms · última noche"
        />
        <div className="flex-1 min-w-0">
          <div className="grid grid-cols-2 gap-y-2.5 gap-x-4 mb-3">
            <StatBlock
              label="Baseline"
              value={hrv.baseline_ms ? `${hrv.baseline_ms} ms` : "—"}
            />
            <StatBlock label="Delta" value={deltaStr} color={deltaColor} />
            <StatBlock
              label="Días"
              value={`${hrv.days_recorded}/${hrv.days_required}`}
            />
          </div>
          <Sparkline
            nights={hrv.nights}
            baseline={hrv.baseline_ms}
            color={color}
          />
        </div>
      </div>

      {/* Progress bar baseline */}
      <div className="mt-3">
        <div className="flex justify-between mb-1.5">
          <span className="text-[11px] text-ink-tertiary">Progreso baseline</span>
          <span className="text-[11px] text-ink-secondary tnum">
            {hrv.days_recorded}/{hrv.days_required}
          </span>
        </div>
        <div className="h-1 rounded-full bg-rule/60 overflow-hidden">
          <div
            className="h-full transition-all"
            style={{ width: `${progress}%`, background: color }}
          />
        </div>
      </div>

      {/* Interpretación Liebre */}
      <div className="mt-3 pt-3 border-t border-rule/40">
        <div className="flex items-center gap-1.5 mb-1.5">
          <span className="text-[11px]">📊</span>
          <span className="label-uppercase">Interpretación Liebre</span>
        </div>
        <p className="text-[13px] text-ink-secondary leading-relaxed">
          Tu HRV de {hrv.latest_value} ms está dentro del rango funcional,
          pero el agente necesita {hrv.days_required - hrv.days_recorded}{" "}
          noches más para establecer tu baseline personal y detectar patrones
          individuales de recuperación.
        </p>
        <CiteBadge text="Plews & Buchheit (2017) · J Strength Cond Res · Observacional" />
      </div>
    </div>
  );
}
