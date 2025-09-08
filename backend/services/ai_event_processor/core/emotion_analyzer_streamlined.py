# ai_event_processor/core/emotion_analyzer_streamlined.py
"""
Streamlined emotion analyzer that uses centralized models service
Removes local transformers dependencies
"""

import asyncio
import logging
import httpx
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)

class StreamlinedEmotionAnalyzer:
    """
    Emotion analyzer that uses centralized models service
    No local transformers - all analysis via models service
    """
    
    def __init__(self):
        self.models_service_url = "http://models_service:8080"  # Internal docker network
        self.use_models_service = True  # Always true now
        self.timeout = 10.0
        
        logger.info("StreamlinedEmotionAnalyzer initialized - using centralized models service")
    
    async def analyze_emotion(
        self, 
        text: str, 
        language: str = "en",
        cultural_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze emotion using centralized models service (Phi-4 via Ollama)
        """
        try:
            # Prepare request for models service
            request_data = {
                "text": text,
                "language": language,
                "cultural_context": cultural_context or {}
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.models_service_url}/api/v1/emotion/analyze",
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Convert to expected format
                    return {
                        "emotion": result["emotion"],
                        "confidence": result["confidence"],
                        "processing_time_ms": result["processing_time_ms"],
                        "language": language,
                        "has_cultural_adaptation": bool(result.get("cultural_adaptation")),
                        "cultural_adaptation": result.get("cultural_adaptation"),
                        "model_used": result["model_used"],
                        "reasoning": result.get("reasoning", ""),
                        "service_source": "models_service_ollama"
                    }
                else:
                    logger.error(f"Models service emotion analysis failed: {response.status_code}")
                    return await self._fallback_emotion_analysis(text)
                    
        except Exception as e:
            logger.error(f"Models service connection failed: {e}")
            return await self._fallback_emotion_analysis(text)
    
    async def _fallback_emotion_analysis(self, text: str) -> Dict[str, Any]:
        """
        Simple fallback emotion analysis when models service is unavailable
        """
        # Basic sentiment keywords
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["angry", "mad", "furious", "hate"]):
            emotion = "anger"
            confidence = 0.6
        elif any(word in text_lower for word in ["sad", "depressed", "crying", "grief"]):
            emotion = "sadness"
            confidence = 0.6
        elif any(word in text_lower for word in ["happy", "joy", "excited", "great"]):
            emotion = "joy"
            confidence = 0.6
        elif any(word in text_lower for word in ["scared", "afraid", "terrified", "fear"]):
            emotion = "fear"
            confidence = 0.6
        elif any(word in text_lower for word in ["surprised", "shocked", "amazed"]):
            emotion = "surprise"
            confidence = 0.6
        else:
            emotion = "neutral"
            confidence = 0.5
        
        return {
            "emotion": emotion,
            "confidence": confidence,
            "processing_time_ms": 50,
            "language": "en",
            "has_cultural_adaptation": False,
            "model_used": "fallback_keyword_based",
            "reasoning": "Fallback analysis due to models service unavailability",
            "service_source": "local_fallback"
        }
    
    async def batch_analyze_emotions(
        self, 
        texts: list[str], 
        language: str = "en",
        cultural_context: Optional[Dict[str, Any]] = None
    ) -> list[Dict[str, Any]]:
        """
        Analyze emotions for multiple texts
        """
        try:
            request_data = {
                "texts": texts,
                "language": language,
                "cultural_context": cultural_context or {}
            }
            
            async with httpx.AsyncClient(timeout=self.timeout * 2) as client:
                response = await client.post(
                    f"{self.models_service_url}/api/v1/emotion/analyze/batch",
                    json=request_data
                )
                
                if response.status_code == 200:
                    results = response.json()
                    return [
                        {
                            "emotion": result["emotion"],
                            "confidence": result["confidence"],
                            "processing_time_ms": result["processing_time_ms"],
                            "language": language,
                            "has_cultural_adaptation": bool(result.get("cultural_adaptation")),
                            "model_used": result["model_used"],
                            "service_source": "models_service_ollama"
                        }
                        for result in results
                    ]
                else:
                    logger.error(f"Batch emotion analysis failed: {response.status_code}")
                    # Fallback to individual analysis
                    results = []
                    for text in texts:
                        result = await self._fallback_emotion_analysis(text)
                        results.append(result)
                    return results
                    
        except Exception as e:
            logger.error(f"Batch emotion analysis failed: {e}")
            # Fallback to individual analysis
            results = []
            for text in texts:
                result = await self._fallback_emotion_analysis(text)
                results.append(result)
            return results
