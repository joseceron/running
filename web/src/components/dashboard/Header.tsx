import Link from "next/link";

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

export function DashboardHeader({ name }: { name: string }) {
  const firstName = name.split(" ")[0];
  const hour = colombiaHour();
  const greeting = hour < 12 ? "Buenos días" : hour < 19 ? "Buenas tardes" : "Buenas noches";
  return (
    <header className="px-8 py-6 border-b border-rule/60 flex items-center justify-between">
      <div className="flex items-center gap-8">
        <Link href="/" className="wordmark text-2xl">
          liebre<span className="dot">.</span>
        </Link>
        <span className="text-sm text-muted hidden md:inline">
          {greeting}, <span className="text-ink font-medium">{firstName}</span>
        </span>
      </div>
      <div className="text-xs text-muted">dev · jose_dev_uid</div>
    </header>
  );
}
