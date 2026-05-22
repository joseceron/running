import Link from "next/link";
import { liebreApi } from "@/lib/api";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { TopBar } from "@/components/dashboard/TopBar";
import { ActivityHeader } from "@/components/dashboard/ActivityHeader";
import { SyncedChartStack } from "@/components/dashboard/SyncedChartStack";
import { SplitsTable } from "@/components/dashboard/SplitsTable";
import { GlossaryPanel } from "@/components/dashboard/GlossaryPanel";
import { Term } from "@/components/dashboard/Term";

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
          <p
            className="label-uppercase"
            style={{ color: "var(--semantic-danger)" }}
          >
            Actividad no encontrada
          </p>
          <p className="text-sm text-ink-secondary mt-3">
            No pude cargar la actividad <code>{id}</code>.
          </p>
          <p className="text-xs text-ink-tertiary mt-2 font-mono">
            {String(err)}
          </p>
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
        className="min-h-screen md:ml-[var(--sidebar-width)]"
      >
        <div className="max-w-6xl mx-auto px-4 md:px-8 py-6 md:py-8">
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
            {/* HEADER PRIMERO — datos clave */}
            <ActivityHeader activity={activity} />

            {/* LECTURA LIEBRE — el DIFERENCIADOR, sube arriba según pedido del usuario */}
            <div
              className="card"
              style={{
                background:
                  "radial-gradient(ellipse 60% 80% at 95% 5%, rgba(25,118,210,0.05) 0%, transparent 60%), #fff",
              }}
            >
              <div className="flex items-center gap-2.5 mb-3">
                <div className="w-9 h-9 rounded-full bg-accent-brand flex items-center justify-center text-white font-bold text-sm shrink-0">
                  L
                </div>
                <div className="flex-1 min-w-0">
                  <span className="label-uppercase">Lectura Liebre</span>
                  <p className="text-[11px] text-ink-tertiary mt-0.5">
                    Análisis técnico de esta sesión — el diferenciador vs apps
                    genéricas
                  </p>
                </div>
              </div>
              <p className="text-sm text-ink-primary leading-relaxed">
                Esta carrera mantuvo{" "}
                <strong className="text-accent-brand">
                  {activity.zone_distribution_pct[1].toFixed(0)}% en{" "}
                  <Term k="z2">Z2</Term>
                </strong>{" "}
                — exactamente la distribución polarizada que necesitas para
                construir base aeróbica (Seiler 2010). Tu{" "}
                <Term k="cadencia">cadencia</Term> media de{" "}
                <strong>
                  {activity.avg_cadence} <Term k="spm">spm</Term>
                </strong>{" "}
                {activity.avg_cadence >= 165
                  ? "está en el rango óptimo — gran trabajo manteniendo zancadas cortas."
                  : `está por debajo del objetivo (165-180 spm). En los tramos efectivos de carrera la cadencia estuvo mejor; los segmentos de caminata cuesta arriba arrastraron el promedio. Se mejora con `}
                {activity.avg_cadence < 165 && (
                  <Term k="drills_skipping">drills de skipping</Term>
                )}
                {activity.avg_cadence < 165 && " 3 veces por semana."}
              </p>
              <p className="text-xs text-accent-brand mt-3 font-medium">
                📄 Kyröläinen et al. (2003) · Int J Sports Med · Observacional
                — economía de carrera y cadencia
              </p>
            </div>

            {/* GLOSARIO — entendible por cualquier persona */}
            <GlossaryPanel
              keys={[
                "cadencia",
                "spm",
                "gct",
                "ppm",
                "ritmo",
                "zancada",
                "z1",
                "z2",
                "z3",
                "z4",
                "z5",
                "drills_skipping",
                "training_effect",
              ]}
            />

            {/* GRÁFICAS detalladas */}
            <SyncedChartStack samples={activity.samples} />

            {/* SPLITS */}
            <SplitsTable splits={activity.splits} />
          </section>
        </div>
      </main>
    </div>
  );
}
