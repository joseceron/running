import Link from "next/link";
import { liebreApi } from "@/lib/api";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { TopBar } from "@/components/dashboard/TopBar";
import { ActivityHeader } from "@/components/dashboard/ActivityHeader";
import { SyncedChartStack } from "@/components/dashboard/SyncedChartStack";
import { SplitsTable } from "@/components/dashboard/SplitsTable";

export const dynamic = "force-dynamic";

export default async function ActivityDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  let activity;
  try {
    activity = await liebreApi.activity(id);
  } catch (err) {
    return (
      <div className="min-h-screen bg-bg-page flex items-center justify-center p-8">
        <div className="card max-w-md text-center">
          <p className="label-uppercase" style={{ color: "var(--semantic-danger)" }}>
            Actividad no encontrada
          </p>
          <p className="text-sm text-ink-secondary mt-3">
            No pude cargar la actividad <code>{id}</code>.
          </p>
          <p className="text-xs text-ink-tertiary mt-2 font-mono">{String(err)}</p>
          <Link
            href="/dashboard"
            className="inline-block mt-4 text-accent-brand text-sm hover:underline"
          >
            ← Volver al dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-page">
      <Sidebar userName="José Luis Cerón" />
      <main
        className="min-h-screen"
        style={{ marginLeft: "var(--sidebar-width)" }}
      >
        <div className="max-w-6xl mx-auto px-8 py-8">
          <div className="mb-4">
            <Link
              href="/dashboard"
              className="text-xs text-ink-secondary hover:text-accent-brand"
            >
              ← Volver al dashboard
            </Link>
          </div>

          <TopBar
            userName="José Luis Cerón"
            title={`actividad · ${activity.name}`}
          />

          <section className="grid gap-4">
            <ActivityHeader activity={activity} />
            <SyncedChartStack samples={activity.samples} />
            <SplitsTable splits={activity.splits} />

            {/* Interpretación Liebre */}
            <div
              className="card"
              style={{
                background:
                  "radial-gradient(ellipse 60% 80% at 95% 5%, rgba(25,118,210,0.05) 0%, transparent 60%), #fff",
              }}
            >
              <div className="flex items-center gap-2.5 mb-3">
                <div className="w-8 h-8 rounded-full bg-accent-brand flex items-center justify-center text-white font-bold text-[13px]">
                  L
                </div>
                <div>
                  <span className="label-uppercase">Lectura Liebre</span>
                  <p className="text-[11px] text-ink-tertiary mt-0.5">
                    Análisis técnico de esta sesión
                  </p>
                </div>
              </div>
              <p className="text-sm text-ink-primary leading-relaxed">
                Esta carrera mantuvo {activity.zone_distribution_pct[1].toFixed(0)}% en Z2,
                que es exactamente la distribución polarizada que necesitas para
                construir base aeróbica. Tu cadencia media de {activity.avg_cadence} spm
                bajó por debajo del objetivo (170 spm) — pasaste por segmentos
                de caminata cuesta arriba que arrastraron el promedio. En los
                tramos efectivos de carrera (km 1, 4, 5) la cadencia estuvo entre
                144–160 spm, todavía mejorable con drills de skipping 3x/semana.
              </p>
              <p className="text-xs text-accent-brand mt-2 font-medium">
                📄 Kyröläinen et al. (2003) · Int J Sports Med · Observacional
              </p>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
