"""
Speech-to-Text (STT) Routes for Models Service
Handles audio transcription using IndicWav2Vec and Whisper models
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging
import asyncio
from models.stt_engine import STTEngine
from models.model_manager import ModelManager

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/stt", tags=["speech-to-text"])

# Global instances
_stt_engine = None
_model_manager = None

async def _get_stt_engine():
    """Get or create STT engine instance"""
    global _stt_engine, _model_manager
    
    if _stt_engine is None:
        if _model_manager is None:
            _model_manager = ModelManager()
        _stt_engine = STTEngine(_model_manager)
        await _stt_engine.load_default_models()
        logger.info("✅ STT Engine initialized")
    
    return _stt_engine

@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form("auto"),
    model_preference: Optional[str] = Form(None)
) -> JSONResponse:
    """
    Transcribe audio to text using STT models
    """
    try:
        # Validate audio file
        if not audio.content_type or not audio.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="Invalid audio file type")
        
        # Read audio data
        audio_data = await audio.read()
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Get STT engine and transcribe
        stt_engine = await _get_stt_engine()
        result = await stt_engine.transcribe(audio_data, language, model_preference)
        
        if result.get("success"):
            return JSONResponse(content={
                "success": True,
                "text": result.get("text", ""),
                "language": result.get("language", language),
                "confidence": result.get("confidence", 0.0),
                "model_used": result.get("model_used", "unknown")
            })
        else:
            raise HTTPException(
                status_code=400, 
                detail=result.get("error", "Transcription failed")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STT transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.get("/languages")
async def get_supported_languages() -> JSONResponse:
    """
    Get list of supported languages for STT
    """
    try:
        stt_engine = await _get_stt_engine()
        languages = await stt_engine.get_supported_languages()
        
        return JSONResponse(content={
            "success": True,
            "languages": languages,
            "total_count": len(languages)
        })
        
    except Exception as e:
        logger.error(f"Failed to get STT languages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get languages: {str(e)}")

@router.get("/health")
async def stt_health_check() -> JSONResponse:
    """
    Health check for STT service
    """
    try:
        stt_engine = await _get_stt_engine()
        languages = await stt_engine.get_supported_languages()
        
        return JSONResponse(content={
            "status": "healthy",
            "service": "stt",
            "supported_languages": len(languages),
            "engines": ["indic_wav2vec", "whisper_fallback"]
        })
        
    except Exception as e:
        logger.error(f"STT health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "stt",
                "error": str(e)
            }
        )
