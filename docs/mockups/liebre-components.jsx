// liebre-components.jsx — Design tokens + primitive components

const C = {
  sidebar:    '#1A1A1A',
  pageBg:     '#F5F5F5',
  cardBg:     '#FFFFFF',
  subtle:     '#F9FAFB',
  t1:         '#1C1C1C',
  t2:         '#6B7280',
  t3:         '#9CA3AF',
  blue:       '#1976D2',
  blueSoft:   '#3B97F3',
  orange:     '#F5A623',
  green:      '#16A544',
  amber:      '#F27716',
  red:        '#E02C2C',
  border:     '#E5E7EB',
};

// ── Typography primitives ──────────────────────────────────

const UpperLabel = ({ children, style = {} }) => (
  React.createElement('span', {
    style: {
      fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 500,
      letterSpacing: '0.06em', textTransform: 'uppercase', color: C.t3,
      lineHeight: 1, ...style,
    }
  }, children)
);

// ── Status Pill ────────────────────────────────────────────

const StatusPill = ({ label, color }) => (
  React.createElement('span', {
    style: {
      display: 'inline-flex', alignItems: 'center', gap: 5,
      padding: '4px 10px', borderRadius: 999,
      background: color + '22',
      fontSize: 12, fontWeight: 600, color, fontFamily: 'Inter, sans-serif',
      lineHeight: 1, whiteSpace: 'nowrap',
    }
  },
    React.createElement('span', { style: { width: 8, height: 8, borderRadius: '50%', background: color, flexShrink: 0 } }),
    label
  )
);

// ── Citation Badge ─────────────────────────────────────────

const CiteBadge = ({ text }) => (
  React.createElement('div', { style: { display: 'flex', gap: 6, marginTop: 8, alignItems: 'flex-start' } },
    React.createElement('span', { style: { fontSize: 12, lineHeight: '1.4', flexShrink: 0 } }, '📄'),
    React.createElement('span', {
      style: { fontSize: 12, fontWeight: 500, color: C.blue, fontFamily: 'Inter, sans-serif', lineHeight: 1.4 }
    }, text)
  )
);

// ── Liebre Interpretation block ────────────────────────────

const LiebreInterp = ({ text, cite }) => (
  React.createElement('div', { style: { marginTop: 12, paddingTop: 12, borderTop: `1px solid ${C.border}` } },
    React.createElement('div', { style: { display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 } },
      React.createElement('span', { style: { fontSize: 11 } }, '📊'),
      React.createElement(UpperLabel, null, 'Interpretación Liebre')
    ),
    React.createElement('p', {
      style: { margin: 0, fontSize: 13, color: C.t2, lineHeight: 1.55, fontFamily: 'Inter, sans-serif' }
    }, text),
    cite && React.createElement(CiteBadge, { text: cite })
  )
);

// ── Circular Gauge (SVG, 270° arc, gap at bottom) ──────────

const Gauge = ({ value, min = 20, max = 120, color = C.blue, size = 132, label = 'ms · última noche' }) => {
  const cx = size / 2, cy = size / 2;
  const r = (size / 2) * 0.8;
  const sw = Math.round(size * 0.082); // stroke width scales with size

  // SVG angles: 0° = East, clockwise positive.
  // Gauge starts at SVG 135° (lower-left, ≈7:30 clock) sweeps 270° CW to SVG 45° (lower-right, ≈4:30 clock)
  const pt = (deg) => {
    const rad = deg * Math.PI / 180;
    return [+(cx + r * Math.cos(rad)).toFixed(2), +(cy + r * Math.sin(rad)).toFixed(2)];
  };

  const [sx, sy] = pt(135);
  const [ex, ey] = pt(45); // 135 + 270 = 405 → mod 360 = 45

  const p = Math.max(0.015, Math.min(0.985, (value - min) / (max - min)));
  const activeAngle = 135 + p * 270;
  const [ax, ay] = pt(activeAngle);
  const laf = p * 270 > 180 ? 1 : 0;

  return React.createElement('div', { style: { position: 'relative', width: size, height: size, flexShrink: 0 } },
    React.createElement('svg', { width: size, height: size },
      // Track
      React.createElement('path', {
        d: `M ${sx} ${sy} A ${r} ${r} 0 1 1 ${ex} ${ey}`,
        fill: 'none', stroke: C.border, strokeWidth: sw, strokeLinecap: 'round',
      }),
      // Active arc
      React.createElement('path', {
        d: `M ${sx} ${sy} A ${r} ${r} 0 ${laf} 1 ${ax} ${ay}`,
        fill: 'none', stroke: color, strokeWidth: sw, strokeLinecap: 'round',
      }),
      // Dot indicator
      React.createElement('circle', { cx: ax, cy: ay, r: Math.round(sw * 0.47), fill: color }),
      // Value number
      React.createElement('text', {
        x: cx, y: cy + 5, textAnchor: 'middle',
        style: {
          fontFamily: "'Instrument Serif', Georgia, serif",
          fontSize: Math.round(size * 0.32), fontWeight: 300,
          fill: C.t1, letterSpacing: '-1.5px', fontVariantNumeric: 'tabular-nums',
        }
      }, value),
      // Sub-label
      React.createElement('text', {
        x: cx, y: cy + Math.round(size * 0.22), textAnchor: 'middle',
        style: { fontFamily: 'Inter, sans-serif', fontSize: 10, fill: C.t3 }
      }, label)
    )
  );
};

