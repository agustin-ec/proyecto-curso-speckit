"""Expense functional persistence repository (Constitution Article I.3, VIII.1, and VIII.2).

This module contains loose functions (NOT a class) per Constitution Article VIII.1 and VIII.2.
All functions return primitive types (dict, float, list[dict]) to decouple domain logic from ORM objects.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.gasto import Gasto


def guardar(
    db: Session,
    usuario_id: int,
    descripcion: str,
    monto: float,
    categoria: str,
) -> dict:
    """Persist a new Gasto record and return a primitive dictionary."""
    gasto = Gasto(
        usuario_id=usuario_id,
        descripcion=descripcion,
        monto=monto,
        categoria=categoria,
    )
    db.add(gasto)
    db.commit()
    db.refresh(gasto)
    return {
        "id": gasto.id,
        "descripcion": gasto.descripcion,
        "monto": gasto.monto,
        "categoria": gasto.categoria,
        "usuario_id": gasto.usuario_id,
    }


def listar(
    db: Session,
    usuario_id: int,
    skip: int = 0,
    limit: int = 20,
) -> list[dict]:
    """Retrieve paginated expenses for a specific user as primitive dictionaries."""
    gastos = (
        db.query(Gasto)
        .filter(Gasto.usuario_id == usuario_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": g.id,
            "descripcion": g.descripcion,
            "monto": g.monto,
            "categoria": g.categoria,
            "usuario_id": g.usuario_id,
        }
        for g in gastos
    ]


def total_por_categoria(db: Session, usuario_id: int, categoria: str) -> float:
    """Calculate the sum of expenses for a user in a given category."""
    total = (
        db.query(func.sum(Gasto.monto))
        .filter(Gasto.usuario_id == usuario_id, Gasto.categoria == categoria)
        .scalar()
    )
    return float(total) if total is not None else 0.0
