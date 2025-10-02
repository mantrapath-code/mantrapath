# models_service/api/text_generation_routes.py
"""
Centralized text generation using Phi-4 directly via Transformers
Replaces Ollama dependency with lightweight Phi-4 implementation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

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

# Global model cache
_phi4_model = None
_phi4_tokenizer = None

async def _get_phi4_model():
    """Load Phi-4 model on demand"""
    global _phi4_model, _phi4_tokenizer
    
    if _phi4_model is None:
        model_name = "microsoft/Phi-3.5-mini-instruct"  # Using smaller model to avoid OOM
        logger.info(f"Loading Phi-4 model: {model_name}")
        
        _phi4_tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        _phi4_model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else "cpu",
            trust_remote_code=True,
            low_cpu_mem_usage=True,  # Reduce CPU memory usage during loading
            use_cache=False,  # Disable KV cache to save memory
            attn_implementation="eager"  # Use memory-efficient attention
        )
        logger.info("✅ Phi-4 model loaded successfully")
    
    return _phi4_model, _phi4_tokenizer

@router.post("/generate", response_model=TextGenerationResponse)
async def generate_text(request: TextGenerationRequest) -> TextGenerationResponse:
    """
    Centralized text generation using Phi-4 directly
    Used by chatbot service and other services needing text generation
    """
    start_time = time.time()
    
    try:
        # Load Phi-4 model
        model, tokenizer = await _get_phi4_model()
        
        # Generate text with compatible parameters
        inputs = tokenizer(request.prompt, return_tensors="pt")
        
        # Move inputs to same device as model
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=request.max_tokens or 1000,
                temperature=request.temperature or 0.7,
                do_sample=True if request.temperature > 0 else False,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True  # Explicitly enable cache
            )
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove input prompt from output
        generated_text = generated_text[len(request.prompt):].strip()
        
        processing_time = (time.time() - start_time) * 1000
        tokens_generated = len(tokenizer.encode(generated_text))
        
        return TextGenerationResponse(
            generated_text=generated_text,
            model_used="microsoft/phi-4",
            tokens_generated=tokens_generated,
            processing_time_ms=processing_time,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

@router.get("/health")
async def check_phi4_health():
    """
    Check if Phi-4 model is healthy and responsive
    """
    try:
        # Quick test generation
        model, tokenizer = await _get_phi4_model()
        
        # Simple test
        test_input = "Hello"
        inputs = tokenizer(test_input, return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=5,
                temperature=0.1,
                do_sample=True
            )
        
        return {
            "phi4_available": True,
            "model_used": "microsoft/phi-4",
            "status": "healthy",
            "device": str(next(model.parameters()).device),
            "dtype": str(next(model.parameters()).dtype)
        }
        
    except Exception as e:
        logger.error(f"Phi-4 health check failed: {e}")
        return {
            "phi4_available": False,
            "status": "unhealthy", 
            "error": str(e)
        }
