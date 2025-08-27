"""
Test cases for Translation Service with multiple languages
"""
import pytest
import pytest_asyncio
import asyncio
from services.simple_translation_engine import TranslationEngine

class TestTranslationEngine:
    """Test the core translation functionality"""
    
    @pytest_asyncio.fixture
    async def engine(self):
        """Create and initialize translation engine"""
        engine = TranslationEngine()
        await engine.initialize()
        return engine
    
    @pytest.mark.asyncio
    async def test_english_to_spanish_basic(self, engine):
        """Test basic English to Spanish translation"""
        result = await engine.translate(
            text="Hello, how are you?",
            target_language="es",
            source_language="en"
        )
        
        assert result is not None
        assert "translated_text" in result
        assert result["source_language"] == "en"
        assert result["target_language"] == "es"
        assert result["engine"] == "local"
        
    @pytest.mark.asyncio
    async def test_meditation_terms_english_to_hindi(self, engine):
        """Test meditation terms from English to Hindi"""
        result = await engine.translate(
            text="meditation and mindfulness",
            target_language="hi",
            source_language="en",
            domain="meditation"
        )
        
        assert result is not None
        assert "translated_text" in result
        assert result["target_language"] == "hi"
        # Should contain Hindi characters
        assert any('\u0900' <= char <= '\u097f' for char in result["translated_text"])
        
    @pytest.mark.asyncio
    async def test_english_to_chinese_meditation(self, engine):
        """Test English to Chinese meditation content"""
        result = await engine.translate(
            text="inner peace and wisdom",
            target_language="zh",
            source_language="en",
            domain="meditation"
        )
        
        assert result is not None
        assert "translated_text" in result
        assert result["target_language"] == "zh"
        # Should contain Chinese characters
        assert any('\u4e00' <= char <= '\u9fff' for char in result["translated_text"])
        
    @pytest.mark.asyncio
    async def test_auto_language_detection(self, engine):
        """Test automatic language detection"""
        # Test English detection
        result = await engine.translate(
            text="This is English text",
            target_language="es"
        )
        
        assert result["source_language"] == "en"
        
    @pytest.mark.asyncio
    async def test_language_detection_direct(self, engine):
        """Test direct language detection"""
        # English text
        result = await engine.detect_language("Hello world")
        assert result["language"] == "en"
        assert result["confidence"] > 0.5
        
        # Spanish text
        result = await engine.detect_language("Hola mundo")
        assert result["language"] == "es"
        
    @pytest.mark.asyncio
    async def test_batch_translation(self, engine):
        """Test batch translation"""
        texts = [
            "Hello",
            "Goodbye", 
            "Thank you"
        ]
        
        results = await engine.translate_batch(
            texts=texts,
            target_language="es",
            source_language="en"
        )
        
        assert len(results) == 3
        for result in results:
            assert "translated_text" in result
            assert result["target_language"] == "es"
            
    @pytest.mark.asyncio
    async def test_cultural_adaptation(self, engine):
        """Test cultural adaptation for meditation terms"""
        result = await engine.translate(
            text="chakra and mantra",
            target_language="es",
            source_language="en",
            domain="meditation",
            cultural_adaptation=True
        )
        
        assert result is not None
        assert "translated_text" in result
        # Should have cultural notes if adaptation was applied
        if "cultural_notes" in result:
            assert isinstance(result["cultural_notes"], list)
            
    @pytest.mark.asyncio
    async def test_supported_languages(self, engine):
        """Test getting supported languages"""
        languages = await engine.get_supported_languages()
        
        assert isinstance(languages, list)
        assert len(languages) > 0
        assert "en" in languages
        assert "es" in languages
        assert "hi" in languages
        assert "zh" in languages
        
    @pytest.mark.asyncio
    async def test_health_check(self, engine):
        """Test health check endpoint"""
        health = await engine.health_check()
        
        assert health["status"] == "healthy"
        assert health["engine"] == "local"
        assert "supported_languages" in health
        assert "features" in health
        
    @pytest.mark.asyncio
    async def test_empty_text(self, engine):
        """Test handling of empty text"""
        result = await engine.translate(
            text="",
            target_language="es",
            source_language="en"
        )
        
        assert result is not None
        # Should handle empty text gracefully
        
    @pytest.mark.asyncio
    async def test_same_language_translation(self, engine):
        """Test translation when source and target are the same"""
        result = await engine.translate(
            text="Hello world",
            target_language="en",
            source_language="en"
        )
        
        assert result is not None
        assert result["translated_text"] == "Hello world"
        assert result["confidence_score"] == 1.0
        
    @pytest.mark.asyncio
    async def test_long_text_translation(self, engine):
        """Test translation of longer text"""
        long_text = """
        Meditation is a practice where an individual uses a technique
        such as mindfulness, or focusing their mind on a particular
        object, thought, or activity to train attention and awareness,
        and achieve a mentally clear and emotionally calm state.
        """
        
        result = await engine.translate(
            text=long_text.strip(),
            target_language="es",
            source_language="en",
            domain="meditation"
        )
        
        assert result is not None
        assert "translated_text" in result
        assert len(result["translated_text"]) > 0
        
    @pytest.mark.asyncio
    async def test_special_characters(self, engine):
        """Test handling of special characters"""
        result = await engine.translate(
            text="Hello! How are you? 😊",
            target_language="es",
            source_language="en"
        )
        
        assert result is not None
        assert "translated_text" in result
        
    @pytest.mark.asyncio
    async def test_multiple_languages_batch(self, engine):
        """Test batch translation with different target languages"""
        # Test individual translations to different languages
        texts = ["peace", "love", "wisdom"]
        targets = ["es", "fr", "de"]
        
        for text, target in zip(texts, targets):
            result = await engine.translate(
                text=text,
                target_language=target,
                source_language="en",
                domain="meditation"
            )
            
            assert result is not None
            assert result["target_language"] == target
