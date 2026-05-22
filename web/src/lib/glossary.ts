/**
 * Glosario de términos especializados de running.
 *
 * Cada entrada tiene una versión `short` (1 línea para tooltip) y `long`
 * (varias frases para el panel). Diseñado para que un corredor casual
 * pueda entender todas las métricas que Liebre muestra.
 */

export type GlossaryEntry = {
  term: string;
  short: string;
  long: string;
  example?: string;
};

export const GLOSSARY = {
  cadencia: {
    term: "Cadencia",
    short:
      "Pasos por minuto durante la carrera. Indicador clave de eficiencia y prevención de lesiones.",
    long:
      "La cadencia es la cantidad de pasos que das por minuto contando ambos pies. Una cadencia óptima (165-180 spm) reduce el impacto sobre rodillas y tobillos porque acortas la zancada. Cadencias menores a 160 spm suelen indicar zancadas demasiado largas y mayor riesgo de lesión.",
    example: "146 spm = 146 pasos en 60 s.",
  },
  spm: {
    term: "SPM",
    short: "Steps Per Minute — pasos por minuto.",
    long:
      "SPM (Steps Per Minute) es la unidad universal para medir cadencia: cuántos pasos das en 60 segundos contando ambos pies. La mayoría de relojes deportivos usa esta sigla.",
  },
  gct: {
    term: "GCT",
    short:
      "Ground Contact Time — milisegundos que el pie permanece tocando el suelo en cada paso.",
    long:
      "GCT (Ground Contact Time) mide cuánto tiempo tu pie pisa el suelo en cada zancada. Corredores eficientes tienen GCT entre 200-280 ms; valores >320 ms suelen indicar zancada poco económica o fatiga. Reducir el GCT mejora la economía de carrera.",
    example: "301 ms = pie en contacto con el suelo 0.3 s por paso.",
  },
  ppm: {
    term: "ppm",
    short: "Pulsaciones por minuto (latidos del corazón).",
    long: "ppm = pulsaciones por minuto. Mide la frecuencia cardíaca: cuántas veces late tu corazón en 60 segundos.",
  },
  lpm: {
    term: "lpm",
    short: "Latidos por minuto. Equivalente a ppm.",
    long: "lpm = latidos por minuto. Es lo mismo que ppm — mide la frecuencia cardíaca.",
  },
  fc_max: {
    term: "FC máxima",
    short:
      "El límite más alto de tu frecuencia cardíaca. Define los rangos de cada zona de entrenamiento.",
    long:
      "FC máxima es la frecuencia cardíaca más alta que tu corazón puede alcanzar. Se estima como 220 - edad (José: ~184 lpm) pero el valor REAL se mide en un test de esfuerzo o se observa en sesiones a tope. Todas las zonas (Z1-Z5) se calculan como porcentaje de tu FC máx.",
    example: "FC máx 190 lpm → Z2 (zona fácil) ≈ 60-70% = 114-133 lpm.",
  },
  fc_reposo: {
    term: "FC en reposo",
    short:
      "Tu frecuencia cardíaca al despertar, antes de levantarte. Indicador de fitness cardiovascular.",
    long:
      "FC en reposo es la cantidad de latidos por minuto de tu corazón cuando estás completamente relajado (idealmente al despertar). Cuanto MÁS BAJA, mejor — refleja un corazón eficiente. Los corredores entrenados suelen tener 40-55 lpm; sedentarios 70-80 lpm. Bajar de 56 a 50 lpm en una semana (caso de José) es señal clara de adaptación aeróbica.",
    example: "51 lpm = corazón bien entrenado.",
  },
  vfc: {
    term: "VFC",
    short:
      "Variabilidad de la Frecuencia Cardíaca — variaciones entre cada latido. Sinónimo de HRV.",
    long:
      "VFC (Variabilidad de la Frecuencia Cardíaca) es la traducción al español de HRV (Heart Rate Variability). Mide las microvariaciones entre latido y latido. VFC alta = sistema nervioso recuperado; VFC baja = fatiga acumulada o estrés. Tu baseline personal es más útil que comparar contra valores poblacionales.",
    example: "52 ms = la media de variación entre latidos nocturnos.",
  },
  ritmo: {
    term: "Ritmo",
    short:
      "Tiempo que tardas en cubrir un kilómetro. Se expresa en minutos:segundos por km.",
    long:
      "El ritmo (o pace) es lo opuesto a la velocidad: en lugar de medir km/h, mide cuántos minutos te toma correr 1 km. Es la métrica estándar en running. Un ritmo de 5:00/km significa 5 minutos para correr un kilómetro.",
    example: "9:21 /km = 9 minutos 21 s para 1 km.",
  },
  zancada: {
    term: "Zancada",
    short: "Longitud (en metros) de cada paso de carrera.",
    long:
      "La longitud de zancada es la distancia que recorres con cada paso. Está directamente relacionada con la cadencia y el ritmo. Una zancada demasiado larga genera más impacto y suele asociarse a cadencias bajas.",
    example: "0.72 m = cada paso cubre 72 cm.",
  },
  hrv: {
    term: "HRV",
    short:
      "Heart Rate Variability — variabilidad entre latidos. Indicador del sistema nervioso autónomo.",
    long:
      "HRV (Heart Rate Variability) o VFC (Variabilidad de la Frecuencia Cardíaca) mide las variaciones milimétricas entre latido y latido. HRV alto indica un sistema nervioso recuperado; HRV bajo indica fatiga, estrés o falta de descanso. Tu baseline personal es más útil que el valor absoluto.",
    example: "52 ms = la media de las variaciones nocturnas fue 52 milisegundos.",
  },
  acwr: {
    term: "ACWR",
    short:
      "Acute:Chronic Workload Ratio — relación entre tu carga reciente y la habitual.",
    long:
      "ACWR (Acute:Chronic Workload Ratio) compara tu carga aguda (últimos 7 días) con tu carga crónica (últimas 4 semanas promedio). Valores 0.8-1.3 = zona segura; >1.5 = riesgo elevado de lesión por sobrecarga; <0.8 = posible detraining.",
    example: "ACWR 1.05 = haces 5% más de lo habitual. Zona segura.",
  },
  vo2max: {
    term: "VO₂max",
    short:
      "Capacidad máxima de tu cuerpo para usar oxígeno durante ejercicio intenso.",
    long:
      "VO₂max es el volumen máximo de oxígeno por minuto y kilo de peso que tu cuerpo puede consumir. Es el mejor indicador de fitness cardiovascular. Para sub-1:50 en media maratón se requiere ~52-53 ml/kg/min.",
    example: "46 ml/kg/min = bueno, pero hay margen hacia sub-1:50.",
  },
  z1: {
    term: "Z1",
    short: "Zona 1 · Calentamiento. Muy fácil — puedes hablar normalmente.",
    long:
      "Z1 (50-60% de tu FC máxima) es la zona de calentamiento o recuperación activa. No genera adaptación pero ayuda a movilizar.",
  },
  z2: {
    term: "Z2",
    short:
      "Zona 2 · Aeróbica fácil. El 'oro' del entrenamiento de base — habla con frases cortas.",
    long:
      "Z2 (60-70% de tu FC máxima) construye base aeróbica, mejora la capacidad mitocondrial y reduce el riesgo de lesión. Es la zona donde deberías pasar el 80% de tu tiempo si entrenas polarizado (Seiler 2010).",
  },
  z3: {
    term: "Z3",
    short: "Zona 3 · Aeróbica moderada. Tempo. Habla con palabras sueltas.",
    long:
      "Z3 (70-80% de tu FC máxima) es zona aeróbica moderada. Útil en sesiones tempo pero abusar de ella es el error más común — produce fatiga sin las adaptaciones del Z4-Z5.",
  },
  z4: {
    term: "Z4",
    short: "Zona 4 · Umbral. Solo respiras, no hablas. Usar con moderación.",
    long:
      "Z4 (80-90% de tu FC máxima) es la zona de umbral láctico. Series y tempo intensos. En un plan polarizado se hace solo 1-2 veces por semana.",
  },
  z5: {
    term: "Z5",
    short: "Zona 5 · VO₂max. Esfuerzo casi máximo. Series cortas, recuperación larga.",
    long:
      "Z5 (90-100% de tu FC máxima) entrena la capacidad cardíaca máxima. Series de 30s-2min con recuperación completa. Pocas repeticiones, alto impacto.",
  },
  drills_skipping: {
    term: "Drills de skipping",
    short:
      "Ejercicios de coordinación: trotar elevando rodillas o golpeando talones a glúteo.",
    long:
      "Los 'skipping drills' son ejercicios técnicos breves (10-30 s) que activan los patrones neuromusculares de la carrera económica: A-skip (elevar rodilla), B-skip (extender pierna), butt kicks (golpear glúteo con talón). Hacerlos 2-3 veces por semana antes del entreno mejora la cadencia y reduce zancadas excesivas.",
  },
  excentrico_soleo: {
    term: "Excéntrico de sóleo",
    short:
      "Ejercicio donde bajas el talón controladamente. Crítico para prevenir desgarros.",
    long:
      "El excéntrico de sóleo se hace parado en un escalón con la punta del pie: subes con ambos pies y bajas controladamente con uno solo, dejando el talón colgar bajo el escalón. Fortalece el sóleo en su fase de elongación, donde se producen la mayoría de desgarros. Protocolo: 3 series × 15 reps por pierna, 2-3 veces por semana.",
  },
  cronologia_24h: {
    term: "Cronología 24h",
    short:
      "Mapa visual de tu día: Body Battery, estrés, sueño y actividad sobre 24 horas.",
    long:
      "La cronología 24h cruza cuatro métricas sobre el mismo eje temporal: la línea negra es tu Body Battery (energía), el área naranja es estrés momento a momento, las bandas azules son sueño, y los marcadores violeta son actividades físicas. Permite ver el día completo y entender la causalidad entre las métricas.",
  },
  body_battery: {
    term: "Body Battery",
    short:
      "Métrica de Garmin que estima tu energía disponible en una escala 0-100.",
    long:
      "Body Battery (de Garmin) combina HRV, estrés, sueño y actividad para estimar cuánta 'batería' tienes. Se carga con descanso y sueño, se descarga con estrés y ejercicio. Es útil como referencia rápida pero NO reemplaza a HRV + ACWR.",
  },
  baseline: {
    term: "Baseline personal",
    short:
      "Tu valor habitual de una métrica. Construido con TUS datos, no con promedios poblacionales.",
    long:
      "Tu baseline es el valor de referencia individual de una métrica (HRV, FC reposo, etc.) construido con tus propios datos de las últimas 2-4 semanas. Comparar contra tu baseline es siempre más útil que compararte con rangos poblacionales.",
  },
  training_effect: {
    term: "Training Effect",
    short:
      "Escala 0-5 que mide el impacto fisiológico de una sesión (aeróbico/anaeróbico).",
    long:
      "Training Effect (TE) mide el impacto de un entreno en una escala 0-5: 0-1.9 sin beneficio, 2.0-2.9 mantenimiento, 3.0-3.9 mejora, 4.0-4.9 alto impacto, 5.0 sobrecarga. Se separa en aeróbico y anaeróbico. Sesiones bajas (TE 2) acumuladas construyen base mucho mejor que pocas sesiones de TE alto.",
  },
} as const;

export type GlossaryKey = keyof typeof GLOSSARY;
