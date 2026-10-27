
from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application
    app_name: str = "HR Policy Assistant API"
    app_version: str = "1.0.0"
    environment: str = "development"

    # Groq
    groq_api_key: SecretStr
    groq_model: str = "openai/gpt-oss-20b"

    # Qdrant Cloud
    qdrant_url: str
    qdrant_api_key: SecretStr
    qdrant_collection: str = "hr_policy_chunks"

    # Hugging Face embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Retrieval
    retrieval_top_k: int = Field(default=5, ge=1, le=20)
    retrieval_score_threshold: float = Field(
        default=0.45,
        ge=0.0,
        le=1.0,
    )

    # API
    api_prefix: str = "/api"
    request_timeout_seconds: int = Field(default=30, ge=5, le=120)

    # CORS: comma-separated origins in the environment variable
    cors_origins: str = "https://hr-guide.streamlit.app,http://localhost:8501"

    @property
    def allowed_origins(self) -> list[str]:
        """Convert configured CORS origins into a list."""
        return [
            origin.strip().rstrip("/")
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached application settings instance."""
    return Settings()
