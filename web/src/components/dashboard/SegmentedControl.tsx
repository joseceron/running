/**
 * SegmentedControl temporal — patrón "1 día / 7 días / 4 semanas / 1 año"
 * idéntico al que Connect usa en todas sus páginas de salud.
 *
 * Estados: fondo gris inactivo, fondo azul brand para activo.
 */

"use client";

import { useState } from "react";

export type RangeOption = "1d" | "7d" | "4w" | "1y";

const LABELS: Record<RangeOption, string> = {
  "1d": "1 día",
  "7d": "7 días",
  "4w": "4 semanas",
  "1y": "1 año",
};

type Props = {
  options?: RangeOption[];
  value?: RangeOption;
  defaultValue?: RangeOption;
  onChange?: (next: RangeOption) => void;
  size?: "sm" | "md";
};

export function SegmentedControl({
  options = ["1d", "7d", "4w"],
  value,
  defaultValue = "7d",
  onChange,
  size = "md",
}: Props) {
  const [internal, setInternal] = useState<RangeOption>(
    value ?? defaultValue
  );
  const active = value ?? internal;

  const handle = (opt: RangeOption) => {
    if (value === undefined) setInternal(opt);
    onChange?.(opt);
  };

  const padding = size === "sm" ? "px-3 py-1 text-xs" : "px-4 py-1.5 text-sm";

  return (
    <div
      role="tablist"
      className="inline-flex bg-bg-card-hover rounded-md p-0.5"
    >
      {options.map((opt) => {
        const isActive = active === opt;
        return (
          <button
            key={opt}
            role="tab"
            aria-selected={isActive}
            onClick={() => handle(opt)}
            className={`${padding} font-medium rounded transition-colors ${
              isActive
                ? "bg-accent-brand text-ink-on-dark shadow-sm"
                : "text-ink-secondary hover:text-ink-primary"
            }`}
          >
            {LABELS[opt]}
          </button>
        );
      })}
    </div>
  );
}
