"""
Integration Test Suite for Enhanced Event Bus
Tests cross-service event publishing and subscription
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

# Test imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.events.enhanced_bus import EnhancedEventBus, V3EventChannels, get_enhanced_event_bus

class TestEnhancedEventBusIntegration:
    """Integration tests for the enhanced event bus"""
    
    @pytest.mark.asyncio
    async def test_event_bus_initialization(self):
        """Test that the enhanced event bus initializes correctly"""
        
        bus = get_enhanced_event_bus()
        assert bus is not None
        assert hasattr(bus, 'publish')
        assert hasattr(bus, 'subscribe')
        
    @pytest.mark.asyncio
    async def test_cross_service_event_flow(self):
        """Test complete event flow across services"""
        
        bus = get_enhanced_event_bus()
        received_events = []
        
        # Create event handler
        async def event_handler(event):
            received_events.append(event)
        
        # Subscribe to all V3 channels
        await bus.subscribe(V3EventChannels.MOOD_ENTRY_CREATED, event_handler)
        await bus.subscribe(V3EventChannels.CHALLENGE_PROGRESS_UPDATED, event_handler)
        await bus.subscribe(V3EventChannels.COMMUNITY_POST_CREATED, event_handler)
        await bus.subscribe(V3EventChannels.INSIGHT_DELTA, event_handler)
        
        # Publish events from different services
        test_events = [
            {
                'channel': V3EventChannels.MOOD_ENTRY_CREATED,
                'data': {
                    'user_id': 'test_user_123',
                    'mood_score': 8,
                    'energy_level': 7,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                },
                'user_id': 'test_user_123'
            },
            {
                'channel': V3EventChannels.CHALLENGE_PROGRESS_UPDATED,
                'data': {
                    'challenge_id': 'challenge_456',
                    'user_id': 'test_user_123',
                    'completed': True,
                    'streak_count': 5
                },
                'user_id': 'test_user_123'
            },
            {
                'channel': V3EventChannels.COMMUNITY_POST_CREATED,
                'data': {
                    'id': 'post_789',
                    'title': 'Test Post',
                    'author_id': 'test_user_123',
                    'post_type': 'thread'
                },
                'user_id': 'test_user_123'
            },
            {
                'channel': V3EventChannels.INSIGHT_DELTA,
                'data': {
                    'user_id': 'test_user_123',
                    'insights': {'trend': 'improving'},
                    'version': 'v2_enhanced'
                },
                'user_id': 'test_user_123'
            }
        ]
        
        # Publish all events
        for event in test_events:
            success = await bus.publish(
                event['channel'],
                event['data'],
                user_id=event['user_id']
            )
            assert success == True
        
        # Give a moment for event processing
        await asyncio.sleep(0.1)
        
        # Verify all events were received
        assert len(received_events) == 4
        
        # Verify event data integrity
        channels_received = [event.channel for event in received_events]
        assert V3EventChannels.MOOD_ENTRY_CREATED in channels_received
        assert V3EventChannels.CHALLENGE_PROGRESS_UPDATED in channels_received
        assert V3EventChannels.COMMUNITY_POST_CREATED in channels_received
        assert V3EventChannels.INSIGHT_DELTA in channels_received

    @pytest.mark.asyncio
    async def test_event_ordering_and_consistency(self):
        """Test that events maintain proper ordering and consistency"""
        
        bus = get_enhanced_event_bus()
        received_events = []
        
        async def ordered_handler(event):
            received_events.append({
                'channel': event.channel,
                'timestamp': event.timestamp,
                'user_id': event.user_id,
                'data': event.data
            })
        
        # Subscribe to mood events
        await bus.subscribe(V3EventChannels.MOOD_ENTRY_CREATED, ordered_handler)
        
        # Publish multiple mood events in sequence
        mood_scores = [6, 7, 8, 7, 9]
        for i, score in enumerate(mood_scores):
            await bus.publish(
                V3EventChannels.MOOD_ENTRY_CREATED,
                {
                    'sequence': i,
                    'mood_score': score,
                    'user_id': 'test_user_123'
                },
                user_id='test_user_123'
            )
        
        await asyncio.sleep(0.1)
        
        # Verify all events received
        assert len(received_events) == 5
        
        # Verify ordering (events should maintain sequence)
        for i, event in enumerate(received_events):
            assert event['data']['sequence'] == i
            assert event['data']['mood_score'] == mood_scores[i]

    @pytest.mark.asyncio 
    async def test_event_subscription_management(self):
        """Test subscribing and unsubscribing from events"""
        
        bus = get_enhanced_event_bus()
        received_events = []
        
        async def test_handler(event):
            received_events.append(event)
        
        # Subscribe to events
        await bus.subscribe(V3EventChannels.MOOD_ENTRY_CREATED, test_handler)
        
        # Publish event - should be received
        await bus.publish(
            V3EventChannels.MOOD_ENTRY_CREATED,
            {'test': 'data1'},
            user_id='test_user'
        )
        
        await asyncio.sleep(0.1)
        assert len(received_events) == 1
        
        # Unsubscribe
        await bus.unsubscribe(V3EventChannels.MOOD_ENTRY_CREATED, test_handler)
        
        # Publish another event - should not be received
        await bus.publish(
            V3EventChannels.MOOD_ENTRY_CREATED,
            {'test': 'data2'},
            user_id='test_user'
        )
        
        await asyncio.sleep(0.1)
        assert len(received_events) == 1  # Should still be 1

    @pytest.mark.asyncio
    async def test_error_handling_in_event_processing(self):
        """Test that errors in event handlers don't break the system"""
        
        bus = get_enhanced_event_bus()
        successful_events = []
        
        async def failing_handler(event):
            raise Exception("Handler failed")
        
        async def successful_handler(event):
            successful_events.append(event)
        
        # Subscribe both handlers to the same channel
        await bus.subscribe(V3EventChannels.MOOD_ENTRY_CREATED, failing_handler)
        await bus.subscribe(V3EventChannels.MOOD_ENTRY_CREATED, successful_handler)
        
        # Publish event
        success = await bus.publish(
            V3EventChannels.MOOD_ENTRY_CREATED,
            {'test': 'error_handling'},
            user_id='test_user'
        )
        
        await asyncio.sleep(0.1)
        
        # Event publishing should still succeed even if one handler fails
        assert success == True
        # Successful handler should still receive the event
        assert len(successful_events) == 1

    def test_v3_event_channel_constants(self):
        """Test that all required V3 event channel constants are defined"""
        
        required_channels = [
            'MOOD_ENTRY_CREATED',
            'JOURNAL_ENTRY_CREATED',
            'CHALLENGE_PROGRESS_UPDATED',
            'COMMUNITY_POST_CREATED',
            'INSIGHT_DELTA'
        ]
        
        for channel in required_channels:
            assert hasattr(V3EventChannels, channel)
            channel_value = getattr(V3EventChannels, channel)
            assert isinstance(channel_value, str)
            assert len(channel_value) > 0

    def test_event_channel_naming_convention(self):
        """Test that event channels follow proper naming convention"""
        
        # Check that channels follow the pattern: service.entity.action
        channels_to_check = [
            (V3EventChannels.MOOD_ENTRY_CREATED, 'mood.entry.created'),
            (V3EventChannels.JOURNAL_ENTRY_CREATED, 'journal.entry.created'),
            (V3EventChannels.CHALLENGE_PROGRESS_UPDATED, 'community.challenge.progress.updated'),
            (V3EventChannels.COMMUNITY_POST_CREATED, 'community.post.created'),
            (V3EventChannels.INSIGHT_DELTA, 'ml.insight.delta')
        ]
        
        for actual, expected in channels_to_check:
            assert actual == expected

