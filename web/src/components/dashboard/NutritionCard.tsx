/**
 * NutritionCard — nutrición, hidratación y factor ambiental.
 *
 * Otro pilar del diferencial Liebre. Datos calculados con fórmulas
 * de ACSM/Burke sobre el perfil del usuario + actividad del día +
 * altitud. CTA "consulta con experto humano" placeholder para futura
 * monetización vía Luz Dálida (nutricionista deportiva).
 */

import type { Nutrition } from "@/lib/api";

export function NutritionCard({ data }: { data: Nutrition }) {
  return (
    <section className="card mt-4">
      <header className="flex items-start gap-3 pb-3 border-b border-rule/40">
        <span className="text-2xl leading-none" aria-hidden>
          🥗
        </span>
        <div className="flex-1 min-w-0">
          <h2 className="text-sm font-semibold text-ink-primary uppercase tracking-wide">
            Nutrición, hidratación y entorno
          </h2>
          <p className="text-[11px] text-ink-tertiary mt-0.5">
            Cálculos sobre tu perfil + sesión + altitud · pilar diferencial Liebre
          </p>
        </div>
      </header>

      <div className="grid md:grid-cols-3 gap-4 mt-4">
        {/* HIDRATACIÓN */}
        <div>
          <p className="label-uppercase">💧 Hidratación</p>
          <p className="mt-1.5 flex items-baseline gap-1">
            <span className="text-3xl font-semibold tabular-nums text-ink-primary">
              {data.hydration.water_ml.toLocaleString()}
            </span>
            <span className="text-xs text-ink-tertiary">ml hoy</span>
          </p>
          {data.hydration.electrolytes_needed && (
            <p
              className="text-[10px] font-semibold uppercase tracking-wider mt-1 inline-block px-1.5 py-0.5 rounded"
              style={{
                background: "rgba(210, 148, 0, 0.14)",
                color: "var(--semantic-warning, #a87500)",
              }}
            >
              + electrolitos
            </p>
          )}
          <ul className="text-xs text-ink-secondary mt-2 space-y-1 leading-relaxed">
            {data.hydration.notes.map((n, i) => (
              <li key={i} className="flex gap-1.5">
                <span aria-hidden className="text-ink-tertiary">·</span>
                <span>{n}</span>
              </li>
            ))}
          </ul>
          {data.hydration.pre_session_ml > 0 && (
            <div className="mt-3 text-[11px] grid grid-cols-3 gap-1 text-center">
              <Mini label="pre" value={`${data.hydration.pre_session_ml}ml`} />
              <Mini
                label="durante"
                value={`${data.hydration.during_session_ml_per_hour}ml/h`}
              />
              <Mini label="post" value={`${data.hydration.post_session_ml}ml`} />
            </div>
          )}
          {data.hydration.real_world_examples.length > 0 && (
            <div
              className="mt-3 px-2 py-2 rounded text-[11px] leading-relaxed"
              style={{ background: "rgba(25,118,210,0.06)" }}
            >
              <p
                className="text-[10px] font-semibold uppercase tracking-wider mb-1"
                style={{ color: "var(--accent-brand, #1976d2)" }}
              >
                Cómo se ve en la práctica
              </p>
              <ul className="space-y-1">
                {data.hydration.real_world_examples.map((ex, i) => (
                  <li key={i} className="flex gap-1.5 text-ink-secondary">
                    <span aria-hidden>→</span>
                    <span>{ex}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* MACROS */}
        <div>
          <p className="label-uppercase">🍽️ Macros · {data.macros.fase}</p>
          <p className="mt-1.5 flex items-baseline gap-1">
            <span className="text-3xl font-semibold tabular-nums text-ink-primary">
              {data.macros.kcal_estimadas.toLocaleString()}
            </span>
            <span className="text-xs text-ink-tertiary">kcal estim.</span>
          </p>
          <div className="mt-2 space-y-1">
            <MacroRow
              label="Carbohidratos"
              value={`${data.macros.carbs_g}g`}
              color="#1976d2"
              pct={(data.macros.carbs_g * 4) / data.macros.kcal_estimadas}
            />
            <MacroRow
              label="Proteína"
              value={`${data.macros.protein_g}g`}
              color="#16a34a"
              pct={(data.macros.protein_g * 4) / data.macros.kcal_estimadas}
            />
            <MacroRow
              label="Grasas"
              value={`${data.macros.fat_g}g`}
              color="#d29400"
              pct={(data.macros.fat_g * 9) / data.macros.kcal_estimadas}
            />
          </div>
          <ul className="text-xs text-ink-secondary mt-3 space-y-1 leading-relaxed">
            {data.macros.timing_notes.map((n, i) => (
              <li key={i} className="flex gap-1.5">
                <span aria-hidden className="text-ink-tertiary">·</span>
                <span>{n}</span>
              </li>
            ))}
          </ul>
          {(data.macros.carbs_examples ||
            data.macros.protein_examples ||
            data.macros.fat_examples) && (
            <div
              className="mt-3 px-2 py-2 rounded text-[11px] leading-relaxed"
              style={{ background: "rgba(25,118,210,0.06)" }}
            >
              <p
                className="text-[10px] font-semibold uppercase tracking-wider mb-1"
                style={{ color: "var(--accent-brand, #1976d2)" }}
              >
                De dónde sacarlo
              </p>
              <ul className="space-y-1 text-ink-secondary">
                {data.macros.carbs_examples && (
                  <li className="flex gap-1.5">
                    <span aria-hidden style={{ color: "#1976d2" }}>●</span>
                    <span>{data.macros.carbs_examples}</span>
                  </li>
                )}
                {data.macros.protein_examples && (
                  <li className="flex gap-1.5">
                    <span aria-hidden style={{ color: "#16a34a" }}>●</span>
                    <span>{data.macros.protein_examples}</span>
                  </li>
                )}
                {data.macros.fat_examples && (
                  <li className="flex gap-1.5">
                    <span aria-hidden style={{ color: "#d29400" }}>●</span>
                    <span>{data.macros.fat_examples}</span>
                  </li>
                )}
              </ul>
            </div>
          )}
        </div>

        {/* AMBIENTE */}
        <div>
          <p className="label-uppercase">☀️ Entorno · {data.environment.altitude_msnm} msnm</p>
          <p className="mt-1.5 flex items-baseline gap-1">
            <span className="text-3xl font-semibold tabular-nums text-ink-primary">
              SPF {data.environment.sunscreen_spf}
            </span>
            <span className="text-xs text-ink-tertiary">UV {data.environment.sun_intensity}</span>
          </p>
          <p className="text-[10px] text-ink-tertiary mt-0.5">
            Reaplicar cada {data.environment.sunscreen_reapply_min} min en sesiones
            al sol
          </p>
          <ul className="text-xs text-ink-secondary mt-2 space-y-1 leading-relaxed">
            {data.environment.extra_notes.map((n, i) => (
              <li key={i} className="flex gap-1.5">
                <span aria-hidden className="text-ink-tertiary">·</span>
                <span>{n}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* CTA monetización — placeholder para Luz Dálida */}
      <div
        className="mt-5 px-4 py-3 rounded-md border border-dashed flex items-start gap-3"
        style={{
          borderColor: "var(--accent-brand, #1976d2)",
          background:
            "linear-gradient(90deg, rgba(25,118,210,0.04), transparent)",
        }}
      >
        <span className="text-xl leading-none" aria-hidden>
          👩‍⚕️
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-ink-primary">
            {data.expert_cta}
          </p>
          <p className="text-[11px] text-ink-tertiary mt-0.5">
            Planes mensuales personalizados sobre tus datos biométricos +
            consultas 1:1 — disponible próximamente.
          </p>
        </div>
        <button
          type="button"
          disabled
          className="text-[11px] font-medium px-3 py-1.5 rounded border whitespace-nowrap opacity-60 cursor-not-allowed"
          style={{
            borderColor: "var(--accent-brand, #1976d2)",
            color: "var(--accent-brand, #1976d2)",
          }}
        >
          Próximamente
        </button>
      </div>

      <p className="text-[10px] text-accent-brand mt-3 font-medium">
        📄 {data.citation}
      </p>
    </section>
  );
}

function Mini({ label, value }: { label: string; value: string }) {
  return (
    <div
      className="rounded py-1.5"
      style={{ background: "var(--bg-card-soft, #f5f6f8)" }}
    >
      <p
        className="text-[9px] uppercase tracking-wider"
        style={{ color: "var(--ink-tertiary)" }}
      >
        {label}
      </p>
      <p
        className="tabular-nums font-semibold"
        style={{ color: "var(--ink-primary)" }}
      >
        {value}
      </p>
    </div>
  );
}

function MacroRow({
  label,
  value,
  color,
  pct,
}: {
  label: string;
  value: string;
  color: string;
  pct: number;
}) {
  const clamped = Math.max(0, Math.min(1, pct));
  return (
    <div>
      <div className="flex justify-between items-baseline text-[11px] mb-0.5">
        <span className="text-ink-secondary">{label}</span>
        <span className="text-ink-tertiary tabular-nums">{value}</span>
      </div>
      <div className="h-1.5 rounded overflow-hidden bg-rule/20">
        <div style={{ width: `${clamped * 100}%`, background: color, height: "100%" }} />
      </div>
    </div>
  );
}
