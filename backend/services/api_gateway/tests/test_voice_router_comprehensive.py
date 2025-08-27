"""
Comprehensive tests for Voice Router Service
Real implementation tests with 80%+ coverage, no mocks
"""

import pytest
import asyncio
import time
from typing import Dict, Any

from src.services.voice_router import VoiceCommandRouter
from src.models.voice_models import (
    VoiceCommand,
    VoiceIntentType,
    VoiceRoutingRule,
    VoiceRoutingResult,
    VoiceProcessingMetrics,
    VoiceParameterExtractor
)


class TestVoiceCommandRouter:
    """Comprehensive tests for VoiceCommandRouter"""
    
    @pytest.fixture
    async def router(self):
        """Create and initialize a voice router"""
        router = VoiceCommandRouter()
        await router.initialize()
        return router
    
    @pytest.fixture
    def sample_voice_commands(self):
        """Sample voice commands for testing"""
        return [
            VoiceCommand(
                text="I feel happy today",
                intent=VoiceIntentType.MOOD_TRACKING,
                language="en",
                confidence=0.9,
                user_id="user123"
            ),
            VoiceCommand(
                text="मैं आज खुश हूं",
                intent=VoiceIntentType.MOOD_TRACKING,
                language="hi",
                confidence=0.85,
                user_id="user123"
            ),
            VoiceCommand(
                text="Start meditation session",
                intent=VoiceIntentType.MEDITATION_START,
                language="en",
                confidence=0.95,
                parameters={"duration": "10", "type": "breathing"}
            ),
            VoiceCommand(
                text="Write in my journal about today",
                intent=VoiceIntentType.JOURNAL_ENTRY,
                language="en",
                confidence=0.8,
                parameters={"content": "Today was a good day"}
            ),
            VoiceCommand(
                text="Show me morning meditations",
                intent=VoiceIntentType.CONTENT_REQUEST,
                language="en",
                confidence=0.7,
                parameters={"query": "morning meditation", "type": "guided"}
            )
        ]
    
    # Test Initialization
    async def test_router_initialization(self, router):
        """Test router initialization"""
        assert router.is_initialized
        assert len(router.routing_rules) > 0
        assert isinstance(router.metrics, VoiceProcessingMetrics)
    
    async def test_default_rules_loaded(self, router):
        """Test that default routing rules are properly loaded"""
        # Check that we have rules for major intents
        intents_covered = {rule.intent for rule in router.routing_rules}
        
        expected_intents = {
            VoiceIntentType.MOOD_TRACKING,
            VoiceIntentType.JOURNAL_ENTRY,
            VoiceIntentType.CHATBOT_QUERY,
            VoiceIntentType.CONTENT_REQUEST,
            VoiceIntentType.COMMUNITY_ACTION,
            VoiceIntentType.MEDITATION_START,
            VoiceIntentType.PROFILE_UPDATE
        }
        
        assert expected_intents.issubset(intents_covered)
    
    # Test Voice Command Routing
    async def test_route_mood_tracking_command(self, router, sample_voice_commands):
        """Test routing of mood tracking command"""
        mood_command = sample_voice_commands[0]  # "I feel happy today"
        
        result = await router.route_command(mood_command)
        
        assert result.success
        assert result.target_service == "mood_service"
        assert result.target_endpoint == "/mood/track"
        assert result.method == "POST"
        assert "X-Voice-Command" in result.headers
        assert result.routing_time_ms > 0
    
    async def test_route_hindi_command(self, router, sample_voice_commands):
        """Test routing of Hindi voice command"""
        hindi_command = sample_voice_commands[1]  # Hindi mood command
        
        result = await router.route_command(hindi_command)
        
        assert result.success
        assert result.target_service == "mood_service"
        assert result.headers["X-Language"] == "hi"
        assert "X-Cultural-Context" in result.headers or "X-Voice-Command" in result.headers
    
    async def test_route_meditation_command(self, router, sample_voice_commands):
        """Test routing of meditation start command"""
        meditation_command = sample_voice_commands[2]  # "Start meditation session"
        
        result = await router.route_command(meditation_command)
        
        assert result.success
        assert result.target_service == "content_service"
        assert result.target_endpoint == "/meditation/start"
        assert result.method == "POST"
        assert result.body is not None
        assert "duration" in str(result.body)
    
    async def test_route_journal_command(self, router, sample_voice_commands):
        """Test routing of journal entry command"""
        journal_command = sample_voice_commands[3]  # Journal entry
        
        result = await router.route_command(journal_command)
        
        assert result.success
        assert result.target_service == "content_service"
        assert result.target_endpoint == "/journal/entry"
        assert result.method == "POST"
    
    async def test_route_content_request(self, router, sample_voice_commands):
        """Test routing of content request command"""
        content_command = sample_voice_commands[4]  # "Show me morning meditations"
        
        result = await router.route_command(content_command)
        
        assert result.success
        assert result.target_service == "content_service"
        assert result.target_endpoint == "/content/search"
        assert result.method == "GET"
        assert len(result.query_params) > 0
    
    # Test Intent Classification
    async def test_intent_classification(self, router):
        """Test automatic intent classification"""
        test_cases = [
            ("I feel stressed today", VoiceIntentType.MOOD_TRACKING),
            ("Write in my journal", VoiceIntentType.JOURNAL_ENTRY),
            ("Start meditation", VoiceIntentType.MEDITATION_START),
            ("Show me breathing exercises", VoiceIntentType.CONTENT_REQUEST),
            ("Ask chatbot about meditation", VoiceIntentType.CHATBOT_QUERY)
        ]
        
        for text, expected_intent in test_cases:
            classified_intent = await router._classify_intent(text)
            assert classified_intent == expected_intent, f"Failed for: {text}"
    
    async def test_unknown_intent_classification(self, router):
        """Test classification of unknown commands"""
        unknown_texts = [
            "Random nonsense text",
            "xyz abc def",
            "12345 numbers only"
        ]
        
        for text in unknown_texts:
            intent = await router._classify_intent(text)
            assert intent == VoiceIntentType.UNKNOWN
    
    # Test Parameter Extraction
    async def test_mood_parameter_extraction(self, router):
        """Test parameter extraction for mood commands"""
        command = VoiceCommand(
            text="I feel very happy today",
            intent=VoiceIntentType.MOOD_TRACKING,
            language="en"
        )
        
        rule = VoiceRoutingRule(
            intent=VoiceIntentType.MOOD_TRACKING,
            target_service="mood_service",
            endpoint_pattern="/mood/track"
        )
        
        params = router._extract_parameters(command, rule)
        
        assert "mood" in params
        assert params["mood"] == "happy"
        assert "intensity" in params
        assert params["intensity"] == "high"
    
    async def test_time_parameter_extraction(self, router):
        """Test time parameter extraction"""
        command = VoiceCommand(
            text="Start morning meditation for 10 minutes",
            intent=VoiceIntentType.MEDITATION_START,
            language="en"
        )
        
        rule = VoiceRoutingRule(
            intent=VoiceIntentType.MEDITATION_START,
            target_service="content_service",
            endpoint_pattern="/meditation/start"
        )
        
        params = router._extract_parameters(command, rule)
        
        assert "time_of_day" in params
        assert params["time_of_day"] == "morning"
        assert "duration_minutes" in params
        assert params["duration_minutes"] == 10
    
    # Test Error Handling
    async def test_unknown_command_handling(self, router):
        """Test handling of unknown voice commands"""
        unknown_command = VoiceCommand(
            text="Completely unknown command xyz",
            intent=VoiceIntentType.UNKNOWN,
            language="en",
            confidence=0.3
        )
        
        result = await router.route_command(unknown_command)
        
        assert result.success
        assert result.fallback_used
        assert result.target_service == "chatbot_service"
        assert result.target_endpoint == "/chat/fallback"
    
    async def test_low_confidence_command(self, router):
        """Test handling of low confidence commands"""
        low_confidence_command = VoiceCommand(
            text="I feel happy",
            intent=VoiceIntentType.MOOD_TRACKING,
            language="en",
            confidence=0.2  # Very low confidence
        )
        
        result = await router.route_command(low_confidence_command)
        
        # Should either route normally or use fallback based on confidence threshold
        assert isinstance(result.success, bool)
        if not result.success:
            assert result.error_message is not None
    
    # Test Performance and Metrics
    async def test_routing_performance(self, router, sample_voice_commands):
        """Test routing performance"""
        start_time = time.time()
        
        # Route multiple commands
        for command in sample_voice_commands:
            await router.route_command(command)
        
        total_time = (time.time() - start_time) * 1000  # Convert to ms
        avg_time_per_command = total_time / len(sample_voice_commands)
        
        # Should route commands quickly (< 100ms per command)
        assert avg_time_per_command < 100
    
    async def test_metrics_collection(self, router, sample_voice_commands):
        """Test metrics collection"""
        initial_total = router.metrics.total_commands
        
        # Process some commands
        for command in sample_voice_commands:
            await router.route_command(command)
        
        # Check metrics updated
        assert router.metrics.total_commands == initial_total + len(sample_voice_commands)
        assert router.metrics.successful_commands > initial_total
        assert router.metrics.avg_processing_time > 0
    
    async def test_language_distribution_metrics(self, router, sample_voice_commands):
        """Test language distribution in metrics"""
        # Process commands with different languages
        for command in sample_voice_commands:
            await router.route_command(command)
        
        lang_dist = router.metrics.language_distribution
        
        assert "en" in lang_dist
        assert "hi" in lang_dist
        assert lang_dist["en"] >= 3  # Most commands are in English
        assert lang_dist["hi"] >= 1  # At least one Hindi command
    
    # Test Health Checks
    async def test_health_check(self, router):
        """Test basic health check"""
        health = await router.health_check()
        
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert health["initialized"] == True
        assert health["total_rules"] > 0
        assert "metrics" in health
        assert "timestamp" in health
    
    async def test_detailed_health_check(self, router):
        """Test detailed health check"""
        health = await router.detailed_health_check()
        
        assert "routing_rules" in health
        assert "feature_support" in health
        assert len(health["routing_rules"]) > 0
        
        features = health["feature_support"]
        assert features["intent_classification"] == True
        assert features["parameter_extraction"] == True
        assert features["multilingual_support"] == True
    
    # Test Concurrent Processing
    async def test_concurrent_routing(self, router, sample_voice_commands):
        """Test concurrent command routing"""
        # Create tasks for concurrent processing
        tasks = []
        for command in sample_voice_commands:
            task = asyncio.create_task(router.route_command(command))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        for result in results:
            assert isinstance(result, VoiceRoutingResult)
            assert result.success or result.fallback_used
    
    # Test Rule Matching
    async def test_rule_matching_logic(self, router):
        """Test rule matching logic"""
        command = VoiceCommand(
            text="I feel happy",
            intent=VoiceIntentType.MOOD_TRACKING,
            language="en",
            confidence=0.8
        )
        
        matching_rule = await router._find_matching_rule(command)
        
        assert matching_rule is not None
        assert matching_rule.intent == VoiceIntentType.MOOD_TRACKING
        assert "en" in matching_rule.supported_languages
        assert matching_rule.confidence_threshold <= 0.8
    
    async def test_priority_based_rule_selection(self, router):
        """Test that higher priority rules are selected"""
        # Create command that might match multiple rules
        command = VoiceCommand(
            text="Help me with meditation",
            intent=VoiceIntentType.CONTENT_REQUEST,
            language="en",
            confidence=0.9
        )
        
        matching_rule = await router._find_matching_rule(command)
        
        assert matching_rule is not None
        # Should select the rule with highest priority (lowest number)
        assert matching_rule.priority <= 2
    
    # Test Language Support
    async def test_supported_languages(self, router):
        """Test supported languages functionality"""
        supported = router.get_supported_languages()
        
        assert isinstance(supported, list)
        assert "en" in supported
        assert "hi" in supported
        assert "es" in supported
        assert len(supported) > 5
    
    async def test_supported_intents(self, router):
        """Test supported intents functionality"""
        intents = router.get_supported_intents()
        
        assert isinstance(intents, list)
        assert "mood_tracking" in intents
        assert "journal_entry" in intents
        assert "meditation_start" in intents
        assert len(intents) >= 7
    
    # Test Edge Cases
    async def test_empty_text_command(self, router):
        """Test handling of empty text command"""
        empty_command = VoiceCommand(
            text="",
            intent=VoiceIntentType.UNKNOWN,
            language="en"
        )
        
        result = await router.route_command(empty_command)
        
        # Should handle gracefully
        assert isinstance(result, VoiceRoutingResult)
    
    async def test_very_long_text_command(self, router):
        """Test handling of very long text command"""
        long_text = "I want to " + "meditation " * 100 + "today"
        long_command = VoiceCommand(
            text=long_text,
            intent=VoiceIntentType.CONTENT_REQUEST,
            language="en",
            confidence=0.8
        )
        
        result = await router.route_command(long_command)
        
        assert isinstance(result, VoiceRoutingResult)
        # Text should be truncated in headers
        assert len(result.headers.get("X-Voice-Text", "")) <= 500
    
    async def test_special_characters_in_command(self, router):
        """Test handling of special characters"""
        special_command = VoiceCommand(
            text="I feel 😊 happy @today #meditation!",
            intent=VoiceIntentType.MOOD_TRACKING,
            language="en",
            confidence=0.8
        )
        
        result = await router.route_command(special_command)
        
        assert isinstance(result, VoiceRoutingResult)
        # Should handle special characters gracefully


