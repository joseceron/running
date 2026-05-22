"""Copia las variables necesarias del .env de referencia al .env local."""
import shutil
import os

REFERENCE_ENV = "/Users/jose.ceron/Documents/emira/.env"
LOCAL_ENV = os.path.join(os.path.dirname(__file__), ".env")

REQUIRED_VARS = [
    "GARMIN_EMAIL",
    "GARMIN_PASSWORD",
    "SCOPUS_API_KEY",
    "WOS_API_KEY",
    "ANTHROPIC_API_KEY",
]

DEFAULTS = {
    "DATABASE_URL": "sqlite:///runner_agent.db",
    "MORNING_CHECK_TIME": "07:00",
}

if os.path.exists(LOCAL_ENV):
    print(f".env ya existe en {LOCAL_ENV}")
else:
    lines = []
    if os.path.exists(REFERENCE_ENV):
        with open(REFERENCE_ENV) as f:
            ref_lines = f.readlines()
        ref_vars = {}
        for line in ref_lines:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, _, val = line.partition("=")
                ref_vars[key.strip()] = val.strip()
        for var in REQUIRED_VARS:
            val = ref_vars.get(var, "")
            lines.append(f"{var}={val}\n")
    else:
        print(f"Archivo de referencia no encontrado: {REFERENCE_ENV}")
        for var in REQUIRED_VARS:
            lines.append(f"{var}=\n")

    for key, val in DEFAULTS.items():
        lines.append(f"{key}={val}\n")

    with open(LOCAL_ENV, "w") as f:
        f.writelines(lines)
    print(f".env creado en {LOCAL_ENV}")
