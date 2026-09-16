"""MCP server initialization and ASGI application export (Constitution Article VI)."""

from mcp.server.fastmcp import FastMCP
from mcp.server.auth.settings import AuthSettings
from app.core.config import settings
from app.mcp.auth import JWTTokenVerifier
from app.mcp.tools import gastos

mcp = FastMCP(
    "gastos-server",
    streamable_http_path="/",
    token_verifier=JWTTokenVerifier(),
    auth=AuthSettings(
        issuer_url=settings.mcp_issuer_url,
        resource_server_url=settings.mcp_resource_url,
        required_scopes=["gastos"],
        validate_token_resource=False,
    ),
)
gastos.register(mcp)

if __name__ == "__main__":
    mcp.run()
