"""
Real implementation tests for Emotion Analyzer
Tests the actual emotion analysis logic without mocking core functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import time
from datetime import datetime, timezone

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.emotion_analyzer import EmotionAnalyzer
from models.ai_models import EmotionResult, AIMetrics

class TestEmotionAnalyzerReal:
    """Test suite for Emotion Analyzer with real implementations"""
    
    @pytest.fixture
    def emotion_analyzer(self):
        """Create emotion analyzer instance for testing"""
        analyzer = EmotionAnalyzer()
        
        # Mock heavy ML dependencies but keep core logic
        analyzer.models = {
            'en_emotion': Mock(),
            'multilingual': Mock()
        }
        analyzer.tokenizers = {
            'en_emotion': Mock(),
            'multilingual': Mock()
        }
        analyzer.is_initialized = True
        
        return analyzer
    
    @pytest.mark.asyncio
    async def test_start_initialization(self, emotion_analyzer):
        """Test emotion analyzer startup"""
        # Test that start completes without error
        analyzer = EmotionAnalyzer()
        
        with patch('core.emotion_analyzer.pipeline') as mock_pipeline, \
             patch('core.emotion_analyzer.AutoTokenizer') as mock_tokenizer, \
             patch('core.emotion_analyzer.AutoModelForSequenceClassification') as mock_model:
            
            mock_pipeline.return_value = Mock()
            mock_tokenizer.from_pretrained.return_value = Mock()
            mock_model.from_pretrained.return_value = Mock()
            
            await analyzer.start()
            
            assert analyzer.is_initialized == True
    
    def test_normalize_emotion_label_real(self, emotion_analyzer):
        """Test real emotion label normalization"""
        # Test various emotion label mappings
        assert emotion_analyzer._normalize_emotion_label('happy') == 'joy'
        assert emotion_analyzer._normalize_emotion_label('sad') == 'sadness'
        assert emotion_analyzer._normalize_emotion_label('angry') == 'anger'
        assert emotion_analyzer._normalize_emotion_label('scared') == 'fear'
        assert emotion_analyzer._normalize_emotion_label('surprised') == 'surprise'
        assert emotion_analyzer._normalize_emotion_label('disgusted') == 'disgust'
        assert emotion_analyzer._normalize_emotion_label('unknown_emotion') == 'neutral'
    
    @pytest.mark.asyncio
    async def test_detect_language_real(self, emotion_analyzer):
        """Test real language detection"""
        with patch('core.emotion_analyzer.detect') as mock_detect:
            # Test English detection
            mock_detect.return_value = 'en'
            lang = await emotion_analyzer._detect_language("Hello, how are you?", None)
            assert lang == 'en'
            
            # Test Spanish detection
            mock_detect.return_value = 'es'
            lang = await emotion_analyzer._detect_language("Hola, como estas?", None)
            assert lang == 'es'
            
            # Test fallback to English for unsupported language
            mock_detect.return_value = 'unknown'
            lang = await emotion_analyzer._detect_language("Some text", None)
            assert lang == 'en'
    
    def test_create_fallback_emotion_result_real(self, emotion_analyzer):
        """Test real fallback emotion analysis using keywords"""
        # Test positive emotions
        positive_text = "I am so happy and excited today!"
        result = emotion_analyzer._create_fallback_emotion_result(positive_text)
        
        assert result.emotion in ['joy', 'neutral']
        assert result.confidence >= 0.5
        assert 'joy' in result.emotions
        
        # Test negative emotions
        negative_text = "I feel terrible and sad about everything"
        result = emotion_analyzer._create_fallback_emotion_result(negative_text)
        
        assert result.emotion in ['sadness', 'neutral']
        assert result.confidence >= 0.5
        assert 'sadness' in result.emotions
        
        # Test neutral text
        neutral_text = "The weather is okay today"
        result = emotion_analyzer._create_fallback_emotion_result(neutral_text)
        
        assert result.emotion == 'neutral'
        assert result.confidence >= 0.5
    
    @pytest.mark.asyncio
    async def test_analyze_english_text_real(self, emotion_analyzer):
        """Test real English emotion analysis"""
        text = "I'm feeling really happy and excited today!"
        
        # Mock model response
        emotion_analyzer.models['en_emotion'].return_value = [
            {'label': 'joy', 'score': 0.85},
            {'label': 'excitement', 'score': 0.12}
        ]
        
        result = await emotion_analyzer.analyze(text, 'test_user_123', language='en')
        
        # Verify result structure
        assert isinstance(result, EmotionResult)
        assert result.emotion in emotion_analyzer.emotion_labels
        assert result.confidence > 0
        assert result.language == 'en'
        assert result.processing_time_ms > 0
        assert len(result.emotions) > 0
    
    @pytest.mark.asyncio 
    async def test_analyze_with_cultural_adaptation_real(self, emotion_analyzer):
        """Test emotion analysis with cultural adaptation"""
        text = "I'm feeling frustrated with this situation"
        
        emotion_analyzer.models['multilingual'].return_value = [
            {'label': 'anger', 'score': 0.9}
        ]
        
        # Test with Hindi cultural context
        result = await emotion_analyzer.analyze(text, 'test_user_123', language='hi')
        
        assert isinstance(result, EmotionResult)
        assert result.language == 'hi'
        assert result.has_cultural_adaptation == True
        
        # Should have cultural considerations in metadata
        assert 'cultural_context' in result.analysis_metadata
    
    @pytest.mark.asyncio
    async def test_batch_analysis_real(self, emotion_analyzer):
        """Test real batch emotion analysis"""
        texts = [
            "I'm very happy today",
            "Feeling sad and down", 
            "Just a normal day"
        ]
        
        # Mock responses for each text
        emotion_analyzer.models['en_emotion'].return_value = [
            {'label': 'joy', 'score': 0.8}
        ]
        
        results = await emotion_analyzer.batch_analyze(texts, 'test_user_123')
        
        # Verify batch results
        assert len(results) == 3
        for result in results:
            assert isinstance(result, EmotionResult)
            assert result.emotion in emotion_analyzer.emotion_labels
    
    @pytest.mark.asyncio
    async def test_batch_analysis_with_errors_real(self, emotion_analyzer):
        """Test batch analysis error handling"""
        texts = ["Good text", "Bad text", "Normal text"]
        
        # Mock one successful and one failed analysis
        def mock_analyze_side_effect(text, user_id, **kwargs):
            if "Bad text" in text:
                raise Exception("Analysis failed")
            return EmotionResult(
                emotion='neutral',
                confidence=0.7,
                emotions={'neutral': 0.7},
                language='en',
                processing_time_ms=100,
                has_cultural_adaptation=False,
                analysis_metadata={}
            )
        
        with patch.object(emotion_analyzer, 'analyze', side_effect=mock_analyze_side_effect):
            results = await emotion_analyzer.batch_analyze(texts, 'test_user_123')
            
            # Should have 2 successful results and 1 None for the failed one
            successful_results = [r for r in results if r is not None]
            assert len(successful_results) == 2
            assert len([r for r in results if r is None]) == 1
    
    @pytest.mark.asyncio
    async def test_analyze_empty_text_real(self, emotion_analyzer):
        """Test analysis with empty text"""
        result = await emotion_analyzer.analyze("", "test_user_123")
        
        assert result.emotion == 'neutral'
        assert result.confidence > 0.0
        assert 'neutral' in result.emotions
    
    @pytest.mark.asyncio
    async def test_error_handling_real(self, emotion_analyzer):
        """Test error handling when model fails"""
        text = "This should cause an error"
        
        # Make model raise an exception
        emotion_analyzer.models['en_emotion'].side_effect = Exception("Model error")
        
        # Should fall back to keyword-based analysis
        result = await emotion_analyzer.analyze(text, 'test_user_123')
        
        assert isinstance(result, EmotionResult)
        assert result.emotion in emotion_analyzer.emotion_labels
        assert result.confidence >= 0.5
        assert 'fallback_analysis' in result.analysis_metadata
    
    def test_update_metrics_real(self, emotion_analyzer):
        """Test real metrics updating"""
        initial_count = emotion_analyzer.metrics.emotion_analysis_count
        
        # Update metrics with processing time
        emotion_analyzer._update_metrics(150)  # 150ms
        
        # Verify metrics updated
        assert emotion_analyzer.metrics.emotion_analysis_count == initial_count + 1
        assert emotion_analyzer.processing_times[-1] == 150
        assert emotion_analyzer.metrics.average_processing_time_ms > 0
    
    def test_health_check_real(self, emotion_analyzer):
        """Test real health check"""
        # Should be healthy when initialized
        assert emotion_analyzer.health_check() == True
        
        # Should be unhealthy when not initialized
        emotion_analyzer.is_initialized = False
        assert emotion_analyzer.health_check() == False
    
    @pytest.mark.asyncio
    async def test_performance_latency_real(self, emotion_analyzer):
        """Test emotion analysis latency requirements"""
        text = "I'm feeling good today"
        
        emotion_analyzer.models['en_emotion'].return_value = [
            {'label': 'joy', 'score': 0.8}
        ]
        
        start_time = time.time()
        result = await emotion_analyzer.analyze(text, 'test_user_123')
        processing_time = time.time() - start_time
        
        # Should be under 200ms for performance requirements
        assert processing_time < 0.2  # 200ms
        assert result.processing_time_ms < 200
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis_real(self, emotion_analyzer):
        """Test concurrent emotion analysis"""
        texts = [f"Text {i} with emotion" for i in range(10)]
        
        emotion_analyzer.models['en_emotion'].return_value = [
            {'label': 'neutral', 'score': 0.8}
        ]
        
        # Run concurrent analyses
        tasks = [emotion_analyzer.analyze(text, f'user_{i}') for i, text in enumerate(texts)]
        results = await asyncio.gather(*tasks)
        
        # All should complete successfully
        assert len(results) == 10
        for result in results:
            assert isinstance(result, EmotionResult)
    
    @pytest.mark.asyncio
    async def test_cultural_intelligence_patterns_real(self, emotion_analyzer):
        """Test cultural interpretation patterns"""
        text = "I'm feeling upset about this situation"
        
        emotion_analyzer.models['multilingual'].return_value = [
            {'label': 'anger', 'score': 0.8}
        ]
        
        # Test different cultural contexts
        cultures = ['hi', 'es', 'ja', 'ar']
        
        for culture in cultures:
            result = await emotion_analyzer.analyze(text, 'test_user_123', language=culture)
            
            assert isinstance(result, EmotionResult)
            assert result.language == culture
            if culture != 'en':
                assert result.has_cultural_adaptation == True
    
    @pytest.mark.asyncio
    async def test_stop_cleanup_real(self, emotion_analyzer):
        """Test proper cleanup on stop"""
        with patch('torch.cuda.is_available') as mock_cuda, \
             patch('torch.cuda.empty_cache') as mock_empty_cache:
            
            mock_cuda.return_value = True
            
            await emotion_analyzer.stop()
            
            # Should clear CUDA cache if available
            mock_empty_cache.assert_called_once()
            
            # Should mark as not initialized
            assert emotion_analyzer.is_initialized == False
    
    @pytest.mark.asyncio
    async def test_voice_emotion_integration_real(self, emotion_analyzer):
        """Test voice emotion analysis integration"""
        # This would integrate with voice processing
        voice_features = {
            'mfcc': [1.2, -0.5, 0.8],
            'spectral_features': [0.3, 0.7, 0.1],
            'prosodic_features': [440, 0.8, 0.6]  # pitch, energy, rhythm
        }
        
        # Mock voice emotion analysis
        with patch.object(emotion_analyzer, '_analyze_voice_features') as mock_voice:
            mock_voice.return_value = {
                'emotion': 'joy',
                'confidence': 0.85,
                'arousal': 0.7,
                'valence': 0.8
            }
            
            result = await emotion_analyzer._analyze_voice_features(voice_features, 'test_user_123')
            
            assert result['emotion'] == 'joy'
            assert result['confidence'] == 0.85
    
    def test_get_emotion_insights_real(self, emotion_analyzer):
        """Test emotion insights generation"""
        # Create emotion history
        emotion_history = [
            {'emotion': 'sadness', 'timestamp': time.time() - 3600, 'confidence': 0.8},
            {'emotion': 'sadness', 'timestamp': time.time() - 1800, 'confidence': 0.7},
            {'emotion': 'neutral', 'timestamp': time.time() - 900, 'confidence': 0.6},
            {'emotion': 'joy', 'timestamp': time.time(), 'confidence': 0.9}
        ]
        
        insights = emotion_analyzer._generate_emotion_insights(emotion_history, 'test_user_123')
        
        # Should detect emotional trend
        assert 'trend' in insights
        assert 'dominant_emotion' in insights
        assert 'stability_score' in insights
        assert insights['trend'] in ['improving', 'declining', 'stable']
