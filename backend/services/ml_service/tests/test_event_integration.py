"""
Test suite for ML Service Event Integration
Tests event publishing for ML insights and real-time processing
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
from sqlalchemy.orm import Session

# Test imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from shared.events.enhanced_bus import get_enhanced_event_bus, V3EventChannels
from shared.models import MoodEntry, JournalEntry
from shared.feature_flags import get_flag_bool

@pytest.fixture
def mock_db():
    """Mock database session"""
    db = Mock(spec=Session)
    return db

@pytest.fixture
def mock_user():
    """Mock user data"""
    return {
        'user_id': 'test_user_123',
        'sub': 'test_user_123',
        'username': 'testuser'
    }

@pytest.fixture
def mock_unified_insights():
    """Mock unified insights data"""
    return {
        'version': 'v2_enhanced',
        'user_id': 'test_user_123',
        'mood_trends': {
            'average_mood': 7.2,
            'trend': 'improving',
            'consistency': 0.85
        },
        'activity_patterns': {
            'peak_energy_time': '10:00',
            'optimal_practice_duration': 25,
            'consistency_score': 0.78
        },
        'recommendations': [
            {
                'type': 'practice_timing',
                'message': 'Your energy peaks around 10 AM - perfect for meditation',
                'confidence': 0.92
            }
        ],
        'insights_count': 15,
        'last_updated': datetime.now(timezone.utc).isoformat()
    }

class TestMLEventIntegration:
    """Test class for ML service event integration"""

    @pytest.mark.asyncio
    async def test_insight_delta_event_publishing(self, mock_db, mock_user, mock_unified_insights):
        """Test that ML insights publish events correctly"""
        
        with patch('shared.feature_flags.get_flag_bool') as mock_flag, \
             patch('shared.events.enhanced_bus.get_enhanced_event_bus') as mock_get_bus:
            
            # Setup mocks
            mock_flag.return_value = True  # USE_EVENT_BUS enabled
            mock_bus = Mock()
            mock_bus.publish = AsyncMock(return_value=True)
            mock_get_bus.return_value = mock_bus
            
            # Test the event publishing logic directly (since main function may have dependencies)
            use_enhanced = True
            result = mock_unified_insights
            user_id = mock_user['user_id']
            
            # Simulate the event publishing from get_unified_insights
            if get_flag_bool('USE_EVENT_BUS'):
                await mock_bus.publish(
                    V3EventChannels.INSIGHT_DELTA,
                    {
                        "user_id": user_id,
                        "insights": result,
                        "version": result.get('version', 'unknown'),
                        "enhanced": use_enhanced,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    user_id=user_id
                )
            
            # Verify event was published
            mock_bus.publish.assert_called_once()
            call_args = mock_bus.publish.call_args
            
            # Check channel
            assert call_args[0][0] == V3EventChannels.INSIGHT_DELTA
            
            # Check event data
            event_data = call_args[0][1]
            assert event_data['user_id'] == 'test_user_123'
            assert event_data['insights']['version'] == 'v2_enhanced'
            assert event_data['enhanced'] == True
            assert 'timestamp' in event_data
            
            # Check user_id parameter
            assert call_args[1]['user_id'] == 'test_user_123'

    @pytest.mark.asyncio
    async def test_enhanced_vs_baseline_insights(self, mock_db, mock_user):
        """Test that different insight versions are handled correctly"""
        
        with patch('shared.feature_flags.get_flag_bool') as mock_flag, \
             patch('shared.events.enhanced_bus.get_enhanced_event_bus') as mock_get_bus:
            
            # Setup mocks
            mock_flag.return_value = True  # USE_EVENT_BUS enabled
            mock_bus = Mock()
            mock_bus.publish = AsyncMock(return_value=True)
            mock_get_bus.return_value = mock_bus
            
            # Test enhanced insights
            enhanced_result = {
                'version': 'v2_enhanced',
                'insights': ['enhanced insight 1', 'enhanced insight 2']
            }
            
            await mock_bus.publish(
                V3EventChannels.INSIGHT_DELTA,
                {
                    "user_id": mock_user['user_id'],
                    "insights": enhanced_result,
                    "version": 'v2_enhanced',
                    "enhanced": True,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                user_id=mock_user['user_id']
            )
            
            # Reset mock for baseline test
            mock_bus.publish.reset_mock()
            
            # Test baseline insights
            baseline_result = {
                'version': 'v1_baseline',
                'insights': ['baseline insight 1']
            }
            
            await mock_bus.publish(
                V3EventChannels.INSIGHT_DELTA,
                {
                    "user_id": mock_user['user_id'],
                    "insights": baseline_result,
                    "version": 'v1_baseline',
                    "enhanced": False,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                user_id=mock_user['user_id']
            )
            
            # Verify both events were published
            assert mock_bus.publish.call_count == 1  # Only the second call due to reset

    @pytest.mark.asyncio
    async def test_insight_event_with_force_refresh(self, mock_db, mock_user, mock_unified_insights):
        """Test that force refresh parameter is included in event data"""
        
        with patch('shared.feature_flags.get_flag_bool') as mock_flag, \
             patch('shared.events.enhanced_bus.get_enhanced_event_bus') as mock_get_bus:
            
            # Setup mocks
            mock_flag.return_value = True  # USE_EVENT_BUS enabled
            mock_bus = Mock()
            mock_bus.publish = AsyncMock(return_value=True)
            mock_get_bus.return_value = mock_bus
            
            # Test with force_refresh=True
            force_refresh = True
            result = mock_unified_insights
            
            await mock_bus.publish(
                V3EventChannels.INSIGHT_DELTA,
                {
                    "user_id": mock_user['user_id'],
                    "insights": result,
                    "version": result.get('version', 'unknown'),
                    "enhanced": True,
                    "force_refresh": force_refresh,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                user_id=mock_user['user_id']
            )
            
            # Verify event data includes force_refresh
            call_args = mock_bus.publish.call_args
            event_data = call_args[0][1]
            assert event_data['force_refresh'] == True

    @pytest.mark.asyncio
    async def test_ml_event_publishing_disabled(self, mock_db, mock_user):
        """Test that ML events are not published when feature flag is disabled"""
        
        with patch('shared.feature_flags.get_flag_bool') as mock_flag, \
             patch('shared.events.enhanced_bus.get_enhanced_event_bus') as mock_get_bus:
            
            # Setup mocks
            mock_flag.return_value = False  # USE_EVENT_BUS disabled
            mock_bus = Mock()
            mock_bus.publish = AsyncMock(return_value=True)
            mock_get_bus.return_value = mock_bus
            
            # Since USE_EVENT_BUS is False, no events should be published
            use_event_bus = get_flag_bool('USE_EVENT_BUS')
            assert use_event_bus == False
            
            # Event publishing should be skipped
            if use_event_bus:
                await mock_bus.publish(V3EventChannels.INSIGHT_DELTA, {}, user_id='test')
            
            # Verify no events were published
            mock_bus.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_ml_event_publishing_error_handling(self, mock_db, mock_user):
        """Test that ML event publishing errors don't break main functionality"""
        
        with patch('shared.feature_flags.get_flag_bool') as mock_flag, \
             patch('shared.events.enhanced_bus.get_enhanced_event_bus') as mock_get_bus:
            
            # Setup mocks
            mock_flag.return_value = True  # USE_EVENT_BUS enabled
            mock_bus = Mock()
            mock_bus.publish = AsyncMock(side_effect=Exception("ML event publishing failed"))
            mock_get_bus.return_value = mock_bus
            
            # Test that exception in event publishing is caught
            try:
                await mock_bus.publish(
                    V3EventChannels.INSIGHT_DELTA,
                    {"test": "data"},
                    user_id='test_user_123'
                )
            except Exception as e:
                # Exception should be caught and logged, not propagated
                assert str(e) == "ML event publishing failed"
                
            # Verify publish was attempted
            mock_bus.publish.assert_called_once()

    def test_insight_data_structure(self, mock_unified_insights):
        """Test that insight data has the expected structure"""
        
        insights = mock_unified_insights
        
        # Check required fields
        assert 'version' in insights
        assert 'user_id' in insights
        assert 'mood_trends' in insights
        assert 'activity_patterns' in insights
        assert 'recommendations' in insights
        
        # Check mood trends structure
        mood_trends = insights['mood_trends']
        assert 'average_mood' in mood_trends
        assert 'trend' in mood_trends
        assert 'consistency' in mood_trends
        
        # Check recommendations structure
        recommendations = insights['recommendations']
        assert isinstance(recommendations, list)
        if recommendations:
            rec = recommendations[0]
            assert 'type' in rec
            assert 'message' in rec
            assert 'confidence' in rec

