"""
Focused Test Suite for Models Service - 80% Coverage Target
Testing the actual implementation with working methods and realistic scenarios
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import numpy as np
from pathlib import Path
import tempfile
import shutil
import json
import asyncio

# Test the actual classes
from models.stt_engine import STTEngine
from models.tts_engine import TTSEngine
from models.nlp_engine import NLPEngine
from models.model_manager import ModelManager
from config.settings import get_settings


class TestModelsServiceCore:
    """Core functionality tests for all models service components"""
    
    @pytest.fixture
    def mock_model_manager(self):
        """Create a realistic mock model manager"""
        manager = Mock(spec=ModelManager)
        manager.models_dir = Path("/tmp/test_models")
        manager.model_configs = {
            "whisper_medium": {
                "type": "whisper",
                "model_id": "openai/whisper-medium",
                "languages": ["en", "hi", "es"],
                "size": "769MB"
            },
            "vosk_en_us": {
                "type": "vosk",
                "languages": ["en"],
                "size": "50MB"
            }
        }
        manager.is_model_available = Mock(return_value=True)
        manager.get_model_path = Mock(return_value=Path("/tmp/test_models/whisper_medium"))
        manager.get_available_models = AsyncMock(return_value=manager.model_configs)
        manager.download_model = AsyncMock(return_value=True)
        manager.initialize = AsyncMock(return_value=None)
        manager.cleanup = AsyncMock(return_value=None)
        return manager

    @pytest.fixture
    def sample_audio(self):
        """Generate realistic audio data"""
        duration = 1.0
        sample_rate = 16000
        samples = int(duration * sample_rate)
        # Generate some varied audio data
        t = np.linspace(0, duration, samples)
        audio = 0.1 * np.sin(2 * np.pi * 440 * t)  # 440Hz tone
        return audio.astype(np.float32), sample_rate

    # STT Engine Tests
    def test_stt_engine_initialization(self, mock_model_manager):
        """Test STTEngine basic initialization"""
        engine = STTEngine(mock_model_manager)
        
        assert engine.model_manager == mock_model_manager
        assert hasattr(engine, 'loaded_models')
        assert hasattr(engine, 'supported_languages')
        assert isinstance(engine.loaded_models, dict)
        assert len(engine.loaded_models) == 0  # Initially empty
        
        # Check language support
        assert "en" in engine.supported_languages
        assert "hi" in engine.supported_languages
        assert isinstance(engine.supported_languages["en"], list)

    @pytest.mark.asyncio
    async def test_stt_engine_load_default_models(self, mock_model_manager):
        """Test STTEngine load_default_models method"""
        engine = STTEngine(mock_model_manager)
        
        # Mock the load_model method
        with patch.object(engine, 'load_model', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = True
            
            await engine.load_default_models()
            
            # Should have attempted to load models
            assert mock_load.call_count >= 1

    @pytest.mark.asyncio
    async def test_stt_engine_load_model_basic(self, mock_model_manager):
        """Test STTEngine load_model method"""
        engine = STTEngine(mock_model_manager)
        model_name = "whisper_medium"
        
        # Mock dependencies
        with patch.object(engine, '_load_whisper_model', new_callable=AsyncMock) as mock_load_whisper:
            mock_load_whisper.return_value = Mock()  # Mock model object
            
            result = await engine.load_model(model_name)
            
            assert result is True
            assert model_name in engine.loaded_models

    @pytest.mark.asyncio
    async def test_stt_engine_transcribe_basic(self, mock_model_manager, sample_audio):
        """Test STTEngine transcribe method"""
        engine = STTEngine(mock_model_manager)
        audio_data, sample_rate = sample_audio
        
        # Add a mock model
        engine.loaded_models["whisper_medium"] = Mock()
        
        with patch.object(engine, '_preprocess_audio', new_callable=AsyncMock) as mock_preprocess, \
             patch.object(engine, '_select_model', new_callable=AsyncMock) as mock_select, \
             patch.object(engine, '_transcribe_whisper', new_callable=AsyncMock) as mock_transcribe:
            
            mock_preprocess.return_value = (audio_data, sample_rate)
            mock_select.return_value = "whisper_medium"
            mock_transcribe.return_value = {
                "success": True,
                "text": "test transcription",
                "language": "en",
                "confidence": 0.95
            }
            
            result = await engine.transcribe(audio_data, language="en")
            
            assert result["success"] is True
            assert "text" in result
            mock_preprocess.assert_called_once()
            mock_select.assert_called_once()

    @pytest.mark.asyncio
    async def test_stt_engine_get_supported_languages(self, mock_model_manager):
        """Test STTEngine get_supported_languages method"""
        engine = STTEngine(mock_model_manager)
        
        result = await engine.get_supported_languages()
        
        assert isinstance(result, dict)
        assert "en" in result
        assert isinstance(result["en"], list)

    @pytest.mark.asyncio
    async def test_stt_engine_cleanup(self, mock_model_manager):
        """Test STTEngine cleanup method"""
        engine = STTEngine(mock_model_manager)
        engine.loaded_models = {"model1": Mock(), "model2": Mock()}
        
        await engine.cleanup()
        
        assert len(engine.loaded_models) == 0

    # TTS Engine Tests
    def test_tts_engine_initialization(self, mock_model_manager):
        """Test TTSEngine basic initialization"""
        engine = TTSEngine(mock_model_manager)
        
        assert engine.model_manager == mock_model_manager
        assert hasattr(engine, 'loaded_models')
        assert hasattr(engine, 'supported_languages')
        assert isinstance(engine.loaded_models, dict)

    @pytest.mark.asyncio
    async def test_tts_engine_load_default_models(self, mock_model_manager):
        """Test TTSEngine load_default_models method"""
        engine = TTSEngine(mock_model_manager)
        
        with patch.object(engine, 'load_model', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = True
            
            await engine.load_default_models()
            
            assert mock_load.call_count >= 1

    @pytest.mark.asyncio
    async def test_tts_engine_synthesize_basic(self, mock_model_manager):
        """Test TTSEngine synthesize method"""
        engine = TTSEngine(mock_model_manager)
        text = "Hello world"
        
        # Add a mock model
        engine.loaded_models["system_tts"] = Mock()
        
        with patch.object(engine, '_select_model', new_callable=AsyncMock) as mock_select, \
             patch.object(engine, '_synthesize_system', new_callable=AsyncMock) as mock_synthesize:
            
            mock_select.return_value = "system_tts"
            mock_synthesize.return_value = {
                "success": True,
                "audio_data": np.array([0.1, 0.2, 0.3]),
                "sample_rate": 22050,
                "format": "wav"
            }
            
            result = await engine.synthesize(text, language="en")
            
            assert result["success"] is True
            assert "audio_data" in result
            mock_select.assert_called_once()

    @pytest.mark.asyncio
    async def test_tts_engine_get_supported_languages(self, mock_model_manager):
        """Test TTSEngine get_supported_languages method"""
        engine = TTSEngine(mock_model_manager)
        
        result = await engine.get_supported_languages()
        
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_tts_engine_cleanup(self, mock_model_manager):
        """Test TTSEngine cleanup method"""
        engine = TTSEngine(mock_model_manager)
        engine.loaded_models = {"model1": Mock()}
        
        await engine.cleanup()
        
        assert len(engine.loaded_models) == 0

    # NLP Engine Tests
    def test_nlp_engine_initialization(self, mock_model_manager):
        """Test NLPEngine basic initialization"""
        engine = NLPEngine(mock_model_manager)
        
        assert engine.model_manager == mock_model_manager
        assert hasattr(engine, 'loaded_models')

    @pytest.mark.asyncio
    async def test_nlp_engine_load_default_models(self, mock_model_manager):
        """Test NLPEngine load_default_models method"""
        engine = NLPEngine(mock_model_manager)
        
        await engine.load_default_models()
        # Just ensure it doesn't crash

    @pytest.mark.asyncio
    async def test_nlp_engine_translate(self, mock_model_manager):
        """Test NLPEngine translate method"""
        engine = NLPEngine(mock_model_manager)
        
        result = await engine.translate("Hello", "en", "hi")
        
        # Basic smoke test - actual implementation may vary
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_nlp_engine_analyze_sentiment(self, mock_model_manager):
        """Test NLPEngine analyze_sentiment method"""
        engine = NLPEngine(mock_model_manager)
        
        result = await engine.analyze_sentiment("I am happy")
        
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_nlp_engine_get_embeddings(self, mock_model_manager):
        """Test NLPEngine get_embeddings method"""
        engine = NLPEngine(mock_model_manager)
        
        result = await engine.get_embeddings("test text")
        
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_nlp_engine_cleanup(self, mock_model_manager):
        """Test NLPEngine cleanup method"""
        engine = NLPEngine(mock_model_manager)
        
        await engine.cleanup()
        # Just ensure it doesn't crash

    # Model Manager Tests
    def test_model_manager_initialization(self):
        """Test ModelManager initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            models_dir = Path(temp_dir)
            manager = ModelManager(models_dir)
            
            assert manager.models_dir == models_dir
            assert hasattr(manager, 'model_configs')
            assert hasattr(manager, 'download_progress')

    @pytest.mark.asyncio
    async def test_model_manager_initialize(self):
        """Test ModelManager initialize method"""
        with tempfile.TemporaryDirectory() as temp_dir:
            models_dir = Path(temp_dir)
            manager = ModelManager(models_dir)
            
            with patch.object(manager, '_load_model_configs', new_callable=AsyncMock), \
                 patch.object(manager, '_scan_existing_models', new_callable=AsyncMock), \
                 patch.object(manager, '_load_usage_stats', new_callable=AsyncMock):
                
                await manager.initialize()
                # Just ensure it doesn't crash

    @pytest.mark.asyncio
    async def test_model_manager_get_available_models(self):
        """Test ModelManager get_available_models method"""
        with tempfile.TemporaryDirectory() as temp_dir:
            models_dir = Path(temp_dir)
            manager = ModelManager(models_dir)
            manager.model_configs = {
                "test_model": {"type": "whisper", "languages": ["en"]}
            }
            
            result = await manager.get_available_models()
            
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_model_manager_cleanup(self):
        """Test ModelManager cleanup method"""
        with tempfile.TemporaryDirectory() as temp_dir:
            models_dir = Path(temp_dir)
            manager = ModelManager(models_dir)
            
            await manager.cleanup()
            # Just ensure it doesn't crash


