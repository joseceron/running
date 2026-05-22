"""Inicializa el perfil del corredor con datos reales de José."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from memory.db import init_db
from memory.runner_profile import create_profile, add_injury, set_goal

init_db()

profile = create_profile(
    name="José Luis Cerón",
    age=30,
    height_cm=170,
    weight_kg=68,
    max_hr=190,
    resting_hr=48,
)
print(f"Perfil creado: {profile['name']}")

add_injury(
    injury_type="desgarro sóleo",
    occurred_on="2024-01-15",
    severity="grave",
    recovery_notes="Desgarro 49% del sóleo por mala técnica y sobrecarga. Recuperación ~4 meses.",
)
print("Lesión registrada: desgarro sóleo")

set_goal(
    event="Media maratón",
    goal_date="2026-10-01",
    goal_time_secs=6600,  # 1h50min
)
print("Meta registrada: Media maratón sub 1:50")
print("\nPerfil de José inicializado correctamente.")
