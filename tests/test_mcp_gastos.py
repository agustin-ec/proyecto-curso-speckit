"""Test suite for MCP tools and authentication (Constitution Article VI and VII.6)."""

import pytest
from unittest.mock import patch
from app.core.config import settings
from app.core.security import create_access_token
from app.mcp.auth import JWTTokenVerifier
from app.mcp.tools import gastos as mcp_gastos
from app.repositories import usuarios as usuarios_repo
from mcp.server.auth.provider import AccessToken


@pytest.mark.anyio
async def test_jwt_token_verifier_valid_token(db_session):
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


def test_mcp_registrar_gasto_demo_user_success(db_session):
    """Verify registrar_gasto tool falls back to demo user and succeeds (stdio mode)."""
    # Override SessionLocal to use db_session in mcp_gastos
    with patch("app.mcp.tools.gastos.SessionLocal", return_value=db_session):
        # Clear any active auth token to simulate stdio
        with patch("app.mcp.tools.gastos.get_access_token", return_value=None):
            resultado = mcp_gastos.registrar_gasto("Almuerzo MCP", 18.50, "comida")

            assert "error" not in resultado
            assert resultado["descripcion"] == "Almuerzo MCP"
            assert resultado["monto"] == 18.50
            assert resultado["categoria"] == "comida"
            assert "usuario_id" in resultado


def test_mcp_registrar_gasto_categoria_invalida_retorna_dict_error(db_session):
    """Verify invalid category returns structured error dict without raising (Article VI.3)."""
    with patch("app.mcp.tools.gastos.SessionLocal", return_value=db_session):
        with patch("app.mcp.tools.gastos.get_access_token", return_value=None):
            resultado = mcp_gastos.registrar_gasto("Cine", 25.0, "categoria_inexistente")

            assert isinstance(resultado, dict)
            assert "error" in resultado
            assert "válida" in resultado["error"].lower() or "categoria" in resultado["error"].lower()


def test_mcp_registrar_gasto_limite_excedido_retorna_dict_error(db_session):
    """Verify exceeding 500 limit returns structured error dict without raising (Article VI.3)."""
    with patch("app.mcp.tools.gastos.SessionLocal", return_value=db_session):
        with patch("app.mcp.tools.gastos.get_access_token", return_value=None):
            # First expense
            mcp_gastos.registrar_gasto("Gasto grande", 490.0, "comida")

            # Second expense exceeding 500
            resultado = mcp_gastos.registrar_gasto("Gasto extra", 20.0, "comida")

            assert isinstance(resultado, dict)
            assert "error" in resultado
            assert "límite" in resultado["error"].lower() or "limite" in resultado["error"].lower()


def test_mcp_listar_gastos_success(db_session):
    """Verify listar_gastos tool returns user's expenses."""
    with patch("app.mcp.tools.gastos.SessionLocal", return_value=db_session):
        with patch("app.mcp.tools.gastos.get_access_token", return_value=None):
            mcp_gastos.registrar_gasto("Gasto 1", 10.0, "comida")
            mcp_gastos.registrar_gasto("Gasto 2", 15.0, "transporte")

            gastos = mcp_gastos.listar_gastos()
            assert isinstance(gastos, list)
            assert len(gastos) >= 2


def test_mcp_token_valido_usuario_inexistente_rechaza_sin_usar_demo(db_session):
    """Verify that when a valid token is provided but the user does not exist in the DB,
    the operation is rejected with an error and NEVER falls back to demo user (Constitution Article VI.4)."""
    fake_token = AccessToken(
        token="valid.jwt.token",
        client_id="noexiste@ejemplo.com",
        scopes=["gastos"],
        subject="noexiste@ejemplo.com",
    )

    with patch("app.mcp.tools.gastos.SessionLocal", return_value=db_session):
        with patch("app.mcp.tools.gastos.get_access_token", return_value=fake_token):
            resultado = mcp_gastos.registrar_gasto("Prueba", 10.0, "comida")

            assert isinstance(resultado, dict)
            assert "error" in resultado
            assert "no corresponde a ningún usuario" in resultado["error"].lower()

            # Ensure no expenses were created for the demo user
            demo_user = usuarios_repo.obtener_por_email(db_session, settings.DEMO_USER_EMAIL)
            if demo_user is not None:
                assert len(demo_user.gastos) == 0



def test_mcp_server_registers_expected_tools():
    """Verify MCP server has registered registrar_gasto and listar_gastos tools."""
    from app.mcp.server import mcp

    # Check tools registration
    tools = mcp._tool_manager.list_tools()
    tool_names = [t.name for t in tools]
    assert "registrar_gasto" in tool_names
    assert "listar_gastos" in tool_names
