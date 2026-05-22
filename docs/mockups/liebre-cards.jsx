// liebre-cards.jsx — Card-level components for the Liebre dashboard

// ── Diagnosis card ─────────────────────────────────────────

const DiagnosisCard = ({ text, action, cite }) =>
  React.createElement(Card, {
    style: {
      background: `radial-gradient(ellipse 60% 80% at 95% 5%, rgba(25,118,210,0.05) 0%, transparent 60%), #fff`,
      height: '100%', boxSizing: 'border-box',
    }
  },
    // Header
    React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 } },
      React.createElement('div', {
        style: {
          width: 32, height: 32, borderRadius: '50%', background: C.blue,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 13, fontWeight: 700, color: '#fff', flexShrink: 0, fontFamily: 'Inter, sans-serif',
        }
      }, 'L'),
      React.createElement('div', null,
        React.createElement(UpperLabel, null, 'Diagnóstico del día'),
        React.createElement('div', {
          style: { fontFamily: 'Inter, sans-serif', fontSize: 11, color: C.t3, marginTop: 2 }
        }, 'Análisis cruzado generado por tu agente')
      )
    ),
    // Body
    React.createElement('p', {
      style: {
        fontFamily: 'Inter, sans-serif', fontSize: 14, color: C.t1,
        lineHeight: 1.65, margin: 0,
      }
    }, text),
    // Action section
    React.createElement('div', { style: { marginTop: 14, paddingTop: 14, borderTop: `1px solid ${C.border}` } },
      React.createElement(UpperLabel, null, 'Acción recomendada para hoy'),
      React.createElement('p', {
        style: {
          fontFamily: 'Inter, sans-serif', fontSize: 13, fontWeight: 500,
          color: C.t1, margin: '7px 0 0', lineHeight: 1.5,
        }
      }, action),
      cite && React.createElement(CiteBadge, { text: cite })
    )
  );

// ── Goal card (dark) ───────────────────────────────────────

const GoalCard = ({ goal, subLabel, date, daysLeft, progress }) =>
  React.createElement(Card, { dark: true, style: { height: '100%', boxSizing: 'border-box' } },
    // Decorative glow
    React.createElement('div', {
      style: {
        position: 'absolute', bottom: -50, right: -50,
        width: 180, height: 180, borderRadius: '50%',
        background: `radial-gradient(circle, ${C.blueSoft}28 0%, transparent 70%)`,
        pointerEvents: 'none',
      }
    }),
    // Label
    React.createElement(UpperLabel, { style: { color: 'rgba(255,255,255,0.45)' } }, 'Tu Meta'),
    // Main metric
    React.createElement('div', { style: { marginTop: 12 } },
      React.createElement('div', {
        style: {
          fontFamily: "'Instrument Serif', Georgia, serif",
          fontSize: 64, fontWeight: 300, color: '#fff',
          lineHeight: 0.9, letterSpacing: '-0.03em',
          fontVariantNumeric: 'tabular-nums',
        }
      }, goal),
      React.createElement('div', {
        style: { fontFamily: 'Inter, sans-serif', fontSize: 13, color: 'rgba(255,255,255,0.7)', marginTop: 10 }
      }, `${subLabel} · ${date}`)
    ),
    // Countdown
    React.createElement('div', {
      style: { marginTop: 16, paddingTop: 16, borderTop: '1px solid rgba(255,255,255,0.1)' }
    },
      React.createElement('div', { style: { display: 'flex', alignItems: 'baseline', gap: 7 } },
        React.createElement('span', {
          style: {
            fontFamily: "'Instrument Serif', Georgia, serif",
            fontSize: 44, fontWeight: 300, color: C.blueSoft,
            letterSpacing: '-0.02em', fontVariantNumeric: 'tabular-nums', lineHeight: 1,
          }
        }, daysLeft),
        React.createElement('span', {
          style: { fontFamily: 'Inter, sans-serif', fontSize: 12, color: 'rgba(255,255,255,0.55)' }
        }, 'días por delante')
      )
    ),
    // Progress
    React.createElement('div', { style: { marginTop: 16 } },
      React.createElement('div', {
        style: { display: 'flex', justifyContent: 'space-between', marginBottom: 6 }
      },
        React.createElement('span', { style: { fontFamily: 'Inter, sans-serif', fontSize: 11, color: 'rgba(255,255,255,0.45)' } }, 'Progreso'),
        React.createElement('span', { style: { fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 600, color: 'rgba(255,255,255,0.75)' } }, `${progress}%`)
      ),
      React.createElement('div', { style: { height: 4, background: 'rgba(255,255,255,0.1)', borderRadius: 2 } },
        React.createElement('div', { style: { width: `${progress}%`, height: '100%', background: C.blueSoft, borderRadius: 2 } })
      )
    )
  );

