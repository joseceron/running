/**
 * TopBar — header del contenido del dashboard con saludo + fecha + botón sync.
 * Responsive: en mobile reduce padding y oculta la fecha extendida.
 */

import { DateNavigator } from "./DateNavigator";
import { SyncButton } from "./SyncButton";

const TZ = "America/Bogota";

function colombiaHour(): number {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: TZ,
    hour: "numeric",
    hour12: false,
  }).formatToParts(new Date());
  const h = parts.find((p) => p.type === "hour")?.value ?? "0";
  return Number(h);
}

function formatDateEsCO(iso?: string): { label: string; isToday: boolean } {
  const today = new Intl.DateTimeFormat("en-CA", {
    timeZone: TZ,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
  const target = iso || today;
  const [y, m, d] = target.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d, 12));
  const label = dt.toLocaleDateString("es-CO", {
    timeZone: TZ,
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
  return { label, isToday: target === today };
}

export function TopBar({
  userName,
  title,
  currentDate,
  showDateNavigator = true,
}: {
  userName: string;
  title: string;
  currentDate?: string;
  showDateNavigator?: boolean;
}) {
  const firstName = userName.split(" ")[0];
  const hour = colombiaHour();
  const greeting =
    hour < 12 ? "Buenos días" : hour < 19 ? "Buenas tardes" : "Buenas noches";
  const { label, isToday } = formatDateEsCO(currentDate);

  return (
    <header
      className="flex items-center justify-between border-b border-rule/60 gap-3 flex-wrap"
      style={{ minHeight: 60, marginBottom: 20, paddingBottom: 12 }}
    >
      <div className="min-w-0">
        <p className="text-base font-semibold text-ink-primary leading-tight">
          {greeting}, {firstName}
        </p>
        <p className="text-xs text-ink-secondary mt-0.5 capitalize truncate">
          Dashboard · {title}
        </p>
      </div>
      <div className="flex items-center gap-3 shrink-0 flex-wrap justify-end">
        <div className="text-right hidden sm:block">
          <p className="label-uppercase">{isToday ? "Hoy" : "Día"}</p>
          <p className="text-xs text-ink-secondary mt-0.5 capitalize">{label}</p>
        </div>
        {showDateNavigator && <DateNavigator />}
        <SyncButton />
      </div>
    </header>
  );
}
