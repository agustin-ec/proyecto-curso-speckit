"""Tests for app/dependencies.py (Constitution Article IV.4 and VIII.1)."""

from datetime import timedelta
import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash
from app.dependencies import get_current_user
from app.models.usuario import Usuario
from app.repositories import usuarios as usuarios_repo


def test_get_current_user_success(db_session: Session):
    # Setup test user
    user = usuarios_repo.guardar(db_session, email="dep_test@example.com", hashed_password=get_password_hash("secret123"))
    token = create_access_token(data={"sub": user.email})

    retrieved_user = get_current_user(token=token, db=db_session)
    assert retrieved_user.id == user.id
    assert retrieved_user.email == user.email


def test_get_current_user_invalid_token(db_session: Session):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="invalid.token.here", db=db_session)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Credenciales inválidas" in exc_info.value.detail


def test_get_current_user_expired_token(db_session: Session):
    token = create_access_token(data={"sub": "user@example.com"}, expires_delta=timedelta(seconds=-10))
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db_session)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Credenciales inválidas" in exc_info.value.detail


def test_get_current_user_missing_sub(db_session: Session):
    token = create_access_token(data={"other_claim": "value"})
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db_session)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Credenciales inválidas" in exc_info.value.detail


def test_get_current_user_user_not_found(db_session: Session):
    token = create_access_token(data={"sub": "nonexistent@example.com"})
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db_session)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Credenciales inválidas" in exc_info.value.detail
