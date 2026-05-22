// liebre-views.jsx — Full view assemblies for all 3 mockups

// ── Shared data ────────────────────────────────────────────

const WEEKS_DATA = [
  { week: '5/11', planned: 25, executed: 19.9, hrv: 53, acwr: 0.95 },
  { week: '5/18', planned: 28, executed: 10.1, hrv: 56, acwr: 1.05 },
];

const PROFILE = { name: 'José Luis Cerón', age: 36, weight: 67.8, height: 170, hrMax: 190, hrRest: 51 };

// ── Dataset 1 — Building baseline ──────────────────────────

const D1 = {
  hrv: {
    value: 52, baseline: 55, delta: '−5%',
    nights: 8, total: 14, status: 'Construyendo baseline', color: C.blue,
    spark: [49, 53, 48, 55, 50, 54, 56, 52],
  },
  diagnosis: {
    text: 'Aún estamos construyendo tu baseline personal de HRV. Con 8 de 14 noches recolectadas, el agente necesita más datos para detectar tendencias individuales con precisión. Tus 52 ms actuales están dentro del rango funcional típico para corredores de fondo, con una tendencia suavemente ascendente los últimos 3 días.',
    action: 'Sincroniza tu Garmin esta noche para avanzar el baseline. Continúa con rodaje en Z2 (30–40 min). Noche 9 de 14 desbloqueará el diagnóstico de carga.',
    cite: 'Seiler (2010) · Int J Sports Physiol Perform · Review — Distribución polarizada 80/20',
  },
  interp: 'Tu HRV de 52 ms está dentro del rango funcional, pero el agente necesita 6 noches más para establecer tu baseline personal y detectar patrones individuales de recuperación.',
  interpCite: 'Plews & Buchheit (2017) · J Strength Cond Res · Observacional',
  factors: [
    { name: 'Sueño', detail: '6h 32m · Calidad media', impact: 41, color: C.green },
    {
      name: 'Carrera', detail: 'Popayán · 5.22 km · Z2',
      impact: -11, color: C.red,
      interpretation: 'Carga aeróbica controlada, dentro del umbral Z2. Impacto leve sobre HRV.',
    },
    {
      name: 'ACWR', detail: 'Ratio aguda/crónica · 1.05',
      impact: 8, color: C.green,
      cite: 'Gabbett (2016) · Br J Sports Med · Estudio cohortivo ACWR',
    },
  ],
};

// ── Dataset 2 — Optimal / Equilibrado ──────────────────────

const D2 = {
  hrv: {
    value: 68, baseline: 62, delta: '+9.7%',
    nights: 14, total: 14, status: 'Equilibrado', color: C.green,
    spark: [58, 62, 65, 70, 64, 68, 71, 68],
  },
  diagnosis: {
    text: 'Sistema autónomo recuperado. Tu HRV de 68 ms supera tu baseline (62 ms) en un 9.7%, indicando una ventana de supercompensación. El agente detecta condiciones óptimas para estímulos de alta intensidad: FC reposo en mínimo histórico (50 lpm), sueño profundo consistente los últimos 4 días.',
    action: 'Sesión de intervalos 5×1000 m a ritmo umbral (≈4:45/km). FC objetivo Z4 (171–182 lpm). Precede con 15 min de calentamiento progresivo.',
    cite: 'Kiviniemi et al. (2010) · Scand J Med Sci Sports · HRV-guided training design',
  },
  interp: 'Tu HRV de 68 ms supera en 9.7% tu baseline personal (62 ms), indicando recuperación del SNA superior a tu media. La variabilidad elevada es indicativa de mayor capacidad adaptativa a estímulos intensos.',
  interpCite: 'Buchheit (2014) · Sports Med · Revisión sistemática HRV y rendimiento',
  factors: [
    { name: 'Sueño', detail: '7h 48m · Calidad alta', impact: 52, color: C.green },
    {
      name: 'Rodaje largo', detail: 'Domingo · 18 km · Z2–Z3',
      impact: 23, color: C.green,
      interpretation: 'Volumen bien dosificado. Adaptación positiva registrada.',
    },
    {
      name: 'ACWR', detail: 'Ratio aguda/crónica · 0.98',
      impact: 12, color: C.green,
      cite: 'Gabbett (2016) · Br J Sports Med · Estudio cohortivo ACWR',
    },
    { name: 'Descanso activo', detail: '2 días de recuperación', impact: 18, color: C.green },
  ],
};

// ── Desktop layout (shared structure) ─────────────────────

const gridRow = { display: 'grid', gridTemplateColumns: '1fr 340px', gap: 16, marginBottom: 16 };

