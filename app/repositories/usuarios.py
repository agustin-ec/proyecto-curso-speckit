"""Usuario functional persistence repository (Constitution Article I.3 and VIII.1).

This module contains loose functions (NOT a class) per Constitution Article VIII.1 and VIII.2.
"""

from sqlalchemy.orm import Session
from app.models.usuario import Usuario


def obtener_por_email(db: Session, email: str) -> Usuario | None:
    """Retrieve a Usuario by email, or None if not found."""
    return db.query(Usuario).filter(Usuario.email == email).first()


def guardar(db: Session, email: str, hashed_password: str) -> Usuario:
    """Persist a new Usuario record with pre-hashed password and return the model."""
    usuario = Usuario(email=email, hashed_password=hashed_password)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
