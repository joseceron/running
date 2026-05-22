Inventario visual de Garmin Connect para Liebre

1. Resumen ejecutivo
3 cosas que Connect hace excelente y debemos replicar
1. El sistema de "semáforo contextual" por factores. En Predisposición para entrenar y Estado de entreno, cada factor contribuyente (sueño, VFC, carga aguda, estrés) aparece como una fila card con nombre + valor + etiqueta verbal ("Óptimo", "Equilibrado", "Baja") + dot de color verde/naranja/rojo. Es extraordinariamente legible: en 3 segundos el usuario sabe qué pesa más en su estado del día. Liebre debe replicar exactamente esta estructura pero añadiendo la capa de interpretación causal ("porque corriste 2 sesiones en Z2 esta semana, tu carga aguda bajó a 132, lo que favorece la supercompensación — ver Bangsbo et al., 2013, J Sports Sci").
2. La cronología de 24 horas del Body Battery y el Estrés. Un gráfico de combinación con múltiples capas (Battery line chart en negro + barras de estrés en naranja + barras de descanso en azul + marcadores de actividad en verde) sobre un eje temporal 12a→6a→12p→6p→12a. El resultado es una narrativa visual del día completo. Es la visualización más rica de Connect. Liebre puede replicarla para el panel diario y añadir la capa de interpretación de la sesión de entrenamiento sobre ese timeline.
3. Los gráficos apilados/multi-serie de la actividad (Highcharts 11). Cada métrica de la carrera tiene su propio gráfico de serie temporal vertical con su media horizontal anotada, usando puntos tipo scatter para running dynamics y línea de área para HR/ritmo. La disposición en stack vertical (un gráfico debajo del otro, todos con el mismo eje X de tiempo) permite correlacionar visualmente Ritmo ↔ FC ↔ Cadencia ↔ Longitud de zancada sin sobrecargar un solo canvas. Liebre debe mantener esta arquitectura de gráficos sincronizados.
3 limitaciones que Liebre puede superar con IA + ciencia
1. Los datos están sin interpretar. Connect dice "tu cadencia fue 147 spm" y "tu VFC fue 55 ms – Equilibrado". Jamás explica por qué ni qué hacer. El único texto interpretativo son frases de marketing como "Bien descansado. Un buen sueño y un entreno más ligero han mejorado tu predisposición". No hay causalidad, no hay paper, no hay acción recomendada específica. Liebre aquí tiene su mayor ventaja diferencial.
2. El baseline de VFC es poblacional-genérico. Connect establece un "valor de referencia" basado en 3 semanas de uso, pero la documentación misma admite que "los valores de VFC pueden variar ampliamente en función del género, la edad, el nivel de forma física e incluso la genética". La ventana de referencia es fija (últimas semanas), no adaptativa. Liebre puede construir un baseline dinámico con percentiles personales, detectar tendencias de largo plazo y alertar cuando la VFC se desvía 1.5 desviaciones estándar del rolling average personal de 28 días.
3. No hay integración longitudinal entre módulos. El sueño vive en su página, la VFC en otra, el Training Load en otra. Connect nunca cruza: "tu sueño fue corto (6h 32m) PERO tu VFC se mantuvo equilibrada (55ms) porque tu carga aguda fue baja (132) — el sistema nervioso autónomo se recuperó sin intervención de sueño profundo adicional." Liebre puede construir una vista de "Diagnóstico del día" que narrativice cómo interactúan todas las métricas.
Patrones visuales recurrentes (sistema de diseño global)

