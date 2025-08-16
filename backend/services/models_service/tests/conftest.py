"""
Test configuration and fixtures
"""

import pytest
import pytest_asyncio
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
import torch
import numpy as np
import json
import logging

# Disable logging during tests
logging.disable(logging.CRITICAL)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_models_dir():
    """Create temporary models directory"""
    temp_dir = tempfile.mkdtemp()
    models_dir = Path(temp_dir) / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    yield models_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_audio_data():
    """Generate sample audio data for testing"""
    # Generate 1 second of 16kHz audio (silence)
    duration = 1.0  # seconds
    sample_rate = 16000
    samples = int(duration * sample_rate)
    audio_data = np.zeros(samples, dtype=np.float32)
    return audio_data, sample_rate

@pytest.fixture
def sample_wav_file(sample_audio_data, temp_models_dir):
    """Create a sample WAV file for testing"""
    import soundfile as sf
    audio_data, sample_rate = sample_audio_data
    wav_path = temp_models_dir / "test_audio.wav"
    sf.write(str(wav_path), audio_data, sample_rate)
    return wav_path

@pytest.fixture
def mock_model_config():
    """Mock model configuration"""
    return {
        "test_model": {
            "type": "stt",
            "engine": "whisper",
            "languages": ["en", "hi"],
            "quality": "good",
            "device": ["cpu"],
            "size_mb": 100,
            "download_url": "https://example.com/test_model.zip"
        },
        "tts_test_model": {
            "type": "tts",
            "engine": "coqui",
            "languages": ["en"],
            "quality": "high",
            "device": ["cpu", "gpu"],
            "size_mb": 200
        }
    }

@pytest.fixture
def mock_settings(temp_models_dir, mock_model_config):
    """Mock settings for testing"""
    settings = Mock()
    settings.MODELS_DIR = temp_models_dir
    settings.MODEL_CONFIGS = mock_model_config
    settings.REDIS_URL = "redis://localhost:6379/10"  # Test database
    settings.MAX_CACHE_SIZE_GB = 5
    settings.DOWNLOAD_TIMEOUT = 30
    settings.INDIAN_LANGUAGES = {
        "hi": {
            "name": "Hindi",
            "stt_models": ["whisper", "vosk"],
            "tts_models": ["coqui", "espeak"]
        },
        "bn": {
            "name": "Bengali", 
            "stt_models": ["whisper"],
            "tts_models": ["espeak"]
        }
    }
    return settings

@pytest.fixture
def mock_torch():
    """Mock torch operations"""
    with patch('torch.cuda.is_available', return_value=False), \
         patch('torch.cuda.device_count', return_value=0), \
         patch('torch.load') as mock_load:
        mock_load.return_value = Mock()
        yield mock_load

@pytest.fixture
def mock_model_manager(temp_models_dir, mock_model_config):
    """Mock ModelManager for testing"""
    from models.model_manager import ModelManager
    
    manager = Mock(spec=ModelManager)
    manager.models_dir = temp_models_dir
    manager.available_models = {}
    manager.loaded_models = {}
    manager.model_configs = mock_model_config
    manager.download_progress = {}
    manager.downloading = set()
    manager.model_usage_stats = {}
    
    # Mock async methods
    manager.initialize = AsyncMock()
    manager.download_model = AsyncMock(return_value=True)
    manager.get_available_models = AsyncMock(return_value=mock_model_config)
    manager.is_model_available = Mock(return_value=True)
    manager.get_model_path = Mock(return_value=temp_models_dir / "test_model")
    manager.cleanup = AsyncMock()
    
    return manager

@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis_mock = AsyncMock()
    redis_mock.ping = AsyncMock(return_value=True)
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.exists = AsyncMock(return_value=False)
    redis_mock.close = AsyncMock()
    return redis_mock

@pytest.fixture
def test_client():
    """Create test client for FastAPI app"""
    # Import here to avoid circular imports
    from main import app
    return TestClient(app)

@pytest.fixture
def mock_whisper():
    """Mock Whisper model"""
    whisper_mock = Mock()
    whisper_mock.transcribe = Mock(return_value={
        "text": "test transcription",
        "language": "en",
        "segments": []
    })
    return whisper_mock

@pytest.fixture
def mock_coqui_model():
    """Mock Coqui TTS model"""
    coqui_mock = Mock()
    coqui_mock.tts = Mock(return_value=np.array([0.1, 0.2, 0.3]))
    coqui_mock.speakers = ["speaker1", "speaker2"]
    return coqui_mock

@pytest.fixture
def create_test_model_dir(temp_models_dir):
    """Create a test model directory with config"""
    def _create(model_name, model_type="stt", engine="whisper"):
        model_dir = temp_models_dir / model_name
        model_dir.mkdir(exist_ok=True)
        
        config = {
            "model_type": engine,
            "model_name": model_name,
            "languages": ["en"],
            "version": "1.0",
            "engine": engine,
            "created": "2024-01-01"
        }
        
        config_file = model_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        # Create dummy model file
        model_file = model_dir / "model.bin"
        model_file.write_bytes(b"dummy model data")
        
        return model_dir
    
    return _create
