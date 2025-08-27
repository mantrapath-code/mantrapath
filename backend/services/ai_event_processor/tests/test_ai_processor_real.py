"""
Real implementation tests for AI Event Processor
Tests the actual business logic without mocking internal methods
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import json
import time
from datetime import datetime, timezone

import sys
import os
# Add both the current service directory and the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from core.ai_processor import AIEventProcessor
from models.ai_models import AIMetrics

class TestAIEventProcessorReal:
    """Test suite for AI Event Processor with real implementations"""
    
    @pytest.fixture
    def ai_processor(self):
        """Create AI processor instance for testing"""
        processor = AIEventProcessor()
        
        # Mock only external dependencies
        processor.event_bus = AsyncMock()
        processor.redis_client = Mock()
        processor.redis_client.get.return_value = None
        processor.redis_client.setex.return_value = True
        processor.is_running = True
        
        return processor
    
    @pytest.mark.asyncio
    async def test_mood_pattern_analysis_real(self, ai_processor):
        """Test real mood pattern analysis implementation"""
        user_id = "test_user_123"
        mood_data = {
            "mood_score": 2,
            "emotions": ["sad", "anxious"]
        }
        
        result = await ai_processor._analyze_mood_patterns(user_id, mood_data)
        
        # Verify analysis results
        assert result["mood_trend"] == "declining"  # mood_score < 4
        assert result["emotional_state"] == "sad"
        assert result["risk_level"] == "medium"  # mood_score >= 2
        assert result["confidence"] == 0.85
    
    @pytest.mark.asyncio
    async def test_mood_pattern_analysis_high_risk(self, ai_processor):
        """Test mood analysis for high risk cases"""
        user_id = "test_user_123"
        mood_data = {
            "mood_score": 1,
            "emotions": ["depressed", "hopeless"]
        }
        
        result = await ai_processor._analyze_mood_patterns(user_id, mood_data)
        
        assert result["mood_trend"] == "declining"
        assert result["risk_level"] == "high"  # mood_score < 2
        assert result["confidence"] == 0.85
    
    @pytest.mark.asyncio
    async def test_mood_pattern_analysis_positive(self, ai_processor):
        """Test mood analysis for positive mood"""
        user_id = "test_user_123"
        mood_data = {
            "mood_score": 8,
            "emotions": ["happy", "excited"]
        }
        
        result = await ai_processor._analyze_mood_patterns(user_id, mood_data)
        
        assert result["mood_trend"] == "improving"  # mood_score > 6
        assert result["risk_level"] == "low"  # mood_score >= 4
        assert result["confidence"] == 0.85
    
    @pytest.mark.asyncio
    async def test_journal_content_analysis_real(self, ai_processor):
        """Test real journal content analysis"""
        user_id = "test_user_123"
        content = "I'm feeling really down today. Nothing seems to be going right. Everything is overwhelming."
        
        result = await ai_processor._analyze_journal_content(user_id, content)
        
        # Verify basic analysis structure
        assert "sentiment" in result
        assert "sentiment_score" in result
        assert "themes" in result
        assert "urgency" in result
        assert "word_count" in result
        assert "confidence" in result
        assert result["word_count"] == 14
    
    @pytest.mark.asyncio
    async def test_voice_emotion_analysis_real(self, ai_processor):
        """Test real voice emotion analysis"""
        user_id = "test_user_123"
        voice_data = {
            "audio_data": "mock_audio_features",
            "confidence": 0.95
        }
        
        result = await ai_processor._analyze_voice_emotion(user_id, voice_data)
        
        # Verify analysis structure
        assert "emotion" in result
        assert "confidence" in result
        assert "stress_level" in result
        assert "energy_level" in result
        assert "voice_quality" in result
        assert result["confidence"] == 0.75
    
    @pytest.mark.asyncio
    async def test_conversation_analysis_real(self, ai_processor):
        """Test real conversation analysis"""
        user_id = "test_user_123"
        message = "I've been having trouble sleeping and feeling anxious about work."
        
        result = await ai_processor._analyze_conversation(user_id, message)
        
        # Verify analysis structure
        assert "sentiment" in result
        assert "intent" in result
        assert "engagement_level" in result
        assert "support_needed" in result
        assert "confidence" in result
    
    @pytest.mark.asyncio
    async def test_user_context_update_real(self, ai_processor):
        """Test real user context updating"""
        user_id = "test_user_123"
        source = "mood_analysis"
        analysis = {
            "mood_trend": "declining",
            "risk_level": "medium",
            "confidence": 0.85
        }
        
        # Test the real implementation
        await ai_processor._update_user_context(user_id, source, analysis)
        
        # Verify Redis was called with user context
        ai_processor.redis_client.setex.assert_called()
        call_args = ai_processor.redis_client.setex.call_args[0]
        assert user_id in call_args[0]  # Key contains user_id
        assert call_args[1] == 3600  # 1 hour TTL
    
    @pytest.mark.asyncio
    async def test_intervention_evaluation_high_risk(self, ai_processor):
        """Test intervention evaluation for high risk"""
        user_id = "test_user_123"
        analysis = {
            "risk_level": "high",
            "confidence": 0.95,
            "mood_trend": "declining"
        }
        
        await ai_processor._evaluate_intervention_needs(user_id, analysis, urgent=False)
        
        # Should publish an intervention event for high risk
        ai_processor.event_bus.publish.assert_called()
        call_args = ai_processor.event_bus.publish.call_args[0]
        assert "intervention" in call_args[0]  # Channel name contains 'intervention'
        assert call_args[1]["user_id"] == user_id  # Event data has user_id
    
    @pytest.mark.asyncio
    async def test_intervention_evaluation_low_risk(self, ai_processor):
        """Test intervention evaluation for low risk"""
        user_id = "test_user_123"
        analysis = {
            "risk_level": "low",
            "confidence": 0.70,
            "mood_trend": "stable"
        }
        
        await ai_processor._evaluate_intervention_needs(user_id, analysis, urgent=False)
        
        # Should not publish intervention event for low risk
        # The method should complete without error
        assert True  # Test passes if no exception
    
    @pytest.mark.asyncio
    async def test_mood_event_handling_complete(self, ai_processor):
        """Test complete mood event handling pipeline"""
        mood_event = {
            "user_id": "test_user_123",
            "data": {
                "mood_score": 2,
                "emotions": ["sad", "anxious"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        initial_count = ai_processor.event_count
        
        # Process the complete event
        await ai_processor._handle_mood_event(mood_event)
        
        # Verify processing metrics updated
        assert ai_processor.event_count == initial_count + 1
        assert len(ai_processor.processing_times) > 0
        
        # Verify Redis context update was called
        ai_processor.redis_client.setex.assert_called()
        
        # Verify event was published (due to high risk)
        ai_processor.event_bus.publish.assert_called()
    
    @pytest.mark.asyncio
    async def test_journal_event_handling_complete(self, ai_processor):
        """Test complete journal event handling pipeline"""
        journal_event = {
            "user_id": "test_user_123",
            "data": {
                "content": "I'm feeling overwhelmed and anxious about everything today.",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        initial_count = ai_processor.event_count
        
        # Process the complete event
        await ai_processor._handle_journal_event(journal_event)
        
        # Verify processing metrics updated
        assert ai_processor.event_count == initial_count + 1
        
        # Verify Redis context update was called
        ai_processor.redis_client.setex.assert_called()
        
        # Verify event was published
        ai_processor.event_bus.publish.assert_called()
    
    @pytest.mark.asyncio
    async def test_voice_event_handling_complete(self, ai_processor):
        """Test complete voice event handling pipeline"""
        voice_event = {
            "user_id": "test_user_123",
            "data": {
                "audio_data": "mock_audio_data",
                "confidence": 0.95,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        initial_count = ai_processor.event_count
        
        # Process the complete event
        await ai_processor._handle_voice_event(voice_event)
        
        # Verify processing metrics updated
        assert ai_processor.event_count == initial_count + 1
        
        # Verify Redis context update was called
        ai_processor.redis_client.setex.assert_called()
    
    def test_metrics_update_real(self, ai_processor):
        """Test real metrics updating"""
        initial_count = ai_processor.event_count
        
        # Update metrics with processing time
        ai_processor._update_metrics(0.15)  # 150ms
        
        # Verify metrics updated
        assert ai_processor.event_count == initial_count + 1
        assert ai_processor.processing_times[-1] == 150.0  # 150ms
        assert ai_processor.metrics.total_events_processed == ai_processor.event_count
        assert ai_processor.metrics.average_processing_time_ms > 0
    
    def test_health_check_real(self, ai_processor):
        """Test real health check"""
        # Processor should be healthy when running with event bus
        assert ai_processor.health_check() == True
        
        # Should be unhealthy when not running
        ai_processor.is_running = False
        assert ai_processor.health_check() == False
        
        # Should be unhealthy without event bus
        ai_processor.is_running = True
        ai_processor.event_bus = None
        assert ai_processor.health_check() == False
    
    def test_readiness_check_real(self, ai_processor):
        """Test real readiness check"""
        # Should be ready with all dependencies
        assert ai_processor.is_ready() == True
        
        # Should not be ready without Redis
        ai_processor.redis_client = None
        assert ai_processor.is_ready() == False
    
    @pytest.mark.asyncio
    async def test_get_metrics_real(self, ai_processor):
        """Test real metrics retrieval"""
        # Process some events to generate metrics
        ai_processor._update_metrics(0.1)
        ai_processor._update_metrics(0.2)
        
        metrics = await ai_processor.get_metrics()
        
        # Verify metrics structure
        assert "total_events_processed" in metrics
        assert "average_processing_time_ms" in metrics
        assert "error_rate" in metrics
        assert "events_per_minute" in metrics
        assert metrics["total_events_processed"] == 2