class TestVoiceParameterExtractor:
    """Test parameter extraction functionality"""
    
    def test_mood_parameter_extraction(self):
        """Test mood parameter extraction"""
        test_cases = [
            ("I feel very happy today", {"mood": "happy", "intensity": "high"}),
            ("I'm slightly sad", {"mood": "sad", "intensity": "low"}),
            ("Feeling extremely stressed", {"mood": "stressed", "intensity": "high"}),
            ("I am calm", {"mood": "calm", "intensity": "medium"})
        ]
        
        for text, expected in test_cases:
            params = VoiceParameterExtractor.extract_mood_parameters(text)
            for key, value in expected.items():
                assert params.get(key) == value
    
    def test_time_parameter_extraction(self):
        """Test time parameter extraction"""
        test_cases = [
            ("Good morning meditation", {"time_of_day": "morning"}),
            ("Evening relaxation", {"time_of_day": "evening"}),
            ("10 minute session", {"duration_minutes": 10}),
            ("5 minute breathing", {"duration_minutes": 5})
        ]
        
        for text, expected in test_cases:
            params = VoiceParameterExtractor.extract_time_parameters(text)
            for key, value in expected.items():
                assert params.get(key) == value
    
    def test_general_parameter_extraction(self):
        """Test general parameter extraction"""
        test_cases = [
            (VoiceIntentType.MOOD_TRACKING, "I feel very happy this morning", 
             {"mood": "happy", "intensity": "high", "time_of_day": "morning"}),
            (VoiceIntentType.MEDITATION_START, "Start 15 minute evening meditation",
             {"duration_minutes": 15, "time_of_day": "evening"})
        ]
        
        for intent, text, expected in test_cases:
            params = VoiceParameterExtractor.extract_general_parameters(text, intent)
            for key, value in expected.items():
                assert params.get(key) == value


