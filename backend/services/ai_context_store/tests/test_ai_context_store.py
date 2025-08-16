"""
Test Suite for AI Context Store Service
Tests all components of the AI Context Store implementation
"""

import pytest
import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from models.context_models import (
    ContextEntry, ContextType, ContextPriority, UserContext,
    MoodContext, CommunityContext, VoiceContext,
    IntelligenceInsight
)
from services.context_aggregator import ContextAggregatorService
from services.intelligence_engine import IntelligenceEngine
from services.event_processor import EventProcessor

class MockEvent:
    """Mock event for testing"""
    def __init__(self, channel: str, user_id: str, data: Dict[str, Any]):
        self.channel = channel
        self.user_id = user_id
        self.data = data
        self.timestamp = datetime.now(timezone.utc)

class TestContextAggregatorService:
    """Test Context Aggregator Service"""
    
    @pytest.fixture
    async def aggregator_service(self):
        """Create aggregator service for testing"""
        service = ContextAggregatorService()
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_create_user_context(self, aggregator_service):
        """Test creating new user context"""
        user_id = "test_user_123"
        
        # Test context creation
        context = await aggregator_service._create_user_context(user_id)
        
        assert context.user_id == user_id
        assert context.context_completeness == 0.0
        assert context.activity_score == 0.0
        assert context.mood_context is None
        
    @pytest.mark.asyncio
    async def test_add_context_entry(self, aggregator_service):
        """Test adding context entries"""
        user_id = "test_user_123"
        
        # Create mood context entry
        context_entry = ContextEntry(
            user_id=user_id,
            context_type=ContextType.MOOD,
            source_service="mood_service",
            event_channel="mood.entry.created",
            raw_data={"mood_score": 7.5, "energy_level": 6.0},
            processed_data={"mood_score": 7.5, "energy_level": 6.0}
        )
        
        # Add context entry
        success = await aggregator_service.add_context_entry(context_entry)
        assert success is True
        
        # Verify it was added to buffer
        assert user_id in aggregator_service.context_buffers
        assert len(aggregator_service.context_buffers[user_id]) > 0
        
    @pytest.mark.asyncio
    async def test_update_mood_context(self, aggregator_service):
        """Test updating mood context"""
        user_id = "test_user_123"
        
        # Test mood context update
        success = await aggregator_service.update_user_context(
            user_id,
            ContextType.MOOD,
            {"mood_score": 8.0, "energy_level": 7.5, "stress_level": 3.0}
        )
        
        assert success is True
        
        # Get updated context
        user_context = await aggregator_service.get_user_context(user_id)
        assert user_context is not None
        assert user_context.mood_context is not None
        assert user_context.mood_context.mood_score == 8.0
        assert user_context.mood_context.energy_level == 7.5
        
    @pytest.mark.asyncio
    async def test_update_community_context(self, aggregator_service):
        """Test updating community context"""
        user_id = "test_user_123"
        
        # Test community context update
        success = await aggregator_service.update_user_context(
            user_id,
            ContextType.COMMUNITY,
            {
                "engagement_level": "high",
                "challenges": ["meditation_challenge", "fitness_challenge"],
                "posts_increment": 2,
                "social_score": 0.8
            }
        )
        
        assert success is True
        
        # Get updated context
        user_context = await aggregator_service.get_user_context(user_id)
        assert user_context is not None
        assert user_context.community_context is not None
        assert user_context.community_context.engagement_level == "high"
        assert len(user_context.community_context.challenge_participation) == 2
        
    @pytest.mark.asyncio
    async def test_context_completeness_calculation(self, aggregator_service):
        """Test context completeness calculation"""
        user_id = "test_user_123"
        
        # Add multiple context types
        contexts = [
            (ContextType.MOOD, {"mood_score": 7.0, "energy_level": 6.0}),
            (ContextType.COMMUNITY, {"engagement_level": "moderate", "posts_increment": 1}),
            (ContextType.VOICE, {"commands": ["start_meditation"], "sentiment": 0.7})
        ]
        
        for context_type, data in contexts:
            await aggregator_service.update_user_context(user_id, context_type, data)
        
        # Check completeness
        user_context = await aggregator_service.get_user_context(user_id)
        assert user_context is not None
        assert user_context.context_completeness == 0.5  # 3 out of 6 contexts

