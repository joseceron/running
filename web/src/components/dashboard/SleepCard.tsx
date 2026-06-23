/**
 * SleepCard — fases de sueño nocturno con barra proporcional + interpretación.
 * Datos: Garmin (deep/REM/light en segundos → minutos).
 * Diseño inspirado en Apple Health: cada fase con color, duración y Term tooltip.
 */

import { Term } from "./Term";
import type { Sleep } from "@/lib/api";

type Phase = {
  key: "deep" | "rem" | "light" | "awake";
  label: string;
  termKey: "sueno_profundo" | "sueno_rem" | "sueno_ligero" | "sueno_vigilia";
  color: string;
  min: number | null;
};

function fmtDuration(min: number | null): string {
  if (!min) return "—";
  const h = Math.floor(min / 60);
  const m = min % 60;
  if (h === 0) return `${m} min`;
  return `${h} h ${m > 0 ? `${m} min` : ""}`.trim();
}

function scoreColor(score: number | null): string {
  if (!score) return "var(--ink-tertiary)";
  if (score >= 80) return "var(--hrv-balanced)";
  if (score >= 60) return "var(--semantic-warning)";
  return "var(--semantic-danger)";
}

function scoreLabel(score: number | null): string {
  if (!score) return "Sin score";
  if (score >= 80) return "Excelente";
  if (score >= 70) return "Bueno";
  if (score >= 60) return "Regular";
  return "Deficiente";
}

export function SleepCard({ sleep }: { sleep: Sleep }) {
  const phases: Phase[] = [
    { key: "deep",  label: "Profundo", termKey: "sueno_profundo", color: "#1e3a8a", min: sleep.deep_min },
    { key: "rem",   label: "REM",      termKey: "sueno_rem",      color: "#60a5fa", min: sleep.rem_min },
    { key: "light", label: "Ligero",   termKey: "sueno_ligero",   color: "#3b82f6", min: sleep.light_min },
    { key: "awake", label: "Vigilia",  termKey: "sueno_vigilia",  color: "#f87171", min: sleep.awake_min },
  ];

  const total = sleep.total_min ?? phases.reduce((s, p) => s + (p.min ?? 0), 0);

  return (
    <div className="card md:col-span-2">
      {/* Header */}
      <div className="flex items-start justify-between mb-3.5">
        <div>
          <div className="flex items-center gap-1.5">
            <span className="text-[13px]">🛏</span>
            <span className="label-uppercase">Sueño Nocturno</span>
          </div>
          <p className="text-[11px] text-ink-tertiary mt-1">Última noche</p>
        </div>
        {sleep.sleep_score && (
          <span
            className="text-[11px] font-semibold px-2.5 py-1 rounded-full"
            style={{
              background: `color-mix(in srgb, ${scoreColor(sleep.sleep_score)} 12%, transparent)`,
              color: scoreColor(sleep.sleep_score),
            }}
          >
            ● {scoreLabel(sleep.sleep_score)} · {sleep.sleep_score}/100
          </span>
        )}
      </div>

      {/* Tiempo total grande */}
      <div className="flex items-baseline gap-3 mb-4">
        <div>
          <p className="text-[11px] text-ink-tertiary uppercase tracking-wider mb-0.5">Tiempo de sueño</p>
          <p className="text-3xl font-bold tnum text-ink-primary">{fmtDuration(total)}</p>
        </div>
        {sleep.time_in_bed_min && (
          <div className="ml-6">
            <p className="text-[11px] text-ink-tertiary uppercase tracking-wider mb-0.5">En cama</p>
            <p className="text-xl font-semibold tnum text-ink-secondary">{fmtDuration(sleep.time_in_bed_min)}</p>
          </div>
        )}
      </div>

      {/* Barra proporcional de fases */}
      <div className="mb-4">
        <div className="flex h-4 rounded-full overflow-hidden gap-0.5">
          {phases.map((p) => {
            if (!p.min || total === 0) return null;
            const pct = (p.min / total) * 100;
            return (
              <div
                key={p.key}
                style={{ width: `${pct}%`, background: p.color }}
                title={`${p.label}: ${fmtDuration(p.min)}`}
              />
            );
          })}
        </div>
      </div>

      {/* Desglose de fases */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        {phases.map((p) => (
          <div key={p.key} className="flex items-center gap-2.5">
            <span
              className="w-2.5 h-2.5 rounded-sm shrink-0"
              style={{ background: p.color }}
            />
            <div className="min-w-0">
              <p className="text-[11px] text-ink-tertiary leading-none mb-0.5">
                <Term k={p.termKey}>{p.label}</Term>
              </p>
              <p className="text-sm font-semibold tnum text-ink-primary">
                {fmtDuration(p.min)}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Interpretación rápida */}
      <div className="pt-3 border-t border-rule/40">
        <p className="text-[12px] text-ink-secondary leading-relaxed">
          {buildInterpretation(sleep)}
        </p>
      </div>
    </div>
  );
}

function buildInterpretation(s: Sleep): string {
  const parts: string[] = [];
  if ((s.deep_min ?? 0) < 45) {
    parts.push("Sueño profundo bajo (<45 min) — falta recuperación física y hormonal.");
  } else if ((s.deep_min ?? 0) >= 60) {
    parts.push(`Sueño profundo sólido (${s.deep_min} min) — reparación muscular y hormonal activa.`);
  }
  if ((s.rem_min ?? 0) < 60) {
    parts.push("REM corto (<60 min) — consolidación de memoria motora incompleta.");
  } else {
    parts.push(`REM adecuado (${s.rem_min} min) — memoria motora y recuperación mental bien.`);
  }
  if ((s.total_min ?? 0) >= 420) {
    parts.push("Duración total óptima (≥7 h).");
  } else {
    parts.push("Duración total insuficiente — prioriza dormir antes de las 11 pm.");
  }
  return parts.join(" ");
}
