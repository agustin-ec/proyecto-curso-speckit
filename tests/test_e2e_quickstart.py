"""End-to-End validation test suite based on specs/001-control-gastos/quickstart.md.

Executes all automated and manual validation scenarios documented in Sections 4 and 5:
- Section 4: REST API flow (User registration, JWT login, expense at 200, boundary expense reaching 500,
  rejection exceeding 500 by 0.50 with 400 Bad Request, and paginated listing).
- Section 5: MCP Tools flow (Tool inspection, authenticated tool invocation for registrar_gasto and listar_gastos).
- Cross-protocol verification: REST and MCP functional parity and unified data state.
"""

from unittest.mock import patch
from starlette.testclient import TestClient

from app.database import get_db
from app.main import app
from app.mcp.server import mcp
from app.mcp.tools import gastos as mcp_gastos
from mcp.server.auth.provider import AccessToken


def test_quickstart_e2e_flow(db_session):
    """Execute complete end-to-end validation scenario documented in quickstart.md."""

    # Ensure app uses the isolated test db_session
    app.dependency_overrides[get_db] = lambda: db_session

    with TestClient(app, raise_server_exceptions=False) as client:
        # =========================================================================
        # Section 4: Validación Manual Paso a Paso (API REST)
        # =========================================================================

        # 4.2: Crear un nuevo usuario
        payload_usuario = {
            "email": "test@ejemplo.com",
            "password": "PasswordSeguro123",
        }
        res_registro = client.post("/usuarios/", json=payload_usuario)
        assert res_registro.status_code == 201, f"Error en registro: {res_registro.text}"
        data_registro = res_registro.json()
        assert data_registro["email"] == "test@ejemplo.com"
        assert "id" in data_registro
        user_id = data_registro["id"]

        # 4.3: Obtener el token JWT
        login_data = {
            "username": "test@ejemplo.com",
            "password": "PasswordSeguro123",
        }
        res_token = client.post("/usuarios/token", data=login_data)
        assert res_token.status_code == 200, f"Error en login: {res_token.text}"
        data_token = res_token.json()
        assert "access_token" in data_token
        assert data_token.get("token_type") == "bearer"
        token = data_token["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 4.4: Registrar un gasto válido (acumulado: 200.0)
        gasto_1 = {
            "descripcion": "Supermercado",
            "monto": 200.0,
            "categoria": "comida",
        }
        res_gasto_1 = client.post("/gastos/", json=gasto_1, headers=headers)
        assert res_gasto_1.status_code == 201, f"Error en gasto 1: {res_gasto_1.text}"
        data_g1 = res_gasto_1.json()
        assert data_g1["descripcion"] == "Supermercado"
        assert data_g1["monto"] == 200.0
        assert data_g1["categoria"] == "comida"
        assert data_g1["usuario_id"] == user_id

        # 4.5: Registrar un gasto en el límite exacto (acumulado previo 200 + 300 = 500.0)
        gasto_2 = {
            "descripcion": "Cena familiar",
            "monto": 300.0,
            "categoria": "comida",
        }
        res_gasto_2 = client.post("/gastos/", json=gasto_2, headers=headers)
        assert res_gasto_2.status_code == 201, f"Error en gasto 2: {res_gasto_2.text}"
        data_g2 = res_gasto_2.json()
        assert data_g2["descripcion"] == "Cena familiar"
        assert data_g2["monto"] == 300.0
        assert data_g2["categoria"] == "comida"
        assert data_g2["usuario_id"] == user_id

        # 4.6: Intentar registrar un gasto que exceda el límite acumulado (500.0 + 0.50 = 500.50)
        gasto_excedido = {
            "descripcion": "Café",
            "monto": 0.50,
            "categoria": "comida",
        }
        res_excedido = client.post("/gastos/", json=gasto_excedido, headers=headers)
        assert res_excedido.status_code == 400, f"Debería fallar con 400: {res_excedido.text}"
        data_err = res_excedido.json()
        assert "detail" in data_err
        assert "500.0" in data_err["detail"]
        assert "comida" in data_err["detail"]

        # 4.7: Consultar la lista paginada de gastos propios
        res_lista = client.get("/gastos/?skip=0&limit=10", headers=headers)
        assert res_lista.status_code == 200, f"Error en listado: {res_lista.text}"
        lista_gastos = res_lista.json()
        assert isinstance(lista_gastos, list)
        assert len(lista_gastos) == 2
        descripciones = [g["descripcion"] for g in lista_gastos]
        assert "Supermercado" in descripciones
        assert "Cena familiar" in descripciones

        # =========================================================================
        # Section 5: Validación de Tools MCP
        # =========================================================================

        # 5.1: Inspección de herramientas
        tools = mcp._tool_manager.list_tools()
        tool_names = [t.name for t in tools]
        assert "registrar_gasto" in tool_names
        assert "listar_gastos" in tool_names

        # Setup MCP auth context with the user's JWT token
        user_access_token = AccessToken(
            token=token,
            client_id="test@ejemplo.com",
            scopes=["gastos"],
            subject="test@ejemplo.com",
        )

        with patch("app.mcp.tools.gastos.SessionLocal", return_value=db_session):
            with patch("app.mcp.tools.gastos.get_access_token", return_value=user_access_token):
                # 5.2: Invocación de registrar_gasto (Taxi, 15.0, transporte)
                res_mcp_gasto = mcp_gastos.registrar_gasto(
                    descripcion="Taxi",
                    monto=15.0,
                    categoria="transporte",
                )
                assert isinstance(res_mcp_gasto, dict)
                assert "error" not in res_mcp_gasto
                assert res_mcp_gasto["descripcion"] == "Taxi"
                assert res_mcp_gasto["monto"] == 15.0
                assert res_mcp_gasto["categoria"] == "transporte"
                assert res_mcp_gasto["usuario_id"] == user_id

                # 5.3: Invocación de listar_gastos (skip=0, limit=20)
                mcp_lista = mcp_gastos.listar_gastos(skip=0, limit=20)
                assert isinstance(mcp_lista, list)
                # Should contain the 2 REST expenses + 1 MCP expense = 3 expenses
                assert len(mcp_lista) == 3
                mcp_descripciones = [g["descripcion"] for g in mcp_lista]
                assert "Supermercado" in mcp_descripciones
                assert "Cena familiar" in mcp_descripciones
                assert "Taxi" in mcp_descripciones

        # 5.4: Paridad cross-protocol: REST API can now also see all 3 expenses
        res_lista_updated = client.get("/gastos/?skip=0&limit=10", headers=headers)
        assert res_lista_updated.status_code == 200
        assert len(res_lista_updated.json()) == 3

    # Clean up overrides
    app.dependency_overrides.clear()
