"""
Mood Data Collector for AI Context Store
Collects mood data from the mood service to build user context
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import httpx

logger = logging.getLogger(__name__)

class MoodDataCollector:
    """Collects mood data from mood service for context building"""
    
    def __init__(self):
        self.mood_service_url = "http://mood-service:8003"
        self.timeout = 30
        
    async def collect_user_mood_data(self, user_id: str, jwt_token: str, days_back: int = 30) -> Dict[str, Any]:
        """
        Collect mood data for a user from the mood service
        
        Args:
            user_id: User ID to collect data for
            jwt_token: Authentication token
            days_back: How many days back to collect data
            
        Returns:
            Dictionary containing mood context data
        """
        try:
            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get mood entries
                mood_response = await client.get(
                    f"{self.mood_service_url}/api/v1/mood/",
                    headers=headers
                )
                
                if mood_response.status_code == 200:
                    mood_entries = mood_response.json()
                    
                    # Get analytics
                    analytics_response = await client.get(
                        f"{self.mood_service_url}/api/v1/mood/analytics",
                        headers=headers
                    )
                    
                    analytics = {}
                    if analytics_response.status_code == 200:
                        analytics = analytics_response.json()
                    
                    return self._process_mood_data(mood_entries, analytics)
                else:
                    logger.error(f"Failed to fetch mood data: {mood_response.status_code}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error collecting mood data for user {user_id}: {e}")
            return {}
    
    def _process_mood_data(self, mood_entries: List[Dict], analytics: Dict) -> Dict[str, Any]:
        """Process raw mood data into context format"""
        if not mood_entries:
            return {}
        
        # Sort by date (most recent first)
        sorted_entries = sorted(mood_entries, key=lambda x: x['created_at'], reverse=True)
        
        # Calculate patterns
        recent_moods = [entry['mood_score'] for entry in sorted_entries[:7]]
        recent_energy = [entry['energy_level'] for entry in sorted_entries[:7]]
        recent_stress = [entry['stress_level'] for entry in sorted_entries[:7]]
        
        avg_mood = sum(recent_moods) / len(recent_moods) if recent_moods else 5
        avg_energy = sum(recent_energy) / len(recent_energy) if recent_energy else 5
        avg_stress = sum(recent_stress) / len(recent_stress) if recent_stress else 5
        
        # Determine trends
        mood_trend = "stable"
        if len(recent_moods) >= 3:
            recent_avg = sum(recent_moods[:3]) / 3
            older_avg = sum(recent_moods[3:6]) / len(recent_moods[3:6]) if len(recent_moods) > 3 else recent_avg
            if recent_avg > older_avg + 1:
                mood_trend = "improving"
            elif recent_avg < older_avg - 1:
                mood_trend = "declining"
        
        # Extract common themes from notes
        notes = [entry.get('notes', '') for entry in sorted_entries if entry.get('notes')]
        common_themes = self._extract_themes(notes)
        
        return {
            "total_entries": len(mood_entries),
            "days_tracked": len(set(entry['created_at'][:10] for entry in mood_entries)),
            "recent_average_mood": round(avg_mood, 1),
            "recent_average_energy": round(avg_energy, 1),
            "recent_average_stress": round(avg_stress, 1),
            "mood_trend": mood_trend,
            "latest_entry": sorted_entries[0] if sorted_entries else None,
            "common_themes": common_themes,
            "mood_patterns": {
                "highest_mood": max(recent_moods) if recent_moods else 0,
                "lowest_mood": min(recent_moods) if recent_moods else 0,
                "mood_variance": max(recent_moods) - min(recent_moods) if recent_moods else 0
            },
            "analytics": analytics,
            "voice_entries": len([e for e in mood_entries if 'voice_input' in e.get('context_tags', [])]),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _extract_themes(self, notes: List[str]) -> List[str]:
        """Extract common themes from mood notes"""
        if not notes:
            return []
        
        # Simple keyword extraction (could be enhanced with NLP)
        keywords = {}
        common_words = ['feeling', 'today', 'good', 'bad', 'great', 'okay', 'not', 'really', 'much', 'that']
        
        for note in notes:
            words = note.lower().split()
            for word in words:
                word = word.strip('.,!?')
                if len(word) > 3 and word not in common_words:
                    keywords[word] = keywords.get(word, 0) + 1
        
        # Return top themes
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_keywords[:5] if count > 1]
