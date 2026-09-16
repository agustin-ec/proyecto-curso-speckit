"""Test application configuration and settings (T005)."""

import os
from app.core.config import Settings, settings


def test_default_settings_values():
    """Verify default settings values for local development and testing."""
    assert settings.JWT_ALGORITHM == "HS256"
    assert isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int)
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0, "Expiration must be positive and finite"
    assert settings.DATABASE_URL.startswith("sqlite") or settings.DATABASE_URL.startswith("postgresql")
    assert settings.DEMO_USER_EMAIL == "demo@gastos.local"


def test_settings_custom_env_override(monkeypatch):
    """Verify settings can be loaded from custom environment variables."""
    monkeypatch.setenv("SECRET_KEY", "custom-super-secret-key")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("DEMO_USER_EMAIL", "custom_demo@gastos.test")

    custom_settings = Settings()
    assert custom_settings.SECRET_KEY == "custom-super-secret-key"
    assert custom_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 120
    assert custom_settings.DATABASE_URL == "sqlite:///:memory:"
    assert custom_settings.DEMO_USER_EMAIL == "custom_demo@gastos.test"
