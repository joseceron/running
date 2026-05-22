"""Tests de los repositorios — validan idempotencia, aislamiento y queries."""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy.orm import Session

from memory.repositories import hrv, nutrition, runner_profile, science_cache, users, weekly, weight


pytestmark = pytest.mark.integration


# ---------------------------- users ---------------------------- #


def test_ensure_idempotent(db_session: Session) -> None:
    users.ensure(db_session, "uid1")
    users.ensure(db_session, "uid1")  # no debe romper
    db_session.flush()
    assert users.get(db_session, "uid1") is not None


def test_list_active_excludes_deleted_and_unconnected(
    db_session: Session, user_a: str, user_b: str
) -> None:
    # A: conectado, B: sin conectar Garmin
    users.mark_garmin_connected(db_session, user_a)
    db_session.flush()
    active = users.list_active_user_ids(db_session)
    assert user_a in active
    assert user_b not in active

    # Borrar A: ya no aparece
    users.soft_delete(db_session, user_a)
    db_session.flush()
    assert user_a not in users.list_active_user_ids(db_session)


# ---------------------------- runner_profile ---------------------------- #


def test_upsert_creates_then_updates(db_session: Session, user_a: str) -> None:
    runner_profile.upsert(db_session, user_a, name="José", age=36, weight_kg=68.0)
    runner_profile.upsert(db_session, user_a, name="José", weight_kg=67.5)
    p = runner_profile.get_as_dict(db_session, user_a)
    assert p is not None
    assert p["age"] == 36
    assert p["weight_kg"] == 67.5


def test_isolation_two_users(db_session: Session, user_a: str, user_b: str) -> None:
    runner_profile.upsert(db_session, user_a, name="A", age=30)
    runner_profile.upsert(db_session, user_b, name="B", age=40)
    pa = runner_profile.get_as_dict(db_session, user_a)
    pb = runner_profile.get_as_dict(db_session, user_b)
    assert pa is not None and pb is not None
    assert pa["age"] == 30
    assert pb["age"] == 40


# ---------------------------- hrv ---------------------------- #


def test_hrv_log_upsert_overwrites(db_session: Session, user_a: str) -> None:
    hrv.log(db_session, user_a, date(2026, 5, 21), 50.0)
    hrv.log(db_session, user_a, date(2026, 5, 21), 55.0)
    recent = hrv.get_recent(db_session, user_a, days=5)
    assert len(recent) == 1
    assert recent[0].hrv_rmssd == 55.0


def test_hrv_baseline_requires_14_days(db_session: Session, user_a: str) -> None:
    for i in range(13):
        hrv.log(db_session, user_a, date(2026, 5, 8 + i), 55.0)
    assert hrv.get_baseline(db_session, user_a) is None

    hrv.log(db_session, user_a, date(2026, 5, 21), 55.0)
    baseline = hrv.get_baseline(db_session, user_a)
    assert baseline is not None
    assert 54.9 <= baseline <= 55.1


def test_hrv_isolation(db_session: Session, user_a: str, user_b: str) -> None:
    for i in range(14):
        hrv.log(db_session, user_a, date(2026, 5, 8 + i), 60.0)
    for i in range(14):
        hrv.log(db_session, user_b, date(2026, 5, 8 + i), 40.0)
    assert abs(hrv.get_baseline(db_session, user_a) - 60.0) < 0.01
    assert abs(hrv.get_baseline(db_session, user_b) - 40.0) < 0.01


# ---------------------------- weekly ---------------------------- #


def test_weekly_upsert_and_history(db_session: Session, user_a: str) -> None:
    weekly.upsert(db_session, user_a, week_start=date(2026, 5, 18), plan_km=30, executed_km=28)
    weekly.upsert(db_session, user_a, week_start=date(2026, 5, 18), executed_km=32)
    history = weekly.get_history(db_session, user_a, n_weeks=4)
    assert len(history) == 1
    assert history[0].executed_km == 32


# ---------------------------- nutrition ---------------------------- #


def test_nutrition_log_intake(db_session: Session, user_a: str) -> None:
    nutrition.log_intake(db_session, user_a, date(2026, 5, 21), kcal=2500, protein_g=140)
    row = nutrition.get_by_date(db_session, user_a, date(2026, 5, 21))
    assert row is not None
    assert row.kcal == 2500


# ---------------------------- weight ---------------------------- #


def test_weight_record_updates_profile(db_session: Session, user_a: str) -> None:
    runner_profile.upsert(db_session, user_a, name="José", weight_kg=68.0)
    weight.record(db_session, user_a, 67.5)
    db_session.flush()
    p = runner_profile.get_as_dict(db_session, user_a)
    assert p["weight_kg"] == 67.5
    history = weight.get_history(db_session, user_a)
    assert len(history) == 1


# ---------------------------- science_cache ---------------------------- #


def test_science_cache_roundtrip(db_session: Session) -> None:
    science_cache.put(db_session, "cadence", "scopus", [{"title": "T1"}])
    cached = science_cache.get(db_session, "cadence", "scopus")
    assert cached == [{"title": "T1"}]


def test_science_cache_stale_returns_none(db_session: Session) -> None:
    science_cache.put(db_session, "old", "scopus", [{"title": "Old"}])
    # TTL 0 días → cualquier hit es stale
    assert science_cache.get(db_session, "old", "scopus", ttl_days=0) is None
