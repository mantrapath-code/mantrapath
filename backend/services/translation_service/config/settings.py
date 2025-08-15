"""
Configuration settings for Translation Service
"""
from pydantic_settings import BaseSettings
from typing import Dict, List, Optional
import os

class TranslationSettings(BaseSettings):
    """Translation service configuration"""
    
    # Service Configuration
    service_name: str = "translation_service"
    service_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8010  # Changed from 8005 to avoid conflicts
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///../../mantrapath.db")
    
    # Redis Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/2")
    cache_ttl_default: int = 3600  # 1 hour
    cache_ttl_premium: int = 86400 * 7  # 7 days
    cache_ttl_critical: int = 86400 * 30  # 30 days for offline cache
    
    # JWT & Authentication
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "translation-service-secret-key")
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    
    # Translation Engine API Keys
    google_translate_api_key: Optional[str] = os.getenv("GOOGLE_TRANSLATE_API_KEY")
    microsoft_translator_key: Optional[str] = os.getenv("MICROSOFT_TRANSLATOR_KEY")
    microsoft_translator_region: str = os.getenv("MICROSOFT_TRANSLATOR_REGION", "global")
    # Google Translate Configuration
GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY", "")

# OpenAI Configuration (for advanced translation with context)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Microsoft Translator Configuration
MICROSOFT_TRANSLATOR_API_KEY = os.getenv("MICROSOFT_TRANSLATOR_API_KEY", "")
MICROSOFT_TRANSLATOR_REGION = os.getenv("MICROSOFT_TRANSLATOR_REGION", "global")

# Performance Settings
MAX_CONCURRENT_TRANSLATIONS = int(os.getenv("MAX_CONCURRENT_TRANSLATIONS", "100"))
TRANSLATION_TIMEOUT = int(os.getenv("TRANSLATION_TIMEOUT", "30"))  # seconds
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "1000"))
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "5000"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))
    
    # Quality Thresholds
MIN_CONFIDENCE_SCORE = float(os.getenv("MIN_CONFIDENCE_SCORE", "0.7"))
FALLBACK_THRESHOLD = float(os.getenv("FALLBACK_THRESHOLD", "0.5"))
CACHE_CONFIDENCE_THRESHOLD = float(os.getenv("CACHE_CONFIDENCE_THRESHOLD", "0.8"))
    
# Local Models Configuration
LOCAL_MODELS_PATH = os.getenv("LOCAL_MODELS_PATH", "./data/models")
SPACY_MODELS_PATH = os.getenv("SPACY_MODELS_PATH", "./data/spacy_models")
FASTTEXT_MODEL_PATH = os.getenv("FASTTEXT_MODEL_PATH", "./data/lid.176.bin")

# Meditation Glossaries
GLOSSARIES_PATH = os.getenv("GLOSSARIES_PATH", "./data/glossaries")
CUSTOM_TERMINOLOGY_ENABLED = os.getenv("CUSTOM_TERMINOLOGY_ENABLED", "true").lower() == "true"

# Voice Translation Settings
VOICE_TRANSLATION_ENABLED = os.getenv("VOICE_TRANSLATION_ENABLED", "true").lower() == "true"
SUPPORTED_AUDIO_FORMATS = ["wav", "mp3", "ogg", "flac"]
MAX_AUDIO_DURATION = int(os.getenv("MAX_AUDIO_DURATION", "300"))  # 5 minutes

# Offline Support
OFFLINE_MODE_ENABLED = os.getenv("OFFLINE_MODE_ENABLED", "true").lower() == "true"
OFFLINE_CACHE_SIZE_MB = int(os.getenv("OFFLINE_CACHE_SIZE_MB", "1000"))
CRITICAL_LANGUAGES = ["en", "hi", "es", "fr", "ar", "zh"]

# Monitoring & Analytics
PROMETHEUS_ENABLED = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
USAGE_ANALYTICS_ENABLED = os.getenv("USAGE_ANALYTICS_ENABLED", "true").lower() == "true"
DETAILED_LOGGING = os.getenv("DETAILED_LOGGING", "false").lower() == "true"