const DesktopLayout = ({ d }) => {
  const { hrv, diagnosis, interp, interpCite, factors } = d;

  return React.createElement('div', {
    style: {
      width: 1440, height: 900, display: 'flex',
      background: C.pageBg, overflow: 'hidden',
      fontFamily: 'Inter, sans-serif',
    }
  },
    React.createElement(Sidebar, null),
    // Main content
    React.createElement('div', { style: { flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 } },
      React.createElement(TopBar, {
        greeting: 'Buenas tardes, José',
        summary: 'Dashboard · Vista general del entrenamiento',
        date: 'jueves, 21 de mayo de 2026',
      }),
      // Scrollable grid
      React.createElement('div', {
        style: { flex: 1, overflowY: 'auto', padding: '18px 24px 0', boxSizing: 'border-box' }
      },
        // Row 1
        React.createElement('div', { style: gridRow },
          React.createElement(DiagnosisCard, {
            text: diagnosis.text,
            action: diagnosis.action,
            cite: diagnosis.cite,
          }),
          React.createElement(GoalCard, {
            goal: '21K', subLabel: 'en 1h50',
            date: '2026-10-01', daysLeft: 133, progress: 60,
          })
        ),
        // Row 2
        React.createElement('div', { style: gridRow },
          React.createElement(HRVCard, {
            value: hrv.value,
            baseline: hrv.baseline,
            delta: hrv.delta,
            nights: hrv.nights,
            totalNights: hrv.total,
            status: hrv.status,
            statusColor: hrv.color,
            sparkData: hrv.spark,
            interpretation: interp,
            cite: interpCite,
          }),
          React.createElement(ProfileCard, { ...PROFILE })
        ),
        // Row 3
        React.createElement('div', { style: { ...gridRow, marginBottom: 0 } },
          React.createElement(FactorsCard, { factors }),
          React.createElement(HistoryCard, {
            weeks: WEEKS_DATA,
            note: 'Semana en curso con FC reposo bajando 56→50 lpm. Señal positiva de adaptación aeróbica.',
          })
        )
      ),
      React.createElement(LiebreFooter, null)
    )
  );
};

// ── Annotation panel (sits alongside each artboard in DC) ──

const AnnotationPanel = ({ notes, height = 900 }) =>
  React.createElement('div', {
    style: {
      width: 264, height,
      background: '#FFFDF0',
      borderLeft: '3px solid #F5C842',
      padding: '20px 16px',
      boxSizing: 'border-box',
      fontFamily: 'Inter, sans-serif',
      overflowY: 'auto',
    }
  },
    React.createElement('div', {
      style: { fontSize: 10, fontWeight: 700, letterSpacing: '0.08em', color: '#B7851A', textTransform: 'uppercase', marginBottom: 16 }
    }, '📝 Decisiones de diseño'),
    ...notes.map((n, i) =>
      React.createElement('div', {
        key: i,
        style: {
          marginBottom: 14, paddingBottom: 14,
          borderBottom: i < notes.length - 1 ? '1px solid rgba(0,0,0,0.07)' : 'none',
        }
      },
        React.createElement('div', { style: { fontSize: 12, fontWeight: 700, color: '#1C1C1C', marginBottom: 4, lineHeight: 1.3 } }, n.title),
        React.createElement('div', { style: { fontSize: 12, color: '#555', lineHeight: 1.55 } }, n.body)
      )
    )
  );

const NOTES_1 = [
  { title: 'Diagnóstico arriba', body: 'El agente ocupa el primer lugar visual porque es la diferenciación clave vs. Garmin Connect puro. Primera capa de valor en cada apertura.' },
  { title: 'Gauge azul = marca, no estado', body: 'Azul #1976D2 cuando el baseline está en construcción. Verde solo aparece al alcanzar estado Equilibrado. El color comunica madurez del modelo.' },
  { title: 'Meta oscura = ancla emocional', body: 'La card negra contrasta deliberadamente con el dashboard claro. El objetivo a largo plazo justifica visualmente todo el tracking diario.' },
  { title: '8/14 noches visible', body: 'La barra de progreso educa al usuario sobre la necesidad del baseline sin texto de onboarding adicional. Progreso claro, sin fricciones.' },
  { title: 'Interpretación Liebre', body: 'Firma del producto. Párrafo causal + cita de paper: el nivel de análisis que ningún tracker wearable ofrece. Visible pero no invasiva.' },
  { title: 'Gap tipográfico: Instrument Serif', body: 'Los números grandes en serif peso 300 crean contraste visual con el body Inter. Evoca rigor científico, no UI deportiva genérica.' },
];

