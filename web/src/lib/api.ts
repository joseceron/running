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

export type Dashboard = {
  profile: Profile;
  hrv: HRV;
  weekly: Weekly;
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
};

export function formatGoalTime(secs: number | null): string {
  if (!secs) return "—";
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  return `${h}h${m.toString().padStart(2, "0")}`;
}
