from pathlib import Path
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings
from typing import List
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Application settings loaded from environment or .env file.
    Supports both CS_* prefixed and standard env variables.
    """
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Allow extra fields without raising errors
    )

    app_name: str = "CampusShield AI Backend"

    debug: bool = Field(default=False, env="CS_DEBUG")
    secret_key: str = Field(default="dev-secret-key-change-in-production", env="CS_SECRET_KEY")

    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    database_url: str = Field(
        default="sqlite:///./backend.db",
        env="DATABASE_URL"
    )

    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
        ],
        env="CS_CORS_ORIGINS",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, v):
        """
        Allow multiple common environment variables to control debug mode across platforms.
        - Accept `CS_DEBUG` (existing), or standard vars like `ENV`, `ENVIRONMENT`, `PYTHON_ENV`.
        - Treat values like 'development', 'dev', '1', 'true', 'yes', 'on' as truthy.
        """
        truthy = ("1", "true", "yes", "on", "dev", "development")

        # If Pydantic provided a boolean (from default), still attempt to detect
        # explicit env vars that may indicate development mode.
        if isinstance(v, bool):
            # If CS_DEBUG explicitly present in env, honor it
            if "CS_DEBUG" in os.environ:
                s = str(os.environ.get("CS_DEBUG", "")).strip().lower()
                return s in truthy

            # Fall back to common environment indicators
            alt = os.environ.get("ENV") or os.environ.get("ENVIRONMENT") or os.environ.get("PYTHON_ENV")
            if alt:
                return str(alt).strip().lower() in truthy

            return v

        if v is None:
            alt = os.environ.get("CS_DEBUG") or os.environ.get("ENV") or os.environ.get("ENVIRONMENT") or os.environ.get("PYTHON_ENV")
            if alt is None:
                return False
            return str(alt).strip().lower() in truthy

        if isinstance(v, str):
            return v.strip().lower() in truthy

        return bool(v)

    @property
    def is_production(self) -> bool:
        return not self.debug


settings = Settings()
