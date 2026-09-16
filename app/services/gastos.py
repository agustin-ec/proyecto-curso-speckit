"""Expense business domain service (Constitution Article II.3, VIII.1)."""

import logging
from app.repositories import gastos as gastos_repository
from app.utils.validadores import categoria_valida

logger = logging.getLogger(__name__)

LIMITE_POR_CATEGORIA: float = 500.0


class CategoriaInvalidaError(Exception):
    """Raised when an expense category is not in the allowed domain categories."""

    pass


class LimiteExcedidoError(Exception):
    """Raised when an expense would cause total category expenses to exceed the limit."""

    pass


def _validar_gasto(descripcion: str, monto: float, categoria: str) -> None:
    """Validate expense domain rules before persistence."""
    if not descripcion or not descripcion.strip():
        raise ValueError("La descripción no puede estar vacía")
    if monto <= 0:
        raise ValueError("El monto debe ser mayor a cero")
    if not categoria_valida(categoria):
        raise CategoriaInvalidaError(f"'{categoria}' no es una categoría válida")


def registrar_gasto(
    db,
    usuario_id: int,
    descripcion: str,
    monto: float,
    categoria: str,
    repo=gastos_repository,
) -> dict:
    """Register an expense enforcing business rules and category limit.

    Exact boundary rule:
    - total_acumulado + monto <= 500.0 is permitted.
    - total_acumulado + monto > 500.0 raises LimiteExcedidoError.
    Uses default DIP parameter repo=gastos_repository (Constitution Article II.3 and VIII.1).
    """
    _validar_gasto(descripcion, monto, categoria)

    total_actual = repo.total_por_categoria(db, usuario_id, categoria)
    if total_actual + monto > LIMITE_POR_CATEGORIA:
        logger.warning(
            "Gasto rechazado por límite: usuario_id=%s categoria=%s",
            usuario_id,
            categoria,
        )
        raise LimiteExcedidoError(
            f"Este gasto supera el límite de {LIMITE_POR_CATEGORIA} para la categoría '{categoria}'"
        )

    resultado = repo.guardar(db, usuario_id, descripcion.strip(), monto, categoria)
    logger.info(
        "Gasto registrado: usuario_id=%s gasto_id=%s categoria=%s",
        usuario_id,
        resultado["id"],
        categoria,
    )
    return resultado


def listar_gastos(
    db,
    usuario_id: int,
    skip: int = 0,
    limit: int = 20,
    repo=gastos_repository,
) -> list[dict]:
    """Retrieve paginated expenses for user via repository."""
    return repo.listar(db, usuario_id, skip, limit)
