"""
Inyecta la sesión activa del browser de Garmin Connect para evitar el rate limit.

En lugar de hacer login programático (que Garmin limita agresivamente), este
script reutiliza los tokens JWT que ya tiene el browser.

Pasos:
1. Abre connect.garmin.com en Chrome/Safari
2. DevTools → Application → Cookies → connect.garmin.com
3. Copia el valor de: JWT_FGP  (o _ga_session / GARMIN-SSO-GUID)
4. Ejecuta: .venv/bin/python inject_browser_session.py

Alternativa más fácil: copia el header 'Authorization' de cualquier
request XHR en DevTools → Network.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

TOKENSTORE = str(Path(__file__).parent / ".garmin_tokens")

print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  INYECTAR SESIÓN DE BROWSER → evitar rate limit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pasos en Chrome/Safari (ya tienes connect.garmin.com abierto):

  1. F12 → pestaña "Network"
  2. Recarga la página (F5)
  3. Haz click en cualquier request a "connect.garmin.com"
  4. Busca el header: "Authorization: Bearer <TOKEN>"
  5. Copia el token (la parte larga después de "Bearer ")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

access_token = input("Pega el Bearer token aquí: ").strip()
if access_token.lower().startswith("bearer "):
    access_token = access_token[7:].strip()

if len(access_token) < 50:
    print("❌ Token muy corto — asegúrate de copiar el token completo.")
    sys.exit(1)

Path(TOKENSTORE).mkdir(exist_ok=True)

# garth espera un archivo oauth2_token.json en el tokenstore
token_data = {
    "access_token": access_token,
    "token_type": "Bearer",
    "refresh_token": "",
    "expires_in": 3600,
    "scope": "CONNECT"
}

token_path = Path(TOKENSTORE) / "oauth2_token.json"
with open(token_path, "w") as f:
    json.dump(token_data, f, indent=2)

print(f"\n✅ Token guardado en {token_path}")
print("Prueba ahora: .venv/bin/python main.py daily")
