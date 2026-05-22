/**
 * ProfileCard — alineado con mockup.
 * Avatar circular con iniciales + nombre + sub-label, luego stats en
 * filas flex space-between (sin border entre filas, espaciado por gap).
 */

import type { Profile } from "@/lib/api";

function initials(name: string): string {
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}

export function ProfileCard({ profile }: { profile: Profile }) {
  const stats: Array<[string, string]> = [
    ["Edad", profile.age ? `${profile.age} años` : "—"],
    ["Peso", profile.weight_kg ? `${profile.weight_kg} kg` : "—"],
    ["Altura", profile.height_cm ? `${profile.height_cm} cm` : "—"],
    ["FC máx", profile.max_hr ? `${profile.max_hr} lpm` : "—"],
    ["FC reposo", profile.resting_hr ? `${profile.resting_hr} lpm` : "—"],
  ];
  return (
    <div className="card">
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
        {stats.map(([label, value]) => (
          <div
            key={label}
            className="flex items-baseline justify-between"
          >
            <dt className="text-[13px] text-ink-tertiary">{label}</dt>
            <dd className="tnum text-[13px] font-semibold text-ink-primary">
              {value}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
