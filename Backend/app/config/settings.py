from pathlib import Path
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Application settings with strict validation and startup checks.
    All critical settings checked on startup.
    """
    
    model_config = ConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "CampusShield AI Backend"
    version: str = "2.0.0"
    debug: bool = Field(default=False, env="CS_DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    secret_key: str = Field(default="dev-secret-key-change-in-production", env="CS_SECRET_KEY")
    
    # Authentication
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # Database
    database_url: str = Field(
        default="sqlite:///./backend.db",
        env="DATABASE_URL"
    )

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
        ],
        env="CS_CORS_ORIGINS",
    )

    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # LLM Configuration
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY") 
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=1024, ge=256, le=4096, env="LLM_MAX_TOKENS")
    llm_timeout: int = Field(default=30, env="LLM_TIMEOUT")

    # Vector Store
    vector_store_type: str = Field(default="faiss", env="VECTOR_STORE_TYPE")
    vector_store_path: str = Field(default="./vector_store", env="VECTOR_STORE_PATH")

    # Feature Flags
    enable_llm: bool = Field(default=True, env="ENABLE_LLM")
    enable_rag: bool = Field(default=False, env="ENABLE_RAG")
    enable_websocket: bool = Field(default=True, env="ENABLE_WEBSOCKET")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v or [
            "http://localhost:3000",
            "http://localhost:5173",
        ]

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid:
            return "INFO"
        return v.upper()

    def validate_startup(self) -> dict[str, bool]:
        """
        Validate all critical settings on startup.
        Returns dict of check results for logging.
        """
        checks = {}

        # Database check
        checks["database"] = bool(self.database_url)
        if not checks["database"]:
            logger.error("DATABASE_URL not configured")

        # LLM check
        if self.enable_llm:
            checks["llm_provider"] = bool(self.llm_provider)
            if self.llm_provider == "openai":
                checks["openai_api_key"] = bool(self.openai_api_key)
                if not checks["openai_api_key"]:
                    logger.warning("OPENAI_API_KEY not set - LLM will be disabled")
                    self.enable_llm = False
            checks["llm_timeout"] = self.llm_timeout > 0
        else:
            checks["llm_provider"] = False
            logger.info("LLM disabled via ENABLE_LLM=False")

        # Vector store check
        if self.enable_rag:
            checks["vector_store"] = bool(self.vector_store_type)
        else:
            checks["vector_store"] = False

        # CORS check
        checks["cors"] = len(self.cors_origins) > 0
        if not checks["cors"]:
            logger.warning("No CORS origins configured - defaulting to localhost")

        return checks

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
        """Determine production mode.

        Priority: explicit `IS_PRODUCTION` env var -> boolean; else inverse of `debug`.
        This avoids a Pydantic Field/property name collision.
        """
        env_val = os.getenv("IS_PRODUCTION")
        if env_val is not None:
            return str(env_val).strip().lower() in ("1", "true", "yes", "on")
        return not self.debug


settings = Settings()
