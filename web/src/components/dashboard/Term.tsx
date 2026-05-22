/**
 * Term — etiqueta inline con tooltip glosario.
 *
 * Uso: <Term k="cadencia">Cadencia</Term>
 *
 * Muestra subrayado dashed para señalar que es término especializado.
 * Al hover muestra la explicación del glosario.
 */

import { GLOSSARY, type GlossaryKey } from "@/lib/glossary";

type Props = {
  k: GlossaryKey;
  children?: React.ReactNode;
};

export function Term({ k, children }: Props) {
  const entry = GLOSSARY[k];
  const label = children ?? entry.term;

  return (
    <span
      className="relative inline group cursor-help"
      style={{
        borderBottom: "1px dotted var(--ink-tertiary)",
      }}
      title={`${entry.term}: ${entry.short}`}
    >
      {label}
    </span>
  );
}