const NOTES_2 = [
  { title: 'Gauge verde = equilibrio fisiológico', body: 'El cambio de azul → verde es automático al superar threshold de baseline. Sin acción del usuario: el agente comunica el estado por color.' },
  { title: 'Delta +9.7% como métrica clave', body: 'Comparación relativa vs. baseline personal, no valor absoluto. Más predictiva del rendimiento que el HRV crudo según literatura.' },
  { title: 'Diagnóstico positivo = experiencia ideal', body: 'Esta vista muestra la recompensa del comportamiento consistente. Diseñada para motivar al usuario a mantener el hábito de sincronización nocturna.' },
  { title: 'Factores todos positivos', body: 'En estado óptimo, los impactos son mayoritariamente verdes. El usuario ve la causalidad entre sus hábitos y su recuperación.' },
  { title: 'Citation badge azul',body: 'El azul #1976D2 de las citas es el mismo acento de marca. Las referencias científicas son parte del sistema de identidad, no elementos secundarios.' },
];

const NOTES_3 = [
  { title: 'Gauge centrado en mobile', body: 'En desktop puede convivir con más contexto. En mobile, el dato más importante ocupa el primer scroll: jerarquía táctil al servicio de la lectura rápida.' },
  { title: 'Bottom nav = sidebar adaptada', body: 'La barra inferior reutiliza el negro #1A1A1A de la sidebar desktop. Coherencia de marca entre plataformas sin duplicar patrones.' },
  { title: 'Diagnosis card colapsada', body: 'El cuerpo del diagnóstico se trunca en mobile. El corredor pre-entreno necesita la idea clave en < 5 segundos, no el análisis completo.' },
  { title: 'Meta oscura conservada', body: 'La card negra se mantiene en mobile para conservar la jerarquía emocional. El objetivo es el mismo independientemente del dispositivo.' },
  { title: 'Cards full-width', body: 'Sin la distribución 2/3 + 1/3 del desktop, todo va en columna única. La densidad se reduce, la legibilidad táctil aumenta.' },
];

// ── Mockup 1: Building baseline ────────────────────────────

const Mockup1Desktop = () => React.createElement(DesktopLayout, { d: D1 });
const Annotation1 = () => React.createElement(AnnotationPanel, { notes: NOTES_1, height: 900 });

// ── Mockup 2: Optimal state ─────────────────────────────────

const Mockup2Desktop = () => React.createElement(DesktopLayout, { d: D2 });
const Annotation2 = () => React.createElement(AnnotationPanel, { notes: NOTES_2, height: 900 });

// ── Mockup 3: Mobile ────────────────────────────────────────

