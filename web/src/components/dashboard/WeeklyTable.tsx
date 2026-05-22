/**
 * WeeklyTable — alineado con mockup HistoryCard.
 * ACWR como texto coloreado peso 700 (sin pill). Nota con border-left azul.
 */

import type { Weekly } from "@/lib/api";

function acwrColor(acwr: number): string {
  if (acwr > 1.3) return "var(--semantic-danger)";
  if (acwr >= 0.8) return "var(--semantic-positive)";
  return "var(--semantic-warning)";
}

export function WeeklyTable({ weekly }: { weekly: Weekly }) {
  return (
    <div className="card">
      <div className="mb-3.5">
        <span className="label-uppercase">Historial Semanal</span>
        <p className="text-[11px] text-ink-tertiary mt-1">
          Últimas {weekly.weeks.length} semanas
        </p>
      </div>

      {weekly.weeks.length === 0 ? (
        <p className="text-sm text-ink-secondary">Sin semanas registradas.</p>
      ) : (
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-rule/60">
              {["Sem.", "Plan", "Ejec.", "HRV", "ACWR"].map((h, i) => (
                <th
                  key={h}
                  className="label-uppercase font-medium py-1.5 px-1.5"
                  style={{ textAlign: i === 0 ? "left" : "right" }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {weekly.weeks.map((w) => (
              <tr
                key={w.week_start}
                className="hover:bg-bg-card-subtle transition-colors"
              >
                <td className="py-2.5 px-1.5 text-ink-secondary font-medium">
                  {w.week_start.slice(5)}
                </td>
                <td className="py-2.5 px-1.5 tnum text-right text-ink-tertiary">
                  {w.plan_km !== null ? `${w.plan_km.toFixed(1)} km` : "—"}
                </td>
                <td className="py-2.5 px-1.5 tnum text-right font-semibold text-ink-primary">
                  {w.executed_km !== null
                    ? `${w.executed_km.toFixed(1)} km`
                    : "—"}
                </td>
                <td className="py-2.5 px-1.5 tnum text-right text-ink-primary">
                  {w.avg_hrv !== null ? w.avg_hrv.toFixed(0) : "—"}
                </td>
                <td
                  className="py-2.5 px-1.5 tnum text-right font-bold"
                  style={{
                    color: w.acwr !== null ? acwrColor(w.acwr) : "var(--ink-tertiary)",
                  }}
                >
                  {w.acwr !== null ? w.acwr.toFixed(2) : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {weekly.weeks[0]?.agent_notes && (
        <div
          className="mt-3.5 px-3 py-2.5 rounded-md bg-bg-card-subtle"
          style={{ borderLeft: "3px solid var(--accent-brand)" }}
        >
          <span className="label-uppercase" style={{ fontSize: 10 }}>
            Nota del Agente
          </span>
          <p className="text-xs text-ink-secondary mt-1 leading-relaxed">
            {weekly.weeks[0].agent_notes}
          </p>
        </div>
      )}
    </div>
  );
}
