/**
 * TopBar — header del contenido del dashboard con saludo + fecha + botón sync.
 * Responsive: en mobile reduce padding y oculta la fecha extendida.
 */

import { DateNavigator } from "./DateNavigator";
import { MobileNav } from "./Sidebar";
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
      className="border-b border-rule/60"
      style={{ marginBottom: 20, paddingBottom: 12 }}
    >
      {/* Fila 1: hamburger + saludo + sync (siempre cabe en una línea) */}
      <div className="flex items-center justify-between gap-3" style={{ minHeight: 48 }}>
        <div className="flex items-center gap-2.5 min-w-0 flex-1">
          <MobileNav userName={userName} />
          <div className="min-w-0">
            <p className="text-base font-semibold text-ink-primary leading-tight truncate">
              {greeting}, {firstName}
            </p>
            <p className="text-xs text-ink-secondary mt-0.5 capitalize truncate">
              Dashboard · {title}
            </p>
          </div>
        </div>
        <div className="shrink-0">
          <SyncButton compact />
        </div>
      </div>

      {/* Fila 2: fecha + DateNavigator (puede envolverse en móvil) */}
      <div className="flex items-center justify-between gap-3 mt-2.5 flex-wrap">
        <div className="min-w-0">
          <span className="label-uppercase mr-2">{isToday ? "Hoy" : "Día"}</span>
          <span className="text-xs text-ink-secondary capitalize">{label}</span>
        </div>
        {showDateNavigator && (
          <div className="shrink-0">
            <DateNavigator />
          </div>
        )}
      </div>
    </header>
  );
}
