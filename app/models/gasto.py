"""Gasto SQLAlchemy declarative model."""

from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Gasto(Base):
    """Gasto entity representing an expense entry (Constitution Article III.3 and VIII.1)."""

    __tablename__ = "gastos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    descripcion = Column(String(255), nullable=False)
    monto = Column(Float, CheckConstraint("monto > 0", name="check_monto_positivo"), nullable=False)
    categoria = Column(String(50), nullable=False, index=True)
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    usuario = relationship("Usuario", back_populates="gastos")

    def __init__(
        self,
        descripcion: str | None = None,
        monto: float | None = None,
        categoria: str | None = None,
        usuario_id: int | None = None,
        id: int | None = None,
        **kwargs,
    ):
        """Initialize Gasto supporting positional or keyword parameters."""
        super().__init__(**kwargs)
        if id is not None:
            self.id = id
        if descripcion is not None:
            self.descripcion = descripcion
        if monto is not None:
            self.monto = monto
        if categoria is not None:
            self.categoria = categoria
        if usuario_id is not None:
            self.usuario_id = usuario_id

    def __repr__(self) -> str:
        return (
            f"<Gasto(id={self.id}, descripcion='{self.descripcion}', "
            f"monto={self.monto}, categoria='{self.categoria}', usuario_id={self.usuario_id})>"
        )