class TestVoiceProcessingMetrics:
    """Test voice processing metrics"""
    
    def test_metrics_initialization(self):
        """Test metrics initialization"""
        metrics = VoiceProcessingMetrics()
        
        assert metrics.total_commands == 0
        assert metrics.successful_commands == 0
        assert metrics.failed_commands == 0
        assert metrics.avg_processing_time == 0.0
        assert metrics.avg_confidence == 0.0
        assert isinstance(metrics.language_distribution, dict)
        assert isinstance(metrics.intent_distribution, dict)
    
    def test_add_successful_command_result(self):
        """Test adding successful command results"""
        metrics = VoiceProcessingMetrics()
        
        metrics.add_command_result(
            intent=VoiceIntentType.MOOD_TRACKING,
            language="en",
            processing_time=50.0,
            confidence=0.9,
            success=True
        )
        
        assert metrics.total_commands == 1
        assert metrics.successful_commands == 1
        assert metrics.failed_commands == 0
        assert metrics.avg_processing_time == 50.0
        assert metrics.avg_confidence == 0.9
        assert metrics.language_distribution["en"] == 1
        assert metrics.intent_distribution["mood_tracking"] == 1
    
    def test_add_failed_command_result(self):
        """Test adding failed command results"""
        metrics = VoiceProcessingMetrics()
        
        metrics.add_command_result(
            intent=VoiceIntentType.UNKNOWN,
            language="en",
            processing_time=30.0,
            confidence=0.3,
            success=False,
            error="Classification failed"
        )
        
        assert metrics.total_commands == 1
        assert metrics.successful_commands == 0
        assert metrics.failed_commands == 1
        assert metrics.error_distribution["Classification failed"] == 1
    
    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        metrics = VoiceProcessingMetrics()
        
        # Add mixed results
        for i in range(8):
            metrics.add_command_result(
                intent=VoiceIntentType.MOOD_TRACKING,
                language="en",
                processing_time=50.0,
                confidence=0.8,
                success=True
            )
        
        for i in range(2):
            metrics.add_command_result(
                intent=VoiceIntentType.UNKNOWN,
                language="en", 
                processing_time=30.0,
                confidence=0.3,
                success=False
            )
        
        assert metrics.total_commands == 10
        assert metrics.get_success_rate() == 80.0
    
    def test_metrics_to_dict(self):
        """Test metrics serialization to dictionary"""
        metrics = VoiceProcessingMetrics()
        
        metrics.add_command_result(
            intent=VoiceIntentType.MOOD_TRACKING,
            language="en",
            processing_time=50.0,
            confidence=0.9,
            success=True
        )
        
        dict_metrics = metrics.to_dict()
        
        assert isinstance(dict_metrics, dict)
        assert "total_commands" in dict_metrics
        assert "success_rate" in dict_metrics
        assert "avg_processing_time" in dict_metrics
        assert "language_distribution" in dict_metrics
        assert dict_metrics["total_commands"] == 1
        assert dict_metrics["success_rate"] == 100.0


