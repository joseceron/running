# Inventario visual de Garmin Connect para Liebre

> Investigación realizada el 21/05/2026. Cuenta: Joselo. Dispositivo: Forerunner 965, software 27.09.
> Idioma de la interfaz: Español (Colombia). URL base: https://connect.garmin.com/app/

---

## 1. Resumen ejecutivo

### 3 cosas que Connect hace excelente y debemos replicar

**1. Sistema de "semáforo por factores contributivos."**
En Predisposición para entrenar, HRV y Estado de entreno, cada variable que compone el score aparece como una row-card horizontal: [Nombre + valor numérico abajo] → [Etiqueta verbal a la derecha] → [Dot de color]. El usuario escanea en 3 segundos qué pesa en su estado del día. Liebre debe replicar esta arquitectura y agregarle la capa causal: "tu carga aguda bajó a 132 (Baja) porque tus últimas 3 sesiones fueron Z2 ≤60 min, lo que permite supercompensación — ver Bangsbo et al., 2013, J Sports Sci, RCT".

**2. La cronología de 24 horas de Body Battery + Estrés.**
Un gráfico de combinación multi-serie con: línea de Body Battery (negro), barras de Descanso (azul #3B82F6), barras de Estrés (naranja #FB923C), barras de Sueño (azul oscuro #1D4ED8), marcadores de Actividad (dot verde). Sobre eje temporal continuo de medianoche a medianoche. Es la visualización más rica de Connect: narra el día completo en una sola imagen. Liebre puede replicarla en el panel diario y añadir una capa de interpretación sobre el timeline.

**3. Los gráficos Highcharts sincronizados en stack vertical.**
En la vista de actividad, cada métrica tiene su propio gráfico de ~130px de alto, todos con el mismo eje X (tiempo o distancia), con crosshair vertical compartido al hacer hover. El resultado permite correlacionar visualmente Ritmo ↔ FC ↔ Cadencia ↔ GCT ↔ Potencia sin sobrecargar un solo canvas. La arquitectura de gráficos sincronizados es la forma correcta de mostrar dinámicas de carrera y Liebre debe adoptarla.

### 3 limitaciones que Liebre supera con IA + ciencia

**1. Datos sin interpretación causal.**
Connect presenta métricas pero nunca explica el "por qué" ni el "qué hacer". El único texto interpretativo es de marketing ("Bien descansado, un buen sueño ha mejorado tu predisposición"). No hay causalidad, no hay paper, no hay recomendación accionable específica. Este es el mayor gap que Liebre cierra.

**2. Baseline de VFC poblacional, no personal adaptativo.**
Connect construye un "valor de referencia" con ~3 semanas de datos y lo mantiene fijo. No detecta tendencias de largo plazo ni alerta cuando la VFC se desvía significativamente del rolling average personal. Liebre puede calcular percentiles propios con ventana deslizante de 28 días y clasificar la desviación diaria en términos estadísticos (±1σ, ±2σ).

**3. Silos de datos: sin integración longitudinal entre módulos.**
Sueño, VFC, Training Load, FC en reposo, Estrés viven en páginas separadas. Connect nunca cruza: "tu sueño fue corto (6h 32m) PERO tu VFC se mantuvo equilibrada (55ms) porque tu carga aguda fue baja (132)". Liebre construye un "Diagnóstico del día" que narrativice cómo interactúan todas las señales.

### Patrones visuales recurrentes

- **Sidebar negra izquierda fija** (~265px) con íconos de deporte monocromos blancos.
- **Content area blanca** con padding generoso (~32px lateral).
- **Cards blancas** sin borde visible, sombra sutil `0 1px 3px rgba(0,0,0,0.08)`, `border-radius: 8px`.
- **Gauge circular de 270°** (donut) como widget universal de "score en 1 número" en todas las páginas de salud.
- **Segmented control** ("1 día / 7 días / 4 semanas") como control temporal universal.
- **Row-factor card** como patrón de descomposición de score en sub-factores.
- **Colores semánticos consistentes**: verde = positivo, naranja = alerta, rojo = peligro, gris = neutro/sin datos.

---

## 2. Sistema de diseño extraído

### Paleta global

| Token | Hex aprox. | Uso |
|---|---|---|
| `--bg-sidebar` | `#1A1A1A` | Fondo de sidebar izquierda |
| `--bg-content` | `#FFFFFF` | Fondo del área principal de contenido |
| `--bg-page` | `#F5F5F5` | Fondo de página / separadores entre secciones |
| `--ink-primary` | `#1C1C1C` | Texto principal, números grandes, títulos |
| `--ink-secondary` | `#6B7280` | Labels, subtítulos, unidades, metadatos |
| `--ink-tertiary` | `#9CA3AF` | Captions, texto deshabilitado, placeholders |
| `--ink-sidebar` | `#FFFFFF` | Texto e íconos en sidebar |
| `--accent-brand` | `#1976D2` | Botones primarios, tab activo, links, donut Body Battery |
| `--accent-orange` | `#F5A623` | Íconos de actividad de carrera, alertas medias |
| `--semantic-green` | `#4CAF7D` | Positivo: Equilibrado, Óptimo, Excelente, Bien |
| `--semantic-amber` | `#F5A623` | Alerta: Bajo, Moderado, Aceptable |
| `--semantic-red` | `#E53935` | Peligro: Desequilibrado, Alto estrés, Rojo FC |
| `--semantic-gray` | `#9CA3AF` | Neutro: Sin datos, Inactivo, Valor de referencia |
| `--chart-hr-fill` | `#FECACA` | Área rellena de Frecuencia cardiaca |
| `--chart-hr-line` | `#EF4444` | Línea de Frecuencia cardiaca |
| `--chart-pace-fill` | `#BAD8F7` | Área rellena de Ritmo |
| `--chart-pace-line` | `#3B82F6` | Línea de Ritmo |
| `--chart-altitude-fill` | `#BBF7D0` | Área rellena de Altitud |
| `--chart-altitude-line` | `#22C55E` | Línea de Altitud |
| `--chart-power-fill` | `#BFDBFE` | Área rellena de Potencia |
| `--chart-power-line` | `#2563EB` | Línea de Potencia |
| `--chart-cadence-good` | `#22C55E` | Puntos scatter de cadencia en rango óptimo |
| `--chart-cadence-mid` | `#F97316` | Puntos scatter de cadencia variable |
| `--chart-cadence-low` | `#EF4444` | Puntos scatter de cadencia baja |
| `--chart-stress-bars` | `#FB923C` | Barras de Estrés en cronología 24h |
| `--chart-rest-bars` | `#3B82F6` | Barras de Descanso en cronología 24h |
| `--chart-bb-line` | `#1C1C1C` | Línea principal de Body Battery |
| `--chart-sleep-bars` | `#1D4ED8` | Barras de Sueño en cronología |
| `--chart-activity-dot` | `#22C55E` | Marcador de Actividad en cronología |
| `--hrv-ref-band` | `#D1D5DB` | Banda de rango de referencia VFC (área gris) |
| `--hrv-dot-balanced` | `#22C55E` | Punto VFC estado Equilibrado |
| `--hrv-dot-unbalanced` | `#F97316` | Punto VFC estado Desequilibrado |
| `--hrv-dot-low` | `#EF4444` | Punto VFC estado Bajo |
| `--sleep-deep` | `#1D4ED8` | Sueño Profundo |
| `--sleep-light` | `#60A5FA` | Sueño Ligero |
| `--sleep-rem` | `#C084FC` | Sueño MOR/REM |
| `--sleep-awake` | `#FCD34D` | Despierto |
| `--zone1-color` | `#9CA3AF` | Z1 Calentamiento (103–122 ppm) |
| `--zone2-color` | `#3B82F6` | Z2 Suave (123–143 ppm) |
| `--zone3-color` | `#22C55E` | Z3 Aeróbica (144–163 ppm) |
| `--zone4-color` | `#FBBF24` | Z4 Umbral (164–184 ppm) |
| `--zone5-color` | `#EF4444` | Z5 Máximo (>185 ppm) |
| `--ts-recovering` | `#3B82F6` | Estado entreno: Recuperación (azul) |
| `--ts-base` | `#6B7280` | Estado entreno: Base (gris) |
| `--ts-productive` | `#9333EA` | Estado entreno: Productivo (morado) |
| `--ts-maintaining` | `#22C55E` | Estado entreno: Mantenimiento (verde) |
| `--ts-peaking` | `#F97316` | Estado entreno: En forma (naranja) |
| `--ts-overreaching` | `#EF4444` | Estado entreno: Sobrecarga (rojo) |
| `--ts-detraining` | `#EAB308` | Estado entreno: Desentrenamiento (amarillo) |

### Tipografía

Connect no declara explícitamente una fuente de marca; el sistema usa la sans-serif del sistema (probablemente `-apple-system / BlinkMacSystemFont / Segoe UI / Roboto`). Inferido por comportamiento visual:

- **Display / Números de score grandes**: sans-serif, peso 300–400, 44–64px, tabular figures. Ej: "79" Training Readiness, "55" HRV, "81" Sleep Score.
- **H1 / Títulos de página**: sans-serif, peso 300–400, 28–36px, color `#1C1C1C`. Ej: "Estado de VFC", "Body Battery", "Predisposición para entrenar".
- **H2 / Subtítulos de sección**: sans-serif, peso 400–500, 16–20px. Ej: "Resumen", "Cronología nocturna", "Factores".
- **KPI numérico de headline** (en listas y actividades): sans-serif, peso 600–700, 24–32px, tabular. Ej: "5.22 km", "9:21 /km".
- **Body / Texto interpretativo**: sans-serif, peso 400, 14px, line-height 1.5, color `#4B5563`.
- **Label / Unidades y columnas de tabla**: ALL CAPS, peso 400, 11px, letter-spacing 0.05em, color `#9CA3AF`. Ej: "DISTANCIA", "RITMO MEDIO", "FRECUENCIA CARDIA...".
- **Caption / Fechas, timestamps**: sans-serif, peso 400, 12px, color `#6B7280`.
- **Pesos observados**: 300 (display ligero), 400 (body), 500 (énfasis medio), 600–700 (KPIs y botones).
- **Tabular figures**: SÍ, se usan en todos los valores numéricos de métricas para alineación vertical en tablas y listas.

### Componentes recurrentes

**Card estándar**
Fondo `#FFFFFF`, `border-radius: 8px`, `box-shadow: 0 1px 3px rgba(0,0,0,0.08)`, padding `16–20px`. Sin border visible en estado normal. En hover o estado activo, algunas cards muestran un borde izquierdo de 3px en color de acento.

**Gauge circular (donut 270°)**
Presente en: Home, HRV, Body Battery, Estrés, Sueño (donut completo), Training Readiness. Grosor del arco: ~12–14px. El arco de 270° va de las 7 a las 5 (como las manecillas de un reloj). El segmento activo se colorea según el valor. El número central usa tipografía Display. Subtexto "100" o el máximo en tiny (~12px) debajo del número central. El punto activo es un dot sólido de ~12px de diámetro posicionado sobre el arco. Tamaño del widget: ~120–160px de diámetro.

**Segmented control de tiempo**
Fila de tabs adyacentes ("1 día / 7 días / 4 semanas / 1 año") con: fondo inactivo `#E5E7EB`, fondo activo `#1976D2` texto blanco, `border-radius: 6px`, height `32–36px`, padding horizontal `16px`. Variante en Training Readiness usa solo flechas `‹ ›` + fecha en botón.

**Row-factor card**
Card horizontal para descomponer un score en sub-factores. Estructura: [Nombre (bold, izquierda)] + [Valor numérico + unidad debajo del nombre, `#6B7280`] ← → [Label verbal (derecha, `#6B7280`)] + [Dot de color 8px (derecha)]. `border-radius: 8px`, fondo `#F9FAFB`, padding `16px`, separación entre rows `8px`. Ejemplo: "Estado de VFC / 55 ms ← → Equilibrado ●verde".

**Tooltip de ayuda "?"**
Círculo de ~18px con "?" en gris `#9CA3AF`. Hover muestra panel lateral con explicación técnica detallada de la métrica.

---

## 3. Tokens REALES extraídos del DOM de Connect

Estos son los `--data-viz-*` que Connect usa internamente (verificados con JS sobre `:root`, no estimados visualmente):

```css
/* Data viz primarios */
--data-viz-green-primary:    #16a544
--data-viz-green-secondary:  #40c35d
--data-viz-red-primary:      #e02c2c
--data-viz-red-secondary:    #f85454
--data-viz-blue-primary:     #1976d2
--data-viz-blue-secondary:   #3b97f3
--data-viz-orange-primary:   #f27716
--data-viz-orange-secondary: #fd9d39
--data-viz-purple-primary:   #6f42f3
--data-viz-purple-secondary: #9370f9
--data-viz-violet-primary:   #d42fc2
--data-viz-violet-secondary: #e55ecb
--data-viz-teal-primary:     #15aabf
--data-viz-yellow-primary:   #faca48
--data-viz-neutral-primary:  #000000
--data-viz-neutral-secondary:#a6a6a6

/* Semánticos específicos */
--color-orange-60:           #de5809   /* estrés alto */
--color-green-primary:       #16a544
--color-blue-primary:        #1976d2
--color-orange-primary:      #f27716
```

**Estos son los hex que vamos a usar en Liebre** (sobreescriben las aproximaciones visuales de la Sección 2). El sistema de pares `primary/secondary` (oscuro/claro) es útil para tener variantes de la misma familia.

---

## 4. Inventario por página

### Página 5: Sueño

> **Nota:** la extensión etiquetó esta página como "HRV" pero las URLs y el contenido confirman que es **Sueño** (`https://connect.garmin.com/app/sleep`). Las páginas HRV, Body Battery y Stress quedan pendientes de un sub-prompt adicional.

**URL:** `https://connect.garmin.com/app/sleep`
**Tecnología de gráficos:** Recharts (React) para vistas 7d/4sem/1año. Highcharts 11.4.1 para cronología nocturna de 1 día.

#### Layout (de arriba abajo)

```
┌──────────────────────────────────────────────────────────────┐
│  TOPBAR: [← Anterior] [📅 May 21 ▾] [Siguiente →]            │
│          [1 día*] [7 días] [4 semanas] [1 año]               │
│          [Tab: Puntuación de sueño] [Tab: Entrenador de sueño]│
├──────────────────────┬───────────────────────────────────────┤
│  PUNTUACIÓN (~40%)   │  FACTORES DE PUNTUACIÓN (~60%)        │
│                      │                                       │
│  Puntuación de sueño │  ┌──────────────────────────────┐    │
│       81             │  │ Duración    6h 32m  Aceptable │    │
│       100            │  │ Estrés      14      Medio     │    │
│  [Campo NOTAS libre] │  │ ...                           │    │
├──────────────────────┴───────────────────────────────────────┤
│  CRONOLOGÍA (ancho completo)                                 │
│  [Tab: Fases]   (único tab visible)                          │
│                                                              │
│  [Donut de stages: 225×225]  │ [Breakdown numérico]         │
│        6h 32m                │  2h 11m Profundo              │
│     Total dormidas           │  2h 32m Ligero                │
│                              │  1h 49m MOR                   │
│                              │  9m     Despierto             │
├──────────────────────────────────────────────────────────────┤
│  [Hypnogram timeline 6h41m con franjas por stage]            │
├──────────────────────────────────────────────────────────────┤
│  [Cronología de estrés durante el sueño]                     │
└──────────────────────────────────────────────────────────────┘
```

#### Visualizaciones clave

**Score numérico grande:** "81" display 52px, "100" subscript 14px gris, label "PUNTUACIÓN" ALL CAPS 11px.

**Donut de stages (Pie chart Highcharts 360°, 225×225px):**
- Centro: "6h 32m" bold 24px + "Total dormidas" caption 11px
- Profundo (2h 11m, ~33%) → `--data-viz-blue-primary` (#1976d2)
- Ligero (2h 32m, ~39%) → `--data-viz-blue-secondary` (#3b97f3)
- MOR/REM (1h 49m, ~27%) → `--data-viz-violet-primary` (#d42fc2)
- Despierto (9m, ~2%) → `--data-viz-neutral-primary` (#000000)
- Hover: slice se "explota" hacia afuera + tooltip con nombre/duración/%
- Sin leyenda gráfica; breakdown a la derecha como lista con dots de color.

**Hypnogram (timeline de fases — Highcharts area multi-serie):**
- Eje X: tiempo `2026-05-20 23:44` → `2026-05-21 06:25` (6h 41min). Etiquetas: 12a, 2a, 4a, 6a.
- Eje Y: niveles discretos 1-6 (sin labels visibles), representando los stages como alturas.
- 17 series superpuestas que forman franjas horizontales a distintas Y (Y=1 profundo, Y=2 ligero, Y=3 REM, Y=4 despierto).
- Forma "hypnogram" — el usuario ve la arquitectura del sueño a lo largo de la noche.
- ⚠️ **Bug detectado**: el hypnogram invierte los colores del donut (en hypnogram, Profundo = azul SECUNDARIO; en donut, Profundo = azul PRIMARIO). Liebre NO debe replicar este bug — mantenemos consistencia.
- Leyenda: labels directas sobre las franjas ("Profundo", "Ligero", "MOR", "Despiert..." truncado).

**Cronología de estrés durante el sueño:**
- Combination chart Highcharts, 6 series, 3 pares de ejes X/Y.
- Barras verticales superpuestas sobre la línea temporal del sueño.
- Eje Y: -5 a 100.
- Barras naranja (`#de5809`) = estrés alto durante sueño = menos recuperación.
- (El output se cortó en este punto — falta el detalle de las series inferiores.)

#### Métricas mostradas

| Métrica | Unidad | Formato | Contextualización |
|---|---|---|---|
| Puntuación de sueño | 0-100 | Entero (81) | "/100" subscript |
| Duración total | h + min | "6h 32m" | Etiqueta "Aceptable / Buena / Excelente" |
| Sueño profundo | h + min | "2h 11m" | % del total + dot color |
| Sueño ligero | h + min | "2h 32m" | idem |
| MOR/REM | h + min | "1h 49m" | idem |
| Despierto | min | "9m" | idem |
| Estrés durante sueño | 0-100 | Entero (14) | "Medio" |

#### Tono y voz
- Métricas con sustantivos puros ("Profundo", "Ligero", "MOR").
- Etiquetas evaluativas en row-factor ("Aceptable", "Medio").
- Campo de notas libre para que el usuario agregue contexto subjetivo.
- Sin texto interpretativo del por qué.

---

### Página 1: HRV (Estado de VFC)

**URL:** `https://connect.garmin.com/app/hrv-status`
**Tecnología:** Highcharts

**Layout:** Arriba tabs `1 día / 7 días (default) / 4 semanas + Resumen`. Centro: gran número `55` con etiqueta "Media de 7 días", dos sub-métricas debajo (`52 ms` nocturna, `87 ms` máximo 5 min), badge de estado `Equilibrado` y párrafo interpretivo. Abajo: "Cronología nocturna" con gráfico de línea de la última noche.

**Insight crítico (NO es un gauge tradicional):** el "gauge principal" NO es un semicírculo. Es un chart Highcharts de **punto único** donde el eje Y se extiende exactamente entre los extremos del **rango personal del usuario (Liebre = 39–83 ms)**. El rango se comunica **implícitamente a través del recorte del eje**, no como banda SVG rellena separada. Esta es una decisión sutil pero brillante — usar los límites del eje para mostrar el rango aceptable sin sobrecargar visualmente.

**Estados posibles:**
- `Equilibrado` (valor dentro del rango personal) → `#1976d2`
- `Bajo` (por debajo del mínimo) → tonos semánticos rojo/naranja
- `Desequilibrado` (fuera de rango por arriba) → tonos semánticos amber
- `Sin estado` (sin datos) → gris neutral

**Default view:** 7 días (no 28).

**Cronología nocturna:** gráfico de línea minuto a minuto (`23:44 → 06:25`), eje Y `25–87 ms`, trazo `#1976d2`. NO hay banda de rango personal renderizada sobre este chart nocturno — solo la línea.

**Texto literal interpretivo:** *"Mantener un estado de VFC equilibrado como este ayuda tanto a tu rendimiento como a tu bienestar general."*

---

### Página 2: Body Battery

**URL:** `https://connect.garmin.com/app/body-battery`
**Tecnología:** Highcharts (la viz más rica de Connect)

**Layout:** Arriba tabs `1 día / 7 días / 4 semanas / Resumen`. Centro: gauge circular con valor `52` (eje 0–100) + resumen de carga/descarga `+43 Cargada, −52 Agotada` + párrafo interpretivo del día. Abajo: **Cronología 24h**.

**Cronología 24h (chart de combinación con 22 series, 10 ejes X y 10 ejes Y, cubre 12am→6am→12pm→6pm→12am):** las capas se renderizan de atrás hacia adelante así:

| # | Capa | Color hex | Renderizado | Notas |
|---|---|---|---|---|
| 1 | **Body Battery** | área `#2a88e6`, puntos `#1976d2` | área principal | Eje Y 0–100, grillas en 25/50/75/100 |
| 2 | **Sueño** | banda área `#544fc5` (índigo-púrpura) | cubre ventana ~11pm–6am | Carga nocturna en primer plano |
| 3 | **Descanso** | área verde brillante | recuperación diurna | |
| 4 | **Estrés** | área `#fe6a35` (naranja-rojo) | nivel continuo 0–100 en eje Y propio | Etiquetas a la derecha: Descanso/Baja/Medio/Alta |
| 5 | **Activo** | área `#fa4b42` (salmón) | ventanas de movimiento | |
| 6 | **Sin datos** | relleno `#6b8abc` (slate) | huecos sin reloj | |
| 7 | **Actividad** | marcadores violeta `#d568fb` / teal `#2ee0ca` | dots de eventos | |

**Tarjetas de factores con impacto signed** (debajo del chart):
- `Estrés bajo · 1h 51m · (+2)`
- `Popayán Carrera · 51m · (−11)`
- `Sueño · 6h 32m · (+41)`

→ Esto es **EXACTAMENTE el patrón de row-factor card con valor signed** que necesitamos para Liebre — explica por qué subió o bajó el Body Battery.

---

### Página 3: Estrés

**URL:** `https://connect.garmin.com/app/stress`
**Tecnología:** Highcharts

**Layout:** Arriba tabs `1 día / 7 días / 4 semanas / 1 año / Resumen`. Centro: donut con `22` en el centro (etiqueta "Nivel de estrés") + distribución del día + texto interpretivo. Abajo: "Cronología diaria" de combinación (19 series, 9 ejes, 24h).

**Donut Highcharts** — 4 slices con mapeo semántico exacto:

| Slice | Color hex | Token |
|---|---|---|
| Descanso | `#1976d2` | `--data-viz-blue-primary` |
| Bajo | `#fd9d39` | `--data-viz-orange-secondary` |
| Medio | `#f27716` | `--data-viz-orange-primary` |
| Alta | `#de5809` | `--color-orange-60` |

**Distribución hoy:** `11h 58m Descanso · … · 10m Alta`

**Cronología diaria:** nivel de estrés como área continua (relleno `#fa4b42`), eje Y 0–100 con referencias 25/50/75/100. Fondo de bandas: Descanso (`#1976d2`), Activo (naranja), Sin datos (`#a6a6a6`). Marcadores de Actividad en eje X.

**NO hay factor-cards** en esta página (a diferencia de Body Battery).

**Texto literal interpretivo:** *"Hoy tienes un día tranquilo. Esto te ayudará a mantenerte con energía. Tu nivel de estrés se determina a partir de las reacciones de estrés que has registrado a lo largo del día."*

---

## 6. Hallazgos clave del rediseño (insumo directo para Liebre)

1. **Patrón "factor signed":** las cards de Body Battery con impacto numérico positivo/negativo (`Sueño +41`, `Carrera −11`) son la mejor forma de **explicar visualmente la causalidad**. Liebre debe adoptarlo en TODOS los scores compuestos (Readiness, HRV trend, Sleep).

2. **Banda implícita por recorte de eje:** Connect comunica el "rango personal" de HRV NO con una banda SVG rellena, sino con el **recorte del eje Y a los extremos del rango**. Solución elegante y limpia. Liebre puede replicar — y mejorar agregando una banda sombreada opcional.

3. **Cronologías 24h multi-capa:** Body Battery y Stress son charts de **combinación con 19-22 series** apiladas. Es la "estrella" visual de Connect. Liebre necesita un componente `Cronologia24h` reutilizable (Recharts `ComposedChart` con `Area + Bar + Line + Scatter`).

4. **Tabs temporales universales:** TODAS las páginas de salud usan el mismo control `1 día / 7 días / 4 semanas [/ 1 año]`. Liebre debe tener un único `<SegmentedControl />` reutilizado.

5. **Vista por defecto NO es 1 día:** HRV abre en 7 días por default. Body Battery abre en 1 día (porque el valor cambia minuto a minuto). Liebre debe seguir esta lógica: vistas con valor *agregado* abren en 7d; vistas con valor *en vivo* abren en 1d.

6. **Texto interpretivo de Connect es genérico:** *"Mantener un estado equilibrado ayuda a tu rendimiento"* — sin causalidad, sin acción. Liebre debe reemplazar cada uno de estos textos con interpretación causal + cita científica. Es el diferenciador #1.

---

## 7. Pendiente (sub-prompt 2 si lo necesitamos)

- Detalle de actividad de carrera (profundizar más allá de lo ya cubierto)
- Training Status / VO2max / Training Load
- Insights / Reportes / Calendar

---

## 8. Sistema Liebre v1 — implementación (2026-05-21)

> Capa de decisiones de implementación tomadas al construir el rediseño basado en lo extraído arriba. **Este es el estado del sistema vivo en `web/`** corriendo en `localhost:3002`.

### Decisiones que diferencian Liebre de Connect

| # | Decisión | Por qué |
|---|---|---|
| D1 | **"Diagnóstico del día" como hero card** (arriba del fold, span 2 cols) | Cierra la limitación #1 de Connect (sin interpretación causal). Es lo primero que ve el usuario al abrir el dashboard. |
| D2 | **Banda sombreada de rango personal en HRV chart**, además del recorte de eje | Mejora la decisión "sutil" de Connect — el rango se ve sin que el usuario tenga que inferirlo. Opacidad `0.06` para no saturar. |
| D3 | **Cita científica embebida** en cada interpretación, formato `📄 Autor (año) · Journal · Tipo de evidencia` | El diferenciador #2: respaldo en literatura validada (Scopus/WoS). |
| D4 | **Card oscura (`#1A1A1A`) para "Tu meta"** con countdown grande + barra de progreso | Toma el patrón Connect (card oscura prominente) y lo aplica a la motivación a largo plazo. |
| D5 | **Pills semánticos con `color-mix()`** para fondos translúcidos del color del estado | Mejor contraste que un fondo gris uniforme; cada estado es visualmente identificable. |
| D6 | **Tabular nums (`font-variant-numeric: tabular-nums`) global en body** | Alineación vertical de cifras en tablas y métricas sin perdir consistencia tipográfica. |
| D7 | **`RowFactorCard` con dos modos**: `verbal` (Connect default) + `signed` (impacto +/- tipo Body Battery) | Reutiliza el componente para HRV factors Y para Body Battery factors. |
| D8 | **Saludo dinámico ES-CO en TopBar** (Buenos días / Buenas tardes / Buenas noches) | Localización + warm onboarding visual. |

### Inventario de componentes implementados

**Primitivos (`web/src/components/dashboard/`)**

| Componente | Líneas | Reúsa de Connect | Innovación Liebre |
|---|---|---|---|
| `GaugeCircular270.tsx` | ~85 | Donut 270°, arco 7→5 reloj, número central display | SVG puro (sin lib), prop `color` para semáforo dinámico |
| `SegmentedControl.tsx` | ~60 | Tabs `1d/7d/4w/1y` con fondo activo azul | Controlled + uncontrolled, accesibilidad ARIA |
| `RowFactorCard.tsx` | ~115 | Patrón factor `[Nombre + Valor + Label + Dot]` | Modo `signed` para impacto +/- + slots `interpretation` y `citation` |
| `ZoneBar.tsx` | ~75 | Stacked bar Z1-Z5 con colores semánticos correctos | Acepta % o minutos, leyenda inline con %, sin dependencias |
| `Sidebar.tsx` | ~120 | Negro fijo 272px, wordmark + nav + avatar | Íconos SVG inline, navegación con destacado del item activo |
| `TopBar.tsx` | ~30 | Header con saludo + fecha | Greeting dinámico por hora ES-CO |

**De dominio (refactor + nuevos)**

| Componente | Estado | Lo que muestra |
|---|---|---|
| `HRVCard.tsx` | Refactor | Gauge 270° + banda implícita rango personal + chart 8 noches + stats + interpretación Liebre con cita Plews & Buchheit |
| `GoalCard.tsx` | Refactor | Card oscura con countdown 133 días + barra progreso |
| `ProfileCard.tsx` | Refactor | Edad/peso/altura/FC máx/FC reposo, lista vertical separada por hairlines |
| `WeeklyTable.tsx` | Refactor | Tabla con ACWR pill coloreado por zona segura |
| `DiagnosticoDelDiaCard.tsx` | **NUEVO** ⭐ | El diferenciador #1: narrativa cruzada generada (placeholder hasta conectar orchestrator real) + acción concreta + cita |
| `FactorImpactList.tsx` | **NUEVO** ⭐ | Replica patrón Body Battery con factores signed `Sueño +41`, `Carrera -11`, `ACWR +8` |

### Tokens CSS finales en `web/src/app/globals.css`

Sistema consolidado:
- **9 categorías**: surfaces, ink, brand, viz primarios, semantic, sleep, zones, cronología 24h, training status
- **75+ custom properties**
- **Mapeados a `@theme inline`** de Tailwind 4 → utilidades tipo `bg-bg-sidebar`, `text-ink-primary`, `text-zone-3`
- **Tipografía utilitaria**: `.wordmark`, `.metric-display`, `.metric-kpi`, `.tnum`, `.label-uppercase`
- **Cards primitivas**: `.card`, `.card-subtle`, `.card-dark`
- **Status pills**: `.status-pill.balanced/.low/.unbalanced/.no-state/.building` con `color-mix()`

### Lo que NO se implementó todavía (roadmap)

| Componente | Inspirado en | Cuándo |
|---|---|---|
| `Cronologia24h` | Body Battery + Stress 24h multi-capa | v2 — necesita Recharts `ComposedChart` |
| `SyncedChartStack` | Stack vertical de gráficos de actividad con crosshair compartido | v2 — vista `/actividad/[id]` |
| `MapPolylineGradient` | Mapa Leaflet con gradient azul→rojo por velocidad | v2 — vista de actividad |
| `TrainingStatusCard` | Gauge + estado (Productivo/Recuperación/Sobrecarga) | v2 — requiere lógica de ACWR + VO2max trend |
| `SleepStagesDonut` + `Hypnogram` | Donut + timeline horizontal de fases | v2 — requiere datos de Garmin Sleep |
| `CalendarHeatmap` | Distribución semanal de entrenamientos | v2 |

### Composición actual del `/dashboard`

```
┌──────────┬─────────────────────────────────────────────────────────────┐
│ SIDEBAR  │ TopBar: "Buenas tardes, José · resumen del día · 21 mayo"   │
│ (negro)  ├─────────────────────────────────────────────────────────────┤
│          │ ┌─────────────────────────────────────┐ ┌─────────────────┐│
│ liebre.  │ │ ⭐ DIAGNÓSTICO DEL DÍA (span 2)     │ │ ⚫ TU META       ││
│          │ │   Narrativa cruzada + acción +     │ │   21K · 1h50     ││
│ Inicio   │ │   📄 paper                         │ │   133 días       ││
│ Activid. │ └─────────────────────────────────────┘ └─────────────────┘│
│ Salud    │ ┌─────────────────────────────────────┐ ┌─────────────────┐│
│ Ciencia  │ │ 🔵 VFC NOCTURNA (span 2)            │ │ Tu perfil        ││
│ Perfil   │ │   Gauge 270° + banda rango +       │ │   36a · 67.8kg   ││
│          │ │   sparkline 8 noches +             │ │   170cm · FCmax  ││
│ ──────   │ │   Interpretación Liebre + 📄        │ │                  ││
│ avatar   │ └─────────────────────────────────────┘ └─────────────────┘│
│ José     │ ┌─────────────────────────────────────┐ ┌─────────────────┐│
│ jose_dev │ │ Factores que influyen (span 2)      │ │ Historial sem.  ││
│          │ │   Sueño +41 · Carrera -11 ...      │ │   Tabla + ACWR  ││
│          │ └─────────────────────────────────────┘ └─────────────────┘│
│          │ footer: localhost:8080/docs + Garmin Connect + capa Liebre │
└──────────┴─────────────────────────────────────────────────────────────┘
```

### Métricas de calidad

- HTTP 200 en `/dashboard` desde primer render
- Página pesa ~64 KB HTML server-side
- Datos reales de Postgres en cada request (cache: no-store)
- Sin dependencias nuevas de npm (todo con primitivos: SVG inline, CSS, Tailwind 4)
- Mantenido SSR en Next.js 16 sobre Firebase App Hosting

