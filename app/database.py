"""Database connection, SQLAlchemy engine, session factory, and get_db dependency."""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.core.config import settings

# Conditional connect_args only for SQLite (Constitution Article III.2)
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Provide a transactional database session per request (Constitution Article VIII.1)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
