/**
 * Data estática de la landing — separada del JSX para mantener limpio el page.
 * Basado en runner-agent/output/propuesta_producto.html
 */

export type Module = {
  n: number;
  title: string;
  description: string;
  bullets: string[];
  realData: string;
  evidence: Array<{ level: 3 | 2 | 1; cite: string; finding: string }>;
};

export const HERO_STATS = [
  { value: "8", label: "Módulos de análisis" },
  { value: "40+", label: "Papers científicos integrados" },
  { value: "0", label: "Valores poblacionales genéricos" },
  { value: "100%", label: "Baseline personal del corredor" },
] as const;

export const PAIN_POINTS = [
  {
    icon: "🎯",
    title: "El pace sugerido está mal calibrado",
    body: "Connect usa fórmulas estimadas. Liebre usa tu respuesta fisiológica real medida sesión a sesión. Para José, Z2 real es 7:00–8:30/km, no 6:15.",
  },
  {
    icon: "📊",
    title: "No detecta la inversión de zonas",
    body: "José tenía 80% de sus sesiones en Z4–Z5. Connect no detectó ni alertó. Liebre lo identificó con el primer análisis de historial.",
  },
  {
    icon: "🦵",
    title: "No recuerda las lesiones",
    body: "Connect+ no sabe que tienes desgarro de sóleo al 49%. Cada plan es genérico. Liebre integra el historial clínico en cada recomendación de carga.",
  },
  {
    icon: "🔬",
    title: "Sin respaldo científico específico",
    body: "Connect da instrucciones. Liebre cita el paper que respalda cada decisión: título, año, journal, nivel de evidencia (RCT / meta-análisis / cohorte).",
  },
  {
    icon: "📈",
    title: "Otras apps adaptativas no muestran tu salud",
    body: "One Running ($14.99/mes) y Runna ($19.99) hacen planes que se ajustan a tu fatiga, pero NO te muestran tu HRV, sueño profundo, Body Battery ni cronología 24h. Liebre visualiza e interpreta cada métrica de tu reloj — no solo la usa internamente.",
  },
  {
    icon: "⌚",
    title: "Hoy: integración nativa con Garmin",
    body: "Sincronización directa con Garmin Connect — HRV, running dynamics, Body Battery, sueño y actividad por minuto. Coros, Polar y Apple Health en el roadmap del próximo trimestre.",
  },
] as const;

export const COMPARISON: Array<{
  capability: string;
  connect: string;
  liebre: string;
}> = [
  { capability: "Plan de entrenamiento semanal", connect: "Genérico por objetivo", liebre: "Ajustado a tu respuesta real" },
  { capability: "Pace objetivo basado en fisiología real", connect: "Estimado por algoritmo", liebre: "Medido de tus sesiones reales" },
  { capability: "Detección de inversión de zonas (Z4–Z5 excesivo)", connect: "No disponible", liebre: "Análisis de historial completo" },
  { capability: "Baseline HRV personal (no poblacional)", connect: "Usa valores medios", liebre: "Construido en 14 noches" },
  { capability: "Integración de historial de lesiones", connect: "No existe", liebre: "Cada plan considera tu lesión" },
  { capability: "ACWR — ratio carga aguda/crónica", connect: "Training Load parcial", liebre: "Gabbett 2016, alertas en tiempo real" },
  { capability: "Análisis running dynamics vs riesgo lesión", connect: "Muestra datos, no interpreta", liebre: "GCT + balance + oscilación con flag clínico" },
  { capability: "Detección de degradación de forma dentro de sesión", connect: "No disponible", liebre: "Cadencia km1 vs km final, alerta ≥5%" },
  { capability: "Nutrición periodizada por tipo de sesión", connect: "Calorías genéricas", liebre: "Mifflin-St Jeor + carga real Garmin" },
  { capability: "Respaldo científico por recomendación", connect: "Sin citas", liebre: "Paper, año, journal, nivel evidencia" },
  { capability: "Evolución semanal de distribución de zonas", connect: "No disponible", liebre: "Gráfico comparativo sesión a sesión" },
  { capability: "Protocolo específico por tipo de lesión", connect: "No existe", liebre: "Ejercicios excéntricos, carga progresiva" },
];

