# models_service/api/text_generation_routes.py
"""
Centralized text generation using Gemma-3 directly via Transformers
Lightweight and efficient text generation for chatbot responses
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/nlp", tags=["text-generation"])

class TextGenerationRequest(BaseModel):
    prompt: str
    message: Optional[str] = None  # Alternative to prompt for chatbot use
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7
    model: Optional[str] = "gemma3"
    system_prompt: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class TextGenerationResponse(BaseModel):
    generated_text: str
    response: Optional[str] = None  # Alias for generated_text
    model_used: str
    tokens_generated: int
    processing_time_ms: float
    success: bool
    confidence: Optional[float] = 0.85

# Global model cache
_gemma_model = None
_gemma_tokenizer = None

async def _get_gemma_model():
    """Load lightweight model on demand"""
    global _gemma_model, _gemma_tokenizer
    
    if _gemma_model is None:
        # Using TinyLlama - very lightweight and memory efficient
        model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        logger.info(f"Loading model: {model_name}")
        
        try:
            _gemma_tokenizer = AutoTokenizer.from_pretrained(model_name)
            _gemma_model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else "cpu",
                low_cpu_mem_usage=True
            )
            logger.info(f"✅ Model loaded successfully on {next(_gemma_model.parameters()).device}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    return _gemma_model, _gemma_tokenizer

@router.post("/generate", response_model=TextGenerationResponse)
async def generate_text(request: TextGenerationRequest) -> TextGenerationResponse:
    """
    Centralized text generation using Gemma-3 directly
    Used by chatbot service and other services needing text generation
    Supports both prompt-based and chat-based generation
    """
    start_time = time.time()
    
    try:
        # Load Gemma model
        model, tokenizer = await _get_gemma_model()
        
        # Determine the user message
        user_message = request.message or request.prompt
        
        # Build messages for chat template
        messages = []
        
        # Add system prompt if provided
        if request.system_prompt:
            messages.append({"role": "user", "content": request.system_prompt})
        
        # Add user message
        messages.append({"role": "user", "content": user_message})
        
        # Apply chat template and prepare inputs
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(model.device)
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_tokens or 256,
                temperature=request.temperature or 0.7,
                do_sample=True if request.temperature > 0 else False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        
        # Decode only the generated part (exclude input)
        generated_text = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[-1]:],
            skip_special_tokens=True
        ).strip()
        
        processing_time = (time.time() - start_time) * 1000
        tokens_generated = outputs.shape[-1] - inputs["input_ids"].shape[-1]
        
        return TextGenerationResponse(
            generated_text=generated_text,
            response=generated_text,  # Alias for chatbot compatibility
            model_used="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            tokens_generated=tokens_generated,
            processing_time_ms=processing_time,
            success=True,
            confidence=0.85
        )
        
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

@router.get("/health")
async def check_gemma_health():
    """
    Check if Gemma model is healthy and responsive
    """
    try:
        # Quick test generation
        model, tokenizer = await _get_gemma_model()
        
        # Simple test with chat template
        messages = [{"role": "user", "content": "Hi"}]
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=5,
                temperature=0.1,
                do_sample=True
            )
        
        return {
            "gemma_available": True,
            "model_used": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            "status": "healthy",
            "device": str(next(model.parameters()).device),
            "dtype": str(next(model.parameters()).dtype)
        }
        
    except Exception as e:
        logger.error(f"Gemma health check failed: {e}")
        return {
            "gemma_available": False,
            "status": "unhealthy", 
            "error": str(e)
        }