# Language Configuration
SUPPORTED_LANGUAGES = {
    # Tier 1 - Premium Support (Native Models + Cultural Adaptation)
    "en": {"name": "English", "native": "English", "rtl": False, "tier": 1},
    "hi": {"name": "Hindi", "native": "हिन्दी", "rtl": False, "tier": 1},
    "es": {"name": "Spanish", "native": "Español", "rtl": False, "tier": 1},
    "fr": {"name": "French", "native": "Français", "rtl": False, "tier": 1},
    "ar": {"name": "Arabic", "native": "العربية", "rtl": True, "tier": 1},
    "zh": {"name": "Chinese", "native": "中文", "rtl": False, "tier": 1},
    "ja": {"name": "Japanese", "native": "日本語", "rtl": False, "tier": 1},
    "sa": {"name": "Sanskrit", "native": "संस्कृतम्", "rtl": False, "tier": 1},
    "th": {"name": "Thai", "native": "ไทย", "rtl": False, "tier": 1},
    "my": {"name": "Myanmar", "native": "မြန်မာ", "rtl": False, "tier": 1},
    
    # Tier 2 - Standard Support
    "de": {"name": "German", "native": "Deutsch", "rtl": False, "tier": 2},
    "it": {"name": "Italian", "native": "Italiano", "rtl": False, "tier": 2},
    "pt": {"name": "Portuguese", "native": "Português", "rtl": False, "tier": 2},
    "ru": {"name": "Russian", "native": "Русский", "rtl": False, "tier": 2},
    "ko": {"name": "Korean", "native": "한국어", "rtl": False, "tier": 2},
    "bn": {"name": "Bengali", "native": "বাংলা", "rtl": False, "tier": 2},
    "ta": {"name": "Tamil", "native": "தமிழ்", "rtl": False, "tier": 2},
    "te": {"name": "Telugu", "native": "తెలుగు", "rtl": False, "tier": 2},
    "ur": {"name": "Urdu", "native": "اردو", "rtl": True, "tier": 2},
    "fa": {"name": "Persian", "native": "فارسی", "rtl": True, "tier": 2},
    "he": {"name": "Hebrew", "native": "עברית", "rtl": True, "tier": 2},
    "tr": {"name": "Turkish", "native": "Türkçe", "rtl": False, "tier": 2},
    "vi": {"name": "Vietnamese", "native": "Tiếng Việt", "rtl": False, "tier": 2},
    "id": {"name": "Indonesian", "native": "Bahasa Indonesia", "rtl": False, "tier": 2},
    "ms": {"name": "Malay", "native": "Bahasa Melayu", "rtl": False, "tier": 2},
    
    # Tier 3 - Basic Support (50+ languages total)
    "pl": {"name": "Polish", "native": "Polski", "rtl": False, "tier": 3},
    "nl": {"name": "Dutch", "native": "Nederlands", "rtl": False, "tier": 3},
    "sv": {"name": "Swedish", "native": "Svenska", "rtl": False, "tier": 3},
    "da": {"name": "Danish", "native": "Dansk", "rtl": False, "tier": 3},
    "no": {"name": "Norwegian", "native": "Norsk", "rtl": False, "tier": 3},
    "fi": {"name": "Finnish", "native": "Suomi", "rtl": False, "tier": 3},
    "hu": {"name": "Hungarian", "native": "Magyar", "rtl": False, "tier": 3},
    "cs": {"name": "Czech", "native": "Čeština", "rtl": False, "tier": 3},
    "sk": {"name": "Slovak", "native": "Slovenčina", "rtl": False, "tier": 3},
    "bg": {"name": "Bulgarian", "native": "Български", "rtl": False, "tier": 3},
    "ro": {"name": "Romanian", "native": "Română", "rtl": False, "tier": 3},
    "hr": {"name": "Croatian", "native": "Hrvatski", "rtl": False, "tier": 3},
    "sr": {"name": "Serbian", "native": "Српски", "rtl": False, "tier": 3},
    "sl": {"name": "Slovenian", "native": "Slovenščina", "rtl": False, "tier": 3},
    "et": {"name": "Estonian", "native": "Eesti", "rtl": False, "tier": 3},
    "lv": {"name": "Latvian", "native": "Latviešu", "rtl": False, "tier": 3},
    "lt": {"name": "Lithuanian", "native": "Lietuvių", "rtl": False, "tier": 3},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "rtl": False, "tier": 3},
    "ml": {"name": "Malayalam", "native": "മലയാളം", "rtl": False, "tier": 3},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી", "rtl": False, "tier": 3},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ", "rtl": False, "tier": 3},
    "mr": {"name": "Marathi", "native": "मराठी", "rtl": False, "tier": 3},
    "or": {"name": "Odia", "native": "ଓଡ଼ିଆ", "rtl": False, "tier": 3},
    "as": {"name": "Assamese", "native": "অসমীয়া", "rtl": False, "tier": 3},
    "ne": {"name": "Nepali", "native": "नेपाली", "rtl": False, "tier": 3},
    "si": {"name": "Sinhala", "native": "සිංහල", "rtl": False, "tier": 3},
    "km": {"name": "Khmer", "native": "ខ្មែរ", "rtl": False, "tier": 3},
    "lo": {"name": "Lao", "native": "ລາວ", "rtl": False, "tier": 3},
    "bo": {"name": "Tibetan", "native": "བོད་ཡིག", "rtl": False, "tier": 3},
    "tl": {"name": "Filipino", "native": "Filipino", "rtl": False, "tier": 3},
    "sw": {"name": "Swahili", "native": "Kiswahili", "rtl": False, "tier": 3},
    "am": {"name": "Amharic", "native": "አማርኛ", "rtl": False, "tier": 3},
}

# Engine Configuration by Tier
TIER_CONFIGURATIONS = {
    1: {
        "engines": ["google", "microsoft", "openai", "local"],
        "cache_duration": 86400 * 7,  # 7 days
        "quality_threshold": 0.95,
        "features": ["real_time", "voice", "cultural_adaptation", "offline", "custom_glossary"],
        "max_retries": 3,
        "fallback_engines": ["microsoft", "google"]
    },
    2: {
        "engines": ["google", "microsoft", "openai"],
        "cache_duration": 86400 * 3,  # 3 days
        "quality_threshold": 0.90,
        "features": ["real_time", "cultural_adaptation", "custom_glossary"],
        "max_retries": 2,
        "fallback_engines": ["microsoft", "google"]
    },
    3: {
        "engines": ["google", "microsoft"],
        "cache_duration": 86400,  # 1 day
        "quality_threshold": 0.85,
        "features": ["real_time"],
        "max_retries": 1,
        "fallback_engines": ["google"]
    }
}

# Meditation-specific terminology domains
MEDITATION_DOMAINS = {
    "mindfulness": "General mindfulness practices",
    "buddhist": "Buddhist meditation traditions",
    "hindu": "Hindu and Vedic traditions",
    "yoga": "Yoga and pranayama practices",
    "zen": "Zen meditation practices",
    "vipassana": "Vipassana insight meditation",
    "loving_kindness": "Metta/loving-kindness practices",
    "body_scan": "Body awareness practices",
    "breathing": "Breath-focused techniques",
    "mantras": "Sacred sounds and chants"
}

settings = TranslationSettings()
