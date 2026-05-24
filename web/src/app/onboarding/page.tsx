/**
 * Onboarding wizard de 3 pasos para un usuario recién registrado.
 *
 * Step 1: datos físicos básicos (nombre, edad, peso, ciudad → altitud auto).
 * Step 2: meta (distancia, fecha, tiempo objetivo opcional).
 * Step 3: Garmin email + password (cifrados antes de persistir en BD).
 *
 * Al finalizar llama POST /v1/users/me/init y, si trae credenciales Garmin,
 * el backend dispara sync inicial como BackgroundTask (~15-30s). El user ve
 * un spinner durante esa espera y aterriza en /dashboard.
 */

"use client";

import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { useAuth } from "@/lib/auth-context";
import { CITIES, findCity, type CityOption } from "@/lib/cities";
import { liebreAuthed, type InitPayload } from "@/lib/api";

type GoalEvent = "5K" | "10K" | "21K" | "42K" | "aprendiendo";

type FormState = {
  // Step 1
  name: string;
  age: string;
  weight_kg: string;
  cityName: string;
  altitude_msnm: string; // string para input controlado; se castea al enviar
  // Step 2
  goal_event: GoalEvent | "";
  goal_date: string; // YYYY-MM-DD
  goal_time_hours: string;
  goal_time_minutes: string;
  // Step 3
  garmin_email: string;
  garmin_password: string;
};

const STEPS = ["Tu perfil", "Tu meta", "Conectar Garmin"];

