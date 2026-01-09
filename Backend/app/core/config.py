"""
Core configuration module for CampusShield AI.
Centralized settings management with environment variable support.
"""
from pathlib import Path
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# BASE_DIR points to Backend folder, PROJ_ROOT points to project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJ_ROOT = BASE_DIR.parent

# Load .env from PROJECT ROOT FIRST (highest priority)
ROOT_ENV_FILE = PROJ_ROOT / ".env"
BACKEND_ENV_FILE = BASE_DIR / ".env"

if ROOT_ENV_FILE.exists():
    load_dotenv(ROOT_ENV_FILE)
elif BACKEND_ENV_FILE.exists():
    load_dotenv(BACKEND_ENV_FILE)

# Determine which .env file to use for pydantic
ENV_FILE = ROOT_ENV_FILE if ROOT_ENV_FILE.exists() else (BACKEND_ENV_FILE if BACKEND_ENV_FILE.exists() else None)


class Settings(BaseSettings):
    """
    Application settings loaded from environment or .env file.
    Supports both CS_* prefixed and standard env variables.
    """
    
    model_config = ConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    app_name: str = "CampusShield AI Backend"
    version: str = "2.0.0"

    # Debug & Environment
    debug: bool = Field(default=False, env="CS_DEBUG")
    secret_key: str = Field(default="dev-secret-key-change-in-production", env="CS_SECRET_KEY")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Security
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

    # LLM Configuration
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.1-8b-instant", env="GROQ_MODEL")
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", env="GEMINI_MODEL")

    # RAG Configuration
    vector_store_type: str = Field(default="faiss", env="VECTOR_STORE_TYPE")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    vector_store_path: str = Field(default="./vector_store", env="VECTOR_STORE_PATH")
    
    # Feature Flags
    enable_llm: bool = Field(default=True, env="ENABLE_LLM")
    enable_rag: bool = Field(default=False, env="ENABLE_RAG")
    enable_websocket: bool = Field(default=True, env="ENABLE_WEBSOCKET")
    
    # Pinecone (optional)
    pinecone_api_key: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    pinecone_environment: Optional[str] = Field(default=None, env="PINECONE_ENVIRONMENT")
    pinecone_index_name: Optional[str] = Field(default=None, env="PINECONE_INDEX_NAME")

    # Weaviate (optional)
    weaviate_url: Optional[str] = Field(default=None, env="WEAVIATE_URL")
    weaviate_api_key: Optional[str] = Field(default=None, env="WEAVIATE_API_KEY")

    # ML Configuration
    ml_model_path: str = Field(default="./models", env="ML_MODEL_PATH")
    risk_prediction_enabled: bool = Field(default=True, env="RISK_PREDICTION_ENABLED")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")

    # Video Streaming (Demo Feature)
    enable_video_stream: bool = Field(default=True, env="ENABLE_VIDEO_STREAM")
    video_stream_fps: int = Field(default=30, env="VIDEO_STREAM_FPS")
    video_stream_resolution: str = Field(default="1280x720", env="VIDEO_STREAM_RESOLUTION")

    # Backend URL (for external access)
    backend_url: str = Field(default="http://localhost:8000", env="BACKEND_URL")
    frontend_url: str = Field(default="http://localhost:3000", env="FRONTEND_URL")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, v):
        """Parse debug mode from various environment variables."""
        truthy = ("1", "true", "yes", "on", "dev", "development")

        if isinstance(v, bool):
            if "CS_DEBUG" in os.environ:
                s = str(os.environ.get("CS_DEBUG", "")).strip().lower()
                return s in truthy
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

    def validate_startup(self) -> dict[str, bool]:
        """
        Validate all critical settings on startup.
        Returns dict of check results for logging.
        """
        checks = {}

        # Database check
        checks["database"] = bool(self.database_url)

        # LLM check
        if self.enable_llm:
            checks["llm_provider"] = bool(self.llm_provider)
            if self.llm_provider == "openai":
                checks["openai_api_key"] = bool(self.openai_api_key)
            checks["llm_model"] = bool(self.openai_model)
        else:
            checks["llm_disabled"] = True

        # Vector store check
        if self.enable_rag:
            checks["vector_store"] = bool(self.vector_store_type)
        else:
            checks["rag_disabled"] = True

        # CORS check
        checks["cors"] = len(self.cors_origins) > 0

        return checks

    @property
    def is_production(self) -> bool:
        return not self.debug


# Singleton instance
settings = Settings()

