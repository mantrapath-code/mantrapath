"""
Voice Service Core Package
Base classes, models, and exceptions
"""
from .models import *
from .base_engine import BaseVoiceEngine, BaseSTTEngine, BaseTTSEngine
from .exceptions import *

__all__ = [
    # Models
    "VoiceCommand",
    "TTSRequest", 
    "STTRequest",
    "VoiceProfile",
    "VoiceResponse",
    "AudioData",
    "EmotionAnalysis",
    
    # Base Classes
    "BaseVoiceEngine",
    "BaseSTTEngine",
    "BaseTTSEngine",
    
    # Exceptions
    "VoiceServiceError",
    "AudioProcessingError",
    "EngineError",
    "UnsupportedLanguageError",
    "AudioValidationError"
]
