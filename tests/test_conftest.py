"""Test conftest shared fixtures and database isolation (T011)."""

from sqlalchemy import text
from sqlalchemy.orm import Session


def test_db_session_fixture_is_functional(db_session: Session):
    """Verify db_session fixture provides an active in-memory SQLite connection."""
    assert isinstance(db_session, Session)
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_db_session_isolation_part_1(db_session: Session):
    """Verify tables created in memory exist within this test."""
    db_session.execute(text("CREATE TABLE isolation_test (id INTEGER PRIMARY KEY, name TEXT)"))
    db_session.execute(text("INSERT INTO isolation_test (name) VALUES ('item1')"))
    db_session.commit()

    count = db_session.execute(text("SELECT COUNT(*) FROM isolation_test")).scalar()
    assert count == 1


def test_db_session_isolation_part_2(db_session: Session):
    """Verify table created in part_1 does not persist into this clean test."""
    try:
        db_session.execute(text("SELECT COUNT(*) FROM isolation_test"))
        table_persisted = True
    except Exception:
        db_session.rollback()
        table_persisted = False

    assert table_persisted is False, "Database session was not properly isolated between tests"
