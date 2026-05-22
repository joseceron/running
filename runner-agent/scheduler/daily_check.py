"""Scheduler APScheduler para el ciclo matutino diario."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

load_dotenv()

from agents.orchestrator import daily_morning_check

scheduler = BlockingScheduler()


def run_daily():
    print("\n" + "=" * 60)
    report = daily_morning_check()
    print(report)
    print("=" * 60 + "\n")


def start():
    check_time = os.environ.get("MORNING_CHECK_TIME", "07:00")
    hour, minute = check_time.split(":")
    scheduler.add_job(run_daily, "cron", hour=int(hour), minute=int(minute))
    print(f"Scheduler iniciado — revisión matutina a las {check_time}")
    scheduler.start()
