/**
 * AuthContext — provee el usuario actual + ID token a todo el árbol cliente.
 *
 * Suscribe a onAuthStateChanged y mantiene el ID token fresco (refresh
 * cada vez que el SDK lo invalida).
 */

"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { onAuthStateChanged, signOut, type User } from "firebase/auth";
import { getFirebaseAuth, isFirebaseConfigured } from "./firebase";

const TOKEN_COOKIE = "liebre_id_token";

/** Setea cookie no-HttpOnly con el idToken para que los Server Components
 *  la lean via next/headers y la pasen como Bearer al backend.
 *
 *  Trade-off: NO es HttpOnly porque la setea el cliente JS — pero ese mismo
 *  idToken ya vive en localStorage del Firebase SDK, así que el nivel de
 *  exposición es equivalente. Para upgrade futuro: endpoint /api/auth/session
 *  que cambia idToken por session cookie HttpOnly firmada server-side.
 */
function setTokenCookie(token: string) {
  // Firebase idToken expira en 1h. Max-Age en segundos.
  const isSecure = typeof window !== "undefined"
    && window.location.protocol === "https:";
  document.cookie = `${TOKEN_COOKIE}=${encodeURIComponent(token)}; Path=/; Max-Age=3600; SameSite=Lax${isSecure ? "; Secure" : ""}`;
}

function clearTokenCookie() {
  document.cookie = `${TOKEN_COOKIE}=; Path=/; Max-Age=0; SameSite=Lax`;
}

type AuthValue = {
  user: User | null;
  loading: boolean;
  idToken: string | null;
  isConfigured: boolean;
  logout: () => Promise<void>;
};

const AuthCtx = createContext<AuthValue>({
  user: null,
  loading: true,
  idToken: null,
  isConfigured: false,
  logout: async () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [idToken, setIdToken] = useState<string | null>(null);

  useEffect(() => {
    if (!isFirebaseConfigured) {
      setLoading(false);
      return;
    }
    const auth = getFirebaseAuth();
    const unsub = onAuthStateChanged(auth, async (u) => {
      setUser(u);
      if (u) {
        try {
          const t = await u.getIdToken();
          setIdToken(t);
          setTokenCookie(t);
        } catch {
          setIdToken(null);
          clearTokenCookie();
        }
      } else {
        setIdToken(null);
        clearTokenCookie();
      }
      setLoading(false);
    });
    return unsub;
  }, []);

  // Refresca el idToken cada 50 min para mantener la cookie viva (Firebase
  // emite tokens de 1h). Sin esto, el SSR ve cookies vencidas tras 1h.
  useEffect(() => {
    if (!user) return;
    const interval = setInterval(async () => {
      try {
        const t = await user.getIdToken(true);
        setIdToken(t);
        setTokenCookie(t);
      } catch {
        /* silencioso — el siguiente onAuthStateChanged lo capturará */
      }
    }, 50 * 60 * 1000);
    return () => clearInterval(interval);
  }, [user]);

  const logout = async () => {
    clearTokenCookie();
    if (isFirebaseConfigured) {
      await signOut(getFirebaseAuth());
    }
  };

  return (
    <AuthCtx.Provider
      value={{ user, loading, idToken, isConfigured: isFirebaseConfigured, logout }}
    >
      {children}
    </AuthCtx.Provider>
  );
}

export function useAuth(): AuthValue {
  return useContext(AuthCtx);
}
