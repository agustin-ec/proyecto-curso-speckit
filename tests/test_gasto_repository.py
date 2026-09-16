"""Unit tests for functional expense repository (Constitution Article VIII.1 and VIII.2)."""

import inspect
from app.repositories import gastos as gastos_repo
from app.models.usuario import Usuario


def test_gastos_repository_is_module_not_class():
    """Verify repository is implemented as functions in a module, not a class (Article VIII.2)."""
    assert inspect.ismodule(gastos_repo)
    assert inspect.isfunction(gastos_repo.guardar)
    assert inspect.isfunction(gastos_repo.listar)
    assert inspect.isfunction(gastos_repo.total_por_categoria)


def test_guardar_gasto_returns_primitive_dict(db_session):
    """Verify guardar persists gasto and returns a plain Python dict."""
    usuario = Usuario(email="repotest@ejemplo.com", hashed_password="fakehashbcrypt")
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    resultado = gastos_repo.guardar(
        db_session,
        usuario_id=usuario.id,
        descripcion="Almuerzo",
        monto=12.50,
        categoria="comida",
    )

    assert isinstance(resultado, dict)
    assert resultado["id"] is not None
    assert resultado["descripcion"] == "Almuerzo"
    assert resultado["monto"] == 12.50
    assert resultado["categoria"] == "comida"
    assert resultado["usuario_id"] == usuario.id


def test_total_por_categoria_aggregation_and_isolation(db_session):
    """Verify total_por_categoria sums correctly and isolates users."""
    u1 = Usuario(email="u1@ejemplo.com", hashed_password="pwd")
    u2 = Usuario(email="u2@ejemplo.com", hashed_password="pwd")
    db_session.add_all([u1, u2])
    db_session.commit()

    # Initial total should be 0.0
    assert gastos_repo.total_por_categoria(db_session, u1.id, "comida") == 0.0

    gastos_repo.guardar(db_session, u1.id, "Desayuno", 10.0, "comida")
    gastos_repo.guardar(db_session, u1.id, "Almuerzo", 15.0, "comida")
    gastos_repo.guardar(db_session, u1.id, "Taxi", 8.0, "transporte")
    gastos_repo.guardar(db_session, u2.id, "Cena U2", 50.0, "comida")

    # u1 comida should be 25.0
    assert gastos_repo.total_por_categoria(db_session, u1.id, "comida") == 25.0
    # u1 transporte should be 8.0
    assert gastos_repo.total_por_categoria(db_session, u1.id, "transporte") == 8.0
    # u2 comida should be 50.0 (user isolation)
    assert gastos_repo.total_por_categoria(db_session, u2.id, "comida") == 50.0


def test_listar_gastos_pagination_and_isolation(db_session):
    """Verify listar respects pagination and user isolation."""
    u = Usuario(email="listar@ejemplo.com", hashed_password="pwd")
    db_session.add(u)
    db_session.commit()

    for i in range(5):
        gastos_repo.guardar(db_session, u.id, f"Gasto {i}", float(10 + i), "comida")

    todos = gastos_repo.listar(db_session, u.id, skip=0, limit=10)
    assert len(todos) == 5
    assert all(isinstance(g, dict) for g in todos)

    paginados = gastos_repo.listar(db_session, u.id, skip=2, limit=2)
    assert len(paginados) == 2
    assert paginados[0]["descripcion"] == "Gasto 2"
    assert paginados[1]["descripcion"] == "Gasto 3"