// ── HRV card ───────────────────────────────────────────────

const HRVCard = ({ value, baseline, delta, nights, totalNights, status, statusColor, sparkData, interpretation, cite }) =>
  React.createElement(Card, { style: { height: '100%', boxSizing: 'border-box' } },
    // Header
    React.createElement('div', {
      style: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }
    },
      React.createElement('div', null,
        React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: 7 } },
          React.createElement('span', { style: { fontSize: 11 } }, '🔵'),
          React.createElement(UpperLabel, null, 'VFC Nocturna')
        ),
        React.createElement('div', {
          style: { fontFamily: 'Inter, sans-serif', fontSize: 11, color: C.t3, marginTop: 3 }
        }, `Media últimos ${nights} días`)
      ),
      React.createElement(StatusPill, { label: status, color: statusColor })
    ),
    // Gauge + stats row
    React.createElement('div', { style: { display: 'flex', gap: 20, alignItems: 'flex-start' } },
      React.createElement(Gauge, { value, color: statusColor, size: 136 }),
      React.createElement('div', { style: { flex: 1 } },
        React.createElement('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px 16px', marginBottom: 12 } },
          React.createElement(StatBlock, { label: 'Baseline', value: `${baseline} ms` }),
          React.createElement(StatBlock, {
            label: 'Delta',
            value: delta,
            color: delta.startsWith('-') ? C.amber : C.green,
          }),
          React.createElement(StatBlock, { label: 'Días', value: `${nights}/${totalNights}` })
        ),
        React.createElement('div', { style: { width: '100%' } },
          React.createElement(Sparkline, { data: sparkData, baseline, color: statusColor, height: 56 })
        )
      )
    ),
    // Progress bar
    React.createElement('div', { style: { marginTop: 12 } },
      React.createElement('div', { style: { display: 'flex', justifyContent: 'space-between', marginBottom: 5 } },
        React.createElement('span', { style: { fontFamily: 'Inter, sans-serif', fontSize: 11, color: C.t3 } }, 'Progreso baseline'),
        React.createElement('span', { style: { fontFamily: 'Inter, sans-serif', fontSize: 11, color: C.t2 } }, `${nights}/${totalNights}`)
      ),
      React.createElement('div', { style: { height: 4, background: C.border, borderRadius: 2 } },
        React.createElement('div', {
          style: { width: `${(nights / totalNights) * 100}%`, height: '100%', background: statusColor, borderRadius: 2 }
        })
      )
    ),
    // Liebre interpretation
    React.createElement(LiebreInterp, { text: interpretation, cite })
  );

// ── Profile card ───────────────────────────────────────────

const ProfileCard = ({ name, age, weight, height, hrMax, hrRest }) =>
  React.createElement(Card, { style: { height: '100%', boxSizing: 'border-box' } },
    React.createElement(UpperLabel, null, 'Tu Perfil'),
    React.createElement('div', {
      style: { display: 'flex', alignItems: 'center', gap: 12, margin: '14px 0 16px' }
    },
      React.createElement('div', {
        style: {
          width: 44, height: 44, borderRadius: '50%', background: C.blue,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 15, fontWeight: 700, color: '#fff', flexShrink: 0, fontFamily: 'Inter, sans-serif',
        }
      }, 'JL'),
      React.createElement('div', null,
        React.createElement('div', { style: { fontFamily: 'Inter, sans-serif', fontSize: 14, fontWeight: 600, color: C.t1 } }, name),
        React.createElement('div', { style: { fontFamily: 'Inter, sans-serif', fontSize: 11, color: C.t3, marginTop: 2 } }, 'Corredor · Plan 21K')
      )
    ),
    React.createElement('div', { style: { display: 'flex', flexDirection: 'column', gap: 9 } },
      ...[
        ['Edad', `${age} años`],
        ['Peso', `${weight} kg`],
        ['Altura', `${height} cm`],
        ['FC máx', `${hrMax} lpm`],
        ['FC reposo', `${hrRest} lpm`],
      ].map(([k, v]) =>
        React.createElement('div', {
          key: k,
          style: { display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }
        },
          React.createElement('span', { style: { fontFamily: 'Inter, sans-serif', fontSize: 13, color: C.t3 } }, k),
          React.createElement('span', {
            style: { fontFamily: 'Inter, sans-serif', fontSize: 13, fontWeight: 600, color: C.t1, fontVariantNumeric: 'tabular-nums' }
          }, v)
        )
      )
    )
  );

