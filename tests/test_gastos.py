"""Unit test suite for expense business logic (Constitution Article VII.2 and VIII.1).

Uses RepositorioFalso in memory (NO unittest.mock) per Constitution Article VII.2.
"""

import pytest
from app.services import gastos as gastos_service
from app.services.gastos import LimiteExcedidoError, CategoriaInvalidaError


class RepositorioFalso:
    """Test double: mismo contrato que app/repositories/gastos.py, sin persistencia real."""

    def __init__(self, total_inicial_por_categoria: float = 0.0):
        self._gastos: list[dict] = []
        self._total_inicial = total_inicial_por_categoria

    def guardar(self, db, usuario_id: int, descripcion: str, monto: float, categoria: str) -> dict:
        gasto = {
            "id": len(self._gastos) + 1,
            "descripcion": descripcion,
            "monto": monto,
            "categoria": categoria,
            "usuario_id": usuario_id,
        }
        self._gastos.append(gasto)
        return gasto

    def listar(self, db, usuario_id: int, skip: int = 0, limit: int = 20) -> list[dict]:
        filtrados = [g for g in self._gastos if g["usuario_id"] == usuario_id]
        return filtrados[skip : skip + limit]

    def total_por_categoria(self, db, usuario_id: int, categoria: str) -> float:
        return self._total_inicial + sum(g["monto"] for g in self._gastos if g["categoria"] == categoria)


def test_registrar_gasto_exitoso():
    repo = RepositorioFalso()

    resultado = gastos_service.registrar_gasto(None, 1, "Almuerzo", 12.50, "comida", repo=repo)

    assert resultado["descripcion"] == "Almuerzo"
    assert repo.listar(None, 1) == [resultado]


def test_registrar_gasto_monto_invalido_lanza_error():
    with pytest.raises(ValueError):
        gastos_service.registrar_gasto(None, 1, "Café", -5.0, "comida", repo=RepositorioFalso())


def test_registrar_gasto_categoria_invalida_lanza_error():
    with pytest.raises(CategoriaInvalidaError):
        gastos_service.registrar_gasto(None, 1, "Cine", 20.0, "categoria-inventada", repo=RepositorioFalso())


def test_registrar_gasto_excede_limite_categoria_lanza_error():
    repo = RepositorioFalso(total_inicial_por_categoria=490.0)

    with pytest.raises(LimiteExcedidoError):
        gastos_service.registrar_gasto(None, 1, "Cena cara", 50.0, "comida", repo=repo)


def test_registrar_gasto_limite_exacto_500_permitido():
    repo = RepositorioFalso(total_inicial_por_categoria=450.0)
    resultado = gastos_service.registrar_gasto(None, 1, "Cena limite", 50.0, "comida", repo=repo)
    assert resultado["monto"] == 50.0


def test_registrar_gasto_limite_superado_por_un_centavo():
    repo = RepositorioFalso(total_inicial_por_categoria=500.0)
    with pytest.raises(LimiteExcedidoError):
        gastos_service.registrar_gasto(None, 1, "Chicle", 0.01, "comida", repo=repo)


def test_registrar_gasto_descripcion_vacia_lanza_error():
    with pytest.raises(ValueError):
        gastos_service.registrar_gasto(None, 1, "   ", 10.0, "comida", repo=RepositorioFalso())


def test_listar_gastos_paginacion():
    repo = RepositorioFalso()
    for i in range(5):
        gastos_service.registrar_gasto(None, 1, f"Gasto {i}", 10.0, "comida", repo=repo)

    pagina = gastos_service.listar_gastos(None, 1, skip=2, limit=2, repo=repo)
    assert len(pagina) == 2
    assert pagina[0]["descripcion"] == "Gasto 2"
    assert pagina[1]["descripcion"] == "Gasto 3"


def test_listar_gastos_aislamiento_usuarios():
    repo = RepositorioFalso()
    gastos_service.registrar_gasto(None, 1, "Gasto User 1", 15.0, "comida", repo=repo)
    gastos_service.registrar_gasto(None, 2, "Gasto User 2", 20.0, "comida", repo=repo)

    gastos_u1 = gastos_service.listar_gastos(None, 1, repo=repo)
    assert len(gastos_u1) == 1
    assert gastos_u1[0]["descripcion"] == "Gasto User 1"

    gastos_u2 = gastos_service.listar_gastos(None, 2, repo=repo)
    assert len(gastos_u2) == 1
    assert gastos_u2[0]["descripcion"] == "Gasto User 2"


def test_listar_gastos_dip_signature_contract():
    """Verify listar_gastos defaults repo to app.repositories.gastos module (Article II.3 & VIII.1)."""
    import inspect
    from app.repositories import gastos as expected_repo

    sig = inspect.signature(gastos_service.listar_gastos)
    assert "repo" in sig.parameters
    assert sig.parameters["repo"].default is expected_repo


