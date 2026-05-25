/**
 * Sidebar — barra de navegación lateral negra fija, estilo Connect.
 * Ancho 272px. Wordmark arriba + items con íconos monocromos.
 *
 * Activo: highlight de fondo sutil + ícono blanco lleno.
 * Inactivo: ícono outline + texto opaco.
 */

"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";

import { useAuth } from "@/lib/auth-context";

type NavItem = {
  href: string;
  label: string;
  icon: ReactNode;
};

const NAV: NavItem[] = [
  { href: "/dashboard", label: "Inicio", icon: <IconHome /> },
  { href: "/dashboard/reporte", label: "Reporte", icon: <IconReport /> },
  { href: "/dashboard/actividad/latest", label: "Última actividad", icon: <IconRun /> },
  { href: "/dashboard/salud", label: "Salud", icon: <IconHeart /> },
  { href: "/dashboard/ciencia", label: "Ciencia", icon: <IconBook /> },
  { href: "/dashboard/perfil", label: "Perfil", icon: <IconUser /> },
  { href: "/dashboard/settings", label: "Ajustes", icon: <IconCog /> },
];

function SidebarContent({
  userName,
  onItemClick,
}: {
  userName: string;
  onItemClick?: () => void;
}) {
  const firstName = userName.split(" ")[0];
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout, isConfigured } = useAuth();
  const [loggingOut, setLoggingOut] = useState(false);

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await logout();
    } catch {
      /* la cookie ya se limpió en logout(), seguimos al login */
    }
    onItemClick?.();
    router.replace("/login");
  };
  return (
    <div className="flex flex-col h-full bg-bg-sidebar text-ink-on-dark">
      <div className="px-6 pt-7 pb-9">
        <Link href="/" className="wordmark text-3xl tracking-tight" onClick={onItemClick}>
          liebre<span className="dot">.</span>
        </Link>
        <p className="text-xs text-ink-on-dark-soft mt-1">
          tu pacer con IA + ciencia
        </p>
      </div>

      <nav className="flex-1 px-3 overflow-y-auto">
        {NAV.map((item) => {
          const isActive =
            item.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onItemClick}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${
                isActive
                  ? "bg-white/8 text-ink-on-dark"
                  : "text-ink-on-dark-soft hover:bg-white/5 hover:text-ink-on-dark"
              }`}
            >
              <span className="opacity-90">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="px-6 py-5 border-t border-white/8 space-y-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-accent-brand flex items-center justify-center text-sm font-semibold shrink-0">
            {firstName[0]}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium truncate">{firstName}</p>
            <p className="text-xs text-ink-on-dark-soft truncate">
              {user?.email ?? user?.phoneNumber ?? (isConfigured ? "—" : "dev")}
            </p>
          </div>
        </div>
        {isConfigured && (
          <button
            type="button"
            onClick={handleLogout}
            disabled={loggingOut}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-md text-xs font-medium text-ink-on-dark-soft hover:bg-white/5 hover:text-ink-on-dark transition-colors disabled:opacity-50"
          >
            <IconLogout />
            {loggingOut ? "Cerrando sesión…" : "Cerrar sesión"}
          </button>
        )}
      </div>
    </div>
  );
}

export function Sidebar({ userName }: { userName: string }) {
  return (
    <aside
      className="hidden md:flex flex-col fixed top-0 left-0 h-screen"
      style={{ width: "var(--sidebar-width)" }}
    >
      <SidebarContent userName={userName} />
    </aside>
  );
}

/**
 * MobileNav — botón hamburguesa que abre el sidebar como drawer overlay
 * en pantallas pequeñas. Se cierra al tocar fuera, presionar Escape o
 * navegar a otro item.
 */
export function MobileNav({ userName }: { userName: string }) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", onKey);
    // Bloquea el scroll del body mientras el drawer está abierto
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [open]);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label="Abrir menú"
        title="Menú"
        className="md:hidden w-9 h-9 rounded-md flex items-center justify-center border border-rule hover:border-accent-brand transition-colors"
        style={{ background: "var(--bg-card)" }}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>

      {open && (
        <div
          className="md:hidden fixed inset-0 z-50"
          onClick={() => setOpen(false)}
          role="dialog"
          aria-modal="true"
        >
          {/* backdrop */}
          <div
            className="absolute inset-0"
            style={{ background: "rgba(0,0,0,0.45)" }}
          />
          {/* drawer */}
          <div
            className="absolute top-0 left-0 h-full w-72 max-w-[85vw] shadow-xl"
            onClick={(e) => e.stopPropagation()}
            style={{ animation: "liebre-slide-in 0.2s ease-out" }}
          >
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Cerrar menú"
              className="absolute top-3 right-3 w-8 h-8 rounded-md flex items-center justify-center text-white/80 hover:text-white hover:bg-white/10 z-10"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
            <SidebarContent userName={userName} onItemClick={() => setOpen(false)} />
          </div>
        </div>
      )}
    </>
  );
}

/* ─── íconos inline SVG monocromos ─── */

function IconReport() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <path d="M14 2v6h6" />
      <path d="M8 13h8" />
      <path d="M8 17h5" />
    </svg>
  );
}
function IconHome() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M3 11l9-7 9 7v9a2 2 0 0 1-2 2h-4v-7H9v7H5a2 2 0 0 1-2-2v-9z" />
    </svg>
  );
}
function IconRun() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="17" cy="4" r="2" />
      <path d="M15 22l-2-5 3-2-3-3 3-4 4 6 3 2" />
      <path d="M8 14l-2 1-3-2 4-4 4 2-2 5z" />
    </svg>
  );
}
function IconHeart() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
    </svg>
  );
}
function IconBook() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
    </svg>
  );
}
function IconUser() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="8" r="4" />
      <path d="M4 22a8 8 0 0 1 16 0" />
    </svg>
  );
}
function IconLogout() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  );
}
function IconCog() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </svg>
  );
}
