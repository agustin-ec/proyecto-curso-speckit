"""Pydantic schemas for User data transfer (Constitution Article IV.1 and V.3)."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCreate(BaseModel):
    """Schema for user registration input."""

    email: EmailStr
    password: str = Field(min_length=6, description="Contraseña del usuario (mínimo 6 caracteres)")


class UsuarioOut(BaseModel):
    """Schema for user output response. Never exposes passwords or hashes (Article IV.1)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr


class Token(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    token_type: str = "bearer"
