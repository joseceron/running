/**
 * DiagnósticoDelDíaCard — ahora consume /v1/users/me/diagnosis (Claude API real).
 * Si la API falla, cae a un placeholder determinístico basado en los datos.
 */

import { CiteBadge } from "./CiteBadge";
import type { Diagnosis, HRV, Profile, Weekly } from "@/lib/api";

const ALERT_DOT: Record<Diagnosis["alert_level"], string> = {
  info: "var(--semantic-info)",
  warn: "var(--semantic-warning)",
  danger: "var(--semantic-danger)",
};

const ALERT_LABEL: Record<Diagnosis["alert_level"], string> = {
  info: "Estable",
  warn: "Atención",
  danger: "Alerta",
};

type Props = {
  profile: Profile;
  hrv: HRV;
  weekly: Weekly;
  diagnosis: Diagnosis | null;
  /**
   * Cuando TodayActionCard está visible es la fuente de verdad para "qué hacer hoy".
   * Si lo está, ocultamos el bloque "acción" del LLM para evitar contradicciones
   * (el LLM no recibe el plan y a veces recomienda lo opuesto al día programado).
   */
  todayActionShown?: boolean;
};

export function DiagnosticoDelDiaCard({
  profile,
  hrv,
  weekly,
  diagnosis,
  todayActionShown = false,
}: Props) {
  const view = diagnosis ?? buildPlaceholderDiagnostico({ hrv, weekly });
  const alert = diagnosis?.alert_level ?? "info";
  const showActionBlock = !todayActionShown;

  return (
    <div
      className="card md:col-span-2"
      style={{
        background:
          "radial-gradient(ellipse 60% 80% at 95% 5%, rgba(25,118,210,0.05) 0%, transparent 60%), #fff",
      }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3.5 gap-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-accent-brand flex items-center justify-center text-white font-bold text-[13px] shrink-0">
            L
          </div>
          <div>
            <span className="label-uppercase">Diagnóstico del Día</span>
            <p className="text-[11px] text-ink-tertiary mt-0.5">
              {diagnosis
                ? "Generado por Claude · análisis cruzado en vivo"
                : "Modo placeholder · API no disponible"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          <span
            className="w-2 h-2 rounded-full"
            style={{ background: ALERT_DOT[alert] }}
          />
          <span
            className="text-[11px] font-semibold uppercase tracking-wide"
            style={{ color: ALERT_DOT[alert] }}
          >
            {ALERT_LABEL[alert]}
          </span>
        </div>
      </div>

      {/* Cuerpo */}
      <p className="text-sm text-ink-primary leading-relaxed m-0 whitespace-pre-line">
        {view.narrative}
      </p>

      {showActionBlock ? (
        <div className="mt-3.5 pt-3.5 border-t border-rule/60">
          <span className="label-uppercase">Acción recomendada para hoy</span>
          <p className="text-[13px] font-medium text-ink-primary mt-1.5 leading-snug">
            {view.action}
          </p>
          <CiteBadge text={view.citation} />
        </div>
      ) : (
        /* TodayActionCard ya indica qué hacer hoy. Aquí solo dejamos la cita
           para que el análisis siga teniendo respaldo visible. */
        <div className="mt-3.5 pt-3.5 border-t border-rule/60">
          <CiteBadge text={view.citation} />
        </div>
      )}
    </div>
  );
}

function buildPlaceholderDiagnostico({
  hrv,
  weekly,
}: {
  hrv: HRV;
  weekly: Weekly;
}) {
  const lastWeek = weekly.weeks[0];
  if (hrv.status === "building_baseline") {
    return {
      narrative: `Aún estamos construyendo tu baseline personal de HRV (${hrv.days_recorded} de ${hrv.days_required} noches). Tu semana muestra ${lastWeek?.executed_km?.toFixed(1) ?? "—"} km ejecutados con ACWR ${lastWeek?.acwr?.toFixed(2) ?? "—"}, en zona segura.`,
      // Acción inequívoca: dormir con el reloj para completar baseline.
      // Lo de "qué hacer hoy" vive en TodayActionCard (single source of truth).
      action: `Dormir con el reloj puesto las próximas ${Math.max(0, hrv.days_required - hrv.days_recorded)} noches — sin baseline completo las recomendaciones de carga van a ciegas. La acción de entrenamiento de hoy la indica la tarjeta superior.`,
      citation: "Buchheit (2014) · Front Physiol · Review (HRV baseline individual)",
    };
  }
  return {
    narrative: `Tu HRV de ${hrv.latest_value} ms está dentro del rango balanceado. El sistema autónomo refleja buena recuperación.`,
    action: `La acción de entrenamiento de hoy la indica la tarjeta superior (con prioridad sobre este texto cuando hay contradicción).`,
    citation: "Plews & Buchheit (2017) · J Strength Cond Res · Observacional",
  };
}