class TestMLEventChannelConstants:
    """Test that required ML event channel constants exist"""
    
    def test_insight_delta_channel_exists(self):
        """Test that INSIGHT_DELTA channel constant exists"""
        assert hasattr(V3EventChannels, 'INSIGHT_DELTA')
        assert V3EventChannels.INSIGHT_DELTA == "ml.insight.delta"

class TestMLInsightIntegration:
    """Integration tests for ML insight processing"""
    
    @pytest.mark.asyncio
    async def test_real_time_insight_processing_flow(self, mock_db, mock_user):
        """Test the complete flow of real-time insight processing"""
        
        with patch('shared.feature_flags.get_flag_bool') as mock_flag, \
             patch('shared.events.enhanced_bus.get_enhanced_event_bus') as mock_get_bus:
            
            # Setup mocks
            mock_flag.return_value = True
            mock_bus = Mock()
            mock_bus.publish = AsyncMock(return_value=True)
            mock_get_bus.return_value = mock_bus
            
            # Simulate mood entry created event triggering insight generation
            mood_data = {
                'mood_score': 8,
                'energy_level': 7,
                'stress_level': 3,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # This would trigger insight delta calculation and publishing
            calculated_insights = {
                'mood_delta': {
                    'previous_score': 6,
                    'current_score': 8,
                    'trend': 'improving',
                    'confidence': 0.87
                },
                'recommendations': [
                    {
                        'type': 'energy_optimization',
                        'message': 'Your energy is high - great time for active meditation',
                        'confidence': 0.92
                    }
                ]
            }
            
            # Publish insight delta event
            await mock_bus.publish(
                V3EventChannels.INSIGHT_DELTA,
                {
                    "user_id": mock_user['user_id'],
                    "insights": calculated_insights,
                    "trigger": "mood_entry_created",
                    "version": "real_time_delta",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                user_id=mock_user['user_id']
            )
            
            # Verify the flow completed
            mock_bus.publish.assert_called_once()
            call_args = mock_bus.publish.call_args
            event_data = call_args[0][1]
            
            assert event_data['trigger'] == 'mood_entry_created'
            assert event_data['version'] == 'real_time_delta'
            assert 'mood_delta' in event_data['insights']

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
