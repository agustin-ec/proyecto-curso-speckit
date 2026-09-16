"""Test Alembic migrations environment configuration (T010)."""

from pathlib import Path
from alembic.config import Config


def test_alembic_files_exist():
    """Verify alembic configuration files exist per Constitution Article III.1."""
    root = Path(__file__).parent.parent
    assert (root / "alembic.ini").is_file(), "alembic.ini is missing"
    assert (root / "alembic" / "env.py").is_file(), "alembic/env.py is missing"
    assert (root / "alembic" / "script.py.mako").is_file(), "alembic/script.py.mako is missing"


def test_alembic_config_loads():
    """Verify Alembic Config object loads alembic.ini cleanly."""
    root = Path(__file__).parent.parent
    cfg = Config(str(root / "alembic.ini"))
    assert cfg.get_main_option("script_location") == "alembic"


def test_alembic_env_references_base_metadata():
    """Verify alembic/env.py targets Base.metadata from app.database."""
    root = Path(__file__).parent.parent
    env_content = (root / "alembic" / "env.py").read_text(encoding="utf-8")
    assert "from app.database import Base" in env_content
    assert "target_metadata = Base.metadata" in env_content
