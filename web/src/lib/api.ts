/**
 * Cliente HTTP para la API de Liebre.
 *
 * Variables de entorno:
 *   NEXT_PUBLIC_LIEBRE_API   URL base de la API (default http://localhost:8080)
 */

const API_BASE =
  process.env.NEXT_PUBLIC_LIEBRE_API ?? "http://localhost:8080";

export type InjuryRecord = {
  name: string;
  recovered_at?: string;
  severity?: "mild" | "moderate" | "severe";
  notes?: string;
};

export type WeeklyPlanOverride = {
  /** Cada key es '0'..'6' (lun..dom). Value es [status, label]. */
  [day: string]: [string, string];
};

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
  city: string | null;
  altitude_msnm: number | null;
  injury_history: InjuryRecord[] | null;
  weekly_plan: WeeklyPlanOverride | null;
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
  /** null cuando Garmin no reporta running dynamics (caminata sin pod) */
  cadence: number | null;
  stride_m: number | null;
  gct_ms: number | null;
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
  avg_cadence: number | null;
  avg_stride_m: number | null;
  avg_gct_ms: number | null;
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

export type Sleep = {
  date: string;
  total_min: number | null;
  deep_min: number | null;
  rem_min: number | null;
  light_min: number | null;
  awake_min: number | null;
  sleep_score: number | null;
  time_in_bed_min: number | null;
};

export type Dashboard = {
  profile: Profile;
  hrv: HRV;
  weekly: Weekly;
  upcoming: UpcomingTrainings;
  days_to_goal: number | null;
  sleep: Sleep | null;
};

