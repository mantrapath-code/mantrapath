"""
Journal Data Collector for AI Context Store
Collects journal data to build user context
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import httpx

logger = logging.getLogger(__name__)

class JournalDataCollector:
    """Collects journal data for context building"""
    
    def __init__(self):
        # Updated to canonical content-service port (8005)
        self.content_service_url = "http://content-service:8005"  # Assuming journal is part of content service
        self.timeout = 30
        
    async def collect_user_journal_data(self, user_id: str, jwt_token: str, days_back: int = 30) -> Dict[str, Any]:
        """
        Collect journal data for a user
        
        Args:
            user_id: User ID to collect data for
            jwt_token: Authentication token
            days_back: How many days back to collect data
            
        Returns:
            Dictionary containing journal context data
        """
        try:
            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get journal entries
                journal_response = await client.get(
                    f"{self.content_service_url}/api/v1/journal/entries",
                    headers=headers
                )
                
                if journal_response.status_code == 200:
                    journal_entries = journal_response.json()
                    return self._process_journal_data(journal_entries)
                else:
                    logger.warning(f"Failed to fetch journal data: {journal_response.status_code}")
                    return {}
                    
        except Exception as e:
            logger.warning(f"Error collecting journal data for user {user_id}: {e}")
            return {}
    
    def _process_journal_data(self, journal_entries: List[Dict]) -> Dict[str, Any]:
        """Process raw journal data into context format"""
        if not journal_entries:
            return {}
        
        # Sort by date (most recent first)
        sorted_entries = sorted(journal_entries, key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Extract insights
        total_entries = len(journal_entries)
        recent_entries = sorted_entries[:7]  # Last week
        
        # Extract common topics/themes
        all_text = ' '.join([entry.get('content', '') + ' ' + entry.get('title', '') for entry in journal_entries])
        themes = self._extract_themes(all_text)
        
        # Calculate writing frequency
        dates = [entry.get('created_at', '')[:10] for entry in journal_entries]
        unique_dates = len(set(dates))
        
        return {
            "total_entries": total_entries,
            "days_with_entries": unique_dates,
            "recent_entries_count": len(recent_entries),
            "latest_entry": sorted_entries[0] if sorted_entries else None,
            "common_themes": themes,
            "writing_patterns": {
                "avg_length": sum(len(entry.get('content', '')) for entry in journal_entries) / total_entries if total_entries > 0 else 0,
                "entries_this_week": len(recent_entries),
                "most_active_day": self._get_most_active_day(dates)
            },
            "sentiment_patterns": self._analyze_sentiment_patterns(journal_entries),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract themes from journal text"""
        if not text:
            return []
        
        # Simple keyword extraction
        words = text.lower().split()
        keywords = {}
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'today', 'feel', 'feeling', 'was', 'had', 'have', 'been', 'that', 'this', 'really', 'very', 'much', 'just', 'like', 'would', 'could', 'should'}
        
        for word in words:
            word = word.strip('.,!?()[]"\'')
            if len(word) > 3 and word not in common_words:
                keywords[word] = keywords.get(word, 0) + 1
        
        # Return top themes
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_keywords[:10] if count > 2]
    
    def _get_most_active_day(self, dates: List[str]) -> str:
        """Find the most active day of the week"""
        if not dates:
            return "unknown"
        
        try:
            days = {}
            for date_str in dates:
                if date_str:
                    day = datetime.fromisoformat(date_str.replace('Z', '+00:00')).strftime('%A')
                    days[day] = days.get(day, 0) + 1
            
            return max(days, key=days.get) if days else "unknown"
        except:
            return "unknown"
    
    def _analyze_sentiment_patterns(self, entries: List[Dict]) -> Dict[str, Any]:
        """Simple sentiment analysis of journal entries"""
        if not entries:
            return {}
        
        positive_words = {'happy', 'good', 'great', 'amazing', 'wonderful', 'excited', 'joy', 'love', 'excellent', 'fantastic', 'positive', 'grateful', 'thankful', 'blessed', 'accomplished'}
        negative_words = {'sad', 'bad', 'terrible', 'awful', 'angry', 'frustrated', 'disappointed', 'worried', 'anxious', 'stressed', 'overwhelmed', 'depressed', 'tired', 'exhausted'}
        
        sentiment_scores = []
        
        for entry in entries:
            content = (entry.get('content', '') + ' ' + entry.get('title', '')).lower()
            positive_count = sum(1 for word in positive_words if word in content)
            negative_count = sum(1 for word in negative_words if word in content)
            
            if positive_count + negative_count > 0:
                sentiment_score = (positive_count - negative_count) / (positive_count + negative_count)
                sentiment_scores.append(sentiment_score)
        
        if sentiment_scores:
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            return {
                "average_sentiment": round(avg_sentiment, 2),
                "sentiment_trend": "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral",
                "entries_analyzed": len(sentiment_scores)
            }
        
        return {"average_sentiment": 0, "sentiment_trend": "neutral", "entries_analyzed": 0}