class TestEventDataValidation:
    """Test event data validation and structure"""
    
    def test_mood_entry_event_data_structure(self):
        """Test mood entry event data has expected structure"""
        
        mood_event_data = {
            'user_id': 'test_user_123',
            'mood_score': 8,
            'energy_level': 7,
            'stress_level': 3,
            'notes': 'Feeling great today',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Required fields
        assert 'user_id' in mood_event_data
        assert 'mood_score' in mood_event_data
        assert 'timestamp' in mood_event_data
        
        # Data types
        assert isinstance(mood_event_data['user_id'], str)
        assert isinstance(mood_event_data['mood_score'], int)
        assert isinstance(mood_event_data['timestamp'], str)
        
        # Value ranges
        assert 1 <= mood_event_data['mood_score'] <= 10

    def test_challenge_progress_event_data_structure(self):
        """Test challenge progress event data has expected structure"""
        
        progress_event_data = {
            'challenge_id': 'challenge_456',
            'user_id': 'test_user_123',
            'completed': True,
            'streak_count': 5,
            'date': datetime.now(timezone.utc).date().isoformat(),
            'mood_rating': 8,
            'difficulty_rating': 3,
            'notes': 'Great progress',
            'reflection': 'Feeling motivated'
        }
        
        # Required fields
        assert 'challenge_id' in progress_event_data
        assert 'user_id' in progress_event_data
        assert 'completed' in progress_event_data
        assert 'streak_count' in progress_event_data
        
        # Data types
        assert isinstance(progress_event_data['challenge_id'], str)
        assert isinstance(progress_event_data['user_id'], str)
        assert isinstance(progress_event_data['completed'], bool)
        assert isinstance(progress_event_data['streak_count'], int)

    def test_community_post_event_data_structure(self):
        """Test community post event data has expected structure"""
        
        post_event_data = {
            'id': 'post_789',
            'forum_id': 'forum_123',
            'title': 'Test Post Title',
            'content': 'Test post content',
            'post_type': 'thread',
            'author_id': 'test_user_123',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Required fields
        assert 'id' in post_event_data
        assert 'author_id' in post_event_data
        assert 'post_type' in post_event_data
        assert 'created_at' in post_event_data
        
        # Data types
        assert isinstance(post_event_data['id'], str)
        assert isinstance(post_event_data['author_id'], str)
        assert isinstance(post_event_data['post_type'], str)

    def test_insight_delta_event_data_structure(self):
        """Test insight delta event data has expected structure"""
        
        insight_event_data = {
            'user_id': 'test_user_123',
            'insights': {
                'mood_trends': {'average': 7.5},
                'recommendations': ['Practice in the morning']
            },
            'version': 'v2_enhanced',
            'enhanced': True,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Required fields
        assert 'user_id' in insight_event_data
        assert 'insights' in insight_event_data
        assert 'version' in insight_event_data
        assert 'timestamp' in insight_event_data
        
        # Data types
        assert isinstance(insight_event_data['user_id'], str)
        assert isinstance(insight_event_data['insights'], dict)
        assert isinstance(insight_event_data['version'], str)

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
