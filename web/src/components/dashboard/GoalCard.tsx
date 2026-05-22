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
      <div className="rounded-2xl border border-rule bg-paper-warm/40 p-6">
        <p className="text-xs uppercase tracking-widest text-muted mb-2">Meta</p>
        <p className="text-sm text-muted">Sin meta configurada todavía.</p>
      </div>
    );
  }
  return (
    <div className="rounded-2xl border border-rule bg-ink text-paper p-6 relative overflow-hidden">
      <p className="text-xs uppercase tracking-widest opacity-60 mb-3">
        Tu meta
      </p>
      <p className="metric text-6xl mb-1">{profile.goal_event}</p>
      <p className="text-sm opacity-80 mb-6">
        objetivo {formatGoalTime(profile.goal_time_secs)} · {profile.goal_date}
      </p>
      {daysToGoal !== null && (
        <div className="flex items-end gap-3">
          <p className="metric text-4xl text-accent">{daysToGoal}</p>
          <p className="text-sm opacity-80 pb-1">días para correrla</p>
        </div>
      )}
      <div
        className="absolute -bottom-10 -right-10 w-40 h-40 rounded-full opacity-20"
        style={{ background: "radial-gradient(closest-side, var(--accent), transparent)" }}
      />
    </div>
  );
}
