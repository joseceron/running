/**
 * InsightCards — 4 cards del diferencial científico Liebre.
 *
 * No replican Connect: cada card responde (1) qué te está pasando en el cuerpo,
 * (2) por qué importa para tu meta, (3) qué paper lo respalda.
 *
 * Visualizaciones inline en SVG, sin librerías. Datos vienen del endpoint
 * /v1/users/me/report > insights.
 */

import type { Insights } from "@/lib/api";

const ZONE_COLORS = [
  "#9aa6b5", // Z1 gris
  "#1976d2", // Z2 azul (base aeróbica)
  "#16a34a", // Z3 verde
  "#d29400", // Z4 ámbar
  "#d92f31", // Z5 rojo
];


export function InsightSection({ insights }: { insights: Insights | null }) {
  if (!insights) {
    return (
      <section className="card mt-4">
        <p className="label-uppercase">🔬 Insights científicos</p>
        <p className="text-sm text-ink-secondary mt-2">
          Sincroniza Garmin para ver los análisis científicos basados en tu última sesión.
        </p>
      </section>
    );
  }

  return (
    <section className="mt-6 space-y-4">
      <header className="border-b border-rule/40 pb-2">
        <h2 className="text-base font-semibold text-ink-primary">
          🔬 Insights científicos
        </h2>
        <p className="text-xs text-ink-tertiary mt-0.5">
          El diferencial Liebre — interpretación con respaldo en literatura. Esto NO lo da Garmin Connect.
        </p>
      </header>

      <div className="grid md:grid-cols-2 gap-4">
        {insights.heart_progress && (
          <HeartProgressCard data={insights.heart_progress} />
        )}
        {insights.polarization && (
          <PolarizationCard data={insights.polarization} />
        )}
        {insights.fat_burn && <FatBurnCard data={insights.fat_burn} />}
        {insights.cardiac_drift && (
          <CardiacDriftCard data={insights.cardiac_drift} />
        )}
      </div>
    </section>
  );
}

// ──────────────────────────────────────────────────────────────────
// 1. HEART PROGRESS — FC reposo + hipertrofia VI
// ──────────────────────────────────────────────────────────────────

function HeartProgressCard({
  data,
}: {
  data: NonNullable<Insights["heart_progress"]>;
}) {
  const trendColor =
    data.rhr_trend === "improving"
      ? "var(--semantic-positive, #18a957)"
      : data.rhr_trend === "stable"
        ? "var(--semantic-warning, #d29400)"
        : "var(--semantic-danger, #d92f31)";
  const trendLabel =
    data.rhr_trend === "improving"
      ? "↓ adaptándose"
      : data.rhr_trend === "stable"
        ? "→ estable"
        : "↑ vigilar";

  return (
    <InsightCardShell
      title="Tu corazón está cambiando"
      subtitle="Hipertrofia excéntrica del ventrículo izquierdo"
      icon="❤️"
    >
      <div className="flex items-baseline gap-3 mt-3">
        <span className="text-4xl font-light tabular-nums text-ink-primary">
          {data.rhr_current}
        </span>
        <span className="text-xs text-ink-tertiary">lpm reposo</span>
        <span
          className="text-[11px] font-semibold uppercase tracking-wide ml-auto"
          style={{ color: trendColor }}
        >
          {trendLabel}
        </span>
      </div>

      {/* Línea visual: baseline anterior → actual → meta */}
      <div className="mt-4 mb-2">
        <div className="flex items-center gap-1 text-[10px] text-ink-tertiary uppercase">
          <span>56</span>
          <div className="flex-1 h-[2px] bg-rule relative">
            <div
              className="absolute top-0 h-full"
              style={{
                left: 0,
                width: `${((56 - data.rhr_current) / (56 - 45)) * 100}%`,
                background: trendColor,
              }}
            />
            <div
              className="absolute -top-1 w-2 h-2 rounded-full"
              style={{
                left: `${((56 - data.rhr_current) / (56 - 45)) * 100}%`,
                background: trendColor,
                transform: "translateX(-50%)",
              }}
            />
          </div>
          <span>45</span>
        </div>
        <div className="flex justify-between text-[10px] text-ink-tertiary mt-1">
          <span>donde empezaste</span>
          <span>baseline {data.rhr_baseline.toFixed(0)}</span>
          <span>meta atleta</span>
        </div>
      </div>

      <p className="text-xs text-ink-primary leading-relaxed mt-3">
        {data.explanation}
      </p>
      <CitationFooter text={data.citation} />
    </InsightCardShell>
  );
}

// ──────────────────────────────────────────────────────────────────
// 2. POLARIZATION — 80/20 visualizado
// ──────────────────────────────────────────────────────────────────

