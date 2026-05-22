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
        } catch {
          setIdToken(null);
        }
      } else {
        setIdToken(null);
      }
      setLoading(false);
    });
    return unsub;
  }, []);

  const logout = async () => {
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
