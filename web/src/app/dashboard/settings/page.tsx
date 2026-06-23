/**
 * Settings — edición de perfil + reconexión de Garmin + borrado de cuenta.
 *
 * Client Component porque hace requests autenticadas con el idToken del
 * AuthContext. Carga el perfil al montar, permite edición por sección y
 * persiste con PATCH /profile o PUT /garmin.
 */

"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { liebreAuthed, type Profile, type ProfilePatchPayload } from "@/lib/api";
import { CITIES, findCity } from "@/lib/cities";
import { useAuth } from "@/lib/auth-context";
import { Sidebar } from "@/components/dashboard/Sidebar";

type Status = { kind: "ok" | "error"; msg: string } | null;

export default function SettingsPage() {
  const router = useRouter();
  const { idToken, loading: authLoading, isConfigured } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<Status>(null);

  useEffect(() => {
    if (authLoading) return;
    liebreAuthed
      .getProfileOrNull(idToken)
      .then((p) => setProfile(p))
      .catch((e) =>
        setStatus({ kind: "error", msg: e instanceof Error ? e.message : String(e) }),
      )
      .finally(() => setLoading(false));
  }, [authLoading, idToken]);

  const showToast = (s: Status) => {
    setStatus(s);
    if (s?.kind === "ok") setTimeout(() => setStatus(null), 4000);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-bg-page">
        <Sidebar userName="" />
        <main className="md:ml-[var(--sidebar-width)] p-8">
          <p className="text-sm text-ink-secondary">Cargando perfil…</p>
        </main>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-bg-page">
        <Sidebar userName="" />
        <main className="md:ml-[var(--sidebar-width)] p-8">
          <p className="text-sm text-ink-secondary">
            Tu perfil aún no está creado.{" "}
            <a className="underline text-accent-brand" href="/onboarding">
              Completar onboarding
            </a>
          </p>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-page">
      <Sidebar userName={profile.name} />

      {/* Toast fijo abajo — visible sin hacer scroll */}
      {status && (
        <div
          className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-5 py-3 rounded-xl shadow-lg text-sm font-medium max-w-sm w-[calc(100%-2rem)] text-center pointer-events-none"
          style={{
            background: status.kind === "ok" ? "var(--hrv-balanced)" : "var(--semantic-danger)",
            color: "white",
          }}
        >
          {status.msg}
        </div>
      )}

      <main className="md:ml-[var(--sidebar-width)] pb-24 md:pb-0">
        <div className="max-w-3xl mx-auto px-4 md:px-8 py-8 md:py-12">
          <header className="mb-6">
            <h1 className="text-2xl font-semibold">Ajustes</h1>
            <p className="text-sm text-ink-secondary">
              Cambia tu perfil, reconecta Garmin o borra tu cuenta.
            </p>
          </header>

          <ProfileSection
            profile={profile}
            idToken={idToken}
            onSaved={(p) => { setProfile(p); showToast({ kind: "ok", msg: "Perfil actualizado." }); }}
            onError={(m) => showToast({ kind: "error", msg: m })}
          />

          <BodyCompositionSection
            idToken={idToken}
            onSaved={() => showToast({ kind: "ok", msg: "Medición guardada. Visible en la curva de adaptación." })}
            onError={(m) => showToast({ kind: "error", msg: m })}
          />

          <GoalSection
            profile={profile}
            idToken={idToken}
            onSaved={(p) => { setProfile(p); showToast({ kind: "ok", msg: "Meta actualizada." }); }}
            onError={(m) => showToast({ kind: "error", msg: m })}
          />

          <GarminSection
            idToken={idToken}
            onSaved={() => showToast({ kind: "ok", msg: "Garmin reconectado." })}
            onError={(m) => showToast({ kind: "error", msg: m })}
          />

          <DangerSection
            idToken={idToken}
            onDeleted={() => router.replace("/login")}
            onError={(m) => showToast({ kind: "error", msg: m })}
          />
          {!isConfigured && (
            <p className="text-[11px] text-ink-tertiary mt-6">
              Modo demo: los cambios no persisten sin Firebase configurado.
            </p>
          )}
        </div>
      </main>
    </div>
  );
}

/* ─── Secciones ─── */

function Section({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="card mb-5">
      <h2 className="text-lg font-semibold mb-1">{title}</h2>
      {description && (
        <p className="text-xs text-ink-secondary mb-4">{description}</p>
      )}
      <div className="space-y-3">{children}</div>
    </section>
  );
}

