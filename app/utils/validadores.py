"""Domain validation utilities (OCP compliant per Constitution Article I.4)."""

# OCP: agregar una categoría nueva = agregar un valor aquí.
# La función de abajo nunca cambia.
CATEGORIAS_PERMITIDAS = {"comida", "transporte", "entretenimiento", "otros"}


def categoria_valida(categoria: str) -> bool:
    """Validate if a category is among the allowed categories."""
    return categoria in CATEGORIAS_PERMITIDAS
