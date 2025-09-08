"""
Configuration settings for the Deployment API Service
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Service Configuration
    DEPLOYMENT_API_PORT: int = 8086
    DEPLOYMENT_API_HOST: str = "0.0.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Authentication
    FRONTEND_ENGINEER_SECRET: str = "your-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    DEFAULT_RATE_LIMIT: int = 1000  # requests per minute
    FRONTEND_ENGINEER_LIMIT: int = 500  # requests per minute
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0", "api-gateway", "deployment-api"]
    
    # Service Discovery
    API_GATEWAY_URL: str = "http://api-gateway:8000"
    VOICE_SERVICE_URL: str = "http://voice-service:8011"
    MODELS_SERVICE_URL: str = "http://models-service:8085"
    COMMUNITY_SERVICE_URL: str = "http://community-service:8006"
    ML_SERVICE_URL: str = "http://ml-service:8008"
    
    # Redis Configuration
    REDIS_URL: str = "redis://redis:6379"
    REDIS_DB: int = 0
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://mantrapath:mantrapath123@postgres:5432/mantrapath"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Model Training Monitoring
    MODEL_TRAINING_CHECK_INTERVAL: int = 30  # seconds
    MODEL_TRAINING_TIMEOUT: int = 300  # seconds
    
    # Health Check Configuration
    HEALTH_CHECK_INTERVAL: int = 30  # seconds
    HEALTH_CHECK_TIMEOUT: int = 10  # seconds
    
    # API Documentation
    DOCS_CACHE_TTL: int = 300  # seconds
    DOCS_MAX_SIZE: int = 1024  # MB
    
    # Usage Tracking
    USAGE_TRACKING_ENABLED: bool = True
    USAGE_RETENTION_DAYS: int = 90
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Environment-specific overrides
def get_environment_settings() -> Settings:
    """Get environment-specific settings"""
    settings = get_settings()
    
    if settings.ENVIRONMENT == "production":
        settings.DEBUG = False
        settings.LOG_LEVEL = "WARNING"
        settings.ALLOWED_ORIGINS = [
            "https://yourdomain.com",
            "https://www.yourdomain.com"
        ]
        settings.ALLOWED_HOSTS = ["yourdomain.com", "www.yourdomain.com"]
    
    elif settings.ENVIRONMENT == "staging":
        settings.DEBUG = False
        settings.LOG_LEVEL = "INFO"
        settings.ALLOWED_ORIGINS = [
            "https://staging.yourdomain.com"
        ]
        settings.ALLOWED_HOSTS = ["staging.yourdomain.com"]
    
    return settings
