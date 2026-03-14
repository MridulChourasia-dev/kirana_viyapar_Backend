"""
Application configuration and environment variables
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Viyapar - Billing & Inventory System"
    PROJECT_DESCRIPTION: str = "A comprehensive SaaS solution for small businesses"
    VERSION: str = "1.0.0"

    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "viyapar"
    DATABASE_ECHO: bool = False

    # Redis Configuration (Optional)
    REDIS_URL: Optional[str] = None
    ENABLE_CACHING: bool = False

    # Security Configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Server Configuration
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
    ]

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Construct async database URL for SQLAlchemy"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
