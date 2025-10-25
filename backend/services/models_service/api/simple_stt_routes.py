"""
Simple STT Routes - Mock implementation without complex dependencies
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/stt", tags=["speech-to-text"])

@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form("auto"),
    model_preference: Optional[str] = Form(None)
) -> JSONResponse:
    """
    Mock transcription endpoint
    """
    try:
        # Validate audio file
        if not audio.content_type or not audio.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="Invalid audio file type")
        
        # Read audio data
        audio_data = await audio.read()
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Mock transcription based on language
        mock_transcriptions = {
            "hi": "नमस्ते, यह एक परीक्षण संदेश है",
            "bn": "নমস্কার, এটি একটি পরীক্ষার বার্তা",
            "te": "నమస్కారం, ఇది ఒక పరీక్ష సందేశం",
            "ta": "வணக்கம், இது ஒரு சோதனை செய்தி",
            "en": "Hello, this is a test message",
            "auto": "Hello, this is a test message"
        }
        
        text = mock_transcriptions.get(language, "Mock transcription result")
        
        return JSONResponse(content={
            "success": True,
            "text": text,
            "language": language,
            "confidence": 0.9,
            "model_used": f"mock_stt_{language}"
        })
            
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
    languages = ["hi", "bn", "te", "ta", "mr", "gu", "kn", "ml", "pa", "or", "as", "ur", "en"]
    
    return JSONResponse(content={
        "success": True,
        "languages": languages,
        "total_count": len(languages)
    })

@router.get("/health")
async def stt_health_check() -> JSONResponse:
    """
    Health check for STT service
    """
    return JSONResponse(content={
        "status": "healthy",
        "service": "stt",
        "supported_languages": 13,
        "engines": ["mock_stt"]
    })
