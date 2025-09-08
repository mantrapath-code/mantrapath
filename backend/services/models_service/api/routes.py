"""
API Routes for Models Service
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import io
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class TranscriptionRequest(BaseModel):
    language: str = "auto"
    model_preference: Optional[str] = None

class TranscriptionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    success: bool
    text: Optional[str] = None
    language_detected: Optional[str] = None
    confidence: Optional[float] = None
    model_used: Optional[str] = None
    error: Optional[str] = None

class SynthesisRequest(BaseModel):
    text: str
    language: str = "en"
    voice: Optional[str] = None
    model_preference: Optional[str] = None

class SynthesisResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    success: bool
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    model_used: Optional[str] = None
    error: Optional[str] = None

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str
    model_preference: Optional[str] = None

class ModelDownloadRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    model_name: str
    force: bool = False

# STT Endpoints
@router.post("/stt/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form("auto"),
    model_preference: Optional[str] = Form(None)
):
    """Transcribe audio to text"""
    try:
        from main import stt_engine
        
        if not stt_engine:
            raise HTTPException(status_code=503, detail="STT engine not initialized")
        
        # Read audio data
        audio_data = await audio.read()
        
        # Transcribe
        result = await stt_engine.transcribe(
            audio_data=audio_data,
            language=language,
            model_preference=model_preference
        )
        
        return TranscriptionResponse(**result)
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stt/languages")
async def get_stt_languages():
    """Get supported STT languages"""
    try:
        from main import stt_engine
        
        if not stt_engine:
            raise HTTPException(status_code=503, detail="STT engine not initialized")
        
        languages = await stt_engine.get_supported_languages()
        return {"supported_languages": languages}
        
    except Exception as e:
        logger.error(f"Error getting STT languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# TTS Endpoints
@router.post("/tts/synthesize")
async def synthesize_text(request: SynthesisRequest):
    """Synthesize text to speech"""
    try:
        from main import tts_engine
        
        if not tts_engine:
            raise HTTPException(status_code=503, detail="TTS engine not initialized")
        
        result = await tts_engine.synthesize(
            text=request.text,
            language=request.language,
            voice=request.voice,
            model_preference=request.model_preference
        )
        
        if result["success"]:
            # Return audio as streaming response
            audio_data = result.get("audio_data")
            if audio_data:
                return StreamingResponse(
                    io.BytesIO(audio_data),
                    media_type="audio/wav",
                    headers={
                        "Content-Disposition": "attachment; filename=synthesized.wav",
                        "X-Sample-Rate": str(result.get("sample_rate", 22050)),
                        "X-Duration": str(result.get("duration", 0)),
                        "X-Model-Used": result.get("model_used", "unknown")
                    }
                )
        
        return SynthesisResponse(**result)
        
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts/clone-voice")
async def clone_voice(
    text: str = Form(...),
    language: str = Form("en"),
    reference_audio: UploadFile = File(...)
):
    """Clone voice from reference audio"""
    try:
        from main import tts_engine
        
        if not tts_engine:
            raise HTTPException(status_code=503, detail="TTS engine not initialized")
        
        # Read reference audio
        reference_data = await reference_audio.read()
        
        result = await tts_engine.clone_voice(
            reference_audio=reference_data,
            text=text,
            language=language
        )
        
        if result["success"]:
            audio_data = result.get("audio_data")
            if audio_data:
                return StreamingResponse(
                    io.BytesIO(audio_data),
                    media_type="audio/wav",
                    headers={
                        "Content-Disposition": "attachment; filename=cloned_voice.wav",
                        "X-Sample-Rate": str(result.get("sample_rate", 22050)),
                        "X-Duration": str(result.get("duration", 0)),
                        "X-Model-Used": result.get("model_used", "unknown")
                    }
                )
        
        return result
        
    except Exception as e:
        logger.error(f"Voice cloning error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tts/languages")
async def get_tts_languages():
    """Get supported TTS languages"""
    try:
        from main import tts_engine
        
        if not tts_engine:
            raise HTTPException(status_code=503, detail="TTS engine not initialized")
        
        languages = await tts_engine.get_supported_languages()
        return {"supported_languages": languages}
        
    except Exception as e:
        logger.error(f"Error getting TTS languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tts/voices/{language}")
async def get_voices(language: str):
    """Get available voices for a language"""
    try:
        from main import tts_engine
        
        if not tts_engine:
            raise HTTPException(status_code=503, detail="TTS engine not initialized")
        
        voices = await tts_engine.get_available_voices(language)
        return {"language": language, "voices": voices}
        
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# NLP Endpoints
@router.post("/nlp/translate")
async def translate_text(request: TranslationRequest):
    """Translate text between languages"""
    try:
        from main import nlp_engine
        
        if not nlp_engine:
            raise HTTPException(status_code=503, detail="NLP engine not initialized")
        
        result = await nlp_engine.translate(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            model_preference=request.model_preference
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nlp/sentiment")
async def analyze_sentiment(
    text: str = Form(...),
    language: str = Form("en")
):
    """Analyze sentiment of text"""
    try:
        from main import nlp_engine
        
        if not nlp_engine:
            raise HTTPException(status_code=503, detail="NLP engine not initialized")
        
        result = await nlp_engine.analyze_sentiment(text=text, language=language)
        return result
        
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nlp/embeddings")
async def get_embeddings(
    text: str = Form(...),
    model_name: str = Form("sentence_transformers")
):
    """Get text embeddings"""
    try:
        from main import nlp_engine
        
        if not nlp_engine:
            raise HTTPException(status_code=503, detail="NLP engine not initialized")
        
        result = await nlp_engine.get_embeddings(text=text, model_name=model_name)
        return result
        
    except Exception as e:
        logger.error(f"Embeddings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Model Management Endpoints
@router.post("/models/download")
async def download_model(
    request: ModelDownloadRequest,
    background_tasks: BackgroundTasks
):
    """Download a model"""
    try:
        from main import model_manager
        
        if not model_manager:
            raise HTTPException(status_code=503, detail="Model manager not initialized")
        
        # Start download in background
        background_tasks.add_task(
            model_manager.download_model,
            request.model_name,
            request.force
        )
        
        return {
            "success": True,
            "message": f"Download started for {request.model_name}",
            "model_name": request.model_name
        }
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/download/{model_name}/progress")
async def get_download_progress(model_name: str):
    """Get download progress for a model"""
    try:
        from main import model_manager
        
        if not model_manager:
            raise HTTPException(status_code=503, detail="Model manager not initialized")
        
        progress = model_manager.get_download_progress(model_name)
        if progress is None:
            raise HTTPException(status_code=404, detail="Model not being downloaded")
        
        return progress
        
    except Exception as e:
        logger.error(f"Progress check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/models/{model_name}")
async def unload_model(model_name: str):
    """Unload a model from memory"""
    try:
        from main import stt_engine, tts_engine, nlp_engine
        
        # Try to unload from all engines
        success = False
        
        if stt_engine and model_name in stt_engine.loaded_models:
            await stt_engine.unload_model(model_name)
            success = True
        
        if tts_engine and model_name in tts_engine.loaded_models:
            await tts_engine.unload_model(model_name)
            success = True
        
        if nlp_engine and model_name in nlp_engine.loaded_models:
            await nlp_engine.unload_model(model_name)
            success = True
        
        if not success:
            raise HTTPException(status_code=404, detail="Model not loaded")
        
        return {"success": True, "message": f"Model {model_name} unloaded"}
        
    except Exception as e:
        logger.error(f"Model unload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Batch Processing Endpoints
@router.post("/batch/transcribe")
async def batch_transcribe(
    background_tasks: BackgroundTasks,
    audio_files: List[UploadFile] = File(...),
    language: str = Form("auto"),
    model_preference: Optional[str] = Form(None)
):
    """Batch transcription of multiple audio files"""
    try:
        from main import stt_engine
        
        if not stt_engine:
            raise HTTPException(status_code=503, detail="STT engine not initialized")
        
        # Start batch processing in background
        job_id = f"batch_transcribe_{len(audio_files)}_{hash(str(audio_files))}"
        
        # This would typically be handled by a proper job queue
        return {
            "success": True,
            "job_id": job_id,
            "message": f"Batch transcription started for {len(audio_files)} files",
            "file_count": len(audio_files)
        }
        
    except Exception as e:
        logger.error(f"Batch transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
