"""API test suite for expense endpoints (Constitution Article VII.5 and VIII.1).

Verifies POST /gastos/ endpoint behavior using dependency_overrides for get_db,
get_gastos_repo, and get_current_user.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_current_user, get_gastos_repo
from app.database import get_db
from app.models.usuario import Usuario
from tests.test_gastos import RepositorioFalso

USUARIO_DE_PRUEBA = Usuario(id=1, email="test@ejemplo.com", hashed_password="no-importa")


@pytest.fixture
def client():
    """FastAPI TestClient with default overrides for db and current user."""
    app.dependency_overrides[get_db] = lambda: None
    app.dependency_overrides[get_current_user] = lambda: USUARIO_DE_PRUEBA
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_crear_gasto_con_repo_falso(client):
    app.dependency_overrides[get_gastos_repo] = lambda: RepositorioFalso()

    response = client.post(
        "/gastos/", json={"descripcion": "Almuerzo", "monto": 12.50, "categoria": "comida"}
    )

    assert response.status_code == 201
    assert response.json()["descripcion"] == "Almuerzo"
    assert response.json()["usuario_id"] == 1


def test_crear_gasto_categoria_invalida_retorna_400(client):
    app.dependency_overrides[get_gastos_repo] = lambda: RepositorioFalso()

    response = client.post(
        "/gastos/", json={"descripcion": "Cine", "monto": 20.0, "categoria": "categoria-invalida"}
    )

    assert response.status_code == 400
    assert "inválida" in response.json()["detail"].lower() or "categoria" in response.json()["detail"].lower()


def test_crear_gasto_limite_excedido_retorna_400(client):
    app.dependency_overrides[get_gastos_repo] = lambda: RepositorioFalso(total_inicial_por_categoria=490.0)

    response = client.post(
        "/gastos/", json={"descripcion": "Cena cara", "monto": 50.0, "categoria": "comida"}
    )

    assert response.status_code == 400
    assert "límite" in response.json()["detail"].lower() or "limite" in response.json()["detail"].lower()


def test_crear_gasto_monto_negativo_retorna_422(client):
    app.dependency_overrides[get_gastos_repo] = lambda: RepositorioFalso()

    response = client.post(
        "/gastos/", json={"descripcion": "Invalido", "monto": -10.0, "categoria": "comida"}
    )

    assert response.status_code == 422


def test_crear_gasto_sin_autenticacion():
    # Create client without get_current_user override
    app.dependency_overrides.clear()
    with TestClient(app, raise_server_exceptions=False) as unauth_client:
        response = unauth_client.post(
            "/gastos/", json={"descripcion": "Test", "monto": 10.0, "categoria": "comida"}
        )
        assert response.status_code == 401


class RepositorioRoto:
    """Simula un fallo inesperado del repositorio (ej. la DB se cae a mitad de la request)."""

    def total_por_categoria(self, db, usuario_id, categoria):
        raise RuntimeError("la base de datos no responde")


def test_error_no_controlado_devuelve_500_sin_stacktrace(client):
    app.dependency_overrides[get_gastos_repo] = lambda: RepositorioRoto()

    response = client.post(
        "/gastos/", json={"descripcion": "Falla", "monto": 10.0, "categoria": "comida"}
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Error interno del servidor"}
