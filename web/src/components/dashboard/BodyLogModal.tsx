"use client";

/**
 * BodyLogModal — formulario para registrar mediciones de báscula inteligente.
 * Campos idénticos a la báscula de José: peso, IMC, grasa, músculo, etc.
 * Se captura desde el ProgressCard con botón "Registrar báscula".
 */

import { useState } from "react";
import { liebreAuthed } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

type Props = {
  onClose: () => void;
  onSaved?: () => void;
};

type FormFields = {
  measured_at: string;
  weight_kg: string;
  bmi: string;
  body_fat_pct: string;
  subcutaneous_fat_pct: string;
  visceral_fat: string;
  muscle_mass_kg: string;
  skeletal_muscle_pct: string;
  fat_free_weight_kg: string;
  bone_mass_kg: string;
  body_water_pct: string;
  bmr_kcal: string;
  metabolic_age: string;
  protein_pct: string;
  notes: string;
};

function n(s: string): number | null {
  const v = parseFloat(s);
  return isNaN(v) ? null : v;
}

export function BodyLogModal({ onClose, onSaved }: Props) {
  const { idToken } = useAuth();
  const today = new Date().toISOString().slice(0, 10);

  const [fields, setFields] = useState<FormFields>({
    measured_at: today,
    weight_kg: "",
    bmi: "",
    body_fat_pct: "",
    subcutaneous_fat_pct: "",
    visceral_fat: "",
    muscle_mass_kg: "",
    skeletal_muscle_pct: "",
    fat_free_weight_kg: "",
    bone_mass_kg: "",
    body_water_pct: "",
    bmr_kcal: "",
    metabolic_age: "",
    protein_pct: "",
    notes: "",
  });

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function set(k: keyof FormFields, v: string) {
    setFields((prev) => ({ ...prev, [k]: v }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await liebreAuthed.postBodyComposition(
        {
          measured_at: fields.measured_at,
          weight_kg: n(fields.weight_kg),
          bmi: n(fields.bmi),
          body_fat_pct: n(fields.body_fat_pct),
          subcutaneous_fat_pct: n(fields.subcutaneous_fat_pct),
          visceral_fat: n(fields.visceral_fat),
          muscle_mass_kg: n(fields.muscle_mass_kg),
          skeletal_muscle_pct: n(fields.skeletal_muscle_pct),
          fat_free_weight_kg: n(fields.fat_free_weight_kg),
          bone_mass_kg: n(fields.bone_mass_kg),
          body_water_pct: n(fields.body_water_pct),
          bmr_kcal: n(fields.bmr_kcal) ? Math.round(n(fields.bmr_kcal)!) : null,
          metabolic_age: n(fields.metabolic_age) ? Math.round(n(fields.metabolic_age)!) : null,
          protein_pct: n(fields.protein_pct),
          notes: fields.notes || null,
        },
        idToken,
      );
      onSaved?.();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  }

  const inputClass =
    "w-full text-sm bg-bg-card border border-rule rounded-lg px-3 py-2 text-ink-primary placeholder-ink-tertiary focus:outline-none focus:border-[var(--accent-brand)] transition-colors";

  return (
    <div
      className="fixed inset-0 z-50 flex items-end md:items-center justify-center p-4"
      style={{ background: "rgba(0,0,0,0.55)" }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        className="w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden"
        style={{ background: "var(--bg-card)" }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 pt-5 pb-3 border-b border-rule/40">
          <div>
            <p className="font-semibold text-ink-primary text-[15px]">Registrar báscula</p>
            <p className="text-[11px] text-ink-tertiary mt-0.5">
              Lunes por la mañana · en ayunas · mismas condiciones
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-ink-tertiary hover:text-ink-primary text-xl leading-none"
          >
            ×
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-5 py-4 overflow-y-auto max-h-[70vh]">
          {/* Fecha */}
          <div className="mb-4">
            <label className="text-[11px] text-ink-tertiary uppercase tracking-wider block mb-1">Fecha</label>
            <input type="date" value={fields.measured_at} onChange={(e) => set("measured_at", e.target.value)} className={inputClass} required />
          </div>

          {/* Grid de campos numéricos */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            {[
              { k: "weight_kg" as const, label: "Peso (kg)", placeholder: "68.9" },
              { k: "bmi" as const, label: "IMC", placeholder: "25.3" },
              { k: "body_fat_pct" as const, label: "Grasa corporal (%)", placeholder: "19.2" },
              { k: "subcutaneous_fat_pct" as const, label: "Grasa subcutánea (%)", placeholder: "16.8" },
              { k: "visceral_fat" as const, label: "Grasa visceral", placeholder: "8" },
              { k: "muscle_mass_kg" as const, label: "Masa muscular (kg)", placeholder: "52.81" },
              { k: "skeletal_muscle_pct" as const, label: "Músculo esquelético (%)", placeholder: "52.1" },
              { k: "fat_free_weight_kg" as const, label: "Peso libre de grasa (kg)", placeholder: "55.64" },
              { k: "body_water_pct" as const, label: "Agua corporal (%)", placeholder: "58.2" },
              { k: "bone_mass_kg" as const, label: "Masa ósea (kg)", placeholder: "2.78" },
              { k: "bmr_kcal" as const, label: "TMB (kcal)", placeholder: "1587" },
              { k: "metabolic_age" as const, label: "Edad metabólica", placeholder: "37" },
              { k: "protein_pct" as const, label: "Proteína (%)", placeholder: "18.4" },
            ].map(({ k, label, placeholder }) => (
              <div key={k}>
                <label className="text-[11px] text-ink-tertiary block mb-1">{label}</label>
                <input
                  type="number"
                  step="0.01"
                  placeholder={placeholder}
                  value={fields[k]}
                  onChange={(e) => set(k, e.target.value)}
                  className={inputClass}
                />
              </div>
            ))}
          </div>

          {/* Notas opcionales */}
          <div className="mb-4">
            <label className="text-[11px] text-ink-tertiary uppercase tracking-wider block mb-1">Notas (opcional)</label>
            <input
              type="text"
              placeholder="Ej: después de semana de mayor volumen"
              value={fields.notes}
              onChange={(e) => set("notes", e.target.value)}
              className={inputClass}
            />
          </div>

          {error && (
            <p className="text-[12px] mb-3" style={{ color: "var(--semantic-danger)" }}>
              {error}
            </p>
          )}

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 rounded-xl text-sm font-medium text-ink-secondary border border-rule hover:border-rule/70 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 py-2.5 rounded-xl text-sm font-semibold transition-colors"
              style={{
                background: saving ? "var(--ink-tertiary)" : "var(--accent-brand)",
                color: "white",
                opacity: saving ? 0.6 : 1,
              }}
            >
              {saving ? "Guardando…" : "Guardar medición"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
