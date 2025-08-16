"""
Realistic test cases for STT Engine based on actual implementation
Tests the actual methods: transcribe(), load_model(), etc.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import numpy as np
from pathlib import Path
import tempfile
import shutil

# Import actual STTEngine
from models.stt_engine import STTEngine


class TestSTTEngineRealistic:
    """Test STTEngine with realistic method names and functionality"""
    
    @pytest.fixture
    def mock_model_manager(self):
        """Mock model manager"""
        manager = Mock()
        manager.get_model_path = Mock(return_value=Path("/mock/path"))
        manager.is_model_available = Mock(return_value=True)
        manager.model_configs = {
            "whisper_medium": {
                "type": "whisper",
                "model_id": "openai/whisper-medium",
                "languages": ["en", "hi", "es"]
            },
            "vosk_en_us": {
                "type": "vosk", 
                "languages": ["en"]
            }
        }
        return manager
    
    @pytest.fixture
    def stt_engine(self, mock_model_manager):
        """Create STTEngine instance"""
        return STTEngine(mock_model_manager)
    
    @pytest.fixture
    def sample_audio_data(self):
        """Generate sample audio data"""
        # Create 1 second of audio at 16kHz
        duration = 1.0
        sample_rate = 16000
        samples = int(duration * sample_rate)
        audio_data = np.random.uniform(-1, 1, samples).astype(np.float32)
        return audio_data, sample_rate

    def test_stt_engine_initialization(self, mock_model_manager):
        """Test STTEngine initialization"""
        engine = STTEngine(mock_model_manager)
        
        assert engine.model_manager == mock_model_manager
        assert hasattr(engine, 'loaded_models')
        assert hasattr(engine, 'supported_languages')
        assert isinstance(engine.loaded_models, dict)
        assert isinstance(engine.supported_languages, dict)
        
        # Check some expected languages
        assert "en" in engine.supported_languages
        assert "hi" in engine.supported_languages
        
    @pytest.mark.asyncio
    async def test_load_default_models_success(self, stt_engine):
        """Test loading default models successfully"""
        with patch.object(stt_engine, 'load_model', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = True
            
            await stt_engine.load_default_models()
            
            # Should have attempted to load some models
            assert mock_load.call_count >= 1
            
    @pytest.mark.asyncio 
    async def test_load_model_whisper_success(self, stt_engine):
        """Test loading Whisper model successfully"""
        model_name = "whisper_medium"
        
        with patch.object(stt_engine, '_load_whisper_model', new_callable=AsyncMock) as mock_load_whisper:
            mock_load_whisper.return_value = "mock_whisper_model"
            
            result = await stt_engine.load_model(model_name)
            
            assert result is True
            assert model_name in stt_engine.loaded_models
            mock_load_whisper.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_load_model_not_available(self, stt_engine):
        """Test loading model that's not available"""
        model_name = "nonexistent_model"
        stt_engine.model_manager.is_model_available.return_value = False
        
        result = await stt_engine.load_model(model_name)
        
        assert result is False
        assert model_name not in stt_engine.loaded_models
        
    @pytest.mark.asyncio
    async def test_transcribe_success(self, stt_engine, sample_audio_data):
        """Test successful transcription"""
        audio_data, sample_rate = sample_audio_data
        expected_result = {
            "success": True,
            "text": "hello world",
            "language": "en",
            "confidence": 0.95,
            "model_used": "whisper_medium"
        }
        
        with patch.object(stt_engine, '_preprocess_audio', new_callable=AsyncMock) as mock_preprocess, \
             patch.object(stt_engine, '_select_model', new_callable=AsyncMock) as mock_select, \
             patch.object(stt_engine, '_transcribe_whisper', new_callable=AsyncMock) as mock_transcribe:
            
            mock_preprocess.return_value = (audio_data, sample_rate)
            mock_select.return_value = "whisper_medium"
            mock_transcribe.return_value = expected_result
            
            # Add model to loaded_models
            stt_engine.loaded_models["whisper_medium"] = "mock_model"
            
            result = await stt_engine.transcribe(audio_data, language="en")
            
            assert result["success"] is True
            assert result["text"] == "hello world"
            mock_preprocess.assert_called_once()
            mock_select.assert_called_once()
            mock_transcribe.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_transcribe_no_models_loaded(self, stt_engine, sample_audio_data):
        """Test transcription when no models are loaded"""
        audio_data, _ = sample_audio_data
        
        with patch.object(stt_engine, '_preprocess_audio', new_callable=AsyncMock) as mock_preprocess, \
             patch.object(stt_engine, '_select_model', new_callable=AsyncMock) as mock_select:
            
            mock_preprocess.return_value = (audio_data, 16000)
            mock_select.return_value = None  # No model available
            
            result = await stt_engine.transcribe(audio_data)
            
            assert result["success"] is False
            assert "error" in result
            
    @pytest.mark.asyncio 
    async def test_transcribe_auto_language_detection(self, stt_engine, sample_audio_data):
        """Test transcription with auto language detection"""
        audio_data, sample_rate = sample_audio_data
        
        with patch.object(stt_engine, '_preprocess_audio', new_callable=AsyncMock) as mock_preprocess, \
             patch.object(stt_engine, '_select_model', new_callable=AsyncMock) as mock_select, \
             patch.object(stt_engine, '_transcribe_whisper', new_callable=AsyncMock) as mock_transcribe:
            
            mock_preprocess.return_value = (audio_data, sample_rate)
            mock_select.return_value = "whisper_medium"
            mock_transcribe.return_value = {
                "success": True,
                "text": "नमस्ते दुनिया",
                "language": "hi", 
                "confidence": 0.92
            }
            
            stt_engine.loaded_models["whisper_medium"] = "mock_model"
            
            result = await stt_engine.transcribe(audio_data, language="auto")
            
            assert result["success"] is True
            assert result["language"] == "hi"
            mock_select.assert_called_with("auto", None)
            
    @pytest.mark.asyncio
    async def test_preprocess_audio_numpy_array(self, stt_engine):
        """Test audio preprocessing with numpy array"""
        audio_data = np.random.uniform(-1, 1, 16000).astype(np.float32)
        
        with patch('librosa.resample') as mock_resample:
            mock_resample.return_value = audio_data
            
            result_audio, result_sr = await stt_engine._preprocess_audio(audio_data)
            
            assert isinstance(result_audio, np.ndarray)
            assert result_sr == 16000
            
    @pytest.mark.asyncio
    async def test_select_model_with_preference(self, stt_engine):
        """Test model selection with preference"""
        stt_engine.loaded_models = {
            "whisper_medium": "model1",
            "vosk_en_us": "model2"
        }
        
        result = await stt_engine._select_model("en", "whisper_medium")
        
        assert result == "whisper_medium"
        
    @pytest.mark.asyncio
    async def test_select_model_no_preference(self, stt_engine):
        """Test model selection without preference"""
        stt_engine.loaded_models = {
            "whisper_medium": "model1",
            "vosk_en_us": "model2"  
        }
        
        result = await stt_engine._select_model("en", None)
        
        # Should return first available model for language
        assert result in ["whisper_medium", "vosk_en_us"]
        
    @pytest.mark.asyncio
    async def test_transcribe_whisper_model(self, stt_engine):
        """Test Whisper transcription"""
        audio_data = np.random.uniform(-1, 1, 16000).astype(np.float32)
        sample_rate = 16000
        
        # Mock Whisper model
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "test transcription",
            "language": "en"
        }
        
        with patch('models.stt_engine.whisper') as mock_whisper:
            result = await stt_engine._transcribe_whisper(
                mock_model, audio_data, sample_rate, "en"
            )
            
            assert result["success"] is True
            assert "text" in result
            
    @pytest.mark.asyncio
    async def test_get_supported_languages(self, stt_engine):
        """Test getting supported languages"""
        result = await stt_engine.get_supported_languages()
        
        assert isinstance(result, dict)
        assert "en" in result
        assert "hi" in result
        assert isinstance(result["en"], list)
        
    @pytest.mark.asyncio
    async def test_unload_model(self, stt_engine):
        """Test unloading a model"""
        model_name = "whisper_medium"
        stt_engine.loaded_models[model_name] = "mock_model"
        
        await stt_engine.unload_model(model_name)
        
        assert model_name not in stt_engine.loaded_models
        
    @pytest.mark.asyncio
    async def test_cleanup(self, stt_engine):
        """Test cleanup of all models"""
        stt_engine.loaded_models = {
            "model1": "mock1",
            "model2": "mock2"
        }
        
        await stt_engine.cleanup()
        
        assert len(stt_engine.loaded_models) == 0


class TestSTTEngineEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.fixture
    def stt_engine(self):
        mock_manager = Mock()
        mock_manager.model_configs = {}
        return STTEngine(mock_manager)
    
    @pytest.mark.asyncio
    async def test_transcribe_with_invalid_audio(self, stt_engine):
        """Test transcription with invalid audio data"""
        invalid_audio = "not_audio_data"
        
        with patch.object(stt_engine, '_preprocess_audio', new_callable=AsyncMock) as mock_preprocess:
            mock_preprocess.side_effect = Exception("Invalid audio format")
            
            result = await stt_engine.transcribe(invalid_audio)
            
            assert result["success"] is False
            assert "error" in result
            
    @pytest.mark.asyncio
    async def test_load_model_whisper_import_error(self, stt_engine):
        """Test loading Whisper model when whisper is not available"""
        model_name = "whisper_medium"
        stt_engine.model_manager.is_model_available.return_value = True
        stt_engine.model_manager.model_configs = {
            model_name: {"type": "whisper"}
        }
        
        with patch('models.stt_engine.whisper', None):
            result = await stt_engine.load_model(model_name)
            
            assert result is False
            
    @pytest.mark.asyncio
    async def test_transcribe_model_error(self, stt_engine):
        """Test transcription when model throws error"""
        audio_data = np.random.uniform(-1, 1, 16000).astype(np.float32)
        
        with patch.object(stt_engine, '_preprocess_audio', new_callable=AsyncMock) as mock_preprocess, \
             patch.object(stt_engine, '_select_model', new_callable=AsyncMock) as mock_select, \
             patch.object(stt_engine, '_transcribe_whisper', new_callable=AsyncMock) as mock_transcribe:
            
            mock_preprocess.return_value = (audio_data, 16000)
            mock_select.return_value = "whisper_medium"
            mock_transcribe.side_effect = Exception("Model error")
            
            stt_engine.loaded_models["whisper_medium"] = "mock_model"
            
            result = await stt_engine.transcribe(audio_data)
            
            assert result["success"] is False
            assert "error" in result
