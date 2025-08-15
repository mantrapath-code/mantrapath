"""
Voice Processing Engines Package
Multiple engine implementations for STT, TTS, and emotion analysis
"""
from .whisper_engine import WhisperSTTEngine
# from .google_stt_engine import GoogleSTTEngine  # TODO: Implement
# from .azure_stt_engine import AzureSTTEngine  # TODO: Implement
from .elevenlabs_tts_engine import ElevenLabsTTSEngine
# from .google_tts_engine import GoogleTTSEngine  # TODO: Implement
# from .azure_tts_engine import AzureTTSEngine  # TODO: Implement
# from .voice_emotion_engine import VoiceEmotionEngine  # TODO: Implement
from .engine_manager import VoiceEngineManager

__all__ = [
    # STT Engines
    "WhisperSTTEngine",
    # "GoogleSTTEngine",  # TODO: Implement
    # "AzureSTTEngine",  # TODO: Implement
    
    # TTS Engines
    "ElevenLabsTTSEngine",
    # "GoogleTTSEngine",  # TODO: Implement
    # "AzureTTSEngine",  # TODO: Implement
    
    # Emotion Engine
    # "VoiceEmotionEngine",  # TODO: Implement
    
    # Engine Manager
    "VoiceEngineManager"
]