class TestIntelligenceEngine:
    """Test Intelligence Engine"""
    
    @pytest.fixture
    async def intelligence_engine(self):
        """Create intelligence engine for testing"""
        engine = IntelligenceEngine()
        await engine.start_intelligence_processing()
        return engine
    
    @pytest.mark.asyncio
    async def test_mood_insights_generation(self, intelligence_engine):
        """Test mood-based insights generation"""
        user_id = "test_user_123"
        
        # Create user context with declining mood
        mood_context = MoodContext(
            mood_score=3.0,
            energy_level=2.5,
            mood_trend="declining",
            timestamp=datetime.now(timezone.utc)
        )
        
        user_context = UserContext(
            user_id=user_id,
            mood_context=mood_context,
            context_completeness=0.3,
            activity_score=0.2
        )
        
        # Generate insights
        insights = await intelligence_engine.generate_user_insights(user_id, user_context)
        
        # Check that mood warning insight was generated
        mood_insights = [i for i in insights if i.insight_type == "mood_trend_warning"]
        assert len(mood_insights) > 0
        
        mood_insight = mood_insights[0]
        assert mood_insight.confidence >= 0.5
        assert len(mood_insight.recommendations) > 0
        
    @pytest.mark.asyncio
    async def test_community_insights_generation(self, intelligence_engine):
        """Test community engagement insights"""
        user_id = "test_user_123"
        
        # Create context with low community engagement
        community_context = CommunityContext(
            engagement_level="low",
            challenge_participation=[],
            posts_created=0,
            social_score=0.1,
            timestamp=datetime.now(timezone.utc)
        )
        
        user_context = UserContext(
            user_id=user_id,
            community_context=community_context,
            context_completeness=0.2
        )
        
        # Generate insights
        insights = await intelligence_engine.generate_user_insights(user_id, user_context)
        
        # Check for low engagement insight
        engagement_insights = [i for i in insights if i.insight_type == "low_community_engagement"]
        assert len(engagement_insights) > 0
        
    @pytest.mark.asyncio
    async def test_holistic_engagement_insights(self, intelligence_engine):
        """Test holistic engagement insights"""
        user_id = "test_user_123"
        
        # Create comprehensive context
        user_context = UserContext(
            user_id=user_id,
            mood_context=MoodContext(
                mood_score=7.5,
                energy_level=7.0,
                mood_trend="improving",
                timestamp=datetime.now(timezone.utc)
            ),
            community_context=CommunityContext(
                engagement_level="high",
                challenge_participation=["challenge1", "challenge2"],
                posts_created=5,
                social_score=0.8,
                timestamp=datetime.now(timezone.utc)
            ),
            voice_context=VoiceContext(
                interaction_frequency=10,
                preferred_voice_commands=["start_session", "track_mood"],
                timestamp=datetime.now(timezone.utc)
            ),
            context_completeness=0.8,
            activity_score=0.7
        )
        
        # Generate insights
        insights = await intelligence_engine.generate_user_insights(user_id, user_context)
        
        # Check for holistic engagement insight
        holistic_insights = [i for i in insights if i.insight_type == "holistic_engagement"]
        assert len(holistic_insights) > 0
        
        holistic_insight = holistic_insights[0]
        assert holistic_insight.priority == ContextPriority.HIGH

class TestEventProcessor:
    """Test Event Processor"""
    
    @pytest.fixture
    async def event_processor(self):
        """Create event processor for testing"""
        aggregator = ContextAggregatorService()
        await aggregator.initialize()
        
        engine = IntelligenceEngine()
        await engine.start_intelligence_processing()
        
        processor = EventProcessor(aggregator, engine)
        return processor, aggregator, engine
    
    @pytest.mark.asyncio
    async def test_mood_event_processing(self, event_processor):
        """Test processing mood events"""
        processor, aggregator, engine = event_processor
        
        # Create mock mood event
        mock_event = MockEvent(
            channel="mood.entry.created",
            user_id="test_user_123",
            data={
                "mood_score": 8.5,
                "energy_level": 7.0,
                "notes": "Feeling great today!"
            }
        )
        
        # Process event
        await processor._handle_mood_entry_created(mock_event)
        
        # Verify context was updated
        user_context = await aggregator.get_user_context("test_user_123")
        assert user_context is not None
        assert user_context.mood_context is not None
        assert user_context.mood_context.mood_score == 8.5
        
    @pytest.mark.asyncio
    async def test_community_event_processing(self, event_processor):
        """Test processing community events"""
        processor, aggregator, engine = event_processor
        
        # Create mock community event
        mock_event = MockEvent(
            channel="community.challenge.progress.updated",
            user_id="test_user_123",
            data={
                "challenge_id": "meditation_challenge",
                "progress": 75,
                "engagement_level": "high"
            }
        )
        
        # Process event
        await processor._handle_challenge_progress(mock_event)
        
        # Verify context was updated
        user_context = await aggregator.get_user_context("test_user_123")
        assert user_context is not None
        assert user_context.community_context is not None
        assert "meditation_challenge" in user_context.community_context.challenge_participation
        
    @pytest.mark.asyncio
    async def test_voice_event_processing(self, event_processor):
        """Test processing voice events"""
        processor, aggregator, engine = event_processor
        
        # Create mock voice event
        mock_event = MockEvent(
            channel="voice.intent_classified",
            user_id="test_user_123",
            data={
                "intent": "start_meditation",
                "command": "start meditation session",
                "confidence": 0.95
            }
        )
        
        # Process event
        await processor._handle_voice_intent_classified(mock_event)
        
        # Verify context was updated
        user_context = await aggregator.get_user_context("test_user_123")
        assert user_context is not None
        assert user_context.voice_context is not None
        assert "start_meditation" in user_context.voice_context.intent_patterns

