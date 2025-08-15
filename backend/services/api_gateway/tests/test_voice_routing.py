"""
Test suite for Voice Command Routing System
Tests voice intent classification, routing, and multilingual support
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from src.voice.models import (
    VoiceIntentType, VoiceCommand, VoiceRoutingRule, 
    VoiceRoutingResult, VoiceLanguageCode, LanguageSupport
)
from src.voice.classifier import VoiceIntentClassifier, IntentPattern
from src.voice.router import VoiceCommandRouter, VoiceRoutingMiddleware
from src.voice.language_support import MultilingualVoiceSupport, CulturalRegion


class TestVoiceModels:
    """Test voice command models"""
    
    def test_voice_command_creation(self):
        """Test VoiceCommand creation and serialization"""
        command = VoiceCommand(
            intent=VoiceIntentType.MOOD_TRACKING,
            confidence=0.85,
            language="en",
            parameters={"mood_value": "happy"},
            raw_text="I'm feeling happy today",
            user_id="user123"
        )
        
        assert command.intent == VoiceIntentType.MOOD_TRACKING
        assert command.confidence == 0.85
        assert command.language == "en"
        assert command.parameters["mood_value"] == "happy"
        assert command.user_id == "user123"
        assert command.timestamp is not None
    
    def test_voice_command_serialization(self):
        """Test VoiceCommand to_dict and from_dict"""
        original = VoiceCommand(
            intent=VoiceIntentType.JOURNAL_ENTRY,
            confidence=0.92,
            language="hi",
            parameters={"topic": "family"},
            raw_text="परिवार के बारे में लिखें",
            cultural_context="indian_subcontinent"
        )
        
        # Serialize to dict
        data = original.to_dict()
        assert data["intent"] == "journal_entry"
        assert data["confidence"] == 0.92
        assert data["language"] == "hi"
        
        # Deserialize from dict
        reconstructed = VoiceCommand.from_dict(data)
        assert reconstructed.intent == original.intent
        assert reconstructed.confidence == original.confidence
        assert reconstructed.language == original.language
        assert reconstructed.cultural_context == original.cultural_context
    
    def test_voice_routing_rule_matches(self):
        """Test VoiceRoutingRule matching logic"""
        rule = VoiceRoutingRule(
            intent=VoiceIntentType.MOOD_TRACKING,
            target_service="mood_service",
            endpoint_pattern="/mood/track",
            required_parameters=[],
            supported_languages=["en", "hi"],
            cultural_adaptations={}
        )
        
        # Matching command
        matching_command = VoiceCommand(
            intent=VoiceIntentType.MOOD_TRACKING,
            confidence=0.8,
            language="en",
            parameters={},
            raw_text="I'm happy"
        )
        assert rule.matches_command(matching_command) is True
        
        # Non-matching intent
        wrong_intent_command = VoiceCommand(
            intent=VoiceIntentType.JOURNAL_ENTRY,
            confidence=0.8,
            language="en",
            parameters={},
            raw_text="Write journal"
        )
        assert rule.matches_command(wrong_intent_command) is False
        
        # Non-matching language
        wrong_language_command = VoiceCommand(
            intent=VoiceIntentType.MOOD_TRACKING,
            confidence=0.8,
            language="fr",
            parameters={},
            raw_text="Je suis heureux"
        )
        assert rule.matches_command(wrong_language_command) is False
    
    def test_voice_routing_rule_endpoint_generation(self):
        """Test endpoint generation with parameters"""
        rule = VoiceRoutingRule(
            intent=VoiceIntentType.PROFILE_UPDATE,
            target_service="profile_service",
            endpoint_pattern="/profile/{user_id}/update/{field}",
            required_parameters=["user_id", "field"],
            supported_languages=["en"],
            cultural_adaptations={}
        )
        
        command = VoiceCommand(
            intent=VoiceIntentType.PROFILE_UPDATE,
            confidence=0.8,
            language="en",
            parameters={"user_id": "123", "field": "name"},
            raw_text="Update my name"
        )
        
        endpoint = rule.generate_endpoint(command)
        assert endpoint == "/profile/123/update/name"


class TestVoiceIntentClassifier:
    """Test voice intent classification"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.classifier = VoiceIntentClassifier()
    
    def test_english_mood_tracking_classification(self):
        """Test English mood tracking intent classification"""
        test_cases = [
            ("I'm feeling happy today", VoiceIntentType.MOOD_TRACKING),
            ("My mood is great", VoiceIntentType.MOOD_TRACKING),
            ("Track my mood as excited", VoiceIntentType.MOOD_TRACKING),
            ("Mood 8 out of 10", VoiceIntentType.MOOD_TRACKING),
        ]
        
        for text, expected_intent in test_cases:
            command = self.classifier.classify_intent(text, "en")
            assert command.intent == expected_intent
            assert command.confidence > 0.3
            assert command.language == "en"
            assert command.raw_text == text
    
    def test_hindi_mood_tracking_classification(self):
        """Test Hindi mood tracking intent classification"""
        test_cases = [
            ("मैं आज खुश हूँ", VoiceIntentType.MOOD_TRACKING),
            ("मेरा मूड अच्छा है", VoiceIntentType.MOOD_TRACKING),
        ]
        
        for text, expected_intent in test_cases:
            command = self.classifier.classify_intent(text, "hi")
            assert command.intent == expected_intent
            assert command.confidence > 0.3
            assert command.language == "hi"
    
    def test_journal_entry_classification(self):
        """Test journal entry intent classification"""
        test_cases = [
            ("Start a new journal entry", VoiceIntentType.JOURNAL_ENTRY),
            ("Add to my journal", VoiceIntentType.JOURNAL_ENTRY),
            ("Write about my day", VoiceIntentType.JOURNAL_ENTRY),
        ]
        
        for text, expected_intent in test_cases:
            command = self.classifier.classify_intent(text, "en")
            assert command.intent == expected_intent
            assert command.confidence > 0.3
    
    def test_chatbot_query_classification(self):
        """Test chatbot query intent classification"""
        test_cases = [
            ("Ask the chatbot about meditation", VoiceIntentType.CHATBOT_QUERY),
            ("Help me with stress management", VoiceIntentType.CHATBOT_QUERY),
            ("Talk to the assistant", VoiceIntentType.CHATBOT_QUERY),
        ]
        
        for text, expected_intent in test_cases:
            command = self.classifier.classify_intent(text, "en")
            assert command.intent == expected_intent
            assert command.confidence > 0.3
    
    def test_unknown_intent_classification(self):
        """Test classification of unknown/unclear intents"""
        unclear_texts = [
            "What is the meaning of life?",
            "Random gibberish text",
            "Blah blah blah",
        ]
        
        for text in unclear_texts:
            command = self.classifier.classify_intent(text, "en")
            assert command.intent == VoiceIntentType.UNKNOWN
            assert command.confidence < 0.5
    
    def test_mood_parameter_extraction(self):
        """Test extraction of mood-specific parameters"""
        command = self.classifier.classify_intent("My mood is 7 out of 10", "en")
        
        assert command.intent == VoiceIntentType.MOOD_TRACKING
        assert "mood_value" in command.parameters
        assert command.parameters["mood_value"] == 7
        assert command.parameters["mood_scale"] == 10
        assert command.parameters["mood_normalized"] == 0.7
    
    def test_custom_pattern_addition(self):
        """Test adding custom intent patterns"""
        custom_pattern = IntentPattern(
            intent=VoiceIntentType.CONTENT_REQUEST,
            patterns=[r"find me some (.+) content"],
            keywords=["find", "content"],
            language=VoiceLanguageCode.ENGLISH
        )
        
        self.classifier.add_custom_pattern("en", custom_pattern)
        
        command = self.classifier.classify_intent("find me some relaxation content", "en")
        assert command.intent == VoiceIntentType.CONTENT_REQUEST
        assert command.confidence > 0.3


