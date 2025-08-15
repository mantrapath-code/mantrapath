"""
Language Detection Service Tests
Tests for automatic language identification
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

# Mock imports for testing
class MockLanguageDetector:
    """Mock language detection for testing"""
    
    def __init__(self):
        self.is_initialized = False
    
    async def initialize(self):
        self.is_initialized = True
        return True
    
    async def detect_language(self, text: str):
        """Simple mock language detection"""
        # Basic heuristics for testing
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            return "zh", 0.95
        elif any('\u0900' <= char <= '\u097f' for char in text):
            return "hi", 0.90
        elif any('\u0600' <= char <= '\u06ff' for char in text):
            return "ar", 0.88
        elif "hola" in text.lower():
            return "es", 0.92
        elif "bonjour" in text.lower():
            return "fr", 0.90
        else:
            return "en", 0.85

class TestLanguageDetection:
    """Test language detection functionality"""
    
    @pytest.fixture
    async def detector(self):
        """Create language detector for testing"""
        detector = MockLanguageDetector()
        await detector.initialize()
        return detector
    
    @pytest.mark.asyncio
    async def test_english_detection(self, detector):
        """Test English language detection"""
        language, confidence = await detector.detect_language("Hello world, how are you today?")
        
        assert language == "en"
        assert confidence > 0.8
    
    @pytest.mark.asyncio
    async def test_spanish_detection(self, detector):
        """Test Spanish language detection"""
        language, confidence = await detector.detect_language("Hola mundo, cómo estás hoy?")
        
        assert language == "es"
        assert confidence > 0.8
    
    @pytest.mark.asyncio
    async def test_chinese_detection(self, detector):
        """Test Chinese language detection"""
        language, confidence = await detector.detect_language("你好世界")
        
        assert language == "zh"
        assert confidence > 0.9
    
    @pytest.mark.asyncio
    async def test_hindi_detection(self, detector):
        """Test Hindi language detection"""
        language, confidence = await detector.detect_language("नमस्ते दुनिया")
        
        assert language == "hi"
        assert confidence > 0.8
    
    @pytest.mark.asyncio
    async def test_arabic_detection(self, detector):
        """Test Arabic language detection"""
        language, confidence = await detector.detect_language("مرحبا بالعالم")
        
        assert language == "ar"
        assert confidence > 0.8
    
    @pytest.mark.asyncio
    async def test_short_text_detection(self, detector):
        """Test detection with very short text"""
        language, confidence = await detector.detect_language("Hi")
        
        assert language in ["en"]
        assert confidence > 0.5  # Lower confidence expected for short text
    
    @pytest.mark.asyncio
    async def test_mixed_language_text(self, detector):
        """Test detection with mixed language content"""
        # English with some Spanish
        language, confidence = await detector.detect_language("Hello world, pero no hablo español")
        
        # Should detect primary language
        assert language in ["en", "es"]
        assert confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_empty_text_handling(self, detector):
        """Test handling of empty or whitespace text"""
        language, confidence = await detector.detect_language("")
        
        # Should have some fallback behavior
        assert language is not None
        assert 0.0 <= confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_numbers_and_symbols(self, detector):
        """Test detection with numbers and symbols"""
        language, confidence = await detector.detect_language("123 !@# $%^")
        
        # Should fallback to default language
        assert language is not None
        assert confidence >= 0.0

class TestLanguageDetectionAccuracy:
    """Test detection accuracy for various scenarios"""
    
    @pytest.fixture
    def test_samples(self):
        """Test samples for accuracy testing"""
        return {
            "en": [
                "The quick brown fox jumps over the lazy dog",
                "Machine learning is transforming technology",
                "Please join us for meditation and mindfulness practice"
            ],
            "es": [
                "El zorro marrón rápido salta sobre el perro perezoso",
                "La meditación ayuda a encontrar paz interior",
                "Por favor únete a nosotros para la práctica de mindfulness"
            ],
            "fr": [
                "Le renard brun rapide saute par-dessus le chien paresseux",
                "La méditation aide à trouver la paix intérieure",
                "Veuillez vous joindre à nous pour la pratique de la pleine conscience"
            ],
            "hi": [
                "ध्यान और शांति का अभ्यास करें",
                "मन की शांति के लिए योग करें",
                "सभी जीवों के कल्याण की कामना करें"
            ],
            "zh": [
                "冥想有助于找到内心的平静",
                "请加入我们的正念练习",
                "所有生命的福祉都很重要"
            ]
        }
    
    @pytest.mark.asyncio
    async def test_detection_accuracy(self, test_samples):
        """Test overall detection accuracy"""
        detector = MockLanguageDetector()
        await detector.initialize()
        
        correct_detections = 0
        total_samples = 0
        
        for expected_lang, samples in test_samples.items():
            for sample in samples:
                detected_lang, confidence = await detector.detect_language(sample)
                
                if detected_lang == expected_lang:
                    correct_detections += 1
                
                total_samples += 1
                
                # All detections should have reasonable confidence
                assert confidence > 0.5
        
        # Calculate accuracy
        accuracy = correct_detections / total_samples
        
        # Should achieve reasonable accuracy (adjust threshold as needed)
        assert accuracy > 0.6  # 60% accuracy minimum for mock detector
        
        print(f"Detection accuracy: {accuracy:.2%}")

class TestLanguageDetectionPerformance:
    """Test detection performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_detection_speed(self):
        """Test language detection speed"""
        import time
        
        detector = MockLanguageDetector()
        await detector.initialize()
        
        test_texts = [
            "Short text",
            "Medium length text for testing detection speed",
            "Much longer text that contains multiple sentences and should still be processed quickly by the language detection system"
        ]
        
        for text in test_texts:
            start_time = time.time()
            language, confidence = await detector.detect_language(text)
            detection_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Detection should be very fast
            assert detection_time < 100  # Under 100ms
            assert language is not None
            assert 0.0 <= confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_batch_detection_efficiency(self):
        """Test efficient batch language detection"""
        detector = MockLanguageDetector()
        await detector.initialize()
        
        texts = [
            "Hello world",
            "Hola mundo",
            "Bonjour le monde",
            "你好世界",
            "नमस्ते दुनिया"
        ] * 10  # 50 texts total
        
        start_time = time.time()
        
        # Simulate batch detection
        results = []
        for text in texts:
            result = await detector.detect_language(text)
            results.append(result)
        
        total_time = time.time() - start_time
        
        assert len(results) == len(texts)
        assert total_time < 5.0  # Should complete in under 5 seconds
        
        # All results should be valid
        for language, confidence in results:
            assert language is not None
            assert 0.0 <= confidence <= 1.0

class TestLanguageDetectionEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.mark.asyncio
    async def test_very_long_text(self):
        """Test detection with very long text"""
        detector = MockLanguageDetector()
        await detector.initialize()
        
        # Create very long text
        long_text = "This is a test sentence. " * 1000  # ~25,000 characters
        
        language, confidence = await detector.detect_language(long_text)
        
        assert language == "en"
        assert confidence > 0.8
    
    @pytest.mark.asyncio
    async def test_special_characters(self):
        """Test with special characters and emojis"""
        detector = MockLanguageDetector()
        await detector.initialize()
        
        texts_with_special_chars = [
            "Hello 😊 world! 🌍",
            "Testing... @#$%^&*()_+ detection",
            "Mixed content: English + 中文 + العربية"
        ]
        
        for text in texts_with_special_chars:
            language, confidence = await detector.detect_language(text)
            
            assert language is not None
            assert 0.0 <= confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_code_and_markup(self):
        """Test detection with code and markup content"""
        detector = MockLanguageDetector()
        await detector.initialize()
        
        code_samples = [
            "def hello_world(): print('Hello, World!')",
            "<html><body>Hello World</body></html>",
            "SELECT * FROM users WHERE name = 'John'"
        ]
        
        for code in code_samples:
            language, confidence = await detector.detect_language(code)
            
            # Should still attempt detection
            assert language is not None
            assert 0.0 <= confidence <= 1.0

class TestLanguageDetectionIntegration:
    """Integration tests for language detection"""
    
    @pytest.mark.asyncio
    async def test_detection_with_translation_pipeline(self):
        """Test language detection as part of translation workflow"""
        detector = MockLanguageDetector()
        await detector.initialize()
        
        # Simulate translation pipeline with auto-detection
        source_text = "Hola, cómo estás?"
        
        # Step 1: Detect language
        detected_lang, confidence = await detector.detect_language(source_text)
        
        # Step 2: Verify detection is reasonable for translation
        assert detected_lang in ["es", "en"]  # Should detect Spanish
        assert confidence > 0.7  # High enough confidence for translation
        
        # Step 3: Use detection result for translation decision
        if confidence > 0.8:
            translation_ready = True
        else:
            translation_ready = False
        
        # Should be ready for translation with good detection
        assert translation_ready or confidence > 0.5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
