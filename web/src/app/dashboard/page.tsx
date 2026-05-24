import { liebreApi } from "@/lib/api";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { TopBar } from "@/components/dashboard/TopBar";
import { GoalCard } from "@/components/dashboard/GoalCard";
import { ProfileCard } from "@/components/dashboard/ProfileCard";
import { HRVCard } from "@/components/dashboard/HRVCard";
import { WeeklyTable } from "@/components/dashboard/WeeklyTable";
import { DiagnosticoDelDiaCard } from "@/components/dashboard/DiagnosticoDelDiaCard";
import { FactorImpactList } from "@/components/dashboard/FactorImpactList";
import { UpcomingTrainingsCard } from "@/components/dashboard/UpcomingTrainingsCard";
import { Cronologia24h } from "@/components/dashboard/Cronologia24h";
import { InsightSection } from "@/components/dashboard/InsightCards";
import { TodayActionCard } from "@/components/dashboard/TodayActionCard";
import { NutritionCard } from "@/components/dashboard/NutritionCard";

export const dynamic = "force-dynamic";

type SearchParams = Promise<{ date?: string }>;

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const { date } = await searchParams;
  // Valida formato YYYY-MM-DD
  const safeDate =
    date && /^\d{4}-\d{2}-\d{2}$/.test(date) ? date : undefined;

  let data;
  let diagnosis = null;
  let cronologia = null;
  let report = null;
  try {
    [data, diagnosis, cronologia, report] = await Promise.all([
      liebreApi.dashboard(),
      liebreApi.diagnosis(safeDate).catch((e) => {
        console.error("diagnosis fetch failed", e);
        return null;
      }),
      liebreApi.cronologia(safeDate).catch((e) => {
        console.error("cronologia fetch failed", e);
        return null;
      }),
      liebreApi.report(safeDate).catch((e) => {
        console.error("report fetch failed", e);
        return null;
      }),
    ]);
  } catch (err) {
    return (
      <main className="min-h-screen flex items-center justify-center p-8 bg-bg-page">
        <div className="max-w-md text-center card">
          <p
            className="label-uppercase"
            style={{ color: "var(--semantic-danger)" }}
          >
            API no disponible
          </p>
          <p className="text-lg text-ink-primary my-3">
            No pude conectar con el backend.
          </p>
          <p className="text-xs text-ink-tertiary mt-3 font-mono">{String(err)}</p>
        </div>
      </main>
    );
  }

  const { profile, hrv, weekly, upcoming, days_to_goal } = data;
  const lastWeek = weekly.weeks[0] ?? null;

  return (
    <div className="min-h-screen bg-bg-page">
      <Sidebar userName={profile.name} />

      <main className="min-h-screen md:ml-[var(--sidebar-width)] pb-24 md:pb-0">
        <div className="max-w-6xl mx-auto px-4 md:px-8 py-6 md:py-8">
          <TopBar
            userName={profile.name}
            title="resumen del día"
            currentDate={safeDate}
          />

          {/* HOY: acción inequívoca + meta */}
          {report?.today_action && (
            <section className="grid md:grid-cols-3 gap-4 mb-4" style={{ gridAutoRows: "min-content" }}>
              <div className="md:col-span-2">
                <TodayActionCard action={report.today_action} />
              </div>
              <GoalCard profile={profile} daysToGoal={days_to_goal} />
            </section>
          )}

          {/* DIAGNÓSTICO (texto LLM cuando hay créditos) */}
          <section
            className="grid md:grid-cols-3 gap-4"
            style={{ gridAutoRows: "min-content" }}
          >
            <DiagnosticoDelDiaCard
              profile={profile}
              hrv={hrv}
              weekly={weekly}
              diagnosis={diagnosis}
              todayActionShown={!!report?.today_action}
            />
            {!report?.today_action && (
              <GoalCard profile={profile} daysToGoal={days_to_goal} />
            )}
          </section>

          {/* INSIGHTS CIENTÍFICOS — diferencial Liebre */}
          {report?.insights && <InsightSection insights={report.insights} />}

          {/* NUTRICIÓN — pilar diferencial + base para monetización Luz Dálida */}
          {report?.nutrition && <NutritionCard data={report.nutrition} />}

          {/* HRV + Perfil */}
          <section className="grid md:grid-cols-3 gap-4 mt-4">
            <HRVCard hrv={hrv} />
            <ProfileCard profile={profile} />
          </section>

          {/* Cronología 24h */}
          {cronologia && (
            <section className="grid grid-cols-1 gap-4 mt-4">
              <Cronologia24h cronologia={cronologia} />
            </section>
          )}

          {/* Próximos entrenos */}
          <section className="grid grid-cols-1 gap-4 mt-4">
            <UpcomingTrainingsCard upcoming={upcoming} />
          </section>

          {/* Factores + Semanal */}
          <section className="grid md:grid-cols-2 gap-4 mt-4">
            <FactorImpactList
              hrv={{
                latest_value: hrv.latest_value,
                baseline_ms: hrv.baseline_ms,
              }}
              weekly={{
                acwr: lastWeek?.acwr ?? null,
                executed_km: lastWeek?.executed_km ?? null,
              }}
            />
            <WeeklyTable weekly={weekly} />
          </section>

          <footer className="mt-10 pt-6 border-t border-rule/30">
            <p className="text-xs text-ink-tertiary text-center">
              Datos en vivo desde Garmin · diseño basado en Connect + capa Liebre
            </p>
          </footer>
        </div>
      </main>
    </div>
  );
}