class TestVoiceCommandRouter:
    """Test voice command routing"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.router = VoiceCommandRouter()
    
    def test_successful_mood_tracking_routing(self):
        """Test successful routing of mood tracking command"""
        result = self.router.route_voice_command(
            text="I'm feeling happy today",
            language="en",
            user_id="user123"
        )
        
        assert result.success is True
        assert result.target_service == "mood_service"
        assert "/mood/track" in result.endpoint
        assert result.processing_time_ms is not None
        assert result.processing_time_ms > 0
    
    def test_successful_journal_routing(self):
        """Test successful routing of journal entry command"""
        result = self.router.route_voice_command(
            text="Start a new journal entry",
            language="en",
            user_id="user123"
        )
        
        assert result.success is True
        assert result.target_service == "content_service"
        assert "/journal/entries" in result.endpoint
    
    def test_cultural_context_adaptation(self):
        """Test cultural context adaptation in routing"""
        result = self.router.route_voice_command(
            text="मेरा मूड अच्छा है",
            language="hi",
            user_id="user123",
            cultural_context="indian_subcontinent"
        )
        
        assert result.success is True
        assert result.target_service == "mood_service"
        # Check if cultural parameters are added
        assert "cultural_" in result.endpoint or result.endpoint.endswith("/mood/track")
    
    def test_unsupported_intent_routing(self):
        """Test routing of unsupported intents"""
        result = self.router.route_voice_command(
            text="Random meaningless text",
            language="en",
            user_id="user123"
        )
        
        assert result.success is False
        assert result.error_message and "No routing rule found" in result.error_message
    
    def test_routing_statistics(self):
        """Test routing statistics tracking"""
        initial_stats = self.router.get_routing_statistics()
        initial_requests = initial_stats["total_requests"]
        
        # Make a successful request
        self.router.route_voice_command(
            text="I'm feeling great",
            language="en",
            user_id="user123"
        )
        
        # Make a failed request
        self.router.route_voice_command(
            text="Nonsense text",
            language="en",
            user_id="user123"
        )
        
        updated_stats = self.router.get_routing_statistics()
        assert updated_stats["total_requests"] == initial_requests + 2
        assert updated_stats["successful_routes"] >= 1
        assert updated_stats["failed_routes"] >= 1
        assert updated_stats["success_rate_percent"] <= 100
    
    def test_custom_routing_rule_addition(self):
        """Test adding custom routing rules"""
        custom_rule = VoiceRoutingRule(
            intent=VoiceIntentType.NOTIFICATION_SETTING,
            target_service="notification_service",
            endpoint_pattern="/notifications/settings",
            required_parameters=[],
            supported_languages=["en"],
            cultural_adaptations={},
            priority=1
        )
        
        self.router.add_routing_rule(custom_rule)
        
        # Check if rule was added
        rules = self.router.get_routing_rules_for_intent(VoiceIntentType.NOTIFICATION_SETTING)
        assert len(rules) >= 1
        assert any(rule.target_service == "notification_service" for rule in rules)
    
    def test_routing_rule_removal(self):
        """Test removing routing rules"""
        # Add a rule first
        custom_rule = VoiceRoutingRule(
            intent=VoiceIntentType.ANALYTICS_REQUEST,
            target_service="test_service",
            endpoint_pattern="/test",
            required_parameters=[],
            supported_languages=["en"],
            cultural_adaptations={}
        )
        
        self.router.add_routing_rule(custom_rule)
        
        # Remove the rule
        removed = self.router.remove_routing_rule(
            VoiceIntentType.ANALYTICS_REQUEST, 
            "test_service"
        )
        
        assert removed is True
        
        # Verify removal
        rules = self.router.get_routing_rules_for_intent(VoiceIntentType.ANALYTICS_REQUEST)
        assert not any(rule.target_service == "test_service" for rule in rules)


class TestMultilingualVoiceSupport:
    """Test multilingual voice support"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.ml_support = MultilingualVoiceSupport()
    
    def test_language_detection_devanagari(self):
        """Test language detection for Devanagari script (Hindi)"""
        hindi_text = "मैं खुश हूँ"
        detected = self.ml_support.detect_language(hindi_text)
        assert detected == "hi"
    
    def test_language_detection_arabic(self):
        """Test language detection for Arabic script"""
        arabic_text = "أنا سعيد"
        detected = self.ml_support.detect_language(arabic_text)
        assert detected == "ar"
    
    def test_language_detection_chinese(self):
        """Test language detection for Chinese characters"""
        chinese_text = "我很高兴"
        detected = self.ml_support.detect_language(chinese_text)
        assert detected == "zh"
    
    def test_language_detection_with_hint(self):
        """Test language detection with hint"""
        text = "Je suis heureux"
        detected = self.ml_support.detect_language(text, hint="fr")
        assert detected == "fr"
    
    def test_cultural_context_retrieval(self):
        """Test cultural context retrieval for languages"""
        hindi_context = self.ml_support.get_cultural_context("hi")
        assert hindi_context == "indian_subcontinent"
        
        french_context = self.ml_support.get_cultural_context("fr")
        assert french_context == "western_europe"
        
        unknown_context = self.ml_support.get_cultural_context("xx")
        assert unknown_context is None
    
    def test_language_support_levels(self):
        """Test language support level categorization"""
        primary_langs = self.ml_support.get_supported_languages_by_level("primary")
        assert len(primary_langs) >= 2
        assert any(lang.code.value == "en" for lang in primary_langs)
        assert any(lang.code.value == "hi" for lang in primary_langs)
        
        secondary_langs = self.ml_support.get_supported_languages_by_level("secondary")
        assert len(secondary_langs) >= 5
        
        regional_langs = self.ml_support.get_supported_languages_by_level("regional")
        assert len(regional_langs) >= 5
    
    def test_language_support_check(self):
        """Test language support checking"""
        assert self.ml_support.is_language_supported("en") is True
        assert self.ml_support.is_language_supported("hi") is True
        assert self.ml_support.is_language_supported("xx") is False
    
    def test_fallback_language_suggestion(self):
        """Test fallback language suggestions"""
        # Unsupported language should fallback to English
        fallback = self.ml_support.suggest_fallback_language("xx")
        assert fallback == "en"
        
        # Regional Indian language should fallback to Hindi
        fallback = self.ml_support.suggest_fallback_language("ta")
        assert fallback == "hi"
        
        # Supported language should return itself
        fallback = self.ml_support.suggest_fallback_language("en")
        assert fallback == "en"
    
    def test_voice_examples_retrieval(self):
        """Test voice command examples retrieval"""
        en_examples = self.ml_support.get_voice_examples_for_language("en")
        assert len(en_examples) >= 3
        assert any(ex["intent"] == "mood_tracking" for ex in en_examples)
        
        hi_examples = self.ml_support.get_voice_examples_for_language("hi")
        assert len(hi_examples) >= 3
        assert any("मूड" in ex["text"] for ex in hi_examples)
    
    def test_regional_adaptations(self):
        """Test regional adaptations retrieval"""
        indian_region = self.ml_support.get_regional_adaptations("indian_subcontinent")
        assert indian_region is not None
        assert indian_region.communication_style == "high-context"
        assert "family_importance" in indian_region.cultural_values
        
        european_region = self.ml_support.get_regional_adaptations("western_europe")
        assert european_region is not None
        assert european_region.communication_style == "direct"
    
    def test_language_statistics(self):
        """Test language statistics generation"""
        stats = self.ml_support.get_language_statistics()
        
        assert "total_languages" in stats
        assert stats["total_languages"] > 10
        
        assert "by_support_level" in stats
        assert "primary" in stats["by_support_level"]
        assert "secondary" in stats["by_support_level"]
        assert "regional" in stats["by_support_level"]
        
        assert "by_cultural_region" in stats
        assert "indian_subcontinent" in stats["by_cultural_region"]
        assert "western_europe" in stats["by_cultural_region"]


