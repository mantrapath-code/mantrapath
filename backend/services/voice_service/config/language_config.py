"""
Language Configuration for Voice Service
Matching translation service language support with voice-specific enhancements
"""
from typing import Dict, Any

# Supported languages matching translation service tiers
SUPPORTED_LANGUAGES: Dict[str, Dict[str, Any]] = {
    # Tier 1 - Premium Support (Native Models + Cultural Adaptation)
    "en": {
        "name": "English",
        "native": "English", 
        "rtl": False,
        "tier": 1,
        "voice_models": ["neural", "standard", "premium"],
        "stt_engines": ["whisper", "google", "azure"],
        "tts_engines": ["elevenlabs", "azure", "google"],
        "emotion_support": True,
        "cultural_adaptation": True
    },
    "hi": {
        "name": "Hindi",
        "native": "हिन्दी",
        "rtl": False,
        "tier": 1,
        "voice_models": ["neural", "standard"],
        "stt_engines": ["whisper", "google"],
        "tts_engines": ["google", "azure"],
        "emotion_support": True,
        "cultural_adaptation": True
    },
    "es": {
        "name": "Spanish", 
        "native": "Español",
        "rtl": False,
        "tier": 1,
        "voice_models": ["neural", "standard", "premium"],
        "stt_engines": ["whisper", "google", "azure"],
        "tts_engines": ["elevenlabs", "azure", "google"],
        "emotion_support": True,
        "cultural_adaptation": True
    },
    "fr": {
        "name": "French",
        "native": "Français", 
        "rtl": False,
        "tier": 1,
        "voice_models": ["neural", "standard"],
        "stt_engines": ["whisper", "google", "azure"],
        "tts_engines": ["azure", "google"],
        "emotion_support": True,
        "cultural_adaptation": True
    },
    "ar": {
        "name": "Arabic",
        "native": "العربية",
        "rtl": True,
        "tier": 1,
        "voice_models": ["neural", "standard"],
        "stt_engines": ["whisper", "google"],
        "tts_engines": ["azure", "google"],
        "emotion_support": True,
        "cultural_adaptation": True
    },
    "zh": {
        "name": "Chinese",
        "native": "中文",
        "rtl": False,
        "tier": 1,
        "voice_models": ["neural", "standard"],
        "stt_engines": ["whisper", "google"],
        "tts_engines": ["azure", "google"],
        "emotion_support": True,
        "cultural_adaptation": True
    },
    "ja": {
        "name": "Japanese",
        "native": "日本語",
        "rtl": False,
        "tier": 1,
        "voice_models": ["neural", "standard"],
        "stt_engines": ["whisper", "google"],
        "tts_engines": ["azure", "google"],
        "emotion_support": True,
        "cultural_adaptation": True
    },
    "sa": {
        "name": "Sanskrit",
        "native": "संस्कृतम्",
        "rtl": False,
        "tier": 1,
        "voice_models": ["standard"],
        "stt_engines": ["whisper"],
        "tts_engines": ["google"],
        "emotion_support": True,
        "cultural_adaptation": True,
        "meditation_optimized": True
    },
    "th": {
        "name": "Thai",
        "native": "ไทย",
        "rtl": False,
        "tier": 1,
        "voice_models": ["neural", "standard"],
        "stt_engines": ["whisper", "google"],
        "tts_engines": ["google"],
        "emotion_support": True,
        "cultural_adaptation": True
    },
    "my": {
        "name": "Myanmar",
        "native": "မြန်မာ",
        "rtl": False,
        "tier": 1,
        "voice_models": ["standard"],
        "stt_engines": ["whisper"],
        "tts_engines": ["google"],
        "emotion_support": True,
        "cultural_adaptation": True
    },
    
    # Tier 2 - Standard Support
    "de": {
        "name": "German",
        "native": "Deutsch",
        "rtl": False,
        "tier": 2,
        "voice_models": ["neural", "standard"],
        "stt_engines": ["whisper", "google"],
        "tts_engines": ["azure", "google"],
        "emotion_support": True,
        "cultural_adaptation": False
    },
    "it": {
        "name": "Italian",
        "native": "Italiano",
        "rtl": False,
        "tier": 2,
        "voice_models": ["neural", "standard"],
        "stt_engines": ["whisper", "google"],
        "tts_engines": ["azure", "google"],
        "emotion_support": True,
        "cultural_adaptation": False
    },
    "pt": {
        "name": "Portuguese",
        "native": "Português",
        "rtl": False,
        "tier": 2,
        "voice_models": ["neural", "standard"],
        "stt_engines": ["whisper", "google"],
        "tts_engines": ["azure", "google"],
        "emotion_support": True,
        "cultural_adaptation": False
    },
    "ru": {
        "name": "Russian",
        "native": "Русский",
        "rtl": False,
        "tier": 2,
        "voice_models": ["neural", "standard"],
        "stt_engines": ["whisper", "google"],
        "tts_engines": ["azure", "google"],
        "emotion_support": True,
        "cultural_adaptation": False
    },
    "ko": {
        "name": "Korean",
        "native": "한국어",
        "rtl": False,
        "tier": 2,
        "voice_models": ["neural", "standard"],
        "stt_engines": ["whisper", "google"],
        "tts_engines": ["azure", "google"],
        "emotion_support": True,
        "cultural_adaptation": False
    },
    "nl": {
        "name": "Dutch",
        "native": "Nederlands",
        "rtl": False,
        "tier": 2,
        "voice_models": ["standard"],
        "stt_engines": ["whisper", "google"],
        "tts_engines": ["azure", "google"],
        "emotion_support": True,
        "cultural_adaptation": False
    }
}

