"""Integration test suite for expense persistence and business logic (Constitution Article VII.4 and VIII.1).

Verifies database transactions against real SQLite in-memory.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.repositories import usuarios as usuarios_repository
from app.repositories import gastos as gastos_repository
from app.services import gastos as gastos_service


@pytest.fixture
def db_session():
    """Isolated in-memory SQLite database session for integration tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


def test_registrar_y_listar_gasto_integracion(db_session):
    usuario = usuarios_repository.guardar(db_session, "test@ejemplo.com", "hash-de-prueba")

    gastos_service.registrar_gasto(
        db_session, usuario.id, "Almuerzo", 12.50, "comida", repo=gastos_repository
    )

    gastos = gastos_service.listar_gastos(db_session, usuario.id, repo=gastos_repository)

    assert len(gastos) == 1
    assert gastos[0]["descripcion"] == "Almuerzo"


def test_limite_por_categoria_integracion(db_session):
    usuario = usuarios_repository.guardar(db_session, "otro@ejemplo.com", "hash-de-prueba")

    gastos_service.registrar_gasto(db_session, usuario.id, "Gasto 1", 490.0, "comida", repo=gastos_repository)

    with pytest.raises(gastos_service.LimiteExcedidoError):
        gastos_service.registrar_gasto(db_session, usuario.id, "Gasto 2", 50.0, "comida", repo=gastos_repository)


def test_listar_gastos_paginacion_integracion(db_session):
    usuario = usuarios_repository.guardar(db_session, "paginacion@ejemplo.com", "hash-de-prueba")
    for i in range(5):
        gastos_service.registrar_gasto(
            db_session, usuario.id, f"Gasto {i}", 10.0, "comida", repo=gastos_repository
        )

    gastos_pagina = gastos_service.listar_gastos(
        db_session, usuario.id, skip=2, limit=2, repo=gastos_repository
    )
    assert len(gastos_pagina) == 2
    assert gastos_pagina[0]["descripcion"] == "Gasto 2"
    assert gastos_pagina[1]["descripcion"] == "Gasto 3"


def test_listar_gastos_aislamiento_usuarios_integracion(db_session):
    u1 = usuarios_repository.guardar(db_session, "aisla1@ejemplo.com", "hash-de-prueba")
    u2 = usuarios_repository.guardar(db_session, "aisla2@ejemplo.com", "hash-de-prueba")

    gastos_service.registrar_gasto(db_session, u1.id, "Gasto de U1", 20.0, "comida", repo=gastos_repository)
    gastos_service.registrar_gasto(db_session, u2.id, "Gasto de U2", 35.0, "transporte", repo=gastos_repository)

    gastos_u1 = gastos_service.listar_gastos(db_session, u1.id, repo=gastos_repository)
    assert len(gastos_u1) == 1
    assert gastos_u1[0]["descripcion"] == "Gasto de U1"
    assert gastos_u1[0]["usuario_id"] == u1.id

    gastos_u2 = gastos_service.listar_gastos(db_session, u2.id, repo=gastos_repository)
    assert len(gastos_u2) == 1
    assert gastos_u2[0]["descripcion"] == "Gasto de U2"
    assert gastos_u2[0]["usuario_id"] == u2.id

