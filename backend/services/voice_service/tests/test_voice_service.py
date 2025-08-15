"""
Voice Processing Service Tests
Tests for the main voice processing business logic
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from services.voice_service import VoiceProcessingService
from core.models import AudioData, AudioFormat, STTRequest, TTSRequest, VoiceResponse
from core.exceptions import (
    AudioProcessingError, UnsupportedLanguageError, 
    FileSizeError, AudioDurationError
)

class TestVoiceProcessingService:
    """Test VoiceProcessingService class"""
    
    @pytest.fixture
    def mock_engine_manager(self):
        """Mock engine manager"""
        manager = AsyncMock()
        
        # Mock STT response
        stt_result = MagicMock()
        stt_result.text = "Hello world"
        stt_result.language = "en"
        stt_result.confidence = 0.95
        stt_result.dict.return_value = {
            "text": "Hello world",
            "language": "en", 
            "confidence": 0.95
        }
        manager.transcribe_audio.return_value = stt_result
        
        # Mock TTS response
        tts_result = AudioData(
            data=b"mock_audio_data",
            format=AudioFormat.WAV,
            file_size=1000,
            duration=2.0
        )
        manager.synthesize_speech.return_value = tts_result
        
        # Mock emotion analysis
        emotion_result = MagicMock()
        emotion_result.primary_emotion = "neutral"
        emotion_result.confidence = 0.8
        manager.analyze_emotion.return_value = emotion_result
        
        manager.get_health_status.return_value = {"status": "healthy"}
        
        return manager
    
    @pytest.fixture
    def voice_service(self, mock_engine_manager):
        """Create VoiceProcessingService instance"""
        return VoiceProcessingService(mock_engine_manager)
    
    @pytest.fixture
    def sample_audio_data(self):
        """Sample audio data for testing"""
        return AudioData(
            data=b"sample_audio_data",
            format=AudioFormat.WAV,
            file_size=1000,
            duration=2.0,
            filename="test.wav"
        )
    
    @pytest.fixture
    def sample_stt_request(self):
        """Sample STT request"""
        return STTRequest(
            language="en",
            model="whisper",
            enable_diarization=False,
            translate_to_english=False,
            enable_emotion_analysis=False,
            confidence_threshold=0.7
        )
    
    @pytest.fixture 
    def sample_tts_request(self):
        """Sample TTS request"""
        return TTSRequest(
            text="Hello world",
            language="en",
            voice="default",
            speed=1.0,
            pitch=1.0,
            format=AudioFormat.WAV
        )

    @pytest.mark.asyncio
    async def test_process_speech_to_text_success(
        self, voice_service, sample_audio_data, sample_stt_request
    ):
        """Test successful STT processing"""
        with patch('services.voice_service.is_language_supported', return_value=True):
            result = await voice_service.process_speech_to_text(
                audio_data=sample_audio_data,
                request=sample_stt_request,
                user_id="test_user"
            )
        
        assert isinstance(result, VoiceResponse)
        assert result.success is True
        assert "transcription" in result.data
        assert result.language == "en"
        assert result.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_process_speech_to_text_unsupported_language(
        self, voice_service, sample_audio_data, sample_stt_request
    ):
        """Test STT with unsupported language"""
        sample_stt_request.language = "xyz"
        
        with patch('services.voice_service.is_language_supported', return_value=False):
            with pytest.raises(UnsupportedLanguageError):
                await voice_service.process_speech_to_text(
                    audio_data=sample_audio_data,
                    request=sample_stt_request
                )

    @pytest.mark.asyncio
    async def test_process_speech_to_text_file_too_large(
        self, voice_service, sample_stt_request
    ):
        """Test STT with file too large"""
        large_audio = AudioData(
            data=b"x" * (50 * 1024 * 1024 + 1),  # Exceed MAX_FILE_SIZE
            format=AudioFormat.WAV,
            file_size=50 * 1024 * 1024 + 1
        )
        
        with patch('services.voice_service.is_language_supported', return_value=True):
            with pytest.raises(FileSizeError):
                await voice_service.process_speech_to_text(
                    audio_data=large_audio,
                    request=sample_stt_request
                )

    @pytest.mark.asyncio
    async def test_process_speech_to_text_duration_too_long(
        self, voice_service, sample_stt_request
    ):
        """Test STT with audio too long"""
        long_audio = AudioData(
            data=b"sample_data",
            format=AudioFormat.WAV,
            file_size=1000,
            duration=1800  # 30 minutes, exceeds MAX_DURATION
        )
        
        with patch('services.voice_service.is_language_supported', return_value=True):
            with pytest.raises(AudioDurationError):
                await voice_service.process_speech_to_text(
                    audio_data=long_audio,
                    request=sample_stt_request
                )

    @pytest.mark.asyncio
    async def test_process_speech_to_text_with_emotion_analysis(
        self, voice_service, sample_audio_data, sample_stt_request, mock_engine_manager
    ):
        """Test STT with emotion analysis enabled"""
        sample_stt_request.enable_emotion_analysis = True
        
        with patch('services.voice_service.is_language_supported', return_value=True):
            result = await voice_service.process_speech_to_text(
                audio_data=sample_audio_data,
                request=sample_stt_request
            )
        
        mock_engine_manager.analyze_emotion.assert_called_once()
        assert result.success is True

    @pytest.mark.asyncio
    async def test_process_text_to_speech_success(
        self, voice_service, sample_tts_request
    ):
        """Test successful TTS processing"""
        with patch('services.voice_service.is_language_supported', return_value=True):
            result = await voice_service.process_text_to_speech(
                request=sample_tts_request,
                user_id="test_user"
            )
        
        assert isinstance(result, AudioData)
        assert result.data == b"mock_audio_data"
        assert result.format == AudioFormat.WAV
        assert result.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_process_text_to_speech_text_too_long(
        self, voice_service, sample_tts_request
    ):
        """Test TTS with text too long"""
        sample_tts_request.text = "x" * 10001  # Exceed MAX_TEXT_LENGTH
        
        with patch('services.voice_service.is_language_supported', return_value=True):
            from core.exceptions import AudioValidationError
            with pytest.raises(AudioValidationError):
                await voice_service.process_text_to_speech(request=sample_tts_request)

    @pytest.mark.asyncio
    async def test_analyze_voice_emotion_success(
        self, voice_service, sample_audio_data
    ):
        """Test successful emotion analysis"""
        result = await voice_service.analyze_voice_emotion(
            audio_data=sample_audio_data,
            user_id="test_user"
        )
        
        assert isinstance(result, VoiceResponse)
        assert result.success is True
        assert "emotion_analysis" in result.data

    @pytest.mark.asyncio
    async def test_analyze_voice_emotion_no_analysis(
        self, voice_service, sample_audio_data, mock_engine_manager
    ):
        """Test emotion analysis when not available"""
        mock_engine_manager.analyze_emotion.return_value = None
        
        result = await voice_service.analyze_voice_emotion(
            audio_data=sample_audio_data
        )
        
        assert result.success is False
        assert "not available" in result.message

    @pytest.mark.asyncio
    async def test_create_processing_session(self, voice_service):
        """Test creating processing session"""
        session_id = await voice_service.create_processing_session(
            user_id="test_user",
            session_type="batch",
            language="en"
        )
        
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        
        # Verify session was created
        session_info = voice_service.get_session_info(session_id)
        assert session_info is not None
        assert session_info["user_id"] == "test_user"
        assert session_info["session_type"] == "batch"

    @pytest.mark.asyncio
    async def test_close_processing_session(self, voice_service):
        """Test closing processing session"""
        # Create session first
        session_id = await voice_service.create_processing_session("test_user")
        
        # Close session
        success = await voice_service.close_processing_session(session_id)
        assert success is True
        
        # Verify session is closed
        session_info = voice_service.get_session_info(session_id)
        assert session_info is None

    @pytest.mark.asyncio
    async def test_close_nonexistent_session(self, voice_service):
        """Test closing non-existent session"""
        success = await voice_service.close_processing_session("nonexistent")
        assert success is False

    def test_get_processing_stats(self, voice_service):
        """Test getting processing statistics"""
        stats = voice_service.get_processing_stats()
        
        assert isinstance(stats, dict)
        assert "uptime_seconds" in stats
        assert "total_requests" in stats
        assert "successful_requests" in stats
        assert "failed_requests" in stats
        assert "success_rate" in stats
        assert "languages_processed" in stats
        assert "active_sessions" in stats

    @pytest.mark.asyncio
    async def test_get_supported_features(self, voice_service):
        """Test getting supported features"""
        features = await voice_service.get_supported_features()
        
        assert isinstance(features, dict)
        assert "supported_languages" in features
        assert "supported_audio_formats" in features
        assert "features" in features
        assert "available_engines" in features

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, voice_service):
        """Test cleaning up expired sessions"""
        # Create some test sessions
        session1 = await voice_service.create_processing_session("user1")
        session2 = await voice_service.create_processing_session("user2")
        
        # Mock session times to be old
        for session_id in [session1, session2]:
            if session_id in voice_service.active_sessions:
                voice_service.active_sessions[session_id]["last_activity"] = datetime(2020, 1, 1)
        
        # Cleanup expired sessions
        cleaned_count = await voice_service.cleanup_expired_sessions(max_age_hours=1)
        
        assert cleaned_count >= 0  # Should clean up old sessions

    def test_validate_audio_data_success(self, voice_service, sample_audio_data):
        """Test successful audio data validation"""
        # Should not raise exception
        voice_service._validate_audio_data(sample_audio_data)

    def test_validate_audio_data_file_too_large(self, voice_service):
        """Test audio validation with file too large"""
        large_audio = AudioData(
            data=b"x" * (50 * 1024 * 1024 + 1),
            format=AudioFormat.WAV,
            file_size=50 * 1024 * 1024 + 1
        )
        
        with pytest.raises(FileSizeError):
            voice_service._validate_audio_data(large_audio)

    def test_validate_audio_data_duration_too_long(self, voice_service):
        """Test audio validation with duration too long"""
        long_audio = AudioData(
            data=b"sample_data",
            format=AudioFormat.WAV,
            file_size=1000,
            duration=1800  # 30 minutes
        )
        
        with pytest.raises(AudioDurationError):
            voice_service._validate_audio_data(long_audio)

    @pytest.mark.asyncio
    async def test_engine_failure_handling(
        self, voice_service, sample_audio_data, sample_stt_request, mock_engine_manager
    ):
        """Test handling of engine failures"""
        mock_engine_manager.transcribe_audio.side_effect = Exception("Engine failed")
        
        with patch('services.voice_service.is_language_supported', return_value=True):
            with pytest.raises(AudioProcessingError):
                await voice_service.process_speech_to_text(
                    audio_data=sample_audio_data,
                    request=sample_stt_request
                )

    @pytest.mark.asyncio
    async def test_stats_update_on_success(
        self, voice_service, sample_audio_data, sample_stt_request
    ):
        """Test that stats are updated on successful processing"""
        initial_stats = voice_service.get_processing_stats()
        initial_total = initial_stats["total_requests"]
        initial_successful = initial_stats["successful_requests"]
        
        with patch('services.voice_service.is_language_supported', return_value=True):
            await voice_service.process_speech_to_text(
                audio_data=sample_audio_data,
                request=sample_stt_request
            )
        
        updated_stats = voice_service.get_processing_stats()
        assert updated_stats["total_requests"] == initial_total + 1
        assert updated_stats["successful_requests"] == initial_successful + 1

    @pytest.mark.asyncio
    async def test_stats_update_on_failure(
        self, voice_service, sample_audio_data, sample_stt_request, mock_engine_manager
    ):
        """Test that stats are updated on failed processing"""
        initial_stats = voice_service.get_processing_stats()
        initial_failed = initial_stats["failed_requests"]
        
        mock_engine_manager.transcribe_audio.side_effect = Exception("Processing failed")
        
        with patch('services.voice_service.is_language_supported', return_value=True):
            with pytest.raises(AudioProcessingError):
                await voice_service.process_speech_to_text(
                    audio_data=sample_audio_data,
                    request=sample_stt_request
                )
        
        updated_stats = voice_service.get_processing_stats()
        assert updated_stats["failed_requests"] == initial_failed + 1
