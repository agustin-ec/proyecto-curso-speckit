"""Pydantic schemas for Expense data transfer (Constitution Article V.3)."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GastoCreate(BaseModel):
    """Schema for expense creation input."""

    descripcion: str = Field(min_length=1, description="Descripción del gasto")
    monto: float = Field(gt=0, description="Monto del gasto (debe ser estrictamente mayor a 0)")
    categoria: str = Field(min_length=1, description="Categoría del gasto")

    @field_validator("descripcion")
    @classmethod
    def validate_descripcion(cls, v: str) -> str:
        """Ensure description is not empty or whitespace only."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("La descripción no puede estar vacía")
        return cleaned


class GastoOut(BaseModel):
    """Schema for expense output response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    descripcion: str
    monto: float
    categoria: str
    usuario_id: int


# Alias for compatibility with Sessions 6-8 reference code
GastoResponse = GastoOut
