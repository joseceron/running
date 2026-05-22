import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col">
      <nav className="px-8 py-6 flex items-center justify-between border-b border-rule/60">
        <Link href="/" className="wordmark text-2xl">
          liebre<span className="dot">.</span>
        </Link>
        <Link
          href="/dashboard"
          className="text-sm px-5 py-2.5 rounded-full bg-ink text-paper hover:bg-ink-soft transition"
        >
          Ir al dashboard →
        </Link>
      </nav>

      <section className="flex-1 px-8 py-20 max-w-5xl mx-auto w-full">
        <p className="text-sm uppercase tracking-widest text-muted mb-6">
          La liebre es quien marca el paso
        </p>
        <h1 className="text-5xl md:text-7xl wordmark leading-[1.05] mb-8">
          Corre seguro con
          <br />
          <span className="text-accent-deep italic">inteligencia artificial</span>
          <br />y ciencia real.
        </h1>
        <p className="text-lg text-muted max-w-2xl mb-10 leading-relaxed">
          Liebre analiza tus datos reales de Garmin (HRV, biomecánica, carga) y los
          combina con literatura científica de Scopus y Web of Science. Cada
          recomendación viene respaldada por papers citados, no por rangos
          poblacionales que no aplican para tu caso.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link
            href="/dashboard"
            className="px-7 py-4 rounded-full bg-ink text-paper hover:bg-ink-soft transition text-sm font-medium"
          >
            Ver mi dashboard
          </Link>
          <a
            href="http://localhost:8080/docs"
            target="_blank"
            rel="noreferrer"
            className="px-7 py-4 rounded-full border border-rule hover:border-ink transition text-sm font-medium"
          >
            Explorar la API
          </a>
        </div>

        <div className="mt-20 grid md:grid-cols-3 gap-6 text-sm">
          <div className="p-6 rounded-2xl border border-rule bg-paper-warm/40">
            <p className="text-xs uppercase tracking-widest text-muted mb-2">
              Baseline propio
            </p>
            <p>
              Tu HRV de referencia se construye con tus 14 noches, no con
              promedios poblacionales.
            </p>
          </div>
          <div className="p-6 rounded-2xl border border-rule bg-paper-warm/40">
            <p className="text-xs uppercase tracking-widest text-muted mb-2">
              Evidencia citada
            </p>
            <p>
              Cada alerta o recomendación trae el paper que la sustenta — RCT,
              meta-análisis, observacional — con autor, año y DOI.
            </p>
          </div>
          <div className="p-6 rounded-2xl border border-rule bg-paper-warm/40">
            <p className="text-xs uppercase tracking-widest text-muted mb-2">
              Multi-canal
            </p>
            <p>
              Dashboard web, WhatsApp 24/7 y reporte matutino automático. Tú
              eliges cómo te llega.
            </p>
          </div>
        </div>
      </section>

      <footer className="px-8 py-8 border-t border-rule/60 text-xs text-muted flex flex-wrap items-center justify-between gap-3">
        <p>
          © {new Date().getFullYear()} Liebre · No reemplaza al médico
          deportivo
        </p>
        <p>Hecho con datos reales de Garmin + Claude + papers de Scopus/WoS</p>
      </footer>
    </main>
  );
}
