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
        os.getenv("API_GATEWAY_URL", "http://localhost:8000"),
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
    redis_url: str = Field(default="redis://localhost:6379")
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
    """Service registry configuration"""
    
    # Auth Service
    auth_service_url: str = Field(default="http://localhost:8001")
    auth_service_health_path: str = Field(default="/health")
    
    # Profile Service
    profile_service_url: str = Field(default="http://localhost:8002")
    profile_service_health_path: str = Field(default="/health")
    
    # Mood Service
    mood_service_url: str = Field(default="http://localhost:8003")
    mood_service_health_path: str = Field(default="/health")
    
    # Chatbot Service
    chatbot_service_url: str = Field(default="http://localhost:8004")
    chatbot_service_health_path: str = Field(default="/health")
    
    # Content Service
    content_service_url: str = Field(default="http://localhost:8005")
    content_service_health_path: str = Field(default="/health")
    
    # Community Service
    community_service_url: str = Field(default="http://localhost:8006")
    community_service_health_path: str = Field(default="/health")
    
    # Notification Service
    notification_service_url: str = Field(default="http://localhost:8007")
    notification_service_health_path: str = Field(default="/health")
    
    # ML Service
    ml_service_url: str = Field(default="http://localhost:8008")
    ml_service_health_path: str = Field(default="/health")
    
    # Media Service
    media_service_url: str = Field(default="http://localhost:8009")
    media_service_health_path: str = Field(default="/health")
    
    # Translation Service
    translation_service_url: str = Field(default="http://localhost:8010")
    translation_service_health_path: str = Field(default="/health")
    
    # Voice Service
    voice_service_url: str = Field(default="http://localhost:8011")
    voice_service_health_path: str = Field(default="/health")
    
    model_config = {
        "env_file": ".env", 
        "env_prefix": "SERVICE_",
        "extra": "ignore"
    }

# Global configuration instances
gateway_config = GatewayConfig()
service_config = ServiceConfig()
