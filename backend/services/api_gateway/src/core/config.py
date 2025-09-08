"""
Configuration management for API Gateway
"""
import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class LoadBalancingStrategy(str, Enum):
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"

class GatewayConfig(BaseSettings):
    """Main gateway configuration"""
    
    # Basic settings
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=True)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    
    # CORS settings
    cors_origins: List[str] = Field(default_factory=lambda: [
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
        os.getenv("API_GATEWAY_URL", "http://api-gateway:8000"),
        
        "http://localhost:5174"  # Additional dev port
    ])
    cors_credentials: bool = Field(default=True)
    cors_methods: List[str] = Field(default=["*"])
    cors_headers: List[str] = Field(default=["*"])
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests_per_minute: int = Field(default=100)
    rate_limit_burst: int = Field(default=20)
    
    # Load balancing
    load_balancing_strategy: LoadBalancingStrategy = Field(default=LoadBalancingStrategy.ROUND_ROBIN)
    
    # Health checks
    health_check_interval: int = Field(default=30)  # seconds
    health_check_timeout: int = Field(default=10)   # seconds
    health_check_retries: int = Field(default=3)
    
    # Circuit breaker
    circuit_breaker_enabled: bool = Field(default=True)
    circuit_breaker_failure_threshold: int = Field(default=5)
    circuit_breaker_recovery_timeout: int = Field(default=60)
    
    # Redis (for caching and state)
    redis_url: str = Field(default="redis://redis:6379")
    redis_ttl: int = Field(default=300)  # 5 minutes
    
    # Security
    jwt_secret_key: str = Field(default="your-secret-key-change-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration: int = Field(default=3600)  # 1 hour
    
    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Monitoring
    metrics_enabled: bool = Field(default=True)
    metrics_port: int = Field(default=9090)
    
    # V3 Enhanced Features
    voice_routing_enabled: bool = Field(default=True)
    ai_context_enabled: bool = Field(default=True)
    cultural_adaptation_enabled: bool = Field(default=True)
    websocket_voice_streaming: bool = Field(default=True)
    performance_monitoring: bool = Field(default=True)
    
    model_config = {
        "env_file": ".env",
        "env_prefix": "GATEWAY_",
        "extra": "ignore"
    }

class ServiceConfig(BaseSettings):
    """Service registry configuration with standardized ports"""
    
    # Gateway Ports Configuration
    gateway_port: int = Field(default=8000, description="Main API Gateway port")
    websocket_port: int = Field(default=8001, description="WebSocket port for real-time features")
    metrics_port: int = Field(default=9090, description="Metrics and monitoring port")
    
    # Standardized Service Ports (using environment variables for correct ports)
    # Auth Service
    auth_service_url: str = Field(default_factory=lambda: f"http://auth-service:{os.getenv('AUTH_SERVICE_PORT', '8001')}")
    auth_service_health_path: str = Field(default="/health")
    
    # Profile Service  
    profile_service_url: str = Field(default_factory=lambda: f"http://profile-service:{os.getenv('PROFILE_SERVICE_PORT', '8002')}")
    profile_service_health_path: str = Field(default="/health")
    
    # Mood Service
    mood_service_url: str = Field(default_factory=lambda: f"http://mood-service:{os.getenv('MOOD_SERVICE_PORT', '8003')}")
    mood_service_health_path: str = Field(default="/health")
    
    # Chatbot Service
    chatbot_service_url: str = Field(default_factory=lambda: f"http://chatbot-service:{os.getenv('CHATBOT_SERVICE_PORT', '8004')}")
    chatbot_service_health_path: str = Field(default="/health")
    
    # Content Service (Fixed naming - was incorrectly mapped to translation service)
    content_service_url: str = Field(default_factory=lambda: f"http://content-service:{os.getenv('CONTENT_SERVICE_PORT', '8005')}")
    content_service_health_path: str = Field(default="/health")
    
    # Community Service
    community_service_url: str = Field(default_factory=lambda: f"http://community-service:{os.getenv('COMMUNITY_SERVICE_PORT', '8006')}")
    community_service_health_path: str = Field(default="/health")
    
    # Notification Service
    notification_service_url: str = Field(default_factory=lambda: f"http://notification-service:{os.getenv('NOTIFICATION_SERVICE_PORT', '8007')}")
    notification_service_health_path: str = Field(default="/health")
    
    # ML Service
    ml_service_url: str = Field(default_factory=lambda: f"http://ml-service:{os.getenv('ML_SERVICE_PORT', '8008')}")
    ml_service_health_path: str = Field(default="/health")
    
    # Media Service
    media_service_url: str = Field(default_factory=lambda: f"http://media-service:{os.getenv('MEDIA_SERVICE_PORT', '8009')}")
    media_service_health_path: str = Field(default="/health")
    
    # Translation Service (Fixed naming - was incorrectly mapped to content service) 
    translation_service_url: str = Field(default_factory=lambda: f"http://translation-service:{os.getenv('TRANSLATION_SERVICE_PORT', '8010')}")
    translation_service_health_path: str = Field(default="/health")
    
    # Voice Service
    voice_service_url: str = Field(default_factory=lambda: f"http://voice-service:{os.getenv('VOICE_SERVICE_PORT', '8011')}")
    voice_service_health_path: str = Field(default="/health")
    
    # Action Orchestrator Service
    action_orchestrator_url: str = Field(default_factory=lambda: f"http://action-orchestrator:{os.getenv('ACTION_ORCHESTRATOR_PORT', '8012')}")
    action_orchestrator_health_path: str = Field(default="/health")
    
    # Models Service (Fixed port conflict - was 8080, now using env var)
    models_service_url: str = Field(default_factory=lambda: f"http://models-service:{os.getenv('MODELS_SERVICE_INTERNAL_PORT', '8080')}")
    models_service_health_path: str = Field(default="/health")
    
    # AI Event Processor Service
    ai_event_processor_url: str = Field(default_factory=lambda: f"http://ai-event-processor:{os.getenv('AI_EVENT_PROCESSOR_PORT', '8014')}")
    ai_event_processor_health_path: str = Field(default="/health")
    
    # AI Context Store Service
    ai_context_store_url: str = Field(default_factory=lambda: f"http://ai-context-store:{os.getenv('AI_CONTEXT_STORE_PORT', '8013')}")
    ai_context_store_health_path: str = Field(default="/health")
    
    model_config = {
        "env_file": ".env", 
        "env_prefix": "SERVICE_",
        "extra": "ignore"
    }

# Global configuration instances
gateway_config = GatewayConfig()
service_config = ServiceConfig()
