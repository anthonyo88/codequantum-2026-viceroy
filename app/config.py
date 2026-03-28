from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://f1admin:f1password@localhost:5432/f1recruiting"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # OpenAI
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-large"
    openai_chat_model: str = "gpt-4o"

    # Auth
    secret_key: str = "dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # App
    environment: str = "development"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # RAG
    rag_context_token_budget: int = 4000
    rag_top_k_chunks: int = 15

    @model_validator(mode="after")
    def sync_celery_redis_urls(self) -> "Settings":
        default_broker = "redis://localhost:6379/0"
        default_backend = "redis://localhost:6379/1"

        if self.celery_broker_url == default_broker and self.redis_url != default_broker:
            self.celery_broker_url = self.redis_url

        if self.celery_result_backend == default_backend:
            if self.redis_url.endswith("/0"):
                self.celery_result_backend = f"{self.redis_url[:-2]}/1"
            elif self.redis_url != default_broker:
                self.celery_result_backend = self.redis_url

        return self


settings = Settings()
