/**
 * CiteBadge — pill de cita científica (Plews 2017 · J Sci · RCT).
 * Replicado del mockup de Claude Design.
 */

export function CiteBadge({ text }: { text: string }) {
  return (
    <div className="flex items-start gap-1.5 mt-2">
      <span className="text-xs leading-relaxed shrink-0">📄</span>
      <span className="text-xs font-medium text-accent-brand leading-snug">
        {text}
      </span>
    </div>
  );
}
