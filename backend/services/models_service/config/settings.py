"""
Configuration settings for Models Service
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Dict, List, Optional

class Settings(BaseSettings):
    """Application settings"""
    
    model_config = {
        "extra": "allow",  # Allow extra fields for Pydantic v2
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }
    
    # Service Configuration
    SERVICE_NAME: str = "models_service"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int = 8080
    DEBUG: bool = False
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    MODELS_DIR: Path = BASE_DIR / "models"
    CACHE_DIR: Path = BASE_DIR / "cache"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Model Configuration
    # Updated defaults (informational; engines handle selection internally)
    DEFAULT_STT_MODEL: str = "wav2vec2_hi"  # Legacy field; strict IndicWav2Vec path now enforced
    DEFAULT_TTS_MODEL: str = "mms_tts_hi"   # MMS handled directly; not part of MODEL_CONFIGS
    DEFAULT_NLP_MODEL: str = "sentence_transformers"
    
    # Hardware Settings
    USE_GPU: bool = True
    MAX_GPU_MEMORY: float = 0.8  # Use 80% of GPU memory
    TORCH_DEVICE: str = "auto"  # auto, cpu, cuda
    
    # Performance Settings
    MAX_CONCURRENT_REQUESTS: int = 10
    MODEL_CACHE_SIZE: int = 5
    REQUEST_TIMEOUT: int = 300  # seconds
    
    # Indian Languages Configuration
    # Pruned Indian language configuration (legacy engines removed)
    # We retain only wav2vec2 entries for transparency; MMS TTS handled outside config.
    INDIAN_LANGUAGES: Dict[str, Dict] = {
        "hi": {"name": "Hindi", "script": "Devanagari", "stt_models": ["wav2vec2-hi"], "tts_models": []},
        "bn": {"name": "Bengali", "script": "Bengali", "stt_models": ["wav2vec2-bn"], "tts_models": []},
        "te": {"name": "Telugu", "script": "Telugu", "stt_models": ["wav2vec2-te"], "tts_models": []},
        "ta": {"name": "Tamil", "script": "Tamil", "stt_models": ["wav2vec2-ta"], "tts_models": []},
        "mr": {"name": "Marathi", "script": "Devanagari", "stt_models": ["wav2vec2-mr"], "tts_models": []},
        "gu": {"name": "Gujarati", "script": "Gujarati", "stt_models": ["wav2vec2-gu"], "tts_models": []},
        "kn": {"name": "Kannada", "script": "Kannada", "stt_models": ["wav2vec2-kn"], "tts_models": []},
        "ml": {"name": "Malayalam", "script": "Malayalam", "stt_models": ["wav2vec2-ml"], "tts_models": []},
        "pa": {"name": "Punjabi", "script": "Gurmukhi", "stt_models": ["wav2vec2-pa"], "tts_models": []},
        "or": {"name": "Odia", "script": "Odia", "stt_models": ["wav2vec2-or"], "tts_models": []},
        "as": {"name": "Assamese", "script": "Bengali", "stt_models": ["wav2vec2-as"], "tts_models": []}
    }
    
    # Model URLs and Configurations
    MODEL_CONFIGS: Dict[str, Dict] = {
        # Retained Wav2Vec2 models (still downloadable if needed by legacy paths)
        "wav2vec2_hi": {
            "type": "stt",
            "engine": "wav2vec2",
            "model_id": "facebook/wav2vec2-large-xlsr-53-hindi",
            "size": "1.2GB",
            "languages": ["hi"],
            "quality": "high",
            "device": ["cpu", "gpu"]
        },
        "wav2vec2_bn": {
            "type": "stt",
            "engine": "wav2vec2", 
            "model_id": "facebook/wav2vec2-large-xlsr-53-bengali",
            "size": "1.2GB",
            "languages": ["bn"],
            "quality": "high", 
            "device": ["cpu", "gpu"]
        },
        "wav2vec2_te": {
            "type": "stt",
            "engine": "wav2vec2",
            "model_id": "facebook/wav2vec2-large-xlsr-53-telugu", 
            "size": "1.2GB",
            "languages": ["te"],
            "quality": "high",
            "device": ["cpu", "gpu"]
        },
        "wav2vec2_ta": {
            "type": "stt",
            "engine": "wav2vec2",
            "model_id": "facebook/wav2vec2-large-xlsr-53-tamil",
            "size": "1.2GB", 
            "languages": ["ta"],
            "quality": "high",
            "device": ["cpu", "gpu"]
        },
        # (TTS via MMS/Indic not listed: loaded dynamically by TTSEngine)
    }
    
    # API Fallback Configuration
    FALLBACK_APIS: Dict[str, Dict] = {
        # Removed OpenAI Whisper fallback; relying on internal/self-hosted models only
        "elevenlabs": {
            "type": "tts",
            "api_key_env": "ELEVENLABS_API_KEY",
            "endpoint": "https://api.elevenlabs.io/v1/text-to-speech",
            "languages": ["en", "es", "fr", "de", "it", "pt"],
            "max_text_length": 2500
        },
        "azure_speech": {
            "type": "both",
            "api_key_env": "AZURE_SPEECH_KEY",
            "region_env": "AZURE_SPEECH_REGION",
            "endpoint": "https://{region}.api.cognitive.microsoft.com/sts/v1.0/issuetoken",
            "languages": ["en", "es", "fr", "de", "it", "pt", "hi", "bn", "te", "ta", "mr", "gu"],
            "features": ["real_time", "batch"]
        },
        "google_speech": {
            "type": "both",
            "api_key_env": "GOOGLE_CLOUD_API_KEY",
            "endpoint": "https://speech.googleapis.com/v1/speech:recognize",
            "languages": ["en", "es", "fr", "de", "it", "pt", "hi", "bn", "te", "ta", "mr", "gu", "kn", "ml"],
            "features": ["streaming", "batch"]
        }
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Create directories
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
