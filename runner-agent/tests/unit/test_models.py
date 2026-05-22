"""Tests del schema ORM — verifican constraints, FKs y aislamiento básico."""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from memory.models import HRVLog, NutritionLog, RunnerProfile, ScienceCache, User


pytestmark = pytest.mark.integration


def test_user_created_with_defaults(db_session: Session, user_a: str) -> None:
    user = db_session.get(User, user_a)
    assert user is not None
    assert user.user_id == user_a
    assert user.created_at is not None
    assert user.deleted_at is None
    assert user.garmin_connected_at is None


def test_hrv_unique_per_user_date(db_session: Session, user_a: str) -> None:
    db_session.add(HRVLog(user_id=user_a, date=date(2026, 5, 21), hrv_rmssd=55.0))
    db_session.flush()
    db_session.add(HRVLog(user_id=user_a, date=date(2026, 5, 21), hrv_rmssd=60.0))
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_hrv_same_date_distinct_users_ok(
    db_session: Session, user_a: str, user_b: str
) -> None:
    db_session.add(HRVLog(user_id=user_a, date=date(2026, 5, 21), hrv_rmssd=55.0))
    db_session.add(HRVLog(user_id=user_b, date=date(2026, 5, 21), hrv_rmssd=62.0))
    db_session.flush()  # no debe romper


def test_runner_profile_is_one_to_one(db_session: Session, user_a: str) -> None:
    db_session.add(RunnerProfile(user_id=user_a, name="José"))
    db_session.flush()
    db_session.add(RunnerProfile(user_id=user_a, name="Otro"))
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_cascade_delete_user_removes_profile(db_session: Session, user_a: str) -> None:
    db_session.add(RunnerProfile(user_id=user_a, name="José"))
    db_session.flush()
    db_session.delete(db_session.get(User, user_a))
    db_session.flush()
    assert db_session.get(RunnerProfile, user_a) is None


def test_science_cache_unique_query_source(db_session: Session) -> None:
    db_session.add(
        ScienceCache(query="cadence injury", source="scopus", results_json="[]")
    )
    db_session.flush()
    db_session.add(
        ScienceCache(query="cadence injury", source="scopus", results_json="[1]")
    )
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_nutrition_log_unique_per_user_date(db_session: Session, user_a: str) -> None:
    db_session.add(NutritionLog(user_id=user_a, date=date(2026, 5, 20), kcal=2500))
    db_session.flush()
    db_session.add(NutritionLog(user_id=user_a, date=date(2026, 5, 20), kcal=2600))
    with pytest.raises(IntegrityError):
        db_session.flush()
