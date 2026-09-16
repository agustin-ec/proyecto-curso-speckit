"""Test .env.example configuration and environment isolation (T003)."""

from pathlib import Path


def test_env_example_exists_and_contains_required_keys():
    """Verify .env.example exists and documents all required variables."""
    root = Path(__file__).parent.parent
    env_example = root / ".env.example"
    assert env_example.is_file(), ".env.example does not exist"

    content = env_example.read_text(encoding="utf-8")
    required_keys = [
        "SECRET_KEY",
        "DATABASE_URL",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "DEMO_USER_EMAIL",
    ]
    for key in required_keys:
        assert f"{key}=" in content, f"Missing {key} in .env.example"


def test_env_file_is_gitignored():
    """Verify .env is gitignored to protect secrets per Constitution Article IV.3."""
    root = Path(__file__).parent.parent
    gitignore = root / ".gitignore"
    assert gitignore.is_file(), ".gitignore does not exist"

    content = gitignore.read_text(encoding="utf-8")
    assert ".env" in content.splitlines(), ".env must be explicitly ignored in .gitignore"
