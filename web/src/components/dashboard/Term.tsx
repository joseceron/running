/**
 * Term — etiqueta inline con tooltip CSS visible al hover.
 *
 * Uso: <Term k="cadencia">Cadencia</Term>
 *
 * En lugar del title nativo (poco descubrible), muestra un popover con
 * fondo oscuro al hacer hover.
 */

"use client";

import { useState } from "react";
import { GLOSSARY, type GlossaryKey } from "@/lib/glossary";

type Props = {
  k: GlossaryKey;
  children?: React.ReactNode;
  /** Posición del tooltip: arriba (default) o abajo */
  side?: "top" | "bottom";
};

export function Term({ k, children, side = "top" }: Props) {
  const entry = GLOSSARY[k];
  const label = children ?? entry.term;
  const [open, setOpen] = useState(false);

  return (
    <span
      className="relative inline-block"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onFocus={() => setOpen(true)}
      onBlur={() => setOpen(false)}
    >
      <span
        tabIndex={0}
        style={{
          borderBottom: "1px dotted var(--ink-tertiary)",
          cursor: "help",
        }}
      >
        {label}
      </span>
      {open && (
        <span
          role="tooltip"
          style={{
            position: "absolute",
            left: "50%",
            transform: "translateX(-50%)",
            ...(side === "top"
              ? { bottom: "calc(100% + 6px)" }
              : { top: "calc(100% + 6px)" }),
            width: 260,
            maxWidth: "min(260px, 90vw)",
            background: "var(--ink-primary)",
            color: "#fff",
            padding: "10px 12px",
            borderRadius: 6,
            fontSize: 12,
            fontWeight: 400,
            lineHeight: 1.45,
            letterSpacing: 0,
            textTransform: "none",
            boxShadow: "0 8px 24px rgba(0,0,0,0.22)",
            zIndex: 50,
            pointerEvents: "none",
            whiteSpace: "normal",
          }}
        >
          <strong
            style={{
              display: "block",
              fontSize: 11,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              opacity: 0.7,
              marginBottom: 4,
              fontWeight: 600,
            }}
          >
            {entry.term}
          </strong>
          {entry.short}
          {entry.example && (
            <span
              style={{
                display: "block",
                marginTop: 6,
                paddingTop: 6,
                borderTop: "1px solid rgba(255,255,255,0.15)",
                opacity: 0.85,
                fontStyle: "italic",
                fontSize: 11,
              }}
            >
              {entry.example}
            </span>
          )}
          {/* Flecha */}
          <span
            style={{
              position: "absolute",
              left: "50%",
              transform: "translateX(-50%) rotate(45deg)",
              width: 8,
              height: 8,
              background: "var(--ink-primary)",
              ...(side === "top" ? { bottom: -4 } : { top: -4 }),
            }}
          />
        </span>
      )}
    </span>
  );
}
