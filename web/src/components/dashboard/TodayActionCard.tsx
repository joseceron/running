/**
 * TodayActionCard — la respuesta inequívoca a "¿qué hago hoy?".
 *
 * Esta card va PRIMERA en el dashboard. Nunca debe haber duda de si
 * el usuario debe entrenar o descansar HOY (no mañana). Tres estados
 * visuales: descanso (verde), recuperación activa (ámbar), entrenamiento
 * (azul), ya entrenó (azul claro).
 */

import type { TodayAction } from "@/lib/api";

const STYLE: Record<
  TodayAction["status"],
  { bg: string; tag: string; tagBg: string; emoji: string; chip: string }
> = {
  // HOY
  rest: {
    bg: "linear-gradient(135deg, #18a957 0%, #138842 100%)",
    tag: "DESCANSO",
    tagBg: "rgba(255,255,255,0.18)",
    emoji: "🛌",
    chip: "Hoy",
  },
  active_recovery: {
    bg: "linear-gradient(135deg, #d29400 0%, #a87500 100%)",
    tag: "RECUPERACIÓN ACTIVA",
    tagBg: "rgba(255,255,255,0.18)",
    emoji: "🧘",
    chip: "Hoy",
  },
  train: {
    bg: "linear-gradient(135deg, #1976d2 0%, #115293 100%)",
    tag: "ENTRENAR",
    tagBg: "rgba(255,255,255,0.18)",
    emoji: "🏃",
    chip: "Hoy",
  },
  trained_already: {
    bg: "linear-gradient(135deg, #2e7eb8 0%, #1e5a8a 100%)",
    tag: "YA ENTRENASTE",
    tagBg: "rgba(255,255,255,0.18)",
    emoji: "✅",
    chip: "Hoy",
  },
  // PASADO
  past_executed: {
    bg: "linear-gradient(135deg, #2d3748 0%, #1a202c 100%)",
    tag: "EJECUTADO",
    tagBg: "rgba(24,169,87,0.45)",
    emoji: "✓",
    chip: "Historial",
  },
  past_rest_planned: {
    bg: "linear-gradient(135deg, #2d3748 0%, #1a202c 100%)",
    tag: "DESCANSO PROGRAMADO",
    tagBg: "rgba(255,255,255,0.16)",
    emoji: "🛌",
    chip: "Historial",
  },
  past_missed: {
    bg: "linear-gradient(135deg, #4a5568 0%, #2d3748 100%)",
    tag: "NO REALIZADO",
    tagBg: "rgba(217,47,49,0.55)",
    emoji: "○",
    chip: "Historial",
  },
  // FUTURO
  future_planned: {
    bg: "linear-gradient(135deg, #5a7fa3 0%, #3d5a78 100%)",
    tag: "PLANIFICADO",
    tagBg: "rgba(255,255,255,0.18)",
    emoji: "📅",
    chip: "Próximo",
  },
};

export function TodayActionCard({ action }: { action: TodayAction }) {
  const s = STYLE[action.status];

  return (
    <div
      className="rounded-lg overflow-hidden text-white shadow-sm"
      style={{ background: s.bg }}
    >
      {/* Header con tag y emoji */}
      <div className="px-5 pt-4 pb-3 flex items-start justify-between gap-3">
        <span
          className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded"
          style={{ background: s.tagBg }}
        >
          {s.chip} · {s.tag}
        </span>
        <span className="text-2xl leading-none" aria-hidden>
          {s.emoji}
        </span>
      </div>

      {/* Headline grande */}
      <div className="px-5">
        <h2
          className="text-2xl md:text-3xl font-bold leading-tight"
          style={{ wordBreak: "break-word" }}
        >
          {action.headline}
        </h2>
        <p className="text-sm mt-2 leading-snug opacity-95">
          {action.short_reason}
        </p>
      </div>

      {/* Razones (datos objetivos) */}
      <div className="px-5 mt-4">
        <p
          className="text-[10px] font-semibold uppercase tracking-widest opacity-80 mb-1.5"
        >
          Por qué
        </p>
        <ul className="space-y-1">
          {action.reasons.map((r, i) => (
            <li key={i} className="text-xs leading-relaxed opacity-95 flex gap-2">
              <span aria-hidden>•</span>
              <span>{r}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Permitido (qué SÍ puedes hacer) — sólo para vistas de HOY */}
      {action.temporal === "today" && action.allowed.length > 0 && (
        <div className="px-5 mt-4">
          <p
            className="text-[10px] font-semibold uppercase tracking-widest opacity-80 mb-1.5"
          >
            {action.status === "trained_already" ? "Complemento opcional" : action.status === "train" ? "Tips para hoy" : "Qué SÍ puedes hacer"}
          </p>
          <ul className="space-y-1">
            {action.allowed.map((a, i) => (
              <li key={i} className="text-xs leading-relaxed opacity-95 flex gap-2">
                <span aria-hidden>✓</span>
                <span>{a}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Próxima sesión */}
      {action.next_session && (
        <div
          className="mt-4 px-5 py-3 text-xs"
          style={{ background: "rgba(0,0,0,0.18)" }}
        >
          <span className="font-semibold uppercase tracking-wide text-[10px] opacity-90">
            Próximo entreno
          </span>
          <p className="mt-0.5 opacity-95">{action.next_session}</p>
        </div>
      )}
    </div>
  );
}
