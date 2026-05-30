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

/** Paleta de acentos por módulo en orden 1-8. */
const MODULE_ACCENTS = [
  { accent: "#2f81f7", icon: "◐" }, // 1 zonas — azul
  { accent: "#3fb950", icon: "❤" }, // 2 HRV — verde
  { accent: "#f0883e", icon: "▲" }, // 3 ACWR — naranja
  { accent: "#a5a0ff", icon: "◇" }, // 4 biomecánica — púrpura
  { accent: "#ff7b72", icon: "✚" }, // 5 lesión — rojo
  { accent: "#e3b341", icon: "◈" }, // 6 nutrición — amarillo
  { accent: "#39d353", icon: "↗" }, // 7 adaptación — teal
  { accent: "#79c0ff", icon: "✦" }, // 8 evidencia — azul claro
] as const;

export function moduleAccent(n: number): { accent: string; icon: string } {
  return MODULE_ACCENTS[n - 1] ?? MODULE_ACCENTS[0];
}

export const HERO_STATS = [
  { value: "−33%", label: "menos tiempo en zona de riesgo", note: "caso real, en 1 semana" },
  { value: "14", label: "noches para conocer tu cuerpo", note: "tu línea base, no un promedio" },
  { value: "40+", label: "estudios científicos detrás", note: "cada consejo con su cita" },
  { value: "8", label: "análisis automáticos cada día", note: "sueño · carga · técnica" },
] as const;

/** Los 3 pasos del "Cómo funciona" — Garmin mide, Liebre decide. Tono aliado. */
export const HOW_STEPS = [
  {
    icon: "⌚",
    title: "Conecta tu reloj",
    body: "En 2 minutos. Liebre lee tu sueño, tu recuperación y tus entrenos directo de Garmin — sin que tengas que apuntar nada.",
  },
  {
    icon: "🧠",
    title: "Liebre entiende tus datos",
    body: "Cruza lo que mide tu reloj con más de 40 estudios científicos y aprende cómo responde tu cuerpo durante las primeras 14 noches.",
  },
  {
    icon: "☀️",
    title: "Cada mañana sabes qué hacer",
    body: "¿Hoy te conviene entrenar fuerte, suave o descansar? Una respuesta clara, en una frase, con la ciencia que la respalda.",
  },
] as const;

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
    realData: "Caso real: 80% del tiempo en zona alta, detectado en el primer análisis",
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
    realData: "Tu línea base personal, lista en 14 noches",
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
    realData: "Caso real: patrón de semanas hard/rest de alto riesgo, detectado a tiempo",
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
      "GCT contextualizado con lesión activa (umbral por tejido)",
      "Oscilación vertical: flag si >9 cm",
      "Detección de degradación de forma: cadencia km1 vs km5",
      "Tendencia semanal de economía (mejora/empeora)",
    ],
    realData: "Distingue caminata (335 ms) de carrera (251 ms) y qué hacer con cada dato",
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
    realData: "Tu historial de lesiones, presente en cada recomendación de carga",
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
    realData: "Cálculo personalizado: BMR, proteína diaria y balance según tu peso",
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
    realData: "Caso real: tiempo en zona alta de 33.7% → 0.6% en una semana",
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
    realData: "Cada consejo enlaza al estudio que lo respalda",
    evidence: [
      { level: 3, cite: "Nuestro diferencial", finding: "Pocas apps vinculan cada recomendación con literatura científica primaria" },
    ],
  },
];

export const REAL_DATA_CARDS = [
  {
    headline: "80%",
    sub: "del tiempo en zona alta",
    body: "El primer análisis de historial lo detectó y lo vinculó con una lesión previa de sóleo. Una señal que es fácil pasar por alto sin que alguien la interprete por ti (Seiler & Kjerland, 2006).",
    tag: "Historial — 17 sesiones desde dic 2025",
  },
  {
    headline: "0.6%",
    sub: "zona alta en la sesión del viernes",
    body: "En 3 días bajó de 33.7% a 0.6%. La herramienta: caminar-correr guiado por la frecuencia cardíaca real, con umbral 138–151 lpm. Ritmo resultante: 8:08–9:04/km.",
    tag: "Semana 1 de corrección — may 12–17",
  },
  {
    headline: "7.18 cm",
    sub: "rebote al correr (↓ desde 8.3)",
    body: "Bajando la intensidad, el rebote vertical mejoró 13% en una semana. Menos rebote = menos carga en el sóleo. Liebre correlacionó la mejora con la cadencia mantenida en 153 pasos por minuto.",
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
      "Para empezar: lo esencial para saber, cada mañana, qué hacer con los datos que tu reloj ya captura.",
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
      "Todo el análisis de Liebre, por una fracción de lo que cuesta un entrenador personal ($150–400/mes) — y con la ciencia que puedes verificar.",
  },
] as const;
