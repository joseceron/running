/**
 * Sidebar — barra de navegación lateral negra fija, estilo Connect.
 * Ancho 272px. Wordmark arriba + items con íconos monocromos.
 *
 * Activo: highlight de fondo sutil + ícono blanco lleno.
 * Inactivo: ícono outline + texto opaco.
 */

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

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
];

export function Sidebar({ userName }: { userName: string }) {
  const firstName = userName.split(" ")[0];
  const pathname = usePathname();
  return (
    <aside
      className="hidden md:flex flex-col fixed top-0 left-0 h-screen bg-bg-sidebar text-ink-on-dark"
      style={{ width: "var(--sidebar-width)" }}
    >
      <div className="px-6 pt-7 pb-9">
        <Link href="/" className="wordmark text-3xl tracking-tight">
          liebre<span className="dot">.</span>
        </Link>
        <p className="text-xs text-ink-on-dark-soft mt-1">
          tu pacer con IA + ciencia
        </p>
      </div>

      <nav className="flex-1 px-3">
        {NAV.map((item) => {
          const isActive =
            item.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
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

      <div className="px-6 py-5 border-t border-white/8">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-accent-brand flex items-center justify-center text-sm font-semibold">
            {firstName[0]}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium truncate">{firstName}</p>
            <p className="text-xs text-ink-on-dark-soft truncate">
              dev · jose_dev_uid
            </p>
          </div>
        </div>
      </div>
    </aside>
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
