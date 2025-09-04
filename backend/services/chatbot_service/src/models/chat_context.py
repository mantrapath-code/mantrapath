"""
Chat Context and Response Models for Enhanced Chatbot Service
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class ChatContext(BaseModel):
    """Chat context for enhanced processing"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Chat session ID")
    user_language: Optional[str] = Field("auto", description="User's preferred language")
    input_type: Optional[str] = Field("text", description="Input type: text, voice, mixed")
    conversation_language: Optional[str] = Field("en", description="Current conversation language")
    user_context: Optional[Dict[str, Any]] = Field(None, description="User context data")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get context value with default"""
        return getattr(self, key, default)


class EnhancedChatResponse(BaseModel):
    """Enhanced chat response with comprehensive data"""
    response: str = Field(..., description="Bot response text")
    session_id: str = Field(..., description="Chat session ID")
    user_id: str = Field(..., description="User ID")
    timestamp: str = Field(..., description="Response timestamp")
    
    # Language and input handling
    language_detected: str = Field(..., description="Detected language from user input")
    conversation_language: str = Field(..., description="Language for conversation consistency")
    input_type: str = Field("text", description="Type of user input")
    should_respond_with_voice: bool = Field(False, description="Whether to respond with voice")
    
    # Voice response data
    audio_response: Optional[str] = Field(None, description="Base64 encoded audio response")
    audio_format: Optional[str] = Field(None, description="Audio format (wav, mp3, etc.)")
    voice_language: Optional[str] = Field(None, description="Language used for voice synthesis")
    
    # Analysis and insights
    crisis_level: str = Field("none", description="Crisis risk level")
    cultural_adaptations: List[Dict[str, Any]] = Field(default_factory=list, description="Cultural adaptations applied")
    actions_triggered: List[Dict[str, Any]] = Field(default_factory=list, description="Actions triggered")
    
    # Processing metadata
    processing_steps: List[str] = Field(default_factory=list, description="Processing steps completed")
    services_used: List[str] = Field(default_factory=list, description="Services used in processing")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Optional fields for backward compatibility
    message_type: Optional[str] = Field(None, description="Message type")
    breathing_exercise: Optional[Dict[str, Any]] = Field(None, description="Breathing exercise data")
    intent: Optional[str] = Field(None, description="Detected intent")
    orchestration_metadata: Optional[Dict[str, Any]] = Field(None, description="Orchestration metadata")
    suggested_actions: Optional[List[str]] = Field(None, description="Suggested actions")
    mood_insights: Optional[Dict[str, Any]] = Field(None, description="Mood insights")
    confidence_score: Optional[float] = Field(None, description="Confidence score")
    source: Optional[str] = Field(None, description="Response source")
