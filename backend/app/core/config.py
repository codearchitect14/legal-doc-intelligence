from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "local"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5435/legal_doc_intelligence"
    redis_url: str = "redis://localhost:6381/0"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    groq_api_key: str = ""
    gemini_api_key: str = ""
    llm_preferred_provider: str = "groq"
    groq_model: str = "openai/gpt-oss-20b"
    gemini_model: str = "gemini-1.5-flash"
    max_tokens_per_case: int = 8000
    llm_max_retries: int = 2
    llm_provider_cooldown_seconds: int = 120

    object_storage_path: str = "./data/uploads"
    max_upload_size_mb: int = 25
    embedding_model_name: str = "all-MiniLM-L6-v2"


@lru_cache
def get_settings() -> Settings:
    return Settings()
