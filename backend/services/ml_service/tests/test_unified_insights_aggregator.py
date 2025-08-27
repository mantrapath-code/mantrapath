"""
Unit tests for Unified Insights Aggregator (E2)
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


class TestUnifiedInsightsAggregator:
    
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
            # Use direct assignment to avoid Mock confusion
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
        
        # Verify calculations
        assert result['dashboard']['weeklySummary']['currentWeekScore'] > 0
        assert result['dashboard']['currentStatus']['moodScore'] > 0
        assert result['metadata']['dataQuality'] > 0
        assert result['metadata']['confidenceScore'] >= 0.1
        assert result['dashboard']['weeklySummary']['daysTracked'] == 8
        assert result['metadata']['sourceDistribution']['personalized'] == 0  # None yet
    
    def test_cache_behavior(self):
        """Test caching works correctly"""
        # Setup mock with minimal data
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        self.mock_db.query.return_value = mock_query
        
        # First call - should be cache miss
        result1 = self.aggregator.get_unified_insights(self.mock_db, self.user_id)
        assert result1['metadata']['cache'] == 'miss'
        
        # Second call - should be cache hit
        result2 = self.aggregator.get_unified_insights(self.mock_db, self.user_id)
        assert result2['metadata']['cache'] == 'hit'
        
        # Force refresh - should be cache miss again
        result3 = self.aggregator.get_unified_insights(self.mock_db, self.user_id, force_refresh=True)
        assert result3['metadata']['cache'] == 'miss'
    
    def test_data_quality_scoring(self):
        """Test data quality calculation"""
        # Test with 15 entries (should give 50% quality)
        mock_entries = []
        for i in range(15):
            entry = Mock(spec=MoodEntry)
            entry.created_at = datetime.now(timezone.utc) - timedelta(days=i)
            entry.mood_score = 7
            entry.energy_level = 6
            mock_entries.append(entry)
        
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_entries
        self.mock_db.query.return_value = mock_query
        
        result = self.aggregator.get_unified_insights(self.mock_db, self.user_id)
        
        expected_quality = min(int((15/30)*100), 100)  # 50%
        assert result['metadata']['dataQuality'] == expected_quality
        assert result['metadata']['confidenceScore'] == 0.4  # >= 5 entries
    
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
            mock_entries.append(entry)
        
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_entries
        self.mock_db.query.return_value = mock_query
        
        result = self.aggregator.get_unified_insights(self.mock_db, self.user_id)
        
        # Should detect 3-day streak from most recent
        assert result['dashboard']['topHighlights']['moodStreak'] == 3
    
    def test_response_contract_structure(self):
        """Test that response matches expected frontend contract"""
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        self.mock_db.query.return_value = mock_query
        
        result = self.aggregator.get_unified_insights(self.mock_db, self.user_id)
        
        # Verify all required top-level keys
        required_keys = ['dashboard', 'detailedAnalysis', 'recommendedActions', 'progressTracking', 'metadata']
        for key in required_keys:
            assert key in result
        
        # Verify dashboard structure
        dashboard = result['dashboard']
        assert 'weeklySummary' in dashboard
        assert 'currentStatus' in dashboard
        assert 'topHighlights' in dashboard
        
        # Verify metadata structure
        metadata = result['metadata']
        assert 'dataQuality' in metadata
        assert 'confidenceScore' in metadata
        assert 'sourceDistribution' in metadata
        assert 'lastUpdated' in metadata
        
        # Verify empty arrays are present (not None)
        assert isinstance(result['recommendedActions'], list)
        assert isinstance(result['detailedAnalysis']['patterns']['timeOfDay'], list)


if __name__ == "__main__":
    pytest.main([__file__])
