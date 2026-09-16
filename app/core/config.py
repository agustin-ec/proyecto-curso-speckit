"""Application settings and environment configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Security & JWT settings (Constitution Article IV.2 and IV.3)
    SECRET_KEY: str = "default-insecure-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Persistence settings (Constitution Article III.2)
    DATABASE_URL: str = "sqlite:///./gastos.db"

    # MCP demo user fallback for stdio transport (Constitution Article VI.4)
    DEMO_USER_EMAIL: str = "demo@gastos.local"


settings = Settings()
