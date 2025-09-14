"""
Models Service Client for Chatbot Service
Provides NLP, sentiment analysis, and voice processing capabilities
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SentimentAnalysis:
    """Sentiment analysis result"""
    sentiment: str  # positive, negative, neutral
    confidence: float
    emotions: Dict[str, float]

@dataclass
class TextEmbedding:
    """Text embedding result"""
    embedding: List[float]
    model_used: str
    dimension: int

@dataclass
class IntentClassification:
    """Intent classification result"""
    intent: str
    confidence: float
    entities: Dict[str, Any]
    parameters: Dict[str, Any]

class ModelsServiceClient:
    """Client for communicating with Models Service"""
    
    def __init__(self):
        import os
        self.models_service_url = os.getenv("MODELS_SERVICE_URL", "http://localhost:8081")
        self.timeout = int(os.getenv("MODELS_SERVICE_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("MODELS_SERVICE_MAX_RETRIES", "3"))
        self.cache_ttl = int(os.getenv("MODELS_SERVICE_CACHE_TTL", "3600"))
        self.is_enabled = os.getenv("MODELS_SERVICE_ENABLED", "true").lower() == "true"
        
        logger.info(f"Models Service Client initialized - URL: {self.models_service_url}, Enabled: {self.is_enabled}")
    
    async def health_check(self) -> bool:
        """Check if Models Service is healthy"""
        if not self.is_enabled:
            return False
            
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.models_service_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Models Service health check failed: {e}")
            return False
    
    async def analyze_sentiment(self, text: str, language: str = "en") -> Optional[SentimentAnalysis]:
        """
        Analyze sentiment of text using Models Service
        
        Args:
            text: Text to analyze
            language: Language code (e.g., 'en', 'hi', 'bn')
            
        Returns:
            SentimentAnalysis object or None if failed
        """
        if not self.is_enabled:
            logger.debug("Models Service is disabled, skipping sentiment analysis")
            return None
            
        try:
            payload = {
                "text": text,
                "language": language
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.models_service_url}/api/v1/nlp/sentiment",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return SentimentAnalysis(
                        sentiment=data.get("sentiment", "neutral"),
                        confidence=data.get("confidence", 0.0),
                        emotions=data.get("emotions", {})
                    )
                else:
                    logger.error(f"Sentiment analysis failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return None
    
    async def get_text_embeddings(self, text: str, language: str = "en") -> Optional[TextEmbedding]:
        """
        Get text embeddings using Models Service
        
        Args:
            text: Text to embed
            language: Language code
            
        Returns:
            TextEmbedding object or None if failed
        """
        if not self.is_enabled:
            logger.debug("Models Service is disabled, skipping text embeddings")
            return None
            
        try:
            payload = {
                "text": text,
                "language": language,
                "model": "sentence-transformers"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.models_service_url}/api/v1/nlp/embeddings",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return TextEmbedding(
                        embedding=data.get("embedding", []),
                        model_used=data.get("model", "unknown"),
                        dimension=len(data.get("embedding", []))
                    )
                else:
                    logger.error(f"Text embeddings failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error in text embeddings: {e}")
            return None
    
    async def classify_intent_nlp(self, text: str, language: str = "en") -> Optional[IntentClassification]:
        """
        Classify intent using NLP models in Models Service
        
        Args:
            text: Text to classify
            language: Language code
            
        Returns:
            IntentClassification object or None if failed
        """
        if not self.is_enabled:
            logger.debug("Models Service is disabled, skipping intent classification")
            return None
            
        try:
            # Use sentiment analysis and embeddings to classify intent
            sentiment = await self.analyze_sentiment(text, language)
            embeddings = await self.get_text_embeddings(text, language)
            
            if not sentiment or not embeddings:
                return None
            
            # Simple intent classification based on sentiment and keywords
            intent = self._classify_intent_from_analysis(text, sentiment)
            
            return IntentClassification(
                intent=intent,
                confidence=sentiment.confidence,
                entities=self._extract_entities(text),
                parameters={"sentiment": sentiment.sentiment, "emotions": sentiment.emotions}
            )
            
        except Exception as e:
            logger.error(f"Error in intent classification: {e}")
            return None
    
    async def generate_tts_response(self, text: str, language: str = "en", voice: str = "default") -> Optional[bytes]:
        """
        Generate TTS response using Models Service
        
        Args:
            text: Text to convert to speech
            language: Language code (e.g., 'en', 'hi', 'bn')
            voice: Voice type to use
            
        Returns:
            Audio data as bytes or None if failed
        """
        if not self.is_enabled:
            logger.debug("Models Service is disabled, skipping TTS generation")
            return None
            
        try:
            payload = {
                "text": text,
                "language": language,
                "voice": voice
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.models_service_url}/api/v1/tts/generate",
                    json=payload
                )
                
                if response.status_code == 200:
                    return response.content
                else:
                    logger.error(f"TTS generation failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error in TTS generation: {e}")
            return None
    
    async def generate_response(
        self, 
        message: str, 
        language: str = "en", 
        context: Optional[Dict[str, Any]] = None,
        jwt_token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate AI response using Models Service
        
        Args:
            message: User message to respond to
            language: Language code (e.g., 'en', 'hi', 'bn')
            context: Additional context for response generation
            jwt_token: JWT token for authentication
            
        Returns:
            Response data or None if failed
        """
        if not self.is_enabled:
            logger.debug("Models Service is disabled, skipping response generation")
            return None
            
        try:
            payload = {
                "message": message,
                "language": language,
                "context": context or {},
                "system_prompt": "You are Mantra-Mitra, an empathetic AI wellness companion. Respond in the user's language with empathy, understanding, and practical wellness guidance."
            }
            
            headers = {}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.models_service_url}/api/v1/nlp/generate",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "response": data.get("response", ""),
                        "confidence": data.get("confidence", 0.0),
                        "model_used": data.get("model_used", "unknown"),
                        "language": language
                    }
                else:
                    logger.error(f"Response generation failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error in response generation: {e}")
            return None
    
    def _classify_intent_from_analysis(self, text: str, sentiment: SentimentAnalysis) -> str:
        """
        Classify intent based on text analysis and sentiment
        
        Args:
            text: Original text
            sentiment: Sentiment analysis result
            
        Returns:
            Intent classification string
        """
        text_lower = text.lower()
        
        # Mental health intents
        if any(word in text_lower for word in ["sad", "depressed", "anxious", "worried", "stressed"]):
            return "mental_health_support"
        elif any(word in text_lower for word in ["happy", "good", "great", "excellent", "wonderful"]):
            return "positive_mood_sharing"
        elif any(word in text_lower for word in ["mood", "feeling", "emotion", "track"]):
            return "mood_tracking"
        elif any(word in text_lower for word in ["help", "support", "advice", "guidance"]):
            return "help_request"
        elif any(word in text_lower for word in ["crisis", "emergency", "harm", "suicide", "hurt"]):
            return "crisis_support"
        elif any(word in text_lower for word in ["journal", "write", "diary", "thoughts"]):
            return "journaling"
        elif any(word in text_lower for word in ["meditation", "breathe", "calm", "relax"]):
            return "mindfulness"
        else:
            return "general_conversation"
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text (simple keyword-based extraction)
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        text_lower = text.lower()
        
        # Time entities
        if "today" in text_lower:
            entities["time"] = "today"
        elif "yesterday" in text_lower:
            entities["time"] = "yesterday"
        elif "tomorrow" in text_lower:
            entities["time"] = "tomorrow"
        
        # Emotion entities
        emotions = ["happy", "sad", "angry", "anxious", "excited", "calm", "stressed", "peaceful"]
        for emotion in emotions:
            if emotion in text_lower:
                entities["emotion"] = emotion
                break
        
        # Intensity entities
        if any(word in text_lower for word in ["very", "extremely", "really", "quite"]):
            entities["intensity"] = "high"
        elif any(word in text_lower for word in ["little", "bit", "slightly", "somewhat"]):
            entities["intensity"] = "low"
        else:
            entities["intensity"] = "medium"
        
        return entities

# Global client instance
models_client = ModelsServiceClient()
