"""
Simple TTS Routes - Direct Transformers pipeline without IndicTTS wrapper
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import tempfile
import os
import io
import base64
import soundfile as sf
import numpy as np
from transformers import pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/simple-tts", tags=["simple-tts"])

# Global TTS pipeline cache
_tts_pipeline = None

class SimpleTTSRequest(BaseModel):
    text: str
    language: Optional[str] = "en"

class SimpleTTSResponse(BaseModel):
    success: bool
    audio_base64: Optional[str] = None
    sample_rate: Optional[int] = None
    duration: Optional[float] = None
    model_used: Optional[str] = None
    error: Optional[str] = None

async def _get_tts_pipeline():
    """Get TTS pipeline (lazy loading)"""
    global _tts_pipeline
    
    if _tts_pipeline is None:
        logger.info("Loading simple TTS pipeline...")
        _tts_pipeline = pipeline(
            "text-to-speech", 
            model="facebook/mms-tts-eng",  # Simple English model
            device="cpu"
        )
        logger.info("✅ Simple TTS pipeline loaded")
    
    return _tts_pipeline

@router.post("/synthesize", response_model=SimpleTTSResponse)
async def simple_synthesize(request: SimpleTTSRequest) -> SimpleTTSResponse:
    """
    Simple TTS synthesis using direct Transformers pipeline
    """
    try:
        logger.info(f"🔊 Simple TTS synthesis: {request.text[:50]}...")
        
        # Get pipeline
        pipe = await _get_tts_pipeline()
        
        # Generate audio
        result = pipe(request.text)
        audio = result["audio"]
        sr = result.get("sampling_rate", 16000)
        
        logger.info(f"Audio generated - shape: {audio.shape}, sr: {sr}")
        
        # Convert to numpy and ensure correct format
        if hasattr(audio, 'numpy'):
            audio = audio.numpy()
        elif not isinstance(audio, np.ndarray):
            audio = np.array(audio)
        
        # Squeeze to remove extra dimensions
        audio = audio.squeeze()
        
        logger.info(f"Audio processed - final shape: {audio.shape}")
        
        # Convert to WAV bytes
        with io.BytesIO() as wav_buffer:
            sf.write(wav_buffer, audio, sr, format='WAV')
            wav_bytes = wav_buffer.getvalue()
        
        # Encode as base64
        audio_base64 = base64.b64encode(wav_bytes).decode('utf-8')
        
        duration = len(audio) / sr
        
        logger.info(f"✅ Simple TTS synthesis successful - duration: {duration:.2f}s")
        
        return SimpleTTSResponse(
            success=True,
            audio_base64=audio_base64,
            sample_rate=sr,
            duration=duration,
            model_used="facebook/mms-tts-eng"
        )
        
    except Exception as e:
        logger.error(f"❌ Simple TTS synthesis failed: {e}")
        return SimpleTTSResponse(
            success=False,
            error=str(e)
        )

@router.get("/health")
async def simple_tts_health():
    """Simple TTS health check"""
    try:
        pipe = await _get_tts_pipeline()
        return {"status": "healthy", "model_loaded": pipe is not None}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}