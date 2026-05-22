/**
 * RowFactorCard — alineado con mockup FactorCard.
 *
 * Layout flex items-start con interpretación + cita SIEMPRE visibles
 * debajo del valor cuando se proveen (no expandibles).
 */

import type { ReactNode } from "react";
import { CiteBadge } from "./CiteBadge";

export type FactorStatus = "balanced" | "low" | "unbalanced" | "neutral";

const STATUS_COLOR: Record<FactorStatus, string> = {
  balanced: "var(--hrv-balanced)",
  low: "var(--hrv-low)",
  unbalanced: "var(--hrv-unbalanced)",
  neutral: "var(--hrv-noState)",
};

type BaseProps = {
  name: string;
  value: string | number;
  unit?: string;
  /** Texto interpretativo (diferencial Liebre). */
  interpretation?: string;
  /** Cita corta. */
  citation?: string;
};

type VerbalProps = BaseProps & {
  mode?: "verbal";
  label: ReactNode;
  status?: FactorStatus;
};

type SignedProps = BaseProps & {
  mode: "signed";
  impact: number;
  impactUnit?: string;
};

type Props = VerbalProps | SignedProps;

export function RowFactorCard(props: Props) {
  const { name, value, unit, interpretation, citation } = props;

  return (
    <div
      className="rounded-md"
      style={{
        background: "var(--bg-card-subtle)",
        padding: "14px 16px",
        marginBottom: 10,
      }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-[13px] font-semibold text-ink-primary">{name}</p>
          <p className="text-xs text-ink-tertiary mt-0.5 tnum">
            {value}
            {unit && <span className="ml-1">{unit}</span>}
          </p>
          {interpretation && (
            <p className="text-xs text-ink-secondary mt-1.5 leading-relaxed">
              {interpretation}
            </p>
          )}
          {citation && <CiteBadge text={citation} />}
        </div>

        {props.mode === "signed" ? (
          <SignedImpact impact={props.impact} unit={props.impactUnit} />
        ) : (
          <VerbalLabel label={props.label} status={props.status ?? "neutral"} />
        )}
      </div>
    </div>
  );
}

function VerbalLabel({ label, status }: { label: ReactNode; status: FactorStatus }) {
  return (
    <div className="flex items-center gap-2 shrink-0 pt-0.5">
      <span className="text-sm text-ink-secondary">{label}</span>
      <span
        aria-hidden
        className="inline-block w-2 h-2 rounded-full"
        style={{ background: STATUS_COLOR[status] }}
      />
    </div>
  );
}

function SignedImpact({ impact, unit }: { impact: number; unit?: string }) {
  const isPositive = impact >= 0;
  const color = isPositive ? "var(--impact-positive)" : "var(--impact-negative)";
  const sign = isPositive ? "+" : "−";
  return (
    <span
      className="tnum text-xl font-bold shrink-0 leading-none"
      style={{ color, paddingTop: 2 }}
    >
      {sign}
      {Math.abs(impact)}
      {unit && <span className="ml-0.5 text-sm">{unit}</span>}
    </span>
  );
}
