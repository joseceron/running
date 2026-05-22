# Prompt para Claude for Chrome — Investigación visual de Garmin Connect

**Uso:** activa la extensión Claude for Chrome con tu sesión de Garmin Connect abierta (https://connect.garmin.com/modern/), pega el prompt completo de abajo en el panel de la extensión, y deja que Claude navegue. Al final tendrás un informe markdown listo para alimentar el rediseño del dashboard de Liebre.

**Tiempo estimado:** 20–30 min con tu cuenta real (más datos = mejor inventario visual).

---

## El prompt (copiar todo lo que está dentro del bloque)

```
Eres un experto en diseño de producto e investigación visual. Estoy construyendo
un SaaS llamado LIEBRE que combina los datos de Garmin Connect con análisis
basado en IA + papers científicos (Scopus, Web of Science) para corredores.

Mi diferenciador frente a Connect y otras apps:
1) BASELINE PERSONAL (no rangos poblacionales): mi HRV de referencia se construye
   con MIS 14 noches, no con la media del segmento "hombre 30-40 años".
2) EVIDENCIA CITADA: toda recomendación trae el paper que la sustenta (autor,
   año, journal, DOI; con nivel: RCT, meta-análisis, observacional).
3) INTERPRETACIÓN, no solo métricas: Connect muestra que "tu cadencia fue
   147 spm"; Liebre dice "tu cadencia bajó porque corriste más lento en Z2,
   no por problema técnico — protocolo de drills X según paper Y".
4) ESCALA Y CONTEXTO PERSONAL: detecto adaptación a altitud (entrenas a 1736
   msnm), patrón de fatiga, hueco de fuerza, distribución 80/20 polarizada,
   etc., todo personalizado.

NECESITO QUE NAVEGUES POR GARMIN CONNECT Y EXTRAIGAS UN INVENTARIO VISUAL Y DE
REPORTERÍA COMPLETO. La meta: rediseñar el dashboard de Liebre con la fluidez
y profesionalismo deportivo de Connect, PERO añadiendo las capas de
interpretación + ciencia que Connect no tiene.

## Páginas a visitar (en este orden)

Para cada una, abre la URL, observa la página completa (scroll incluido), y
reporta lo que pido en la sección "QUÉ CAPTURAR" más abajo. Si una página
requiere clic en sub-tabs, recorre los tabs principales.

1. **Home / Resumen del día**
   https://connect.garmin.com/modern/

2. **Detalle de una actividad de carrera reciente** (entra a la última
   actividad que tenga running dynamics)
   https://connect.garmin.com/modern/activities
   → clic en una actividad → recorre las tabs: Resumen, Mapa, Gráficas,
     Splits, Running Dynamics, Frecuencia cardíaca, Performance Condition

3. **Lista de actividades + filtros**
   https://connect.garmin.com/modern/activities

4. **Calendario**
   https://connect.garmin.com/modern/calendar

5. **HRV nocturno** (Heart Rate Variability)
   https://connect.garmin.com/modern/hrv-status

6. **Body Battery**
   https://connect.garmin.com/modern/body-battery

7. **Sueño**
   https://connect.garmin.com/modern/sleep

8. **Estrés**
   https://connect.garmin.com/modern/stress

9. **Training Status / VO₂max / Training Load / Acute Load**
   https://connect.garmin.com/modern/training-status

10. **Insights / Reportes / Tendencias**
    https://connect.garmin.com/modern/insights
    https://connect.garmin.com/modern/reports

11. **Performance Stats** (si está disponible)
    https://connect.garmin.com/modern/performance-stats

## Qué capturar de CADA página

Por cada página visitada, genera una sección en el reporte final con:

### A. Identificación
- Nombre de la página (cómo la llama Connect)
- URL exacta
- Para qué se usa (1 frase)
- ¿Es vista principal, sub-vista o widget dentro de otra?

### B. Layout
- Estructura general: ¿sidebar + content? ¿topbar? ¿cards grid? ¿tabs?
- Cuántas columnas en escritorio
- Jerarquía visual (qué es lo más prominente arriba)
- Densidad de información (alta/media/baja)

### C. Componentes de UI presentes
Enumera: cards, tabs, segmented controls, dropdowns, date pickers,
sliders, modals, tooltips, badges, pills de estado, progress bars, etc.
Para cada uno, describe forma (rounded? sharp?), color, comportamiento.

### D. Tipos de visualización de datos
Para cada gráfico, indica:
- Tipo (line chart, bar chart, donut, area, heatmap, sparkline, gauge,
  radar, stacked bar, scatter, etc.)
- Qué dato muestra
- Ejes (qué variables)
- Colores usados (cuántas series, paleta)
- Interactividad (hover tooltip? click? zoom? selección de rango?)
- Etiquetas y leyendas (posición, formato)

### E. Métricas mostradas
Lista de métricas con: nombre exacto, unidad, formato (entero, decimal,
HH:MM:SS), cómo se contextualiza (vs promedio, vs ayer, vs meta, semáforo).

### F. Iconografía y motion
- Estilo de íconos (outline? filled? gradiente? animados?)
- Iconografía deportiva específica (corredor, corazón, zapatilla, montaña…)
- Animaciones (transiciones entre tabs, entrada de cards, pulsos)

### G. Paleta de colores observada en ESTA página
Lista los colores que ves (extrae los hex aproximados de los principales):
- Fondo
- Texto principal y secundario
- Color de marca / acento
- Colores semánticos: positivo (verde), alerta (amarillo), peligro (rojo),
  neutro (azul, gris)
- Colores por zona de FC (zone 1–5)
- Color del estado de fatiga, sueño, HRV (mapeo color ↔ significado)

### H. Tipografía
- ¿Serif o sans-serif para titulares?
- ¿Tabular numerals para cifras grandes?
- Jerarquía de tamaños (display, h1, h2, body, caption)
- Pesos usados (400, 500, 600, 700)

### I. Texto y voz de marca
- Cómo Connect titula los módulos (literal)
- Cómo explica métricas al usuario (cantidad de texto, tono: técnico,
  amigable, motivador)
- ¿Hay tooltips o "¿qué es esto?" embebidos?
- ¿Hay recomendaciones automáticas o solo datos crudos?

## Atención especial — reportería que LIEBRE NECESITA REPLICAR Y MEJORAR

Estas son las vistas que más necesitamos rediseñar para Liebre. Profundiza
en ellas:

### 1. Análisis post-actividad de carrera (vista de detalle)
- ¿Cómo organiza la información de UNA carrera?
- Orden: ¿mapa primero? ¿números primero? ¿gráfica de FC?
- Cómo muestra los SPLITS km a km (tabla? gráfico de barras? mixto?)
- Cómo visualiza distribución de zonas de FC (donut? stacked bar?
  porcentajes? minutos en cada zona?)
- Cómo muestra running dynamics: cadencia, oscilación vertical, GCT,
  longitud de zancada, balance izq/der
- Si hay "performance condition" en vivo durante la actividad, cómo se
  grafica

### 2. HRV nocturno
- Gráfica histórica (¿cuántos días default? 7, 28, 90?)
- Cómo muestra el "rango balanceado" personal
- Sparkline, alertas, comparación vs baseline propio
- Cómo etiqueta estados (balanced, low, unbalanced, poor)

### 3. Training Status / Load / VO2max
- Cómo combina carga aguda vs crónica visualmente (¿ACWR? ¿bandas?)
- Cómo muestra evolución de VO2max
- Indicador de "productivo / mantener / detraining / recuperación"

### 4. Sueño
- Stages de sueño (deep, light, REM, awake) — cómo los apila
- Score de sueño y cómo se construye visualmente

### 5. Calendario / vista semanal
- Cómo distribuye actividades en una grilla
- Color por tipo de entreno, intensidad o zona
- Cómo muestra el plan vs lo ejecutado

## REGLA IMPORTANTE — NO TOMES SCREENSHOTS

NO uses la herramienta de screenshot ni adjuntes imágenes al reporte. Las
páginas de Connect son muy largas (>2000 px) y rompen los límites de la
API cuando se acumulan en una sola sesión.

EN LUGAR DE SCREENSHOTS, describe textualmente con MÁXIMO detalle. Si vieras
un gráfico, descríbelo así:

> "Gráfico de barras horizontales apiladas en una sola fila, mostrando %
> de tiempo en cada zona de FC. De izquierda a derecha: Z1 (calentamiento,
> color gris claro #C8D6E0, ~5%), Z2 (fácil, azul medio #5B9BD5, ~70%),
> Z3 (aeróbico, verde #70AD47, ~20%), Z4 (umbral, naranja #ED7D31, ~4%),
> Z5 (VO2max, rojo #C00000, ~1%). Altura ~24 px, esquinas ligeramente
> redondeadas. Debajo, leyenda con dot de color + nombre de zona + minutos
> totales."

Ese nivel de detalle es lo que necesito. Reemplaza cualquier "captura de
pantalla" con descripción equivalente. Hex aproximados son suficientes —
no necesito EyeDropper, solo tu mejor estimación visual.

## OUTPUT FINAL — FORMATO ESPERADO

Devuelve TODO en MARKDOWN con esta estructura:

```
# Inventario visual de Garmin Connect para Liebre

## 1. Resumen ejecutivo (½ página)
- 3 cosas que Connect hace excelente y debemos replicar
- 3 limitaciones que Liebre puede superar con IA + ciencia
- Patrones visuales recurrentes (paleta global, sistema de cards, etc.)

## 2. Sistema de diseño extraído
### Paleta global
| Token | Hex aprox | Uso |
| ink   | #...      | texto principal |
| ...   | ...       | ... |

### Tipografía
- Display: ...
- Body: ...
- Tabular: ...

### Componentes recurrentes
- Card: ... (radio, sombra, padding)
- Pill de estado: ...
- ...

## 3. Inventario por página
Por cada página visitada, una sección con todos los apartados A–I.

## 4. Reportería detallada (las 5 vistas críticas)
Subsecciones extra-detalladas para las 5 vistas listadas arriba.

## 5. Recomendaciones para Liebre
Tu opinión: qué visualizaciones de Connect adoptar tal cual, qué cambiar
para darle el twist de "interpretación + ciencia", qué inventar nuevo.

Pensar especialmente en CÓMO mostrar:
- Por qué entrenar en Z2 fue mejor que Z4 esta semana (interpretación
  causal, no solo datos)
- Adaptación a la altitud como ventaja
- Próximo entrenamiento con justificación
- Análisis km a km con identificación de degradación de forma + cita
  científica del paper que respalda el umbral usado
```

## Restricciones

- Solo usa MI cuenta (la sesión ya está abierta en el browser).
- No clickees en NADA que requiera pago o suscripción premium.
- No publiques mis datos personales en el output (anonimiza fechas y
  números si las copias literales).
- Si una página no carga o falla, sigue con la siguiente.
- Si te encuentras con una pantalla en inglés y otra en español, marca la
  diferencia.

Empieza por la página 1 (Home / Resumen del día). Avísame cuando hayas
terminado las 11 páginas con el reporte completo en markdown.

## Si AUN ASÍ la sesión se vuelve muy larga o falla

Termina lo que llevas y entrégame un reporte PARCIAL con esta nota al inicio:
"REPORTE PARCIAL — páginas cubiertas: 1, 2, ..., X. Faltan: Y, Z."

Voy a relanzarte una segunda sesión solo para las páginas restantes,
referenciando el output anterior para mantener consistencia en paleta y
componentes.
```

---

## Cómo usarlo

1. Abre Chrome y entra a https://connect.garmin.com/modern/ con tu cuenta.
2. Activa la extensión Claude for Chrome (icono en la barra de extensiones).
3. Copia el bloque ` ``` ` completo de arriba (todo lo que está entre las tres comillas invertidas).
4. Pégalo en el panel de la extensión.
5. Confirma cada acción si la extensión te pide permiso para navegar.
6. Cuando termine, guarda el output (todo el markdown que Claude te genere) en `docs/connect-research-output.md` del repo.
7. Avísame y arranco el rediseño del dashboard de Liebre basado en el inventario.

## Qué hago yo con el output

Cuando me pases el markdown:

1. Extraigo la paleta y la consolido en `web/src/app/globals.css`.
2. Mapeo el sistema de componentes a los nuestros (cards, pills, gráficos).
3. Identifico qué gráficos necesito implementar con `recharts` (líneas, barras, donuts, sparklines).
4. Rediseño cada card del dashboard actual con la estética nueva.
5. Agrego nuevas vistas: análisis km a km, distribución de zonas, training status, calendario semanal.
6. **Capa Liebre encima**: cada métrica viene acompañada de su interpretación generada por el orchestrator + el paper citado.