// ── HRV Sparkline ──────────────────────────────────────────

const Sparkline = ({ data, baseline, color = C.blue, height = 60 }) => {
  const W = 260, H = height;
  const pad = { l: 4, r: 4, t: 6, b: 6 };
  const minV = Math.min(...data, baseline * 0.9) - 1;
  const maxV = Math.max(...data, baseline * 1.1) + 1;
  const range = maxV - minV;

  const xv = (i) => pad.l + i * (W - pad.l - pad.r) / (data.length - 1);
  const yv = (v) => H - pad.b - ((v - minV) / range) * (H - pad.t - pad.b);

  const pts = data.map((v, i) => `${xv(i).toFixed(1)},${yv(v).toFixed(1)}`).join(' ');
  const bY = yv(baseline);
  const bandTop = yv(baseline * 1.06);
  const bandBot = yv(baseline * 0.94);

  return React.createElement('svg', {
    width: W, height: H, style: { display: 'block', width: '100%' },
    viewBox: `0 0 ${W} ${H}`, preserveAspectRatio: 'none',
  },
    // Band
    React.createElement('rect', {
      x: pad.l, y: bandTop, width: W - pad.l - pad.r, height: bandBot - bandTop,
      fill: color, fillOpacity: 0.07,
    }),
    // Baseline dash
    React.createElement('line', {
      x1: pad.l, y1: bY, x2: W - pad.r, y2: bY,
      stroke: C.t3, strokeWidth: 1, strokeDasharray: '3 3',
    }),
    // Line
    React.createElement('polyline', {
      points: pts, fill: 'none', stroke: color, strokeWidth: 2,
      strokeLinejoin: 'round', strokeLinecap: 'round',
    }),
    // Dots
    ...data.map((v, i) =>
      React.createElement('circle', {
        key: i, cx: xv(i), cy: yv(v),
        r: i === data.length - 1 ? 3.5 : 2.5,
        fill: color,
      })
    )
  );
};

// ── Sidebar ────────────────────────────────────────────────

const Sidebar = ({ active = 'Inicio' }) => {
  const items = [
    ['⌂', 'Inicio'],
    ['◆', 'Actividades'],
    ['♡', 'Salud'],
    ['▤', 'Ciencia'],
    ['◯', 'Perfil'],
  ];

  return React.createElement('div', {
    style: {
      width: 272, background: C.sidebar, display: 'flex', flexDirection: 'column',
      padding: '24px 0', flexShrink: 0, boxSizing: 'border-box', height: '100%',
    }
  },
    // Wordmark
    React.createElement('div', { style: { padding: '0 20px' } },
      React.createElement('div', {
        style: {
          fontFamily: "'Instrument Serif', Georgia, serif",
          fontSize: 30, fontWeight: 400, color: '#fff', lineHeight: 1,
        }
      }, 'liebre', React.createElement('span', { style: { color: C.blue } }, '.')),
      React.createElement('div', {
        style: { fontSize: 11, color: 'rgba(255,255,255,0.55)', marginTop: 5, fontFamily: 'Inter, sans-serif' }
      }, 'tu pacer con IA + ciencia')
    ),
    // Divider
    React.createElement('div', { style: { height: 1, background: 'rgba(255,255,255,0.08)', margin: '20px 0' } }),
    // Nav
    React.createElement('nav', { style: { flex: 1, padding: '0 12px' } },
      ...items.map(([icon, label]) => {
        const isActive = label === active;
        return React.createElement('div', {
          key: label,
          style: {
            display: 'flex', alignItems: 'center', gap: 10,
            padding: '10px 12px', borderRadius: 6, marginBottom: 2,
            background: isActive ? 'rgba(255,255,255,0.08)' : 'transparent',
          }
        },
          React.createElement('span', {
            style: { fontSize: 15, color: isActive ? '#fff' : 'rgba(255,255,255,0.5)', width: 20, textAlign: 'center' }
          }, icon),
          React.createElement('span', {
            style: {
              fontFamily: 'Inter, sans-serif', fontSize: 14, fontWeight: 500,
              color: isActive ? '#fff' : 'rgba(255,255,255,0.55)',
            }
          }, label)
        );
      })
    ),
    // Divider
    React.createElement('div', { style: { height: 1, background: 'rgba(255,255,255,0.08)', margin: '0 0 16px' } }),
    // User
    React.createElement('div', { style: { padding: '0 20px', display: 'flex', alignItems: 'center', gap: 10 } },
      React.createElement('div', {
        style: {
          width: 36, height: 36, borderRadius: '50%', background: C.blue,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 14, fontWeight: 700, color: '#fff', flexShrink: 0, fontFamily: 'Inter, sans-serif',
        }
      }, 'J'),
      React.createElement('div', null,
        React.createElement('div', { style: { fontSize: 14, color: '#fff', fontFamily: 'Inter, sans-serif', fontWeight: 500, lineHeight: 1.3 } }, 'José'),
        React.createElement('div', { style: { fontSize: 11, color: 'rgba(255,255,255,0.45)', fontFamily: 'Inter, sans-serif', lineHeight: 1.3 } }, 'dev · jose_dev_uid')
      )
    )
  );
};