class TestIntegration:
    """Integration tests for full AI Context Store workflow"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # Initialize services
        aggregator = ContextAggregatorService()
        await aggregator.initialize()
        
        engine = IntelligenceEngine()
        await engine.start_intelligence_processing()
        
        processor = EventProcessor(aggregator, engine)
        
        user_id = "integration_test_user"
        
        # Simulate multiple events
        events = [
            MockEvent("mood.entry.created", user_id, {
                "mood_score": 4.0, "energy_level": 3.5
            }),
            MockEvent("community.post.created", user_id, {
                "type": "support", "tags": ["anxiety", "coping"]
            }),
            MockEvent("voice.activity_detected", user_id, {
                "command": "start breathing exercise", "sentiment_score": 0.3
            }),
            MockEvent("translation.completed", user_id, {
                "source_language": "en", "target_language": "es", "content_type": "affirmation"
            })
        ]
        
        # Process all events
        for event in events:
            if event.channel == "mood.entry.created":
                await processor._handle_mood_entry_created(event)
            elif event.channel == "community.post.created":
                await processor._handle_community_post_created(event)
            elif event.channel == "voice.activity_detected":
                await processor._handle_voice_activity_detected(event)
            elif event.channel == "translation.completed":
                await processor._handle_translation_completed(event)
        
        # Get final context
        user_context = await aggregator.get_user_context(user_id)
        assert user_context is not None
        
        # Verify all contexts were updated
        assert user_context.mood_context is not None
        assert user_context.community_context is not None
        assert user_context.voice_context is not None
        assert user_context.translation_context is not None
        
        # Generate insights
        insights = await engine.generate_user_insights(user_id, user_context)
        assert len(insights) > 0
        
        # Verify we got appropriate insights for low mood
        mood_warnings = [i for i in insights if "declining" in i.description.lower()]
        assert len(mood_warnings) > 0
        
        print(f"✅ End-to-end test completed successfully")
        print(f"   - Context completeness: {user_context.context_completeness}")
        print(f"   - Activity score: {user_context.activity_score}")
        print(f"   - Insights generated: {len(insights)}")
        
        # Cleanup
        await aggregator.stop()
        await engine.stop()

# Performance tests
class TestPerformance:
    """Performance tests for AI Context Store"""
    
    @pytest.mark.asyncio
    async def test_high_volume_context_updates(self):
        """Test handling high volume of context updates"""
        aggregator = ContextAggregatorService()
        await aggregator.initialize()
        
        # Create multiple users
        user_count = 100
        updates_per_user = 10
        
        start_time = datetime.now()
        
        # Perform many context updates
        for user_id in range(user_count):
            for update_count in range(updates_per_user):
                await aggregator.update_user_context(
                    f"user_{user_id}",
                    ContextType.MOOD,
                    {"mood_score": 5.0 + (update_count * 0.5), "energy_level": 5.0}
                )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        total_updates = user_count * updates_per_user
        updates_per_second = total_updates / duration
        
        print(f"✅ Performance test completed:")
        print(f"   - Total updates: {total_updates}")
        print(f"   - Duration: {duration:.2f} seconds")
        print(f"   - Updates per second: {updates_per_second:.2f}")
        
        # Verify performance is acceptable (should handle at least 100 updates/second)
        assert updates_per_second > 50
        
        await aggregator.stop()

if __name__ == "__main__":
    # Run tests manually
    import asyncio
    
    async def run_tests():
        """Run all tests manually"""
        print("🧪 Running AI Context Store Tests...")
        
        # Test Context Aggregator
        print("\n📊 Testing Context Aggregator...")
        aggregator = ContextAggregatorService()
        await aggregator.initialize()
        
        # Test creating context
        user_id = "manual_test_user"
        context = await aggregator._create_user_context(user_id)
        print(f"✅ Created context for user {user_id}")
        
        # Test mood update
        success = await aggregator.update_user_context(
            user_id, ContextType.MOOD, {"mood_score": 7.5, "energy_level": 6.0}
        )
        print(f"✅ Updated mood context: {success}")
        
        # Test Intelligence Engine
        print("\n🧠 Testing Intelligence Engine...")
        engine = IntelligenceEngine()
        await engine.start_intelligence_processing()
        
        user_context = await aggregator.get_user_context(user_id)
        insights = await engine.generate_user_insights(user_id, user_context)
        print(f"✅ Generated {len(insights)} insights")
        
        # Test Event Processor
        print("\n🔄 Testing Event Processor...")
        processor = EventProcessor(aggregator, engine)
        
        mock_event = MockEvent(
            "mood.entry.created", user_id, {"mood_score": 8.0, "energy_level": 7.5}
        )
        await processor._handle_mood_entry_created(mock_event)
        print("✅ Processed mock event")
        
        # Cleanup
        await aggregator.stop()
        await engine.stop()
        
        print("\n🎉 All manual tests completed successfully!")
    
    asyncio.run(run_tests())
