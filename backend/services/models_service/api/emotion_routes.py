# models_service/api/emotion_routes.py
"""
Centralized emotion analysis using Phi-4 via Ollama
Replaces individual transformers models in other services
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import time
import sys
import os

# Add the parent directory to the path to import ollama_integration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ollama_integration import ollama_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/emotion", tags=["emotion"])

class EmotionRequest(BaseModel):
    text: str
    language: Optional[str] = "en"
    cultural_context: Optional[Dict[str, Any]] = None

class EmotionResponse(BaseModel):
    emotion: str
    confidence: float
    reasoning: str
    processing_time_ms: float
    model_used: str
    cultural_adaptation: Optional[Dict[str, Any]] = None

class BatchEmotionRequest(BaseModel):
    texts: List[str]
    language: Optional[str] = "en"
    cultural_context: Optional[Dict[str, Any]] = None

@router.post("/analyze", response_model=EmotionResponse)
async def analyze_emotion(request: EmotionRequest) -> EmotionResponse:
    """
    Centralized emotion analysis using Phi-4 via Ollama
    Replaces transformers models in ai_event_processor
    """
    start_time = time.time()
    
    try:
        # Use Phi-4 for emotion analysis
        result = await ollama_client.analyze_emotion_via_phi4(request.text)
        
        # Add cultural adaptation if provided
        cultural_adaptation = None
        if request.cultural_context:
            cultural_adaptation = await _apply_cultural_context(
                result, request.cultural_context
            )
        
        processing_time = (time.time() - start_time) * 1000
        
        return EmotionResponse(
            emotion=result["emotion"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            processing_time_ms=processing_time,
            model_used=result["model_used"],
            cultural_adaptation=cultural_adaptation
        )
        
    except Exception as e:
        logger.error(f"Emotion analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Emotion analysis failed: {str(e)}")

@router.post("/analyze/batch", response_model=List[EmotionResponse])
async def analyze_emotions_batch(request: BatchEmotionRequest) -> List[EmotionResponse]:
    """
    Batch emotion analysis for multiple texts
    """
    results = []
    
    for text in request.texts:
        emotion_request = EmotionRequest(
            text=text,
            language=request.language,
            cultural_context=request.cultural_context
        )
        result = await analyze_emotion(emotion_request)
        results.append(result)
    
    return results

async def _apply_cultural_context(
    emotion_result: Dict[str, Any], 
    cultural_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Apply cultural context to emotion analysis
    """
    cultural_region = cultural_context.get("cultural_region", "western")
    
    # Cultural adaptations for different regions
    adaptations: Dict[str, Any] = {
        "interpretation": emotion_result["emotion"],
        "cultural_notes": [],
        "communication_suggestions": []
    }
    
    # Indian cultural context
    if "india" in cultural_region.lower():
        if emotion_result["emotion"] == "anger":
            adaptations["cultural_notes"].append(
                "In Indian culture, expressing anger directly may not be appropriate in many contexts"
            )
            adaptations["communication_suggestions"].append(
                "Consider addressing concerns with respectful dialogue"
            )
        elif emotion_result["emotion"] == "sadness":
            adaptations["cultural_notes"].append(
                "Family and community support are important in Indian culture"
            )
            adaptations["communication_suggestions"].append(
                "Sharing with trusted family or friends might be helpful"
            )
    
    # Japanese cultural context
    elif "japan" in cultural_region.lower():
        if emotion_result["emotion"] in ["anger", "frustration"]:
            adaptations["cultural_notes"].append(
                "In Japanese culture, maintaining harmony (wa) is valued"
            )
            adaptations["communication_suggestions"].append(
                "Consider indirect communication to address issues"
            )
    
    return adaptations
