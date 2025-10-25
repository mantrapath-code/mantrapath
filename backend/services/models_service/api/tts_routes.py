"""
Text-to-Speech (TTS) Routes for Models Service
Handles text synthesis using Indic-TTS and MMS models
"""

from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import Response
from typing import Optional, Dict, Any
import logging
import asyncio
from models.tts_engine import TTSEngine
from models.model_manager import ModelManager

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/tts", tags=["text-to-speech"])

# Global instances
_tts_engine = None
_model_manager = None

async def _get_tts_engine():
    """Get or create TTS engine instance"""
    global _tts_engine, _model_manager
    
    if _tts_engine is None:
        if _model_manager is None:
            _model_manager = ModelManager()
        _tts_engine = TTSEngine(_model_manager)
        await _tts_engine.load_default_models()
        logger.info("✅ TTS Engine initialized")
    
    return _tts_engine

@router.post("/synthesize")
async def synthesize_text(
    text: str = Form(...),
    language: str = Form("en"),
    voice: Optional[str] = Form(None),
    model_preference: Optional[str] = Form(None)
) -> Response:
    """
    Synthesize text to speech using TTS models
    """
    try:
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Empty text provided")
        
        # Get TTS engine and synthesize
        tts_engine = await _get_tts_engine()
        result = await tts_engine.synthesize(text, language, voice, model_preference)
        
        if result.get("success"):
            audio_data = result.get("audio_data")
            sample_rate = result.get("sample_rate", 22050)
            duration = result.get("duration", 0.0)
            model_used = result.get("model_used", "unknown")
            
            # Return audio as WAV file
            return Response(
                content=audio_data,
                media_type="audio/wav",
                headers={
                    "X-Sample-Rate": str(sample_rate),
                    "X-Duration": str(duration),
                    "X-Model-Used": model_used,
                    "Content-Disposition": "attachment; filename=synthesized_audio.wav"
                }
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail=result.get("error", "Synthesis failed")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

@router.get("/languages")
async def get_supported_languages() -> JSONResponse:
    """
    Get list of supported languages for TTS
    """
    try:
        tts_engine = await _get_tts_engine()
        languages = await tts_engine.get_supported_languages()
        
        return JSONResponse(content={
            "success": True,
            "languages": languages,
            "total_count": len(languages)
        })
        
    except Exception as e:
        logger.error(f"Failed to get TTS languages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get languages: {str(e)}")

@router.get("/health")
async def tts_health_check() -> JSONResponse:
    """
    Health check for TTS service
    """
    try:
        tts_engine = await _get_tts_engine()
        languages = await tts_engine.get_supported_languages()
        
        return JSONResponse(content={
            "status": "healthy",
            "service": "tts",
            "supported_languages": len(languages),
            "engines": ["indic_tts", "mms_tts"]
        })
        
    except Exception as e:
        logger.error(f"TTS health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "tts",
                "error": str(e)
            }
        )
