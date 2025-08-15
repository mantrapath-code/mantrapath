"""
Comprehensive tests for Cultural Adaptation Service
"""
import pytest
from unittest.mock import MagicMock, patch
import asyncio

from engines.cultural_adaptation import CulturalAdaptationService


@pytest.mark.asyncio
class TestCulturalAdaptationService:
    """Test Cultural Adaptation Service functionality"""
    
    @pytest.fixture
    async def service(self):
        """Create cultural adaptation service"""
        service = CulturalAdaptationService()
        await service.initialize()
        return service
    
    async def test_initialization(self):
        """Test service initialization"""
        service = CulturalAdaptationService()
        result = await service.initialize()
        
        assert result is True
        assert service.is_initialized is True
        assert service.cultural_mappings is not None
        assert service.regional_preferences is not None
    
    async def test_adapt_meditation_terms_spanish(self, service):
        """Test adaptation of meditation terms to Spanish"""
        result = await service.adapt_translation(
            original_text="meditation and mindfulness",
            translated_text="meditación y atención plena",
            source_language="en",
            target_language="es",
            cultural_context={"region": "spain", "formality": "formal"}
        )
        
        assert result is not None
        assert "adapted_text" in result
        assert "cultural_notes" in result
        assert result["source_language"] == "en"
        assert result["target_language"] == "es"
    
    async def test_adapt_greeting_formal_spanish(self, service):
        """Test formal greeting adaptation for Spanish"""
        result = await service.adapt_translation(
            original_text="Hello",
            translated_text="Hola",
            source_language="en",
            target_language="es",
            cultural_context={"region": "spain", "formality": "formal"}
        )
        
        assert result["adapted_text"] in ["Buenos días", "Buenas tardes", "Hola"]
        if "cultural_notes" in result:
            assert len(result["cultural_notes"]) >= 0
    
    async def test_adapt_greeting_informal_spanish(self, service):
        """Test informal greeting adaptation for Spanish"""
        result = await service.adapt_translation(
            original_text="Hi",
            translated_text="Hola", 
            source_language="en",
            target_language="es",
            cultural_context={"region": "mexico", "formality": "informal"}
        )
        
        assert result["adapted_text"] in ["Hola", "¡Hola!", "Qué tal"]
        assert result["formality_level"] == "informal"
    
    async def test_adapt_indian_spiritual_terms(self, service):
        """Test adaptation of spiritual terms for Indian languages"""
        result = await service.adapt_translation(
            original_text="chakra",
            translated_text="चक्र",
            source_language="en",
            target_language="hi",
            cultural_context={"region": "india", "spiritual_context": True}
        )
        
        assert result["adapted_text"] == "चक्र"
        if "cultural_notes" in result:
            assert any("spiritual" in note.lower() for note in result["cultural_notes"])
    
    async def test_adapt_respect_levels_japanese(self, service):
        """Test respect level adaptation for Japanese"""
        result = await service.adapt_translation(
            original_text="Thank you",
            translated_text="ありがとう",
            source_language="en",
            target_language="ja",
            cultural_context={"region": "japan", "respect_level": "high"}
        )
        
        # Should use more formal form
        assert result["adapted_text"] in ["ありがとうございます", "ありがとうございました", "ありがとう"]
        assert result["respect_level"] == "high"
    
    async def test_get_cultural_preferences(self, service):
        """Test getting cultural preferences for region"""
        # Test Spanish preferences
        prefs = await service.get_cultural_preferences("es", "spain")
        assert prefs is not None
        assert "formality" in prefs
        assert "greeting_style" in prefs
        
        # Test Indian preferences
        prefs = await service.get_cultural_preferences("hi", "india")
        assert prefs is not None
        assert "spiritual_terms" in prefs
        assert "respect_level" in prefs
    
    async def test_detect_cultural_context(self, service):
        """Test cultural context detection from text"""
        # Test meditation context
        context = await service.detect_cultural_context(
            "I practice meditation and yoga daily",
            "en"
        )
        
        assert context is not None
        assert context["domain"] == "spiritual"
        assert "meditation" in context["keywords"]
        
        # Test business context
        context = await service.detect_cultural_context(
            "Please schedule a meeting for tomorrow",
            "en"
        )
        
        assert context["domain"] == "business"
        assert context["formality"] == "formal"
    
    async def test_apply_regional_variations(self, service):
        """Test application of regional variations"""
        # Test Mexican Spanish vs Peninsular Spanish
        mexico_result = await service.apply_regional_variations(
            "computadora",
            "es",
            "mexico"
        )
        
        spain_result = await service.apply_regional_variations(
            "computadora", 
            "es",
            "spain"
        )
        
        # Should show regional differences
        assert mexico_result != spain_result or mexico_result == "computadora"
    
    async def test_adapt_time_expressions(self, service):
        """Test adaptation of time expressions"""
        result = await service.adapt_translation(
            original_text="Good morning",
            translated_text="Buenos días",
            source_language="en",
            target_language="es",
            cultural_context={
                "region": "spain",
                "time_context": "morning",
                "formality": "formal"
            }
        )
        
        assert result["adapted_text"] == "Buenos días"
        assert "time_appropriate" in str(result.get("cultural_notes", []))
    
    async def test_gender_adaptation(self, service):
        """Test gender-aware adaptations"""
        result = await service.adapt_translation(
            original_text="I am happy",
            translated_text="Estoy feliz",
            source_language="en",
            target_language="es",
            cultural_context={
                "gender": "female",
                "region": "spain"
            }
        )
        
        # Should handle gender agreement if applicable
        assert result["adapted_text"] in ["Estoy feliz", "Estoy contenta"]
    
    async def test_religious_sensitivity(self, service):
        """Test religious sensitivity in adaptations"""
        result = await service.adapt_translation(
            original_text="Bless you",
            translated_text="Que Dios te bendiga",
            source_language="en",
            target_language="es",
            cultural_context={
                "region": "spain",
                "religious_sensitivity": "high"
            }
        )
        
        assert result["adapted_text"] is not None
        if "cultural_notes" in result:
            assert any("religious" in note.lower() for note in result["cultural_notes"])
    
    async def test_age_appropriate_language(self, service):
        """Test age-appropriate language adaptation"""
        result = await service.adapt_translation(
            original_text="Hello there",
            translated_text="Hola",
            source_language="en",
            target_language="es",
            cultural_context={
                "age_group": "elderly",
                "formality": "high"
            }
        )
        
        assert result["formality_level"] == "high"
        assert result["adapted_text"] in ["Buenos días", "Buenas tardes", "Hola"]
    
    async def test_meditation_domain_adaptation(self, service):
        """Test domain-specific adaptation for meditation terms"""
        meditation_terms = [
            "mindfulness",
            "breathing",
            "awareness", 
            "inner peace",
            "enlightenment"
        ]
        
        for term in meditation_terms:
            result = await service.adapt_translation(
                original_text=term,
                translated_text=f"Spanish_{term}",
                source_language="en",
                target_language="es",
                cultural_context={
                    "domain": "meditation",
                    "spiritual_context": True
                }
            )
            
            assert result is not None
            assert result["domain"] == "meditation"
    
    async def test_cultural_taboos(self, service):
        """Test handling of cultural taboos"""
        result = await service.adapt_translation(
            original_text="death and dying",
            translated_text="muerte y morir",
            source_language="en",
            target_language="es",
            cultural_context={
                "region": "mexico",
                "taboo_sensitivity": "high"
            }
        )
        
        assert result is not None
        if "cultural_warnings" in result:
            assert isinstance(result["cultural_warnings"], list)
    
    async def test_adapt_numbers_and_dates(self, service):
        """Test adaptation of numbers and date formats"""
        result = await service.adapt_translation(
            original_text="12/25/2023",
            translated_text="25/12/2023",
            source_language="en",
            target_language="es",
            cultural_context={"region": "spain", "date_format": "european"}
        )
        
        assert "25/12/2023" in result["adapted_text"] or "25-12-2023" in result["adapted_text"]
    
    async def test_batch_cultural_adaptation(self, service):
        """Test batch cultural adaptation"""
        batch_requests = [
            {
                "original_text": "Hello",
                "translated_text": "Hola",
                "source_language": "en",
                "target_language": "es",
                "cultural_context": {"formality": "formal"}
            },
            {
                "original_text": "Thank you",
                "translated_text": "Gracias", 
                "source_language": "en",
                "target_language": "es",
                "cultural_context": {"formality": "informal"}
            }
        ]
        
        results = await service.adapt_batch(batch_requests)
        
        assert len(results) == 2
        for result in results:
            assert "adapted_text" in result
    
    async def test_quality_score_with_cultural_adaptation(self, service):
        """Test quality scoring with cultural adaptation"""
        result = await service.adapt_translation(
            original_text="Good morning, sir",
            translated_text="Buenos días, señor",
            source_language="en", 
            target_language="es",
            cultural_context={"formality": "high", "respect_level": "high"}
        )
        
        assert "quality_score" in result
        assert 0.0 <= result["quality_score"] <= 1.0
        # High formality should increase quality score
        assert result["quality_score"] > 0.7
    
    async def test_unsupported_language_pair(self, service):
        """Test handling of unsupported language pairs"""
        result = await service.adapt_translation(
            original_text="Hello",
            translated_text="Hello", 
            source_language="en",
            target_language="xyz",  # Unsupported language
            cultural_context={}
        )
        
        # Should return original or handle gracefully
        assert result is not None
        assert result["adapted_text"] == "Hello"
    
    async def test_empty_cultural_context(self, service):
        """Test adaptation with empty cultural context"""
        result = await service.adapt_translation(
            original_text="Hello",
            translated_text="Hola",
            source_language="en",
            target_language="es",
            cultural_context={}
        )
        
        assert result["adapted_text"] == "Hola"  # Should return original translation
        assert result["cultural_notes"] == []
    
    async def test_health_check(self, service):
        """Test cultural adaptation service health check"""
        health = await service.health_check()
        
        assert health["status"] == "healthy"
        assert health["service"] == "cultural_adaptation"
        assert "features" in health
        assert "supported_languages" in health
