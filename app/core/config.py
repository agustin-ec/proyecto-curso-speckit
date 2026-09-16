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

    # Logging settings
    LOG_LEVEL: str = "INFO"

    # MCP demo user fallback for stdio transport and server URLs (Constitution Article VI.4)
    DEMO_USER_EMAIL: str = "demo@gastos.local"
    MCP_DEMO_EMAIL: str = "demo@gastos.local"
    MCP_DEMO_PASSWORD: str = "demo1234"
    MCP_ISSUER_URL: str = "http://127.0.0.1:8000"
    MCP_RESOURCE_URL: str = "http://127.0.0.1:8000/mcp"

    @property
    def mcp_demo_email(self) -> str:
        return self.MCP_DEMO_EMAIL

    @property
    def mcp_demo_password(self) -> str:
        return self.MCP_DEMO_PASSWORD

    @property
    def mcp_issuer_url(self) -> str:
        return self.MCP_ISSUER_URL

    @property
    def mcp_resource_url(self) -> str:
        return self.MCP_RESOURCE_URL

    @property
    def log_level(self) -> str:
        return self.LOG_LEVEL


settings = Settings()