# Language tier definitions
LANGUAGE_TIERS = {
    "tier_1": {
        "name": "Premium Support",
        "description": "Native models with cultural adaptation, meditation optimization",
        "features": [
            "Advanced emotion detection",
            "Cultural voice adaptation", 
            "Meditation-specific vocabulary",
            "Premium voice quality",
            "Multiple engine support",
            "Real-time processing"
        ]
    },
    "tier_2": {
        "name": "Standard Support", 
        "description": "High-quality translation and voice processing",
        "features": [
            "Standard emotion detection",
            "High-quality voice synthesis",
            "Multiple engine support",
            "Real-time processing"
        ]
    }
}

# Voice engine priorities by language
ENGINE_PRIORITIES = {
    "stt": {
        "tier_1": ["whisper", "google", "azure"],
        "tier_2": ["whisper", "google"]
    },
    "tts": {
        "tier_1": ["elevenlabs", "azure", "google"],
        "tier_2": ["azure", "google"]
    }
}

# Meditation-specific language configurations
MEDITATION_LANGUAGES = {
    "sa": {
        "mantras_supported": True,
        "pronunciation_guide": True,
        "traditional_voices": ["male_priest", "female_teacher"]
    },
    "hi": {
        "mantras_supported": True,
        "pronunciation_guide": True,
        "traditional_voices": ["classical_male", "classical_female"]
    },
    "th": {
        "meditation_tradition": "buddhist",
        "chanting_support": True
    },
    "my": {
        "meditation_tradition": "buddhist", 
        "chanting_support": True
    }
}

def get_language_info(language_code: str) -> Dict[str, Any]:
    """Get comprehensive language information"""
    return SUPPORTED_LANGUAGES.get(language_code, {})

def get_supported_engines(language_code: str, engine_type: str) -> list:
    """Get supported engines for a language and type (stt/tts)"""
    lang_info = SUPPORTED_LANGUAGES.get(language_code, {})
    return lang_info.get(f"{engine_type}_engines", [])

def is_language_supported(language_code: str) -> bool:
    """Check if language is supported"""
    return language_code in SUPPORTED_LANGUAGES

def get_tier_languages(tier: int) -> list:
    """Get all languages in a specific tier"""
    return [
        code for code, info in SUPPORTED_LANGUAGES.items() 
        if info.get("tier") == tier
    ]