// ── History card ───────────────────────────────────────────

const HistoryCard = ({ weeks, note }) =>
  React.createElement(Card, { style: { height: '100%', boxSizing: 'border-box' } },
    React.createElement('div', { style: { marginBottom: 14 } },
      React.createElement(UpperLabel, null, 'Historial Semanal'),
      React.createElement('div', { style: { fontFamily: 'Inter, sans-serif', fontSize: 11, color: C.t3, marginTop: 3 } }, 'Últimas 2 semanas')
    ),
    React.createElement('table', { style: { width: '100%', borderCollapse: 'collapse', fontFamily: 'Inter, sans-serif', fontSize: 12 } },
      React.createElement('thead', null,
        React.createElement('tr', null,
          ...['Sem.', 'Plan', 'Ejec.', 'HRV', 'ACWR'].map(h =>
            React.createElement('th', {
              key: h,
              style: {
                textAlign: h === 'Sem.' ? 'left' : 'right',
                padding: '4px 6px', color: C.t3, fontWeight: 500,
                borderBottom: `1px solid ${C.border}`,
                letterSpacing: '0.04em', textTransform: 'uppercase', fontSize: 10,
              }
            }, h)
          )
        )
      ),
      React.createElement('tbody', null,
        ...weeks.map((w, i) =>
          React.createElement('tr', { key: i },
            React.createElement('td', { style: { padding: '9px 6px', color: C.t2, fontWeight: 500 } }, w.week),
            React.createElement('td', { style: { padding: '9px 6px', color: C.t3, textAlign: 'right', fontVariantNumeric: 'tabular-nums' } }, `${w.planned} km`),
            React.createElement('td', { style: { padding: '9px 6px', color: C.t1, textAlign: 'right', fontWeight: 600, fontVariantNumeric: 'tabular-nums' } }, `${w.executed} km`),
            React.createElement('td', { style: { padding: '9px 6px', color: C.t1, textAlign: 'right', fontVariantNumeric: 'tabular-nums' } }, w.hrv),
            React.createElement('td', { style: { padding: '9px 6px', textAlign: 'right' } },
              React.createElement('span', {
                style: {
                  fontWeight: 700, fontSize: 12, fontVariantNumeric: 'tabular-nums',
                  color: w.acwr >= 0.8 && w.acwr <= 1.3 ? C.green : w.acwr > 1.3 ? C.red : C.amber,
                }
              }, w.acwr.toFixed(2))
            )
          )
        )
      )
    ),
    note && React.createElement('div', {
      style: {
        marginTop: 14, padding: '10px 12px', background: C.subtle, borderRadius: 6,
        borderLeft: `3px solid ${C.blue}`,
      }
    },
      React.createElement(UpperLabel, { style: { fontSize: 10 } }, 'Nota del Agente'),
      React.createElement('p', {
        style: { fontFamily: 'Inter, sans-serif', fontSize: 12, color: C.t2, margin: '5px 0 0', lineHeight: 1.5 }
      }, note)
    )
  );

// ── Factors section card ───────────────────────────────────

const FactorsCard = ({ factors }) =>
  React.createElement(Card, { style: { height: '100%', boxSizing: 'border-box' } },
    React.createElement('div', { style: { marginBottom: 12 } },
      React.createElement(UpperLabel, null, 'Factores que influyen en tu estado')
    ),
    ...factors.map((f, i) =>
      React.createElement(FactorCard, { key: i, ...f })
    )
  );

Object.assign(window, {
  DiagnosisCard, GoalCard, HRVCard, ProfileCard, HistoryCard, FactorsCard,
});
