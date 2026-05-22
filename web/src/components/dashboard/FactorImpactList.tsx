/**
 * FactorImpactList — replica el patrón Body Battery de Connect con cards
 * de impacto signed (+/-). Liebre añade interpretación + cita.
 */

import { RowFactorCard } from "./RowFactorCard";

type Props = {
  hrv: { latest_value: number | null; baseline_ms: number | null };
  weekly: { acwr: number | null; executed_km: number | null };
};

export function FactorImpactList({ hrv, weekly }: Props) {
  const factors = [
    {
      name: "Sueño",
      value: "6h 32m",
      unit: "",
      impact: 41,
      interpretation:
        "Sueño dentro de tu rango funcional. Los stages de profundo y REM se completaron bien.",
    },
    {
      name: "Carrera del día",
      value: "Popayán · 5.22 km",
      unit: "",
      impact: -11,
      interpretation:
        "Carrera Z2 controlada. El impacto negativo es la depleción esperada de Body Battery.",
    },
    {
      name: "Estrés bajo",
      value: "1h 51m",
      unit: "",
      impact: 2,
    },
    {
      name: "Carga semanal (ACWR)",
      value: weekly.acwr?.toFixed(2) ?? "—",
      unit: "",
      impact:
        weekly.acwr && weekly.acwr > 0.8 && weekly.acwr < 1.3 ? 8 : -5,
      interpretation:
        weekly.acwr && weekly.acwr > 0.8 && weekly.acwr < 1.3
          ? "ACWR en zona segura — supercompensación favorecida."
          : "ACWR fuera de zona — ajustar volumen.",
      citation: "Gabbett (2016) · Br J Sports Med · Review",
    },
  ];

  return (
    <div className="card md:col-span-2">
      <div className="mb-4">
        <p className="label-uppercase">Factores que influyen en tu estado</p>
        <p className="text-xs text-ink-tertiary mt-1">
          Cada uno con su impacto numérico — patrón Connect, enriquecido con
          interpretación de Liebre.
        </p>
      </div>
      <div className="space-y-2">
        {factors.map((f, i) => (
          <RowFactorCard key={i} mode="signed" {...f} />
        ))}
      </div>
    </div>
  );
}
