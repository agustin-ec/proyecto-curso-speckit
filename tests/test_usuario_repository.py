"""Test Usuario repository functional implementation (T015)."""

import types
from sqlalchemy.orm import Session
from app.repositories import usuarios as usuarios_repo
from app.models.usuario import Usuario


def test_repository_is_module_not_class():
    """Verify repository is a module with loose functions per Constitution Article VIII.1 & VIII.2."""
    assert isinstance(usuarios_repo, types.ModuleType), "app.repositories.usuarios must be a module"
    assert callable(usuarios_repo.guardar)
    assert callable(usuarios_repo.obtener_por_email)


def test_guardar_and_obtener_por_email(db_session: Session):
    """Verify guardar creates and obtener_por_email retrieves the user correctly."""
    email = "test_repo@ejemplo.com"
    hashed_pwd = "$2b$12$fakerepohashforuser"

    # Save
    user = usuarios_repo.guardar(db_session, email, hashed_pwd)
    assert isinstance(user, Usuario)
    assert user.id is not None
    assert user.email == email
    assert user.hashed_password == hashed_pwd

    # Retrieve
    fetched = usuarios_repo.obtener_por_email(db_session, email)
    assert fetched is not None
    assert fetched.id == user.id
    assert fetched.email == email


def test_obtener_por_email_not_found(db_session: Session):
    """Verify obtener_por_email returns None when email does not exist."""
    assert usuarios_repo.obtener_por_email(db_session, "noexiste@ejemplo.com") is None
