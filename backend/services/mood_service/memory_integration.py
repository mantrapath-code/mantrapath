"""
Memory Service Integration for Mood Service
Handles communication between Mood Service and Memory Service
"""
import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MemoryServiceIntegration:
    """Integration client for Memory Service communication"""
    
    def __init__(self, memory_service_url: str = "http://localhost:8017"):
        self.memory_service_url = memory_service_url
        self.session = None
    
    async def _get_session(self):
        """Get or create HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def send_mood_interaction(self, user_id: str, mood_data: Dict[str, Any]) -> bool:
        """Send mood entry to Memory Service for pattern analysis"""
        try:
            session = await self._get_session()
            
            interaction_data = {
                "user_id": user_id,
                "interaction_type": "mood",
                "interaction_data": {
                    "mood_score": mood_data.get("mood_score"),
                    "mood_labels": mood_data.get("mood_labels", []),
                    "stress_level": mood_data.get("stress_level"),
                    "energy_level": mood_data.get("energy_level"),
                    "context": mood_data.get("context", {}),
                    "timestamp": mood_data.get("timestamp", datetime.utcnow().isoformat())
                },
                "cultural_context": mood_data.get("cultural_context", {}),
                "metadata": {
                    "source": "mood_service",
                    "version": "v3"
                }
            }
            
            async with session.post(
                f"{self.memory_service_url}/api/v1/interactions",
                json=interaction_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    logger.info(f"Successfully sent mood interaction to memory service for user {user_id}")
                    return True
                else:
                    logger.warning(f"Failed to send mood interaction: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending mood interaction to memory service: {e}")
            return False
    
    async def get_mood_patterns(self, user_id: str, days: int = 30) -> Optional[List[Dict[str, Any]]]:
        """Retrieve mood patterns from Memory Service"""
        try:
            session = await self._get_session()
            
            async with session.get(
                f"{self.memory_service_url}/api/v1/patterns/{user_id}",
                params={"pattern_type": "mood", "days": days}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("patterns", [])
                else:
                    logger.warning(f"Failed to get mood patterns: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting mood patterns from memory service: {e}")
            return None
    
    async def get_mood_insights(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve mood-related behavioral insights from Memory Service"""
        try:
            session = await self._get_session()
            
            async with session.get(
                f"{self.memory_service_url}/api/v1/insights/{user_id}",
                params={"insight_type": "mood"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("insights", [])
                else:
                    logger.warning(f"Failed to get mood insights: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting mood insights from memory service: {e}")
            return None
    
    async def get_memory_based_recommendations(self, user_id: str, current_mood: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Get personalized recommendations based on mood history from Memory Service"""
        try:
            session = await self._get_session()
            
            request_data = {
                "user_id": user_id,
                "current_mood": current_mood,
                "recommendation_type": "mood_improvement"
            }
            
            async with session.post(
                f"{self.memory_service_url}/api/v1/recommendations",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("recommendations", [])
                else:
                    logger.warning(f"Failed to get mood recommendations: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting mood recommendations from memory service: {e}")
            return None
    
    async def check_memory_service_health(self) -> bool:
        """Check if Memory Service is available"""
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.memory_service_url}/health") as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Memory service health check failed: {e}")
            return False

# Global instance
memory_integration = MemoryServiceIntegration()

# Enhanced mood analysis with memory integration
class EnhancedMoodAnalyzer:
    """Enhanced mood analyzer with memory service integration"""
    
    def __init__(self, memory_integration: MemoryServiceIntegration):
        self.memory_integration = memory_integration
    
    async def analyze_mood_with_memory(self, user_id: str, mood_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze mood entry with historical context from memory service"""
        
        # Send current mood to memory service
        await self.memory_integration.send_mood_interaction(user_id, mood_data)
        
        # Get historical patterns
        patterns = await self.memory_integration.get_mood_patterns(user_id, days=30)
        
        # Get behavioral insights
        insights = await self.memory_integration.get_mood_insights(user_id)
        
        # Get personalized recommendations
        recommendations = await self.memory_integration.get_memory_based_recommendations(
            user_id, mood_data
        )
        
        # Combine analysis
        analysis = {
            "current_mood": mood_data,
            "historical_patterns": patterns or [],
            "behavioral_insights": insights or [],
            "personalized_recommendations": recommendations or [],
            "memory_integration_status": "active" if patterns is not None else "unavailable",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        return analysis
    
    def extract_mood_trends(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract mood trends from memory patterns"""
        if not patterns:
            return {"trend": "insufficient_data", "confidence": 0.0}
        
        # Simple trend analysis
        mood_scores = []
        for pattern in patterns:
            pattern_data = pattern.get("pattern_data", {})
            if "mood_score" in pattern_data:
                mood_scores.append(pattern_data["mood_score"])
        
        if not mood_scores:
            return {"trend": "insufficient_data", "confidence": 0.0}
        
        # Calculate trend
        if len(mood_scores) >= 3:
            recent_avg = sum(mood_scores[-3:]) / 3
            older_avg = sum(mood_scores[:-3]) / max(1, len(mood_scores) - 3)
            
            if recent_avg > older_avg + 0.5:
                trend = "improving"
            elif recent_avg < older_avg - 0.5:
                trend = "declining"
            else:
                trend = "stable"
            
            confidence = min(1.0, len(mood_scores) / 10)
        else:
            trend = "emerging"
            confidence = 0.3
        
        return {
            "trend": trend,
            "confidence": confidence,
            "data_points": len(mood_scores),
            "average_mood": sum(mood_scores) / len(mood_scores)
        }

# Global enhanced analyzer
enhanced_mood_analyzer = EnhancedMoodAnalyzer(memory_integration)
