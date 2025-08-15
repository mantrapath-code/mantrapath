"""
Voice Models for API Gateway V3 Enhanced
Data models for voice command processing and routing
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator
import time
import json


class VoiceIntentType(Enum):
    """Enumeration of supported voice intents"""
    MOOD_TRACKING = "mood_tracking"
    JOURNAL_ENTRY = "journal_entry"
    CHATBOT_QUERY = "chatbot_query"
    CONTENT_REQUEST = "content_request"
    COMMUNITY_ACTION = "community_action"
    PROFILE_UPDATE = "profile_update"
    NOTIFICATION_SETTING = "notification_setting"
    ANALYTICS_REQUEST = "analytics_request"
    MEDITATION_START = "meditation_start"
    MEDITATION_STOP = "meditation_stop"
    BREATHING_EXERCISE = "breathing_exercise"
    GOAL_SETTING = "goal_setting"
    PROGRESS_CHECK = "progress_check"
    UNKNOWN = "unknown"


class VoiceLanguage(Enum):
    """Supported voice languages"""
    ENGLISH = "en"
    HINDI = "hi"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    JAPANESE = "ja"
    CHINESE_SIMPLIFIED = "zh"
    CHINESE_TRADITIONAL = "zh-tw"
    KOREAN = "ko"
    ARABIC = "ar"
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


class VoiceConfidenceLevel(Enum):
    """Voice recognition confidence levels"""
    HIGH = "high"      # > 0.8
    MEDIUM = "medium"  # 0.5 - 0.8
    LOW = "low"        # < 0.5


class VoiceCommand(BaseModel):
    """Voice command input model"""
    text: str = Field(..., description="The voice command text")
    intent: Optional[VoiceIntentType] = Field(None, description="Detected or specified intent")
    language: Optional[str] = Field(None, description="Language code (ISO 639-1)")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Recognition confidence")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Extracted parameters")
    cultural_context: Optional[str] = Field(None, description="Cultural context identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    timestamp: float = Field(default_factory=time.time, description="Command timestamp")
    audio_metadata: Dict[str, Any] = Field(default_factory=dict, description="Audio metadata")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v
    
    @validator('language')
    def validate_language(cls, v):
        if v is not None:
            # Accept both language codes and VoiceLanguage enum values
            valid_languages = [lang.value for lang in VoiceLanguage]
            if v not in valid_languages:
                raise ValueError(f'Language must be one of: {valid_languages}')
        return v
    
    def get_confidence_level(self) -> VoiceConfidenceLevel:
        """Get confidence level classification"""
        if self.confidence is None:
            return VoiceConfidenceLevel.MEDIUM
        elif self.confidence > 0.8:
            return VoiceConfidenceLevel.HIGH
        elif self.confidence >= 0.5:
            return VoiceConfidenceLevel.MEDIUM
        else:
            return VoiceConfidenceLevel.LOW
    
    class Config:
        use_enum_values = True


@dataclass
class VoiceRoutingRule:
    """Rule for routing voice commands to services"""
    intent: VoiceIntentType
    target_service: str
    endpoint_pattern: str
    method: str = "POST"
    required_parameters: List[str] = field(default_factory=list)
    optional_parameters: List[str] = field(default_factory=list)
    supported_languages: List[str] = field(default_factory=list)
    cultural_adaptations: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    timeout: float = 5.0
    retry_count: int = 2
    fallback_service: Optional[str] = None
    confidence_threshold: float = 0.5
    
    def matches_command(self, command: VoiceCommand) -> bool:
        """Check if this rule matches the given command"""
        # Check intent
        if command.intent != self.intent:
            return False
        
        # Check confidence threshold
        if command.confidence and command.confidence < self.confidence_threshold:
            return False
        
        # Check language support
        if (command.language and 
            self.supported_languages and 
            command.language not in self.supported_languages):
            return False
        
        # Check required parameters
        for param in self.required_parameters:
            if param not in command.parameters:
                return False
        
        return True


@dataclass
class VoiceRoutingResult:
    """Result of voice command routing"""
    rule: VoiceRoutingRule
    target_service: str
    target_endpoint: str
    method: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    query_params: Dict[str, str] = field(default_factory=dict)
    routing_time_ms: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    fallback_used: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "target_service": self.target_service,
            "target_endpoint": self.target_endpoint,
            "method": self.method,
            "headers": self.headers,
            "body": self.body,
            "query_params": self.query_params,
            "routing_time_ms": self.routing_time_ms,
            "success": self.success,
            "error_message": self.error_message,
            "fallback_used": self.fallback_used
        }


class VoiceResponse(BaseModel):
    """Voice command processing response"""
    request_id: str = Field(..., description="Unique request identifier")
    status: str = Field(..., description="Processing status")
    response: Optional[Dict[str, Any]] = Field(None, description="Service response data")
    processing_time_ms: float = Field(..., description="Total processing time")
    routing_info: Optional[Dict[str, Any]] = Field(None, description="Routing information")
    ai_context: Optional[Dict[str, Any]] = Field(None, description="AI context used")
    cultural_context: Optional[Dict[str, Any]] = Field(None, description="Cultural context applied")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    warnings: List[str] = Field(default_factory=list, description="Any warnings")
    
    class Config:
        use_enum_values = True


class VoiceStreamMessage(BaseModel):
    """WebSocket voice streaming message"""
    type: str = Field(..., description="Message type")
    data: Optional[Dict[str, Any]] = Field(None, description="Message data")
    timestamp: float = Field(default_factory=time.time, description="Message timestamp")
    session_id: Optional[str] = Field(None, description="Session identifier")
    
    class Config:
        use_enum_values = True


class VoiceProcessingStatus(Enum):
    """Voice processing status values"""
    RECEIVED = "received"
    PROCESSING = "processing"
    ROUTING = "routing"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class VoiceProcessingMetrics:
    """Metrics for voice command processing"""
    total_commands: int = 0
    successful_commands: int = 0
    failed_commands: int = 0
    avg_processing_time: float = 0.0
    avg_confidence: float = 0.0
    language_distribution: Dict[str, int] = field(default_factory=dict)
    intent_distribution: Dict[str, int] = field(default_factory=dict)
    error_distribution: Dict[str, int] = field(default_factory=dict)
    
    def add_command_result(
        self,
        intent: VoiceIntentType,
        language: str,
        processing_time: float,
        confidence: Optional[float],
        success: bool,
        error: Optional[str] = None
    ):
        """Add a command processing result to metrics"""
        self.total_commands += 1
        
        if success:
            self.successful_commands += 1
        else:
            self.failed_commands += 1
            if error:
                self.error_distribution[error] = self.error_distribution.get(error, 0) + 1
        
        # Update average processing time
        if self.total_commands == 1:
            self.avg_processing_time = processing_time
        else:
            alpha = 2.0 / (self.total_commands + 1)  # Exponential moving average
            self.avg_processing_time = (
                alpha * processing_time + 
                (1 - alpha) * self.avg_processing_time
            )
        
        # Update average confidence
        if confidence is not None:
            if self.avg_confidence == 0:
                self.avg_confidence = confidence
            else:
                alpha = 2.0 / (self.total_commands + 1)
                self.avg_confidence = (
                    alpha * confidence + 
                    (1 - alpha) * self.avg_confidence
                )
        
        # Update distributions
        self.language_distribution[language] = self.language_distribution.get(language, 0) + 1
        intent_str = intent.value if isinstance(intent, VoiceIntentType) else str(intent)
        self.intent_distribution[intent_str] = self.intent_distribution.get(intent_str, 0) + 1
    
    def get_success_rate(self) -> float:
        """Get success rate as percentage"""
        if self.total_commands == 0:
            return 0.0
        return (self.successful_commands / self.total_commands) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "total_commands": self.total_commands,
            "successful_commands": self.successful_commands,
            "failed_commands": self.failed_commands,
            "success_rate": round(self.get_success_rate(), 2),
            "avg_processing_time": round(self.avg_processing_time, 2),
            "avg_confidence": round(self.avg_confidence, 3),
            "language_distribution": self.language_distribution,
            "intent_distribution": self.intent_distribution,
            "error_distribution": self.error_distribution
        }


class VoiceParameterExtractor:
    """Extract parameters from voice command text"""
    
    @staticmethod
    def extract_mood_parameters(text: str) -> Dict[str, Any]:
        """Extract mood-related parameters"""
        parameters = {}
        
        # Common mood keywords
        mood_mapping = {
            "happy": "happy",
            "sad": "sad",
            "angry": "angry",
            "excited": "excited",
            "calm": "calm",
            "anxious": "anxious",
            "stressed": "stressed",
            "peaceful": "peaceful",
            "frustrated": "frustrated",
            "content": "content"
        }
        
        text_lower = text.lower()
        for keyword, mood in mood_mapping.items():
            if keyword in text_lower:
                parameters["mood"] = mood
                break
        
        # Extract intensity
        if any(word in text_lower for word in ["very", "really", "extremely"]):
            parameters["intensity"] = "high"
        elif any(word in text_lower for word in ["slightly", "a bit", "somewhat"]):
            parameters["intensity"] = "low"
        else:
            parameters["intensity"] = "medium"
        
        return parameters
    
    @staticmethod
    def extract_time_parameters(text: str) -> Dict[str, Any]:
        """Extract time-related parameters"""
        parameters = {}
        
        text_lower = text.lower()
        
        # Time of day
        if any(word in text_lower for word in ["morning", "am"]):
            parameters["time_of_day"] = "morning"
        elif any(word in text_lower for word in ["afternoon", "pm"]):
            parameters["time_of_day"] = "afternoon"
        elif any(word in text_lower for word in ["evening", "night"]):
            parameters["time_of_day"] = "evening"
        
        # Duration
        if "minute" in text_lower:
            import re
            match = re.search(r'(\d+)\s*minute', text_lower)
            if match:
                parameters["duration_minutes"] = int(match.group(1))
        
        return parameters
    
    @staticmethod
    def extract_general_parameters(text: str, intent: VoiceIntentType) -> Dict[str, Any]:
        """Extract general parameters based on intent"""
        parameters = {}
        
        if intent == VoiceIntentType.MOOD_TRACKING:
            parameters.update(VoiceParameterExtractor.extract_mood_parameters(text))
        
        parameters.update(VoiceParameterExtractor.extract_time_parameters(text))
        
        return parameters
