/**
 * renderWithTerms — convierte texto plano en nodos React,
 * envolviendo términos conocidos en <Term> y eliminando sus
 * explicaciones parentéticas inline (ej: "HRV (variación entre...)").
 *
 * El LLM genera las definiciones inline para corredores no técnicos,
 * pero en el UI esas definiciones viven en el tooltip de <Term>.
 */

import { Term } from "@/components/dashboard/Term";
import type { GlossaryKey } from "@/lib/glossary";

// Mapa: patrón regex (sin flags) → GlossaryKey
// El orden importa — primero los más largos para evitar solapamientos.
const TERM_MAP: Array<{ pattern: RegExp; key: GlossaryKey }> = [
  { pattern: /Body Battery/g,   key: "body_battery" },
  { pattern: /VO₂max/g,         key: "vo2max" },
  { pattern: /VO2max/g,         key: "vo2max" },
  { pattern: /ACWR/g,           key: "acwr" },
  { pattern: /HRV/g,            key: "hrv" },
  { pattern: /VFC/g,            key: "vfc" },
  { pattern: /\bGCT\b/g,        key: "gct" },
  { pattern: /\bSPM\b/g,        key: "spm" },
  { pattern: /\bZ1\b/g,         key: "z1" },
  { pattern: /\bZ2\b/g,         key: "z2" },
  { pattern: /\bZ3\b/g,         key: "z3" },
  { pattern: /\bZ4\b/g,         key: "z4" },
  { pattern: /\bZ5\b/g,         key: "z5" },
  { pattern: /\bbaseline\b/gi,  key: "baseline" },
];

// Regex que captura un término seguido opcionalmente de "(definición)" o
// "(definición más larga con coma)" — hasta 300 chars entre paréntesis.
function buildFullPattern(): RegExp {
  const terms = TERM_MAP.map((t) =>
    t.pattern.source.replace(/\\b/g, "").replace(/\//g, "")
  ).join("|");
  // Captura: (término)(paréntesis opcional)
  return new RegExp(
    `(${terms})(\\s*\\([^)]{0,300}\\))?`,
    "g"
  );
}

export function renderWithTerms(text: string): React.ReactNode[] {
  const fullPattern = buildFullPattern();
  const nodes: React.ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = fullPattern.exec(text)) !== null) {
    const [fullMatch, termText] = match;
    const matchStart = match.index;

    // Texto antes del match
    if (matchStart > lastIndex) {
      nodes.push(text.slice(lastIndex, matchStart));
    }

    // Buscar la clave correspondiente al término detectado
    const entry = TERM_MAP.find((t) => {
      const r = new RegExp(t.pattern.source, "i");
      return r.test(termText);
    });

    if (entry) {
      nodes.push(
        <Term key={`${entry.key}-${matchStart}`} k={entry.key}>
          {termText}
        </Term>
      );
    } else {
      nodes.push(fullMatch);
    }

    lastIndex = matchStart + fullMatch.length;
  }

  // Texto sobrante
  if (lastIndex < text.length) {
    nodes.push(text.slice(lastIndex));
  }

  return nodes;
}
