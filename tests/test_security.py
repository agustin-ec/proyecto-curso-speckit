"""Test password hashing and JWT functions (T006)."""

from datetime import timedelta
import pytest
import jwt
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)


def test_password_hashing_and_verification():
    """Verify bcrypt hashing and password verification per Constitution Article IV.1."""
    password = "MiPasswordSeguro123!"
    hashed = get_password_hash(password)

    assert hashed != password
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_create_and_decode():
    """Verify JWT creation and decoding with HS256 per Constitution Article IV.2."""
    payload = {"sub": "usuario@ejemplo.com", "usuario_id": 42}
    token = create_access_token(payload)

    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "usuario@ejemplo.com"
    assert decoded["usuario_id"] == 42
    assert "exp" in decoded


def test_jwt_expired_token_fails():
    """Verify expired token raises ExpiredSignatureError."""
    payload = {"sub": "usuario@ejemplo.com"}
    # Token expired 1 minute ago
    expired_token = create_access_token(payload, expires_delta=timedelta(minutes=-1))

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(expired_token)


def test_jwt_invalid_token_fails():
    """Verify invalid token raises PyJWTError."""
    with pytest.raises(jwt.PyJWTError):
        decode_access_token("token.invalido.falso")
