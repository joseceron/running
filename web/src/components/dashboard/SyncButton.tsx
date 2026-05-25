/**
 * SyncButton — botón para disparar la sincronización Garmin desde la UI.
 * Tras éxito recarga la página para reflejar los nuevos datos.
 */

"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { useAuth } from "@/lib/auth-context";

type Status = "idle" | "syncing" | "ok" | "error";

export function SyncButton({ compact = false }: { compact?: boolean }) {
  const router = useRouter();
  const { idToken } = useAuth();
  const [status, setStatus] = useState<Status>("idle");
  const [msg, setMsg] = useState<string>("");

  const trigger = async () => {
    setStatus("syncing");
    setMsg("");
    try {
      const apiBase =
        process.env.NEXT_PUBLIC_LIEBRE_API ?? "http://localhost:8080";
      const res = await fetch(`${apiBase}/v1/users/me/sync`, {
        method: "POST",
        headers: idToken ? { Authorization: `Bearer ${idToken}` } : undefined,
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`HTTP ${res.status}: ${text}`);
      }
      const data = (await res.json()) as {
        hrv_nights: number;
        cronologia_ok: boolean;
        activity_ok: boolean;
        duration_secs: number;
        error: string | null;
      };
      setStatus("ok");
      setMsg(
        `✓ ${data.hrv_nights} noches HRV · cronología ${
          data.cronologia_ok ? "OK" : "—"
        } · actividad ${data.activity_ok ? "OK" : "—"} · ${data.duration_secs}s`
      );
      // Recarga server components con los nuevos datos
      router.refresh();
      setTimeout(() => setStatus("idle"), 4000);
    } catch (e) {
      setStatus("error");
      setMsg(e instanceof Error ? e.message : String(e));
      setTimeout(() => setStatus("idle"), 5000);
    }
  };

  const isLoading = status === "syncing";

  if (compact) {
    return (
      <button
        type="button"
        onClick={trigger}
        disabled={isLoading}
        title="Sincronizar con Garmin"
        aria-label="Sincronizar"
        className="w-9 h-9 rounded-full flex items-center justify-center border border-rule hover:border-accent-brand hover:text-accent-brand transition-colors disabled:opacity-50"
        style={{ background: "var(--bg-card)" }}
      >
        <RefreshIcon spinning={isLoading} />
      </button>
    );
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <button
        type="button"
        onClick={trigger}
        disabled={isLoading}
        className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md border border-rule hover:border-accent-brand hover:text-accent-brand transition-colors text-xs font-medium disabled:opacity-50"
        style={{ background: "var(--bg-card)" }}
      >
        <RefreshIcon spinning={isLoading} />
        {isLoading ? "Sincronizando…" : "Sincronizar Garmin"}
      </button>
      {msg && (
        <p
          className="text-[10px] max-w-[260px] text-right leading-tight"
          style={{
            color:
              status === "ok"
                ? "var(--semantic-positive)"
                : status === "error"
                  ? "var(--semantic-danger)"
                  : "var(--ink-tertiary)",
          }}
        >
          {msg}
        </p>
      )}
    </div>
  );
}

function RefreshIcon({ spinning }: { spinning?: boolean }) {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{
        animation: spinning ? "spin 1s linear infinite" : undefined,
      }}
    >
      <path d="M21 12a9 9 0 0 1-15 6.7L3 16" />
      <path d="M3 12a9 9 0 0 1 15-6.7L21 8" />
      <path d="M21 3v5h-5" />
      <path d="M3 21v-5h5" />
      <style>{`@keyframes spin { from { transform: rotate(0); } to { transform: rotate(360deg); } }`}</style>
    </svg>
  );
}
