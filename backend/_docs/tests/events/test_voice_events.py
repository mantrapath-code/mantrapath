"""
Test suite for Voice Event Schemas
Tests voice activity and intent events with multilingual support.
"""

import pytest
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

try:
    from shared.events.voice_events import (
        VoiceActivityEvent,
        VoiceIntentEvent,
        VoiceEventType,
        VoiceIntentType,
        AudioMetadata,
        VoiceFeatures,
        VoiceContext,
        DeviceInfo,
        IntentData,
        ProcessingMetadata,
        create_voice_activity_event,
        create_voice_intent_event,
        validate_voice_event_schema,
        get_cultural_context_for_language,
        SUPPORTED_LANGUAGES,
        CULTURAL_REGIONS
    )
    VOICE_EVENTS_AVAILABLE = True
except ImportError as e:
    VOICE_EVENTS_AVAILABLE = False
    pytest.skip(f"Voice events not available: {e}", allow_module_level=True)


class TestVoiceEventSchemas:
    """Test voice event schema validation and creation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.device_info = DeviceInfo(
            device_id="test-device-001",
            device_type="microphone",
            manufacturer="Test Corp",
            model="TestMic v1.0",
            os_version="iOS 17.0",
            app_version="1.0.0"
        )
        
        self.audio_metadata = AudioMetadata(
            duration_ms=1500,
            sample_rate=16000,
            channels=1,
            format="wav",
            bitrate=256,
            encoding="pcm_s16le"
        )
        
        self.voice_features = VoiceFeatures(
            volume_level=0.75,
            pitch_frequency=150.0,
            emotion_confidence={
                "joy": 0.3,
                "neutral": 0.5,
                "excitement": 0.2
            },
            speech_rate=120.0,
            pause_duration=0.2,
            energy_level=0.8,
            accent_confidence={
                "american": 0.7,
                "british": 0.2,
                "australian": 0.1
            }
        )
        
        self.voice_context = VoiceContext(
            session_id=str(uuid.uuid4()),
            user_id="test-user-123",
            device_info=self.device_info,
            environment_noise_level=0.1,
            preferred_language="en",
            cultural_region="US",
            timezone="America/New_York",
            conversation_turn=1,
            interaction_mode="voice_only"
        )
    
    def test_audio_metadata_validation(self):
        """Test audio metadata validation"""
        # Valid metadata
        metadata = AudioMetadata(duration_ms=1000)
        assert metadata.duration_ms == 1000
        assert metadata.sample_rate == 16000  # Default
        
        # Invalid duration
        with pytest.raises(ValueError):
            AudioMetadata(duration_ms=-100)
        
        # Invalid sample rate
        with pytest.raises(ValueError):
            AudioMetadata(duration_ms=1000, sample_rate=1000)  # Too low
    
    def test_voice_features_validation(self):
        """Test voice features validation"""
        # Valid features
        features = VoiceFeatures(
            volume_level=0.5,
            pitch_frequency=150.0
        )
        assert features.volume_level == 0.5
        assert features.pitch_frequency == 150.0
        
        # Invalid volume level
        with pytest.raises(ValueError):
            VoiceFeatures(volume_level=1.5, pitch_frequency=150.0)
        
        # Invalid pitch frequency
        with pytest.raises(ValueError):
            VoiceFeatures(volume_level=0.5, pitch_frequency=10.0)  # Too low
    
    def test_voice_context_creation(self):
        """Test voice context creation and defaults"""
        context = VoiceContext(device_info=self.device_info)
        
        assert context.device_info == self.device_info
        assert context.environment_noise_level == 0.0  # Default
        assert context.conversation_turn == 1  # Default
        assert context.interaction_mode == "voice_only"  # Default
        assert context.session_id is not None  # Auto-generated
    
    def test_voice_activity_event_creation(self):
        """Test voice activity event creation"""
        event = VoiceActivityEvent(
            event_type=VoiceEventType.SPEECH_START,
            audio_metadata=self.audio_metadata,
            voice_features=self.voice_features,
            context=self.voice_context,
            processing_time_ms=50,
            confidence_score=0.95
        )
        
        assert event.event_type == VoiceEventType.SPEECH_START
        assert event.audio_metadata.duration_ms == 1500
        assert event.voice_features.volume_level == 0.75
        assert event.context.user_id == "test-user-123"
        assert event.processing_time_ms == 50
        assert event.confidence_score == 0.95
        assert event.event_id is not None
        assert event.timestamp is not None
    
    def test_voice_intent_event_creation(self):
        """Test voice intent event creation"""
        intent_data = IntentData(
            primary_intent="meditation_request",
            confidence_score=0.92,
            language_detected="en",
            parameters={"duration": "10 minutes", "type": "breathing"},
            alternative_intents=[
                {"intent": "relaxation_request", "confidence": 0.85}
            ]
        )
        
        processing_metadata = ProcessingMetadata(
            classification_model="intent-classifier-v2",
            processing_time_ms=200,
            cultural_context_applied=True,
            cultural_rules_applied=["US_directness", "English_formality"]
        )
        
        event = VoiceIntentEvent(
            event_type=VoiceIntentType.INTENT_CLASSIFIED,
            intent_data=intent_data,
            processing_metadata=processing_metadata,
            context=self.voice_context,
            transcription_quality=0.95,
            raw_transcription="I want to meditate for ten minutes",
            processed_text="meditation request: 10 minutes"
        )
        
        assert event.event_type == VoiceIntentType.INTENT_CLASSIFIED
        assert event.intent_data.primary_intent == "meditation_request"
        assert event.intent_data.confidence_score == 0.92
        assert event.processing_metadata.processing_time_ms == 200
        assert event.transcription_quality == 0.95
        assert len(event.intent_data.alternative_intents) == 1
    
    def test_emotion_confidence_normalization(self):
        """Test emotion confidence score normalization"""
        # Emotion scores that sum to > 1.0 should be normalized
        features = VoiceFeatures(
            volume_level=0.5,
            pitch_frequency=150.0,
            emotion_confidence={
                "joy": 0.8,
                "excitement": 0.7,
                "neutral": 0.3
            }  # Sum = 1.8, should be normalized
        )
        
        total = sum(features.emotion_confidence.values())
        assert abs(total - 1.0) < 0.1  # Should be close to 1.0 after normalization
    
    def test_helper_functions(self):
        """Test helper functions for event creation"""
        # Test voice activity event creation helper
        event = create_voice_activity_event(
            event_type=VoiceEventType.SPEECH_START,
            audio_duration_ms=1000,
            volume_level=0.6,
            pitch_frequency=140.0,
            device_info=self.device_info,
            user_id="helper-test-user"
        )
        
        assert event.event_type == VoiceEventType.SPEECH_START
        assert event.audio_metadata.duration_ms == 1000
        assert event.voice_features.volume_level == 0.6
        assert event.context.user_id == "helper-test-user"
        
        # Test voice intent event creation helper
        intent_event = create_voice_intent_event(
            event_type=VoiceIntentType.INTENT_CLASSIFIED,
            primary_intent="journal_entry",
            confidence_score=0.88,
            language_detected="es",
            classification_model="multilingual-intent-v1",
            processing_time_ms=180,
            device_info=self.device_info,
            user_id="helper-test-user"
        )
        
        assert intent_event.event_type == VoiceIntentType.INTENT_CLASSIFIED
        assert intent_event.intent_data.primary_intent == "journal_entry"
        assert intent_event.intent_data.language_detected == "es"
        assert intent_event.processing_metadata.processing_time_ms == 180
    
    def test_event_validation(self):
        """Test event schema validation"""
        # Valid voice activity event data
        valid_data = {
            "event_type": VoiceEventType.SPEECH_START,
            "audio_metadata": self.audio_metadata.dict(),
            "voice_features": self.voice_features.dict(),
            "context": self.voice_context.dict(),
            "confidence_score": 0.9
        }
        
        assert validate_voice_event_schema(valid_data, "voice.activity_detected")
        
        # Invalid event type
        assert not validate_voice_event_schema(valid_data, "invalid.event_type")
        
        # Missing required field
        invalid_data = valid_data.copy()
        del invalid_data["audio_metadata"]
        assert not validate_voice_event_schema(invalid_data, "voice.activity_detected")


class TestMultilingualSupport:
    """Test multilingual support in voice events"""
    
    def test_supported_languages(self):
        """Test supported language list"""
        assert "en" in SUPPORTED_LANGUAGES
        assert "es" in SUPPORTED_LANGUAGES
        assert "zh" in SUPPORTED_LANGUAGES
        assert "ja" in SUPPORTED_LANGUAGES
        assert len(SUPPORTED_LANGUAGES) >= 20
    
    def test_cultural_regions(self):
        """Test cultural region mapping"""
        assert "US" in CULTURAL_REGIONS
        assert "JP" in CULTURAL_REGIONS
        assert "DE" in CULTURAL_REGIONS
        assert len(CULTURAL_REGIONS) >= 15
    
    def test_cultural_context_mapping(self):
        """Test cultural context retrieval"""
        # Test English (US) - direct communication
        us_context = get_cultural_context_for_language("en")
        assert us_context["directness"] == "high"
        assert us_context["formality"] == "medium"
        
        # Test Japanese - indirect communication, high formality
        jp_context = get_cultural_context_for_language("ja")
        assert jp_context["directness"] == "low"
        assert jp_context["formality"] == "high"
        assert jp_context["context"] == "high"
        
        # Test German - very direct communication
        de_context = get_cultural_context_for_language("de")
        assert de_context["directness"] == "high"
        
        # Test unknown language - should return default (US)
        unknown_context = get_cultural_context_for_language("xx")
        assert unknown_context["formality"] == "medium"
    
    @pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
    def test_all_supported_languages(self, language):
        """Test cultural context for all supported languages"""
        context = get_cultural_context_for_language(language)
        
        # All languages should have basic cultural context
        assert "formality" in context
        assert "directness" in context
        assert "context" in context
        
        # Values should be valid
        assert context["formality"] in ["low", "medium", "high"]
        assert context["directness"] in ["low", "medium", "high", "very_high"]
        assert context["context"] in ["low", "medium", "high"]
    
    def test_multilingual_intent_event(self):
        """Test intent event with different languages"""
        device_info = DeviceInfo(device_id="test-device")
        
        # Test Spanish intent
        spanish_event = create_voice_intent_event(
            event_type=VoiceIntentType.INTENT_CLASSIFIED,
            primary_intent="solicitud_meditacion",
            confidence_score=0.89,
            language_detected="es",
            classification_model="multilingual-v1",
            processing_time_ms=220,
            device_info=device_info,
            user_id="spanish-user"
        )
        
        assert spanish_event.intent_data.language_detected == "es"
        assert spanish_event.intent_data.primary_intent == "solicitud_meditacion"
        
        # Test Chinese intent
        chinese_event = create_voice_intent_event(
            event_type=VoiceIntentType.INTENT_CLASSIFIED,
            primary_intent="冥想请求",
            confidence_score=0.91,
            language_detected="zh",
            classification_model="multilingual-v1",
            processing_time_ms=190,
            device_info=device_info,
            user_id="chinese-user"
        )
        
        assert chinese_event.intent_data.language_detected == "zh"
        assert chinese_event.intent_data.primary_intent == "冥想请求"


class TestEventTypes:
    """Test all event type enumerations"""
    
    def test_voice_event_types(self):
        """Test voice event type enumeration"""
        # Test voice activity types
        assert VoiceEventType.ACTIVITY_DETECTED == "voice.activity_detected"
        assert VoiceEventType.SPEECH_START == "voice.speech_start"
        assert VoiceEventType.SPEECH_END == "voice.speech_end"
        assert VoiceEventType.SILENCE_DETECTED == "voice.silence_detected"
        
        # Test quality events
        assert VoiceEventType.QUALITY_HIGH == "voice.quality_high"
        assert VoiceEventType.QUALITY_DEGRADED == "voice.quality_degraded"
        assert VoiceEventType.QUALITY_RESTORED == "voice.quality_restored"
    
    def test_voice_intent_types(self):
        """Test voice intent type enumeration"""
        # Test intent classification types
        assert VoiceIntentType.INTENT_CLASSIFIED == "voice.intent_classified"
        assert VoiceIntentType.INTENT_CONFIDENCE_LOW == "voice.intent_confidence_low"
        assert VoiceIntentType.INTENT_AMBIGUOUS == "voice.intent_ambiguous"
        assert VoiceIntentType.INTENT_MULTIMODAL == "voice.intent_multimodal"
        
        # Test cultural intent types
        assert VoiceIntentType.CULTURAL_CONTEXT_DETECTED == "voice.cultural_context_detected"
        assert VoiceIntentType.LANGUAGE_SWITCHED == "voice.language_switched"


class TestPerformanceAndValidation:
    """Test performance characteristics and validation"""
    
    def test_event_serialization_performance(self):
        """Test event serialization performance"""
        import time
        
        device_info = DeviceInfo(device_id="perf-test")
        
        # Create a complex event
        event = create_voice_activity_event(
            event_type=VoiceEventType.ACTIVITY_DETECTED,
            audio_duration_ms=5000,
            volume_level=0.8,
            pitch_frequency=175.0,
            device_info=device_info,
            user_id="perf-user"
        )
        
        # Test serialization speed
        start_time = time.time()
        for _ in range(100):
            serialized = event.json()
            VoiceActivityEvent.parse_raw(serialized)
        
        elapsed = time.time() - start_time
        
        # Should be able to serialize/deserialize 100 events in under 1 second
        assert elapsed < 1.0, f"Serialization too slow: {elapsed:.3f}s for 100 events"
    
    def test_large_emotion_confidence_dict(self):
        """Test handling of large emotion confidence dictionaries"""
        # Create large emotion dictionary
        large_emotions = {f"emotion_{i}": 0.01 for i in range(100)}
        
        features = VoiceFeatures(
            volume_level=0.5,
            pitch_frequency=150.0,
            emotion_confidence=large_emotions
        )
        
        # Should handle large dictionaries gracefully
        assert len(features.emotion_confidence) == 100
        
        # Total should be normalized to ~1.0
        total = sum(features.emotion_confidence.values())
        assert abs(total - 1.0) < 0.1
    
    def test_unicode_support(self):
        """Test Unicode support in voice events"""
        # Test Unicode in intent data
        intent_data = IntentData(
            primary_intent="solicitud_meditación_心灵平静",
            confidence_score=0.9,
            language_detected="es",
            parameters={
                "tipo": "respiración",
                "duración": "10 minutos",
                "nivel": "principiante",
                "emoji": "🧘‍♀️"
            }
        )
        
        # Should serialize and deserialize correctly
        serialized = intent_data.json()
        deserialized = IntentData.parse_raw(serialized)
        
        assert deserialized.primary_intent == "solicitud_meditación_心灵平静"
        assert deserialized.parameters["emoji"] == "🧘‍♀️"
        assert deserialized.parameters["duración"] == "10 minutos"
    
    def test_edge_case_values(self):
        """Test edge case values in voice events"""
        # Test minimum values
        min_features = VoiceFeatures(
            volume_level=0.0,  # Minimum volume
            pitch_frequency=50.0,  # Minimum pitch
            emotion_confidence={}  # Empty emotions
        )
        assert min_features.volume_level == 0.0
        
        # Test maximum values
        max_features = VoiceFeatures(
            volume_level=1.0,  # Maximum volume
            pitch_frequency=2000.0,  # Maximum pitch
            speech_rate=300.0,  # Very fast speech
            energy_level=1.0  # Maximum energy
        )
        assert max_features.volume_level == 1.0
        assert max_features.pitch_frequency == 2000.0
    
    def test_timestamp_consistency(self):
        """Test timestamp consistency across events"""
        device_info = DeviceInfo(device_id="timestamp-test")
        
        # Create multiple events
        events = []
        for i in range(5):
            event = create_voice_activity_event(
                event_type=VoiceEventType.ACTIVITY_DETECTED,
                audio_duration_ms=1000,
                volume_level=0.5,
                pitch_frequency=150.0,
                device_info=device_info
            )
            events.append(event)
        
        # Timestamps should be in order and reasonable
        for i in range(1, len(events)):
            # Events should be created within milliseconds of each other
            time_diff = events[i].timestamp - events[i-1].timestamp
            assert time_diff.total_seconds() < 1.0  # Should be very close


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