async function fetchJson<T>(path: string, idToken?: string | null): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    headers: idToken ? { Authorization: `Bearer ${idToken}` } : undefined,
  });
  if (!res.ok) {
    throw new Error(`Liebre API ${path} → ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

function withDate(path: string, date?: string): string {
  return date ? `${path}?date=${date}` : path;
}

export type FatBurnZone = {
  zone: number;
  label: string;
  pct_time: number;
  kcal_total: number;
  kcal_fat: number;
  kcal_cho: number;
  fat_pct: number;
};

export type Insights = {
  fat_burn: {
    activity_name: string;
    total_kcal: number;
    fat_kcal: number;
    cho_kcal: number;
    fat_grams: number;
    by_zone: FatBurnZone[];
    citation: string;
  } | null;
  cardiac_drift: {
    activity_name: string;
    first_half_hr: number;
    second_half_hr: number;
    drift_pct: number;
    evaluation: string;
    citation: string;
  } | null;
  heart_progress: {
    rhr_current: number;
    rhr_baseline: number;
    rhr_trend: "improving" | "stable" | "regressing";
    explanation: string;
    citation: string;
  } | null;
  polarization: {
    z1_z2_pct: number;
    z3_pct: number;
    z4_z5_pct: number;
    ideal_z1_z2_pct: number;
    ideal_z3_pct: number;
    ideal_z4_z5_pct: number;
    evaluation: "aligned" | "too_easy" | "too_hard" | "mixed";
    source_label: string;
    citation: string;
  } | null;
};

export type TodayAction = {
  status:
    | "rest"
    | "train"
    | "active_recovery"
    | "trained_already"
    | "past_executed"
    | "past_rest_planned"
    | "past_missed"
    | "future_planned";
  temporal: "today" | "past" | "future";
  headline: string;
  short_reason: string;
  reasons: string[];
  allowed: string[];
  next_session: string;
};

export type Nutrition = {
  hydration: {
    water_ml: number;
    electrolytes_needed: boolean;
    pre_session_ml: number;
    during_session_ml_per_hour: number;
    post_session_ml: number;
    notes: string[];
    real_world_examples: string[];
  };
  macros: {
    fase: string;
    kcal_estimadas: number;
    carbs_g: number;
    protein_g: number;
    fat_g: number;
    timing_notes: string[];
    carbs_examples: string;
    protein_examples: string;
    fat_examples: string;
  };
  environment: {
    altitude_msnm: number;
    sun_intensity: string;
    sunscreen_spf: number;
    sunscreen_reapply_min: number;
    extra_notes: string[];
  };
  expert_cta: string;
  citation: string;
};

export type Report = {
  date: string;
  today_action: TodayAction;
  activities_today: { hour: number; label: string; type: string }[];
  biomechanics: {
    cadence_spm: number | null;
    stride_m: number | null;
    gct_ms: number | null;
    cadence_avg_7: number | null;
    gct_avg_7: number | null;
    cadence_delta: number | null;
    gct_delta: number | null;
    is_walk: boolean;
  } | null;
  heart: {
    resting_hr: number | null;
    resting_hr_baseline: number;
    resting_hr_delta: number | null;
    hrv_last_night: number | null;
    hrv_baseline: number | null;
    hrv_state: string;
    vo2max: number | null;
  };
  load: {
    body_battery_max: number | null;
    body_battery_min: number | null;
    stress_avg: number | null;
    acwr: number | null;
    acwr_zone: string;
  };
  gates: {
    label: string;
    status: "green" | "yellow" | "red";
    detail: string;
  }[];
  interpretation: string[];
  insights: Insights | null;
  nutrition: Nutrition | null;
};

export const liebreApi = {
  dashboard: () => fetchJson<Dashboard>("/v1/users/me/dashboard"),
  profile: () => fetchJson<Profile>("/v1/users/me/profile"),
  hrv: () => fetchJson<HRV>("/v1/users/me/hrv"),
  weekly: () => fetchJson<Weekly>("/v1/users/me/weekly"),
  upcoming: () => fetchJson<UpcomingTrainings>("/v1/users/me/upcoming-trainings"),
  diagnosis: (date?: string) =>
    fetchJson<Diagnosis>(withDate("/v1/users/me/diagnosis", date)),
  cronologia: (date?: string) =>
    fetchJson<Cronologia>(withDate("/v1/users/me/cronologia", date)),
  activity: (id: string) =>
    fetchJson<ActivityDetail>(`/v1/users/me/activities/${id}`),
  report: (date?: string) =>
    fetchJson<Report>(withDate("/v1/users/me/report", date)),
};

/* ─── Auth-aware helpers para llamadas desde componentes cliente ───────
   El SSR usa fetchJson sin token (cae al DEMO_FALLBACK_USER_ID por ahora).
   Los flujos interactivos (onboarding, settings) deben usar estos helpers
   con el idToken del AuthContext para que el backend identifique al user
   correcto via Firebase.
*/

export type InitPayload = {
  name: string;
  age?: number;
  weight_kg?: number;
  height_cm?: number;
  city?: string;
  altitude_msnm?: number;
  goal_event?: "5K" | "10K" | "21K" | "42K" | "aprendiendo";
  goal_date?: string; // YYYY-MM-DD
  goal_time_secs?: number;
  injury_history?: InjuryRecord[];
  garmin_email?: string;
  garmin_password?: string;
};

export type ProfilePatchPayload = Partial<{
  name: string;
  age: number;
  weight_kg: number;
  height_cm: number;
  max_hr: number;
  resting_hr: number;
  city: string;
  altitude_msnm: number;
  goal_event: "5K" | "10K" | "21K" | "42K" | "aprendiendo";
  goal_date: string;
  goal_time_secs: number;
  injury_history: InjuryRecord[];
  weekly_plan: WeeklyPlanOverride;
}>;

async function _authedFetch<T>(
  path: string,
  init: RequestInit,
  idToken: string | null,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(idToken ? { Authorization: `Bearer ${idToken}` } : {}),
      ...(init.headers || {}),
    },
    cache: "no-store",
  });
  if (res.status === 204) return undefined as T;
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(`Liebre API ${path} → ${detail}`);
  }
  return (await res.json()) as T;
}

export const liebreAuthed = {
  initUser: (body: InitPayload, idToken: string | null) =>
    _authedFetch<Profile>(
      "/v1/users/me/init",
      { method: "POST", body: JSON.stringify(body) },
      idToken,
    ),
  patchProfile: (body: ProfilePatchPayload, idToken: string | null) =>
    _authedFetch<Profile>(
      "/v1/users/me/profile",
      { method: "PATCH", body: JSON.stringify(body) },
      idToken,
    ),
  putGarmin: (
    body: { email: string; password: string },
    idToken: string | null,
  ) =>
    _authedFetch<void>(
      "/v1/users/me/garmin",
      { method: "PUT", body: JSON.stringify(body) },
      idToken,
    ),
  deleteMe: (idToken: string | null) =>
    _authedFetch<void>(
      "/v1/users/me",
      { method: "DELETE", body: JSON.stringify({ confirm: "DELETE" }) },
      idToken,
    ),
  // Detecta si el usuario YA tiene perfil completado (200) o necesita onboarding (404).
  // Devuelve null si 404, lanza si otro error.
  getProfileOrNull: async (idToken: string | null): Promise<Profile | null> => {
    const res = await fetch(`${API_BASE}/v1/users/me/profile`, {
      headers: idToken ? { Authorization: `Bearer ${idToken}` } : {},
      cache: "no-store",
    });
    if (res.status === 404) return null;
    if (!res.ok) {
      throw new Error(`profile fetch → ${res.status}`);
    }
    return (await res.json()) as Profile;
  },
};

export function formatGoalTime(secs: number | null): string {
  if (!secs) return "—";
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  return `${h}h${m.toString().padStart(2, "0")}`;
}
