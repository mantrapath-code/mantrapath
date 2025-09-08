"""
Comprehensive tests for the translation service
"""
import pytest
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engines.translation_coordinator import TranslationCoordinator

class TestTranslationService:
    """Test the translation service functionality"""
    
    @pytest.fixture
    async def coordinator(self):
        """Create and initialize translation coordinator"""
        coord = TranslationCoordinator()
        await coord.initialize()
        return coord
    
    @pytest.mark.asyncio
    async def test_indian_language_translation(self, coordinator):
        """Test translation between Indian languages"""
        
        # Test English to Hindi
        result = await coordinator.translate(
            text="Hello, how are you?",
            source_language="en",
            target_language="hi"
        )
        
        assert result.translated_text is not None
        assert result.source_language == "en"
        assert result.target_language == "hi"
        assert result.quality_score > 0
        assert result.engine in ["bhashini", "indictrans2"]
    
    @pytest.mark.asyncio
    async def test_auto_language_detection(self, coordinator):
        """Test automatic language detection"""
        
        result = await coordinator.translate(
            text="Hello world",
            source_language="auto",
            target_language="hi"
        )
        
        assert result.source_language in ["en", "auto"]
        assert result.translated_text is not None
    
    @pytest.mark.asyncio
    async def test_multiple_indian_languages(self, coordinator):
        """Test support for multiple Indian languages"""
        
        test_cases = [
            ("en", "hi", "Hello"),
            ("en", "bn", "Thank you"),
            ("en", "ta", "Good morning"),
            ("en", "te", "How are you?"),
            ("en", "gu", "Welcome"),
        ]
        
        for source, target, text in test_cases:
            result = await coordinator.translate(
                text=text,
                source_language=source,
                target_language=target
            )
            
            assert result.translated_text is not None
            assert result.quality_score > 0
            print(f"{source}->{target}: '{text}' -> '{result.translated_text}' ({result.engine})")
    
    def test_supported_languages(self, coordinator):
        """Test that all Indian languages are supported"""
        
        languages = coordinator.get_supported_languages()
        
        # Check for major Indian languages
        expected_languages = [
            "hi", "bn", "ta", "te", "ml", "kn", "gu", "mr", "pa", "ur"
        ]
        
        for lang in expected_languages:
            assert lang in languages, f"Language {lang} should be supported"
        
        print(f"Total supported languages: {len(languages)}")
        print(f"Indian languages: {[l for l in languages if l in coordinator.indian_languages]}")
    
    @pytest.mark.asyncio
    async def test_health_check(self, coordinator):
        """Test health check functionality"""
        
        health = await coordinator.health_check()
        assert health is True
    
    @pytest.mark.asyncio
    async def test_engine_priority(self, coordinator):
        """Test that engines are prioritized correctly for Indian languages"""
        
        # For Indian languages, Bhashini should be prioritized
        priority = coordinator._get_engine_priority("en", "hi")
        assert priority[0] == "bhashini"
        
        # For non-Indian languages, IndicTrans2 should be first
        priority = coordinator._get_engine_priority("en", "fr")
        assert priority[0] == "indictrans2"
    
    def test_indian_language_detection(self, coordinator):
        """Test Indian language detection"""
        
        test_languages = ["hi", "bn", "ta", "te", "ml", "kn", "gu", "mr"]
        
        for lang in test_languages:
            is_indian = coordinator._is_indian_language(lang)
            assert is_indian is True, f"{lang} should be detected as Indian language"
        
        # Test non-Indian languages
        non_indian = ["en", "fr", "de", "es", "zh"]
        for lang in non_indian:
            is_indian = coordinator._is_indian_language(lang)
            assert is_indian is False, f"{lang} should not be detected as Indian language"

if __name__ == "__main__":
    # Run basic tests without pytest
    async def run_basic_tests():
        coordinator = TranslationCoordinator()
        await coordinator.initialize()
        
        print("Running basic translation tests...")
        
        # Test 1: English to Hindi
        result = await coordinator.translate("Hello", "en", "hi")
        print(f"EN->HI: Hello -> {result.translated_text} ({result.engine})")
        
        # Test 2: Multiple languages
        languages = ["hi", "bn", "ta", "te", "gu"]
        for lang in languages:
            result = await coordinator.translate("Thank you", "en", lang)
            print(f"EN->{lang.upper()}: Thank you -> {result.translated_text}")
        
        # Test 3: Language support
        supported = coordinator.get_supported_languages()
        indian_count = len([l for l in supported if l in coordinator.indian_languages])
        print(f"Supported languages: {len(supported)} total, {indian_count} Indian")
        
        print("All tests completed!")
    
    asyncio.run(run_basic_tests())
