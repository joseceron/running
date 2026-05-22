/**
 * Cliente HTTP para la API de Liebre.
 *
 * Variables de entorno:
 *   NEXT_PUBLIC_LIEBRE_API   URL base de la API (default http://localhost:8080)
 */

const API_BASE =
  process.env.NEXT_PUBLIC_LIEBRE_API ?? "http://localhost:8080";

export type Profile = {
  user_id: string;
  name: string;
  age: number | null;
  height_cm: number | null;
  weight_kg: number | null;
  max_hr: number | null;
  resting_hr: number | null;
  goal_event: "5K" | "10K" | "21K" | "42K" | "aprendiendo" | null;
  goal_date: string | null;
  goal_time_secs: number | null;
  system_start: string;
};

export type HRVNight = {
  date: string;
  hrv_rmssd: number;
};

export type HRVStatus =
  | "optimal"
  | "reduced"
  | "suppressed"
  | "building_baseline";

export type HRV = {
  nights: HRVNight[];
  baseline_ms: number | null;
  days_recorded: number;
  days_required: number;
  latest_value: number | null;
  latest_delta_pct: number | null;
  status: HRVStatus;
};

export type WeeklyEntry = {
  week_start: string;
  plan_km: number | null;
  executed_km: number | null;
  avg_hrv: number | null;
  avg_body_battery: number | null;
  acwr: number | null;
  agent_notes: string | null;
};

export type Weekly = {
  weeks: WeeklyEntry[];
};

export type ActivitySample = {
  t_secs: number;
  distance_km: number;
  pace_secs_per_km: number | null;
  hr: number | null;
  cadence: number | null;
  elevation_m: number | null;
  power_w: number | null;
};

export type ActivitySplit = {
  km: number;
  time_secs: number;
  pace: string;
  avg_hr: number;
  max_hr: number;
  cadence: number;
  stride_m: number;
  gct_ms: number;
  elevation_gain_m: number;
};

export type ActivityDetail = {
  activity_id: string;
  name: string;
  started_at: string;
  type: "run" | "walk" | "bike" | "swim";
  distance_km: number;
  duration_secs: number;
  avg_pace: string;
  avg_hr: number;
  max_hr: number;
  elevation_gain_m: number;
  calories: number;
  avg_cadence: number;
  avg_stride_m: number;
  avg_gct_ms: number;
  training_effect_aerobic: number;
  zone_distribution_pct: number[];
  samples: ActivitySample[];
  splits: ActivitySplit[];
};

export type CronologiaPoint = {
  hour: number;
  body_battery: number | null;
  stress: number | null;
  is_sleeping: boolean;
  is_active: boolean;
};

export type CronologiaActivity = {
  hour: number;
  label: string;
  type: string;
};

export type Cronologia = {
  points: CronologiaPoint[];
  activities: CronologiaActivity[];
  summary: {
    body_battery_start: number;
    body_battery_end: number;
    body_battery_max: number;
    body_battery_min: number;
    stress_avg: number;
    stress_max: number;
    sleep_duration_min: number;
  };
};

export type Diagnosis = {
  narrative: string;
  action: string;
  citation: string;
  alert_level: "info" | "warn" | "danger";
  generated_at: string;
};

export type UpcomingTraining = {
  day_label: string;
  relative_days: number;
  type:
    | "Rodaje Z2"
    | "Series Z4"
    | "Tempo Z3"
    | "Rodaje largo Z2"
    | "Fuerza"
    | "Movilidad"
    | "Descanso";
  duration_min: number;
  zone_target: "Z1" | "Z2" | "Z3" | "Z4" | "Z5" | "—";
  distance_km: number | null;
  rationale: string;
};

export type UpcomingTrainings = {
  sessions: UpcomingTraining[];
};

export type Dashboard = {
  profile: Profile;
  hrv: HRV;
  weekly: Weekly;
  upcoming: UpcomingTrainings;
  days_to_goal: number | null;
};

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Liebre API ${path} → ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const liebreApi = {
  dashboard: () => fetchJson<Dashboard>("/v1/users/me/dashboard"),
  profile: () => fetchJson<Profile>("/v1/users/me/profile"),
  hrv: () => fetchJson<HRV>("/v1/users/me/hrv"),
  weekly: () => fetchJson<Weekly>("/v1/users/me/weekly"),
  upcoming: () => fetchJson<UpcomingTrainings>("/v1/users/me/upcoming-trainings"),
  diagnosis: () => fetchJson<Diagnosis>("/v1/users/me/diagnosis"),
  cronologia: () => fetchJson<Cronologia>("/v1/users/me/cronologia"),
  activity: (id: string) =>
    fetchJson<ActivityDetail>(`/v1/users/me/activities/${id}`),
};

export function formatGoalTime(secs: number | null): string {
  if (!secs) return "—";
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  return `${h}h${m.toString().padStart(2, "0")}`;
}