function PolarizationCard({
  data,
}: {
  data: NonNullable<Insights["polarization"]>;
}) {
  const evalMap = {
    aligned: { color: "var(--semantic-positive, #18a957)", text: "✓ Distribución polarizada correcta" },
    too_easy: { color: "var(--semantic-warning, #d29400)", text: "Falta calidad — todo Z1-Z2 sin estímulo VO₂máx" },
    too_hard: { color: "var(--semantic-danger, #d92f31)", text: "Demasiada intensidad — riesgo de sobreuso" },
    mixed: { color: "var(--semantic-warning, #d29400)", text: "Mucha zona gris (Z3) — ni base ni VO₂máx" },
  };
  const e = evalMap[data.evaluation];

  // Barra horizontal: yours vs ideal
  return (
    <InsightCardShell
      title="Distribución polarizada 80/20"
      subtitle="Seiler — la receta de los élite mundiales de fondo"
      icon="🎯"
    >
      <div className="mt-3 space-y-3">
        <BarRow label="Tu sesión" z12={data.z1_z2_pct} z3={data.z3_pct} z45={data.z4_z5_pct} bold />
        <BarRow
          label="Ideal Seiler"
          z12={data.ideal_z1_z2_pct}
          z3={data.ideal_z3_pct}
          z45={data.ideal_z4_z5_pct}
        />
      </div>

      <p className="text-xs font-medium mt-3" style={{ color: e.color }}>
        {e.text}
      </p>
      <p className="text-xs text-ink-secondary leading-relaxed mt-2">
        El modelo polarizado (80% fácil + 20% muy intenso, evitando Z3) produce más adaptaciones aeróbicas
        que el modelo umbral en corredores de fondo. La Z3 es "tierra de nadie": cansa como Z4 sin estimular como Z4.
      </p>
      <p className="text-[10px] text-ink-tertiary mt-2 italic">
        Basado en {data.source_label}
      </p>
      <CitationFooter text={data.citation} />
    </InsightCardShell>
  );
}

