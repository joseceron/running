/**
 * GlossaryPanel — sección expandible con TODOS los términos especializados
 * usados en esta vista. Reduce la curva de aprendizaje del corredor casual.
 */

"use client";

import { useState } from "react";
import { GLOSSARY, type GlossaryKey } from "@/lib/glossary";

type Props = {
  /** Qué términos mostrar (si se omite, muestra todos). */
  keys?: GlossaryKey[];
};

export function GlossaryPanel({ keys }: Props) {
  const [open, setOpen] = useState(false);
  const entries = (keys ?? (Object.keys(GLOSSARY) as GlossaryKey[]))
    .map((k) => ({ k, ...GLOSSARY[k] }));

  return (
    <div className="card">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between text-left"
      >
        <div>
          <div className="flex items-center gap-2">
            <span className="text-base">📚</span>
            <span className="label-uppercase">
              ¿Qué significa cada término?
            </span>
          </div>
          <p className="text-[11px] text-ink-tertiary mt-1">
            Glosario de los términos especializados de esta vista (
            {entries.length})
          </p>
        </div>
        <span
          className="text-ink-secondary text-xl transition-transform"
          style={{ transform: open ? "rotate(180deg)" : "rotate(0deg)" }}
        >
          ⌃
        </span>
      </button>

      {open && (
        <div className="mt-4 pt-4 border-t border-rule/40 grid md:grid-cols-2 gap-x-6 gap-y-4">
          {entries.map(({ k, term, long, example }) => (
            <div key={k}>
              <p className="text-[13px] font-semibold text-ink-primary">
                {term}
              </p>
              <p className="text-xs text-ink-secondary leading-relaxed mt-1">
                {long}
              </p>
              {example && (
                <p
                  className="text-[11px] mt-1.5 px-2 py-1 rounded text-ink-secondary"
                  style={{ background: "var(--bg-card-subtle)" }}
                >
                  ↳ {example}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
