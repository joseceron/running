import Link from "next/link";
import {
  COMPARISON,
  HERO_STATS,
  MODULES,
  PAIN_POINTS,
  PLANS,
  REAL_DATA_CARDS,
  fmtCOP,
  moduleAccent,
} from "@/lib/landing-data";

/* ════════════════════════════════════════════════════════════════
   PALETA — tema oscuro tipo GitHub, basado en propuesta_producto.html
   ════════════════════════════════════════════════════════════════ */
const C = {
  bg: "#080c10",
  surface: "#0d1117",
  surface2: "#161b22",
  surface3: "#21262d",
  border: "#30363d",
  borderSoft: "#21262d",
  text: "#e6edf3",
  textMuted: "#8b949e",
  textDim: "#484f58",
  accent: "#2f81f7",
  accentSoft: "rgba(31,111,235,0.16)",
  green: "#3fb950",
  yellow: "#e3b341",
  red: "#ff7b72",
};

export default function HomePage() {
  return (
    <main
      style={{
        background: C.bg,
        color: C.text,
        minHeight: "100vh",
        fontFamily:
          "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, sans-serif",
      }}
    >
      {/* ─────────────── NAV ─────────────── */}
      <nav
        style={{
          position: "sticky",
          top: 0,
          zIndex: 30,
          background: "rgba(8,12,16,0.85)",
          backdropFilter: "blur(12px)",
          borderBottom: `1px solid ${C.border}`,
        }}
      >
        <div className="max-w-6xl mx-auto px-4 md:px-8 py-3.5 flex items-center justify-between">
          <Link
            href="/"
            className="wordmark text-2xl md:text-3xl"
            style={{ color: C.text }}
          >
            liebre
            <span style={{ color: C.accent }}>.</span>
          </Link>
          <div className="flex items-center gap-1 md:gap-2">
            <NavLink href="#modulos">Módulos</NavLink>
            <NavLink href="#comparativa">vs Connect</NavLink>
            <NavLink href="#planes">Planes</NavLink>
            <Link
              href="/dashboard"
              className="text-sm font-semibold ml-2 px-4 py-2 rounded-md transition-opacity hover:opacity-90"
              style={{ background: C.accent, color: "#fff" }}
            >
              Entrar
            </Link>
          </div>
        </div>
      </nav>

      {/* ─────────────── HERO ─────────────── */}
      <section
        style={{
          position: "relative",
          overflow: "hidden",
          background: `radial-gradient(ellipse 80% 60% at 50% 0%, #0d2044 0%, ${C.bg} 70%)`,
        }}
      >
        {/* Grid pattern animado */}
        <div
          className="liebre-grid-bg"
          style={{
            position: "absolute",
            inset: 0,
            opacity: 0.45,
            pointerEvents: "none",
          }}
        />

        {/* Orbs flotantes (gradient blobs con blur) */}
        <div
          className="liebre-orb"
          style={{
            width: 480,
            height: 480,
            top: "-180px",
            left: "10%",
            background: "radial-gradient(circle, #2f81f7 0%, transparent 65%)",
            opacity: 0.35,
            animationDelay: "0s",
          }}
        />
        <div
          className="liebre-orb"
          style={{
            width: 380,
            height: 380,
            top: "60px",
            right: "8%",
            background: "radial-gradient(circle, #a5a0ff 0%, transparent 65%)",
            opacity: 0.28,
            animationDelay: "-7s",
          }}
        />
        <div
          className="liebre-orb"
          style={{
            width: 320,
            height: 320,
            bottom: "-120px",
            left: "30%",
            background: "radial-gradient(circle, #3fb950 0%, transparent 65%)",
            opacity: 0.22,
            animationDelay: "-13s",
          }}
        />

        {/* Sparkles aleatorios */}
        {[
          { top: "12%", left: "18%", delay: "0s" },
          { top: "22%", left: "82%", delay: "1.2s" },
          { top: "55%", left: "12%", delay: "2.4s" },
          { top: "68%", left: "88%", delay: "0.8s" },
          { top: "38%", left: "92%", delay: "3.1s" },
          { top: "82%", left: "25%", delay: "1.8s" },
          { top: "16%", left: "55%", delay: "2.6s" },
          { top: "78%", left: "65%", delay: "0.4s" },
        ].map((s, i) => (
          <span
            key={i}
            className="liebre-sparkle"
            style={{
              top: s.top,
              left: s.left,
              animationDelay: s.delay,
              boxShadow: "0 0 8px rgba(121, 192, 255, 0.8)",
            }}
          />
        ))}

        <div className="max-w-5xl mx-auto px-4 md:px-8 py-20 md:py-32 text-center relative">
          <div className="flex flex-wrap items-center justify-center gap-2 mb-6">
            <span
              style={{
                display: "inline-block",
                fontSize: 11,
                textTransform: "uppercase",
                letterSpacing: "0.2em",
                color: C.accent,
                background: C.accentSoft,
                border: `1px solid rgba(47,129,247,0.27)`,
                padding: "5px 14px",
                borderRadius: 20,
                fontWeight: 600,
              }}
            >
              Inteligencia artificial para corredores
            </span>
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                fontSize: 11,
                fontWeight: 600,
                color: C.green,
                background: "rgba(63,185,80,0.12)",
                border: "1px solid rgba(63,185,80,0.32)",
                padding: "5px 12px",
                borderRadius: 20,
              }}
            >
              ⌚ Sincroniza con Garmin
            </span>
          </div>

          <h1
            style={{
              fontSize: "clamp(40px, 6.5vw, 72px)",
              fontWeight: 800,
              lineHeight: 1.06,
              letterSpacing: "-0.02em",
              maxWidth: 880,
              margin: "0 auto 24px",
              background: `linear-gradient(135deg, ${C.text} 30%, ${C.accent} 100%)`,
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
            }}
          >
            Lo que Garmin ve.
            <br />
            Lo que un entrenador entiende.
          </h1>

          <p
            style={{
              fontSize: 18,
              color: C.textMuted,
              maxWidth: 620,
              margin: "0 auto 40px",
              lineHeight: 1.65,
            }}
          >
            Garmin registra tus datos. Liebre los interpreta con evidencia
            científica, construye tu perfil fisiológico personal y detecta lo
            que el app nunca te va a decir.
          </p>

          <div className="flex flex-wrap gap-3 justify-center mb-16">
            <Link
              href="/dashboard"
              className="liebre-shimmer liebre-lift"
              style={{
                background: C.accent,
                color: "#fff",
                fontWeight: 700,
                fontSize: 14,
                padding: "13px 28px",
                borderRadius: 8,
                textDecoration: "none",
                display: "inline-block",
                boxShadow: "0 4px 14px rgba(47,129,247,0.4)",
              }}
            >
              Ver demo del dashboard →
            </Link>
            <a
              href="#comparativa"
              className="liebre-lift"
              style={{
                background: "rgba(13,17,23,0.6)",
                backdropFilter: "blur(8px)",
                color: C.text,
                fontWeight: 600,
                fontSize: 14,
                padding: "13px 28px",
                borderRadius: 8,
                border: `1px solid ${C.border}`,
                textDecoration: "none",
                display: "inline-block",
              }}
            >
              Comparar con Connect
            </a>
          </div>

          {/* Stats con reveal animado */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-10 max-w-3xl mx-auto">
            {HERO_STATS.map((s, i) => (
              <div
                key={s.label}
                className="text-center liebre-reveal"
                style={{ animationDelay: `${0.1 + i * 0.12}s` }}
              >
                <p
                  className="liebre-stat-num"
                  style={{
                    fontSize: 42,
                    fontWeight: 800,
                    fontVariantNumeric: "tabular-nums",
                    letterSpacing: "-0.02em",
                  }}
                >
                  {s.value}
                </p>
                <p
                  style={{
                    fontSize: 12,
                    color: C.textMuted,
                    marginTop: 6,
                    lineHeight: 1.4,
                  }}
                >
                  {s.label}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─────────────── EL PROBLEMA ─────────────── */}
      <section
        style={{
          background: C.surface,
          borderTop: `1px solid ${C.border}`,
          borderBottom: `1px solid ${C.border}`,
          padding: "80px 0",
        }}
      >
        <div className="max-w-6xl mx-auto px-4 md:px-8">
          <div className="text-center mb-12">
            <p
              style={{
                fontSize: 11,
                textTransform: "uppercase",
                letterSpacing: "0.2em",
                color: C.accent,
                marginBottom: 12,
                fontWeight: 600,
              }}
            >
              El problema
            </p>
            <h2
              style={{
                fontSize: "clamp(26px, 4vw, 42px)",
                fontWeight: 800,
                lineHeight: 1.15,
                maxWidth: 720,
                margin: "0 auto",
                color: C.text,
              }}
            >
              Garmin te dice <span style={{ color: C.textMuted }}>qué</span>{" "}
              entrenar.
              <br />
              Nadie te dice <span style={{ color: C.red }}>por qué</span> estás
              en riesgo.
            </h2>
          </div>

          <div className="grid md:grid-cols-2 gap-5 max-w-5xl mx-auto">
            {PAIN_POINTS.map((p) => (
              <div
                key={p.title}
                style={{
                  background: C.surface2,
                  border: `1px solid ${C.border}`,
                  borderRadius: 14,
                  padding: "22px 24px",
                  display: "flex",
                  gap: 16,
                }}
              >
                <div
                  style={{
                    fontSize: 24,
                    flexShrink: 0,
                    width: 40,
                    height: 40,
                    borderRadius: 8,
                    background: C.surface3,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  {p.icon}
                </div>
                <div>
                  <h3
                    style={{
                      fontSize: 14,
                      fontWeight: 700,
                      color: C.text,
                      marginBottom: 6,
                    }}
                  >
                    {p.title}
                  </h3>
                  <p
                    style={{
                      fontSize: 13,
                      color: C.textMuted,
                      lineHeight: 1.6,
                    }}
                  >
                    {p.body}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─────────────── COMPARATIVA ─────────────── */}
      <section
        id="comparativa"
        style={{ background: C.bg, padding: "80px 0" }}
      >
        <div className="max-w-5xl mx-auto px-4 md:px-8">
          <div className="text-center mb-12">
            <p
              style={{
                fontSize: 11,
                textTransform: "uppercase",
                letterSpacing: "0.2em",
                color: C.accent,
                marginBottom: 12,
                fontWeight: 600,
              }}
            >
              Comparativa
            </p>
            <h2
              style={{
                fontSize: "clamp(26px, 4vw, 42px)",
                fontWeight: 800,
                lineHeight: 1.15,
                color: C.text,
              }}
            >
              Liebre vs Garmin Connect+
            </h2>
            <p
              style={{
                fontSize: 15,
                color: C.textMuted,
                marginTop: 12,
                maxWidth: 580,
                margin: "12px auto 0",
                lineHeight: 1.6,
              }}
            >
              Garmin Connect+ cuesta $8.99/mes. Esta es la diferencia en lo que
              realmente importa para rendimiento y prevención.
            </p>
          </div>

          <div
            style={{
              border: `1px solid ${C.border}`,
              borderRadius: 12,
              overflow: "hidden",
            }}
          >
            <div style={{ overflowX: "auto" }}>
              <table
                style={{
                  width: "100%",
                  borderCollapse: "separate",
                  borderSpacing: 0,
                  fontSize: 13,
                }}
              >
                <thead>
                  <tr>
                    <th
                      style={{
                        textAlign: "left",
                        padding: "16px 20px",
                        background: C.surface2,
                        color: C.text,
                        fontWeight: 700,
                        fontSize: 12,
                        textTransform: "uppercase",
                        letterSpacing: "0.05em",
                      }}
                    >
                      Capacidad
                    </th>
                    <th
                      style={{
                        background: "#1a1a2e",
                        color: "#79c0ff",
                        padding: "16px 20px",
                        textAlign: "center",
                        fontWeight: 700,
                        fontSize: 12,
                        textTransform: "uppercase",
                        letterSpacing: "0.05em",
                        borderLeft: `1px solid ${C.border}`,
                      }}
                    >
                      Connect+ · $8.99
                    </th>
                    <th
                      style={{
                        background: "#0d2a14",
                        color: C.green,
                        padding: "16px 20px",
                        textAlign: "center",
                        fontWeight: 700,
                        fontSize: 12,
                        textTransform: "uppercase",
                        letterSpacing: "0.05em",
                        borderLeft: `1px solid ${C.border}`,
                      }}
                    >
                      Liebre
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {COMPARISON.map((row) => {
                    const connectNo =
                      row.connect.includes("No") ||
                      row.connect === "Sin citas" ||
                      row.connect === "No existe";
                    return (
                      <tr key={row.capability}>
                        <td
                          style={{
                            padding: "13px 20px",
                            background: C.surface,
                            color: C.textMuted,
                            borderTop: `1px solid ${C.borderSoft}`,
                          }}
                        >
                          {row.capability}
                        </td>
                        <td
                          style={{
                            padding: "13px 20px",
                            background: "#0d0d1a",
                            textAlign: "center",
                            borderTop: `1px solid ${C.borderSoft}`,
                            borderLeft: `1px solid ${C.borderSoft}`,
                          }}
                        >
                          <span
                            style={{
                              color: connectNo ? C.red : C.yellow,
                              fontSize: 16,
                              marginRight: 6,
                            }}
                          >
                            {connectNo ? "✗" : "~"}
                          </span>
                          <span
                            style={{ color: C.textMuted, fontSize: 12 }}
                          >
                            {row.connect}
                          </span>
                        </td>
                        <td
                          style={{
                            padding: "13px 20px",
                            background: "#0a1f0a",
                            textAlign: "center",
                            borderTop: `1px solid ${C.borderSoft}`,
                            borderLeft: `1px solid ${C.borderSoft}`,
                          }}
                        >
                          <span
                            style={{
                              color: C.green,
                              fontSize: 16,
                              marginRight: 6,
                            }}
                          >
                            ✓
                          </span>
                          <span style={{ color: C.text, fontSize: 12 }}>
                            {row.liebre}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* ─────────────── 8 MÓDULOS ─────────────── */}
      <section
        id="modulos"
        style={{
          background: C.surface,
          borderTop: `1px solid ${C.border}`,
          borderBottom: `1px solid ${C.border}`,
          padding: "80px 0",
        }}
      >
        <div className="max-w-6xl mx-auto px-4 md:px-8">
          <div className="text-center mb-12">
            <p
              style={{
                fontSize: 11,
                textTransform: "uppercase",
                letterSpacing: "0.2em",
                color: C.accent,
                marginBottom: 12,
                fontWeight: 600,
              }}
            >
              Módulos especializados
            </p>
            <h2
              style={{
                fontSize: "clamp(26px, 4vw, 42px)",
                fontWeight: 800,
                lineHeight: 1.15,
                color: C.text,
                maxWidth: 720,
                margin: "0 auto",
              }}
            >
              8 reportes que{" "}
              <span style={{ color: C.accent }}>Connect no tiene</span>
            </h2>
            <p
              style={{
                fontSize: 15,
                color: C.textMuted,
                marginTop: 14,
                maxWidth: 640,
                margin: "14px auto 0",
                lineHeight: 1.6,
              }}
            >
              Cada módulo cruza tus datos reales de Garmin con literatura
              científica actualizada (Scopus + Web of Science) para generar
              recomendaciones con nombre y apellido.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-5">
            {MODULES.map((m) => {
              const { accent, icon } = moduleAccent(m.n);
              return (
                <article
                  key={m.n}
                  className="liebre-module-card"
                  style={{
                    background: C.surface2,
                    border: `1px solid ${C.border}`,
                    borderTop: `3px solid ${accent}`,
                    borderRadius: 14,
                    padding: 24,
                    display: "flex",
                    flexDirection: "column",
                    position: "relative",
                    overflow: "hidden",
                    ["--module-accent" as never]: accent,
                  }}
                >
                  {/* Glow decorativo */}
                  <div
                    style={{
                      position: "absolute",
                      top: -40,
                      right: -40,
                      width: 140,
                      height: 140,
                      borderRadius: "50%",
                      background: `radial-gradient(circle, ${accent}33 0%, transparent 70%)`,
                      pointerEvents: "none",
                    }}
                  />

                  {/* Header: icon + module number */}
                  <div className="flex items-center gap-3 mb-3 relative">
                    <span
                      className="liebre-module-icon"
                      style={{
                        width: 38,
                        height: 38,
                        borderRadius: 10,
                        background: `${accent}22`,
                        color: accent,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: 18,
                        flexShrink: 0,
                      }}
                    >
                      {icon}
                    </span>
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: 700,
                        letterSpacing: "0.1em",
                        textTransform: "uppercase",
                        color: accent,
                        background: `${accent}1a`,
                        padding: "4px 10px",
                        borderRadius: 4,
                      }}
                    >
                      Módulo {String(m.n).padStart(2, "0")}
                    </span>
                  </div>

                  <h3
                    style={{
                      fontSize: 19,
                      fontWeight: 700,
                      color: C.text,
                      marginBottom: 10,
                      lineHeight: 1.25,
                    }}
                  >
                    {m.title}
                  </h3>
                  <p
                    style={{
                      fontSize: 13,
                      color: C.textMuted,
                      lineHeight: 1.6,
                      marginBottom: 16,
                    }}
                  >
                    {m.description}
                  </p>

                  <ul
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: 7,
                      marginBottom: 16,
                      flex: 1,
                      listStyle: "none",
                      padding: 0,
                    }}
                  >
                    {m.bullets.map((b) => (
                      <li
                        key={b}
                        style={{
                          fontSize: 12.5,
                          color: C.textMuted,
                          display: "flex",
                          gap: 8,
                          alignItems: "flex-start",
                          lineHeight: 1.5,
                        }}
                      >
                        <span style={{ color: accent, flexShrink: 0 }}>▸</span>
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>

                  <div
                    style={{
                      background: "rgba(63,185,80,0.08)",
                      border: "1px solid rgba(63,185,80,0.25)",
                      borderRadius: 8,
                      padding: "10px 12px",
                      marginBottom: 14,
                      fontSize: 12,
                      color: C.green,
                    }}
                  >
                    <span style={{ fontWeight: 700 }}>✓ Dato real:</span>{" "}
                    {m.realData}
                  </div>

                  <div
                    style={{
                      borderTop: `1px solid ${C.border}`,
                      paddingTop: 12,
                    }}
                  >
                    <p
                      style={{
                        fontSize: 10,
                        textTransform: "uppercase",
                        letterSpacing: "0.08em",
                        color: C.textDim,
                        marginBottom: 8,
                        fontWeight: 600,
                      }}
                    >
                      Evidencia científica
                    </p>
                    {m.evidence.map((e, i) => (
                      <div key={i} style={{ fontSize: 11, marginBottom: 6 }}>
                        <p
                          style={{
                            color: C.text,
                            fontWeight: 500,
                            lineHeight: 1.4,
                          }}
                        >
                          <span style={{ color: C.yellow }}>
                            {"★".repeat(e.level)}
                          </span>{" "}
                          {e.cite}
                        </p>
                        <p
                          style={{
                            color: C.textMuted,
                            lineHeight: 1.5,
                            marginTop: 2,
                          }}
                        >
                          {e.finding}
                        </p>
                      </div>
                    ))}
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      {/* ─────────────── DATOS REALES ─────────────── */}
      <section style={{ background: C.bg, padding: "80px 0" }}>
        <div className="max-w-6xl mx-auto px-4 md:px-8">
          <div className="text-center mb-12">
            <p
              style={{
                fontSize: 11,
                textTransform: "uppercase",
                letterSpacing: "0.2em",
                color: C.accent,
                marginBottom: 12,
                fontWeight: 600,
              }}
            >
              Datos reales · José Luis Cerón
            </p>
            <h2
              style={{
                fontSize: "clamp(26px, 4vw, 42px)",
                fontWeight: 800,
                lineHeight: 1.15,
                color: C.text,
                maxWidth: 720,
                margin: "0 auto",
              }}
            >
              Lo que el análisis descubrió{" "}
              <span style={{ color: C.green }}>en la primera semana</span>
            </h2>
            <p
              style={{
                fontSize: 14,
                color: C.textMuted,
                marginTop: 14,
                maxWidth: 580,
                margin: "14px auto 0",
                lineHeight: 1.6,
              }}
            >
              No simulaciones. Datos reales descargados de Garmin, analizados
              con el sistema activo.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-5">
            {REAL_DATA_CARDS.map((c) => (
              <article
                key={c.headline}
                style={{
                  background: C.surface,
                  border: `1px solid ${C.border}`,
                  borderRadius: 14,
                  padding: 24,
                }}
              >
                <p
                  style={{
                    fontSize: 10,
                    textTransform: "uppercase",
                    letterSpacing: "0.1em",
                    color: C.textDim,
                    fontWeight: 600,
                    marginBottom: 16,
                  }}
                >
                  {c.tag}
                </p>
                <p
                  style={{
                    fontSize: "clamp(48px, 6vw, 64px)",
                    fontWeight: 800,
                    color: C.accent,
                    lineHeight: 1,
                    fontVariantNumeric: "tabular-nums",
                    letterSpacing: "-0.02em",
                  }}
                >
                  {c.headline}
                </p>
                <p
                  style={{
                    fontSize: 14,
                    fontWeight: 700,
                    color: C.text,
                    marginTop: 10,
                    marginBottom: 12,
                  }}
                >
                  {c.sub}
                </p>
                <p
                  style={{
                    fontSize: 13,
                    color: C.textMuted,
                    lineHeight: 1.65,
                  }}
                >
                  {c.body}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ─────────────── PLANES ─────────────── */}
      <section
        id="planes"
        style={{
          background: C.surface,
          borderTop: `1px solid ${C.border}`,
          borderBottom: `1px solid ${C.border}`,
          padding: "80px 0",
        }}
      >
        <div className="max-w-5xl mx-auto px-4 md:px-8">
          <div className="text-center mb-12">
            <p
              style={{
                fontSize: 11,
                textTransform: "uppercase",
                letterSpacing: "0.2em",
                color: C.accent,
                marginBottom: 12,
                fontWeight: 600,
              }}
            >
              Planes
            </p>
            <h2
              style={{
                fontSize: "clamp(26px, 4vw, 42px)",
                fontWeight: 800,
                lineHeight: 1.15,
                color: C.text,
              }}
            >
              Comparado con lo que ya pagas
            </h2>
            <p
              style={{
                fontSize: 14,
                color: C.textMuted,
                marginTop: 14,
                maxWidth: 560,
                margin: "14px auto 0",
                lineHeight: 1.6,
              }}
            >
              Versus Garmin Connect+ ($8.99/mes) o un entrenador personal
              ($150–400/mes).
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-5">
            {PLANS.map((p) => {
              const isRec = p.badge === "Recomendado";
              return (
                <article
                  key={p.tier}
                  className={isRec ? "liebre-pricing-featured liebre-lift" : "liebre-lift"}
                  style={{
                    background: isRec ? C.surface2 : C.surface,
                    border: isRec
                      ? "1px solid transparent"
                      : `1px solid ${C.border}`,
                    borderRadius: 14,
                    padding: 28,
                    position: "relative",
                    boxShadow: isRec
                      ? `0 0 60px rgba(47,129,247,0.18)`
                      : "none",
                  }}
                >
                  {p.badge && (
                    <span
                      style={{
                        position: "absolute",
                        top: -12,
                        right: 24,
                        fontSize: 10,
                        fontWeight: 800,
                        letterSpacing: "0.08em",
                        textTransform: "uppercase",
                        background: C.accent,
                        color: "#fff",
                        padding: "5px 12px",
                        borderRadius: 20,
                      }}
                    >
                      {p.badge}
                    </span>
                  )}
                  <p
                    style={{
                      fontSize: 11,
                      textTransform: "uppercase",
                      letterSpacing: "0.1em",
                      color: C.textMuted,
                      fontWeight: 600,
                      marginBottom: 12,
                    }}
                  >
                    Liebre {p.tier}
                  </p>
                  <div className="flex items-baseline gap-2 mb-1">
                    <span
                      style={{
                        fontSize: 54,
                        fontWeight: 800,
                        color: C.text,
                        lineHeight: 1,
                        letterSpacing: "-0.02em",
                        fontVariantNumeric: "tabular-nums",
                      }}
                    >
                      ${p.price}
                    </span>
                    <span style={{ color: C.textMuted, fontSize: 14 }}>
                      USD/mes
                    </span>
                  </div>
                  <p
                    style={{
                      fontSize: 13,
                      color: C.textMuted,
                      marginBottom: 24,
                      fontVariantNumeric: "tabular-nums",
                    }}
                  >
                    {fmtCOP(p.price)}{" "}
                    <span style={{ color: C.textDim }}>
                      COP/mes aprox · tasa referencial
                    </span>
                  </p>

                  <ul
                    style={{
                      listStyle: "none",
                      padding: 0,
                      margin: 0,
                      marginBottom: 24,
                    }}
                  >
                    {p.features.map((f) => (
                      <li
                        key={f}
                        style={{
                          fontSize: 13.5,
                          color: C.text,
                          marginBottom: 10,
                          display: "flex",
                          gap: 10,
                          lineHeight: 1.5,
                        }}
                      >
                        <span
                          style={{
                            color: isRec ? C.accent : C.green,
                            flexShrink: 0,
                            fontWeight: 700,
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
                    className={isRec ? "liebre-shimmer" : ""}
                    style={{
                      display: "block",
                      textAlign: "center",
                      padding: "13px 20px",
                      borderRadius: 8,
                      fontWeight: 700,
                      fontSize: 14,
                      textDecoration: "none",
                      background: isRec ? C.accent : "transparent",
                      color: isRec ? "#fff" : C.text,
                      border: isRec ? "none" : `1px solid ${C.border}`,
                      boxShadow: isRec
                        ? "0 6px 20px rgba(47,129,247,0.4)"
                        : "none",
                    }}
                  >
                    Probar gratis
                  </Link>

                  <p
                    style={{
                      fontSize: 11,
                      color: C.textDim,
                      marginTop: 14,
                      lineHeight: 1.55,
                    }}
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
      <section
        style={{
          background: `radial-gradient(ellipse 80% 60% at 50% 50%, #0d2044 0%, ${C.bg} 70%)`,
          padding: "80px 0",
          textAlign: "center",
        }}
      >
        <div className="max-w-3xl mx-auto px-4 md:px-8">
          <h2
            style={{
              fontSize: "clamp(28px, 4vw, 44px)",
              fontWeight: 800,
              lineHeight: 1.15,
              color: C.text,
              marginBottom: 16,
            }}
          >
            Conoce <span style={{ color: C.accent }}>tu</span> respuesta
            fisiológica
            <br />
            antes de la próxima carrera
          </h2>
          <p
            style={{
              fontSize: 15,
              color: C.textMuted,
              lineHeight: 1.7,
              marginBottom: 28,
              maxWidth: 580,
              margin: "0 auto 28px",
            }}
          >
            Liebre se conecta a tu Garmin, construye tu perfil en 14 noches y
            empieza a ajustar tu plan con los datos que tu cuerpo realmente da
            — no con promedios poblacionales.
          </p>
          <Link
            href="/dashboard"
            className="liebre-shimmer liebre-lift"
            style={{
              display: "inline-block",
              background: C.accent,
              color: "#fff",
              fontWeight: 700,
              fontSize: 15,
              padding: "14px 32px",
              borderRadius: 8,
              textDecoration: "none",
              boxShadow: "0 8px 30px rgba(47,129,247,0.4)",
            }}
          >
            Entrar al dashboard →
          </Link>
        </div>
      </section>

      {/* ─────────────── FOOTER ─────────────── */}
      <footer
        style={{
          background: C.surface,
          borderTop: `1px solid ${C.border}`,
          padding: "48px 0 32px",
        }}
      >
        <div className="max-w-6xl mx-auto px-4 md:px-8">
          <div className="grid md:grid-cols-3 gap-10 mb-10">
            <div>
              <p
                className="wordmark text-2xl mb-3"
                style={{ color: C.text }}
              >
                liebre<span style={{ color: C.accent }}>.</span>
              </p>
              <p
                style={{
                  fontSize: 13,
                  color: C.textMuted,
                  lineHeight: 1.65,
                  maxWidth: 280,
                }}
              >
                Tu pacer con inteligencia artificial y ciencia validada.
                Construido para corredores que quieren entender, no solo medir.
              </p>
            </div>
            <FooterLinks
              title="Producto"
              links={[
                { href: "#modulos", label: "Módulos" },
                { href: "#comparativa", label: "vs Garmin Connect" },
                { href: "#planes", label: "Planes" },
                { href: "/dashboard", label: "Demo del dashboard" },
              ]}
            />
            <div>
              <p
                style={{
                  fontSize: 11,
                  textTransform: "uppercase",
                  letterSpacing: "0.1em",
                  color: C.textDim,
                  marginBottom: 12,
                  fontWeight: 600,
                }}
              >
                Tecnología
              </p>
              <ul
                style={{
                  listStyle: "none",
                  padding: 0,
                  fontSize: 12,
                  color: C.textMuted,
                  lineHeight: 1.85,
                }}
              >
                <li>Powered by Anthropic Claude</li>
                <li>Datos: Garmin Connect</li>
                <li>Evidencia: Scopus + Web of Science</li>
              </ul>
            </div>
          </div>
          <div
            style={{
              paddingTop: 24,
              borderTop: `1px solid ${C.border}`,
              display: "flex",
              flexWrap: "wrap",
              justifyContent: "space-between",
              gap: 10,
              fontSize: 11,
              color: C.textDim,
              lineHeight: 1.5,
            }}
          >
            <p>
              © {new Date().getFullYear()} Liebre. Todos los derechos
              reservados.
            </p>
            <p style={{ maxWidth: 460, textAlign: "right" }}>
              Los reportes son informativos y complementan — no reemplazan — la
              evaluación de un médico deportivo o fisioterapeuta.
            </p>
          </div>
        </div>
      </footer>
    </main>
  );
}

/* ─── Sub-componentes ─── */

function NavLink({
  href,
  children,
}: {
  href: string;
  children: React.ReactNode;
}) {
  return (
    <a
      href={href}
      className="hidden sm:inline text-sm px-3 py-1.5"
      style={{
        color: C.textMuted,
        textDecoration: "none",
        fontWeight: 500,
      }}
    >
      {children}
    </a>
  );
}

function FooterLinks({
  title,
  links,
}: {
  title: string;
  links: Array<{ href: string; label: string }>;
}) {
  return (
    <div>
      <p
        style={{
          fontSize: 11,
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          color: C.textDim,
          marginBottom: 12,
          fontWeight: 600,
        }}
      >
        {title}
      </p>
      <ul
        style={{
          listStyle: "none",
          padding: 0,
          fontSize: 13,
          lineHeight: 1.9,
        }}
      >
        {links.map((l) => (
          <li key={l.href}>
            <a
              href={l.href}
              style={{
                color: C.textMuted,
                textDecoration: "none",
              }}
            >
              {l.label}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
