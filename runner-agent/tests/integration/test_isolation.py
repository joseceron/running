"""Tests end-to-end de aislamiento multi-tenant.

Validan que ninguna operación de un usuario puede leer o modificar datos de otro.
"""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy.orm import Session

from memory.repositories import hrv, nutrition, runner_profile, users, weekly


pytestmark = pytest.mark.integration


def test_two_users_independent_data(
    db_session: Session, user_a: str, user_b: str
) -> None:
    # Insertar mucho dato en A
    runner_profile.upsert(db_session, user_a, name="José", age=36, weight_kg=68)
    for i in range(14):
        hrv.log(db_session, user_a, date(2026, 5, 8 + i), 55.0)
    weekly.upsert(db_session, user_a, week_start=date(2026, 5, 18), executed_km=30)
    nutrition.log_intake(db_session, user_a, date(2026, 5, 21), kcal=2500)

    # B no debe ver nada
    assert runner_profile.get(db_session, user_b) is None
    assert hrv.get_recent(db_session, user_b, days=20) == []
    assert weekly.get_history(db_session, user_b) == []
    assert nutrition.get_by_date(db_session, user_b, date(2026, 5, 21)) is None

    # A sí ve lo suyo
    assert runner_profile.get(db_session, user_a) is not None
    assert len(hrv.get_recent(db_session, user_a, days=20)) == 14


def test_cascade_delete_purges_all_user_data(
    db_session: Session, user_a: str
) -> None:
    runner_profile.upsert(db_session, user_a, name="José", age=36)
    hrv.log(db_session, user_a, date(2026, 5, 21), 55.0)
    weekly.upsert(db_session, user_a, week_start=date(2026, 5, 18), executed_km=30)
    nutrition.log_intake(db_session, user_a, date(2026, 5, 21), kcal=2500)

    users.hard_delete(db_session, user_a)
    db_session.flush()

    assert runner_profile.get(db_session, user_a) is None
    assert hrv.get_recent(db_session, user_a, days=20) == []
    assert weekly.get_history(db_session, user_a) == []
    assert nutrition.get_by_date(db_session, user_a, date(2026, 5, 21)) is None