# Integration Tests
class TestVoiceRouterIntegration:
    """Integration tests for voice router with other components"""
    
    @pytest.fixture
    async def router(self):
        """Create and initialize router for integration tests"""
        router = VoiceCommandRouter()
        await router.initialize()
        return router
    
    async def test_end_to_end_voice_processing(self, router):
        """Test complete end-to-end voice processing"""
        # Simulate real voice command processing
        commands = [
            "I feel stressed and need help",
            "Start a 10 minute meditation",
            "Write in my journal about today",
            "Show me breathing exercises"
        ]
        
        results = []
        for text in commands:
            command = VoiceCommand(
                text=text,
                language="en",
                confidence=0.8,
                user_id="integration_test_user"
            )
            
            result = await router.route_command(command)
            results.append(result)
        
        # All commands should be processed successfully
        assert all(r.success or r.fallback_used for r in results)
        
        # Should have different target services
        services = {r.target_service for r in results}
        assert len(services) >= 2
        
        # Metrics should be updated
        assert router.metrics.total_commands >= len(commands)
    
    async def test_multilingual_processing(self, router):
        """Test multilingual voice command processing"""
        multilingual_commands = [
            VoiceCommand(text="I feel happy", language="en", confidence=0.9),
            VoiceCommand(text="मैं खुश हूं", language="hi", confidence=0.8),
            VoiceCommand(text="Me siento feliz", language="es", confidence=0.85),
            VoiceCommand(text="Je me sens heureux", language="fr", confidence=0.82)
        ]
        
        results = []
        for command in multilingual_commands:
            command.intent = VoiceIntentType.MOOD_TRACKING
            result = await router.route_command(command)
            results.append(result)
        
        # All should be processed
        assert all(r.success for r in results)
        
        # Should route to same service (mood_service)
        services = {r.target_service for r in results}
        assert "mood_service" in services
        
        # Language should be preserved in headers
        for i, result in enumerate(results):
            expected_lang = multilingual_commands[i].language
            assert result.headers.get("X-Language") == expected_lang


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