export const MODULES: Module[] = [
  {
    n: 1,
    title: "Diagnóstico de Distribución de Zonas",
    description:
      "Analiza tu historial completo de sesiones y detecta si la distribución de intensidad sigue el modelo 80/20 polarizado. Identifica inversión de zonas — el patrón más asociado a lesiones de tejido blando en corredores recreativos.",
    bullets: [
      "% real en cada zona vs objetivo 80/20",
      "Gráfico de evolución sesión a sesión",
      "Alerta automática si Z4–Z5 > 25% acumulado",
      "Pace Z2 real calibrado a tu FC, no estimado",
    ],
    realData: "José tenía 80% en Z4–Z5 — Connect nunca alertó",
    evidence: [
      { level: 3, cite: "Seiler & Kjerland (2006) · Scand J Med Sci Sports", finding: "300+ atletas de élite, 75–80% baja intensidad como distribución óptima" },
      { level: 3, cite: "Stöggl & Sperlich (2014) · Front Physiol", finding: "RCT: modelo polarizado supera al entrenamiento de umbral en VO₂máx" },
    ],
  },
  {
    n: 2,
    title: "Perfil HRV Personal",
    description:
      "Construye el baseline de HRV nocturno individual en las primeras 14 noches. Todas las decisiones de carga se toman en relación a tu HRV, no a valores poblacionales. Detecta supresión del sistema nervioso autónomo antes de que sientas el cansancio.",
    bullets: [
      "Rolling 7-day mean sobre últimas 14 noches",
      "Alerta: HRV ≥ 1.5σ por debajo del baseline personal",
      "Correlación HRV vs rendimiento en sesiones Z4–Z5",
      "Estado del sistema nervioso autónomo (simpático/parasimpático)",
    ],
    realData: "José en construcción de baseline (noche 8/14)",
    evidence: [
      { level: 3, cite: "Plews et al. (2013) · Int J Sports Physiol Perform", finding: "HRV individual superior a FC reposo para monitorear adaptación al entrenamiento" },
      { level: 2, cite: "Kiviniemi et al. (2010) · J Strength Cond Res", finding: "Planes guiados por HRV individual mejoran VO₂máx vs planes fijos" },
    ],
  },
  {
    n: 3,
    title: "Carga y Riesgo de Lesión (ACWR)",
    description:
      "Calcula el Acute:Chronic Workload Ratio semana a semana. Alerta cuando la carga aguda supera en 1.5× la crónica. Detecta el 'pico de riesgo' antes de que ocurra la lesión, no después.",
    bullets: [
      "ACWR semanal con proxy carga = km × (FC/FCmáx)",
      "Semáforo: 0.8–1.3 seguro / >1.5 alto riesgo",
      "Histograma de carga 8 semanas",
      "Volumen máximo recomendado para la próxima semana (+10%)",
    ],
    realData: "Patrón detectado: semanas alternas hard/rest de alto riesgo",
    evidence: [
      { level: 3, cite: "Gabbett (2016) · Br J Sports Med", finding: "ACWR >1.5 asociado a riesgo de lesión 4–6× mayor" },
      { level: 2, cite: "Nielsen et al. (2012) · Br J Sports Med", finding: "Incremento >10%/sem es predictor independiente de lesión" },
    ],
  },
  {
    n: 4,
    title: "Economía de Carrera y Biomecánica",
    description:
      "Interpreta los running dynamics de Garmin (GCT, oscilación vertical, balance izq/der, longitud de zancada) en función de tu historial de lesiones y la literatura. No muestra números: explica qué hacer con ellos.",
    bullets: [
      "GCT contextualizado con lesión activa (sóleo → umbral 240 ms)",
      "Oscilación vertical: flag si >9 cm",
      "Detección de degradación de forma: cadencia km1 vs km5",
      "Tendencia semanal de economía (mejora/empeora)",
    ],
    realData: "GCT 335ms caminata vs 251ms carrera — Connect no distingue",
    evidence: [
      { level: 3, cite: "Heiderscheit et al. (2011) · Med Sci Sports Exerc", finding: "Aumentar cadencia 5–10% reduce fuerzas de impacto hasta 20%" },
      { level: 2, cite: "Aubol (2026) · J Sci Med Sport", finding: "GCT reducido correlaciona con menor fuerza en tendón de Aquiles" },
    ],
  },
  {
    n: 5,
    title: "Protocolo de Lesión Activa",
    description:
      "Integra el historial clínico del corredor en cada recomendación. No es un disclaimer genérico: es un protocolo específico por tipo de lesión con ejercicios, umbrales de carga y señales de alarma.",
    bullets: [
      "Ejercicios excéntricos específicos por lesión",
      "Umbral de FC máxima antes de requerir calentamiento ampliado",
      "Señales de recaída: qué sensaciones detienen el plan",
      "Progresión de vuelta al volumen post-lesión",
    ],
    realData: "Desgarro sóleo 49% en cada recomendación de José",
    evidence: [
      { level: 3, cite: "Alfredson et al. (1998) · Am J Sports Med", finding: "Protocolo excéntrico de sóleo: 12 semanas, 100% de atletas vs cirugía" },
      { level: 2, cite: "Beyer et al. (2015) · Am J Sports Med", finding: "Ejercicio excéntrico > PRP en tendinopatía a 6 meses" },
    ],
  },
  {
    n: 6,
    title: "Nutrición Periodizada",
    description:
      "Cruza el gasto calórico real de Garmin con el tipo de sesión del día para calcular balance y requerimientos de macros. Detecta déficit calórico crónico (riesgo de pérdida de masa muscular) y alerta proteica en rodajes largos.",
    bullets: [
      "BMR personalizado (Mifflin-St Jeor) + TDEE por día",
      "Alerta: déficit >500 kcal por 3+ días consecutivos",
      "Alerta proteica: <1.6 g/kg en días >15 km",
      "Timing de macros: pre/post sesión por tipo",
    ],
    realData: "1,597 kcal BMR · 109g proteína/día · 68 kg",
    evidence: [
      { level: 3, cite: "Morton et al. (2018) · Br J Sports Med", finding: "Meta-análisis: 1.6 g/kg/día umbral mínimo para síntesis proteica" },
      { level: 2, cite: "Impey et al. (2018) · Eur J Sport Sci", finding: "'Train low, compete high': periodizar carbohidratos mejora mitocondrias" },
    ],
  },
  {
    n: 7,
    title: "Adaptación Semanal y Tendencias",
    description:
      "Compara cada semana contra la anterior en distribución de zonas, volumen, cadencia y métricas de sueño. Muestra si estás adaptando o estancando, y ajusta el plan de la semana siguiente en consecuencia.",
    bullets: [
      "Comparativa semana a semana: Z2% esta semana vs anterior",
      "Tendencia de cadencia (mejora/estancamiento)",
      "Sueño profundo + REM vs carga de entrenamiento",
      "Ajuste automático del plan si ACWR > 1.3 o sueño <6h",
    ],
    realData: "Z4% bajó de 33.7% → 0.6% en una semana",
    evidence: [
      { level: 3, cite: "Simpson et al. (2017) · Sports Med", finding: "Sueño 8h mejora tiempo de reacción 15%" },
      { level: 2, cite: "Mujika & Padilla (2003) · Sports Med", finding: "Ciclos carga/descarga 30% cada 4 sem optimizan supercompensación" },
    ],
  },
  {
    n: 8,
    title: "Evidencia Científica por Demanda",
    description:
      "Cada recomendación del agente incluye la cita del paper que la respalda. Además, puedes preguntar sobre cualquier tema de entrenamiento y recibir una síntesis de la literatura disponible (Scopus + Web of Science).",
    bullets: [
      "Búsqueda en tiempo real en Scopus y Web of Science",
      "Clasificación: RCT ★★★ / Cohorte ★★ / Observacional ★",
      "Abstract + cita APA formateada por recomendación",
      "Caché de 7 días para keywords frecuentes",
    ],
    realData: "9 papers integrados en reportes activos",
    evidence: [
      { level: 3, cite: "Diferencial exclusivo", finding: "Ninguna app del mercado vincula recomendaciones con literatura primaria" },
    ],
  },
];

