"""AI-powered emotion detection and sentiment analysis service."""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import redis
import json

from src.core.config import settings
from src.models.schemas import MoodAnalysisResult, EmotionAnalysis, SentimentType

logger = logging.getLogger(__name__)


class EmotionAnalysisService:
    """Service for emotion detection using GoEmotions model."""
    
    # Official GoEmotions sentiment groupings (from research paper)
    SENTIMENT_GROUPS = {
        "positive": ["admiration", "amusement", "approval", "caring", "desire", "excitement",
                     "gratitude", "joy", "love", "optimism", "pride", "relief"],
        "negative": ["anger", "annoyance", "disappointment", "disapproval", "disgust",
                     "embarrassment", "fear", "grief", "nervousness", "remorse", "sadness"],
        "ambiguous": ["confusion", "curiosity", "realization", "surprise"],
        "neutral": ["neutral"]
    }
    
    # Reverse mapping for quick lookup
    EMOTION_TO_SENTIMENT = {}
    
    # Color mapping for emotions
    SENTIMENT_COLORS = {
        'positive': '#22c55e',    # Green
        'negative': '#ef4444',    # Red
        'ambiguous': '#f59e0b',   # Orange
        'neutral': '#6b7280'      # Gray
    }
    
    def __init__(self):
        """Initialize the emotion analysis service."""
        # Build emotion to sentiment mapping
        for sentiment, emotions in self.SENTIMENT_GROUPS.items():
            for emotion in emotions:
                self.EMOTION_TO_SENTIMENT[emotion] = sentiment
        
        self.classifier = None
        self.redis_client = None
        self._initialized = False
    
    async def _initialize_async_components(self):
        """Initialize async components (model, redis)."""
        try:
            # Initialize Redis for caching
            if settings.redis_url:
                self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
                logger.info("Redis connection initialized for emotion analysis caching")
            
            # Initialize the emotion detection model
            await self._load_emotion_model()
            
        except Exception as e:
            logger.error(f"Failed to initialize emotion analysis components: {e}")
    
    async def _load_emotion_model(self):
        """Load the GoEmotions model."""
        if not settings.enable_emotion_detection:
            logger.info("Emotion detection disabled via settings")
            return
            
        try:
            from transformers import pipeline
            self.classifier = pipeline(
                "text-classification", 
                model=settings.emotion_model_name, 
                top_k=None
            )
            logger.info(f"Loaded emotion model: {settings.emotion_model_name}")
        except Exception as e:
            logger.error(f"Failed to load emotion model: {e}")
            self.classifier = None
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text analysis."""
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"emotion_analysis:{text_hash}"
    
    async def _get_cached_analysis(self, text: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result if available."""
        if not self.redis_client:
            return None
            
        try:
            cache_key = self._get_cache_key(text)
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
        except Exception as e:
            logger.warning(f"Failed to get cached emotion analysis: {e}")
        
        return None
    
    async def _cache_analysis(self, text: str, result: Dict[str, Any]) -> None:
        """Cache analysis result."""
        if not self.redis_client:
            return
            
        try:
            cache_key = self._get_cache_key(text)
            self.redis_client.setex(
                cache_key,
                settings.emotion_cache_ttl,
                json.dumps(result, default=str)
            )
        except Exception as e:
            logger.warning(f"Failed to cache emotion analysis: {e}")
    
    def _get_sentiment_color(self, sentiment: str) -> str:
        """Get color for sentiment visualization."""
        return self.SENTIMENT_COLORS.get(sentiment, '#6b7280')
    
    async def analyze_emotion(self, text: str) -> MoodAnalysisResult:
        """
        Analyze emotions in text using GoEmotions model.
        
        Args:
            text: Text to analyze
            
        Returns:
            MoodAnalysisResult with detected emotions and sentiments
        """
        # Lazy initialization
        if not self._initialized:
            await self._initialize_async_components()
            self._initialized = True
            
        # Input validation
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        
        if len(text) > settings.max_text_length:
            text = text[:settings.max_text_length]
        
        text = text.strip()
        
        # Check cache first
        cached_result = await self._get_cached_analysis(text)
        if cached_result:
            logger.debug("Using cached emotion analysis result")
            return MoodAnalysisResult(**cached_result)
        
        # If model not available, return neutral result
        if not self.classifier:
            logger.warning("Emotion classifier not available, returning neutral result")
            return self._get_fallback_result()
        
        try:
            # Run emotion detection
            predictions = self.classifier(text)
            
            # Handle different pipeline output formats
            if isinstance(predictions, list) and len(predictions) > 0:
                if isinstance(predictions[0], list):
                    sorted_preds = sorted(predictions[0], key=lambda x: x['score'], reverse=True)
                else:
                    sorted_preds = sorted(predictions, key=lambda x: x['score'], reverse=True)
            else:
                logger.error("Invalid prediction format from emotion model")
                return self._get_fallback_result()
            
            # Process top 5 emotions
            top_emotions = []
            for pred in sorted_preds[:5]:
                emotion = pred['label'].lower()
                sentiment = self.EMOTION_TO_SENTIMENT.get(emotion, 'neutral')
                
                emotion_analysis = EmotionAnalysis(
                    emotion=emotion,
                    sentiment=SentimentType(sentiment),
                    confidence=round(pred['score'] * 100, 1),
                    color=self._get_sentiment_color(sentiment)
                )
                top_emotions.append(emotion_analysis)
            
            # Create result
            result = MoodAnalysisResult(
                top_emotions=top_emotions,
                primary_emotion=top_emotions[0].emotion if top_emotions else 'neutral',
                primary_sentiment=top_emotions[0].sentiment if top_emotions else SentimentType.NEUTRAL,
                confidence_score=top_emotions[0].confidence if top_emotions else 0.0
            )
            
            # Cache the result
            await self._cache_analysis(text, result.model_dump())
            
            return result
            
        except Exception as e:
            logger.error(f"Emotion analysis failed: {str(e)}")
            return self._get_fallback_result()
    
    def _get_fallback_result(self) -> MoodAnalysisResult:
        """Get fallback result when analysis fails."""
        neutral_emotion = EmotionAnalysis(
            emotion="neutral",
            sentiment=SentimentType.NEUTRAL,
            confidence=50.0,
            color=self._get_sentiment_color('neutral')
        )
        
        return MoodAnalysisResult(
            top_emotions=[neutral_emotion],
            primary_emotion="neutral",
            primary_sentiment=SentimentType.NEUTRAL,
            confidence_score=50.0
        )
    
    async def get_emotion_summary(self, emotions_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate emotion summary from multiple emotion analyses.
        
        Args:
            emotions_data: List of emotion analysis results
            
        Returns:
            Summary statistics and insights
        """
        if not emotions_data:
            return {"dominant_emotion": "neutral", "distribution": {}}
        
        # Count emotion occurrences
        emotion_counts = {}
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0, "ambiguous": 0}
        
        for emotion_result in emotions_data:
            if "top_emotions" in emotion_result:
                for emotion in emotion_result["top_emotions"]:
                    emotion_name = emotion["emotion"]
                    sentiment = emotion["sentiment"]
                    
                    emotion_counts[emotion_name] = emotion_counts.get(emotion_name, 0) + 1
                    sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        # Find dominant emotion and sentiment
        dominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else "neutral"
        dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        
        return {
            "dominant_emotion": dominant_emotion,
            "dominant_sentiment": dominant_sentiment,
            "emotion_distribution": emotion_counts,
            "sentiment_distribution": sentiment_counts,
            "total_analyses": len(emotions_data)
        }
    
    def get_health_status(self) -> Dict[str, str]:
        """
        Get health status without triggering model loading.
        
        Returns:
            Dict with health status information
        """
        if not settings.enable_emotion_detection:
            return {
                "status": "disabled",
                "message": "Emotion detection disabled in settings"
            }
        
        if self.classifier is not None:
            return {
                "status": "healthy", 
                "message": "Model loaded and ready"
            }
        elif self._initialized:
            return {
                "status": "degraded",
                "message": "Initialization attempted but model not loaded"
            }
        else:
            # Check if transformers library is available
            try:
                import transformers
                return {
                    "status": "ready",
                    "message": "Model dependencies available, will load on first use (lazy loading)"
                }
            except ImportError:
                return {
                    "status": "unhealthy",
                    "message": "Missing transformers library dependency"
                }


# Global emotion analysis service instance
emotion_service = EmotionAnalysisService()