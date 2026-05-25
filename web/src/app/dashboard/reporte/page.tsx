import { liebreApiServer } from "@/lib/api-server";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { TopBar } from "@/components/dashboard/TopBar";
import { InsightSection } from "@/components/dashboard/InsightCards";
import { TodayActionCard } from "@/components/dashboard/TodayActionCard";
import { NutritionCard } from "@/components/dashboard/NutritionCard";

export const dynamic = "force-dynamic";

type SearchParams = Promise<{ date?: string }>;

const GATE_COLOR: Record<string, string> = {
  green: "var(--semantic-positive, #18a957)",
  yellow: "var(--semantic-warning, #d29400)",
  red: "var(--semantic-danger, #d92f31)",
};

const GATE_LABEL: Record<string, string> = {
  green: "OK",
  yellow: "PENDIENTE",
  red: "BLOQUEADO",
};

export default async function ReportPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const { date } = await searchParams;
  const safeDate = date && /^\d{4}-\d{2}-\d{2}$/.test(date) ? date : undefined;

  let dashboardData;
  let report;
  let cronologia = null;

  try {
    [dashboardData, report, cronologia] = await Promise.all([
      liebreApiServer.dashboard(),
      liebreApiServer.report(safeDate),
      liebreApiServer.cronologia(safeDate).catch(() => null),
    ]);
  } catch (err) {
    return (
      <main className="min-h-screen flex items-center justify-center p-8 bg-bg-page">
        <div className="max-w-md text-center card">
          <p className="label-uppercase" style={{ color: "var(--semantic-danger)" }}>
            Reporte no disponible
          </p>
          <p className="text-sm text-ink-secondary mt-3">No pude generar el reporte.</p>
          <p className="text-xs text-ink-tertiary mt-2 font-mono">{String(err)}</p>
        </div>
      </main>
    );
  }

  const { profile } = dashboardData;
  const greenGates = report.gates.filter((g) => g.status === "green").length;

  return (
    <div className="min-h-screen bg-bg-page">
      <Sidebar userName={profile.name} />
      <main className="min-h-screen md:ml-[var(--sidebar-width)] pb-24 md:pb-0">
        <div className="max-w-6xl mx-auto px-4 md:px-8 py-6 md:py-8">
          <TopBar
            userName={profile.name}
            title="reporte del día — 8 secciones"
            currentDate={safeDate}
          />

          {/* HOY: acción inequívoca arriba */}
          <div className="mb-4">
            <TodayActionCard action={report.today_action} />
          </div>

          {/* INSIGHTS CIENTÍFICOS — diferencial Liebre */}
          <InsightSection insights={report.insights} />

          {/* NUTRICIÓN — diferencial + base monetización Luz Dálida */}
          {report.nutrition && <NutritionCard data={report.nutrition} />}

          {/* 1. Entrenos del día */}
          <Section number={1} title="Entrenos del día">
            {report.activities_today.length === 0 ? (
              <p className="text-sm text-ink-secondary">
                Sin entrenos registrados en esta fecha.
                {cronologia && cronologia.summary.sleep_duration_min === 0 && (
                  <span className="block mt-1 text-xs text-ink-tertiary">
                    (Si esperabas ver datos, sincroniza Garmin)
                  </span>
                )}
              </p>
            ) : (
              <ul className="space-y-2">
                {report.activities_today.map((a, i) => (
                  <li
                    key={i}
                    className="flex items-baseline gap-3 text-sm"
                  >
                    <span className="font-mono text-xs text-ink-tertiary w-12">
                      {formatHour(a.hour)}
                    </span>
                    <span className="font-medium text-ink-primary flex-1">
                      {a.label}
                    </span>
                    <span className="label-uppercase">{a.type}</span>
                  </li>
                ))}
              </ul>
            )}
          </Section>

          {/* 2. Pisada y biomecánica */}
          <Section
            number={2}
            title={`Pisada y biomecánica${
              report.biomechanics?.is_walk ? " (caminata)" : " (carrera)"
            }`}
          >
            {!report.biomechanics ? (
              <p className="text-sm text-ink-secondary">
                Sin actividad reciente con métricas de running dynamics.
              </p>
            ) : (
              <div className="grid grid-cols-3 gap-4">
                <Stat
                  label="Cadencia"
                  value={
                    report.biomechanics.cadence_spm
                      ? `${report.biomechanics.cadence_spm}`
                      : "—"
                  }
                  unit="spm"
                  hint={evalCadence(
                    report.biomechanics.cadence_spm,
                    report.biomechanics.is_walk
                  )}
                />
                <Stat
                  label="Longitud zancada"
                  value={
                    report.biomechanics.stride_m
                      ? report.biomechanics.stride_m.toFixed(2)
                      : "—"
                  }
                  unit="m"
                />
                <Stat
                  label="GCT"
                  value={
                    report.biomechanics.gct_ms
                      ? `${report.biomechanics.gct_ms}`
                      : "—"
                  }
                  unit="ms"
                />
              </div>
            )}
          </Section>

          {/* 3. Corazón */}
          <Section number={3} title="Corazón">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Stat
                label="FC reposo"
                value={
                  report.heart.resting_hr ?? report.heart.resting_hr_baseline
                }
                unit="lpm"
                hint={
                  report.heart.resting_hr_delta != null
                    ? `${report.heart.resting_hr_delta > 0 ? "+" : ""}${report.heart.resting_hr_delta.toFixed(0)} vs baseline`
                    : `baseline ${report.heart.resting_hr_baseline}`
                }
              />
              <Stat
                label="HRV anoche"
                value={report.heart.hrv_last_night ?? "—"}
                unit="ms"
                hint={report.heart.hrv_state}
              />
              <Stat
                label="HRV baseline"
                value={
                  report.heart.hrv_baseline
                    ? report.heart.hrv_baseline.toFixed(0)
                    : "—"
                }
                unit="ms"
              />
              <Stat
                label="VO₂Max"
                value={report.heart.vo2max ?? "—"}
                unit="ml/kg/min"
                hint="meta sub 1:50 ≥ 52"
              />
            </div>
          </Section>

          {/* 4. Carga y recuperación */}
          <Section number={4} title="Carga y recuperación">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Stat
                label="Body Battery"
                value={
                  report.load.body_battery_max != null
                    ? `${report.load.body_battery_max} → ${report.load.body_battery_min}`
                    : "—"
                }
                unit=""
              />
              <Stat
                label="Stress medio"
                value={report.load.stress_avg ?? "—"}
                unit=""
              />
              <Stat
                label="ACWR"
                value={
                  report.load.acwr != null ? report.load.acwr.toFixed(2) : "—"
                }
                unit=""
                hint={`zona ${report.load.acwr_zone}`}
              />
              <Stat
                label="Sueño"
                value={
                  cronologia
                    ? `${Math.floor(cronologia.summary.sleep_duration_min / 60)}h ${cronologia.summary.sleep_duration_min % 60}m`
                    : "—"
                }
                unit=""
              />
            </div>
          </Section>

          {/* 5. Progreso vs plan */}
          <Section number={5} title="Progreso vs plan">
            <p className="text-sm text-ink-primary">
              <strong>Fase actual:</strong>{" "}
              <em>reconstrucción de base aeróbica</em> (polarizado 80/20). Z1-Z2
              prioritario, Z4 desbloquea cuando los gates abajo estén en verde.
            </p>
            <p className="text-sm text-ink-secondary mt-2">
              Meta: media maratón sub 1:50 — necesitas VO₂Max ~52-53 (actual{" "}
              {report.heart.vo2max ?? "—"}).
            </p>
          </Section>

          {/* 6. Gates */}
          <Section
            number={6}
            title={`Gates de progresión · ${greenGates}/4 en verde`}
          >
            <ul className="space-y-2">
              {report.gates.map((g, i) => (
                <li
                  key={i}
                  className="flex items-start gap-3 text-sm border-l-2 pl-3 py-1"
                  style={{ borderColor: GATE_COLOR[g.status] }}
                >
                  <span
                    className="label-uppercase mt-0.5"
                    style={{ color: GATE_COLOR[g.status] }}
                  >
                    {GATE_LABEL[g.status]}
                  </span>
                  <div className="flex-1">
                    <p className="text-ink-primary font-medium">{g.label}</p>
                    <p className="text-xs text-ink-tertiary mt-0.5">
                      {g.detail}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
            {greenGates === 4 ? (
              <p className="text-xs text-accent-brand mt-3 font-medium">
                ✓ Listo para empezar trote en intervalos 2′/3′ × 6.
              </p>
            ) : (
              <p className="text-xs text-ink-tertiary mt-3">
                Cuando los 4 gates estén verdes, próximo nivel: trote en
                intervalos 2′/3′ × 6.
              </p>
            )}
          </Section>

          {/* 7. Lectura del agente */}
          <Section number={7} title="Lectura del agente">
            <ul className="space-y-1.5">
              {report.interpretation.map((line, i) => (
                <li
                  key={i}
                  className="text-sm text-ink-primary leading-relaxed flex gap-2"
                >
                  <span className="text-accent-brand mt-1">•</span>
                  <span>{line}</span>
                </li>
              ))}
            </ul>
          </Section>

          <footer className="mt-10 pt-6 border-t border-rule/30">
            <p className="text-xs text-ink-tertiary text-center">
              Reporte generado a partir de tus datos reales de Garmin · sincronizado{" "}
              {report.date}
            </p>
          </footer>
        </div>
      </main>
    </div>
  );
}

function Section({
  number,
  title,
  children,
}: {
  number: number;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="card mt-4">
      <div className="flex items-baseline gap-2.5 mb-3 pb-2.5 border-b border-rule/40">
        <span className="text-2xl font-light text-accent-brand tabular-nums">
          {number.toString().padStart(2, "0")}
        </span>
        <h2 className="text-sm font-semibold text-ink-primary uppercase tracking-wide">
          {title}
        </h2>
      </div>
      {children}
    </section>
  );
}

function Stat({
  label,
  value,
  unit,
  hint,
}: {
  label: string;
  value: string | number;
  unit?: string;
  hint?: string;
}) {
  return (
    <div>
      <p className="label-uppercase">{label}</p>
      <p className="mt-1 flex items-baseline gap-1">
        <span className="text-2xl font-semibold tabular-nums text-ink-primary">
          {value}
        </span>
        {unit && <span className="text-xs text-ink-tertiary">{unit}</span>}
      </p>
      {hint && <p className="text-[11px] text-ink-tertiary mt-0.5">{hint}</p>}
    </div>
  );
}

function formatHour(h: number): string {
  const hh = Math.floor(h);
  const mm = Math.floor((h - hh) * 60);
  return `${hh.toString().padStart(2, "0")}:${mm.toString().padStart(2, "0")}`;
}

function evalCadence(cad: number | null, isWalk: boolean): string {
  if (!cad) return "—";
  if (isWalk) {
    if (cad >= 130) return "caminata enérgica ✓";
    if (cad >= 110) return "rango normal caminata";
    return "subir cadencia ayudaría";
  }
  if (cad < 165) return `${165 - cad} spm bajo objetivo 165-180`;
  if (cad > 180) return "sobre objetivo ✓";
  return "rango óptimo ✓";
}