Sidebar izquierda fija negra (#1A1A1A, ~265px wide) con iconografía monocroma blanca (outline para inactivos, filled/highlight para activo). Divide la app en navegación primaria colapsable.
Content area blanca o gris muy claro (#F5F5F5) con padding generoso (~32px).
Cards de contenido con fondo blanco, sin border visible, sombra box-shadow sutil (~2px 4px rgba(0,0,0,0.08)), border-radius ~8px, padding ~16–20px.
Sistema de colores semánticos consistente: verde #4CAF7D (bueno/equilibrado), naranja/ámbar #F5A623 (alerta/moderado), azul #1976D2 (acento de marca, botones primarios), rojo #E53935 (peligro/alto).
Segmented control ("1 día / 7 días / 4 semanas / 1 año") es el widget de navegación temporal universal en todas las páginas de salud. Fondo gris inactivo, azul sólido para activo.
Gauge circular (donut parcial de 270°) es el widget de "resumen en 1 número" de casi todas las páginas de salud y rendimiento.


2. Sistema de diseño extraído
Paleta global
TokenHex aproximadoUso--bg-sidebar#1A1A1AFondo de sidebar izquierda--bg-content#FFFFFFFondo del área principal--bg-subtle#F5F5F5Fondo de página / separadores--ink-primary#1C1C1CTexto principal, números grandes--ink-secondary#6B7280Labels, subtítulos, unidades--ink-sidebar#FFFFFFTexto e íconos en sidebar--accent-brand#1976D2Botones primarios, tab activo, links--accent-orange#F5A623Actividad/Alerta media, iconos corredor--semantic-green#4CAF7DPositivo: Equilibrado, Óptimo, Excelente--semantic-amber#F5A623Alerta: Bajo, Moderado, Aceptable--semantic-red#E53935Peligro: Desequilibrado, Alto estrés--semantic-gray#9CA3AFNeutro: Sin datos, Inactivo--chart-hr#EF4444Línea de Frecuencia cardiaca--chart-pace#60A5FAÁrea de Ritmo (azul claro)--chart-altitude#86EFACÁrea de Altura (verde claro)--chart-cadence-green#22C55EPuntos de cadencia "buena" en scatter--chart-cadence-orange#F97316Puntos de cadencia "variable"--chart-stress-orange#FB923CBarras de estrés en cronología--chart-rest-blue#3B82F6Barras de descanso en cronología--chart-bb-line#1C1C1CLínea principal de Body Battery--zone1#B5C4D0Z1 – Calentamiento (gris azulado)--zone2#60A5FAZ2 – Fácil (azul)--zone3#34D399Z3 – Aeróbico (verde-teal)--zone4#FBBF24Z4 – Umbral (ámbar)--zone5#EF4444Z5 – VO2max (rojo)--sleep-deep#1D4ED8Sueño profundo (azul oscuro)--sleep-light#60A5FASueño ligero (azul claro)--sleep-rem#C084FCMOR/REM (púrpura/lavanda)--sleep-awake#FCD34DDespierto (amarillo)--hrv-ref-band#D1D5DBBanda de referencia VFC (gris claro)--training-status-barMultiBarra cromática de estados (ver sección 9)
Tipografía
Connect usa una sans-serif de sistema sin anunciar explícitamente una fuente de marca. Por comportamiento visual inferido:

Display / Números grandes: Sans-serif tabular, peso 300–400, tamaño ~48–64px. Ej: "79" en Training Readiness, "55" en HRV, "81" en Sleep Score. Números con proporciones monoespacio (tabular figures) para alineación vertical.
H1 / Títulos de página: Sans-serif, peso 300–400, ~28–32px, color #1C1C1C. Ej: "Estado de VFC", "Body Battery", "Sueño".
H2 / Subtítulos de sección: Sans-serif, peso 400–500, ~16–18px. Ej: "Resumen", "Cronología nocturna", "Factores".
Body / Texto explicativo: Sans-serif, peso 400, ~14px, color #4B5563. Ej: los párrafos interpretativos de cada sección.
Label / Unidades y metadatos: Sans-serif, peso 400, ~11–12px, color #9CA3AF, UPPERCASE con letter-spacing leve para unidades. Ej: "DISTANCIA", "RITMO MEDIO", "FRECUENCIA CARDIA...".
Valores de métricas en listas: peso 600–700, ~20–24px, tabular, color #1C1C1C.
Pesos usados: 300 (display ligero), 400 (body), 500 (énfasis suave), 600–700 (valores numéricos y CTAs).

Componentes recurrentes
Card estándar: fondo #FFFFFF, border-radius 8px, box-shadow 0 1px 3px rgba(0,0,0,0.08), padding 16–20px. Sin border visible. Algunas cards tienen un micro-título en uppercase pequeño en la esquina superior izquierda.
Gauge circular (donut 270°): Presente en Home, HRV, Body Battery, Sueño, Estrés, Training Readiness. Grosor del arco ~12–14px. El arco se divide en segmentos de colores semánticos. El número central es el valor principal en display bold. El label secundario debajo es tiny (~12px). Tamaño del widget ~120–160px de diámetro.
Segmented control de tiempo ("1 día / 7 días / 4 semanas"): Fila de botones con fondo gris #E5E7EB inactivo y #1976D2 activo (texto blanco). Border-radius 6px. Height ~32–36px. Padding horizontal 16px. Separación entre opciones: 0 (son contiguos, estilo "pill group").
Pill de estado: Texto como "Equilibrado", "Óptimo", "Alta" sin pill explícito. Se usa texto con color semántico + dot de color a la derecha. En Training Readiness los dots son círculos sólidos de ~8px. El contraste viene del par [valor numérico / label verbal].
Row-factor card: En páginas de salud, cada factor contribuyente es una card horizontal con: [Nombre del factor (left, bold)] + [Valor numérico debajo del nombre, secondary color] + [Label verbal (right, secondary)] + [Dot de color (right)]. Border-radius 8px, separación entre rows 8px, fondo #F9FAFB.
Tooltip / "?" de ayuda: Círculo de ~18px con "?" en gris #9CA3AF. Al hacer hover muestra panel lateral o modal con explicación extensa de la métrica. El texto de ayuda es muy técnico y detallado (varios párrafos).
Date picker: Botón con ícono de calendario + fecha en texto. Navegación ‹ › izquierda/derecha para moverse entre días/semanas. Sin modal calendar visible, sólo navegación incremental.
Botón primario: Fondo #1976D2, texto blanco, border-radius 4–6px, padding 10px 20px, peso 500.
Botón secundario / "Exportar": Borde fino 1px gris, fondo transparente, texto gris oscuro.

3. Inventario por página

Página 1: Home / Resumen del día
A. Identificación

Nombre en Connect: "Inicio"
URL: https://connect.garmin.com/app/home
Para qué se usa: Panel principal de bienvenida que agrega el estado de salud y actividad del día en una sola pantalla.
Tipo de vista: Vista principal (home dashboard).

B. Layout

Estructura: Sidebar negra izquierda fija (265px) + content area blanca dividida en 2 columnas: columna principal (~60% width) + columna derecha (~35% width) para widgets secundarios ("Novedades", "Actividad de hoy").
Columnas en desktop: 2 + sidebar = 3 zonas visuales.
Jerarquía visual: El bloque "Destacado" es lo más prominente. Ocupa ~50% del viewport arriba del fold. Contiene una mega-card dividida en 2 sub-cards horizontales: [Predisposición para entrenar | Estado de entreno]. Debajo: bloque "De un vistazo" con 4 widgets en fila.
Densidad: Media-alta. Mucha información comprimida en el fold.

C. Componentes de UI presentes

Mega-card "Destacado": 2 sub-cards en fila, fondo blanco, radius 8px, sin shadow visible, border-bottom 1px #E5E7EB entre secciones.
Gauge circular (270°) en sub-card de "Predisposición para entrenar": muestra el score "79" con etiqueta "Alta".
Mini-iconos de estado semántico: En la sub-card de "Estado de entreno", íconos pequeños azules de corredor + montaña + termómetro.
Barra cromática horizontal en el bloque "Estado de entreno – Últimas 4 semanas": barra de ~16px de alto con segmentos de colores múltiples (morado, naranja/ámbar, verde, rojo, gris, azul) representando los diferentes estados de entreno diarios. Es la única instancia de timeline visual en la home.
Cards "De un vistazo": 4 cards horizontales en fila — Frecuencia cardiaca, Body Battery, Puntuación de sueño, Estado de VFC. Cada una con un ícono a color a la izquierda, el valor principal grande, y 2–3 sub-métricas debajo.
Cards de "Actividad de hoy" (columna derecha): cards verticales apiladas. Cada sesión de entrenamiento planificada tiene una pill badge de tipo ("SESIÓN DE ENTRENAMIENTO") + badge "MAÑANA" en azul oscuro cuando es del día siguiente. Debajo el nombre del workout y la estimación de duración.
Card de actividad reciente ("Popayán Carrera"): mini-card con nombre, icono naranja de corredor, distancia y tiempos.
Botón "Editar Inicio": CTA terciario, texto azul, sin relleno.
Banner de notificación/novedad (columna derecha): card con heading bold + párrafo + CTA azul + botón de cierre ×.

D. Tipos de visualización de datos

Gauge circular 270° (donut): Score de Predisposición para entrenar. Arco segmentado en 3 colores (rojo izq., verde centro-derecha, naranja extremo). El punto activo es un dot verde sólido en la posición "79/100". Centro: "79" en display bold + "100" subtexto.
Barra de timeline cromática: Serie horizontal continua de ~640px × 16px. Segmentos de color contiguos representando estados de entreno día a día en las últimas 4 semanas (Abr 23 – May 21). Colores observados de izquierda a derecha: morado (~Productivo), naranja (~Sobrecarga), verde (~Mantenimiento), rojo (~Detraining), gris (~Sin datos/Base), azul (~Recuperación). Es esencialmente un heatmap lineal de 1 fila.
Mini-gauge Body Battery (en card De un vistazo): Donut 3/4 azul. Valor "69", máx "100".
KPI numérico simple (FC en reposo, Sleep Score, VFC media): Número grande + label + sub-métricas en texto pequeño.

E. Métricas mostradas
MétricaUnidadFormatoContextualizaciónPredisposición para entrenarScore 0-100EnteroEtiqueta verbal "Alta/Baja/Moderada"Estado de entrenoLabelTexto"Recuperación", con foco de cargaVO2 máximoml/kg/minEnteroEtiqueta "Bueno"Carga (aguda)ScoreEntero"Baja"Estado de VFCLabelTexto"Equilibrado"Aclimatación altitudmEntero (1,700 m)+ porcentaje "16%"FC media en reposoppmEntero"Media en reposo de 7 días: 50 ppm"Body Battery0-100Entero (69)"+39 Cargada / -31 Agotada"Puntuación de sueño0-100Entero (81)Duración + hora inicio/finVFC media 7 díasmsEntero (55 ms)"Últimas 4 semanas"
F. Iconografía y motion

Estilo: Outline para iconos del sidebar inactivos, filled para el activo (el item activo "Inicio" tiene un highlight de fondo ligeramente más claro). Para íconos de métricas en cards (corazón, batería, luna, running man): filled monocromáticos en naranja-azul-verde.
Iconografía deportiva: Corredor silueta naranja (#F5A623) como ícono principal de actividades de carrera. Montaña para aclimatación a la altitud. Termómetro para temperatura/calor.
Motion: Transición suave (fade-in ~200ms) cuando se cambia de sección. Las cards del sidebar hacen collapse/expand con animación de height. No se observan animaciones de entrada de cards.

G. Paleta de colores (esta página)

Fondo sidebar: #1A1A1A
Fondo content: #FFFFFF / #F5F5F5
Texto principal: #1C1C1C
Texto secundario/labels: #6B7280
Acento de marca: #1976D2
Color de actividad/running: #F5A623 (naranja-ámbar)
Positivo/verde: #4CAF7D
Gauge arco rojo: #EF4444
Gauge arco verde: #4CAF7D
Gauge arco naranja: #F97316
Body Battery azul: #3B82F6
Barra timeline: morado #9333EA, naranja #F97316, verde #22C55E, rojo #EF4444, gris #D1D5DB, azul #3B82F6

H. Tipografía

Títulos de sección ("Destacado", "De un vistazo"): sans-serif 400, ~20px
Números de KPI grandes: sans-serif 300–400, ~44–52px, tabular
Labels de métricas: ALL CAPS 400, ~11px, #9CA3AF
Texto de estado ("Alta", "Equilibrado"): sans-serif 600, ~14px

I. Texto y voz de marca

Módulos se titulan con sustantivos: "Destacado", "De un vistazo", "Actividad de hoy", "Novedades".
Las métricas de estado se etiquetan con adjetivos puros sin verbo: "Alta", "Equilibrado", "Óptimo", "Bajo".
La única frase interpretativa explícita en el home está en la sub-card de Estado de entreno: "Recuperación. Foco de carga – Equilibrado". No explica por qué.
No hay tooltips embebidos en la home (el "?" aparece en sub-páginas).
El tono es neutro-informativo, no motivacional. Excepción: "Actividad de hoy" con la sesión de entrenamiento planificada que sí tiene tono de plan de acción.


Página 2: Detalle de actividad de carrera
A. Identificación

Nombre en Connect: "Popayán Carrera" (nombre del usuario) / vista genérica: "Actividad"
URL: https://connect.garmin.com/app/activity/22959729618
Para qué se usa: Vista completa de una actividad individual con todos los datos de la sesión, gráficas, splits y dinámicas de carrera.
Tipo de vista: Sub-vista accedida desde la lista de actividades. Vista principal de detalle.

B. Layout

Estructura: No usa tabs separadas. Es una sola página de scroll vertical largo. La información se organiza verticalmente en esta secuencia:

Header de actividad (breadcrumb tipo + nombre + fecha/hora)
Barra de 5 KPIs en línea (Distancia, Tiempo, Ritmo medio, Ascenso, Calorías)
Mapa interactivo (Leaflet.js) con overlay de velocidad en gradiente de color
Toggle Tiempo/Distancia para el eje X
Stack de gráficos verticales sincronizados (uno debajo del otro)
Sección de estadísticas textuales (en dos columnas)
Sección de vueltas/splits (tabla)
Sidebar derecha fija con: Fotos, Notas, Device card (Forerunner 965), Equipo


Columnas en desktop: Content principal (~70%) + Sidebar derecha (~30%)
Jerarquía visual: El mapa toma la mayor área visual (~380px alto × todo el ancho del content). Luego viene el stack de gráficos. Los KPIs superiores son las "señales de headline".
Densidad: Muy alta. Es la página más densa de toda la app.

C. Componentes de UI presentes

Breadcrumb de tipo de actividad: "CARRERA ▾ POR JOSELO EL HOY @ 7:22 AM" — tipo dropdown seleccionable para cambiar el tipo de actividad. Pequeño, gris, uppercase.
Barra de KPIs: 5 valores en fila separados por divisores verticales. Cada uno: valor grande + label small debajo. Ej: "5.22 km / Distancia".
Mapa Leaflet: Mapa base de tiles neutros (estilo cartográfico gris-beige). El track GPS se dibuja como polyline con gradiente de color (azul → cian → verde → amarillo → naranja → rojo) de "Más lento" a "Más rápido". Marcador de inicio en rojo (pin clásico) y de fin en verde (triángulo play). Controles: +/– zoom, capas, fullscreen. Leyenda "Más lento ← gradiente → Más rápido" debajo del mapa.
Toggle Tiempo/Distancia: Segmented control de 2 opciones para el eje X de todos los gráficos. Estilo igual al temporal pero más pequeño (height ~28px).
Highcharts sincronizados (stacked verticalmente): Cada gráfico ocupa ~120–140px de alto. Son independientes pero comparten el eje X. Al hacer hover en uno, una línea vertical cruzada aparece en todos los demás simultáneamente. Cada gráfico tiene:

Nombre de métrica en la esquina superior izquierda + ícono de color circular
"?" de ayuda en algunos
Ícono de expand/fullscreen en la esquina superior derecha
Línea horizontal de media anotada con tooltip "Media: X.XX unidad"


Dropdown de gráficos personalizables: Botón "Personalizar gráficos" abre un selector para agregar/quitar gráficos del stack.
Segmented control de velocidad en la sección de Ritmo/velocidad: Botones "Ritmo" / "Velocidad" para cambiar las unidades mostradas.
Tabla de splits/vueltas: Tabla HTML completa con columnas de datos. Header sticky. Columnas: Vuelta | Tiempo | Tiempo acumulado | Distancia km | Ritmo medio | GAP medio | FC media | FC máxima | Ascenso | Descenso | Potencia | W/kg | Potencia máx | Max W/kg | Cadencia | GCT | Balance GCT% | Longitud zancada | Oscilación vertical | Ratio vertical | Calorías | Temperatura | Ritmo óptimo | Cadencia máx | Tiempo en mov. | Ritmo mov. | Pérdida vel. | % pérdida vel.
Sección de estadísticas textuales: Dos columnas de pares valor + label. Sin visualización, solo texto. Organizada en sub-secciones: Nutrición e hidratación, Autoevaluación, Stamina, Training Effect, Frecuencia cardiaca, Tiempo, Potencia, Altura, Detección carrera/caminar, Ritmo, Dinámica de carrera, Minutos de intensidad, Body Battery.
Card Stamina: Barra de progreso de 0 a 100% horizontal. Muestra potencial inicial (100%) y potencial final (76%) como puntos sobre la barra.
Card Training Effect: Etiqueta texto "Base (Aeróbica baja)" + valor 2.2 (escala 0-5) + "Mantenimiento" + Anaeróbica: 0.0 "Sin mejora".
Sección de Zonas de FC: Presente en las estadísticas pero Connect no muestra el breakdown gráfico de zonas en esta página (solo FC media: 133 ppm y FC máxima: 154 ppm). Las zonas detalladas están en la vista de informes.

D. Tipos de visualización de datos
Mapa con heatmap de ritmo: Polyline sobre mapa base cartográfico (Leaflet). El color del track es un gradiente continuo de 6 colores mapeados a la escala de velocidad. Azul (#3B82F6) = más lento; rojo (#EF4444) = más rápido. Permite ver visualmente dónde se aceleró y deceleró el corredor a lo largo de la ruta. Interactivo: click/pan/zoom.
Gráfico de área — Altura: Área rellena de verde suave (#86EFAC) con línea borde verde oscuro. Eje Y: 1,640–1,800 m. Eje X: tiempo 0:00 a 41:40. La línea de elevation profile es casi plana (variación de 47m entre mín 1,715 y máx 1,762) con una ligera ondulación.
Gráfico de área invertida — Ritmo: Área rellena de azul claro (#BAD8F7), línea borde azul. Eje Y invertido (0:00 arriba, 40:00 abajo) para que "más rápido = más alto visualmente". Línea horizontal discontinua de media "Media: 9:21 /km". Los picos hacia abajo representan caminata (ritmo muy lento ~20:00+ /km).
Gráfico de área — Frecuencia cardiaca: Área rellena de rojo claro (#FECACA), línea borde rojo (#EF4444). Eje Y: 75–200 ppm. Línea horizontal de media "Media: 133 ppm". La forma del gráfico muestra una FC estable alrededor de 130–145 ppm con picos ocasionales hasta 154.
Gráfico de barras suaves / área — Condición de rendimiento: Línea de área gris-azul muy plana, entre -3 y -4 (escala -5 a +5). La zona positiva (>0) está en blanco, la negativa en azul muy suave. Muestra que la Performance Condition fue consistentemente ligeramente negativa durante toda la carrera.
Scatter plot — Longitud de zancada: Nube de puntos dispersos con color uniforme (azul #3B82F6). Eje Y: 0–2 m. Media 0.72 m marcada con línea horizontal. Los puntos se agrupan entre 0.6–0.9 m durante la carrera y caen durante los segmentos de caminata.
Scatter plot multi-color — Cadencia de carrera: Puntos en 3 colores según la zona de cadencia — verde (#22C55E) para cadencia en rango óptimo (~160-180 spm), naranja (#F97316) para baja, rojo (#EF4444) para muy baja. Eje Y: 100–200 spm. Media 147 spm (baja porque incluye caminata). Máxima: 193 spm.
Gráfico de área — Potencia (Vatios): Área azul medio, línea continua. Eje Y: 0–500 W. Media: 157 W, máxima 285 W.
Scatter plot — Ratio vertical / Oscilación vertical: Similar en estructura al de cadencia. Eje Y: 5–15%. Media 9.9%. Puntos de colores múltiples.
Scatter plot — GCT (Tiempo de contacto con el suelo): Eje Y: 0–600 ms. Media 301.5 ms. Punto disperso de color uniforme.
Área de combinación — Stamina: Dos series: "Stamina" (azul oscuro) y "Stamina potencial" (gris claro). Ambas líneas de área sobre el mismo eje. El gap entre potencial (100%) y real (final 76%) representa el gasto de estamina.
Gráfico de barras categóricas — Carrera/Caminar: 3 series de barras apiladas: "Carrera" (verde), "Caminar" (azul), "Inactivo" (gris). Sobre eje temporal.
E. Métricas mostradas
MétricaUnidadFormatoDistanciakm1 decimal (5.22 km)TiempoHH:MM:SS(48:50)Ritmo mediomin/kmMM:SS (9:21 /km)Ascenso totalmEntero (65 m)CaloríaskcalEntero (316)FC mediappmEntero (133 ppm)FC máximappmEntero (154 ppm)Cadencia mediaspmEntero (147 spm)Cadencia máximaspmEntero (193 spm)Longitud de zancadam2 decimales (0.72 m)Oscilación verticalcm1 decimal (7.1 cm)Ratio vertical%1 decimal (9.9%)GCT mediamsEntero (302 ms)Potencia mediaWEntero (157 W)Potencia máximaWEntero (285 W)Cadencia a altitud—(datos de contexto)Stamina final%Entero (76%)Training Effect aeróbico0–51 decimal (2.2)Carga de ejercicioscoreEntero (30)Body Battery impactodeltaEntero (-11)Tiempo de carreraMM:SS(34:21)Tiempo de caminataMM:SS(13:01)Ritmo óptimomin/kmMM:SS (6:30 /km)Ritmo medio en movimientomin/kmMM:SS (9:00 /km)Ascenso/Descenso totalmEnteroAltitud mínima/máximamEntero (1,715 – 1,762 m)
Tabla de splits (vueltas km a km):
VueltaTiempoRitmoGAPFC medFC máxAscensoCadenciaGCTLong.Zancada17:58.17:587:4812213974m1602730.77m29:14.09:149:0413114542m1583100.68m310:5610:5610:18133154207m1272990.71m49:45.79:469:21137147225m1443110.71m58:48.28:489:031391490m1523020.73m6 (parcial)2:08.19:449:5613314515m1423470.71mResumen48:509:219:1013315465m1473020.72m
F. Iconografía y motion

Íconos de métrica en el header de cada gráfico: círculo de color de ~8px (dot de color de la serie) + nombre de la métrica en texto small.
Ícono de actividad corredor: círculo naranja sólido con silueta de corredor blanca en el breadcrumb superior.
Ícono "?" de ayuda: gris, presente en "Condición de rendimiento", "GCT", "Oscilación vertical" y otros.
Al hacer hover sobre los gráficos Highcharts, aparece un tooltip flotante con: [valor + unidad + timestamp]. Se muestra crosshair vertical que se sincroniza entre todos los gráficos.

G. Paleta de colores (esta página)

Gradiente de mapa: azul #3B82F6 → cian #06B6D4 → verde #22C55E → amarillo #EAB308 → naranja #F97316 → rojo #EF4444
FC: área #FECACA, línea #EF4444
Ritmo: área #BAD8F7, línea #3B82F6
Altura: área #BBF7D0, línea #22C55E
Cadencia: scatter verde #22C55E, naranja #F97316, rojo #EF4444
Potencia: área #BFDBFE, línea #2563EB

H. Tipografía

KPIs de headline: 32px, tabular, peso 300.
Labels de KPI ("DISTANCIA", "TIEMPO"): ALL CAPS, 11px, #6B7280.
Nombres de gráficos: 14px, 500.
Valores en tabla de splits: 13–14px, 400, tabular.

I. Texto y voz de marca

No hay interpretación del rendimiento en esta página. Solo datos.
Los únicos textos son: nombres de métricas, valores, y el panel lateral de "Autoevaluación" (que el usuario llena).
Hay un bloque "Dinámica de carrera" al fondo que incluye definiciones técnicas de cada métrica (ej.: "La longitud de la zancada es la longitud de tu zancada de una pisada a la siguiente"). Es puramente definitorio, no interpretativo.
El panel de "Training Effect" muestra "Base (Aeróbica baja) – Beneficio principal" y el score 2.2 / "Mantenimiento". No explica qué significa en el contexto de este corredor o esta semana de