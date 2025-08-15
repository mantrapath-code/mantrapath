"""
Unit tests for Cultural Processor
"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.core.cultural_processor import CulturalProcessor
from src.models import (
    CulturalContext, ActionWorkflow, WorkflowStep, ServiceAction,
    IntentType, ConfidenceLevel
)


class TestCulturalProcessor:
    """Test CulturalProcessor functionality"""
    
    @pytest.fixture
    def cultural_processor(self):
        """Create cultural processor instance"""
        return CulturalProcessor()
    
    @pytest.fixture
    def us_cultural_context(self):
        """US cultural context for testing"""
        return CulturalContext(
            language="en",
            cultural_region="US",
            communication_style="direct",
            formality_level="casual"
        )
    
    @pytest.fixture
    def japanese_cultural_context(self):
        """Japanese cultural context for testing"""
        return CulturalContext(
            language="ja",
            cultural_region="JP",
            communication_style="indirect",
            formality_level="formal",
            cultural_sensitivities=["privacy", "hierarchy"]
        )
    
    @pytest.fixture
    def sample_workflow(self, us_cultural_context):
        """Sample workflow for testing"""
        action = ServiceAction(
            service_name="journal_service",
            action_type="create_entry",
            parameters={
                "title": "My Meditation Journey",
                "content": "Today I practiced mindfulness"
            }
        )
        
        step = WorkflowStep(actions=[action])
        
        return ActionWorkflow(
            workflow_id=uuid4(),
            user_id=uuid4(),
            intent_type=IntentType.JOURNAL_ENTRY,
            steps=[step],
            cultural_context=us_cultural_context
        )
    
    @pytest.mark.asyncio
    async def test_adapt_workflow_us_context(self, cultural_processor, sample_workflow, us_cultural_context):
        """Test workflow adaptation for US cultural context"""
        adapted_workflow = await cultural_processor.adapt_workflow(
            sample_workflow, 
            us_cultural_context
        )
        
        assert adapted_workflow.cultural_context.language == "en"
        assert adapted_workflow.cultural_context.cultural_region == "US"
        
        # Check that content remains direct and casual
        action = adapted_workflow.steps[0].actions[0]
        assert action.cultural_adaptations.get("communication_style") == "direct"
    
    @pytest.mark.asyncio
    async def test_adapt_workflow_japanese_context(self, cultural_processor, sample_workflow, japanese_cultural_context):
        """Test workflow adaptation for Japanese cultural context"""
        adapted_workflow = await cultural_processor.adapt_workflow(
            sample_workflow,
            japanese_cultural_context
        )
        
        assert adapted_workflow.cultural_context.language == "ja"
        assert adapted_workflow.cultural_context.cultural_region == "JP"
        
        # Check formal adaptations
        action = adapted_workflow.steps[0].actions[0]
        assert action.cultural_adaptations.get("formality_level") == "formal"
        assert "privacy" in action.cultural_adaptations.get("sensitivities", [])
    
    @pytest.mark.asyncio
    async def test_localize_content_english(self, cultural_processor, us_cultural_context):
        """Test content localization for English"""
        original_content = {
            "greeting": "Hello",
            "message": "Welcome to your meditation journey"
        }
        
        localized = await cultural_processor.localize_content(
            original_content,
            us_cultural_context
        )
        
        assert localized["greeting"] == "Hello"
        assert "meditation journey" in localized["message"]
    
    @pytest.mark.asyncio
    async def test_localize_content_japanese(self, cultural_processor, japanese_cultural_context):
        """Test content localization for Japanese"""
        original_content = {
            "greeting": "Hello",
            "message": "Welcome to your meditation journey"
        }
        
        localized = await cultural_processor.localize_content(
            original_content,
            japanese_cultural_context
        )
        
        # Should be adapted for Japanese context
        assert localized["language"] == "ja"
        assert localized["formality_level"] == "formal"
    
    def test_apply_cultural_sensitivity_privacy_high(self, cultural_processor):
        """Test applying high privacy cultural sensitivity"""
        parameters = {
            "share_publicly": True,
            "include_location": True,
            "share_emotions": True
        }
        
        sensitivities = ["privacy"]
        adapted = cultural_processor._apply_cultural_sensitivities(
            parameters,
            sensitivities
        )
        
        assert adapted["share_publicly"] is False
        assert adapted["include_location"] is False
        assert adapted.get("privacy_level") == "high"
    
    def test_apply_cultural_sensitivity_hierarchy(self, cultural_processor):
        """Test applying hierarchy cultural sensitivity"""
        parameters = {
            "tone": "casual",
            "address_style": "first_name"
        }
        
        sensitivities = ["hierarchy"]
        adapted = cultural_processor._apply_cultural_sensitivities(
            parameters,
            sensitivities
        )
        
        assert adapted["tone"] == "formal"
        assert adapted["address_style"] == "title_last_name"
    
    def test_adapt_communication_style_direct(self, cultural_processor):
        """Test adapting communication style to direct"""
        content = "Maybe you could consider trying meditation"
        
        adapted = cultural_processor._adapt_communication_style(
            content,
            "direct"
        )
        
        assert "Try meditation" in adapted or "Start meditating" in adapted
    
    def test_adapt_communication_style_indirect(self, cultural_processor):
        """Test adapting communication style to indirect"""
        content = "Start meditating now"
        
        adapted = cultural_processor._adapt_communication_style(
            content,
            "indirect"
        )
        
        assert "might" in adapted or "could" in adapted or "perhaps" in adapted
    
    def test_get_cultural_defaults_us(self, cultural_processor):
        """Test getting cultural defaults for US"""
        defaults = cultural_processor._get_cultural_defaults("US")
        
        assert defaults["communication_style"] == "direct"
        assert defaults["formality_level"] == "casual"
        assert defaults["privacy_expectations"] == "medium"
    
    def test_get_cultural_defaults_japan(self, cultural_processor):
        """Test getting cultural defaults for Japan"""
        defaults = cultural_processor._get_cultural_defaults("JP")
        
        assert defaults["communication_style"] == "indirect"
        assert defaults["formality_level"] == "formal"
        assert defaults["privacy_expectations"] == "high"
    
    def test_get_cultural_defaults_unknown(self, cultural_processor):
        """Test getting cultural defaults for unknown region"""
        defaults = cultural_processor._get_cultural_defaults("UNKNOWN")
        
        # Should return neutral defaults
        assert defaults["communication_style"] == "neutral"
        assert defaults["formality_level"] == "neutral"
        assert defaults["privacy_expectations"] == "medium"
    
    @pytest.mark.asyncio
    async def test_validate_cultural_appropriateness_appropriate(self, cultural_processor, japanese_cultural_context):
        """Test validating culturally appropriate content"""
        content = {
            "message": "Please consider this meditation practice",
            "tone": "respectful"
        }
        
        is_appropriate = await cultural_processor.validate_cultural_appropriateness(
            content,
            japanese_cultural_context
        )
        
        assert is_appropriate is True
    
    @pytest.mark.asyncio
    async def test_validate_cultural_appropriateness_inappropriate(self, cultural_processor, japanese_cultural_context):
        """Test validating culturally inappropriate content"""
        content = {
            "message": "You must do this meditation right now!",
            "tone": "demanding"
        }
        
        is_appropriate = await cultural_processor.validate_cultural_appropriateness(
            content,
            japanese_cultural_context
        )
        
        assert is_appropriate is False
    
    def test_supported_languages(self, cultural_processor):
        """Test supported languages list"""
        languages = cultural_processor.supported_languages
        
        assert "en" in languages
        assert "ja" in languages
        assert "es" in languages
        assert "fr" in languages
        assert len(languages) >= 4
    
    def test_supported_regions(self, cultural_processor):
        """Test supported cultural regions list"""
        regions = cultural_processor.supported_regions
        
        assert "US" in regions
        assert "JP" in regions
        assert "ES" in regions
        assert "FR" in regions
        assert len(regions) >= 4
