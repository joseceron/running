/**
 * AuthGuard — bloquea contenido si no hay sesión activa.
 *
 * En dev sin Firebase configurado, deja pasar (no bloquea — modo demo).
 * En producción con Firebase configurado, redirige a /login si no hay user.
 */

"use client";

import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { useAuth } from "@/lib/auth-context";

export function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { user, loading, isConfigured } = useAuth();

  useEffect(() => {
    // Si Firebase no está configurado (modo demo dev), no bloqueamos
    if (!isConfigured) return;
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [isConfigured, loading, user, router]);

  // En modo demo dev, mostrar contenido siempre
  if (!isConfigured) return <>{children}</>;

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg-page">
        <div className="text-center">
          <div
            className="w-10 h-10 rounded-full mx-auto mb-3 animate-spin"
            style={{
              borderTop: "2px solid var(--accent-brand)",
              borderRight: "2px solid var(--accent-brand)",
              borderBottom: "2px solid transparent",
              borderLeft: "2px solid transparent",
            }}
          />
          <p className="text-sm text-ink-secondary">Cargando sesión…</p>
        </div>
      </div>
    );
  }

  // Sin sesión: el useEffect ya redirige; renderizar nada mientras tanto
  if (!user) return null;

  return <>{children}</>;
}
