"""Application configuration settings."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Service Configuration
    service_name: str = "mood-service"
    version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = int(os.getenv("MOOD_SERVICE_PORT", "8003"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database Configuration
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://mantrapath:mantrapath123@postgres:5432/mantrapath"
    )
    
    # Redis Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    redis_cache_ttl: int = int(os.getenv("REDIS_CACHE_TTL", "300"))
    
    # JWT Configuration
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
    jwt_algorithm: str = "HS256"
    
    class Config:
        env_file = ".env"


settings = Settings()