/**
 * TopBar — header del contenido del dashboard.
 * Replica del mockup: height fijo 60px + border-bottom + saludo izq / fecha der.
 */

export function TopBar({ userName, title }: { userName: string; title: string }) {
  const firstName = userName.split(" ")[0];
  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? "Buenos días" : hour < 19 ? "Buenas tardes" : "Buenas noches";
  const today = new Date().toLocaleDateString("es-CO", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <header
      className="flex items-center justify-between border-b border-rule/60"
      style={{ height: 60, marginBottom: 24 }}
    >
      <div>
        <p className="text-base font-semibold text-ink-primary leading-tight">
          {greeting}, {firstName}
        </p>
        <p className="text-xs text-ink-secondary mt-0.5 capitalize">
          Dashboard · {title}
        </p>
      </div>
      <div className="text-right">
        <p className="label-uppercase">Hoy</p>
        <p className="text-xs text-ink-secondary mt-0.5 capitalize">{today}</p>
      </div>
    </header>
  );
}
