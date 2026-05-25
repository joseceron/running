/**
 * Cliente HTTP autenticado para Server Components.
 *
 * Lee la cookie `liebre_id_token` (setada por AuthContext en el browser tras
 * cada onAuthStateChanged + refresh cada 50 min) y la envía como Bearer al
 * backend. Sin token, la request va anónima — el backend devolverá 401 si el
 * endpoint requiere auth (recuerda: ya no hay DEMO_FALLBACK_USER_ID en prod).
 *
 * IMPORTANTE: este archivo importa `next/headers` que SOLO existe en server.
 * No lo importes desde Client Components — usa `liebreAuthed` de api.ts.
 */

import { cookies } from "next/headers";

import type {
  ActivityDetail,
  Cronologia,
  Dashboard,
  Diagnosis,
  HRV,
  Profile,
  Report,
  UpcomingTrainings,
  Weekly,
} from "./api";

const API_BASE =
  process.env.NEXT_PUBLIC_LIEBRE_API ?? "http://localhost:8080";

const TOKEN_COOKIE = "liebre_id_token";

async function _readToken(): Promise<string | null> {
  // En Next 16 `cookies()` es async.
  const store = await cookies();
  const c = store.get(TOKEN_COOKIE);
  return c?.value ?? null;
}

async function _fetch<T>(path: string): Promise<T> {
  const token = await _readToken();
  const res = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  if (!res.ok) {
    throw new Error(`Liebre API ${path} → ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

function _withDate(path: string, date?: string): string {
  return date ? `${path}?date=${date}` : path;
}

export const liebreApiServer = {
  dashboard: () => _fetch<Dashboard>("/v1/users/me/dashboard"),
  profile: () => _fetch<Profile>("/v1/users/me/profile"),
  hrv: () => _fetch<HRV>("/v1/users/me/hrv"),
  weekly: () => _fetch<Weekly>("/v1/users/me/weekly"),
  upcoming: () => _fetch<UpcomingTrainings>("/v1/users/me/upcoming-trainings"),
  diagnosis: (date?: string) =>
    _fetch<Diagnosis>(_withDate("/v1/users/me/diagnosis", date)),
  cronologia: (date?: string) =>
    _fetch<Cronologia>(_withDate("/v1/users/me/cronologia", date)),
  activity: (id: string) =>
    _fetch<ActivityDetail>(`/v1/users/me/activities/${id}`),
  report: (date?: string) =>
    _fetch<Report>(_withDate("/v1/users/me/report", date)),
};

/** Helper para Server Components: detecta si el usuario tiene cookie de
 *  auth. Útil para redirigir a /login si no la hay antes de hacer fetches. */
export async function hasAuthCookie(): Promise<boolean> {
  return (await _readToken()) !== null;
}
