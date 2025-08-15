#!/usr/bin/env python3
"""
Debug script for unified insights aggregator
"""
import sys
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'ml_service'))

from integrations.unified_insights_aggregator import UnifiedInsightsAggregator

def test_mood_stats():
    aggregator = UnifiedInsightsAggregator()
    
    # Create a mock mood entry with proper attributes
    mock_entry = Mock()
    mock_entry.created_at = datetime.now(timezone.utc)
    mock_entry.mood_score = 7
    mock_entry.energy_level = 6
    
    # Test _gather_mood_stats with a list containing one entry
    mock_db = Mock()
    mock_query = Mock()
    mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_entry]
    mock_db.query.return_value = mock_query
    
    # Debug the conversion process
    print("Testing mood stats gathering...")
    result = aggregator._gather_mood_stats(mock_db, "test-user")
    print("Result:", result)
    
    # Test full aggregation
    print("\nTesting full aggregation...")
    full_result = aggregator.get_unified_insights(mock_db, "test-user")
    print("Dashboard score:", full_result['dashboard']['weeklySummary']['currentWeekScore'])
    print("Data quality:", full_result['metadata']['dataQuality'])

if __name__ == "__main__":
    test_mood_stats()
