"""
Application Configuration
"""
import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application Settings"""

    # Application
    APP_NAME: str = "CASUALTY UW UIUX - LLM Data Integration PoC"
    APP_VERSION: str = "0.1.0"
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://casualty_user:casualty_password@localhost:5432/casualty_db",
    )

    # LLM APIs
    CLAUDE_API_KEY: Optional[str] = os.getenv("CLAUDE_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    PREFERRED_LLM: str = os.getenv("PREFERRED_LLM", "claude")

    # Microsoft Outlook / Azure
    OUTLOOK_CLIENT_ID: Optional[str] = os.getenv("OUTLOOK_CLIENT_ID")
    OUTLOOK_CLIENT_SECRET: Optional[str] = os.getenv("OUTLOOK_CLIENT_SECRET")
    OUTLOOK_TENANT_ID: Optional[str] = os.getenv("OUTLOOK_TENANT_ID")
    OUTLOOK_REDIRECT_URI: str = os.getenv(
        "OUTLOOK_REDIRECT_URI", "http://localhost:8000/api/auth/callback"
    )

    # Server Configuration
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", 8000))
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")

    # Frontend Configuration
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # CORS Configuration
    CORS_ORIGINS: list[str] = [
        url.strip()
        for url in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    ]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = (
        os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    )
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", 100))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", 3600))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", "logs/app.log")

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get settings instance (cached)"""
    return Settings()


# Export settings
settings = get_settings()
