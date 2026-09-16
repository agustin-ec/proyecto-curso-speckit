"""Test Usuario SQLAlchemy model and constraints (T013)."""

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.usuario import Usuario


def test_usuario_constructor_contract():
    """Verify constructor accepts (id=, email=, hashed_password=) per Constitution Article VIII.1."""
    u = Usuario(id=10, email="test@ejemplo.com", hashed_password="fakehashbcrypt")
    assert u.id == 10
    assert u.email == "test@ejemplo.com"
    assert u.hashed_password == "fakehashbcrypt"


def test_usuario_persistence_in_db(db_session):
    """Verify Usuario can be inserted and queried from database."""
    u = Usuario(email="guardado@ejemplo.com", hashed_password="$2b$12$hashseguro")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    assert u.id is not None
    assert u.email == "guardado@ejemplo.com"

    # Query back
    recovered = db_session.query(Usuario).filter_by(email="guardado@ejemplo.com").first()
    assert recovered is not None
    assert recovered.id == u.id


def test_usuario_email_unique_constraint(db_session):
    """Verify duplicate email violates database uniqueness constraint."""
    u1 = Usuario(email="repetido@ejemplo.com", hashed_password="hash1")
    db_session.add(u1)
    db_session.commit()

    u2 = Usuario(email="repetido@ejemplo.com", hashed_password="hash2")
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
