"""Unit tests for Gasto Pydantic schemas (T022)."""

import pytest
from pydantic import ValidationError
from app.models.gasto import Gasto
from app.schemas.gasto import GastoCreate, GastoOut, GastoResponse


def test_gasto_create_valid():
    """Verify valid GastoCreate schema."""
    g = GastoCreate(descripcion="Almuerzo de negocios", monto=25.50, categoria="comida")
    assert g.descripcion == "Almuerzo de negocios"
    assert g.monto == 25.50
    assert g.categoria == "comida"


def test_gasto_create_negative_or_zero_monto():
    """Verify GastoCreate rejects monto <= 0."""
    with pytest.raises(ValidationError):
        GastoCreate(descripcion="Test", monto=0.0, categoria="comida")

    with pytest.raises(ValidationError):
        GastoCreate(descripcion="Test", monto=-15.0, categoria="comida")


def test_gasto_create_empty_or_whitespace_descripcion():
    """Verify GastoCreate rejects empty or whitespace-only description."""
    with pytest.raises(ValidationError):
        GastoCreate(descripcion="", monto=10.0, categoria="comida")

    with pytest.raises(ValidationError):
        GastoCreate(descripcion="   ", monto=10.0, categoria="comida")


def test_gasto_out_serialization_from_orm():
    """Verify GastoOut and GastoResponse deserialize from ORM model."""
    orm_gasto = Gasto(id=1, descripcion="Cena", monto=30.0, categoria="comida", usuario_id=5)
    out = GastoOut.model_validate(orm_gasto)
    assert out.id == 1
    assert out.descripcion == "Cena"
    assert out.monto == 30.0
    assert out.categoria == "comida"
    assert out.usuario_id == 5

    resp = GastoResponse.model_validate(orm_gasto)
    assert resp.id == 1
    assert resp.descripcion == "Cena"
