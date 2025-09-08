# models_service/api/text_generation_routes.py
"""
Centralized text generation using Ollama backend
Replaces all transformers-based text generation across services
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

router = APIRouter(prefix="/api/v1/nlp", tags=["text-generation"])

class TextGenerationRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    model: Optional[str] = "phi4"

class TextGenerationResponse(BaseModel):
    generated_text: str
    model_used: str
    tokens_generated: int
    processing_time_ms: float
    success: bool

@router.post("/generate", response_model=TextGenerationResponse)
async def generate_text(request: TextGenerationRequest) -> TextGenerationResponse:
    """
    Centralized text generation using Phi-4 via Ollama
    Used by chatbot service and other services needing text generation
    """
    start_time = time.time()
    
    try:
        # Use Ollama for text generation
        result = await ollama_client.generate_text(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens or 1000,
            temperature=request.temperature or 0.7
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        if result["success"]:
            return TextGenerationResponse(
                generated_text=result["generated_text"],
                model_used=result["model_used"],
                tokens_generated=result["tokens_generated"],
                processing_time_ms=processing_time,
                success=True
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Text generation failed: {result.get('error', 'Unknown error')}"
            )
        
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

@router.get("/health")
async def check_ollama_health():
    """
    Check if Ollama backend is healthy and responsive
    """
    try:
        # Quick test generation
        result = await ollama_client.generate_text(
            prompt="Test", 
            max_tokens=10, 
            temperature=0.1
        )
        
        return {
            "ollama_available": result["success"],
            "model_used": result.get("model_used", "unknown"),
            "status": "healthy" if result["success"] else "unhealthy",
            "error": result.get("error") if not result["success"] else None
        }
        
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        return {
            "ollama_available": False,
            "status": "unhealthy", 
            "error": str(e)
        }
