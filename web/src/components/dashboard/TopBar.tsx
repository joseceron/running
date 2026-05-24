/**
 * TopBar — header del contenido del dashboard con saludo + fecha + botón sync.
 * Responsive: en mobile reduce padding y oculta la fecha extendida.
 */

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

export function TopBar({ userName, title }: { userName: string; title: string }) {
  const firstName = userName.split(" ")[0];
  const hour = colombiaHour();
  const greeting =
    hour < 12 ? "Buenos días" : hour < 19 ? "Buenas tardes" : "Buenas noches";
  const today = new Date().toLocaleDateString("es-CO", {
    timeZone: TZ,
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <header
      className="flex items-center justify-between border-b border-rule/60 gap-3"
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
      <div className="flex items-center gap-3 shrink-0">
        <div className="text-right hidden sm:block">
          <p className="label-uppercase">Hoy</p>
          <p className="text-xs text-ink-secondary mt-0.5 capitalize">{today}</p>
        </div>
        <SyncButton />
      </div>
    </header>
  );
}