class TestVoiceRoutingMiddleware:
    """Test voice routing middleware"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.router = VoiceCommandRouter()
        self.middleware = VoiceRoutingMiddleware(self.router)
    
    @pytest.mark.asyncio
    async def test_successful_voice_request_processing(self):
        """Test successful voice request processing"""
        request_data = {
            "text": "I'm feeling happy today",
            "language": "en",
            "user_id": "user123",
            "cultural_context": "western_europe"
        }
        
        result = await self.middleware.process_voice_request(request_data)
        
        assert result["success"] is True
        assert "target_service" in result
        assert "endpoint" in result
        assert result["target_service"] == "mood_service"
    
    @pytest.mark.asyncio
    async def test_empty_text_error_handling(self):
        """Test error handling for empty text"""
        request_data = {
            "text": "",
            "language": "en",
            "user_id": "user123"
        }
        
        result = await self.middleware.process_voice_request(request_data)
        
        assert result["success"] is False
        assert "Empty voice text" in result["error"]
    
    @pytest.mark.asyncio
    async def test_missing_parameters_handling(self):
        """Test handling of missing parameters"""
        request_data = {
            "language": "en"
            # Missing text
        }
        
        result = await self.middleware.process_voice_request(request_data)
        
        assert result["success"] is False
        assert "error" in result


# Integration tests
class TestVoiceSystemIntegration:
    """Integration tests for the complete voice system"""
    
    def setup_method(self):
        """Setup integrated system"""
        self.ml_support = MultilingualVoiceSupport()
        self.classifier = VoiceIntentClassifier()
        self.router = VoiceCommandRouter(self.classifier)
        self.middleware = VoiceRoutingMiddleware(self.router)
    
    def test_end_to_end_english_flow(self):
        """Test complete English voice command flow"""
        text = "I'm feeling excited about my journal entry today"
        language = self.ml_support.detect_language(text)
        
        assert language == "en"
        
        result = self.router.route_voice_command(text, language, "user123")
        assert result.success is True
        # Should route to either mood_service or content_service
        assert result.target_service in ["mood_service", "content_service"]
    
    def test_end_to_end_hindi_flow(self):
        """Test complete Hindi voice command flow"""
        text = "मैं आज बहुत खुश हूँ"
        language = self.ml_support.detect_language(text)
        
        assert language == "hi"
        
        cultural_context = self.ml_support.get_cultural_context(language)
        assert cultural_context == "indian_subcontinent"
        
        result = self.router.route_voice_command(
            text, language, "user123", cultural_context
        )
        assert result.success is True
        assert result.target_service == "mood_service"
    
    @pytest.mark.asyncio
    async def test_end_to_end_middleware_flow(self):
        """Test complete middleware processing flow"""
        request_data = {
            "text": "Start writing about my meditation practice",
            "language": "en",
            "user_id": "user123",
            "cultural_context": "western_europe"
        }
        
        result = await self.middleware.process_voice_request(request_data)
        
        assert result["success"] is True
        assert result["target_service"] in ["content_service", "chatbot_service"]
        assert "endpoint" in result
        assert "processing_time_ms" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
