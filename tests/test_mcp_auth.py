"""Unit tests for app/mcp/auth.py (Constitution Article VI.4)."""

import pytest
from app.core.security import create_access_token
from app.mcp.auth import JWTTokenVerifier


@pytest.mark.anyio
async def test_jwt_token_verifier_valid_token():
    """Verify JWTTokenVerifier validates signed JWT and returns AccessToken."""
    verifier = JWTTokenVerifier()
    token = create_access_token(data={"sub": "mcp_user@ejemplo.com"})

    access_token = await verifier.verify_token(token)
    assert access_token is not None
    assert access_token.subject == "mcp_user@ejemplo.com"
    assert "gastos" in access_token.scopes


@pytest.mark.anyio
async def test_jwt_token_verifier_invalid_token():
    """Verify JWTTokenVerifier returns None for invalid token."""
    verifier = JWTTokenVerifier()
    access_token = await verifier.verify_token("invalid.token.string")
    assert access_token is None


@pytest.mark.anyio
async def test_jwt_token_verifier_missing_sub():
    """Verify JWTTokenVerifier returns None when sub claim is missing."""
    verifier = JWTTokenVerifier()
    token = create_access_token(data={"other": "claim"})
    access_token = await verifier.verify_token(token)
    assert access_token is None
