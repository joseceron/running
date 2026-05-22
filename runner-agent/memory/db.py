"""Capa de persistencia SQLite."""
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def get_connection() -> sqlite3.Connection:
    db_url = os.environ.get("DATABASE_URL", "sqlite:///runner_agent.db")
    db_path = db_url.replace("sqlite:///", "")
    if not Path(db_path).is_absolute():
        db_path = str(Path(__file__).parent.parent / db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS runner_profile (
            id              INTEGER PRIMARY KEY,
            name            TEXT NOT NULL,
            age             INTEGER,
            height_cm       REAL,
            weight_kg       REAL,
            max_hr          INTEGER,
            resting_hr      INTEGER,
            goal_event      TEXT,
            goal_date       TEXT,
            goal_time_secs  INTEGER,
            system_start    TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS body_weight_history (
            id          INTEGER PRIMARY KEY,
            weight_kg   REAL NOT NULL,
            recorded_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS hrv_log (
            id          INTEGER PRIMARY KEY,
            date        TEXT NOT NULL UNIQUE,
            hrv_rmssd   REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS weekly_history (
            id                  INTEGER PRIMARY KEY,
            week_start          TEXT NOT NULL UNIQUE,
            plan_km             REAL,
            executed_km         REAL,
            avg_hrv             REAL,
            avg_body_battery    REAL,
            acwr                REAL,
            agent_notes         TEXT
        );

        CREATE TABLE IF NOT EXISTS nutrition_log (
            id          INTEGER PRIMARY KEY,
            date        TEXT NOT NULL UNIQUE,
            kcal        REAL,
            protein_g   REAL,
            status      TEXT DEFAULT 'logged'
        );

        CREATE TABLE IF NOT EXISTS science_cache (
            id          INTEGER PRIMARY KEY,
            query       TEXT NOT NULL,
            source      TEXT NOT NULL,
            results_json TEXT NOT NULL,
            cached_at   TEXT NOT NULL,
            UNIQUE(query, source)
        );
    """)
    conn.commit()
    conn.close()
