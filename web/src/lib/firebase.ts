/**
 * Firebase Web SDK — inicialización singleton.
 *
 * Lee la config de NEXT_PUBLIC_FIREBASE_* env vars.
 * Si faltan (ej. en dev sin config), expone un cliente "noop" para que
 * la UI no crashee — pero el login no funcionará hasta que estén.
 */

import { getApps, initializeApp, type FirebaseApp } from "firebase/app";
import {
  GoogleAuthProvider,
  PhoneAuthProvider,
  getAuth,
  type Auth,
} from "firebase/auth";

const config = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

export const isFirebaseConfigured =
  !!config.apiKey && !!config.authDomain && !!config.projectId;

let _app: FirebaseApp | null = null;
let _auth: Auth | null = null;

export function getFirebaseApp(): FirebaseApp {
  if (!isFirebaseConfigured) {
    throw new Error(
      "Firebase no está configurado — define NEXT_PUBLIC_FIREBASE_API_KEY, " +
        "NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN, NEXT_PUBLIC_FIREBASE_PROJECT_ID y " +
        "NEXT_PUBLIC_FIREBASE_APP_ID en .env.local"
    );
  }
  if (_app === null) {
    _app = getApps().length ? getApps()[0]! : initializeApp(config as never);
  }
  return _app;
}

export function getFirebaseAuth(): Auth {
  if (_auth === null) {
    _auth = getAuth(getFirebaseApp());
  }
  return _auth;
}

export const googleProvider = new GoogleAuthProvider();

export { PhoneAuthProvider };