function BarRow({
  label,
  z12,
  z3,
  z45,
  bold = false,
}: {
  label: string;
  z12: number;
  z3: number;
  z45: number;
  bold?: boolean;
}) {
  return (
    <div>
      <div className="flex justify-between items-baseline text-[11px] mb-1">
        <span className={bold ? "font-semibold text-ink-primary" : "text-ink-tertiary"}>
          {label}
        </span>
        <span className="text-ink-tertiary tabular-nums">
          {z12.toFixed(0)}% · {z3.toFixed(0)}% · {z45.toFixed(0)}%
        </span>
      </div>
      <div className="flex h-3 rounded overflow-hidden bg-rule/20">
        <div
          style={{ width: `${z12}%`, background: ZONE_COLORS[1] }}
          title={`Z1-Z2: ${z12.toFixed(0)}%`}
        />
        <div
          style={{ width: `${z3}%`, background: ZONE_COLORS[2] }}
          title={`Z3: ${z3.toFixed(0)}%`}
        />
        <div
          style={{ width: `${z45}%`, background: ZONE_COLORS[4] }}
          title={`Z4-Z5: ${z45.toFixed(0)}%`}
        />
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────
// 3. FAT BURN — FatMax por zona
// ──────────────────────────────────────────────────────────────────

function FatBurnCard({
  data,
}: {
  data: NonNullable<Insights["fat_burn"]>;
}) {
  const fatPctTotal = Math.round((data.fat_kcal / data.total_kcal) * 100);

  return (
    <InsightCardShell
      title="Quema de grasa real"
      subtitle={`${data.activity_name} · FatMax por zona FC`}
      icon="🔥"
    >
      <div className="mt-3 grid grid-cols-3 gap-3 text-center">
        <div>
          <p className="text-2xl font-semibold tabular-nums text-ink-primary">
            {data.fat_kcal}
          </p>
          <p className="text-[10px] text-ink-tertiary uppercase">kcal grasa</p>
        </div>
        <div>
          <p className="text-2xl font-semibold tabular-nums text-ink-primary">
            {data.fat_grams}g
          </p>
          <p className="text-[10px] text-ink-tertiary uppercase">tejido adiposo</p>
        </div>
        <div>
          <p className="text-2xl font-semibold tabular-nums text-ink-primary">
            {fatPctTotal}%
          </p>
          <p className="text-[10px] text-ink-tertiary uppercase">del esfuerzo</p>
        </div>
      </div>

      {/* Bar chart kcal grasa vs CHO por zona */}
      <div className="mt-4 space-y-1.5">
        {data.by_zone
          .filter((z) => z.pct_time > 0.5)
          .map((z) => (
            <div key={z.zone}>
              <div className="flex items-baseline justify-between text-[10px] mb-0.5">
                <span className="text-ink-secondary">{z.label}</span>
                <span className="text-ink-tertiary tabular-nums">
                  {z.kcal_fat.toFixed(0)} grasa · {z.kcal_cho.toFixed(0)} CHO
                </span>
              </div>
              <div className="flex h-2.5 rounded overflow-hidden bg-rule/20">
                {z.kcal_total > 0 && (
                  <>
                    <div
                      style={{
                        width: `${(z.kcal_fat / data.total_kcal) * 100}%`,
                        background: "#d29400",
                      }}
                      title={`${z.kcal_fat.toFixed(0)} kcal grasa`}
                    />
                    <div
                      style={{
                        width: `${(z.kcal_cho / data.total_kcal) * 100}%`,
                        background: "#9aa6b5",
                      }}
                      title={`${z.kcal_cho.toFixed(0)} kcal CHO`}
                    />
                  </>
                )}
              </div>
            </div>
          ))}
      </div>

      <p className="text-xs text-ink-primary leading-relaxed mt-3">
        En Z2 oxidas ~{data.by_zone[1]?.fat_pct}% como grasa; en Z4 baja a ~{data.by_zone[3]?.fat_pct}%.
        Por eso una caminata larga en Z2 quema más grasa absoluta que un sprint en Z5 — no por
        intensidad, por sustrato. Tu Z2 hoy convirtió {data.fat_grams}g de grasa en energía.
      </p>
      <CitationFooter text={data.citation} />
    </InsightCardShell>
  );
}

// ──────────────────────────────────────────────────────────────────
// 4. CARDIAC DRIFT — eficiencia cardíaca
// ──────────────────────────────────────────────────────────────────

function CardiacDriftCard({
  data,
}: {
  data: NonNullable<Insights["cardiac_drift"]>;
}) {
  const driftColor =
    data.drift_pct < 5
      ? "var(--semantic-positive, #18a957)"
      : data.drift_pct < 10
        ? "var(--semantic-warning, #d29400)"
        : "var(--semantic-danger, #d92f31)";

  return (
    <InsightCardShell
      title="Cardiac drift"
      subtitle={`${data.activity_name} · eficiencia intra-sesión`}
      icon="📈"
    >
      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-4xl font-light tabular-nums" style={{ color: driftColor }}>
          {data.drift_pct > 0 ? "+" : ""}
          {data.drift_pct.toFixed(1)}%
        </span>
        <span className="text-xs text-ink-tertiary">drift FC en la sesión</span>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-3">
        <div className="card-inset" style={{ background: "var(--bg-card-soft, #f5f6f8)", padding: "8px 12px", borderRadius: 6 }}>
          <p className="text-[10px] uppercase text-ink-tertiary">Primera mitad</p>
          <p className="text-lg tabular-nums font-semibold text-ink-primary">
            {data.first_half_hr.toFixed(0)} <span className="text-xs font-normal text-ink-tertiary">lpm</span>
          </p>
        </div>
        <div className="card-inset" style={{ background: "var(--bg-card-soft, #f5f6f8)", padding: "8px 12px", borderRadius: 6 }}>
          <p className="text-[10px] uppercase text-ink-tertiary">Segunda mitad</p>
          <p className="text-lg tabular-nums font-semibold text-ink-primary">
            {data.second_half_hr.toFixed(0)} <span className="text-xs font-normal text-ink-tertiary">lpm</span>
          </p>
        </div>
      </div>

      <p className="text-xs text-ink-primary leading-relaxed mt-3">
        <strong>{data.evaluation}</strong>. El drift &lt;5% en Z2 indica que tu corazón mantiene FC
        a pesar de la fatiga acumulada — economía cardíaca real. Es uno de los marcadores más sensibles
        de adaptación aeróbica y predice mejor que VO₂máx el rendimiento sostenido en distancias largas.
      </p>
      <CitationFooter text={data.citation} />
    </InsightCardShell>
  );
}

// ──────────────────────────────────────────────────────────────────
// Shell común
// ──────────────────────────────────────────────────────────────────

function InsightCardShell({
  title,
  subtitle,
  icon,
  children,
}: {
  title: string;
  subtitle?: string;
  icon: string;
  children: React.ReactNode;
}) {
  return (
    <div
      className="card"
      style={{
        background:
          "radial-gradient(ellipse 60% 80% at 95% 5%, rgba(25,118,210,0.04) 0%, transparent 60%), #fff",
      }}
    >
      <div className="flex items-start gap-3 pb-2 border-b border-rule/40">
        <span className="text-2xl leading-none">{icon}</span>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-ink-primary leading-tight">
            {title}
          </h3>
          {subtitle && (
            <p className="text-[11px] text-ink-tertiary mt-0.5">{subtitle}</p>
          )}
        </div>
      </div>
      {children}
    </div>
  );
}

function CitationFooter({ text }: { text: string }) {
  return (
    <p className="text-[10px] text-accent-brand mt-3 font-medium border-t border-rule/30 pt-2">
      📄 {text}
    </p>
  );
}
