import Link from "next/link";
import {
  COMPARISON,
  HERO_STATS,
  MODULES,
  PAIN_POINTS,
  PLANS,
  REAL_DATA_CARDS,
  fmtCOP,
} from "@/lib/landing-data";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-bg-page text-ink-primary">
      {/* ─────────────── NAV ─────────────── */}
      <nav className="sticky top-0 z-30 bg-bg-page/95 backdrop-blur border-b border-rule/60">
        <div className="max-w-6xl mx-auto px-4 md:px-8 py-3 flex items-center justify-between">
          <Link href="/" className="wordmark text-2xl md:text-3xl">
            liebre<span className="dot">.</span>
          </Link>
          <div className="flex items-center gap-2 md:gap-3">
            <a
              href="#modulos"
              className="hidden sm:inline text-sm text-ink-secondary hover:text-ink-primary px-3 py-1.5"
            >
              Módulos
            </a>
            <a
              href="#comparativa"
              className="hidden sm:inline text-sm text-ink-secondary hover:text-ink-primary px-3 py-1.5"
            >
              vs Connect
            </a>
            <a
              href="#planes"
              className="hidden sm:inline text-sm text-ink-secondary hover:text-ink-primary px-3 py-1.5"
            >
              Planes
            </a>
            <Link
              href="/dashboard"
              className="text-sm font-semibold px-4 py-2 rounded-md bg-accent-brand text-white hover:opacity-90 transition"
            >
              Entrar
            </Link>
          </div>
        </div>
      </nav>

      {/* ─────────────── HERO ─────────────── */}
      <section className="relative overflow-hidden">
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "radial-gradient(ellipse 80% 60% at 50% 0%, rgba(25,118,210,0.10) 0%, transparent 70%)",
          }}
        />
        <div className="max-w-5xl mx-auto px-4 md:px-8 py-16 md:py-28 text-center relative">
          <div className="flex flex-wrap items-center justify-center gap-2 mb-6">
            <span
              className="inline-block text-[11px] uppercase tracking-[0.2em] font-semibold px-3 py-1 rounded-full"
              style={{
                background:
                  "color-mix(in srgb, var(--accent-brand) 12%, transparent)",
                color: "var(--accent-brand)",
              }}
            >
              Inteligencia artificial para corredores
            </span>
            <span
              className="inline-flex items-center gap-1.5 text-[11px] font-medium px-3 py-1 rounded-full"
              style={{
                background:
                  "color-mix(in srgb, var(--semantic-positive) 10%, transparent)",
                color: "var(--semantic-positive)",
              }}
            >
              <span>⌚</span> Sincroniza con Garmin
            </span>
          </div>
          <h1 className="wordmark text-4xl md:text-6xl lg:text-7xl leading-[1.05] max-w-3xl mx-auto mb-5">
            Lo que Garmin <span className="text-ink-tertiary">ve</span>.
            <br />
            Lo que un entrenador{" "}
            <span className="text-accent-brand italic">entiende</span>.
          </h1>
          <p className="text-base md:text-lg text-ink-secondary max-w-2xl mx-auto leading-relaxed mb-8 md:mb-10">
            Garmin registra tus datos. Liebre los interpreta con evidencia
            científica, construye tu perfil fisiológico personal y detecta lo
            que el app nunca te va a decir.
          </p>
          <div className="flex flex-wrap gap-3 justify-center mb-12 md:mb-16">
            <Link
              href="/dashboard"
              className="px-6 py-3 rounded-md bg-accent-brand text-white font-semibold text-sm hover:opacity-90 transition"
            >
              Ver demo del dashboard
            </Link>
            <a
              href="#comparativa"
              className="px-6 py-3 rounded-md border border-rule text-sm font-semibold hover:border-ink-primary transition"
            >
              Comparar con Connect
            </a>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-10 max-w-3xl mx-auto">
            {HERO_STATS.map((s) => (
              <div key={s.label} className="text-center">
                <p className="metric-display text-3xl md:text-4xl text-ink-primary mb-1">
                  {s.value}
                </p>
                <p className="text-[11px] text-ink-tertiary leading-snug">
                  {s.label}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─────────────── EL PROBLEMA ─────────────── */}
      <section className="border-t border-rule/60 bg-bg-content">
        <div className="max-w-6xl mx-auto px-4 md:px-8 py-16 md:py-24">
          <div className="text-center mb-10 md:mb-14">
            <p className="label-uppercase mb-3">El problema</p>
            <h2 className="text-2xl md:text-4xl wordmark text-ink-primary leading-tight max-w-2xl mx-auto">
              Garmin te dice <span className="text-ink-tertiary">qué</span>{" "}
              entrenar.
              <br />
              Nadie te dice{" "}
              <span className="text-accent-brand italic">por qué</span> estás en
              riesgo.
            </h2>
          </div>

          <div className="grid md:grid-cols-2 gap-4 md:gap-5 max-w-5xl mx-auto">
            {PAIN_POINTS.map((p) => (
              <article
                key={p.title}
                className="card flex gap-4"
                style={{ padding: "20px 22px" }}
              >
                <div className="text-2xl shrink-0">{p.icon}</div>
                <div>
                  <h3 className="text-sm font-semibold text-ink-primary mb-1.5">
                    {p.title}
                  </h3>
                  <p className="text-[13px] text-ink-secondary leading-relaxed">
                    {p.body}
                  </p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ─────────────── COMPARATIVA ─────────────── */}
      <section
        id="comparativa"
        className="border-t border-rule/60"
        style={{ background: "var(--bg-card-subtle)" }}
      >
        <div className="max-w-5xl mx-auto px-4 md:px-8 py-16 md:py-24">
          <div className="text-center mb-10 md:mb-14">
            <p className="label-uppercase mb-3">Comparativa</p>
            <h2 className="text-2xl md:text-4xl wordmark text-ink-primary leading-tight">
              Liebre vs Garmin Connect+
            </h2>
            <p className="text-sm text-ink-secondary mt-3 max-w-xl mx-auto">
              Garmin Connect+ cuesta $8.99 USD/mes. Esta es la diferencia en lo
              que realmente importa para rendimiento y prevención.
            </p>
          </div>

          <div className="card p-0 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr
                    className="border-b border-rule/60"
                    style={{ background: "var(--bg-card-subtle)" }}
                  >
                    <th className="text-left px-4 py-3 label-uppercase font-medium">
                      Capacidad
                    </th>
                    <th className="text-left px-4 py-3 label-uppercase font-medium">
                      Connect+ · $8.99/mes
                    </th>
                    <th className="text-left px-4 py-3 label-uppercase font-medium text-accent-brand">
                      Liebre
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {COMPARISON.map((row, i) => (
                    <tr
                      key={row.capability}
                      className="border-b border-rule/30 last:border-0"
                      style={{
                        background:
                          i % 2 === 0 ? "transparent" : "var(--bg-card-subtle)",
                      }}
                    >
                      <td className="px-4 py-3 font-medium text-ink-primary">
                        {row.capability}
                      </td>
                      <td className="px-4 py-3 text-ink-tertiary">
                        <span className="inline-flex items-center gap-1">
                          {row.connect.includes("No") ||
                          row.connect.includes("disp") ||
                          row.connect === "Sin citas" ||
                          row.connect === "No existe" ? (
                            <span className="text-danger">✗</span>
                          ) : (
                            <span className="text-warning">~</span>
                          )}
                          {row.connect}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-ink-primary font-medium">
                        <span className="inline-flex items-center gap-1">
                          <span className="text-positive">✓</span>
                          {row.liebre}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* ─────────────── 8 MÓDULOS ─────────────── */}
      <section id="modulos" className="border-t border-rule/60 bg-bg-content">
        <div className="max-w-6xl mx-auto px-4 md:px-8 py-16 md:py-24">
          <div className="text-center mb-10 md:mb-14">
            <p className="label-uppercase mb-3">Módulos especializados</p>
            <h2 className="text-2xl md:text-4xl wordmark text-ink-primary leading-tight max-w-2xl mx-auto">
              8 reportes que{" "}
              <span className="text-accent-brand italic">Connect no tiene</span>
            </h2>
            <p className="text-sm text-ink-secondary mt-3 max-w-2xl mx-auto leading-relaxed">
              Cada módulo cruza tus datos reales de Garmin con literatura
              científica actualizada (Scopus + Web of Science) para generar
              recomendaciones con nombre y apellido.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-4 md:gap-5">
            {MODULES.map((m) => (
              <article key={m.n} className="card flex flex-col">
                <div className="flex items-baseline gap-3 mb-3">
                  <span
                    className="text-xs font-bold px-2 py-1 rounded shrink-0"
                    style={{
                      background:
                        "color-mix(in srgb, var(--accent-brand) 12%, transparent)",
                      color: "var(--accent-brand)",
                    }}
                  >
                    MÓDULO {m.n.toString().padStart(2, "0")}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-ink-primary leading-tight mb-2">
                  {m.title}
                </h3>
                <p className="text-[13px] text-ink-secondary leading-relaxed mb-4">
                  {m.description}
                </p>

                <ul className="space-y-1.5 mb-4 flex-1">
                  {m.bullets.map((b) => (
                    <li
                      key={b}
                      className="text-[12px] text-ink-secondary flex gap-2"
                    >
                      <span className="text-accent-brand shrink-0">▸</span>
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>

                <div
                  className="rounded-md px-3 py-2 mb-3 text-[12px]"
                  style={{
                    background:
                      "color-mix(in srgb, var(--semantic-positive) 8%, transparent)",
                    color: "var(--semantic-positive)",
                  }}
                >
                  <span className="font-semibold">✓ Dato real: </span>
                  {m.realData}
                </div>

                <div className="border-t border-rule/40 pt-3 space-y-2">
                  <p className="label-uppercase">Evidencia científica</p>
                  {m.evidence.map((e, i) => (
                    <div key={i} className="text-[11px]">
                      <p className="font-medium text-ink-primary">
                        <span
                          style={{ color: "var(--semantic-warning)" }}
                          aria-label={`Nivel ${e.level}`}
                        >
                          {"★".repeat(e.level)}
                        </span>{" "}
                        {e.cite}
                      </p>
                      <p className="text-ink-tertiary leading-snug">
                        {e.finding}
                      </p>
                    </div>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ─────────────── DATOS REALES ─────────────── */}
      <section
        className="border-t border-rule/60"
        style={{ background: "var(--bg-card-subtle)" }}
      >
        <div className="max-w-6xl mx-auto px-4 md:px-8 py-16 md:py-24">
          <div className="text-center mb-10">
            <p className="label-uppercase mb-3">Datos reales · José Luis Cerón</p>
            <h2 className="text-2xl md:text-4xl wordmark text-ink-primary leading-tight max-w-2xl mx-auto">
              Lo que el análisis descubrió{" "}
              <span className="italic text-accent-brand">en la primera semana</span>
            </h2>
            <p className="text-sm text-ink-secondary mt-3 max-w-xl mx-auto">
              No simulaciones. Datos reales descargados de Garmin, analizados con
              el sistema activo.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-4 md:gap-5">
            {REAL_DATA_CARDS.map((c) => (
              <article key={c.headline} className="card">
                <p className="label-uppercase mb-3">{c.tag}</p>
                <p className="metric-display text-5xl md:text-6xl text-accent-brand leading-none">
                  {c.headline}
                </p>
                <p className="text-sm font-semibold text-ink-primary mt-2 mb-3">
                  {c.sub}
                </p>
                <p className="text-[13px] text-ink-secondary leading-relaxed">
                  {c.body}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ─────────────── PLANES ─────────────── */}
      <section id="planes" className="border-t border-rule/60 bg-bg-content">
        <div className="max-w-5xl mx-auto px-4 md:px-8 py-16 md:py-24">
          <div className="text-center mb-10">
            <p className="label-uppercase mb-3">Planes</p>
            <h2 className="text-2xl md:text-4xl wordmark text-ink-primary leading-tight">
              Comparado con lo que ya pagas
            </h2>
            <p className="text-sm text-ink-secondary mt-3 max-w-xl mx-auto">
              Versus Garmin Connect+ ($8.99/mes) o un entrenador personal
              ($150–400/mes).
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-4 md:gap-5">
            {PLANS.map((p) => {
              const isRecommended = p.badge === "Recomendado";
              return (
                <article
                  key={p.tier}
                  className={isRecommended ? "card-dark relative" : "card relative"}
                  style={{
                    ...(isRecommended
                      ? {}
                      : { border: "1px solid var(--rule)" }),
                  }}
                >
                  {p.badge && (
                    <span
                      className="absolute -top-3 right-5 text-[10px] font-bold px-3 py-1 rounded-full"
                      style={{
                        background: "var(--accent-brand)",
                        color: "white",
                        letterSpacing: "0.05em",
                      }}
                    >
                      {p.badge.toUpperCase()}
                    </span>
                  )}
                  <p
                    className="label-uppercase mb-2"
                    style={
                      isRecommended ? { color: "rgba(255,255,255,0.5)" } : undefined
                    }
                  >
                    Liebre {p.tier}
                  </p>
                  <div>
                    <p
                      className="metric-display text-5xl leading-none"
                      style={{
                        color: isRecommended ? "#ffffff" : "var(--ink-primary)",
                      }}
                    >
                      ${p.price}
                      <span
                        className="text-base font-normal ml-1"
                        style={{
                          color: isRecommended
                            ? "rgba(255,255,255,0.6)"
                            : "var(--ink-tertiary)",
                        }}
                      >
                        USD/mes
                      </span>
                    </p>
                    <p
                      className="text-[13px] mt-2 tnum"
                      style={{
                        color: isRecommended
                          ? "rgba(255,255,255,0.65)"
                          : "var(--ink-secondary)",
                      }}
                    >
                      {fmtCOP(p.price)}{" "}
                      <span
                        style={{
                          color: isRecommended
                            ? "rgba(255,255,255,0.4)"
                            : "var(--ink-tertiary)",
                        }}
                      >
                        COP/mes aprox · tasa referencial
                      </span>
                    </p>
                  </div>
                  <ul
                    className="space-y-2 mt-6 mb-6 text-sm"
                    style={
                      isRecommended
                        ? { color: "rgba(255,255,255,0.85)" }
                        : { color: "var(--ink-secondary)" }
                    }
                  >
                    {p.features.map((f) => (
                      <li key={f} className="flex gap-2">
                        <span
                          className="shrink-0"
                          style={{
                            color: isRecommended
                              ? "var(--accent-brand-soft)"
                              : "var(--semantic-positive)",
                          }}
                        >
                          ✓
                        </span>
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                  <Link
                    href="/dashboard"
                    className={`block text-center px-4 py-3 rounded-md font-semibold text-sm transition ${
                      isRecommended
                        ? "bg-accent-brand-soft text-white hover:bg-accent-brand"
                        : "bg-ink-primary text-white hover:bg-black"
                    }`}
                    style={
                      isRecommended ? { background: "var(--accent-brand-soft)" } : {}
                    }
                  >
                    Probar gratis
                  </Link>
                  <p
                    className="text-[11px] mt-4 leading-snug"
                    style={
                      isRecommended
                        ? { color: "rgba(255,255,255,0.55)" }
                        : { color: "var(--ink-tertiary)" }
                    }
                  >
                    {p.footnote}
                  </p>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      {/* ─────────────── CTA FINAL ─────────────── */}
      <section className="border-t border-rule/60 bg-bg-content">
        <div className="max-w-3xl mx-auto px-4 md:px-8 py-16 md:py-20 text-center">
          <h2 className="text-2xl md:text-4xl wordmark text-ink-primary leading-tight mb-4">
            Conoce <span className="italic text-accent-brand">tu</span> respuesta
            fisiológica antes de la próxima carrera
          </h2>
          <p className="text-sm md:text-base text-ink-secondary leading-relaxed mb-7 max-w-xl mx-auto">
            Liebre se conecta a tu Garmin, construye tu perfil en 14 noches y
            empieza a ajustar tu plan con los datos que tu cuerpo realmente da —
            no con promedios poblacionales.
          </p>
          <Link
            href="/dashboard"
            className="inline-block px-7 py-3 rounded-md bg-accent-brand text-white font-semibold text-sm hover:opacity-90 transition"
          >
            Entrar al dashboard
          </Link>
        </div>
      </section>

      {/* ─────────────── FOOTER ─────────────── */}
      <footer
        className="border-t border-rule/60"
        style={{ background: "var(--bg-sidebar)", color: "var(--ink-on-dark)" }}
      >
        <div className="max-w-6xl mx-auto px-4 md:px-8 py-10 md:py-14">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <p className="wordmark text-2xl mb-2">
                liebre<span style={{ color: "var(--accent-brand-soft)" }}>.</span>
              </p>
              <p
                className="text-xs leading-relaxed"
                style={{ color: "rgba(255,255,255,0.6)" }}
              >
                Tu pacer con inteligencia artificial y ciencia validada.
                <br />
                Construido para corredores que quieren entender, no solo medir.
              </p>
            </div>
            <div>
              <p
                className="label-uppercase mb-3"
                style={{ color: "rgba(255,255,255,0.5)" }}
              >
                Producto
              </p>
              <ul className="space-y-1.5 text-sm">
                <li>
                  <a
                    href="#modulos"
                    style={{ color: "rgba(255,255,255,0.75)" }}
                    className="hover:opacity-100"
                  >
                    Módulos
                  </a>
                </li>
                <li>
                  <a
                    href="#comparativa"
                    style={{ color: "rgba(255,255,255,0.75)" }}
                  >
                    vs Garmin Connect
                  </a>
                </li>
                <li>
                  <a
                    href="#planes"
                    style={{ color: "rgba(255,255,255,0.75)" }}
                  >
                    Planes
                  </a>
                </li>
                <li>
                  <Link
                    href="/dashboard"
                    style={{ color: "rgba(255,255,255,0.75)" }}
                  >
                    Demo del dashboard
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <p
                className="label-uppercase mb-3"
                style={{ color: "rgba(255,255,255,0.5)" }}
              >
                Tecnología
              </p>
              <ul
                className="space-y-1.5 text-xs"
                style={{ color: "rgba(255,255,255,0.6)" }}
              >
                <li>Powered by Anthropic Claude</li>
                <li>Datos: Garmin Connect</li>
                <li>Evidencia: Scopus + Web of Science</li>
              </ul>
            </div>
          </div>
          <div
            className="mt-10 pt-6 border-t flex flex-col md:flex-row gap-3 items-start md:items-center justify-between text-[11px]"
            style={{
              borderColor: "rgba(255,255,255,0.08)",
              color: "rgba(255,255,255,0.45)",
            }}
          >
            <p>© {new Date().getFullYear()} Liebre. Todos los derechos reservados.</p>
            <p className="max-w-md md:text-right">
              Los reportes son informativos y complementan — no reemplazan — la
              evaluación de un médico deportivo o fisioterapeuta.
            </p>
          </div>
        </div>
      </footer>
    </main>
  );
}
