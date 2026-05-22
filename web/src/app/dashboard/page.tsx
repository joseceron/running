import { liebreApi } from "@/lib/api";
import { DashboardHeader } from "@/components/dashboard/Header";
import { GoalCard } from "@/components/dashboard/GoalCard";
import { ProfileCard } from "@/components/dashboard/ProfileCard";
import { HRVCard } from "@/components/dashboard/HRVCard";
import { WeeklyTable } from "@/components/dashboard/WeeklyTable";

// Forzar SSR siempre — datos en vivo
export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  let data;
  try {
    data = await liebreApi.dashboard();
  } catch (err) {
    return (
      <main className="min-h-screen flex items-center justify-center p-8">
        <div className="max-w-md text-center">
          <p className="text-sm uppercase tracking-widest text-signal mb-3">
            API no disponible
          </p>
          <p className="text-lg mb-4">No pude conectar con el backend de Liebre.</p>
          <p className="text-sm text-muted">
            Verifica que `uvicorn api.main:app --port 8080` esté corriendo y que
            el Postgres local esté arriba.
          </p>
          <p className="text-xs text-muted mt-3 font-mono">{String(err)}</p>
        </div>
      </main>
    );
  }

  const { profile, hrv, weekly, days_to_goal } = data;

  return (
    <main className="min-h-screen">
      <DashboardHeader name={profile.name} />

      <section className="px-8 py-8 max-w-6xl mx-auto">
        <div className="grid md:grid-cols-3 gap-5">
          <GoalCard profile={profile} daysToGoal={days_to_goal} />
          <ProfileCard profile={profile} />
          <div className="rounded-2xl border border-rule bg-paper-warm/40 p-6">
            <p className="text-xs uppercase tracking-widest text-muted mb-3">
              Próximos pasos
            </p>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start gap-3">
                <span className="text-accent-deep mt-1">▸</span>
                <span>Completar {hrv.days_required - hrv.days_recorded} noches más de HRV</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-accent-deep mt-1">▸</span>
                <span>Conectar Garmin con OAuth oficial (en roadmap)</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-accent-deep mt-1">▸</span>
                <span>Recibir reportes en WhatsApp (Fase 2)</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-5 mt-5">
          <HRVCard hrv={hrv} />
          <WeeklyTable weekly={weekly} />
        </div>

        <p className="text-xs text-muted mt-8 text-center">
          Datos en vivo desde Postgres · API en{" "}
          <code className="text-ink">localhost:8080</code> ·{" "}
          <a
            href="http://localhost:8080/docs"
            target="_blank"
            rel="noreferrer"
            className="underline hover:text-ink"
          >
            ver Swagger
          </a>
        </p>
      </section>
    </main>
  );
}
