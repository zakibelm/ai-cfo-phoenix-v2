from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI CFO Suite - Phoenix"
    APP_VERSION: str = "3.0.0"
    APP_URL: str = "http://localhost:3000"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://aicfo:aicfo_secure_pass_2025@localhost:5432/aicfo_db"
    
    # Qdrant Vector DB
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_PREFIX: str = "aicfo_"
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600  # 1 hour
    
    # MinIO Object Storage
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET: str = "aicfo-documents"
    MINIO_SECURE: bool = False
    
    # AI Models
    OPENROUTER_API_KEY: Optional[str] = None  # Required for LLM access
    HUGGINGFACE_TOKEN: Optional[str] = None
    EMBED_MODEL: str = "BAAI/bge-small-en-v1.5"
    RERANK_MODEL: str = "BAAI/bge-reranker-base"
    DEFAULT_LLM_MODEL: str = "gpt-4-turbo"  # OpenRouter model key
    
    # RAG Settings
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100
    TOP_K: int = 10
    RERANK_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Agent Settings
    AGENT_TIMEOUT: int = 300  # 5 minutes
    MAX_ITERATIONS: int = 10
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ENCRYPTION_KEY: str = "your-encryption-key-32-bytes-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # i18n (Internationalization)
    DEFAULT_LANGUAGE: str = "fr"  # French by default
    SUPPORTED_LANGUAGES: list = ["fr", "en"]  # French and English
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
