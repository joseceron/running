import type { Weekly } from "@/lib/api";

export function WeeklyTable({ weekly }: { weekly: Weekly }) {
  return (
    <div className="rounded-2xl border border-rule bg-paper p-6 col-span-2">
      <p className="text-xs uppercase tracking-widest text-muted mb-4">
        Historial semanal
      </p>
      {weekly.weeks.length === 0 ? (
        <p className="text-sm text-muted">
          Sin semanas registradas todavía.
        </p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-widest text-muted border-b border-rule/60">
              <th className="py-2 font-medium">Semana</th>
              <th className="py-2 font-medium text-right">Plan</th>
              <th className="py-2 font-medium text-right">Ejecutado</th>
              <th className="py-2 font-medium text-right">HRV prom</th>
              <th className="py-2 font-medium text-right">ACWR</th>
            </tr>
          </thead>
          <tbody>
            {weekly.weeks.map((w) => (
              <tr
                key={w.week_start}
                className="border-b border-rule/30 last:border-0"
              >
                <td className="py-3">{w.week_start}</td>
                <td className="py-3 tnum text-right">
                  {w.plan_km !== null ? `${w.plan_km.toFixed(1)} km` : "—"}
                </td>
                <td className="py-3 tnum text-right font-medium">
                  {w.executed_km !== null ? `${w.executed_km.toFixed(1)} km` : "—"}
                </td>
                <td className="py-3 tnum text-right">
                  {w.avg_hrv !== null ? `${w.avg_hrv.toFixed(0)} ms` : "—"}
                </td>
                <td className="py-3 tnum text-right">
                  {w.acwr !== null ? (
                    <span
                      className={
                        w.acwr > 1.5
                          ? "text-signal font-semibold"
                          : w.acwr < 0.8
                          ? "text-muted"
                          : "text-accent-deep font-medium"
                      }
                    >
                      {w.acwr.toFixed(2)}
                    </span>
                  ) : (
                    "—"
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {weekly.weeks[0]?.agent_notes && (
        <div className="mt-5 pt-5 border-t border-rule/60">
          <p className="text-xs uppercase tracking-widest text-muted mb-2">
            Nota del agente · semana actual
          </p>
          <p className="text-sm leading-relaxed">{weekly.weeks[0].agent_notes}</p>
        </div>
      )}
    </div>
  );
}
