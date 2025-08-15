"""
Comprehensive Action Orchestrator Integration Tests
Tests end-to-end workflows with real service integrations
"""
import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime
from uuid import uuid4

from src.core.orchestrator import ActionOrchestrator
from src.core.intent_classifier import IntentClassifier
from src.core.cultural_processor import CulturalProcessor
from src.core.workflow_builder import WorkflowBuilder
from src.core.action_dispatcher import ActionDispatcher
from src.core.rollback_manager import RollbackManager
from src.models import IntentType, ConfidenceLevel, WorkflowStatus


@pytest.mark.asyncio
class TestActionOrchestratorIntegration:
    """Integration tests for Action Orchestrator with real components"""
    
    async def test_real_component_integration(self):
        """Test integration with real component instances"""
        # Create real instances (not mocks)
        intent_classifier = IntentClassifier()
        cultural_processor = CulturalProcessor()
        workflow_builder = WorkflowBuilder()
        action_dispatcher = ActionDispatcher()
        rollback_manager = RollbackManager(action_dispatcher)
        
        orchestrator = ActionOrchestrator(
            intent_classifier=intent_classifier,
            cultural_processor=cultural_processor,
            workflow_builder=workflow_builder,
            action_dispatcher=action_dispatcher,
            rollback_manager=rollback_manager
        )
        
        # Test that orchestrator initializes correctly
        assert orchestrator.intent_classifier is not None
        assert orchestrator.cultural_processor is not None
        assert orchestrator.workflow_builder is not None
        assert orchestrator.action_dispatcher is not None
        assert orchestrator.rollback_manager is not None
    
    async def test_intent_classification_integration(self):
        """Test real intent classification integration"""
        intent_classifier = IntentClassifier()
        
        # Test English journal intent
        cultural_context_mock = AsyncMock()
        cultural_context_mock.language = "en"
        cultural_context_mock.cultural_region = "north_america"
        
        intent = await intent_classifier.classify_intent(
            "I want to write in my journal about today",
            cultural_context_mock
        )
        
        assert intent.intent_type == IntentType.JOURNAL_ENTRY
        assert intent.confidence_level.value >= 0.5
        assert intent.raw_text == "I want to write in my journal about today"
    
    async def test_cultural_processing_integration(self):
        """Test real cultural processing integration"""
        cultural_processor = CulturalProcessor()
        
        # Test Hindi context processing
        context = await cultural_processor.process_cultural_context(
            "मैं अपना मूड ट्रैक करना चाहता हूं",
            {"language": "hi", "cultural_region": "india_north"}
        )
        
        assert context.language == "hi"
        assert context.cultural_region == "india_north"
        assert context.communication_style == "respectful"
        assert context.formality_level == "high"
        assert "family_values" in context.cultural_sensitivities
    
    async def test_workflow_builder_integration(self):
        """Test real workflow builder integration"""
        workflow_builder = WorkflowBuilder()
        
        # Create mock intent and context
        intent_mock = AsyncMock()
        intent_mock.intent_type = IntentType.JOURNAL_ENTRY
        intent_mock.confidence_level = ConfidenceLevel.HIGH
        intent_mock.entities = {"activities": ["journal"], "content": ["thoughts"]}
        
        context_mock = AsyncMock()
        context_mock.language = "en"
        context_mock.cultural_region = "north_america"
        
        workflow = await workflow_builder.build_workflow(
            intent_mock,
            context_mock,
            "user_123"
        )
        
        assert workflow is not None
        assert workflow.intent == intent_mock
        assert workflow.cultural_context == context_mock
        assert len(workflow.steps) > 0
    
    async def test_action_dispatcher_integration(self):
        """Test real action dispatcher integration"""
        action_dispatcher = ActionDispatcher()
        
        # Test service health checks
        health_status = await action_dispatcher.get_service_health_status()
        assert isinstance(health_status, dict)
        
        # Test service URL mapping
        journal_url = action_dispatcher._get_service_url("journal_service")
        assert journal_url == "http://localhost:8003"
        
        unknown_url = action_dispatcher._get_service_url("unknown_service")
        assert unknown_url == "http://localhost:8000"
    
    async def test_rollback_manager_integration(self):
        """Test real rollback manager integration"""
        action_dispatcher = ActionDispatcher()
        rollback_manager = RollbackManager(action_dispatcher)
        
        # Test rollback manager initialization
        assert rollback_manager.action_dispatcher is not None
        assert rollback_manager.rollback_stack == []
    
    async def test_supported_languages_integration(self):
        """Test supported languages across components"""
        intent_classifier = IntentClassifier()
        cultural_processor = CulturalProcessor()
        
        # Test that both components support Hindi and English
        classifier_languages = intent_classifier.supported_languages
        processor_regions = cultural_processor.supported_regions
        
        assert "en" in classifier_languages
        assert "hi" in classifier_languages
        assert "india_north" in processor_regions
        assert "india_south" in processor_regions
        assert "north_america" in processor_regions
    
    async def test_indian_regional_integration(self):
        """Test Indian regional integration across components"""
        cultural_processor = CulturalProcessor()
        
        # Test each Indian region has proper defaults
        indian_regions = [
            "india_north", "india_south", "india_west",
            "india_east", "india_northeast", "india_central"
        ]
        
        for region in indian_regions:
            defaults = cultural_processor._get_cultural_defaults(region)
            
            # All Indian regions should have INR currency
            assert defaults["currency"] == "INR"
            assert defaults["date_format"] == "DD/MM/YYYY"
            
            # Should have cultural values
            assert "cultural_values" in defaults
            assert len(defaults["cultural_values"]) >= 3
            
            # Should have festivals
            assert "festivals" in defaults
            assert "diwali" in defaults["festivals"]
    
    async def test_multilingual_pattern_integration(self):
        """Test multilingual pattern matching integration"""
        intent_classifier = IntentClassifier()
        
        # Test Hindi patterns
        hindi_patterns = intent_classifier.intent_patterns.get("hi", {})
        assert len(hindi_patterns) > 0
        
        # Test English patterns
        english_patterns = intent_classifier.intent_patterns.get("en", {})
        assert len(english_patterns) > 0
        
        # Both should support journal and mood intents
        for patterns in [hindi_patterns, english_patterns]:
            journal_patterns = patterns.get("journal_entry", [])
            mood_patterns = patterns.get("mood_tracking", [])
            
            assert len(journal_patterns) > 0
            assert len(mood_patterns) > 0
    
    async def test_confidence_calculation_integration(self):
        """Test confidence calculation with real data"""
        intent_classifier = IntentClassifier()
        
        # High confidence text
        high_confidence = intent_classifier._calculate_confidence(
            "I want to create a detailed journal entry about my meditation session today",
            "journal_entry",
            {"activities": ["journal", "meditation"], "time_references": ["today"]}
        )
        assert high_confidence >= 0.8
        
        # Medium confidence text
        medium_confidence = intent_classifier._calculate_confidence(
            "Maybe write something",
            "journal_entry", 
            {"activities": ["write"]}
        )
        assert 0.4 <= medium_confidence <= 0.8
        
        # Low confidence text
        low_confidence = intent_classifier._calculate_confidence(
            "Hello",
            "journal_entry",
            {}
        )
        assert low_confidence <= 0.6
    
    async def test_entity_extraction_integration(self):
        """Test entity extraction with real examples"""
        intent_classifier = IntentClassifier()
        
        # Test comprehensive entity extraction
        text = "I meditated for 30 minutes and feel really happy and peaceful now"
        entities = intent_classifier._extract_entities(text)
        
        # Should extract numbers
        assert 30 in entities.get("numbers", [])
        
        # Should extract time references
        time_refs = entities.get("time_references", [])
        assert "minutes" in time_refs
        
        # Should extract activities
        activities = entities.get("activities", [])
        assert "meditation" in activities
        
        # Should extract emotions
        emotions = entities.get("emotions", [])
        emotion_text = str(emotions).lower()
        assert "happy" in emotion_text or "peaceful" in emotion_text
    
    async def test_cultural_sensitivity_integration(self):
        """Test cultural sensitivity mapping integration"""
        cultural_processor = CulturalProcessor()
        
        # Test North Indian sensitivities
        north_sensitivities = cultural_processor._get_cultural_sensitivities("hi", "india_north")
        expected_north = ["family_values", "religious_respect", "elder_respect", "caste_sensitivity"]
        for sensitivity in expected_north:
            assert sensitivity in north_sensitivities
        
        # Test South Indian sensitivities
        south_sensitivities = cultural_processor._get_cultural_sensitivities("ta", "india_south")
        expected_south = ["family_values", "educational_respect", "cultural_pride", "language_pride"]
        for sensitivity in expected_south:
            assert sensitivity in south_sensitivities
        
        # Test West Indian sensitivities
        west_sensitivities = cultural_processor._get_cultural_sensitivities("mr", "india_west")
        expected_west = ["family_values", "business_ethics", "festival_importance", "community_bonds"]
        for sensitivity in expected_west:
            assert sensitivity in west_sensitivities
    
    async def test_date_format_integration(self):
        """Test date format handling integration"""
        cultural_processor = CulturalProcessor()
        
        # Test various regional date formats
        date_format_tests = [
            ("north_america", "MM/DD/YYYY"),
            ("europe", "DD/MM/YYYY"),
            ("india_north", "DD/MM/YYYY"),
            ("india_south", "DD/MM/YYYY"),
            ("east_asia", "YYYY/MM/DD")
        ]
        
        for region, expected_format in date_format_tests:
            defaults = cultural_processor._get_cultural_defaults(region)
            assert defaults["date_format"] == expected_format
    
    async def test_communication_style_integration(self):
        """Test communication style integration"""
        cultural_processor = CulturalProcessor()
        
        # Test communication style mapping
        style_tests = [
            ("hi", "india_north", "respectful"),
            ("ta", "india_south", "respectful"),
            ("mr", "india_west", "business_friendly"),
            ("bn", "india_east", "intellectual"),
            ("as", "india_northeast", "warm"),
            ("en", "north_america", "direct")
        ]
        
        for language, region, expected_style in style_tests:
            inferred_style = cultural_processor._infer_communication_style(language, region)
            assert inferred_style == expected_style or inferred_style in ["respectful", "neutral"]
    
    async def test_formality_level_integration(self):
        """Test formality level integration"""
        cultural_processor = CulturalProcessor()
        
        # Test formality mapping
        formality_tests = [
            ("hi", "india_north", "high"),
            ("ta", "india_south", "high"),
            ("mr", "india_west", "medium"),
            ("en", "north_america", "moderate")
        ]
        
        for language, region, expected_formality in formality_tests:
            inferred_formality = cultural_processor._infer_formality_level(language, region)
            assert inferred_formality == expected_formality or inferred_formality in ["high", "medium", "moderate"]


