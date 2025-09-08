"""
MantraPath Translation Service
Clean, efficient translation service with Indian language focus
"""
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

from engines.phi3_enhanced_coordinator import Phi3EnhancedTranslationCoordinator as TranslationCoordinator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="MantraPath Translation Service",
    description="Translation service with focus on Indian regional languages",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global coordinator instance
coordinator = None

@app.on_event("startup")
async def startup_event():
    """Initialize translation coordinator"""
    global coordinator
    coordinator = TranslationCoordinator()
    await coordinator.initialize()
    logger.info("Translation service started successfully")

# Request/Response models
class TranslationRequest(BaseModel):
    text: str
    source_language: str = "auto"
    target_language: str
    domain: Optional[str] = None

class TranslationResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
    confidence_score: float
    engine: str
    processing_time_ms: Optional[int] = 0
    cache_hit: Optional[bool] = False

class LanguagesResponse(BaseModel):
    supported_languages: List[str]
    indian_languages: List[str]

class LanguageDetectionRequest(BaseModel):
    text: str

class LanguageDetectionResponse(BaseModel):
    detected_language: str
    confidence: Optional[float] = None

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Translate text using the best available engine"""
    try:
        if not coordinator:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        result = await coordinator.translate(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            domain=request.domain
        )
        
        return TranslationResponse(
            translated_text=result.translated_text,
            source_language=result.source_language,
            target_language=result.target_language,
            confidence_score=result.confidence_score,
            engine=result.engine,
            processing_time_ms=getattr(result, 'processing_time_ms', 0),
            cache_hit=getattr(result, 'cache_hit', False)
        )
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(request: LanguageDetectionRequest):
    """Detect the language of the provided text"""
    try:
        if not coordinator:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        detected_lang = await coordinator.detect_language(request.text)
        
        return LanguageDetectionResponse(
            detected_language=detected_lang,
            confidence=0.8  # Default confidence for now
        )
        
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/languages", response_model=LanguagesResponse)
async def get_supported_languages():
    """Get list of supported languages"""
    try:
        if not coordinator:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        languages = coordinator.get_supported_languages()
        
        # Indian languages as defined in the coordinator
        indian_languages = [
            "hi", "bn", "ta", "te", "ml", "kn", "gu", "or", "pa", "as", "mr", "ur",
            "ne", "sd", "kok", "mai", "sat", "doi", "mni", "brx", "bh"
        ]
        
        return LanguagesResponse(
            supported_languages=languages,
            indian_languages=indian_languages
        )
        
    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API v1 endpoints for frontend compatibility
@app.post("/api/v1/translation/generate-text", response_model=TranslationResponse)
async def generate_text_v1(request: TranslationRequest):
    """Generate translated text - API v1 endpoint for frontend compatibility"""
    return await translate_text(request)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "translation_service", 
        "version": "2.0.0",
        "timestamp": str(__import__('datetime').datetime.utcnow())
    }

if __name__ == "__main__":
    import os
    port = int(os.getenv("TRANSLATION_PORT", "8010"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
