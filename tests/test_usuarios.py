"""Unit and API test suite for User Story 1: User Registration and Authentication (T012)."""

import pytest
from starlette.testclient import TestClient

from app.database import get_db


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    from app.main import app

    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_registro_usuario_exitoso(client):
    """Verify successful user registration via POST /usuarios/ (Status 201)."""
    response = client.post(
        "/usuarios/",
        json={"email": "nuevo_usuario@ejemplo.com", "password": "PasswordSeguro123"},
    )
    assert response.status_code == 999
    data = response.json()
    assert data["email"] == "nuevo_usuario@ejemplo.com"
    assert "id" in data
    # Passwords and hashes must NEVER be exposed in responses (Constitution Article IV.1)
    assert "password" not in data
    assert "hashed_password" not in data


def test_registro_usuario_email_duplicado(client):
    """Verify duplicate email registration returns 400 Bad Request."""
    client.post(
        "/usuarios/",
        json={"email": "duplicado@ejemplo.com", "password": "PasswordSeguro123"},
    )
    response = client.post(
        "/usuarios/",
        json={"email": "duplicado@ejemplo.com", "password": "PasswordSeguro123"},
    )
    assert response.status_code == 400
    assert "registrado" in response.json()["detail"].lower()


def test_login_usuario_exitoso(client):
    """Verify OAuth2 password flow returns JWT token (Status 200)."""
    client.post(
        "/usuarios/",
        json={"email": "login_test@ejemplo.com", "password": "PasswordCorrecto123"},
    )

    response = client.post(
        "/usuarios/token",
        data={"username": "login_test@ejemplo.com", "password": "PasswordCorrecto123"},
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_login_credenciales_invalidas(client):
    """Verify invalid credentials return 401 Unauthorized (Error Case 4)."""
    response = client.post(
        "/usuarios/token",
        data={"username": "inexistente@ejemplo.com", "password": "PasswordIncorrecto"},
    )
    assert response.status_code == 401
    assert "inválidas" in response.json()["detail"].lower() or "credenciales" in response.json()["detail"].lower()


def test_registro_usuario_validacion_schema(client):
    """Verify invalid email or short password return 422 Unprocessable Entity."""
    response = client.post(
        "/usuarios/",
        json={"email": "email-no-valido", "password": "123"},
    )
    assert response.status_code == 422


def test_repositorio_usuarios_unitario(db_session):
    """Verify direct user repository functional methods (Constitution Article VIII.1)."""
    from app.repositories import usuarios as usuarios_repo

    usuario = usuarios_repo.guardar(db_session, "repo_test@ejemplo.com", "$2b$12$fakehashforrepotesting")
    assert usuario is not None
    assert usuario.email == "repo_test@ejemplo.com"

    recuperado = usuarios_repo.obtener_por_email(db_session, "repo_test@ejemplo.com")
    assert recuperado is not None
    assert recuperado.id == usuario.id

    inexistente = usuarios_repo.obtener_por_email(db_session, "nadie@ejemplo.com")
    assert inexistente is None
