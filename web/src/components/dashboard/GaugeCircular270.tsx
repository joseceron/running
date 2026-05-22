/**
 * Gauge circular tipo Garmin Connect — donut parcial de 270°.
 * Usado para HRV score, Readiness, Body Battery, Stress, Sleep score.
 *
 * Decisión de diseño Connect: el arco va de las 7 a las 5 (orientación
 * de reloj), grosor ~12-14px, número central en tipografía display.
 * El dot indicador se posiciona en el % del arco según el valor.
 */

import type { ReactNode } from "react";

type Props = {
  value: number;
  max?: number;
  min?: number;
  /** Color del arco activo (hex). Default azul Connect. */
  color?: string;
  /** Tamaño en px del lado del SVG (cuadrado). */
  size?: number;
  /** Label opcional debajo del número central. */
  caption?: ReactNode;
  /** Subtexto pequeño junto al número (ej. "/100"). */
  unit?: string;
};

const ARC_SWEEP_DEG = 270;
const ARC_START_DEG = 135; // 7 en reloj

function polar(cx: number, cy: number, r: number, deg: number) {
  const rad = ((deg - 90) * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function arcPath(cx: number, cy: number, r: number, startDeg: number, endDeg: number) {
  const start = polar(cx, cy, r, endDeg);
  const end = polar(cx, cy, r, startDeg);
  const large = endDeg - startDeg <= 180 ? 0 : 1;
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${large} 0 ${end.x} ${end.y}`;
}

export function GaugeCircular270({
  value,
  max = 100,
  min = 0,
  color = "#1976d2",
  size = 156,
  caption,
  unit,
}: Props) {
  const clamped = Math.max(min, Math.min(max, value));
  const pct = (clamped - min) / (max - min);
  const stroke = 12;
  const r = (size - stroke) / 2;
  const cx = size / 2;
  const cy = size / 2;

  const arcEnd = ARC_START_DEG + ARC_SWEEP_DEG;
  const activeEnd = ARC_START_DEG + ARC_SWEEP_DEG * pct;
  const dot = polar(cx, cy, r, activeEnd);

  const trackPath = arcPath(cx, cy, r, ARC_START_DEG, arcEnd);
  const activePath = arcPath(cx, cy, r, ARC_START_DEG, activeEnd);

  return (
    <div
      className="relative inline-flex flex-col items-center justify-center"
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <path
          d={trackPath}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth={stroke}
          strokeLinecap="round"
        />
        <path
          d={activePath}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
        />
        <circle cx={dot.x} cy={dot.y} r={stroke / 1.6} fill={color} />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <div className="metric-display text-5xl">
          {Math.round(clamped)}
          {unit && (
            <span className="text-base text-ink-tertiary ml-1 font-normal">{unit}</span>
          )}
        </div>
        {caption && (
          <div className="text-xs text-ink-tertiary mt-1 px-3">{caption}</div>
        )}
      </div>
    </div>
  );
}
