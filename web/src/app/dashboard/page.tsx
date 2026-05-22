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

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  let data;
  let diagnosis = null;
  let cronologia = null;
  try {
    [data, diagnosis, cronologia] = await Promise.all([
      liebreApi.dashboard(),
      liebreApi.diagnosis().catch((e) => {
        console.error("diagnosis fetch failed", e);
        return null;
      }),
      liebreApi.cronologia().catch((e) => {
        console.error("cronologia fetch failed", e);
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
          <TopBar userName={profile.name} title="resumen del día" />

          {/* DIAGNÓSTICO + META */}
          <section
            className="grid md:grid-cols-3 gap-4"
            style={{ gridAutoRows: "min-content" }}
          >
            <DiagnosticoDelDiaCard
              profile={profile}
              hrv={hrv}
              weekly={weekly}
              diagnosis={diagnosis}
            />
            <GoalCard profile={profile} daysToGoal={days_to_goal} />
          </section>

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