// ── TopBar ─────────────────────────────────────────────────

const TopBar = ({ greeting, summary, date }) => (
  React.createElement('div', {
    style: {
      height: 60, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 24px', flexShrink: 0, background: C.pageBg,
      borderBottom: `1px solid ${C.border}`,
    }
  },
    React.createElement('div', null,
      React.createElement('div', { style: { fontFamily: 'Inter, sans-serif', fontSize: 18, fontWeight: 600, color: C.t1, lineHeight: 1.2 } }, greeting),
      React.createElement('div', { style: { fontFamily: 'Inter, sans-serif', fontSize: 12, color: C.t2, marginTop: 1 } }, summary)
    ),
    React.createElement('div', { style: { textAlign: 'right' } },
      React.createElement('div', { style: { fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 600, color: C.t3, textTransform: 'uppercase', letterSpacing: '0.06em' } }, 'HOY'),
      React.createElement('div', { style: { fontFamily: 'Inter, sans-serif', fontSize: 13, color: C.t2, marginTop: 2 } }, date)
    )
  )
);

// ── Card wrappers ──────────────────────────────────────────

const Card = ({ children, style = {}, dark = false, subtle = false }) =>
  React.createElement('div', {
    style: {
      background: dark ? C.sidebar : subtle ? C.subtle : C.cardBg,
      borderRadius: 8,
      padding: dark ? 24 : 20,
      boxShadow: dark ? 'none' : '0 1px 3px rgba(0,0,0,0.08)',
      position: 'relative', overflow: 'hidden',
      ...style,
    }
  }, children);

// ── Factor impact row card ─────────────────────────────────

const FactorCard = ({ name, detail, interpretation, impact, color, cite }) =>
  React.createElement(Card, { subtle: true, style: { marginBottom: 10, padding: '14px 16px' } },
    React.createElement('div', { style: { display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 } },
      React.createElement('div', { style: { flex: 1 } },
        React.createElement('div', { style: { fontFamily: 'Inter, sans-serif', fontSize: 13, fontWeight: 600, color: C.t1 } }, name),
        React.createElement('div', { style: { fontFamily: 'Inter, sans-serif', fontSize: 12, color: C.t3, marginTop: 2 } }, detail),
        interpretation && React.createElement('div', {
          style: { fontFamily: 'Inter, sans-serif', fontSize: 12, color: C.t2, marginTop: 5, lineHeight: 1.45 }
        }, interpretation),
        cite && React.createElement(CiteBadge, { text: cite })
      ),
      React.createElement('div', {
        style: {
          fontFamily: 'Inter, sans-serif', fontSize: 20, fontWeight: 700,
          color, fontVariantNumeric: 'tabular-nums', flexShrink: 0,
          lineHeight: 1, paddingTop: 2,
        }
      }, impact > 0 ? `+${impact}` : `−${Math.abs(impact)}`)
    )
  );

// ── Footer ─────────────────────────────────────────────────

const LiebreFooter = () =>
  React.createElement('div', {
    style: {
      padding: '8px 24px', textAlign: 'center',
      fontFamily: 'Inter, sans-serif', fontSize: 11, color: C.t3,
      borderTop: `1px solid ${C.border}`, flexShrink: 0,
    }
  }, 'Datos en vivo · API localhost:8080 · ver Swagger · Diseño basado en Garmin Connect + capa Liebre');

// ── Stat block (label / value pair) ───────────────────────

const StatBlock = ({ label, value, color }) =>
  React.createElement('div', null,
    React.createElement('div', {
      style: {
        fontFamily: 'Inter, sans-serif', fontSize: 10, fontWeight: 500,
        color: C.t3, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 2,
      }
    }, label),
    React.createElement('div', {
      style: {
        fontFamily: 'Inter, sans-serif', fontSize: 16, fontWeight: 600,
        color: color || C.t1, fontVariantNumeric: 'tabular-nums',
      }
    }, value)
  );

Object.assign(window, {
  C, UpperLabel, StatusPill, CiteBadge, LiebreInterp,
  Gauge, Sparkline, Sidebar, TopBar, Card, FactorCard, LiebreFooter, StatBlock,
});
