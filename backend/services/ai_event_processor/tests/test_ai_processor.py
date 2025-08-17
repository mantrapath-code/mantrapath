import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import json
import time
from datetime import datetime, timezone

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.ai_processor import AIEventProcessor
from models.ai_models import AIMetrics

class TestAIEventProcessor:
    """Test suite for AI Event Processor"""
    
    @pytest.fixture
    async def ai_processor(self):
        """Create AI processor instance for testing"""
        processor = AIEventProcessor()
        
        # Mock dependencies
        processor.event_bus = AsyncMock()
        processor.redis_client = Mock()
        processor.is_running = True
        
        return processor
    
    @pytest.mark.asyncio
    async def test_start(self):
        """Test AI processor startup"""
        processor = AIEventProcessor()
        
        with patch('core.ai_processor.get_enhanced_event_bus') as mock_bus, \
             patch('core.ai_processor.Redis') as mock_redis:
            
            mock_event_bus = AsyncMock()
            mock_bus.return_value = mock_event_bus
            
            mock_redis_client = Mock()
            mock_redis.from_url.return_value = mock_redis_client
            
            await processor.start()
            
            assert processor.is_running
            assert processor.event_bus == mock_event_bus
            mock_event_bus.connect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mood_event_processing(self, ai_processor):
        """Test mood event processing"""
        mood_event = {
            "user_id": "test_user_123",
            "data": {
                "mood_score": 3,
                "emotions": ["sad", "anxious"]
            }
        }
        
        with patch.object(ai_processor, '_analyze_mood_patterns') as mock_analyze, \
             patch.object(ai_processor, '_update_user_context') as mock_update_context, \
             patch.object(ai_processor, '_evaluate_intervention_needs') as mock_evaluate:
            
            mock_analyze.return_value = {
                "mood_trend": "declining",
                "emotional_state": "sad",
                "risk_level": "medium",
                "confidence": 0.85
            }
            
            await ai_processor._handle_mood_event(mood_event)
            
            # Verify processing steps
            mock_analyze.assert_called_once_with("test_user_123", mood_event["data"])
            mock_update_context.assert_called_once()
            mock_evaluate.assert_called_once()
            
            # Verify event publishing
            ai_processor.event_bus.publish.assert_called_once()
            args, kwargs = ai_processor.event_bus.publish.call_args
            assert args[0] == "ai.emotion_analyzed"
    
    @pytest.mark.asyncio
    async def test_journal_event_processing(self, ai_processor):
        """Test journal event processing"""
        journal_event = {
            "user_id": "test_user_123",
            "data": {
                "content": "I'm feeling really down today. Nothing seems to be going right."
            }
        }
        
        with patch.object(ai_processor, '_analyze_journal_content') as mock_analyze:
            mock_analyze.return_value = {
                "sentiment": "negative",
                "sentiment_score": -0.7,
                "themes": ["emotional_distress"],
                "urgency": "medium",
                "confidence": 0.82
            }
            
            await ai_processor._handle_journal_event(journal_event)
            
            mock_analyze.assert_called_once_with("test_user_123", journal_event["data"]["content"])
            ai_processor.event_bus.publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_voice_event_processing(self, ai_processor):
        """Test voice event processing with urgency"""
        voice_event = {
            "user_id": "test_user_123",
            "data": {
                "audio_data": "mock_audio_data",
                "confidence": 0.95
            }
        }
        
        with patch.object(ai_processor, '_analyze_voice_emotion') as mock_analyze, \
             patch.object(ai_processor, '_evaluate_intervention_needs') as mock_evaluate:
            
            mock_analyze.return_value = {
                "emotion": "distress",
                "confidence": 0.89,
                "stress_level": "high"
            }
            
            await ai_processor._handle_voice_event(voice_event)
            
            # Verify urgent intervention evaluation
            mock_evaluate.assert_called_once()
            args, kwargs = mock_evaluate.call_args
            assert kwargs.get('urgent') == True
    
    @pytest.mark.asyncio
    async def test_context_update(self, ai_processor):
        """Test user context updating"""
        user_id = "test_user_123"
        source = "mood"
        analysis = {
            "mood_trend": "declining",
            "risk_level": "medium"
        }
        
        # Mock Redis operations
        ai_processor.redis_client.get.return_value = json.dumps({
            "user_id": user_id,
            "sources": {}
        })
        
        await ai_processor._update_user_context(user_id, source, analysis)
        
        # Verify Redis operations
        ai_processor.redis_client.setex.assert_called_once()
        ai_processor.event_bus.publish.assert_called_once()
        
        # Verify event data
        args, kwargs = ai_processor.event_bus.publish.call_args
        assert args[0] == "ai.context_updated"
        assert args[1]["user_id"] == user_id
        assert args[1]["source"] == source
    
    @pytest.mark.asyncio
    async def test_intervention_evaluation_high_risk(self, ai_processor):
        """Test intervention evaluation for high risk cases"""
        user_id = "test_user_123"
        analysis = {
            "risk_level": "high",
            "confidence": 0.95
        }
        
        await ai_processor._evaluate_intervention_needs(user_id, analysis)
        
        # Should trigger intervention needed event
        ai_processor.event_bus.publish.assert_called_once()
        args, kwargs = ai_processor.event_bus.publish.call_args
        assert args[0] == "ai.intervention_needed"
        assert args[1]["urgency"] == "medium"  # Default urgency when not urgent parameter
    
    @pytest.mark.asyncio
    async def test_intervention_evaluation_low_risk(self, ai_processor):
        """Test intervention evaluation for low risk cases"""
        user_id = "test_user_123"
        analysis = {
            "risk_level": "low",
            "confidence": 0.7
        }
        
        await ai_processor._evaluate_intervention_needs(user_id, analysis)
        
        # Should not trigger any intervention events
        ai_processor.event_bus.publish.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_metrics_update(self, ai_processor):
        """Test metrics updating"""
        initial_count = ai_processor.event_count
        processing_time = 0.15  # 150ms
        
        ai_processor._update_metrics(processing_time)
        
        assert ai_processor.event_count == initial_count + 1
        assert len(ai_processor.processing_times) == 1
        assert ai_processor.processing_times[0] == 150.0  # ms
    
    @pytest.mark.asyncio
    async def test_mood_pattern_analysis(self, ai_processor):
        """Test mood pattern analysis logic"""
        mood_data = {
            "mood_score": 2,
            "emotions": ["sad", "anxious"]
        }
        
        result = await ai_processor._analyze_mood_patterns("test_user", mood_data)
        
        assert result["mood_trend"] == "declining"
        assert result["emotional_state"] == "sad"
        assert result["risk_level"] == "high"  # Score 2 is high risk
        assert result["confidence"] == 0.85
    
    @pytest.mark.asyncio
    async def test_journal_content_analysis(self, ai_processor):
        """Test journal content analysis"""
        content = "I'm feeling really anxious about everything. Can't seem to focus."
        
        result = await ai_processor._analyze_journal_content("test_user", content)
        
        assert "sentiment" in result
        assert "themes" in result
        assert "word_count" in result
        assert result["word_count"] > 0
    
    @pytest.mark.asyncio
    async def test_voice_emotion_analysis(self, ai_processor):
        """Test voice emotion analysis"""
        voice_data = {
            "audio_features": {"mfcc": [1, 2, 3]},
            "confidence": 0.9
        }
        
        result = await ai_processor._analyze_voice_emotion("test_user", voice_data)
        
        assert "emotion" in result
        assert "confidence" in result
        assert "stress_level" in result
        assert "energy_level" in result
    
    @pytest.mark.asyncio
    async def test_conversation_analysis(self, ai_processor):
        """Test conversation analysis"""
        message = "I've been struggling lately and could use some support."
        
        result = await ai_processor._analyze_conversation("test_user", message)
        
        assert "sentiment" in result
        assert "intent" in result
        assert "engagement_level" in result
        assert "support_needed" in result
    
    @pytest.mark.asyncio
    async def test_health_check(self, ai_processor):
        """Test health check functionality"""
        ai_processor.is_running = True
        ai_processor.event_bus = Mock()
        
        assert ai_processor.health_check() == True
        
        ai_processor.is_running = False
        assert ai_processor.health_check() == False
    
    @pytest.mark.asyncio
    async def test_readiness_check(self, ai_processor):
        """Test readiness check functionality"""
        ai_processor.is_running = True
        ai_processor.event_bus = Mock()
        ai_processor.redis_client = Mock()
        
        assert ai_processor.is_ready() == True
        
        ai_processor.redis_client = None
        assert ai_processor.is_ready() == False
    
    @pytest.mark.asyncio
    async def test_error_handling_mood_event(self, ai_processor):
        """Test error handling in mood event processing"""
        invalid_event = {
            "user_id": None,  # Invalid user ID
            "data": {"mood_score": 5}
        }
        
        # Should not raise exception
        await ai_processor._handle_mood_event(invalid_event)
        
        # Verify error counting
        assert ai_processor.error_count == 0  # No error for missing user_id, just warning
    
    @pytest.mark.asyncio
    async def test_error_handling_context_update(self, ai_processor):
        """Test error handling in context updates"""
        # Simulate Redis error
        ai_processor.redis_client.setex.side_effect = Exception("Redis connection failed")
        
        # Should not raise exception
        await ai_processor._update_user_context("test_user", "test_source", {"test": "data"})
        
        # Processing should continue despite Redis error
        assert True  # Test passes if no exception is raised
    
    @pytest.mark.asyncio
    async def test_processing_latency(self, ai_processor):
        """Test processing latency requirements"""
        start_time = time.time()
        
        mood_event = {
            "user_id": "test_user_123",
            "data": {"mood_score": 5, "emotions": ["neutral"]}
        }
        
        await ai_processor._handle_mood_event(mood_event)
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Should process within 200ms requirement
        assert processing_time < 200, f"Processing took {processing_time}ms, should be <200ms"
    
    @pytest.mark.asyncio
    async def test_concurrent_event_processing(self, ai_processor):
        """Test concurrent event processing"""
        events = []
        for i in range(10):
            events.append({
                "user_id": f"test_user_{i}",
                "data": {"mood_score": i % 10, "emotions": ["neutral"]}
            })
        
        # Process events concurrently
        tasks = [ai_processor._handle_mood_event(event) for event in events]
        await asyncio.gather(*tasks)
        
        # All events should be processed
        assert ai_processor.event_count >= 10
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, ai_processor):
        """Test metrics collection"""
        # Process some events
        for i in range(5):
            ai_processor._update_metrics(0.1 + i * 0.01)  # Varying processing times
        
        metrics = await ai_processor.get_metrics()
        
        assert metrics["total_events_processed"] == 5
        assert metrics["average_processing_time_ms"] > 0
        assert metrics["events_per_minute"] >= 0
        assert metrics["error_rate"] >= 0

if __name__ == "__main__":
    pytest.main([__file__])