export default function OnboardingPage() {
  const router = useRouter();
  const { user, loading: authLoading, idToken, isConfigured } = useAuth();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<FormState>({
    name: "",
    age: "",
    weight_kg: "",
    cityName: "",
    altitude_msnm: "",
    goal_event: "",
    goal_date: "",
    goal_time_hours: "",
    goal_time_minutes: "",
    garmin_email: "",
    garmin_password: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Si Firebase está configurado pero el user no está logueado, redirigir.
  useEffect(() => {
    if (isConfigured && !authLoading && !user) {
      router.replace("/login");
    }
  }, [isConfigured, authLoading, user, router]);

  // Si el user llega con nombre desde Google, pre-cargar.
  useEffect(() => {
    if (user?.displayName && !form.name) {
      setForm((f) => ({ ...f, name: user.displayName ?? "" }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.displayName]);

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  const handleCityChange = (cityName: string) => {
    const match = findCity(cityName);
    setForm((f) => ({
      ...f,
      cityName,
      altitude_msnm: match ? String(match.altitude_msnm) : f.altitude_msnm,
    }));
  };

  const canNextStep1 =
    form.name.trim().length > 0 &&
    parseInt(form.age || "0", 10) >= 10 &&
    parseFloat(form.weight_kg || "0") > 0;

  const canNextStep2 = form.goal_event !== "";

  const canSubmit = useMemo(() => {
    if (!canNextStep1 || !canNextStep2) return false;
    // Step 3 es opcional — el user puede saltar Garmin
    if (form.garmin_email || form.garmin_password) {
      return (
        form.garmin_email.includes("@") && form.garmin_password.length >= 1
      );
    }
    return true;
  }, [canNextStep1, canNextStep2, form.garmin_email, form.garmin_password]);

  const submit = async () => {
    setSubmitting(true);
    setError(null);
    const goal_time_secs =
      form.goal_time_hours || form.goal_time_minutes
        ? parseInt(form.goal_time_hours || "0", 10) * 3600 +
          parseInt(form.goal_time_minutes || "0", 10) * 60
        : undefined;
    const payload: InitPayload = {
      name: form.name.trim(),
      age: parseInt(form.age, 10),
      weight_kg: parseFloat(form.weight_kg),
      city: form.cityName || undefined,
      altitude_msnm: form.altitude_msnm
        ? parseInt(form.altitude_msnm, 10)
        : undefined,
      goal_event: form.goal_event || undefined,
      goal_date: form.goal_date || undefined,
      goal_time_secs,
    };
    if (form.garmin_email && form.garmin_password) {
      payload.garmin_email = form.garmin_email.trim();
      payload.garmin_password = form.garmin_password;
    }
    try {
      await liebreAuthed.initUser(payload, idToken);
      router.replace("/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col bg-bg-page text-ink-primary">
      <nav className="px-4 md:px-8 py-4 border-b border-rule/60">
        <span className="wordmark text-2xl">
          liebre<span className="dot">.</span>
        </span>
      </nav>

      <section className="flex-1 flex items-start justify-center px-4 py-10 md:py-16">
        <div className="w-full max-w-xl">
          <Stepper current={step} />

          <div className="card mt-6">
            {step === 0 && (
              <StepOne
                form={form}
                update={update}
                handleCityChange={handleCityChange}
              />
            )}
            {step === 1 && <StepTwo form={form} update={update} />}
            {step === 2 && (
              <StepThree form={form} update={update} submitting={submitting} />
            )}

            {error && (
              <div
                className="mt-4 p-3 rounded-md text-xs"
                style={{
                  background:
                    "color-mix(in srgb, var(--semantic-danger) 12%, transparent)",
                  color: "var(--semantic-danger)",
                }}
              >
                {error}
              </div>
            )}

            <div className="mt-6 flex items-center justify-between gap-3">
              <button
                type="button"
                onClick={() => setStep((s) => Math.max(0, s - 1))}
                disabled={step === 0 || submitting}
                className="px-3 py-2 text-sm text-ink-secondary hover:text-ink-primary disabled:opacity-30 transition"
              >
                ← Atrás
              </button>

              {step < 2 ? (
                <button
                  type="button"
                  onClick={() => setStep((s) => s + 1)}
                  disabled={
                    (step === 0 && !canNextStep1) ||
                    (step === 1 && !canNextStep2)
                  }
                  className="px-4 py-2.5 rounded-md bg-accent-brand text-white text-sm font-semibold hover:opacity-90 transition disabled:opacity-50"
                >
                  Siguiente →
                </button>
              ) : (
                <button
                  type="button"
                  onClick={submit}
                  disabled={submitting || !canSubmit}
                  className="px-4 py-2.5 rounded-md bg-accent-brand text-white text-sm font-semibold hover:opacity-90 transition disabled:opacity-50"
                >
                  {submitting ? "Conectando y sincronizando…" : "Empezar"}
                </button>
              )}
            </div>
          </div>

          <p className="text-[11px] text-ink-tertiary mt-4 text-center leading-relaxed">
            Tus datos se guardan cifrados. Solo tú accedes a ellos.
            <br />
            Puedes editarlos en cualquier momento en Perfil.
          </p>
        </div>
      </section>
    </main>
  );
}

/* ─── UI auxiliares ─── */

function Stepper({ current }: { current: number }) {
  return (
    <ol className="flex items-center gap-2">
      {STEPS.map((label, i) => {
        const done = i < current;
        const active = i === current;
        return (
          <li key={label} className="flex items-center gap-2 flex-1">
            <span
              className={`flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold transition-colors`}
              style={{
                background: done || active ? "var(--accent-brand)" : "transparent",
                color: done || active ? "#fff" : "var(--text-secondary)",
                border:
                  done || active ? "none" : "1px solid var(--ink-tertiary)",
              }}
            >
              {done ? "✓" : i + 1}
            </span>
            <span
              className={`text-xs ${
                active ? "text-ink-primary font-semibold" : "text-ink-secondary"
              }`}
            >
              {label}
            </span>
            {i < STEPS.length - 1 && (
              <span
                className="flex-1 h-px"
                style={{
                  background:
                    i < current
                      ? "var(--accent-brand)"
                      : "var(--ink-tertiary)",
                }}
              />
            )}
          </li>
        );
      })}
    </ol>
  );
}

function StepOne({
  form,
  update,
  handleCityChange,
}: {
  form: FormState;
  update: <K extends keyof FormState>(k: K, v: FormState[K]) => void;
  handleCityChange: (s: string) => void;
}) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold mb-1">Cuéntanos quién eres</h2>
        <p className="text-sm text-ink-secondary">
          Datos básicos para personalizar tu plan. Todo se puede editar después.
        </p>
      </div>
      <Field label="Nombre">
        <input
          type="text"
          value={form.name}
          onChange={(e) => update("name", e.target.value)}
          placeholder="Cómo te llamas"
          className="w-full px-3 py-2.5 rounded-md border border-rule text-sm" style={{ background: "var(--bg-card)" }}
          autoComplete="name"
        />
      </Field>
      <div className="grid grid-cols-2 gap-3">
        <Field label="Edad">
          <input
            type="number"
            min={10}
            max={99}
            value={form.age}
            onChange={(e) => update("age", e.target.value)}
            placeholder="36"
            className="w-full px-3 py-2.5 rounded-md border border-rule text-sm tnum" style={{ background: "var(--bg-card)" }}
          />
        </Field>
        <Field label="Peso (kg)">
          <input
            type="number"
            min={20}
            max={250}
            step="0.1"
            value={form.weight_kg}
            onChange={(e) => update("weight_kg", e.target.value)}
            placeholder="68"
            className="w-full px-3 py-2.5 rounded-md border border-rule text-sm tnum" style={{ background: "var(--bg-card)" }}
          />
        </Field>
      </div>
      <Field label="Ciudad de entrenamiento">
        <input
          list="city-options"
          value={form.cityName}
          onChange={(e) => handleCityChange(e.target.value)}
          placeholder="Bogotá, Medellín…"
          className="w-full px-3 py-2.5 rounded-md border border-rule text-sm" style={{ background: "var(--bg-card)" }}
          autoComplete="off"
        />
        <datalist id="city-options">
          {CITIES.map((c) => (
            <option key={c.name} value={c.name}>
              {c.label}
            </option>
          ))}
        </datalist>
        <p className="text-[11px] text-ink-tertiary mt-1">
          {form.altitude_msnm
            ? `Altitud: ${form.altitude_msnm} msnm`
            : "Si tu ciudad no está, ingresa la altitud manualmente abajo."}
        </p>
      </Field>
      <Field label="Altitud (msnm) — opcional">
        <input
          type="number"
          min={0}
          max={6000}
          value={form.altitude_msnm}
          onChange={(e) => update("altitude_msnm", e.target.value)}
          placeholder="0 = nivel del mar"
          className="w-full px-3 py-2.5 rounded-md border border-rule text-sm tnum" style={{ background: "var(--bg-card)" }}
        />
      </Field>
    </div>
  );
}

function StepTwo({
  form,
  update,
}: {
  form: FormState;
  update: <K extends keyof FormState>(k: K, v: FormState[K]) => void;
}) {
  const eventOptions: { v: GoalEvent; label: string; sub: string }[] = [
    { v: "5K", label: "5K", sub: "Velocidad / iniciación" },
    { v: "10K", label: "10K", sub: "Resistencia base" },
    { v: "21K", label: "21K", sub: "Media maratón" },
    { v: "42K", label: "42K", sub: "Maratón" },
    { v: "aprendiendo", label: "Sin meta aún", sub: "Voy explorando" },
  ];
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold mb-1">¿Qué quieres lograr?</h2>
        <p className="text-sm text-ink-secondary">
          Esto define el ritmo y las zonas de tu plan.
        </p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {eventOptions.map((opt) => {
          const active = form.goal_event === opt.v;
          return (
            <button
              key={opt.v}
              type="button"
              onClick={() => update("goal_event", opt.v)}
              className="text-left p-3 rounded-md border transition-colors"
              style={{
                borderColor: active
                  ? "var(--accent-brand)"
                  : "var(--rule)",
                background: active
                  ? "color-mix(in srgb, var(--accent-brand) 8%, var(--bg-card))"
                  : "var(--bg-card)",
              }}
            >
              <div className="font-semibold">{opt.label}</div>
              <div className="text-xs text-ink-secondary mt-0.5">{opt.sub}</div>
            </button>
          );
        })}
      </div>

      {form.goal_event && form.goal_event !== "aprendiendo" && (
        <>
          <Field label="Fecha objetivo (opcional)">
            <input
              type="date"
              value={form.goal_date}
              onChange={(e) => update("goal_date", e.target.value)}
              className="w-full px-3 py-2.5 rounded-md border border-rule text-sm" style={{ background: "var(--bg-card)" }}
            />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Tiempo objetivo · horas">
              <input
                type="number"
                min={0}
                max={10}
                value={form.goal_time_hours}
                onChange={(e) => update("goal_time_hours", e.target.value)}
                placeholder="1"
                className="w-full px-3 py-2.5 rounded-md border border-rule text-sm tnum" style={{ background: "var(--bg-card)" }}
              />
            </Field>
            <Field label="Tiempo objetivo · minutos">
              <input
                type="number"
                min={0}
                max={59}
                value={form.goal_time_minutes}
                onChange={(e) => update("goal_time_minutes", e.target.value)}
                placeholder="50"
                className="w-full px-3 py-2.5 rounded-md border border-rule text-sm tnum" style={{ background: "var(--bg-card)" }}
              />
            </Field>
          </div>
        </>
      )}
    </div>
  );
}

function StepThree({
  form,
  update,
  submitting,
}: {
  form: FormState;
  update: <K extends keyof FormState>(k: K, v: FormState[K]) => void;
  submitting: boolean;
}) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold mb-1">Conecta tu Garmin</h2>
        <p className="text-sm text-ink-secondary">
          Sin Garmin Liebre no puede leer tu HRV, biomecánica ni actividades.
          Tu password se{" "}
          <span className="font-semibold">cifra antes de guardarla</span> — solo
          la usamos para leer tus datos. Puedes saltarte este paso y
          conectarlo después.
        </p>
      </div>
      <Field label="Email de Garmin Connect">
        <input
          type="email"
          value={form.garmin_email}
          onChange={(e) => update("garmin_email", e.target.value)}
          placeholder="tu@email.com"
          className="w-full px-3 py-2.5 rounded-md border border-rule text-sm" style={{ background: "var(--bg-card)" }}
          autoComplete="email"
          inputMode="email"
        />
      </Field>
      <Field label="Password de Garmin Connect">
        <input
          type="password"
          value={form.garmin_password}
          onChange={(e) => update("garmin_password", e.target.value)}
          placeholder="••••••••"
          className="w-full px-3 py-2.5 rounded-md border border-rule text-sm" style={{ background: "var(--bg-card)" }}
          autoComplete="current-password"
        />
      </Field>
      {submitting && (
        <p
          className="text-xs"
          style={{ color: "var(--accent-brand)" }}
        >
          Validando con Garmin y descargando tus últimas 14 noches de HRV…
        </p>
      )}
    </div>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="label-uppercase mb-1.5 block">{label}</span>
      {children}
    </label>
  );
}
