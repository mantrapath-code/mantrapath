"""
Configuration settings for Action Orchestrator Service
"""
import os
from typing import List

class Settings:
    """Application settings"""
    
    # Server Configuration
    HOST: str = os.getenv("ORCHESTRATOR_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("ORCHESTRATOR_PORT", "8012"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://mantrapath:mantrapath123@localhost:5432/mantrapath")
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key")
    
    # External Service URLs
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    PROFILE_SERVICE_URL: str = os.getenv("PROFILE_SERVICE_URL", "http://localhost:8002") 
    MOOD_SERVICE_URL: str = os.getenv("MOOD_SERVICE_URL", "http://localhost:8003")
    CHATBOT_SERVICE_URL: str = os.getenv("CHATBOT_SERVICE_URL", "http://localhost:8004")
    CONTENT_SERVICE_URL: str = os.getenv("CONTENT_SERVICE_URL", "http://localhost:8005")
    COMMUNITY_SERVICE_URL: str = os.getenv("COMMUNITY_SERVICE_URL", "http://localhost:8006")
    NOTIFICATION_SERVICE_URL: str = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8007")
    ML_SERVICE_URL: str = os.getenv("ML_SERVICE_URL", "http://localhost:8008")
    MEDIA_SERVICE_URL: str = os.getenv("MEDIA_SERVICE_URL", "http://localhost:8009")
    TRANSLATION_SERVICE_URL: str = os.getenv("TRANSLATION_SERVICE_URL", "http://localhost:8010")
    VOICE_SERVICE_URL: str = os.getenv("VOICE_SERVICE_URL", "http://localhost:8011")
    API_GATEWAY_URL: str = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
    
    # AI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Orchestrator Configuration
    MAX_RETRY_ATTEMPTS: int = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    CIRCUIT_BREAKER_THRESHOLD: int = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:8000",
        "http://localhost:8001"
    ]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Create settings instance
settings = Settings()
