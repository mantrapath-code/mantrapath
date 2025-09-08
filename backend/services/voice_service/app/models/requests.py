"""
Request Models
Pydantic models for API requests
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class TTSRequest(BaseModel):
    """Text-to-Speech request model"""
    text: str = Field(..., description="Text to synthesize", min_length=1)
    language: str = Field("en", description="Language code")
    voice: Optional[str] = Field(None, description="Specific voice to use")
    model_preference: Optional[str] = Field(None, description="Preferred TTS model")
    enhance_output: bool = Field(False, description="Apply audio enhancement")
    cache_audio: bool = Field(True, description="Cache the generated audio")
    force_regenerate: bool = Field(False, description="Force regeneration even if cached")
    
    model_config = {"protected_namespaces": ()}

class VoiceEnhancementRequest(BaseModel):
    """Voice enhancement request model"""
    settings: Optional[Dict[str, Any]] = Field(None, description="Enhancement settings")
    target_quality: str = Field("high", description="Target quality level")
    
    model_config = {"protected_namespaces": ()}

class ConversationRequest(BaseModel):
    """Conversation request model"""
    text: str = Field(..., description="User input text")
    language: str = Field("auto", description="Language code or 'auto'")
    session_id: Optional[str] = Field(None, description="Session ID")
    user_id: Optional[str] = Field(None, description="User ID")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    voice_response: bool = Field(True, description="Include voice response")
    
    model_config = {"protected_namespaces": ()}

class SessionCreateRequest(BaseModel):
    """Session creation request model"""
    user_id: Optional[str] = Field(None, description="User ID")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")
    voice_settings: Optional[Dict[str, Any]] = Field(None, description="Voice settings")
    
    model_config = {"protected_namespaces": ()}

class SessionUpdateRequest(BaseModel):
    """Session update request model"""
    preferences: Optional[Dict[str, Any]] = Field(None, description="Updated preferences")
    voice_settings: Optional[Dict[str, Any]] = Field(None, description="Updated voice settings")
    context: Optional[Dict[str, Any]] = Field(None, description="Updated context")
    
    model_config = {"protected_namespaces": ()}

class LanguageDetectionRequest(BaseModel):
    """Language detection request model"""
    text: str = Field(..., description="Text to analyze")
    detailed: bool = Field(False, description="Include detailed analysis")
    
    model_config = {"protected_namespaces": ()}

class CreateSessionRequest(BaseModel):
    """Create session request model"""
    user_id: Optional[str] = Field(None, description="User ID")
    language: str = Field("en", description="Default language")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")
    voice_settings: Optional[Dict[str, Any]] = Field(None, description="Voice settings")
    
    model_config = {"protected_namespaces": ()}

class UpdateSessionRequest(BaseModel):
    """Update session request model"""
    language: Optional[str] = Field(None, description="Updated language")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Updated preferences")
    voice_settings: Optional[Dict[str, Any]] = Field(None, description="Updated voice settings")
    context: Optional[Dict[str, Any]] = Field(None, description="Updated context")
    
    model_config = {"protected_namespaces": ()}
