"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import {
  RecaptchaVerifier,
  signInWithPhoneNumber,
  signInWithPopup,
  type ConfirmationResult,
} from "firebase/auth";
import { getFirebaseAuth, googleProvider, isFirebaseConfigured } from "@/lib/firebase";
import { useAuth } from "@/lib/auth-context";
import { liebreAuthed } from "@/lib/api";

type Stage = "choose" | "phone-input" | "phone-code";

/** Decide a dónde mandar a un user recién autenticado:
 *  /onboarding si nunca completó perfil, /dashboard si sí.
 */
async function postLoginRedirect(idToken: string | null): Promise<string> {
  try {
    const profile = await liebreAuthed.getProfileOrNull(idToken);
    return profile ? "/dashboard" : "/onboarding";
  } catch {
    // Si el backend está caído, intentar dashboard de todos modos.
    return "/dashboard";
  }
}

export default function LoginPage() {
  const router = useRouter();
  const { user, loading, idToken } = useAuth();
  const [stage, setStage] = useState<Stage>("choose");
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [confirmation, setConfirmation] = useState<ConfirmationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const recaptchaRef = useRef<HTMLDivElement | null>(null);

  // Si ya está logueado, decidir destino (onboarding vs dashboard) según perfil.
  useEffect(() => {
    if (!loading && user) {
      postLoginRedirect(idToken).then((dest) => router.replace(dest));
    }
  }, [loading, user, idToken, router]);

  const handleGoogle = async () => {
    if (!isFirebaseConfigured) {
      setError("Firebase no está configurado en este entorno.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const result = await signInWithPopup(getFirebaseAuth(), googleProvider);
      const token = await result.user.getIdToken();
      const dest = await postLoginRedirect(token);
      router.replace(dest);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  const handleSendCode = async () => {
    if (!phone.startsWith("+")) {
      setError("Incluye el código de país: +57 3XXXXXXXXX");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const auth = getFirebaseAuth();
      const verifier = new RecaptchaVerifier(auth, recaptchaRef.current!, {
        size: "invisible",
      });
      const conf = await signInWithPhoneNumber(auth, phone, verifier);
      setConfirmation(conf);
      setStage("phone-code");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  const handleVerifyCode = async () => {
    if (!confirmation) return;
    setBusy(true);
    setError(null);
    try {
      const result = await confirmation.confirm(code);
      const token = await result.user.getIdToken();
      const dest = await postLoginRedirect(token);
      router.replace(dest);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col bg-bg-page text-ink-primary">
      <nav className="px-4 md:px-8 py-4 border-b border-rule/60">
        <Link href="/" className="wordmark text-2xl">
          liebre<span className="dot">.</span>
        </Link>
      </nav>

      <section className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="card w-full max-w-md">
          <p className="label-uppercase mb-2">Entrar a Liebre</p>
          <h1 className="text-2xl font-semibold leading-tight mb-1">
            Tu pacer con IA + ciencia
          </h1>
          <p className="text-sm text-ink-secondary mb-6">
            Sin contraseña — Google o tu número de teléfono.
          </p>

          {!isFirebaseConfigured && (
            <div
              className="mb-4 p-3 rounded-md text-xs"
              style={{
                background:
                  "color-mix(in srgb, var(--semantic-warning) 12%, transparent)",
                color: "var(--semantic-warning)",
              }}
            >
              ⚠️ Firebase aún no está configurado en este entorno. El login
              está deshabilitado. Mientras tanto, puedes ver el{" "}
              <Link
                href="/dashboard"
                className="underline font-semibold"
              >
                demo del dashboard
              </Link>
              .
            </div>
          )}

          {error && (
            <div
              className="mb-4 p-3 rounded-md text-xs"
              style={{
                background:
                  "color-mix(in srgb, var(--semantic-danger) 12%, transparent)",
                color: "var(--semantic-danger)",
              }}
            >
              {error}
            </div>
          )}

          {stage === "choose" && (
            <div className="space-y-3">
              <button
                type="button"
                onClick={handleGoogle}
                disabled={busy || !isFirebaseConfigured}
                className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-md border border-rule font-medium text-sm hover:border-ink-primary transition disabled:opacity-50"
              >
                <GoogleLogo />
                Continuar con Google
              </button>
              <button
                type="button"
                onClick={() => setStage("phone-input")}
                disabled={!isFirebaseConfigured}
                className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-md font-medium text-sm bg-ink-primary text-white hover:opacity-90 transition disabled:opacity-50"
              >
                📱 Continuar con tu teléfono
              </button>
            </div>
          )}

          {stage === "phone-input" && (
            <div className="space-y-3">
              <label className="block">
                <span className="label-uppercase mb-2 block">
                  Número con código de país
                </span>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+57 3001234567"
                  className="w-full px-4 py-3 rounded-md border border-rule text-base tnum"
                  style={{ background: "var(--bg-card)" }}
                  autoComplete="tel"
                />
              </label>
              <div ref={recaptchaRef} />
              <button
                type="button"
                onClick={handleSendCode}
                disabled={busy || phone.length < 8}
                className="w-full px-4 py-3 rounded-md bg-accent-brand text-white font-semibold text-sm hover:opacity-90 transition disabled:opacity-50"
              >
                {busy ? "Enviando código..." : "Enviar código por SMS"}
              </button>
              <button
                type="button"
                onClick={() => setStage("choose")}
                className="w-full text-xs text-ink-secondary hover:text-ink-primary py-2"
              >
                ← Volver
              </button>
            </div>
          )}

          {stage === "phone-code" && (
            <div className="space-y-3">
              <label className="block">
                <span className="label-uppercase mb-2 block">
                  Código SMS de 6 dígitos
                </span>
                <input
                  type="text"
                  inputMode="numeric"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder="123456"
                  className="w-full px-4 py-3 rounded-md border border-rule text-base tnum text-center font-bold"
                  style={{ background: "var(--bg-card)", letterSpacing: "0.3em" }}
                  maxLength={6}
                  autoComplete="one-time-code"
                />
              </label>
              <button
                type="button"
                onClick={handleVerifyCode}
                disabled={busy || code.length !== 6}
                className="w-full px-4 py-3 rounded-md bg-accent-brand text-white font-semibold text-sm hover:opacity-90 transition disabled:opacity-50"
              >
                {busy ? "Verificando..." : "Entrar"}
              </button>
              <button
                type="button"
                onClick={() => setStage("phone-input")}
                className="w-full text-xs text-ink-secondary hover:text-ink-primary py-2"
              >
                ← Cambiar número
              </button>
            </div>
          )}

          <p className="text-[11px] text-ink-tertiary mt-6 leading-relaxed text-center">
            Al continuar aceptas los términos del servicio. Nunca te enviaremos
            spam ni compartiremos tu información.
          </p>
        </div>
      </section>
    </main>
  );
}

function GoogleLogo() {
  return (
    <svg width="18" height="18" viewBox="0 0 48 48">
      <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3c-1.7 4.6-6.1 8-11.3 8a12 12 0 1 1 0-24c3 0 5.8 1.1 8 3l5.7-5.7C33.6 6.1 29 4 24 4 13 4 4 13 4 24s9 20 20 20 20-9 20-20c0-1.2-.1-2.3-.4-3.5z"/>
      <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 16 18.9 13 24 13c3 0 5.8 1.1 8 3l5.7-5.7C33.6 6.1 29 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/>
      <path fill="#4CAF50" d="M24 44c5 0 9.5-1.9 12.9-5l-6-5C29 35.4 26.6 36 24 36c-5.1 0-9.5-3.3-11.2-7.9l-6.6 5C9.5 39.6 16.2 44 24 44z"/>
      <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.3-2.3 4.3-4.3 5.7l6 5C40.5 35.1 44 30 44 24c0-1.2-.1-2.3-.4-3.5z"/>
    </svg>
  );
}