const MobileLayout = () => {
  const { hrv, diagnosis, factors } = D1;

  return React.createElement('div', {
    style: {
      width: 375, height: 812, background: C.pageBg,
      display: 'flex', flexDirection: 'column',
      fontFamily: 'Inter, sans-serif', position: 'relative', overflow: 'hidden',
    }
  },
    // Status bar
    React.createElement('div', {
      style: {
        height: 44, background: C.sidebar, display: 'flex', alignItems: 'center',
        justifyContent: 'space-between', padding: '0 20px', flexShrink: 0,
      }
    },
      React.createElement('span', { style: { color: '#fff', fontSize: 13, fontWeight: 600, fontFamily: 'Inter, sans-serif' } }, '9:41'),
      React.createElement('span', { style: { color: 'rgba(255,255,255,0.8)', fontSize: 12, letterSpacing: 1 } }, '● ◀ ⬛')
    ),
    // Dark header
    React.createElement('div', {
      style: { background: C.sidebar, padding: '10px 20px 18px', flexShrink: 0 }
    },
      React.createElement('div', {
        style: { fontFamily: "'Instrument Serif', Georgia, serif", fontSize: 22, color: '#fff', lineHeight: 1 }
      }, 'liebre', React.createElement('span', { style: { color: C.blue } }, '.')),
      React.createElement('div', { style: { fontSize: 17, color: '#fff', fontWeight: 600, marginTop: 6, fontFamily: 'Inter, sans-serif' } }, 'Buenas tardes, José'),
      React.createElement('div', { style: { fontSize: 12, color: 'rgba(255,255,255,0.55)', marginTop: 2, fontFamily: 'Inter, sans-serif' } }, 'jueves, 21 de mayo · 2026')
    ),
    // Scroll content
    React.createElement('div', {
      style: { flex: 1, overflowY: 'auto', padding: '14px 16px 70px', boxSizing: 'border-box' }
    },
      // HRV gauge centered
      React.createElement(Card, { style: { marginBottom: 12 } },
        React.createElement('div', { style: { textAlign: 'center' } },
          React.createElement(UpperLabel, null, 'VFC Nocturna'),
          React.createElement('div', { style: { display: 'flex', justifyContent: 'center', margin: '12px 0 8px' } },
            React.createElement(Gauge, { value: hrv.value, color: hrv.color, size: 128 })
          ),
          React.createElement('div', { style: { display: 'flex', justifyContent: 'center', marginBottom: 12 } },
            React.createElement(StatusPill, { label: hrv.status, color: hrv.color })
          ),
          React.createElement('div', { style: { display: 'flex', justifyContent: 'center', gap: 28 } },
            React.createElement(StatBlock, { label: 'Baseline', value: `${hrv.baseline} ms` }),
            React.createElement(StatBlock, { label: 'Delta', value: hrv.delta, color: C.amber }),
            React.createElement(StatBlock, { label: 'Noches', value: `${hrv.nights}/${hrv.total}` })
          )
        )
      ),
      // Diagnosis card (collapsed)
      React.createElement(Card, {
        style: {
          marginBottom: 12,
          background: `radial-gradient(ellipse 80% 80% at 95% 5%, rgba(25,118,210,0.05) 0%, transparent 60%), #fff`,
        }
      },
        React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 } },
          React.createElement('div', {
            style: {
              width: 28, height: 28, borderRadius: '50%', background: C.blue,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 12, fontWeight: 700, color: '#fff', flexShrink: 0, fontFamily: 'Inter, sans-serif',
            }
          }, 'L'),
          React.createElement(UpperLabel, null, 'Diagnóstico del día')
        ),
        React.createElement('p', {
          style: { fontFamily: 'Inter, sans-serif', fontSize: 13, color: C.t1, lineHeight: 1.6, margin: '0 0 10px' }
        }, diagnosis.text.slice(0, 180) + '…'),
        React.createElement(CiteBadge, { text: diagnosis.cite })
      ),
      // Goal card (dark)
      React.createElement(Card, { dark: true, style: { marginBottom: 12, padding: 20 } },
        React.createElement('div', {
          style: { position: 'absolute', bottom: -30, right: -30, width: 120, height: 120, borderRadius: '50%', background: `radial-gradient(circle, ${C.blueSoft}30, transparent 70%)` }
        }),
        React.createElement(UpperLabel, { style: { color: 'rgba(255,255,255,0.4)' } }, 'Tu Meta'),
        React.createElement('div', { style: { display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginTop: 8 } },
          React.createElement('div', null,
            React.createElement('div', {
              style: { fontFamily: "'Instrument Serif', Georgia, serif", fontSize: 52, color: '#fff', lineHeight: 1, letterSpacing: '-0.02em', fontVariantNumeric: 'tabular-nums' }
            }, '21K'),
            React.createElement('div', { style: { fontFamily: 'Inter, sans-serif', fontSize: 12, color: 'rgba(255,255,255,0.65)', marginTop: 4 } }, 'en 1h50 · 2026-10-01')
          ),
          React.createElement('div', { style: { textAlign: 'right' } },
            React.createElement('div', { style: { fontFamily: "'Instrument Serif', Georgia, serif", fontSize: 40, color: C.blueSoft, lineHeight: 1, fontVariantNumeric: 'tabular-nums' } }, '133'),
            React.createElement('div', { style: { fontFamily: 'Inter, sans-serif', fontSize: 11, color: 'rgba(255,255,255,0.45)' } }, 'días')
          )
        ),
        React.createElement('div', { style: { marginTop: 14, height: 3, background: 'rgba(255,255,255,0.1)', borderRadius: 2 } },
          React.createElement('div', { style: { width: '60%', height: '100%', background: C.blueSoft, borderRadius: 2 } })
        )
      ),
      // Factors (compact)
      React.createElement(Card, { style: { marginBottom: 12 } },
        React.createElement('div', { style: { marginBottom: 10 } }, React.createElement(UpperLabel, null, 'Factores')),
        ...D1.factors.map((f, i) => React.createElement(FactorCard, { key: i, ...f }))
      )
    ),
    // Bottom nav
    React.createElement('div', {
      style: {
        position: 'absolute', bottom: 0, left: 0, right: 0, height: 58,
        background: C.sidebar, display: 'flex', alignItems: 'center',
        justifyContent: 'space-around', borderTop: '1px solid rgba(255,255,255,0.08)',
        flexShrink: 0,
      }
    },
      ...[['⌂', 'Inicio', true], ['◆', 'Actividades', false], ['♡', 'Salud', false], ['▤', 'Ciencia', false], ['◯', 'Perfil', false]].map(
        ([icon, label, active]) =>
          React.createElement('div', {
            key: label,
            style: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3, padding: '0 6px' }
          },
            React.createElement('span', { style: { fontSize: 18, color: active ? '#fff' : 'rgba(255,255,255,0.4)' } }, icon),
            React.createElement('span', {
              style: {
                fontSize: 10, fontFamily: 'Inter, sans-serif',
                color: active ? C.blue : 'rgba(255,255,255,0.4)',
                fontWeight: active ? 600 : 400,
              }
            }, label)
          )
      )
    )
  );
};

const Annotation3 = () => React.createElement(AnnotationPanel, { notes: NOTES_3, height: 812 });

Object.assign(window, {
  Mockup1Desktop, Annotation1,
  Mockup2Desktop, Annotation2,
  MobileLayout, Annotation3,
});