function ProfileSection({
  profile,
  idToken,
  onSaved,
  onError,
}: {
  profile: Profile;
  idToken: string | null;
  onSaved: (p: Profile) => void;
  onError: (m: string) => void;
}) {
  const [name, setName] = useState(profile.name);
  const [age, setAge] = useState(profile.age?.toString() ?? "");
  const [weight, setWeight] = useState(profile.weight_kg?.toString() ?? "");
  const [height, setHeight] = useState(profile.height_cm?.toString() ?? "");
  const [restingHr, setRestingHr] = useState(profile.resting_hr?.toString() ?? "");
  const [city, setCity] = useState(profile.city ?? "");
  const [alt, setAlt] = useState(profile.altitude_msnm?.toString() ?? "");
  const [busy, setBusy] = useState(false);

  const handleCity = (n: string) => {
    const match = findCity(n);
    setCity(n);
    if (match) setAlt(String(match.altitude_msnm));
  };

  const save = async () => {
    setBusy(true);
    try {
      const patch: ProfilePatchPayload = {
        name: name.trim() || profile.name,
        age: age ? parseInt(age, 10) : undefined,
        weight_kg: weight ? parseFloat(weight) : undefined,
        height_cm: height ? parseFloat(height) : undefined,
        resting_hr: restingHr ? parseInt(restingHr, 10) : undefined,
        city: city.trim() || undefined,
        altitude_msnm: alt ? parseInt(alt, 10) : undefined,
      };
      const updated = await liebreAuthed.patchProfile(patch, idToken);
      onSaved(updated);
    } catch (e) {
      onError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Section title="Perfil físico" description="Datos para personalizar tu plan y nutrición.">
      <Row label="Nombre">
        <Input value={name} onChange={setName} placeholder="Nombre" />
      </Row>
      <div className="grid grid-cols-2 gap-3">
        <Row label="Edad">
          <Input value={age} onChange={setAge} placeholder="36" type="number" />
        </Row>
        <Row label="Peso (kg)">
          <Input
            value={weight}
            onChange={setWeight}
            placeholder="68"
            type="number"
          />
        </Row>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <Row label="Estatura (cm)">
          <Input
            value={height}
            onChange={setHeight}
            placeholder="170"
            type="number"
          />
        </Row>
        <Row label="FC reposo">
          <Input
            value={restingHr}
            onChange={setRestingHr}
            placeholder="51"
            type="number"
          />
        </Row>
      </div>
      <Row label="Ciudad">
        <input
          list="settings-city-options"
          value={city}
          onChange={(e) => handleCity(e.target.value)}
          placeholder="Bogotá, Medellín…"
          className="w-full px-3 py-2.5 rounded-md border border-rule text-sm"
          style={{ background: "var(--bg-card)" }}
        />
        <datalist id="settings-city-options">
          {CITIES.map((c) => (
            <option key={c.name} value={c.name}>
              {c.label}
            </option>
          ))}
        </datalist>
      </Row>
      <Row label="Altitud (msnm)">
        <Input value={alt} onChange={setAlt} placeholder="0" type="number" />
      </Row>
      <SaveButton busy={busy} onClick={save} />
    </Section>
  );
}

function GoalSection({
  profile,
  idToken,
  onSaved,
  onError,
}: {
  profile: Profile;
  idToken: string | null;
  onSaved: (p: Profile) => void;
  onError: (m: string) => void;
}) {
  const [goalEvent, setGoalEvent] = useState<NonNullable<Profile["goal_event"]> | "">(
    profile.goal_event ?? "",
  );
  const [goalDate, setGoalDate] = useState(profile.goal_date ?? "");
  const [hours, setHours] = useState(
    profile.goal_time_secs ? Math.floor(profile.goal_time_secs / 3600).toString() : "",
  );
  const [minutes, setMinutes] = useState(
    profile.goal_time_secs
      ? Math.floor((profile.goal_time_secs % 3600) / 60).toString()
      : "",
  );
  const [busy, setBusy] = useState(false);

  const save = async () => {
    setBusy(true);
    try {
      const secs =
        hours || minutes
          ? parseInt(hours || "0", 10) * 3600 +
            parseInt(minutes || "0", 10) * 60
          : undefined;
      const updated = await liebreAuthed.patchProfile(
        {
          goal_event: goalEvent || undefined,
          goal_date: goalDate || undefined,
          goal_time_secs: secs,
        },
        idToken,
      );
      onSaved(updated);
    } catch (e) {
      onError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Section title="Meta" description="Tu próxima carrera o evento.">
      <Row label="Distancia">
        <select
          value={goalEvent}
          onChange={(e) =>
            setGoalEvent(e.target.value as NonNullable<Profile["goal_event"]> | "")
          }
          className="w-full px-3 py-2.5 rounded-md border border-rule text-sm"
          style={{ background: "var(--bg-card)" }}
        >
          <option value="">Sin meta</option>
          <option value="5K">5K</option>
          <option value="10K">10K</option>
          <option value="21K">21K · media maratón</option>
          <option value="42K">42K · maratón</option>
          <option value="aprendiendo">Voy explorando</option>
        </select>
      </Row>
      <Row label="Fecha objetivo">
        <Input value={goalDate} onChange={setGoalDate} type="date" />
      </Row>
      <div className="grid grid-cols-2 gap-3">
        <Row label="Tiempo · horas">
          <Input value={hours} onChange={setHours} placeholder="1" type="number" />
        </Row>
        <Row label="Tiempo · minutos">
          <Input value={minutes} onChange={setMinutes} placeholder="50" type="number" />
        </Row>
      </div>
      <SaveButton busy={busy} onClick={save} />
    </Section>
  );
}

function BodyCompositionSection({
  idToken,
  onSaved,
  onError,
}: {
  idToken: string | null;
  onSaved: () => void;
  onError: (m: string) => void;
}) {
  const today = new Date().toISOString().slice(0, 10);
  const [date, setDate] = useState(today);
  const [fields, setFields] = useState({
    weight_kg: "",
    bmi: "",
    body_fat_pct: "",
    subcutaneous_fat_pct: "",
    visceral_fat: "",
    muscle_mass_kg: "",
    skeletal_muscle_pct: "",
    fat_free_weight_kg: "",
    body_water_pct: "",
    bone_mass_kg: "",
    bmr_kcal: "",
    metabolic_age: "",
    protein_pct: "",
  });
  const [busy, setBusy] = useState(false);

  const set = (k: keyof typeof fields, v: string) =>
    setFields((prev) => ({ ...prev, [k]: v }));
  const n = (s: string) => { const v = parseFloat(s); return isNaN(v) ? null : v; };

  const save = async () => {
    setBusy(true);
    try {
      await liebreAuthed.postBodyComposition(
        {
          measured_at: date,
          weight_kg: n(fields.weight_kg),
          bmi: n(fields.bmi),
          body_fat_pct: n(fields.body_fat_pct),
          subcutaneous_fat_pct: n(fields.subcutaneous_fat_pct),
          visceral_fat: n(fields.visceral_fat),
          muscle_mass_kg: n(fields.muscle_mass_kg),
          skeletal_muscle_pct: n(fields.skeletal_muscle_pct),
          fat_free_weight_kg: n(fields.fat_free_weight_kg),
          body_water_pct: n(fields.body_water_pct),
          bone_mass_kg: n(fields.bone_mass_kg),
          bmr_kcal: n(fields.bmr_kcal) != null ? Math.round(n(fields.bmr_kcal)!) : null,
          metabolic_age: n(fields.metabolic_age) != null ? Math.round(n(fields.metabolic_age)!) : null,
          protein_pct: n(fields.protein_pct),
          notes: null,
        },
        idToken,
      );
      onSaved();
    } catch (e) {
      onError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  const FIELDS: { k: keyof typeof fields; label: string; placeholder: string }[] = [
    { k: "weight_kg",           label: "Peso (kg)",               placeholder: "68.90" },
    { k: "bmi",                 label: "IMC",                     placeholder: "25.3" },
    { k: "body_fat_pct",        label: "Grasa corporal (%)",      placeholder: "19.2" },
    { k: "subcutaneous_fat_pct",label: "Grasa subcutánea (%)",    placeholder: "16.8" },
    { k: "visceral_fat",        label: "Grasa visceral",          placeholder: "8" },
    { k: "muscle_mass_kg",      label: "Masa muscular (kg)",      placeholder: "52.81" },
    { k: "skeletal_muscle_pct", label: "Músculo esquelético (%)", placeholder: "52.1" },
    { k: "fat_free_weight_kg",  label: "Peso libre de grasa (kg)",placeholder: "55.64" },
    { k: "body_water_pct",      label: "Agua corporal (%)",       placeholder: "58.2" },
    { k: "bone_mass_kg",        label: "Masa ósea (kg)",          placeholder: "2.78" },
    { k: "bmr_kcal",            label: "TMB (kcal)",              placeholder: "1587" },
    { k: "metabolic_age",       label: "Edad metabólica",         placeholder: "37" },
    { k: "protein_pct",         label: "Proteína (%)",            placeholder: "18.4" },
  ];

  return (
    <Section
      title="Composición corporal"
      description="Registra los datos de tu báscula inteligente. Recomendado: lunes por la mañana en ayunas, mismas condiciones siempre."
    >
      <Row label="Fecha de medición">
        <Input value={date} onChange={setDate} type="date" />
      </Row>
      <div className="grid grid-cols-2 gap-3">
        {FIELDS.map(({ k, label, placeholder }) => (
          <Row key={k} label={label}>
            <Input
              value={fields[k]}
              onChange={(v) => set(k, v)}
              placeholder={placeholder}
              type="number"
            />
          </Row>
        ))}
      </div>
      <SaveButton busy={busy} onClick={save} label="Guardar medición" />
    </Section>
  );
}

function GarminSection({
  idToken,
  onSaved,
  onError,
}: {
  idToken: string | null;
  onSaved: () => void;
  onError: (m: string) => void;
}) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);

  const save = async () => {
    if (!email || !password) {
      onError("Email y password son obligatorios.");
      return;
    }
    setBusy(true);
    try {
      await liebreAuthed.putGarmin({ email, password }, idToken);
      onSaved();
      setEmail("");
      setPassword("");
    } catch (e) {
      onError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Section
      title="Garmin Connect"
      description="Re-conectar o cambiar credenciales. El password se cifra antes de guardarse y validamos el login antes de persistir."
    >
      <Row label="Email">
        <Input value={email} onChange={setEmail} placeholder="tu@email.com" type="email" />
      </Row>
      <Row label="Password">
        <Input
          value={password}
          onChange={setPassword}
          placeholder="••••••••"
          type="password"
        />
      </Row>
      <SaveButton busy={busy} onClick={save} label="Reconectar Garmin" />
    </Section>
  );
}

function DangerSection({
  idToken,
  onDeleted,
  onError,
}: {
  idToken: string | null;
  onDeleted: () => void;
  onError: (m: string) => void;
}) {
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (confirm !== "DELETE") {
      onError("Escribe DELETE para confirmar.");
      return;
    }
    if (!window.confirm("Esta acción es irreversible. ¿Borrar cuenta?")) return;
    setBusy(true);
    try {
      await liebreAuthed.deleteMe(idToken);
      onDeleted();
    } catch (e) {
      onError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <section
      className="card"
      style={{
        borderColor: "color-mix(in srgb, var(--semantic-danger) 30%, var(--rule))",
      }}
    >
      <h2 className="text-lg font-semibold mb-1" style={{ color: "var(--semantic-danger)" }}>
        Borrar cuenta
      </h2>
      <p className="text-xs text-ink-secondary mb-4">
        Borra toda tu información (perfil, HRV, actividades, credenciales Garmin).
        No se puede deshacer. Escribe <code>DELETE</code> para confirmar.
      </p>
      <Input value={confirm} onChange={setConfirm} placeholder="DELETE" />
      <button
        type="button"
        onClick={submit}
        disabled={busy || confirm !== "DELETE"}
        className="mt-3 px-4 py-2 rounded-md text-sm font-semibold text-white disabled:opacity-40"
        style={{ background: "var(--semantic-danger)" }}
      >
        {busy ? "Borrando…" : "Borrar mi cuenta"}
      </button>
    </section>
  );
}

/* ─── inputs primitivos ─── */

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="label-uppercase mb-1.5 block">{label}</span>
      {children}
    </label>
  );
}

function Input({
  value,
  onChange,
  placeholder,
  type = "text",
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
}) {
  return (
    <input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full px-3 py-2.5 rounded-md border border-rule text-sm"
      style={{ background: "var(--bg-card)" }}
    />
  );
}

function SaveButton({
  busy,
  onClick,
  label = "Guardar cambios",
}: {
  busy: boolean;
  onClick: () => void;
  label?: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={busy}
      className="mt-2 px-4 py-2 rounded-md bg-accent-brand text-white text-sm font-semibold hover:opacity-90 transition disabled:opacity-50"
    >
      {busy ? "Guardando…" : label}
    </button>
  );
}
