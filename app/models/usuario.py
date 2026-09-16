"""Usuario SQLAlchemy declarative model."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Usuario(Base):
    """Usuario entity representing a registered system user (Constitution Article VIII.1)."""

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    gastos = relationship("Gasto", back_populates="usuario", cascade="all, delete-orphan")

    def __init__(
        self,
        email: str | None = None,
        hashed_password: str | None = None,
        id: int | None = None,
        **kwargs,
    ):
        """Initialize Usuario with support for positional or keyword parameters per Article VIII.1."""
        super().__init__(**kwargs)
        if id is not None:
            self.id = id
        if email is not None:
            self.email = email
        if hashed_password is not None:
            self.hashed_password = hashed_password

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, email={self.email})>"
