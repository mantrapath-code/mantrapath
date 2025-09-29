"""Configuration settings for the Mood Service."""

import os
from pydantic_settings import BaseSettings
from typing import Optional

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
    
    # AI Model Configuration
    emotion_model_name: str = "joeddav/distilbert-base-uncased-go-emotions-student"
    emotion_cache_ttl: int = int(os.getenv("EMOTION_CACHE_TTL", "3600"))
    
    # Service URLs for integration
    api_gateway_url: Optional[str] = os.getenv("API_GATEWAY_URL")
    auth_service_url: Optional[str] = os.getenv("AUTH_SERVICE_URL") 
    memory_service_url: Optional[str] = os.getenv("MEMORY_SERVICE_URL")
    chatbot_service_url: Optional[str] = os.getenv("CHATBOT_SERVICE_URL")
    
    # Feature Flags
    enable_emotion_detection: bool = os.getenv("ENABLE_EMOTION_DETECTION", "true").lower() == "true"
    enable_sentiment_analysis: bool = os.getenv("ENABLE_SENTIMENT_ANALYSIS", "true").lower() == "true"
    enable_mood_patterns: bool = os.getenv("ENABLE_MOOD_PATTERNS", "true").lower() == "true"
    
    # Performance Settings
    max_text_length: int = int(os.getenv("MAX_TEXT_LENGTH", "1000"))
    batch_processing_enabled: bool = os.getenv("BATCH_PROCESSING_ENABLED", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()