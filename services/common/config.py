from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "kb"
    redis_url: str = "redis://localhost:6379/0"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "http://localhost:3001"
    jwt_secret: str = "dev-secret"
    router_url: str = "http://localhost:8100"

    embed_model: str = "BAAI/bge-m3"
    rerank_model: str = "BAAI/bge-reranker-v2-m3"
    opus_model: str = "gpt-4o"
    haiku_model: str = "gpt-4o-mini"

    chunk_max_tokens: int = 500
    chunk_overlap: int = 80
    top_k_retrieve: int = 50
    top_k_rerank: int = 8
    critique_threshold: float = 0.75
    max_retries: int = 2


@lru_cache
def get_settings() -> Settings:
    return Settings()
