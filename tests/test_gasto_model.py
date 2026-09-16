"""Unit tests for Gasto SQLAlchemy model (T021)."""

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.usuario import Usuario
from app.models.gasto import Gasto


def test_gasto_constructor_contract():
    """Verify Gasto constructor supports fields per Constitution Article VIII.1."""
    g = Gasto(id=1, descripcion="Almuerzo", monto=15.50, categoria="comida", usuario_id=2)
    assert g.id == 1
    assert g.descripcion == "Almuerzo"
    assert g.monto == 15.50
    assert g.categoria == "comida"
    assert g.usuario_id == 2


def test_gasto_persistence_and_relationship(db_session):
    """Verify Gasto persistence and bidirectional relationship with Usuario."""
    usuario = Usuario(email="gastousuario@ejemplo.com", hashed_password="fakehashbcrypt")
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    gasto = Gasto(descripcion="Cena", monto=45.0, categoria="comida", usuario_id=usuario.id)
    db_session.add(gasto)
    db_session.commit()
    db_session.refresh(gasto)

    assert gasto.id is not None
    assert gasto.usuario.email == "gastousuario@ejemplo.com"
    assert len(usuario.gastos) == 1
    assert usuario.gastos[0].id == gasto.id


def test_gasto_foreign_key_required(db_session):
    """Verify Gasto cannot be created without a valid non-null usuario_id."""
    gasto = Gasto(descripcion="Huérfano", monto=10.0, categoria="otros", usuario_id=None)
    db_session.add(gasto)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
