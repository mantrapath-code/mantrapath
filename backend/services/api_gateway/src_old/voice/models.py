"""
Voice Command Models for Enhanced API Gateway V3
Voice command system with multilingual support and cultural context
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone


class VoiceIntentType(Enum):
    """Voice intent classification types"""
    MOOD_TRACKING = "mood_tracking"
    JOURNAL_ENTRY = "journal_entry" 
    CHATBOT_QUERY = "chatbot_query"
    CONTENT_REQUEST = "content_request"
    COMMUNITY_ACTION = "community_action"
    PROFILE_UPDATE = "profile_update"
    NOTIFICATION_SETTING = "notification_setting"
    ANALYTICS_REQUEST = "analytics_request"
    UNKNOWN = "unknown"


@dataclass
class VoiceCommand:
    """Voice command model with multilingual support"""
    intent: VoiceIntentType
    confidence: float
    language: str
    parameters: Dict[str, Any]
    raw_text: str
    cultural_context: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "intent": self.intent.value,
            "confidence": self.confidence,
            "language": self.language,
            "parameters": self.parameters,
            "raw_text": self.raw_text,
            "cultural_context": self.cultural_context,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VoiceCommand':
        """Create from dictionary"""
        timestamp = None
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"])
        
        return cls(
            intent=VoiceIntentType(data["intent"]),
            confidence=data["confidence"],
            language=data["language"],
            parameters=data["parameters"],
            raw_text=data["raw_text"],
            cultural_context=data.get("cultural_context"),
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            timestamp=timestamp
        )


@dataclass
class VoiceRoutingRule:
    """Routing rule for voice commands"""
    intent: VoiceIntentType
    target_service: str
    endpoint_pattern: str
    required_parameters: List[str]
    supported_languages: List[str]
    cultural_adaptations: Dict[str, Any]
    priority: int = 1
    timeout: float = 5.0
    retries: int = 3
    
    def matches_command(self, command: VoiceCommand) -> bool:
        """Check if this rule matches the given voice command"""
        # Check intent match
        if self.intent != command.intent:
            return False
        
        # Check language support
        if command.language not in self.supported_languages:
            return False
        
        # Check required parameters
        for param in self.required_parameters:
            if param not in command.parameters:
                return False
        
        return True
    
    def generate_endpoint(self, command: VoiceCommand) -> str:
        """Generate the target endpoint for this command"""
        endpoint = self.endpoint_pattern
        
        # Replace parameter placeholders
        for param, value in command.parameters.items():
            placeholder = f"{{{param}}}"
            if placeholder in endpoint:
                endpoint = endpoint.replace(placeholder, str(value))
        
        return endpoint


@dataclass
class VoiceRoutingResult:
    """Result of voice command routing"""
    success: bool
    target_service: str
    endpoint: str
    rule: Optional[VoiceRoutingRule] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "success": self.success,
            "target_service": self.target_service,
            "endpoint": self.endpoint,
            "rule": {
                "intent": self.rule.intent.value,
                "target_service": self.rule.target_service,
                "endpoint_pattern": self.rule.endpoint_pattern
            } if self.rule else None,
            "error_message": self.error_message,
            "processing_time_ms": self.processing_time_ms
        }


class VoiceLanguageCode(Enum):
    """Supported voice language codes with regional variants"""
    # Primary languages
    ENGLISH = "en"
    HINDI = "hi"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    
    # Secondary languages
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    JAPANESE = "ja"
    CHINESE = "zh"
    KOREAN = "ko"
    ARABIC = "ar"
    
    # Regional Indian languages
    BENGALI = "bn"
    TAMIL = "ta"
    TELUGU = "te"
    GUJARATI = "gu"
    MARATHI = "mr"
    PUNJABI = "pa"
    URDU = "ur"
    MALAYALAM = "ml"
    KANNADA = "kn"
    ASSAMESE = "as"


@dataclass
class LanguageSupport:
    """Language support configuration"""
    code: VoiceLanguageCode
    name: str
    support_level: str  # "primary", "secondary", "regional"
    cultural_context: Optional[str] = None
    regional_variants: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.regional_variants is None:
            self.regional_variants = []
