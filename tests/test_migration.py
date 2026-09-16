"""Test Alembic migrations (T037)."""

import os
import tempfile
import pytest
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_and_downgrade():
    """Verify alembic upgrade head creates tables and downgrade base drops them."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db_path = tmp.name

    try:
        db_url = f"sqlite:///{tmp_db_path}"

        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)

        # Run migration upgrade to head
        command.upgrade(alembic_cfg, "head")

        engine = create_engine(db_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        assert "usuarios" in tables
        assert "gastos" in tables
        assert "alembic_version" in tables

        # Verify columns in usuarios
        user_cols = [c["name"] for c in inspector.get_columns("usuarios")]
        assert "id" in user_cols
        assert "email" in user_cols
        assert "hashed_password" in user_cols

        # Verify columns in gastos
        gasto_cols = [c["name"] for c in inspector.get_columns("gastos")]
        assert "id" in gasto_cols
        assert "descripcion" in gasto_cols
        assert "monto" in gasto_cols
        assert "categoria" in gasto_cols
        assert "usuario_id" in gasto_cols

        engine.dispose()

        # Run migration downgrade to base
        command.downgrade(alembic_cfg, "base")

        engine2 = create_engine(db_url)
        inspector2 = inspect(engine2)
        tables_after = inspector2.get_table_names()
        assert "usuarios" not in tables_after
        assert "gastos" not in tables_after
        engine2.dispose()

    finally:
        if os.path.exists(tmp_db_path):
            os.remove(tmp_db_path)
