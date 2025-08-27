"""
Comprehensive Cultural Processor Functionality Tests
Tests real cultural adaptation, language processing, and regional customization
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from src.core.cultural_processor import CulturalProcessor
from src.models import CulturalContext, WorkflowResult, WorkflowStatus


@pytest.mark.asyncio
class TestCulturalProcessorFunctionality:
    """Test comprehensive cultural processing functionality"""
    
    async def test_hindi_cultural_context_processing(self):
        """Test processing Hindi input with North Indian cultural context"""
        processor = CulturalProcessor()
        
        hindi_text = "मैं अपने मूड को ट्रैक करना चाहता हूं"
        
        context = await processor.process_cultural_context(
            hindi_text,
            cultural_preferences={"language": "hi", "cultural_region": "india_north"}
        )
        
        assert context.language == "hi"
        assert context.cultural_region == "india_north"
        assert context.communication_style == "respectful"
        assert context.formality_level == "high"
        assert "family_values" in context.cultural_sensitivities
        assert "religious_respect" in context.cultural_sensitivities
    
    async def test_tamil_south_indian_adaptation(self):
        """Test Tamil language with South Indian cultural adaptations"""
        processor = CulturalProcessor()
        
        context = await processor.process_cultural_context(
            "I want to journal",
            cultural_preferences={"language": "ta", "cultural_region": "india_south"}
        )
        
        # Check regional mapping
        assert context.language == "ta"
        assert context.cultural_region == "india_south"
        
        # Test cultural defaults
        defaults = processor._get_cultural_defaults("india_south")
        assert defaults["language"] == "ta"
        assert "education" in defaults["cultural_values"]
        assert "pongal" in defaults["festivals"]
        assert defaults["currency"] == "INR"
    
    async def test_gujarati_business_culture_adaptation(self):
        """Test Gujarati business culture from West India"""
        processor = CulturalProcessor()
        
        context = await processor.process_cultural_context(
            "business meeting reminder",
            cultural_preferences={"language": "gu", "cultural_region": "india_west"}
        )
        
        defaults = processor._get_cultural_defaults("india_west")
        assert defaults["communication_style"] == "business_friendly"
        assert "entrepreneurship" in defaults["cultural_values"]
        assert "ganesh_chaturthi" in defaults["festivals"]
        assert context.formality_level == "medium"
    
    async def test_bengali_intellectual_culture(self):
        """Test Bengali intellectual culture from East India"""
        processor = CulturalProcessor()
        
        context = await processor.process_cultural_context(
            "poetry and literature discussion",
            cultural_preferences={"language": "bn", "cultural_region": "india_east"}
        )
        
        defaults = processor._get_cultural_defaults("india_east")
        assert defaults["communication_style"] == "intellectual"
        assert "literature" in defaults["cultural_values"]
        assert "durga_puja" in defaults["festivals"]
        
        # Test cultural sensitivities
        sensitivities = processor._get_cultural_sensitivities("bn", "india_east")
        assert "intellectual_respect" in sensitivities
        assert "artistic_appreciation" in sensitivities
    
    async def test_assamese_northeast_harmony(self):
        """Test Assamese culture from Northeast India"""
        processor = CulturalProcessor()
        
        context = await processor.process_cultural_context(
            "nature meditation session",
            cultural_preferences={"language": "as", "cultural_region": "india_northeast"}
        )
        
        defaults = processor._get_cultural_defaults("india_northeast")
        assert defaults["communication_style"] == "warm"
        assert "nature" in defaults["cultural_values"]
        assert "bihu" in defaults["festivals"]
        
        sensitivities = processor._get_cultural_sensitivities("as", "india_northeast")
        assert "nature_respect" in sensitivities
        assert "tribal_sensitivity" in sensitivities
    
    async def test_text_normalization_multilingual(self):
        """Test text normalization across different languages"""
        processor = CulturalProcessor()
        
        # English normalization
        en_context = CulturalContext(
            language="en",
            cultural_region="north_america",
            communication_style="direct",
            formality_level="medium",
            cultural_sensitivities=[],
            time_zone="UTC",
            date_format="MM/DD/YYYY"
        )
        
        normalized_en = await processor.normalize_text(
            "  hey, gonna write   in my journal!!!  ",
            en_context
        )
        assert "hey" not in normalized_en  # Should be normalized to "hello"
        assert "going to" in normalized_en  # "gonna" -> "going to"
        
        # Hindi normalization
        hi_context = CulturalContext(
            language="hi",
            cultural_region="india_north",
            communication_style="respectful",
            formality_level="high",
            cultural_sensitivities=["family_values"],
            time_zone="Asia/Kolkata",
            date_format="DD/MM/YYYY"
        )
        
        normalized_hi = await processor.normalize_text(
            "  मैं   अपना मूड ट्रैक करूंगा  ",
            hi_context
        )
        assert len(normalized_hi.strip()) > 0
        assert normalized_hi.count(" ") < 3  # Should normalize whitespace
    
    async def test_action_parameter_cultural_adaptation(self):
        """Test cultural adaptation of action parameters"""
        processor = CulturalProcessor()
        
        # Hindi formal context
        hi_context = CulturalContext(
            language="hi",
            cultural_region="india_north",
            communication_style="respectful",
            formality_level="high",
            cultural_sensitivities=["family_values", "religious_respect"],
            time_zone="Asia/Kolkata",
            date_format="DD/MM/YYYY"
        )
        
        original_params = {
            "content": "Create a journal entry",
            "user_id": "12345",
            "action_type": "journal_creation"
        }
        
        adapted_params = await processor.adapt_action_parameters(
            original_params,
            {"response_style": "respectful"},
            hi_context
        )
        
        assert adapted_params["formality_level"] == "high"
        assert adapted_params["cultural_metadata"]["language"] == "hi"
        assert adapted_params["cultural_metadata"]["communication_style"] == "respectful"
        assert "family_values" in adapted_params["cultural_metadata"]["cultural_sensitivities"]
    
    async def test_response_message_creation_multilingual(self):
        """Test creating culturally appropriate response messages"""
        processor = CulturalProcessor()
        
        # Create mock workflow result
        workflow_result = WorkflowResult(
            workflow_id="test-123",
            status=WorkflowStatus.COMPLETED,
            completed_actions=2,
            failed_actions=0,
            total_execution_time_ms=1500,
            results=[]
        )
        
        # English response
        en_context = CulturalContext(
            language="en",
            cultural_region="north_america",
            communication_style="direct",
            formality_level="medium",
            cultural_sensitivities=[],
            time_zone="UTC",
            date_format="MM/DD/YYYY"
        )
        
        en_message = await processor.create_response_message(workflow_result, en_context)
        assert "successfully completed" in en_message.lower()
        assert "1.5 seconds" in en_message
        
        # Hindi response with high formality
        hi_context = CulturalContext(
            language="hi",
            cultural_region="india_north",
            communication_style="respectful",
            formality_level="high",
            cultural_sensitivities=["family_values"],
            time_zone="Asia/Kolkata",
            date_format="DD/MM/YYYY"
        )
        
        hi_message = await processor.create_response_message(workflow_result, hi_context)
        assert "आदरणीय उपयोगकर्ता" in hi_message  # Formal greeting
        assert "सेकंड" in hi_message  # Time in Hindi
    
    async def test_failed_workflow_cultural_response(self):
        """Test cultural responses for failed workflows"""
        processor = CulturalProcessor()
        
        failed_result = WorkflowResult(
            workflow_id="failed-123",
            status=WorkflowStatus.FAILED,
            completed_actions=1,
            failed_actions=2,
            total_execution_time_ms=800,
            results=[]
        )
        
        hi_context = CulturalContext(
            language="hi",
            cultural_region="india_north",
            communication_style="respectful",
            formality_level="high",
            cultural_sensitivities=["family_values"],
            time_zone="Asia/Kolkata",
            date_format="DD/MM/YYYY"
        )
        
        failure_message = await processor.create_response_message(failed_result, hi_context)
        assert "खेद" in failure_message  # Apology in Hindi
        assert "कठिनाइयों" in failure_message  # "difficulties" in Hindi
    
    async def test_comprehensive_cultural_adaptations(self):
        """Test comprehensive cultural adaptation system"""
        processor = CulturalProcessor()
        
        # Test all supported Indian regions
        indian_regions = [
            "india_north", "india_south", "india_west", 
            "india_east", "india_northeast", "india_central"
        ]
        
        for region in indian_regions:
            defaults = processor._get_cultural_defaults(region)
            
            # All Indian regions should have INR currency
            assert defaults["currency"] == "INR"
            assert defaults["date_format"] == "DD/MM/YYYY"
            assert "family" in str(defaults["cultural_values"]).lower()
            
            # Should have specific festivals
            assert len(defaults["festivals"]) >= 3
            assert "diwali" in defaults["festivals"]
    
    def test_language_to_region_mapping_accuracy(self):
        """Test accurate language to region mapping"""
        processor = CulturalProcessor()
        
        # Test Indian language mappings
        language_mappings = {
            "hi": "india_north",    # Hindi -> North India
            "ta": "india_south",    # Tamil -> South India
            "te": "india_south",    # Telugu -> South India
            "mr": "india_west",     # Marathi -> West India
            "gu": "india_west",     # Gujarati -> West India
            "bn": "india_east",     # Bengali -> East India
            "as": "india_northeast", # Assamese -> Northeast
            "pa": "india_north",    # Punjabi -> North India
        }
        
        for language, expected_region in language_mappings.items():
            inferred_region = processor._infer_cultural_region(language)
            assert inferred_region == expected_region, f"{language} should map to {expected_region}"
    
    def test_cultural_sensitivity_mapping(self):
        """Test cultural sensitivity mapping for different regions"""
        processor = CulturalProcessor()
        
        # Test specific cultural sensitivities
        sensitivity_tests = [
            ("hi", "india_north", ["family_values", "religious_respect", "elder_respect", "caste_sensitivity"]),
            ("ta", "india_south", ["family_values", "educational_respect", "cultural_pride", "language_pride"]),
            ("mr", "india_west", ["family_values", "business_ethics", "festival_importance", "community_bonds"]),
            ("bn", "india_east", ["intellectual_respect", "artistic_appreciation", "family_values", "cultural_heritage"]),
            ("as", "india_northeast", ["nature_respect", "tribal_sensitivity", "community_harmony", "simplicity"])
        ]
        
        for language, region, expected_sensitivities in sensitivity_tests:
            sensitivities = processor._get_cultural_sensitivities(language, region)
            for sensitivity in expected_sensitivities:
                assert sensitivity in sensitivities, f"{sensitivity} should be in {region} sensitivities"
    
    def test_supported_regions_comprehensiveness(self):
        """Test that all supported regions are properly implemented"""
        processor = CulturalProcessor()
        
        supported_regions = processor.supported_regions
        
        # Should include all Indian regions
        indian_regions = [
            "india_north", "india_south", "india_west", 
            "india_east", "india_northeast", "india_central"
        ]
        
        for region in indian_regions:
            assert region in supported_regions, f"{region} should be in supported regions"
        
        # Should include global regions
        global_regions = ["north_america", "europe", "east_asia", "middle_east"]
        for region in global_regions:
            assert region in supported_regions, f"{region} should be in supported regions"
        
        # Test that all supported regions have defaults
        for region in supported_regions:
            defaults = processor._get_cultural_defaults(region)
            assert "communication_style" in defaults
            assert "formality_level" in defaults
            assert "language" in defaults


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
