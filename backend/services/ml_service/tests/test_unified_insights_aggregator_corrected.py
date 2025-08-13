"""
Unit tests for Unified Insights Aggregator (E2) - Corrected Version
Tests the actual backend response format, not the frontend transformed format
"""
import pytest
import sys
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock

# Add the parent directories to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from integrations.unified_insights_aggregator import UnifiedInsightsAggregator
from shared.models import MoodEntry


class TestUnifiedInsightsAggregatorCorrected:
    
    def setup_method(self):
        self.aggregator = UnifiedInsightsAggregator()
        self.mock_db = Mock()
        self.user_id = "test-user-123"
        # Clear cache between tests to avoid interference
        self.aggregator.clear_cache()
    
    def test_empty_mood_data(self):
        """Test aggregator with no mood entries"""
        # Mock empty query result
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        self.mock_db.query.return_value = mock_query
        
        result = self.aggregator.get_unified_insights(self.mock_db, self.user_id)
        
        # Verify backend response structure (NOT frontend format)
        assert 'user_id' in result
        assert 'timestamp' in result
        assert 'aggregated_insights' in result
        assert 'cache_info' in result
        
        # Check aggregated insights structure
        insights = result['aggregated_insights']
        assert 'mood' in insights
        assert 'trends' in insights
        assert 'insights_summary' in insights
        
        # With no mood data, should have zero scores
        mood_data = insights['mood']
        assert mood_data['total_entries'] == 0
        assert mood_data['average_score'] == 0
        assert mood_data['current_score'] == 0
        
        # Data quality should be low
        summary = insights['insights_summary']
        assert summary['data_quality'] == 0
        assert summary['confidence_score'] == 0.1
    
    def test_mood_data_aggregation(self):
        """Test aggregator with sample mood entries"""
        # Create mock mood entries
        now = datetime.now(timezone.utc)
        mock_entries = []
        
        # Create 8 entries over past week with varying scores
        for i in range(8):
            entry = Mock(spec=MoodEntry)
            entry.created_at = now - timedelta(days=i)
            entry.mood_score = 6 + (i % 3)  # scores: 6,7,8,6,7,8,6,7
            entry.energy_level = 5 + (i % 2)  # energy: 5,6,5,6,5,6,5,6
            
            # Configure mock to return the values properly
            entry.__dict__['mood_score'] = entry.mood_score
            entry.__dict__['energy_level'] = entry.energy_level
            entry.__dict__['created_at'] = entry.created_at
            
            mock_entries.append(entry)
        
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_entries
        self.mock_db.query.return_value = mock_query
        
        result = self.aggregator.get_unified_insights(self.mock_db, self.user_id)
        
        # Verify backend response structure and calculations
        insights = result['aggregated_insights']
        mood_data = insights['mood']
        
        assert mood_data['total_entries'] == 8
        assert mood_data['average_score'] > 0  # Should be around 6.875
        assert mood_data['current_score'] > 0
        assert mood_data['days_tracked'] > 0
        
        # Should have quality score since we have > 5 entries
        summary = insights['insights_summary']
        assert summary['data_quality'] > 0
        assert summary['confidence_score'] >= 0.4  # Should be 0.4 for > 5 entries
    
    def test_cache_behavior(self):
        """Test caching works correctly"""
        # Setup mock with minimal data
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        self.mock_db.query.return_value = mock_query
        
        # First call - should be cache miss
        result1 = self.aggregator.get_unified_insights(self.mock_db, self.user_id)
        assert result1['cache_info']['hit'] == False
        
        # Second call - should be cache hit
        result2 = self.aggregator.get_unified_insights(self.mock_db, self.user_id)
        assert result2['cache_info']['hit'] == True
        
        # Force refresh - should bypass cache
        result3 = self.aggregator.get_unified_insights(self.mock_db, self.user_id, force_refresh=True)
        assert result3['cache_info']['hit'] == False
    
    def test_data_quality_scoring(self):
        """Test data quality calculation"""
        # Test with 15 entries (should give 50% quality)
        mock_entries = []
        for i in range(15):
            entry = Mock(spec=MoodEntry)
            entry.created_at = datetime.now(timezone.utc) - timedelta(days=i)
            entry.mood_score = 7
            entry.energy_level = 6
            entry.__dict__['mood_score'] = entry.mood_score
            entry.__dict__['energy_level'] = entry.energy_level
            entry.__dict__['created_at'] = entry.created_at
            mock_entries.append(entry)
        
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_entries
        self.mock_db.query.return_value = mock_query
        
        result = self.aggregator.get_unified_insights(self.mock_db, self.user_id)
        
        expected_quality = min(int((15/30)*100), 100)  # 50%
        summary = result['aggregated_insights']['insights_summary']
        assert summary['data_quality'] == expected_quality
        assert summary['confidence_score'] == 0.4  # Should be 0.4 for >= 5 entries
    
    def test_mood_streak_calculation(self):
        """Test mood streak calculation logic"""
        now = datetime.now(timezone.utc)
        mock_entries = []
        
        # Create streak of good moods (above average)
        # Days 0-2: score 8, Day 3: score 4, Days 4-6: score 8
        scores = [8, 8, 8, 4, 8, 8, 8]
        for i, score in enumerate(scores):
            entry = Mock(spec=MoodEntry)
            entry.created_at = now - timedelta(days=i)
            entry.mood_score = score
            entry.energy_level = 6
            entry.__dict__['mood_score'] = entry.mood_score
            entry.__dict__['energy_level'] = entry.energy_level
            entry.__dict__['created_at'] = entry.created_at
            mock_entries.append(entry)
        
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_entries
        self.mock_db.query.return_value = mock_query
        
        result = self.aggregator.get_unified_insights(self.mock_db, self.user_id)
        
        # Should detect streak from most recent entries
        mood_data = result['aggregated_insights']['mood']
        assert mood_data['mood_streak'] >= 3  # At least 3 day streak from recent
    
    def test_response_contract_structure(self):
        """Test that response matches expected backend contract"""
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        self.mock_db.query.return_value = mock_query
        
        result = self.aggregator.get_unified_insights(self.mock_db, self.user_id)
        
        # Verify all required top-level keys for BACKEND format
        required_keys = ['user_id', 'timestamp', 'aggregated_insights', 'cache_info']
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"
        
        # Verify aggregated_insights structure
        insights = result['aggregated_insights']
        required_insight_keys = ['mood', 'trends', 'insights_summary']
        for key in required_insight_keys:
            assert key in insights, f"Missing insights key: {key}"
        
        # Verify mood data structure
        mood = insights['mood']
        required_mood_keys = ['current_score', 'average_score', 'total_entries', 'days_tracked']
        for key in required_mood_keys:
            assert key in mood, f"Missing mood key: {key}"
        
        # Verify insights summary structure
        summary = insights['insights_summary']
        required_summary_keys = ['confidence_score', 'data_quality', 'dominant_mood']
        for key in required_summary_keys:
            assert key in summary, f"Missing summary key: {key}"
        
        # Verify cache info structure
        cache_info = result['cache_info']
        required_cache_keys = ['hit', 'ttl_seconds', 'last_updated']
        for key in required_cache_keys:
            assert key in cache_info, f"Missing cache key: {key}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