export const REAL_DATA_CARDS = [
  {
    headline: "80%",
    sub: "de sesiones en Z4–Z5",
    body: "Connect nunca alertó. El agente lo detectó en el primer análisis y vinculó la inversión de zonas con el desgarro de sóleo previo (Seiler & Kjerland, 2006).",
    tag: "Historial — 17 sesiones desde dic 2025",
  },
  {
    headline: "0.6%",
    sub: "Z4 en sesión del viernes",
    body: "En 3 días el corredor bajó de 33.7% Z4 a 0.6%. Herramienta: walk-run guiado por FC real con umbral 138–151 lpm. Pace resultante: 8:08–9:04/km.",
    tag: "Semana 1 de corrección — may 12–17",
  },
  {
    headline: "7.18 cm",
    sub: "Oscilación vertical (↓ desde 8.3)",
    body: "Bajando la intensidad a Z2, la oscilación vertical mejoró 13% en una semana. Menor rebote = menor carga en sóleo. Agente correlacionó la mejora con cadencia mantenida en 153 spm.",
    tag: "Running dynamics — may 15",
  },
] as const;

/** Tasa de cambio USD→COP referencial. Lanzamiento Colombia.
 *  Convertir a fetch dinámico en producción si el delta importa. */
export const USD_TO_COP = 4000;

export function fmtCOP(usd: number): string {
  const cop = Math.round((usd * USD_TO_COP) / 1000) * 1000;
  return `$${cop.toLocaleString("es-CO")}`;
}

export const PLANS = [
  {
    tier: "Esencial",
    price: 12,
    badge: null,
    features: [
      "Sincronización nativa con Garmin Connect",
      "Reporte matutino diario (HRV + carga + recomendación)",
      "Análisis post-sesión automático",
      "Módulos 1, 3 y 7 (zonas, ACWR, tendencias)",
      "Plan semanal adaptativo",
      "Historial de 6 meses",
    ],
    footnote:
      "Garmin Connect+ ($8.99) muestra datos sin interpretar. One Running ($14.99) hace planes adaptativos pero NO visualiza tu HRV, sueño ni Body Battery.",
  },
  {
    tier: "Pro",
    price: 29,
    badge: "Recomendado",
    features: [
      "Todo lo de Esencial",
      "Todos los 8 módulos activos",
      "Evidencia científica por demanda (Scopus + WoS)",
      "Protocolo de lesión personalizado",
      "Nutrición periodizada con alertas",
      "Análisis biomecánico sesión a sesión",
      "Historial completo sin límite",
    ],
    footnote:
      "Entrenador personal de running: $150–400/mes — sin acceso a datos Garmin ni literatura científica integrada",
  },
] as const;
