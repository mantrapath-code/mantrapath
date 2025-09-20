"""
Translation API routes for Models Service using Phi-3
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
import asyncio
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response models
class TranslationRequest(BaseModel):
    text: str
    source_language: str = "auto"
    target_language: str = "en"
    context: Optional[str] = None

class TranslationResponse(BaseModel):
    success: bool
    translated_text: str
    source_language: str
    target_language: str
    confidence_score: float
    processing_time_ms: int
    engine: str = "phi3"
    error: Optional[str] = None

class LanguageDetectionRequest(BaseModel):
    text: str

class LanguageDetectionResponse(BaseModel):
    language: str
    confidence: float

class SentimentRequest(BaseModel):
    text: str
    language: str = "en"

class SentimentResponse(BaseModel):
    sentiment: str
    confidence: float

class TextGenerationRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7

class TextGenerationResponse(BaseModel):
    success: bool
    generated_text: str
    error: Optional[str] = None

# Global reference to models service components
nlp_engine_ref = None
_nlp_init_lock = asyncio.Lock()

def set_models_service(service):
    global nlp_engine_ref
    nlp_engine_ref = service

async def ensure_nlp_initialized():
    """Ensure NLPEngine is initialized; perform lazy init if needed.
    Uses an async lock to avoid concurrent initializations."""
    global nlp_engine_ref
    if nlp_engine_ref is None:
        raise HTTPException(status_code=503, detail="NLP Engine not initialized (missing reference)")
    try:
        if getattr(nlp_engine_ref, 'is_initialized', False):
            return
        async with _nlp_init_lock:
            # Double-check inside lock
            if getattr(nlp_engine_ref, 'is_initialized', False):
                return
            logger.info("🧠 Lazy-initializing NLP Engine (Phi-3) on first request...")
            init_ok = await nlp_engine_ref.initialize()
            if not init_ok or not getattr(nlp_engine_ref, 'is_initialized', False):
                logger.error("❌ NLP Engine lazy init failed")
                raise HTTPException(status_code=503, detail="NLP Engine not ready")
            logger.info("✅ NLP Engine initialized successfully (lazy)")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during NLP Engine init: {e}")
        raise HTTPException(status_code=503, detail=f"NLP Engine init error: {str(e)}")

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Translate text using Phi-3 model"""
    logger.info(f"Translation request received. nlp_engine_ref: {nlp_engine_ref}")

    # Ensure NLP engine is ready (lazy-init on demand)
    await ensure_nlp_initialized()
    
    try:
        result = await nlp_engine_ref.translate(
            text=request.text,
            source_lang=request.source_language,
            target_lang=request.target_language
        )
        
        if result.get("success", False):
            return TranslationResponse(
                success=True,
                translated_text=result["translated_text"],
                source_language=result["source_language"],
                target_language=result["target_language"],
                confidence_score=result["confidence_score"],
                processing_time_ms=result.get("processing_time_ms", 0),
                engine="phi3"
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=result.get("error", "Translation failed")
            )
            
    except Exception as e:
        logger.error(f"Translation API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(request: LanguageDetectionRequest):
    """Detect language of text using Phi-3"""
    # Ensure NLP engine is ready (lazy-init on demand)
    await ensure_nlp_initialized()
    
    try:
        result = await nlp_engine_ref.detect_language(request.text)
        return LanguageDetectionResponse(
            language=result["language"],
            confidence=result["confidence"]
        )
    except Exception as e:
        logger.error(f"Language detection API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """Analyze sentiment using Phi-3"""
    await ensure_nlp_initialized()
    
    try:
        result = await nlp_engine_ref.analyze_sentiment(
            request.text, request.language
        )
        return SentimentResponse(
            sentiment=result["sentiment"],
            confidence=result["confidence"]
        )
    except Exception as e:
        logger.error(f"Sentiment analysis API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-text", response_model=TextGenerationResponse)
async def generate_text(request: TextGenerationRequest):
    """Generate text using Phi-3"""
    await ensure_nlp_initialized()
    
    try:
        result = await nlp_engine_ref.generate_text(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        if result.get("success", False):
            return TextGenerationResponse(
                success=True,
                generated_text=result["generated_text"]
            )
        else:
            return TextGenerationResponse(
                success=False,
                generated_text="",
                error=result.get("error", "Text generation failed")
            )
            
    except Exception as e:
        logger.error(f"Text generation API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supported-languages")
async def get_supported_languages():
    """Get list of supported languages"""
    if nlp_engine_ref is None or not getattr(nlp_engine_ref, 'is_initialized', False):
        raise HTTPException(status_code=503, detail="NLP Engine not initialized")
    
    try:
        languages = nlp_engine_ref.get_supported_languages()
        return {"supported_languages": languages}
    except Exception as e:
        logger.error(f"Get supported languages API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-info")
async def get_model_info():
    """Get information about the loaded Phi-3 model"""
    if nlp_engine_ref is None or not getattr(nlp_engine_ref, 'is_initialized', False):
        raise HTTPException(status_code=503, detail="NLP Engine not initialized")
    
    try:
        info = nlp_engine_ref.get_model_info()
        return info
    except Exception as e:
        logger.error(f"Get model info API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
