"""
MantraPath Voice Service Configuration Settings
Enterprise-grade configuration management following API Gateway patterns
"""
import os
import json
from typing import List, Dict, Any
from pydantic_settings import BaseSettings

class VoiceServiceConfig(BaseSettings):
    """Voice service configuration with environment variable support"""
    
    # Service Configuration
    service_name: str = "voice_service"
    service_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8011
    debug: bool = False
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    ENVIRONMENT: str = environment  # Uppercase alias for backward compatibility
    
    # Authentication & Security
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "voice-service-secret-key")
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///../../mantrapath.db")
    
    # Redis Configuration (for caching and real-time features)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/3")
    cache_ttl_default: int = 3600  # 1 hour
    cache_ttl_voice_profiles: int = 86400 * 7  # 7 days
    cache_ttl_audio_cache: int = 86400 * 3  # 3 days
    
    # Audio Processing Configuration
    SUPPORTED_AUDIO_FORMATS: List[str] = ["wav", "mp3", "ogg", "flac", "webm", "m4a"]
    MAX_AUDIO_DURATION: int = 300  # 5 minutes
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    SAMPLE_RATE: int = 16000
    CHANNELS: int = 1
    
    # Text Processing Configuration
    MAX_TEXT_LENGTH: int = 10000  # Maximum characters for TTS
    SUPPORTED_LANGUAGES: List[str] = ["en", "hi", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"]
    
    # Voice Engine API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    google_cloud_api_key: str = os.getenv("GOOGLE_CLOUD_API_KEY", "")
    azure_speech_key: str = os.getenv("AZURE_SPEECH_KEY", "")
    azure_speech_region: str = os.getenv("AZURE_SPEECH_REGION", "eastus")
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    
    # Performance Settings
    max_concurrent_requests: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))  # seconds
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "1000"))
    
    # Real-time Processing
    websocket_max_connections: int = int(os.getenv("WEBSOCKET_MAX_CONNECTIONS", "100"))
    stream_chunk_size: int = int(os.getenv("STREAM_CHUNK_SIZE", "1024"))
    
    # Voice Quality Settings
    min_confidence_score: float = float(os.getenv("MIN_CONFIDENCE_SCORE", "0.7"))
    emotion_analysis_enabled: bool = os.getenv("EMOTION_ANALYSIS_ENABLED", "true").lower() == "true"
    voice_cloning_enabled: bool = os.getenv("VOICE_CLONING_ENABLED", "true").lower() == "true"
    MIN_TRAINING_DURATION: int = int(os.getenv("MIN_TRAINING_DURATION", "60"))  # seconds
    
    # File Storage
    audio_storage_path: str = os.getenv("AUDIO_STORAGE_PATH", "./data/audio")
    voice_models_path: str = os.getenv("VOICE_MODELS_PATH", "./data/models")
    temp_storage_path: str = os.getenv("TEMP_STORAGE_PATH", "./data/temp")
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:8080,https://mantrapath.app,https://*.mantrapath.app"
    cors_credentials: bool = True
    cors_methods: str = "*"
    cors_headers: str = "*"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert cors_origins string to list"""
        if not self.cors_origins or self.cors_origins.strip() == "":
            return ["http://localhost:3000", "http://localhost:8080", "https://mantrapath.app", "https://*.mantrapath.app"]
        try:
            # Try to parse as JSON first
            return json.loads(self.cors_origins)
        except json.JSONDecodeError:
            # Fall back to comma-separated parsing
            return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]
    
    @property 
    def cors_methods_list(self) -> List[str]:
        """Convert cors_methods string to list"""
        if not self.cors_methods or self.cors_methods.strip() == "":
            return ["*"]
        try:
            return json.loads(self.cors_methods)
        except json.JSONDecodeError:
            return [method.strip() for method in self.cors_methods.split(',') if method.strip()]
    
    @property
    def cors_headers_list(self) -> List[str]:
        """Convert cors_headers string to list"""
        if not self.cors_headers or self.cors_headers.strip() == "":
            return ["*"]
        try:
            return json.loads(self.cors_headers)
        except json.JSONDecodeError:
            return [header.strip() for header in self.cors_headers.split(',') if header.strip()]
    
    # Backward compatibility aliases
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Backward compatibility property"""
        return self.cors_origins_list
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    
    # Service Discovery & Health Checks
    health_check_interval: int = 30  # seconds
    service_registry_url: str = os.getenv("SERVICE_REGISTRY_URL", "http://localhost:8500")
    
    # Integration with other MantraPath services
    auth_service_url: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    profile_service_url: str = os.getenv("PROFILE_SERVICE_URL", "http://localhost:8002")
    translation_service_url: str = os.getenv("TRANSLATION_SERVICE_URL", "http://localhost:8010")
    chatbot_service_url: str = os.getenv("CHATBOT_SERVICE_URL", "http://localhost:8004")
    community_service_url: str = os.getenv("COMMUNITY_SERVICE_URL", "http://localhost:8005")
    content_service_url: str = os.getenv("CONTENT_SERVICE_URL", "http://localhost:8006")
    
    # Additional service URLs (uppercase for backward compatibility)
    AUTH_SERVICE_URL: str = auth_service_url
    PROFILE_SERVICE_URL: str = profile_service_url
    CONTENT_SERVICE_URL: str = content_service_url
    COMMUNITY_SERVICE_URL: str = community_service_url
    TRANSLATION_SERVICE_URL: str = translation_service_url
    NOTIFICATION_SERVICE_URL: str = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8007")
    MEDIA_SERVICE_URL: str = os.getenv("MEDIA_SERVICE_URL", "http://localhost:8008")
    MOOD_SERVICE_URL: str = os.getenv("MOOD_SERVICE_URL", "http://localhost:8009")
    API_GATEWAY_URL: str = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
    
    # Monitoring & Metrics
    prometheus_enabled: bool = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
    metrics_port: int = int(os.getenv("METRICS_PORT", "9011"))
    detailed_logging: bool = os.getenv("DETAILED_LOGGING", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global configuration instance
voice_config = VoiceServiceConfig()
