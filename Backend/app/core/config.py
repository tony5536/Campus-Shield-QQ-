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

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file from Backend directory
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    # Try loading from project root as fallback
    load_dotenv(BASE_DIR.parent / ".env")


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

    @property
    def is_production(self) -> bool:
        return not self.debug


# Singleton instance
settings = Settings()