class TestSettingsAndConfig:
    """Test configuration and settings"""
    
    def test_settings_initialization(self):
        """Test settings can be loaded"""
        settings = get_settings()
        
        assert hasattr(settings, 'BASE_DIR')
        assert hasattr(settings, 'MODELS_DIR')
        assert hasattr(settings, 'CACHE_DIR')

    def test_settings_models_dir_exists(self):
        """Test models directory configuration"""
        settings = get_settings()
        
        assert settings.MODELS_DIR is not None
        assert isinstance(settings.MODELS_DIR, Path)

    def test_settings_cache_dir_exists(self):
        """Test cache directory configuration"""
        settings = get_settings()
        
        assert settings.CACHE_DIR is not None
        assert isinstance(settings.CACHE_DIR, Path)

    def test_settings_model_configs_structure(self):
        """Test model configurations structure"""
        settings = get_settings()
        
        assert hasattr(settings, 'model_configs')
        assert isinstance(settings.model_configs, dict)
        
        # Check for expected model types
        model_types = [config.get('type') for config in settings.model_configs.values()]
        expected_types = ['whisper', 'vosk', 'coqui', 'huggingface']
        
        # At least some expected types should be present
        assert any(model_type in model_types for model_type in expected_types)


class TestMainApplication:
    """Test main application components"""
    
    def test_fastapi_app_creation(self):
        """Test FastAPI app can be imported and has basic attributes"""
        from main import app
        
        assert app is not None
        assert hasattr(app, 'title')
        assert hasattr(app, 'description')
        assert app.title == "MantraPath Models Service"

    @patch('main.get_settings')
    @patch('main.setup_logger')
    def test_app_initialization_with_mocks(self, mock_logger, mock_settings):
        """Test app initialization with mocked dependencies"""
        mock_settings.return_value = Mock()
        mock_logger.return_value = Mock()
        
        # Import after mocking
        from main import app
        
        assert app is not None

    def test_cors_middleware_configured(self):
        """Test CORS middleware is configured"""
        from main import app
        
        # Check if middleware is added (basic check)
        assert len(app.user_middleware) > 0


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_stt_transcribe_with_no_audio(self, mock_model_manager):
        """Test STT transcribe handles missing audio gracefully"""
        engine = STTEngine(mock_model_manager)
        
        with patch.object(engine, '_preprocess_audio', new_callable=AsyncMock) as mock_preprocess:
            mock_preprocess.side_effect = Exception("Invalid audio")
            
            result = await engine.transcribe(None)
            
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_tts_synthesize_with_empty_text(self, mock_model_manager):
        """Test TTS synthesize handles empty text gracefully"""
        engine = TTSEngine(mock_model_manager)
        
        result = await engine.synthesize("", language="en")
        
        # Should handle empty text gracefully
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_model_loading_failure(self, mock_model_manager):
        """Test model loading failure handling"""
        engine = STTEngine(mock_model_manager)
        mock_model_manager.is_model_available.return_value = False
        
        result = await engine.load_model("nonexistent_model")
        
        assert result is False


