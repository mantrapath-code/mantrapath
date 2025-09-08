# models_service/api/translation_routes_ollama.py
"""
Centralized translation using Phi-4 via Ollama
Replaces IndicTrans2 models in translation_service
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import time
import sys
import os

# Add the parent directory to the path to import ollama_integration  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ollama_integration import ollama_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/translation", tags=["translation"])

class TranslationRequest(BaseModel):
    text: str
    source_language: str = "auto"
    target_language: str
    context: Optional[str] = None
    preserve_cultural_context: bool = True

class TranslationResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    cultural_notes: Optional[str] = None
    processing_time: float

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text using Phi-4 via Ollama with cultural context preservation
    
    This endpoint centralizes translation capabilities, replacing IndicTrans2
    models used in individual services with a unified Ollama-based approach.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Translating from {request.source_language} to {request.target_language}")
        
        # Use Ollama client for translation
        result = await ollama_client.translate_via_phi4(
            text=request.text,
            source_lang=request.source_language,
            target_lang=request.target_language,
            context=request.context,
            preserve_cultural_context=request.preserve_cultural_context
        )
        
        processing_time = time.time() - start_time
        
        # Extract cultural notes if preserve_cultural_context is enabled
        cultural_notes = None
        if request.preserve_cultural_context and result.get("cultural_analysis"):
            cultural_notes = result["cultural_analysis"]
        
        response = TranslationResponse(
            translated_text=result["translated_text"],
            source_language=result.get("detected_source_language", request.source_language),
            target_language=request.target_language,
            confidence=result.get("confidence", 0.85),
            cultural_notes=cultural_notes,
            processing_time=processing_time
        )
        
        logger.info(f"Translation completed in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )

@router.get("/health")
async def translation_health():
    """Health check for translation service"""
    try:
        # Test Ollama connectivity
        test_result = await ollama_client.translate_via_phi4(
            text="Hello",
            source_lang="en",
            target_lang="es",
            context=None,
            preserve_cultural_context=False
        )
        
        return {
            "status": "healthy",
            "service": "translation_via_ollama",
            "model": "phi4",
            "test_translation": test_result.get("translated_text", "Hola")
        }
    except Exception as e:
        logger.error(f"Translation health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Translation service unhealthy: {str(e)}"
        )

@router.get("/supported-languages")
async def get_supported_languages():
    """Get list of supported languages for translation"""
    return {
        "languages": {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "hi": "Hindi",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "ar": "Arabic",
            "ru": "Russian",
            "bn": "Bengali",
            "ta": "Tamil",
            "te": "Telugu",
            "mr": "Marathi",
            "gu": "Gujarati",
            "kn": "Kannada",
            "ml": "Malayalam",
            "pa": "Punjabi",
            "ur": "Urdu",
            "auto": "Auto-detect"
        },
        "note": "Phi-4 supports many languages with varying degrees of accuracy"
    }
