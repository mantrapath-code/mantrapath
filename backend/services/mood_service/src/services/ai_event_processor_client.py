"""
AI Event Processor Client
Integrates with the AI Event Processor service for advanced emotion analysis
"""

import httpx
import logging
from typing import Dict, Any, Optional, List
from src.core.config import settings

logger = logging.getLogger(__name__)

class AIEventProcessorClient:
    """
    Client for interacting with the AI Event Processor service for advanced emotion analysis.
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        logger.info(f"AIEventProcessorClient initialized with base URL: {self.base_url}")

    async def analyze_emotion(
        self,
        text: str,
        user_id: str,
        language: str = "en",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze emotions using the AI Event Processor service.
        
        Args:
            text: Text to analyze for emotions
            user_id: User identifier
            language: Language code (default: "en")
            context: Additional context for analysis
            
        Returns:
            Dictionary containing emotion analysis results
        """
        if not settings.enable_ai_event_processor:
            logger.warning("AI Event Processor integration is disabled. Using local analysis.")
            return {"error": "AI Event Processor disabled"}

        try:
            payload = {
                "text": text,
                "language": language,
                "user_id": user_id,
                "context": context or {}
            }
            
            response = await self.client.post(
                "/api/v1/analyze/emotion",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"AI Event Processor analysis successful for user {user_id}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"AI Event Processor HTTP error: {e.response.status_code} - {e.response.text}")
            return {"error": f"AI Event Processor HTTP error: {e.response.text}"}
        except httpx.RequestError as e:
            logger.error(f"AI Event Processor network error: {e}")
            return {"error": f"AI Event Processor network error: {e}"}
        except Exception as e:
            logger.error(f"Unexpected error in AI Event Processor: {e}")
            return {"error": f"Unexpected error: {e}"}

    async def convert_ai_processor_result(self, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert AI Event Processor result to internal emotion analysis format.
        
        Args:
            ai_result: Raw result from AI Event Processor
            
        Returns:
            Converted result in internal format
        """
        try:
            if "error" in ai_result:
                return ai_result
                
            result_data = ai_result.get("result", {})
            
            # Extract emotion data
            primary_emotion = result_data.get("emotion", "neutral")
            confidence = result_data.get("confidence", 0.5)
            emotions = result_data.get("emotions", {})
            
            # Convert to internal format
            converted_result = {
                "primary_emotion": primary_emotion,
                "confidence_score": confidence * 100,  # Convert to percentage
                "emotions": emotions,
                "cultural_context": result_data.get("cultural_context"),
                "language": result_data.get("language", "en"),
                "processing_time_ms": result_data.get("processing_time_ms", 0),
                "has_cultural_adaptation": result_data.get("has_cultural_adaptation", False),
                "source": "ai_event_processor"
            }
            
            # Create top emotions list for compatibility
            top_emotions = []
            for emotion, score in emotions.items():
                if score > 0.1:  # Only include emotions with >10% confidence
                    sentiment = self._map_emotion_to_sentiment(emotion)
                    top_emotions.append({
                        "emotion": emotion,
                        "sentiment": sentiment,
                        "confidence": score * 100,
                        "color": self._get_sentiment_color(sentiment)
                    })
            
            # Sort by confidence
            top_emotions.sort(key=lambda x: x["confidence"], reverse=True)
            converted_result["top_emotions"] = top_emotions[:5]  # Top 5 emotions
            
            return converted_result
            
        except Exception as e:
            logger.error(f"Error converting AI Event Processor result: {e}")
            return {"error": f"Conversion error: {e}"}

    def _map_emotion_to_sentiment(self, emotion: str) -> str:
        """Map emotion to sentiment category."""
        emotion = emotion.lower()
        
        positive_emotions = [
            "joy", "happiness", "excitement", "optimism", "contentment", 
            "satisfaction", "pleasure", "enthusiasm", "cheerfulness"
        ]
        negative_emotions = [
            "sadness", "anger", "fear", "anxiety", "stress", "worry",
            "frustration", "disappointment", "grief", "despair"
        ]
        ambiguous_emotions = [
            "surprise", "confusion", "curiosity", "uncertainty"
        ]
        
        if emotion in positive_emotions:
            return "positive"
        elif emotion in negative_emotions:
            return "negative"
        elif emotion in ambiguous_emotions:
            return "ambiguous"
        else:
            return "neutral"

    def _get_sentiment_color(self, sentiment: str) -> str:
        """Get color for sentiment."""
        colors = {
            "positive": "#22c55e",
            "negative": "#ef4444", 
            "ambiguous": "#f59e0b",
            "neutral": "#6b7280"
        }
        return colors.get(sentiment, "#6b7280")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Create singleton instance
ai_event_processor_client = AIEventProcessorClient(settings.ai_event_processor_url)
