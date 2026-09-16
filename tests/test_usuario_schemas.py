"""Test Usuario Pydantic schemas (T014)."""

import pytest
from pydantic import ValidationError
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioOut, Token


def test_usuario_create_valid():
    """Verify valid UsuarioCreate instance."""
    data = {"email": "usuario@ejemplo.com", "password": "Password123"}
    user_in = UsuarioCreate(**data)
    assert user_in.email == "usuario@ejemplo.com"
    assert user_in.password == "Password123"


def test_usuario_create_invalid_email():
    """Verify email format validation with email-validator."""
    with pytest.raises(ValidationError):
        UsuarioCreate(email="not-a-valid-email", password="Password123")


def test_usuario_create_short_password():
    """Verify minimum password length validation."""
    with pytest.raises(ValidationError):
        UsuarioCreate(email="user@test.com", password="123")


def test_usuario_out_from_orm_model():
    """Verify UsuarioOut serializes from Usuario model and excludes secret fields."""
    user_orm = Usuario(id=1, email="test@ejemplo.com", hashed_password="$2b$12$secretpasswordhash")
    user_out = UsuarioOut.model_validate(user_orm)

    assert user_out.id == 1
    assert user_out.email == "test@ejemplo.com"
    out_dict = user_out.model_dump()
    assert "password" not in out_dict
    assert "hashed_password" not in out_dict


def test_token_schema():
    """Verify Token schema fields and defaults."""
    token = Token(access_token="fake.jwt.token")
    assert token.access_token == "fake.jwt.token"
    assert token.token_type == "bearer"
