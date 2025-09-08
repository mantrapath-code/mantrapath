"""
Chatbot Service Configuration
Manages integration settings for all internal services
"""
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class ServiceConfig:
    """Configuration for a service"""
    url: str
    timeout: int
    max_retries: int
    enabled: bool
    auth_required: bool = True

@dataclass 
class ChatbotConfig:
    """Main chatbot configuration"""
    # Service configurations
    models_service: ServiceConfig
    ml_service: ServiceConfig
    ai_context_store: ServiceConfig
    translation_service: ServiceConfig
    voice_service: ServiceConfig
    action_orchestrator: ServiceConfig
    memory_service: ServiceConfig
    proactive_assistance_engine: ServiceConfig
    ai_event_processor: ServiceConfig
    
    # General settings
    default_language: str
    supported_languages: List[str]
    response_timeout: int
    max_context_length: int
    enable_voice: bool
    enable_translation: bool
    enable_ml_insights: bool
    enable_workflows: bool
    
    # Crisis detection settings
    crisis_detection_enabled: bool
    crisis_threshold: float
    immediate_escalation_keywords: List[str]
    
    # Response generation settings
    max_response_length: int
    cultural_adaptation_enabled: bool
    emotion_detection_enabled: bool
    personalization_enabled: bool
    
    # Caching settings
    cache_enabled: bool
    cache_ttl: int
    
    # Logging settings
    log_level: str
    log_conversations: bool
    
    @classmethod
    def from_environment(cls) -> 'ChatbotConfig':
        """Create configuration from environment variables"""
        
        # Models Service Configuration
        models_service = ServiceConfig(
            url=os.getenv("MODELS_SERVICE_URL", "http://models-service:8085"),
            timeout=int(os.getenv("MODELS_SERVICE_TIMEOUT", "30")),
            max_retries=int(os.getenv("MODELS_SERVICE_MAX_RETRIES", "3")),
            enabled=os.getenv("MODELS_SERVICE_ENABLED", "true").lower() == "true",
            auth_required=os.getenv("MODELS_SERVICE_AUTH_REQUIRED", "true").lower() == "true"
        )
        
        # ML Service Configuration  
        ml_service = ServiceConfig(
            url=os.getenv("ML_SERVICE_URL", "http://ml-service:8008"),
            timeout=int(os.getenv("ML_SERVICE_TIMEOUT", "30")),
            max_retries=int(os.getenv("ML_SERVICE_MAX_RETRIES", "3")),
            enabled=os.getenv("ML_SERVICE_ENABLED", "true").lower() == "true",
            auth_required=os.getenv("ML_SERVICE_AUTH_REQUIRED", "true").lower() == "true"
        )
        
        # AI Context Store Configuration
        ai_context_store = ServiceConfig(
            url=os.getenv("AI_CONTEXT_STORE_URL", "http://ai-context-store:8013"),
            timeout=int(os.getenv("AI_CONTEXT_STORE_TIMEOUT", "30")),
            max_retries=int(os.getenv("AI_CONTEXT_STORE_MAX_RETRIES", "3")),
            enabled=os.getenv("AI_CONTEXT_STORE_ENABLED", "true").lower() == "true",
            auth_required=os.getenv("AI_CONTEXT_STORE_AUTH_REQUIRED", "true").lower() == "true"
        )
        
        # Translation Service Configuration
        translation_service = ServiceConfig(
            url=os.getenv("TRANSLATION_SERVICE_URL", "http://translation-service:8010"),
            timeout=int(os.getenv("TRANSLATION_SERVICE_TIMEOUT", "30")),
            max_retries=int(os.getenv("TRANSLATION_SERVICE_MAX_RETRIES", "3")),
            enabled=os.getenv("TRANSLATION_SERVICE_ENABLED", "true").lower() == "true",
            auth_required=os.getenv("TRANSLATION_SERVICE_AUTH_REQUIRED", "true").lower() == "true"
        )
        
        # Voice Service Configuration
        voice_service = ServiceConfig(
            url=os.getenv("VOICE_SERVICE_URL", "http://voice-service:8011"),
            timeout=int(os.getenv("VOICE_SERVICE_TIMEOUT", "60")),
            max_retries=int(os.getenv("VOICE_SERVICE_MAX_RETRIES", "3")),
            enabled=os.getenv("VOICE_SERVICE_ENABLED", "true").lower() == "true",
            auth_required=os.getenv("VOICE_SERVICE_AUTH_REQUIRED", "true").lower() == "true"
        )
        
        # Action Orchestrator Configuration
        action_orchestrator = ServiceConfig(
            url=os.getenv("ACTION_ORCHESTRATOR_URL", "http://action-orchestrator:8012"),
            timeout=int(os.getenv("ACTION_ORCHESTRATOR_TIMEOUT", "60")),
            max_retries=int(os.getenv("ACTION_ORCHESTRATOR_MAX_RETRIES", "3")),
            enabled=os.getenv("ACTION_ORCHESTRATOR_ENABLED", "true").lower() == "true",
            auth_required=os.getenv("ACTION_ORCHESTRATOR_AUTH_REQUIRED", "true").lower() == "true"
        )
        
        # Memory Service Configuration
        memory_service = ServiceConfig(
            url=os.getenv("MEMORY_SERVICE_URL", "http://memory-service:8017"),
            timeout=int(os.getenv("MEMORY_SERVICE_TIMEOUT", "30")),
            max_retries=int(os.getenv("MEMORY_SERVICE_MAX_RETRIES", "3")),
            enabled=os.getenv("MEMORY_SERVICE_ENABLED", "true").lower() == "true",
            auth_required=os.getenv("MEMORY_SERVICE_AUTH_REQUIRED", "true").lower() == "true"
        )
        
        # Proactive Assistance Engine Configuration
        proactive_assistance_engine = ServiceConfig(
            url=os.getenv("PROACTIVE_ASSISTANCE_ENGINE_URL", "http://proactive-assistance-engine:8018"),
            timeout=int(os.getenv("PROACTIVE_ASSISTANCE_ENGINE_TIMEOUT", "30")),
            max_retries=int(os.getenv("PROACTIVE_ASSISTANCE_ENGINE_MAX_RETRIES", "3")),
            enabled=os.getenv("PROACTIVE_ASSISTANCE_ENGINE_ENABLED", "true").lower() == "true",
            auth_required=os.getenv("PROACTIVE_ASSISTANCE_ENGINE_AUTH_REQUIRED", "true").lower() == "true"
        )
        
        # AI Event Processor Configuration
        ai_event_processor = ServiceConfig(
            url=os.getenv("AI_EVENT_PROCESSOR_URL", "http://ai-event-processor:8014"),
            timeout=int(os.getenv("AI_EVENT_PROCESSOR_TIMEOUT", "30")),
            max_retries=int(os.getenv("AI_EVENT_PROCESSOR_MAX_RETRIES", "3")),
            enabled=os.getenv("AI_EVENT_PROCESSOR_ENABLED", "true").lower() == "true",
            auth_required=os.getenv("AI_EVENT_PROCESSOR_AUTH_REQUIRED", "true").lower() == "true"
        )
        
        # Supported languages from MantraPath documentation
        supported_languages = [
            "en", "hi", "bn", "te", "ta", "ur", "gu", 
            "kn", "ml", "mr", "pa", "or", "as", "ks", 
            "sd", "ne", "sa"
        ]
        
        # Crisis detection keywords
        immediate_escalation_keywords = [
            "suicide", "kill myself", "end my life", "want to die",
            "harm myself", "hurt myself", "no point living",
            "better off dead", "end it all"
        ]
        
        return cls(
            # Service configurations
            models_service=models_service,
            ml_service=ml_service,
            ai_context_store=ai_context_store,
            translation_service=translation_service,
            voice_service=voice_service,
            action_orchestrator=action_orchestrator,
            memory_service=memory_service,
            proactive_assistance_engine=proactive_assistance_engine,
            ai_event_processor=ai_event_processor,
            
            # General settings
            default_language=os.getenv("CHATBOT_DEFAULT_LANGUAGE", "en"),  # Changed from "hi" to "en"
            supported_languages=supported_languages,
            response_timeout=int(os.getenv("CHATBOT_RESPONSE_TIMEOUT", "30")),
            max_context_length=int(os.getenv("CHATBOT_MAX_CONTEXT_LENGTH", "4000")),
            enable_voice=os.getenv("CHATBOT_ENABLE_VOICE", "true").lower() == "true",
            enable_translation=os.getenv("CHATBOT_ENABLE_TRANSLATION", "true").lower() == "true",
            enable_ml_insights=os.getenv("CHATBOT_ENABLE_ML_INSIGHTS", "true").lower() == "true",
            enable_workflows=os.getenv("CHATBOT_ENABLE_WORKFLOWS", "true").lower() == "true",
            
            # Crisis detection settings
            crisis_detection_enabled=os.getenv("CHATBOT_CRISIS_DETECTION_ENABLED", "true").lower() == "true",
            crisis_threshold=float(os.getenv("CHATBOT_CRISIS_THRESHOLD", "0.7")),
            immediate_escalation_keywords=immediate_escalation_keywords,
            
            # Response generation settings
            max_response_length=int(os.getenv("CHATBOT_MAX_RESPONSE_LENGTH", "500")),
            cultural_adaptation_enabled=os.getenv("CHATBOT_CULTURAL_ADAPTATION_ENABLED", "true").lower() == "true",
            emotion_detection_enabled=os.getenv("CHATBOT_EMOTION_DETECTION_ENABLED", "true").lower() == "true",
            personalization_enabled=os.getenv("CHATBOT_PERSONALIZATION_ENABLED", "true").lower() == "true",
            
            # Caching settings
            cache_enabled=os.getenv("CHATBOT_CACHE_ENABLED", "true").lower() == "true",
            cache_ttl=int(os.getenv("CHATBOT_CACHE_TTL", "3600")),
            
            # Logging settings
            log_level=os.getenv("CHATBOT_LOG_LEVEL", "INFO"),
            log_conversations=os.getenv("CHATBOT_LOG_CONVERSATIONS", "true").lower() == "true"
        )
    
    def get_service_config(self, service_name: str) -> Optional[ServiceConfig]:
        """Get configuration for a specific service"""
        service_map = {
            "models": self.models_service,
            "ml": self.ml_service,
            "context": self.ai_context_store,
            "translation": self.translation_service,
            "voice": self.voice_service,
            "orchestrator": self.action_orchestrator,
            "memory": self.memory_service,
            "proactive": self.proactive_assistance_engine,
            "event_processor": self.ai_event_processor
        }
        return service_map.get(service_name)
    
    def is_service_enabled(self, service_name: str) -> bool:
        """Check if a service is enabled"""
        config = self.get_service_config(service_name)
        return config.enabled if config else False
    
    def get_all_service_urls(self) -> Dict[str, str]:
        """Get all service URLs"""
        return {
            "models": self.models_service.url,
            "ml": self.ml_service.url,
            "context": self.ai_context_store.url,
            "translation": self.translation_service.url,
            "voice": self.voice_service.url,
            "orchestrator": self.action_orchestrator.url,
            "memory": self.memory_service.url,
            "proactive": self.proactive_assistance_engine.url,
            "event_processor": self.ai_event_processor.url
        }
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []
        
        # Check required services
        required_services = ["models", "context"]
        for service in required_services:
            if not self.is_service_enabled(service):
                errors.append(f"Required service '{service}' is disabled")
        
        # Validate language settings
        if self.default_language not in self.supported_languages:
            errors.append(f"Default language '{self.default_language}' not in supported languages")
        
        # Validate crisis threshold
        if not 0.0 <= self.crisis_threshold <= 1.0:
            errors.append("Crisis threshold must be between 0.0 and 1.0")
        
        # Validate timeouts
        if self.response_timeout <= 0:
            errors.append("Response timeout must be positive")
        
        if self.max_response_length <= 0:
            errors.append("Max response length must be positive")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "services": {
                "models": {
                    "url": self.models_service.url,
                    "timeout": self.models_service.timeout,
                    "enabled": self.models_service.enabled
                },
                "ml": {
                    "url": self.ml_service.url,
                    "timeout": self.ml_service.timeout,
                    "enabled": self.ml_service.enabled
                },
                "context": {
                    "url": self.ai_context_store.url,
                    "timeout": self.ai_context_store.timeout,
                    "enabled": self.ai_context_store.enabled
                },
                "translation": {
                    "url": self.translation_service.url,
                    "timeout": self.translation_service.timeout,
                    "enabled": self.translation_service.enabled
                },
                "voice": {
                    "url": self.voice_service.url,
                    "timeout": self.voice_service.timeout,
                    "enabled": self.voice_service.enabled
                },
                "orchestrator": {
                    "url": self.action_orchestrator.url,
                    "timeout": self.action_orchestrator.timeout,
                    "enabled": self.action_orchestrator.enabled
                }
            },
            "general": {
                "default_language": self.default_language,
                "supported_languages": self.supported_languages,
                "response_timeout": self.response_timeout,
                "max_context_length": self.max_context_length,
                "enable_voice": self.enable_voice,
                "enable_translation": self.enable_translation,
                "enable_ml_insights": self.enable_ml_insights,
                "enable_workflows": self.enable_workflows
            },
            "crisis_detection": {
                "enabled": self.crisis_detection_enabled,
                "threshold": self.crisis_threshold,
                "escalation_keywords": self.immediate_escalation_keywords
            },
            "response_generation": {
                "max_length": self.max_response_length,
                "cultural_adaptation": self.cultural_adaptation_enabled,
                "emotion_detection": self.emotion_detection_enabled,
                "personalization": self.personalization_enabled
            },
            "caching": {
                "enabled": self.cache_enabled,
                "ttl": self.cache_ttl
            },
            "logging": {
                "level": self.log_level,
                "log_conversations": self.log_conversations
            }
        }

# Global configuration instance
chatbot_config = ChatbotConfig.from_environment()
