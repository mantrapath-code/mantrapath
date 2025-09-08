"""
Models Service Client for AI Event Processor
Centralized AI model access via Models Service API
"""

import asyncio
import httpx
import structlog
from typing import Dict, Any, Optional
import os

logger = structlog.get_logger(__name__)

class ModelsServiceClient:
    """
    Client for accessing centralized Models Service
    Provides emotion analysis, sentiment analysis, and other NLP tasks
    """
    
    def __init__(self):
        self.base_url = os.getenv("MODELS_SERVICE_URL", "http://models-service:8080")
        self.timeout = float(os.getenv("MODELS_SERVICE_TIMEOUT", "30"))
        self.enabled = os.getenv("USE_MODELS_SERVICE", "true").lower() == "true"
        self.client = None
        self.is_healthy = False
        
    async def initialize(self):
        """Initialize the Models Service client"""
        if not self.enabled:
            logger.info("Models Service integration disabled")
            return False
            
        try:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
            )
            
            # Test connection
            response = await self.client.get("/health")
            if response.status_code == 200:
                self.is_healthy = True
                logger.info("✅ Models Service client initialized successfully")
                return True
            else:
                logger.warning(f"⚠️ Models Service unhealthy: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ Cannot connect to Models Service: {e}")
            return False
    
    async def close(self):
        """Close the client connection"""
        if self.client:
            await self.client.aclose()
    
    async def analyze_emotion(
        self,
        text: str,
        language: str = "en",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze emotion using Models Service
        Falls back to basic sentiment if emotion analysis unavailable
        """
        if not self.is_healthy or not self.client:
            return await self._fallback_emotion_analysis(text, language)
            
        try:
            # Try sentiment analysis first (available in Models Service)
            response = await self.client.post(
                "/api/v1/nlp/sentiment",
                json={
                    "text": text,
                    "language": language
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Convert sentiment to emotion format
                emotion_result = self._convert_sentiment_to_emotion(result)
                emotion_result.update({
                    "processing_time_ms": 50.0,  # Estimated network time
                    "language": language,
                    "has_cultural_adaptation": False,
                    "model_used": "models_service_sentiment",
                    "analysis_metadata": {
                        "source": "models_service",
                        "sentiment_result": result
                    }
                })
                
                logger.debug(f"Models Service emotion analysis completed for user {user_id}")
                return emotion_result
            else:
                logger.warning(f"Models Service sentiment analysis failed: {response.status_code}")
                return await self._fallback_emotion_analysis(text, language)
                
        except Exception as e:
            logger.warning(f"Models Service emotion analysis error: {e}")
            return await self._fallback_emotion_analysis(text, language)
    
    def _convert_sentiment_to_emotion(self, sentiment_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert sentiment analysis to emotion analysis format
        Maps sentiment to basic emotions
        """
        sentiment = sentiment_result.get("sentiment", "neutral").lower()
        confidence = sentiment_result.get("confidence", 0.5)
        
        # Map sentiment to emotions
        emotion_mapping = {
            "positive": "joy",
            "negative": "sadness", 
            "neutral": "neutral"
        }
        
        emotion = emotion_mapping.get(sentiment, "neutral")
        
        # Create emotion distribution
        emotions = {emotion: confidence}
        if emotion != "neutral":
            emotions["neutral"] = 1.0 - confidence
        
        return {
            "emotion": emotion,
            "confidence": confidence,
            "emotions": emotions,
            "cultural_context": None
        }
    
    async def _fallback_emotion_analysis(
        self,
        text: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Fallback emotion analysis when Models Service unavailable
        Uses simple keyword-based emotion detection
        """
        # Simple keyword-based emotion detection
        text_lower = text.lower()
        
        emotion_keywords = {
            "joy": ["happy", "joy", "excited", "great", "wonderful", "amazing", "love"],
            "sadness": ["sad", "depressed", "down", "upset", "disappointed", "hurt"],
            "anger": ["angry", "mad", "furious", "annoyed", "frustrated", "irritated"],
            "fear": ["scared", "afraid", "worried", "anxious", "nervous", "panic"],
            "surprise": ["surprised", "shocked", "amazed", "unexpected"],
            "disgust": ["disgusted", "revolted", "sick", "gross"]
        }
        
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = min(score / len(keywords), 1.0)
        
        if emotion_scores:
            # Get dominant emotion
            dominant_emotion = max(emotion_scores.keys(), key=lambda x: emotion_scores[x])
            confidence = emotion_scores[dominant_emotion]
        else:
            dominant_emotion = "neutral"
            confidence = 0.5
            emotion_scores = {"neutral": 0.5}
        
        return {
            "emotion": dominant_emotion,
            "confidence": confidence,
            "emotions": emotion_scores,
            "cultural_context": None,
            "processing_time_ms": 10.0,
            "language": language,
            "has_cultural_adaptation": False,
            "model_used": "fallback_keyword_detection",
            "analysis_metadata": {
                "source": "fallback",
                "method": "keyword_detection"
            }
        }
    
    async def health_check(self) -> bool:
        """Check if Models Service is healthy"""
        if not self.enabled or not self.client:
            return False
            
        try:
            response = await self.client.get("/health", timeout=5.0)
            self.is_healthy = response.status_code == 200
            return self.is_healthy
        except Exception:
            self.is_healthy = False
            return False
