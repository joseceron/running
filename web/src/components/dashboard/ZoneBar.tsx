/**
 * ZoneBar — barra horizontal apilada de distribución por zonas de FC.
 * Patrón estándar Garmin: Z1-Z5 con sus colores semánticos.
 *
 * Acepta % o minutos directos; renderiza con ancho proporcional.
 */

const ZONE_COLOR = [
  "var(--zone-1)",
  "var(--zone-2)",
  "var(--zone-3)",
  "var(--zone-4)",
  "var(--zone-5)",
] as const;

const ZONE_LABEL = ["Z1", "Z2", "Z3", "Z4", "Z5"] as const;

type ZoneDistribution = {
  /** Valores Z1-Z5; pueden ser % (0-100) o minutos. La normalización es proporcional al total. */
  values: [number, number, number, number, number];
  /** Si true, renderiza la leyenda inferior con labels y %. */
  showLegend?: boolean;
  /** Altura en px. Default 12. */
  height?: number;
};

export function ZoneBar({ values, showLegend = true, height = 12 }: ZoneDistribution) {
  const total = values.reduce((acc, v) => acc + v, 0);
  if (total === 0) {
    return (
      <div
        className="rounded-full bg-bg-card-hover"
        style={{ height }}
        aria-label="Sin datos de zonas"
      />
    );
  }

  return (
    <div>
      <div
        className="flex w-full overflow-hidden rounded-full"
        style={{ height }}
      >
        {values.map((v, i) => {
          const pct = (v / total) * 100;
          if (pct === 0) return null;
          return (
            <div
              key={i}
              style={{
                width: `${pct}%`,
                background: ZONE_COLOR[i],
              }}
              title={`${ZONE_LABEL[i]}: ${pct.toFixed(1)}%`}
            />
          );
        })}
      </div>
      {showLegend && (
        <div className="mt-3 grid grid-cols-5 gap-1 text-[10px]">
          {values.map((v, i) => {
            const pct = total > 0 ? (v / total) * 100 : 0;
            return (
              <div key={i} className="flex flex-col items-center">
                <div className="flex items-center gap-1">
                  <span
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ background: ZONE_COLOR[i] }}
                  />
                  <span className="font-semibold text-ink-secondary">
                    {ZONE_LABEL[i]}
                  </span>
                </div>
                <span className="text-ink-tertiary tnum mt-0.5">
                  {pct.toFixed(0)}%
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
