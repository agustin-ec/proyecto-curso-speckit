"""Test domain enumerations and category validations (T008)."""

from app.models.enums import CategoriaGasto, CATEGORIAS_VALIDAS, is_valid_categoria


def test_categoria_gasto_enum_values():
    """Verify exact 4 valid categories per spec and Constitution Article II.2."""
    expected = {"comida", "transporte", "entretenimiento", "otros"}
    actual = {c.value for c in CategoriaGasto}
    assert actual == expected, f"Expected {expected}, got {actual}"
    assert CATEGORIAS_VALIDAS == expected


def test_is_valid_categoria():
    """Verify authorization helper identifies valid vs invalid categories."""
    assert is_valid_categoria("comida") is True
    assert is_valid_categoria("transporte") is True
    assert is_valid_categoria("entretenimiento") is True
    assert is_valid_categoria("otros") is True

    # Invalid categories (Case 2 from spec.md)
    assert is_valid_categoria("viajes") is False
    assert is_valid_categoria("salud") is False
    assert is_valid_categoria("") is False
    assert is_valid_categoria("COMIDA") is False
