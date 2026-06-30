/**
 * AuthGuard — bloquea contenido si no hay sesión activa.
 *
 * En dev sin Firebase configurado, deja pasar (no bloquea — modo demo).
 * En producción con Firebase configurado, redirige a /login si no hay user.
 */

"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { useAuth } from "@/lib/auth-context";
import { liebreAuthed } from "@/lib/api";

export function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, loading, isConfigured, idToken } = useAuth();

  useEffect(() => {
    // Si Firebase no está configurado (modo demo dev), no bloqueamos
    if (!isConfigured) return;
    if (loading) return;
    if (!user) {
      router.replace("/login");
      return;
    }
    // Hay user logueado: si NO tiene perfil y no estamos ya en onboarding,
    // redirigir. Esto cubre el caso de un user que cierra y vuelve a abrir
    // sin haber completado el wizard.
    if (pathname?.startsWith("/onboarding")) return;
    // El idToken se hidrata en un setState aparte del listener, así que puede
    // llegar como null aunque ya haya user. Sin esto, la llamada iría sin
    // Bearer → 401 → rebote espurio a /onboarding en el primer ciclo.
    if (!idToken) return;
    liebreAuthed
      .getProfileOrNull(idToken)
      .then((profile) => {
        if (!profile) router.replace("/onboarding");
      })
      .catch(() => {
        /* backend caído: dejamos seguir, dashboard mostrará su propio error */
      });
  }, [isConfigured, loading, user, idToken, pathname, router]);

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
