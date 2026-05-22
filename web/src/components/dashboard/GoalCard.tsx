/**
 * GoalCard — adopta la estética Connect con fondo oscuro (mismo patrón de
 * la "Predisposición" en su Home) pero con el twist Liebre: countdown de
 * días + barra de progreso del entrenamiento hacia la meta.
 */

import type { Profile } from "@/lib/api";
import { formatGoalTime } from "@/lib/api";

export function GoalCard({
  profile,
  daysToGoal,
}: {
  profile: Profile;
  daysToGoal: number | null;
}) {
  if (!profile.goal_event || !profile.goal_date) {
    return (
      <div className="card">
        <p className="label-uppercase">Meta</p>
        <p className="text-sm text-ink-secondary mt-3">
          Configura tu meta para activar el plan adaptativo.
        </p>
      </div>
    );
  }

  // % aproximado del camino al goal — placeholder hasta tener fecha de inicio del entreno
  const totalDays = 365 * 0.4; // 4-5 meses típicos
  const elapsed = daysToGoal ? Math.max(0, totalDays - daysToGoal) : 0;
  const progressPct = Math.min(100, (elapsed / totalDays) * 100);

  return (
    <div className="card-dark relative overflow-hidden">
      <p className="label-uppercase opacity-60">Tu meta</p>

      <div className="mt-3 mb-4">
        <p className="metric-display text-6xl text-ink-on-dark">
          {profile.goal_event}
        </p>
        <p className="text-sm text-ink-on-dark-soft mt-1">
          en {formatGoalTime(profile.goal_time_secs)} · {profile.goal_date}
        </p>
      </div>

      {daysToGoal !== null && (
        <div className="flex items-end justify-between mb-4">
          <div>
            <p className="metric-kpi text-4xl text-accent-brand-soft">
              {daysToGoal}
            </p>
            <p className="text-xs text-ink-on-dark-soft mt-1">días por delante</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-ink-on-dark-soft uppercase tracking-wider">
              Progreso
            </p>
            <p className="text-sm font-medium text-ink-on-dark tnum">
              {progressPct.toFixed(0)}%
            </p>
          </div>
        </div>
      )}

      <div className="h-1 rounded-full bg-white/10 overflow-hidden">
        <div
          className="h-full bg-accent-brand-soft transition-all"
          style={{ width: `${progressPct}%` }}
        />
      </div>

      <div
        className="absolute -bottom-16 -right-16 w-48 h-48 rounded-full opacity-15"
        style={{
          background:
            "radial-gradient(closest-side, var(--accent-brand-soft), transparent)",
        }}
      />
    </div>
  );
}
