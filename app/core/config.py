"""Application Configuration Module."""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """System settings validated via environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "ARC PDS"
    API_V1_STR: str = "/api/v1"
    SERVER_DOMAIN: str = Field(
        default="localhost:8000",
        description="Public server domain for W3C did:web resolution",
    )

    # Cryptographic secrets
    # Ensure SECRET_KEY contains at least 32 bytes of cryptographic entropy in production
    SECRET_KEY: str = Field(
        default="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
        description="HMAC secret key for JWT signing",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./pds.db",
        description="Async database connection string",
    )

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
    ]

    # Authorized ARC PDS Client Applications
    ALLOWED_CLIENT_IDS: List[str] = [
        "chirp",
        "burrow",
        "scratch",
        "scout",
        "echo",
        "flock",
    ]


settings = Settings()
