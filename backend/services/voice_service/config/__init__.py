"""
Voice Service Configuration Package
"""
from .settings import voice_config, VoiceServiceConfig
from .language_config import SUPPORTED_LANGUAGES, LANGUAGE_TIERS

__all__ = [
    "voice_config",
    "VoiceServiceConfig", 
    "SUPPORTED_LANGUAGES",
    "LANGUAGE_TIERS"
]
