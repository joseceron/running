/**
 * ProfileCard — perfil del corredor con avatar circular + sub-label + stats.
 * FC máx, FC reposo y lpm tienen tooltip de glosario.
 */

import type { Profile } from "@/lib/api";
import { Term } from "./Term";
import type { GlossaryKey } from "@/lib/glossary";

function initials(name: string): string {
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}

type StatRow = {
  label: React.ReactNode;
  value: string;
  unit?: GlossaryKey;
};

export function ProfileCard({ profile }: { profile: Profile }) {
  const stats: StatRow[] = [
    { label: "Edad", value: profile.age ? `${profile.age} años` : "—" },
    { label: "Peso", value: profile.weight_kg ? `${profile.weight_kg} kg` : "—" },
    { label: "Altura", value: profile.height_cm ? `${profile.height_cm} cm` : "—" },
    {
      label: <Term k="fc_max">FC máx</Term>,
      value: profile.max_hr ? `${profile.max_hr}` : "—",
      unit: profile.max_hr ? "lpm" : undefined,
    },
    {
      label: <Term k="fc_reposo">FC reposo</Term>,
      value: profile.resting_hr ? `${profile.resting_hr}` : "—",
      unit: profile.resting_hr ? "lpm" : undefined,
    },
  ];
  return (
    <div className="card overflow-visible">
      <span className="label-uppercase">Tu Perfil</span>

      <div className="flex items-center gap-3 mt-3.5 mb-4">
        <div className="w-11 h-11 rounded-full bg-accent-brand flex items-center justify-center text-white font-bold text-[15px] shrink-0">
          {initials(profile.name)}
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-ink-primary truncate">
            {profile.name}
          </p>
          <p className="text-[11px] text-ink-tertiary mt-0.5">
            Corredor · Plan {profile.goal_event ?? "—"}
          </p>
        </div>
      </div>

      <dl className="flex flex-col gap-2.5">
        {stats.map((s, i) => (
          <div key={i} className="flex items-baseline justify-between">
            <dt className="text-[13px] text-ink-tertiary">{s.label}</dt>
            <dd className="tnum text-[13px] font-semibold text-ink-primary">
              {s.value}
              {s.unit && (
                <span className="ml-1 font-normal text-ink-tertiary">
                  <Term k={s.unit}>{s.unit}</Term>
                </span>
              )}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
