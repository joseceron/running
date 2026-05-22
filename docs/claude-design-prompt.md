# Prompt para Claude Design — Dashboard de Liebre

> Pega esto en Claude Design (claude.ai con el modelo de diseño). Genera mockups de alta fidelidad del dashboard para validar el look antes de iterar el código. Optimizado para que devuelva mockups que coincidan con el frontend que ya construimos.

---

## El prompt (copia todo lo de adentro del bloque)

```
Diseña la pantalla principal del dashboard de un producto SaaS llamado
LIEBRE — un agente de IA para corredores que combina datos biomecánicos de
Garmin (HRV, running dynamics, Body Battery, VO₂max) con literatura
científica (Scopus, Web of Science) para generar planes de entrenamiento
adaptativos.

POSICIONAMIENTO: deportivo · tecnológico · profesional · fresco. NO
minimalista frío estilo Apple Health. NO sobrecargado estilo Strava.
Tono: "Garmin Connect rediseñado por una agencia de producto premium con
una capa de inteligencia que Connect no tiene".

DIFERENCIADOR VISUAL ÚNICO: cada métrica viene con una capa de
"Interpretación Liebre" — un párrafo de texto explicativo causal +
una cita de paper científico como badge azul (formato:
"📄 Plews & Buchheit (2017) · J Strength Cond Res · Observacional").
Esa es la firma del producto. Hazla visible pero no invasiva.

═══════════════════════════════════════════════════════════════════
SISTEMA DE DISEÑO (basado en investigación visual real de Garmin Connect)
═══════════════════════════════════════════════════════════════════

PALETA EXACTA (no inventar otros tonos):
- Sidebar negra:        #1A1A1A
- Fondo de página:      #F5F5F5
- Fondo de card:        #FFFFFF
- Fondo card sutil:     #F9FAFB
- Texto principal:      #1C1C1C
- Texto secundario:     #6B7280
- Texto terciario:      #9CA3AF
- Acento marca (azul):  #1976D2  (Connect blue — botones, tabs activos,
                                 línea principal HRV, dot indicador del gauge)
- Acento marca soft:    #3B97F3
- Naranja running:      #F5A623  (íconos de actividad, badge corredor)

Semánticos:
- Verde positivo:       #16A544  (estados Equilibrado, Óptimo, impactos +)
- Naranja alerta:       #F27716  (estados Bajo, Moderado, ACWR amber)
- Rojo peligro:         #E02C2C  (Suprimido, sobrecarga, impactos −)
- Neutro:               #9CA3AF

Zonas de frecuencia cardíaca:
- Z1 calentamiento:     #9CA3AF  (gris)
- Z2 fácil:             #3B82F6  (azul)
- Z3 aeróbico:          #22C55E  (verde)
- Z4 umbral:            #FBBF24  (ámbar)
- Z5 máximo:            #EF4444  (rojo)

TIPOGRAFÍA:
- Display (números grandes): Instrument Serif (o serif similar elegante),
  peso 300, tamaño 48-64px, tabular figures, letter-spacing -0.04em.
  USO: "52" en gauge HRV, "21K" en card de meta, "133" en countdown.
- Body: Inter, peso 400, 14px, line-height 1.5
- KPIs medianos: Inter peso 600, 24-32px, tabular
- Labels uppercase: Inter peso 500, 11px, letter-spacing 0.06em, color
  #9CA3AF. Ejemplos: "VFC NOCTURNA", "TU META", "DISTANCIA"
- TODOS los números deben usar font-variant-numeric: tabular-nums

COMPONENTES BASE:
- Card estándar: fondo blanco #FFFFFF, border-radius 8px, sombra muy sutil
  box-shadow: 0 1px 3px rgba(0,0,0,0.08), padding 20px. SIN BORDER VISIBLE.
- Card oscura: fondo #1A1A1A, texto blanco, mismo radius, padding 24px.
  Usada solo para destacar UN elemento heroico (la meta del corredor).
- Card sutil: fondo #F9FAFB, radius 8px, padding 16px. Para
  row-factor cards.
- Status pill: pequeño, redondeado completo (radius 999px), padding
  4px 10px, fuente 12px peso 600. El fondo es color semántico al 12-14%
  (translúcido), el texto es el color sólido. Llevan un dot circular de
  8px del mismo color a la izquierda.
- Sidebar: ancho exacto 272px, fondo #1A1A1A, texto blanco al 100% para
  activo, blanco al 60% para inactivos. Wordmark "liebre." arriba (con
  el punto en color azul #1976D2). Items con ícono SVG outline 18px +
  texto medium 14px.

═══════════════════════════════════════════════════════════════════
LAYOUT EXACTO DEL DASHBOARD A DISEÑAR
═══════════════════════════════════════════════════════════════════

Es desktop, viewport 1440x900 idealmente.

┌──────────┬─────────────────────────────────────────────────────────┐
│          │  TopBar (sin fondo, 64px de alto)                       │
│ SIDEBAR  │  "Buenas tardes, José"            HOY                   │
│ 272px    │  resumen del día           jueves, 21 de mayo           │
│ NEGRA    │                                                         │
│ #1A1A1A  ├─────────────────────────────────────────────────────────┤
│          │                                                         │
│ liebre.  │  ┌──────────────────────────────┐ ┌───────────────────┐ │
│ (32px)   │  │ ⭐ DIAGNÓSTICO DEL DÍA        │ │ ⚫ TU META          │ │
│          │  │ (span 2 cols, fondo blanco)  │ │ (card oscura)     │ │
│ tu pacer │  │                              │ │                   │ │
│ IA+cien. │  │ [Avatar circular azul "L"]   │ │ TU META           │ │
│          │  │ DIAGNÓSTICO DEL DÍA          │ │                   │ │
│ ───      │  │ análisis cruzado por agente  │ │   21K             │ │
│          │  │                              │ │   (serif gigante) │ │
│ ⌂ Inicio │  │ "Aún estamos construyendo    │ │ en 1h50           │ │
│ ◆ Activ. │  │  tu baseline personal de     │ │ · 2026-10-01      │ │
│ ♡ Salud  │  │  HRV (8 de 14 noches         │ │                   │ │
│ ▤ Ciencia│  │  recolectadas)..."           │ │   133             │ │
│ ◯ Perfil │  │                              │ │   días por delante│ │
│          │  │ ─────────────────────────    │ │                   │ │
│ ───      │  │ ACCIÓN RECOMENDADA           │ │ Progreso  60%     │ │
│          │  │ "Sincroniza tu Garmin..."    │ │ ━━━━━━━━━━━━━━━━  │ │
│ [avatar  │  │                              │ │                   │ │
│  azul J] │  │ 📄 Seiler (2010) · IJSPP     │ │                   │ │
│ José     │  │    · Review polarizada 80/20 │ │                   │ │
│ jose_dev │  └──────────────────────────────┘ └───────────────────┘ │
│          │                                                         │
│          │  ┌──────────────────────────────┐ ┌───────────────────┐ │
│          │  │ 🔵 VFC NOCTURNA               │ │ TU PERFIL          │ │
│          │  │ (span 2 cols)                │ │                   │ │
│          │  │                              │ │ José Luis Cerón   │ │
│          │  │ VFC NOCTURNA      [pill]     │ │                   │ │
│          │  │ Media últimos 8d   building   │ │ Edad      36       │ │
│          │  │                              │ │ Peso      67.8 kg │ │
│          │  │ ╭─────╮                      │ │ Altura    170 cm  │ │
│          │  │ │ Gauge│   Baseline  55 ms   │ │ FC máx    190 lpm │ │
│          │  │ │ 52 ms│   Delta     -5%     │ │ FC reposo 51 lpm  │ │
│          │  │ ╰─────╯   Días      8/14     │ │                   │ │
│          │  │                              │ │                   │ │
│          │  │ [sparkline azul de 8 puntos │ │                   │ │
│          │  │  con banda sombreada del    │ │                   │ │
│          │  │  rango personal al 6% opac.]│ │                   │ │
│          │  │                              │ │                   │ │
│          │  │ Progreso baseline ━━━━━━━□  │ │                   │ │
│          │  │ 8/14                         │ │                   │ │
│          │  │ ─────────────────────────    │ │                   │ │
│          │  │ 📊 INTERPRETACIÓN LIEBRE     │ │                   │ │
│          │  │ "Tu HRV de 52 ms está dentro │ │                   │ │
│          │  │  del rango funcional..."     │ │                   │ │
│          │  │ 📄 Plews & Buchheit (2017)   │ │                   │ │
│          │  └──────────────────────────────┘ └───────────────────┘ │
│          │                                                         │
│          │  ┌──────────────────────────────┐ ┌───────────────────┐ │
│          │  │ FACTORES QUE INFLUYEN        │ │ HISTORIAL SEMANAL │ │
│          │  │ EN TU ESTADO                 │ │ últimas 2 semanas │ │
│          │  │                              │ │                   │ │
│          │  │ ┌──────────────────┐         │ │ ┌──┬──┬──┬──┬──┐ │ │
│          │  │ │ Sueño    +41     │ verde   │ │ │Sem│Pln│Eje│HRV│ACWR│ │
│          │  │ │ 6h 32m           │         │ │ ├──┼──┼──┼──┼──┤ │ │
│          │  │ └──────────────────┘         │ │ │5/11│25│19.9│53│0.95│ │
│          │  │                              │ │ │5/18│28│10.1│56│[1.05]│ │
│          │  │ ┌──────────────────┐         │ │ │   │   │   │   │↑verde│
│          │  │ │ Carrera   -11    │ rojo    │ │ └──┴──┴──┴──┴──┘ │ │
│          │  │ │ Popayán 5.22km   │         │ │                   │ │
│          │  │ │                  │         │ │ NOTA DEL AGENTE   │ │
│          │  │ │ "Carrera Z2 con- │         │ │ "Semana en curso  │ │
│          │  │ │  trolada..."     │         │ │  FC reposo baja-  │ │
│          │  │ └──────────────────┘         │ │  ndo 56→50 lpm"   │ │
│          │  │                              │ │                   │ │
│          │  │ ┌──────────────────┐         │ │                   │ │
│          │  │ │ ACWR     +8      │         │ │                   │ │
│          │  │ │ 1.05             │         │ │                   │ │
│          │  │ │ "Zona segura..." │         │ │                   │ │
│          │  │ │ 📄 Gabbett 2016  │         │ │                   │ │
│          │  │ └──────────────────┘         │ │                   │ │
│          │  └──────────────────────────────┘ └───────────────────┘ │
│          │                                                         │
│          │  footer pequeño centrado:                              │
│          │  Datos en vivo · API localhost:8080 · ver Swagger        │
│          │  diseño basado en Garmin Connect + capa Liebre          │
└──────────┴─────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════
DETALLES CRÍTICOS DE LOS COMPONENTES
═══════════════════════════════════════════════════════════════════

GAUGE CIRCULAR 270° (en la HRV card):
- Tamaño: 148px x 148px
- Arco va de las 7 a las 5 en posición de reloj (270° de barrido)
- Grosor del arco: 12px
- Track (gris): #E5E7EB
- Arco activo: del color del estado (azul #1976D2 para Equilibrado,
  ámbar #F27716 para Bajo, rojo #E02C2C para Suprimido)
- Dot indicador: círculo sólido del mismo color, ~10px, posicionado en
  el extremo del arco activo
- Número central: tipografía display serif 48-52px peso 300, ej. "52"
- Subtexto: 12px gris #9CA3AF, ej. "ms · última noche"

SPARKLINE DE HRV (8 puntos):
- Línea continua azul #1976D2, grosor 2px, strokeLinejoin round
- Banda sombreada del rango personal: rect azul #1976D2 con opacity 0.06
- Línea horizontal de baseline: gris #9CA3AF dasharray "3 3"
- Cada noche: dot azul #1976D2 de 2.5px (el último un poco más grande)
- Eje X: implícito (sin labels), las 8 noches igualmente espaciadas

DIAGNÓSTICO DEL DÍA CARD:
- Header con avatar circular azul (32px) con letra "L" blanca
- Título "DIAGNÓSTICO DEL DÍA" en label uppercase
- Subtítulo "Análisis cruzado generado por tu agente" en 12px gris
- Cuerpo: párrafo en texto principal 16px peso 400 line-height 1.6
- Separador (hairline border-top #E5E7EB con padding 16px arriba)
- "ACCIÓN RECOMENDADA PARA HOY" label uppercase
- Acción: párrafo 14px peso 500 color #1C1C1C
- Cita: 12px peso 500 color #1976D2 (azul brand), formato "📄 ..."
- Tinte de fondo decorativo: radial-gradient azul con opacity 0.05 en
  esquina superior derecha

TU META CARD (la oscura):
- Fondo sólido #1A1A1A, texto blanco #FFFFFF
- "TU META" en label uppercase con opacity 0.6
- Métrica gigante "21K" en serif 64px peso 300 BLANCO
- Subtítulo "en 1h50 · 2026-10-01" en 14px opacity 0.8
- Bloque countdown: número grande azul soft "133" + label "días por delante"
- Barra de progreso 4px alto, fondo blanco 10% opacity, fill azul soft
- Decoración: radial-gradient azul soft con opacity 0.15 en esquina
  inferior derecha (sutil glow)

FACTOR IMPACT CARDS (3-4 cards apiladas verticalmente):
- Cada una es una card sutil (#F9FAFB, radius 8px, padding 16px)
- Layout horizontal: [Nombre + valor abajo en gris] ↔ [Impacto signed grande]
- Impacto positivo: color verde #16A544 con signo "+" delante. Ej "+41"
- Impacto negativo: color rojo #E02C2C con signo "−" delante. Ej "-11"
- Cifra del impacto: 20px tabular, peso 600
- Opcionalmente con sección expansible: interpretación 12px gris +
  cita en pill azul

SIDEBAR:
- Wordmark "liebre." en serif 32px peso 400, blanco, con el punto final
  en azul #1976D2 (el punto es el que hace branding)
- Tagline "tu pacer con IA + ciencia" 11px gris claro (white 60%)
- Items: padding 10px 12px, radius 6px. Activo con fondo white 8%.
  Ícono SVG outline 18px + texto medium 14px
- Avatar abajo: círculo 36px azul brand con letra "J" blanca peso 600,
  al lado nombre "José" 14px + "dev · jose_dev_uid" 12px en gris claro

═══════════════════════════════════════════════════════════════════
QUÉ QUIERO QUE GENERES
═══════════════════════════════════════════════════════════════════

3 mockups en alta fidelidad, formato 1440x900 cada uno:

1. **Vista principal del dashboard** (la composición completa descrita
   arriba). Datos de ejemplo: José Luis Cerón, 36 años, meta 21K en
   1h50 el 2026-10-01 (faltan 133 días), HRV 52 ms con baseline 55 ms,
   status "Construyendo baseline" 8/14 noches.

2. **Vista del dashboard con DATOS ÓPTIMOS** (todo en verde, status
   "Equilibrado"): mismo layout pero gauge HRV en verde #16A544,
   diagnóstico positivo "Sistema autónomo recuperado, listo para Z4-Z5",
   factores con impactos mayormente positivos. Útil para mostrar cómo se
   ve la "experiencia ideal" del producto.

3. **Estado mobile** del dashboard (375x812, viewport iPhone). Mismo
   contenido pero colapsado: sidebar se convierte en bottom navigation
   bar negra, cards van en columna única, gauge HRV centrado, factor
   cards full-width. Mantener la misma jerarquía.

CRITERIOS DE CALIDAD:
- Coherencia tipográfica (serif para display, sans para body, tabular
  para números)
- Sombras y radios CONSISTENTES (no inventar otros)
- Cero emojis distintos de los listados (📊 📄 ⭐ ⚫ 🔵 ⌂ ◆ ♡ ▤ ◯)
- Cero gradients estridentes
- Espaciado generoso (padding 20-24px en cards, gap 16px entre cards)
- Densidad MEDIA (Connect-like, no Strava)

Devuelve los 3 mockups en una sola entrega con anotaciones cortas al
margen explicando decisiones clave (por qué el diagnóstico va arriba,
por qué el gauge azul, etc.).
```

---

## Cómo usarlo

1. Abre **claude.ai** en una conversación nueva (preferiblemente con un modelo de diseño habilitado, o un proyecto/skill de "design").
2. Pega TODO lo que está dentro del bloque ` ``` ` de arriba.
3. Si el modelo te ofrece "mejorar el prompt" antes de generar, acepta — suele afinar el resultado.
4. Cuando recibas los mockups:
   - Guarda los PNGs en `docs/mockups/` (haz commit)
   - Si algo no convence, dime qué ajustar (p.ej. "el HRV card es muy denso", "el sidebar debería ser más estrecho") y vuelvo a iterar el prompt.

## Lo que YO hago cuando lleguen los mockups

1. Comparo el render actual de `localhost:3002/dashboard` con el mockup.
2. Identifico gaps de diseño concretos (espaciado, color, jerarquía).
3. Ajusto los componentes para alinear con el mockup aprobado.
4. Repito hasta que coincida o quede como tú quieres.
