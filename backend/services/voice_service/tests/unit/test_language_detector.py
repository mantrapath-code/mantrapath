"""
Unit tests for LanguageDetector
Tests language detection for Indian languages and code-switching scenarios
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.core.language_detector import LanguageDetector
from tests.fixtures.test_data import INDIAN_LANGUAGE_TEST_DATA, CODE_SWITCHING_TEST_DATA, REGIONAL_DIALECTS

class TestLanguageDetector:
    
    @pytest.fixture
    def detector(self):
        """Create a LanguageDetector instance for testing"""
        return LanguageDetector()
    
    @pytest.mark.asyncio
    async def test_detect_hindi_text(self, detector):
        """Test detection of Hindi text"""
        hindi_text = "नमस्ते, आप कैसे हैं? मैं आज बहुत खुश हूं।"
        
        result = await detector.detect_language(hindi_text)
        
        assert result["primary_language"] == "hi"
        assert result["confidence"] > 0.8
        assert result["script_detected"] == "devanagari"
        assert "North India" in result.get("regions_detected", [])
    
    @pytest.mark.asyncio
    async def test_detect_bengali_text(self, detector):
        """Test detection of Bengali text"""
        bengali_text = "আপনি কেমন আছেন? আমি ভালো আছি।"
        
        result = await detector.detect_language(bengali_text)
        
        assert result["primary_language"] == "bn"
        assert result["confidence"] > 0.8
        assert result["script_detected"] == "bengali"
        assert "East India" in result.get("regions_detected", [])
    
    @pytest.mark.asyncio
    async def test_detect_tamil_text(self, detector):
        """Test detection of Tamil text"""
        tamil_text = "நீங்கள் எப்படி இருக்கிறீர்கள்? நான் நன்றாக இருக்கிறேன்।"
        
        result = await detector.detect_language(tamil_text)
        
        assert result["primary_language"] == "ta"
        assert result["confidence"] > 0.8
        assert result["script_detected"] == "tamil"
        assert "South India" in result.get("regions_detected", [])
    
    @pytest.mark.asyncio
    async def test_detect_all_indian_languages(self, detector):
        """Test detection for all supported Indian languages"""
        for lang_name, lang_data in INDIAN_LANGUAGE_TEST_DATA.items():
            result = await detector.detect_language(lang_data["text"])
            
            assert result["primary_language"] == lang_data["language_code"]
            assert result["confidence"] > 0.7  # Allow some variation
            assert lang_data["region"] in result.get("regions_detected", [])
    
    @pytest.mark.asyncio
    async def test_detect_code_switching_hindi_english(self, detector):
        """Test detection of code-switching between Hindi and English"""
        for example in CODE_SWITCHING_TEST_DATA:
            result = await detector.detect_language(example["text"])
            
            assert result["is_mixed"] is True
            assert result["primary_language"] in example["languages"]
            
            # Check if code switching analysis is provided
            if "code_switching" in result:
                assert "switch_points" in result["code_switching"]
                assert "language_segments" in result["code_switching"]
    
    @pytest.mark.asyncio
    async def test_detect_english_text(self, detector):
        """Test detection of English text"""
        english_text = "Hello, how are you? I am doing well today."
        
        result = await detector.detect_language(english_text)
        
        assert result["primary_language"] == "en"
        assert result["confidence"] > 0.9
        assert result["script_detected"] == "latin"
        assert result["is_mixed"] is False
    
    @pytest.mark.asyncio
    async def test_detect_mixed_scripts(self, detector):
        """Test detection of text with mixed scripts"""
        mixed_text = "Hello नमस्ते 123 @#$"
        
        result = await detector.detect_language(mixed_text)
        
        assert result["is_mixed"] is True
        assert len(result["language_scores"]) > 1
        assert "en" in result["language_scores"]
        assert "hi" in result["language_scores"]
    
    @pytest.mark.asyncio
    async def test_detect_regional_dialects(self, detector):
        """Test detection of regional dialects"""
        for language, dialects in REGIONAL_DIALECTS.items():
            for dialect_name, dialect_text in dialects.items():
                result = await detector.detect_language(dialect_text, detailed=True)
                
                # Should detect the base language
                if language == "hindi":
                    assert result["primary_language"] == "hi"
                elif language == "tamil":
                    assert result["primary_language"] == "ta"
                
                # Should provide dialect information if detailed=True
                if "dialect_info" in result:
                    assert dialect_name in str(result["dialect_info"]).lower()
    
    @pytest.mark.asyncio
    async def test_detect_urdu_vs_hindi(self, detector):
        """Test distinguishing between Urdu and Hindi"""
        hindi_text = "नमस्ते, आप कैसे हैं?"
        urdu_text = "آپ کیسے ہیں؟"
        
        hindi_result = await detector.detect_language(hindi_text)
        urdu_result = await detector.detect_language(urdu_text)
        
        assert hindi_result["primary_language"] == "hi"
        assert urdu_result["primary_language"] == "ur"
        assert hindi_result["script_detected"] == "devanagari"
        assert urdu_result["script_detected"] == "arabic"
    
    @pytest.mark.asyncio
    async def test_confidence_scoring(self, detector):
        """Test confidence scoring for different text lengths and clarity"""
        test_cases = [
            {"text": "नमस्ते", "expected_confidence": 0.7},  # Short text, lower confidence
            {"text": "नमस्ते, आप कैसे हैं? मैं आज बहुत खुश हूं।", "expected_confidence": 0.9},  # Long text, high confidence
            {"text": "hi नमस्ते bye", "expected_confidence": 0.6},  # Mixed, lower confidence
        ]
        
        for case in test_cases:
            result = await detector.detect_language(case["text"])
            assert result["confidence"] >= case["expected_confidence"]
    
    @pytest.mark.asyncio
    async def test_language_suggestions(self, detector):
        """Test language suggestions for ambiguous text"""
        ambiguous_text = "123 @#$ !@#"  # Numbers and symbols only
        
        result = await detector.detect_language(ambiguous_text, detailed=True)
        
        if "suggestions" in result:
            assert len(result["suggestions"]) > 0
            assert all(isinstance(suggestion, str) for suggestion in result["suggestions"])
    
    @pytest.mark.asyncio
    async def test_geographic_regions(self, detector):
        """Test geographic region detection"""
        region_tests = [
            {"text": "नमस्ते", "expected_regions": ["North India"]},
            {"text": "আপনি কেমন আছেন?", "expected_regions": ["East India"]},
            {"text": "நீங்கள் எப்படி இருக்கிறீர்கள்?", "expected_regions": ["South India"]},
            {"text": "તમે કેમ છો?", "expected_regions": ["West India"]},
        ]
        
        for test in region_tests:
            result = await detector.detect_language(test["text"], detailed=True)
            
            if "regions_detected" in result:
                assert any(region in result["regions_detected"] for region in test["expected_regions"])
    
    @pytest.mark.asyncio
    async def test_error_handling_empty_text(self, detector):
        """Test error handling for empty text"""
        result = await detector.detect_language("")
        
        assert "error" in result or result["primary_language"] == "unknown"
    
    @pytest.mark.asyncio
    async def test_error_handling_only_numbers(self, detector):
        """Test handling of text with only numbers"""
        result = await detector.detect_language("12345")
        
        assert result["primary_language"] in ["unknown", "numeric"]
        assert result["confidence"] < 0.5
    
    @pytest.mark.asyncio
    async def test_batch_detection(self, detector):
        """Test batch language detection"""
        texts = [
            "नमस्ते",
            "Hello",
            "আপনি কেমন আছেন?",
            "நீங்கள் எப்படி இருக்கிறீர்கள்?"
        ]
        
        if hasattr(detector, 'detect_batch'):
            results = await detector.detect_batch(texts)
            
            assert len(results) == len(texts)
            assert results[0]["primary_language"] == "hi"
            assert results[1]["primary_language"] == "en"
            assert results[2]["primary_language"] == "bn"
            assert results[3]["primary_language"] == "ta"
    
    @pytest.mark.asyncio
    async def test_performance_large_text(self, detector):
        """Test performance with large text"""
        large_text = "नमस्ते, आप कैसे हैं? " * 1000  # Repeat 1000 times
        
        import time
        start_time = time.time()
        result = await detector.detect_language(large_text)
        end_time = time.time()
        
        processing_time = end_time - start_time
        assert processing_time < 5.0  # Should complete within 5 seconds
        assert result["primary_language"] == "hi"
        assert result["confidence"] > 0.9
    
    @pytest.mark.asyncio
    async def test_caching_mechanism(self, detector):
        """Test caching of detection results"""
        text = "नमस्ते, आप कैसे हैं?"
        
        # First call
        import time
        start_time = time.time()
        result1 = await detector.detect_language(text)
        first_call_time = time.time() - start_time
        
        # Second call (should be faster if cached)
        start_time = time.time()
        result2 = await detector.detect_language(text)
        second_call_time = time.time() - start_time
        
        # Results should be identical
        assert result1["primary_language"] == result2["primary_language"]
        assert result1["confidence"] == result2["confidence"]
        
        # Second call should be faster (if caching is implemented)
        if hasattr(detector, '_cache'):
            assert second_call_time < first_call_time
    
    @pytest.mark.asyncio
    async def test_special_characters_handling(self, detector):
        """Test handling of special characters and emojis"""
        special_texts = [
            "नमस्ते 😊",
            "Hello! 👋",
            "आप कैसे हैं? 🤔",
            "नमस्ते... क्या हाल है???",
        ]
        
        for text in special_texts:
            result = await detector.detect_language(text)
            
            # Should still detect language despite special characters
            assert result["primary_language"] in ["hi", "en"]
            assert result["confidence"] > 0.6
    
    @pytest.mark.asyncio
    async def test_transliterated_text(self, detector):
        """Test detection of transliterated Indian language text"""
        transliterated_texts = [
            "namaste aap kaise hain",  # Hindi in Latin script
            "aap kya kar rahe hain",
            "main theek hun dhanyawad"
        ]
        
        for text in transliterated_texts:
            result = await detector.detect_language(text, detailed=True)
            
            # Might detect as English but should have transliteration hints
            if "transliteration_detected" in result:
                assert result["transliteration_detected"] is True
                assert "source_language_hint" in result
