"""MCP Bearer token authentication provider (Constitution Article VI.4)."""

from mcp.server.auth.provider import AccessToken, TokenVerifier
from app.core.security import decode_access_token


class JWTTokenVerifier(TokenVerifier):
    """Verifies MCP Bearer tokens reusing standard application JWT authentication (Article VI.4)."""

    async def verify_token(self, token: str) -> AccessToken | None:
        """Verify signed JWT token and return AccessToken with gastos scope or None."""
        try:
            payload = decode_access_token(token)
        except Exception:
            return None

        email = payload.get("sub")
        if not email:
            return None

        return AccessToken(
            token=token,
            client_id=email,
            scopes=["gastos"],
            expires_at=payload.get("exp"),
            subject=email,
        )