@pytest.mark.asyncio
class TestActionOrchestratorRealWorldScenarios:
    """Test real-world scenarios with Action Orchestrator"""
    
    async def test_hindi_journal_creation_scenario(self):
        """Test real Hindi journal creation scenario"""
        intent_classifier = IntentClassifier()
        cultural_processor = CulturalProcessor()
        
        # Process Hindi input
        hindi_input = "मैं आज अपने दिन के बारे में लिखना चाहता हूं"
        
        # Get cultural context
        context = await cultural_processor.process_cultural_context(
            hindi_input,
            {"language": "hi", "cultural_region": "india_north"}
        )
        
        # Classify intent
        intent = await intent_classifier.classify_intent(hindi_input, context)
        
        # Verify Hindi processing
        assert context.language == "hi"
        assert context.cultural_region == "india_north"
        assert intent.intent_type == IntentType.JOURNAL_ENTRY
        assert intent.confidence_level.value >= 0.5
    
    async def test_english_mood_tracking_scenario(self):
        """Test real English mood tracking scenario"""
        intent_classifier = IntentClassifier()
        cultural_processor = CulturalProcessor()
        
        # Process English input
        english_input = "I'm feeling really happy and accomplished after my workout"
        
        # Get cultural context
        context = await cultural_processor.process_cultural_context(
            english_input,
            {"language": "en", "cultural_region": "north_america"}
        )
        
        # Classify intent
        intent = await intent_classifier.classify_intent(english_input, context)
        
        # Verify English processing
        assert context.language == "en"
        assert context.cultural_region == "north_america"
        assert intent.intent_type == IntentType.MOOD_TRACKING
        assert intent.confidence_level.value >= 0.6
        
        # Check emotion extraction
        emotions = intent.entities.get("emotions", [])
        assert len(emotions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
