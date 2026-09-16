"""Test database module and session lifecycle (T007)."""

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base, get_db


def test_database_symbols_exist():
    """Verify contractual symbols required by Constitution Article VIII.1."""
    assert engine is not None
    assert SessionLocal is not None
    assert Base is not None
    assert callable(get_db)


def test_get_db_session_lifecycle():
    """Verify get_db yields an active SQLAlchemy Session and closes it."""
    db_generator = get_db()
    db = next(db_generator)

    try:
        assert isinstance(db, Session)
        result = db.execute(text("SELECT 1")).scalar()
        assert result == 1
    finally:
        # Exhaust generator to trigger finally: db.close()
        try:
            next(db_generator)
        except StopIteration:
            pass

    # Session is closed, inactive or detached
    assert db.is_active is False or not db.in_transaction()
