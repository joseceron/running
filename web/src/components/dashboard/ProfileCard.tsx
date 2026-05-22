import type { Profile } from "@/lib/api";

export function ProfileCard({ profile }: { profile: Profile }) {
  const stats: Array<[string, string]> = [
    ["Edad", profile.age ? `${profile.age} años` : "—"],
    ["Peso", profile.weight_kg ? `${profile.weight_kg} kg` : "—"],
    ["Altura", profile.height_cm ? `${profile.height_cm} cm` : "—"],
    ["FC máx", profile.max_hr ? `${profile.max_hr} lpm` : "—"],
    ["FC reposo", profile.resting_hr ? `${profile.resting_hr} lpm` : "—"],
  ];
  return (
    <div className="rounded-2xl border border-rule bg-paper-warm/40 p-6">
      <p className="text-xs uppercase tracking-widest text-muted mb-4">
        Tu perfil
      </p>
      <p className="wordmark text-2xl mb-5">{profile.name}</p>
      <dl className="grid grid-cols-2 gap-y-3 gap-x-6 text-sm">
        {stats.map(([label, value]) => (
          <div key={label} className="flex items-baseline justify-between">
            <dt className="text-muted">{label}</dt>
            <dd className="tnum font-medium">{value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
