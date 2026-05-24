/**
 * DateNavigator — flechas prev/next + picker para moverse entre días.
 * Sincroniza el query param ?date=YYYY-MM-DD del URL.
 * No permite navegar a fechas futuras.
 */

"use client";

import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { useCallback, useMemo } from "react";

const TZ = "America/Bogota";

function todayInBogota(): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: TZ,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
}

function addDays(iso: string, days: number): string {
  const [y, m, d] = iso.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  dt.setUTCDate(dt.getUTCDate() + days);
  return dt.toISOString().slice(0, 10);
}

export function DateNavigator() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const today = useMemo(() => todayInBogota(), []);
  const current = searchParams.get("date") || today;
  const isToday = current === today;

  const push = useCallback(
    (date: string) => {
      const params = new URLSearchParams(searchParams);
      if (date === today) params.delete("date");
      else params.set("date", date);
      const q = params.toString();
      router.push(q ? `${pathname}?${q}` : pathname);
    },
    [router, pathname, searchParams, today]
  );

  const onPrev = () => push(addDays(current, -1));
  const onNext = () => {
    const next = addDays(current, 1);
    if (next > today) return;
    push(next);
  };
  const onPick = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.value && e.target.value <= today) push(e.target.value);
  };
  const onToday = () => push(today);

  return (
    <div className="flex items-center gap-1.5">
      <button
        type="button"
        onClick={onPrev}
        aria-label="Día anterior"
        title="Día anterior"
        className="w-7 h-7 rounded-md border border-rule hover:border-accent-brand hover:text-accent-brand transition-colors flex items-center justify-center text-xs"
        style={{ background: "var(--bg-card)" }}
      >
        ◀
      </button>
      <input
        type="date"
        value={current}
        max={today}
        onChange={onPick}
        aria-label="Selecciona fecha"
        className="text-xs px-2 py-1 rounded-md border border-rule hover:border-accent-brand focus:border-accent-brand outline-none"
        style={{ background: "var(--bg-card)", color: "var(--ink-primary)" }}
      />
      <button
        type="button"
        onClick={onNext}
        disabled={isToday}
        aria-label="Día siguiente"
        title={isToday ? "Ya estás en hoy" : "Día siguiente"}
        className="w-7 h-7 rounded-md border border-rule hover:border-accent-brand hover:text-accent-brand transition-colors flex items-center justify-center text-xs disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:border-rule disabled:hover:text-current"
        style={{ background: "var(--bg-card)" }}
      >
        ▶
      </button>
      {!isToday && (
        <button
          type="button"
          onClick={onToday}
          className="text-[10px] uppercase tracking-wide px-2 py-1 rounded-md border border-rule hover:border-accent-brand hover:text-accent-brand transition-colors"
          style={{ background: "var(--bg-card)" }}
        >
          Hoy
        </button>
      )}
    </div>
  );
}
