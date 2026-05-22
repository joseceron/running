/**
 * SplitsTable — tabla densa de splits km a km, estilo Connect.
 */

import type { ActivitySplit } from "@/lib/api";

export function SplitsTable({ splits }: { splits: ActivitySplit[] }) {
  return (
    <div className="card">
      <div className="mb-4">
        <span className="label-uppercase">Splits · kilómetro a kilómetro</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-rule/60">
              {["Km", "Tiempo", "Ritmo", "FC med", "FC máx", "Cadencia", "Zancada", "GCT", "Ascenso"].map((h, i) => (
                <th
                  key={h}
                  className="label-uppercase font-medium py-2 px-2"
                  style={{ textAlign: i === 0 ? "left" : "right" }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {splits.map((s) => (
              <tr
                key={s.km}
                className="border-b border-rule/15 last:border-0 hover:bg-bg-card-subtle transition-colors"
              >
                <td className="py-2.5 px-2 text-ink-primary font-semibold tnum">
                  {s.km}
                </td>
                <td className="py-2.5 px-2 tnum text-right text-ink-secondary">
                  {fmt(s.time_secs)}
                </td>
                <td className="py-2.5 px-2 tnum text-right font-semibold text-ink-primary">
                  {s.pace}
                </td>
                <td className="py-2.5 px-2 tnum text-right text-ink-secondary">
                  {s.avg_hr}
                </td>
                <td className="py-2.5 px-2 tnum text-right text-ink-secondary">
                  {s.max_hr}
                </td>
                <td
                  className="py-2.5 px-2 tnum text-right font-medium"
                  style={{
                    color: s.cadence >= 160 ? "var(--chart-cadence-good)" :
                           s.cadence >= 140 ? "var(--ink-primary)" :
                           "var(--chart-cadence-low)",
                  }}
                >
                  {s.cadence}
                </td>
                <td className="py-2.5 px-2 tnum text-right text-ink-secondary">
                  {s.stride_m.toFixed(2)} m
                </td>
                <td className="py-2.5 px-2 tnum text-right text-ink-secondary">
                  {s.gct_ms}
                </td>
                <td className="py-2.5 px-2 tnum text-right text-ink-secondary">
                  +{s.elevation_gain_m.toFixed(0)} m
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function fmt(secs: number): string {
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}
