"""Domain enumerations and category definitions."""

from enum import Enum


class CategoriaGasto(str, Enum):
    """Supported expense categories (Constitution Article II.2)."""

    COMIDA = "comida"
    TRANSPORTE = "transporte"
    ENTRETENIMIENTO = "entretenimiento"
    OTROS = "otros"


CATEGORIAS_VALIDAS: set[str] = {c.value for c in CategoriaGasto}


def is_valid_categoria(categoria: str) -> bool:
    """Check if a given category string is in the authorized categories set."""
    return categoria in CATEGORIAS_VALIDAS
