"""
Voice Event Models
Pydantic models for voice event processing
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional, Any
from datetime import datetime, timezone
import uuid

class VoiceEvent(BaseModel):
    """Voice event data model"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Audio data
    audio_data: Optional[bytes] = None
    audio_format: str = "pcm_16"
    sample_rate: int = 16000
    duration: Optional[float] = None
    audio_quality: Optional[str] = None
    
    # Context
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            bytes: lambda v: v.hex() if v else None
        }

class VoiceAnalysisResult(BaseModel):
    """Voice analysis result model"""
    event_id: str
    session_id: str
    user_id: str
    timestamp: datetime
    
    # Analysis results
    voice_detected: bool = False
    emotion_scores: Dict[str, float] = Field(default_factory=dict)
    transcript: str = ""
    audio_quality: str = "unknown"
    
    # Processing metadata
    processing_time: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class VoiceStreamConfig(BaseModel):
    """Voice stream configuration"""
    session_id: str
    sample_rate: int = 16000
    channels: int = 1
    format: str = "pcm_16"
    buffer_size: int = 1024
    enable_vad: bool = True
    enable_emotion: bool = True
    enable_transcription: bool = True
    
class VoiceStreamStatus(BaseModel):
    """Voice stream status"""
    session_id: str
    is_active: bool
    start_time: datetime
    packets_received: int = 0
    bytes_processed: int = 0
    errors: int = 0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
