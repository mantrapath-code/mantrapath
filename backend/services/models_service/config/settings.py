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
    DEFAULT_STT_MODEL: str = "whisper_medium"
    DEFAULT_TTS_MODEL: str = "coqui_xtts_v2"
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
    INDIAN_LANGUAGES: Dict[str, Dict] = {
        "hi": {
            "name": "Hindi",
            "script": "Devanagari",
            "stt_models": ["vosk-hi", "wav2vec2-hi", "whisper-hi"],
            "tts_models": ["coqui-hi", "festival-hi", "espeak-hi"]
        },
        "bn": {
            "name": "Bengali",
            "script": "Bengali",
            "stt_models": ["vosk-bn", "wav2vec2-bn"],
            "tts_models": ["coqui-bn", "espeak-bn"]
        },
        "te": {
            "name": "Telugu",
            "script": "Telugu",
            "stt_models": ["vosk-te", "wav2vec2-te"],
            "tts_models": ["coqui-te", "espeak-te"]
        },
        "ta": {
            "name": "Tamil",
            "script": "Tamil",
            "stt_models": ["vosk-ta", "wav2vec2-ta"],
            "tts_models": ["coqui-ta", "espeak-ta"]
        },
        "mr": {
            "name": "Marathi",
            "script": "Devanagari",
            "stt_models": ["vosk-mr", "wav2vec2-mr"],
            "tts_models": ["coqui-mr", "espeak-mr"]
        },
        "gu": {
            "name": "Gujarati",
            "script": "Gujarati",
            "stt_models": ["vosk-gu"],
            "tts_models": ["coqui-gu", "espeak-gu"]
        },
        "kn": {
            "name": "Kannada",
            "script": "Kannada",
            "stt_models": ["vosk-kn"],
            "tts_models": ["coqui-kn", "espeak-kn"]
        },
        "ml": {
            "name": "Malayalam",
            "script": "Malayalam",
            "stt_models": ["vosk-ml"],
            "tts_models": ["coqui-ml", "espeak-ml"]
        },
        "pa": {
            "name": "Punjabi",
            "script": "Gurmukhi",
            "stt_models": ["vosk-pa"],
            "tts_models": ["espeak-pa"]
        },
        "or": {
            "name": "Odia",
            "script": "Odia",
            "stt_models": ["vosk-or"],
            "tts_models": ["espeak-or"]
        },
        "as": {
            "name": "Assamese",
            "script": "Bengali",
            "stt_models": ["vosk-as"],
            "tts_models": ["espeak-as"]
        }
    }
    
    # Model URLs and Configurations
    MODEL_CONFIGS: Dict[str, Dict] = {
        # Whisper Models
        "whisper_tiny": {
            "type": "stt",
            "engine": "whisper",
            "size": "39MB",
            "languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "hi", "bn"],
            "quality": "fast",
            "device": ["cpu", "gpu"]
        },
        "whisper_base": {
            "type": "stt", 
            "engine": "whisper",
            "size": "74MB",
            "languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "hi", "bn"],
            "quality": "good",
            "device": ["cpu", "gpu"]
        },
        "whisper_small": {
            "type": "stt",
            "engine": "whisper", 
            "size": "244MB",
            "languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "hi", "bn"],
            "quality": "better",
            "device": ["cpu", "gpu"]
        },
        "whisper_medium": {
            "type": "stt",
            "engine": "whisper",
            "size": "769MB", 
            "languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "hi", "bn"],
            "quality": "high",
            "device": ["cpu", "gpu"]
        },
        "whisper_large": {
            "type": "stt",
            "engine": "whisper",
            "size": "1550MB",
            "languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "hi", "bn"],
            "quality": "highest",
            "device": ["gpu"]
        },
        
        # Vosk Models (including Indian languages)
        "vosk_en_us": {
            "type": "stt",
            "engine": "vosk",
            "url": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
            "size": "1.8GB",
            "languages": ["en"],
            "quality": "high",
            "device": ["cpu"]
        },
        "vosk_en_us_small": {
            "type": "stt",
            "engine": "vosk",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip", 
            "size": "40MB",
            "languages": ["en"],
            "quality": "fast",
            "device": ["cpu"]
        },
        "vosk_hi": {
            "type": "stt",
            "engine": "vosk",
            "url": "https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip",
            "size": "1.1GB",
            "languages": ["hi"],
            "quality": "good",
            "device": ["cpu"]
        },
        "vosk_hi_small": {
            "type": "stt", 
            "engine": "vosk",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip",
            "size": "45MB",
            "languages": ["hi"],
            "quality": "fast",
            "device": ["cpu"]
        },
        
        # Wav2Vec2 Models for Indian Languages
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
        
        # Coqui TTS Models
        "coqui_xtts_v2": {
            "type": "tts",
            "engine": "coqui",
            "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
            "size": "6GB",
            "languages": ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh", "hu", "ko", "ja", "hi"],
            "quality": "highest",
            "device": ["gpu"],
            "features": ["voice_cloning", "multilingual"]
        },
        "coqui_bark": {
            "type": "tts",
            "engine": "coqui",
            "model_name": "tts_models/multilingual/multi-dataset/bark",
            "size": "10GB",
            "languages": ["en", "de", "es", "fr", "hi", "it", "ja", "ko", "pl", "pt", "ru", "tr", "zh"],
            "quality": "highest",
            "device": ["gpu"],
            "features": ["emotional_speech", "multilingual"]
        },
        
        # Indian TTS Models (Coqui Fine-tuned)
        "coqui_hi": {
            "type": "tts",
            "engine": "coqui",
            "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
            "size": "1.9GB",
            "languages": ["hi", "en", "es", "fr", "de", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja"],
            "quality": "excellent",
            "device": ["cpu", "gpu"],
            "features": ["multilingual", "voice_cloning", "emotional_speech"]
        },
        "coqui_bn": {
            "type": "tts",
            "engine": "coqui", 
            "model_name": "tts_models/bn/male/tacotron2-DDC",
            "size": "200MB",
            "languages": ["bn"],
            "quality": "good",
            "device": ["cpu", "gpu"]
        },
        
        # Festival/eSpeak for Indian Languages
        "festival_hi": {
            "type": "tts",
            "engine": "festival",
            "voice": "hindi_male",
            "size": "50MB",
            "languages": ["hi"],
            "quality": "basic",
            "device": ["cpu"]
        },
        "espeak_hi": {
            "type": "tts",
            "engine": "espeak",
            "voice": "hi",
            "size": "10MB", 
            "languages": ["hi"],
            "quality": "basic",
            "device": ["cpu"]
        }
    }
    
    # API Fallback Configuration
    FALLBACK_APIS: Dict[str, Dict] = {
        "openai_whisper": {
            "type": "stt",
            "api_key_env": "OPENAI_API_KEY",
            "endpoint": "https://api.openai.com/v1/audio/transcriptions",
            "languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "hi"],
            "max_file_size": "25MB"
        },
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