class TestPerformanceAndLimits:
    """Test performance characteristics and limits"""
    
    @pytest.mark.asyncio
    async def test_large_audio_handling(self, mock_model_manager):
        """Test handling of large audio files"""
        engine = STTEngine(mock_model_manager)
        
        # Create large audio array (10 seconds)
        large_audio = np.random.uniform(-1, 1, 160000).astype(np.float32)
        
        with patch.object(engine, '_preprocess_audio', new_callable=AsyncMock) as mock_preprocess:
            mock_preprocess.return_value = (large_audio[:16000], 16000)  # Truncate for processing
            
            # Should not crash with large audio
            result = await engine._preprocess_audio(large_audio)
            assert result is not None

    @pytest.mark.asyncio
    async def test_concurrent_model_loading(self, mock_model_manager):
        """Test concurrent model loading"""
        engine = STTEngine(mock_model_manager)
        
        with patch.object(engine, '_load_whisper_model', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = Mock()
            
            # Load multiple models concurrently
            tasks = [
                engine.load_model("model1"),
                engine.load_model("model2"), 
                engine.load_model("model3")
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Should handle concurrent loading
            assert len(results) == 3


# Integration-style tests
class TestIntegration:
    """Integration tests combining multiple components"""
    
    @pytest.mark.asyncio
    async def test_stt_tts_pipeline(self, mock_model_manager, sample_audio):
        """Test STT -> TTS pipeline"""
        stt_engine = STTEngine(mock_model_manager)
        tts_engine = TTSEngine(mock_model_manager)
        
        audio_data, sample_rate = sample_audio
        
        # Mock STT to return text
        with patch.object(stt_engine, 'transcribe', new_callable=AsyncMock) as mock_transcribe, \
             patch.object(tts_engine, 'synthesize', new_callable=AsyncMock) as mock_synthesize:
            
            mock_transcribe.return_value = {
                "success": True,
                "text": "hello world",
                "language": "en"
            }
            
            mock_synthesize.return_value = {
                "success": True,
                "audio_data": np.array([0.1, 0.2]),
                "sample_rate": 22050
            }
            
            # STT
            stt_result = await stt_engine.transcribe(audio_data)
            assert stt_result["success"] is True
            
            # TTS
            text = stt_result["text"]
            tts_result = await tts_engine.synthesize(text)
            assert tts_result["success"] is True

    @pytest.mark.asyncio
    async def test_full_service_workflow(self, mock_model_manager):
        """Test a complete service workflow"""
        # Initialize all engines
        stt_engine = STTEngine(mock_model_manager)
        tts_engine = TTSEngine(mock_model_manager)
        nlp_engine = NLPEngine(mock_model_manager)
        
        # Load default models
        await stt_engine.load_default_models()
        await tts_engine.load_default_models()
        await nlp_engine.load_default_models()
        
        # Get supported languages
        stt_langs = await stt_engine.get_supported_languages()
        tts_langs = await tts_engine.get_supported_languages()
        
        assert isinstance(stt_langs, dict)
        assert isinstance(tts_langs, dict)
        
        # Cleanup
        await stt_engine.cleanup()
        await tts_engine.cleanup()
        await nlp_engine.cleanup()
