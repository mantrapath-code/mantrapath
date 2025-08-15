"""
Voice Service Configuration Package
"""
from .settings import voice_config
from .language_config import SUPPORTED_LANGUAGES, LANGUAGE_TIERS

__all__ = [
    "voice_config",
    "SUPPORTED_LANGUAGES",
    "LANGUAGE_TIERS"
]
