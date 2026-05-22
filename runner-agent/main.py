#!/usr/bin/env python3
"""CLI principal del Runner Agent."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()


def usage():
    print("""
Uso: python main.py <comando>

Comandos disponibles:
  daily       — Revisión matutina (HRV, Body Battery, recomendación del día)
  post-run    — Análisis post-entrenamiento (técnica, ACWR, resumen de sesión)
  weekly      — Revisión semanal + plan de la próxima semana
  schedule    — Inicia el scheduler para revisión matutina automática
  init        — Inicializa la base de datos y el perfil del corredor
""")


def cmd_daily():
    from agents.orchestrator import daily_morning_check
    print(daily_morning_check())


def cmd_post_run():
    from agents.orchestrator import post_run_analysis
    print(post_run_analysis())


def cmd_weekly():
    from agents.orchestrator import weekly_review
    from reports.weekly_report import format_weekly_report
    from datetime import date
    review = weekly_review()
    print(format_weekly_report(review))


def cmd_schedule():
    from scheduler.daily_check import start
    start()


def cmd_init():
    from memory.db import init_db
    from memory.runner_profile import get_profile
    init_db()
    profile = get_profile()
    if profile:
        print(f"Perfil existente: {profile['name']}")
        print("Ejecuta `python init_profile.py` si necesitas reiniciar el perfil.")
    else:
        print("Base de datos inicializada. Ejecuta `python init_profile.py` para crear el perfil.")


COMMANDS = {
    "daily": cmd_daily,
    "post-run": cmd_post_run,
    "weekly": cmd_weekly,
    "schedule": cmd_schedule,
    "init": cmd_init,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        usage()
        sys.exit(1)
    COMMANDS[sys.argv[1]]()
