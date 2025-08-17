import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import time

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.emotion_analyzer import EmotionAnalyzer
from models.ai_models import AIMetrics

class TestEmotionAnalyzer:
    """Test suite for Emotion Analyzer"""
    
    @pytest.fixture
    def emotion_analyzer(self):
        """Create emotion analyzer instance for testing"""
        analyzer = EmotionAnalyzer()
        
        # Mock the model loading to avoid downloading models during tests
        analyzer.models = {
            'en_emotion': Mock(),
            'sentiment': Mock(),
            'multilingual': Mock()
        }
        analyzer.is_initialized = True
        
        return analyzer
    
    @pytest.mark.asyncio
    async def test_start_initialization(self):
        """Test emotion analyzer initialization"""
        analyzer = EmotionAnalyzer()
        
        with patch.object(analyzer, '_load_primary_models') as mock_primary, \
             patch.object(analyzer, '_load_multilingual_models') as mock_multilingual:
            
            await analyzer.start()
            
            assert analyzer.is_initialized
            mock_primary.assert_called_once()
            mock_multilingual.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_english_text(self, emotion_analyzer):
        """Test emotion analysis for English text"""
        text = "I'm feeling really happy and excited today!"
        
        # Mock model response
        emotion_analyzer.models['en_emotion'].return_value = [
            {'label': 'joy', 'score': 0.85},
            {'label': 'excitement', 'score': 0.12}
        ]
        
        with patch.object(emotion_analyzer, '_detect_language') as mock_detect:
            mock_detect.return_value = 'en'
            
            result = await emotion_analyzer.analyze(
                text=text,
                language='en',
                user_id='test_user_123'
            )
        
        assert result['emotion'] == 'joy'
        assert result['confidence'] == 0.85
        assert result['language'] == 'en'
        assert result['processing_time_ms'] > 0
        assert 'emotions' in result
    
    @pytest.mark.asyncio
    async def test_analyze_multilingual_text(self, emotion_analyzer):
        """Test emotion analysis for non-English text"""
        text = "मैं बहुत खुश हूं"  # Hindi: "I am very happy"
        
        # Mock model response
        emotion_analyzer.models['multilingual'].return_value = [
            {'label': 'joy', 'score': 0.78},
            {'label': 'neutral', 'score': 0.22}
        ]
        
        with patch.object(emotion_analyzer, '_detect_language') as mock_detect:
            mock_detect.return_value = 'hi'
            
            result = await emotion_analyzer.analyze(
                text=text,
                language='hi',
                user_id='test_user_123'
            )
        
        assert result['emotion'] == 'joy'
        assert result['language'] == 'hi'
        assert result['cultural_adaptation'] is not None
    
    @pytest.mark.asyncio
    async def test_cultural_adaptation(self, emotion_analyzer):
        """Test cultural adaptation of emotion analysis"""
        text = "I'm feeling angry about this situation"
        
        emotion_analyzer.models['multilingual'].return_value = [
            {'label': 'anger', 'score': 0.9}
        ]
        
        with patch.object(emotion_analyzer, '_detect_language') as mock_detect:
            mock_detect.return_value = 'hi'  # Hindi context
            
            result = await emotion_analyzer.analyze(
                text=text,
                language='hi',
                user_id='test_user_123'
            )
        
        # Should have cultural interpretation for Hindi context
        assert result['cultural_context'] is not None
        assert result['cultural_adaptation']['adapted_culture'] == 'hi'
        # Confidence should be slightly reduced for cross-cultural analysis
        assert result['confidence'] < 0.9
    
    @pytest.mark.asyncio
    async def test_language_detection(self, emotion_analyzer):
        """Test automatic language detection"""
        text = "Bonjour, je suis très heureux!"  # French
        
        with patch('core.emotion_analyzer.detect') as mock_detect:
            mock_detect.return_value = 'fr'
            
            detected_lang = await emotion_analyzer._detect_language(text, None)
            assert detected_lang == 'fr'
    
    @pytest.mark.asyncio
    async def test_language_detection_fallback(self, emotion_analyzer):
        """Test language detection fallback to English"""
        text = "Some text in unsupported language"
        
        with patch('core.emotion_analyzer.detect') as mock_detect:
            mock_detect.return_value = 'unknown_lang'
            
            detected_lang = await emotion_analyzer._detect_language(text, None)
            assert detected_lang == 'en'  # Should fallback to English
    
    @pytest.mark.asyncio
    async def test_empty_text_handling(self, emotion_analyzer):
        """Test handling of empty or whitespace text"""
        result = await emotion_analyzer.analyze(
            text="   ",
            user_id='test_user_123'
        )
        
        assert result['emotion'] == 'neutral'
        assert result['confidence'] == 1.0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, emotion_analyzer):
        """Test error handling when model fails"""
        text = "This should cause an error"
        
        # Make model raise an exception
        emotion_analyzer.models['en_emotion'].side_effect = Exception("Model error")
        
        with patch.object(emotion_analyzer, '_detect_language') as mock_detect:
            mock_detect.return_value = 'en'
            
            result = await emotion_analyzer.analyze(
                text=text,
                user_id='test_user_123'
            )
        
        # Should return error result without crashing
        assert result['emotion'] == 'neutral'
        assert result['confidence'] == 0.0
    
    @pytest.mark.asyncio
    async def test_fallback_emotion_analysis(self, emotion_analyzer):
        """Test fallback emotion analysis using keywords"""
        positive_text = "I am so happy and wonderful today"
        negative_text = "I feel terrible and sad"
        neutral_text = "The weather is okay"
        
        # Test positive
        result = emotion_analyzer._create_fallback_emotion_result(positive_text)
        assert result['primary_emotion'] == 'joy'
        
        # Test negative
        result = emotion_analyzer._create_fallback_emotion_result(negative_text)
        assert result['primary_emotion'] == 'sadness'
        
        # Test neutral
        result = emotion_analyzer._create_fallback_emotion_result(neutral_text)
        assert result['primary_emotion'] == 'neutral'
    
    @pytest.mark.asyncio
    async def test_emotion_label_normalization(self, emotion_analyzer):
        """Test emotion label normalization"""
        assert emotion_analyzer._normalize_emotion_label('happy') == 'joy'
        assert emotion_analyzer._normalize_emotion_label('angry') == 'anger'
        assert emotion_analyzer._normalize_emotion_label('scared') == 'fear'
        assert emotion_analyzer._normalize_emotion_label('unknown_emotion') == 'neutral'
    
    @pytest.mark.asyncio
    async def test_batch_analysis(self, emotion_analyzer):
        """Test batch emotion analysis"""
        texts = [
            "I'm very happy today",
            "Feeling sad and down",
            "Just a normal day"
        ]
        
        # Mock individual analysis calls
        emotion_analyzer.models['en_emotion'].return_value = [
            {'label': 'joy', 'score': 0.8}
        ]
        
        with patch.object(emotion_analyzer, 'analyze') as mock_analyze:
            mock_analyze.side_effect = [
                {'emotion': 'joy', 'confidence': 0.8},
                {'emotion': 'sadness', 'confidence': 0.75},
                {'emotion': 'neutral', 'confidence': 0.9}
            ]
            
            results = await emotion_analyzer.analyze_batch(
                texts=texts,
                language='en',
                user_id='test_user_123'
            )
        
        assert len(results) == 3
        assert results[0]['emotion'] == 'joy'
        assert results[1]['emotion'] == 'sadness'
        assert results[2]['emotion'] == 'neutral'
    
    @pytest.mark.asyncio
    async def test_batch_analysis_with_errors(self, emotion_analyzer):
        """Test batch analysis with some failures"""
        texts = ["Good text", "Bad text", "Normal text"]
        
        with patch.object(emotion_analyzer, 'analyze') as mock_analyze:
            # Second analysis fails
            mock_analyze.side_effect = [
                {'emotion': 'joy', 'confidence': 0.8},
                Exception("Analysis failed"),
                {'emotion': 'neutral', 'confidence': 0.9}
            ]
            
            results = await emotion_analyzer.analyze_batch(
                texts=texts,
                user_id='test_user_123'
            )
        
        assert len(results) == 3
        assert results[0]['emotion'] == 'joy'
        assert results[1]['confidence'] == 0.0  # Error result
        assert results[2]['emotion'] == 'neutral'
    
    @pytest.mark.asyncio
    async def test_performance_latency(self, emotion_analyzer):
        """Test emotion analysis latency requirements"""
        text = "I'm feeling good today"
        
        emotion_analyzer.models['en_emotion'].return_value = [
            {'label': 'joy', 'score': 0.8}
        ]
        
        start_time = time.time()
        
        with patch.object(emotion_analyzer, '_detect_language') as mock_detect:
            mock_detect.return_value = 'en'
            
            result = await emotion_analyzer.analyze(
                text=text,
                user_id='test_user_123'
            )
        
        processing_time = time.time() - start_time
        
        # Should meet latency requirement of <200ms
        assert processing_time < 0.2, f"Processing took {processing_time}s, should be <200ms"
        assert result['processing_time_ms'] < 200
    
    @pytest.mark.asyncio
    async def test_metrics_tracking(self, emotion_analyzer):
        """Test metrics tracking"""
        initial_count = emotion_analyzer.metrics.emotion_analysis_count
        
        # Simulate processing
        emotion_analyzer._update_metrics(150.0)  # 150ms processing time
        
        assert emotion_analyzer.metrics.emotion_analysis_count == initial_count + 1
        assert len(emotion_analyzer.processing_times) == 1
        assert emotion_analyzer.processing_times[0] == 150.0
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, emotion_analyzer):
        """Test metrics collection"""
        # Add some processing times
        for i in range(5):
            emotion_analyzer._update_metrics(100 + i * 10)
        
        metrics = await emotion_analyzer.get_metrics()
        
        assert metrics['total_analyses'] == 5
        assert metrics['average_processing_time_ms'] == 120.0  # (100+110+120+130+140)/5
        assert metrics['supported_languages'] == len(emotion_analyzer.supported_languages)
        assert metrics['is_initialized'] == True
    
    @pytest.mark.asyncio
    async def test_health_check(self, emotion_analyzer):
        """Test health check functionality"""
        assert emotion_analyzer.health_check() == True
        
        emotion_analyzer.is_initialized = False
        assert emotion_analyzer.health_check() == False
        
        emotion_analyzer.is_initialized = True
        emotion_analyzer.models.clear()
        assert emotion_analyzer.health_check() == False
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis(self, emotion_analyzer):
        """Test concurrent emotion analysis"""
        texts = [f"Text {i} with emotion" for i in range(10)]
        
        emotion_analyzer.models['en_emotion'].return_value = [
            {'label': 'neutral', 'score': 0.8}
        ]
        
        with patch.object(emotion_analyzer, '_detect_language') as mock_detect:
            mock_detect.return_value = 'en'
            
            # Process concurrently
            tasks = [
                emotion_analyzer.analyze(text, user_id=f'user_{i}') 
                for i, text in enumerate(texts)
            ]
            
            results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        for result in results:
            assert 'emotion' in result
            assert 'confidence' in result
    
    @pytest.mark.asyncio
    async def test_cultural_interpretation_patterns(self, emotion_analyzer):
        """Test cultural interpretation patterns"""
        # Test Indian cultural context
        result = await emotion_analyzer._apply_cultural_adaptation(
            {'primary_emotion': 'anger', 'confidence': 0.8, 'emotion_scores': {}},
            'hi',
            None
        )
        assert 'cultural_interpretation' in result
        assert 'family' in result['cultural_interpretation'] or 'circumstances' in result['cultural_interpretation']
        
        # Test Arabic cultural context
        result = await emotion_analyzer._apply_cultural_adaptation(
            {'primary_emotion': 'joy', 'confidence': 0.8, 'emotion_scores': {}},
            'ar',
            None
        )
        assert 'cultural_interpretation' in result
        assert 'spiritual' in result['cultural_interpretation'] or 'community' in result['cultural_interpretation']
    
    @pytest.mark.asyncio
    async def test_stop_cleanup(self, emotion_analyzer):
        """Test proper cleanup on stop"""
        with patch('torch.cuda.is_available') as mock_cuda, \
             patch('torch.cuda.empty_cache') as mock_empty_cache:
            
            mock_cuda.return_value = True
            
            await emotion_analyzer.stop()
            
            assert not emotion_analyzer.is_initialized
            assert len(emotion_analyzer.models) == 0
            mock_empty_cache.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])
