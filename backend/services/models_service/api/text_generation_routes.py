# models_service/api/text_generation_routes.py
"""
Centralized text generation using TinyLlama directly via Transformers
Lightweight and efficient text generation for chatbot responses using TinyLlama-1.1B-Chat-v1.0
Supports GPU acceleration and response caching (in-memory + Redis) for production use
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import hashlib
import json
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/nlp", tags=["text-generation"])

# Redis client for distributed caching (optional, falls back to in-memory)
_redis_client = None
_redis_available = False

async def _get_redis_client():
    """Get or create Redis client for distributed caching"""
    global _redis_client, _redis_available
    
    if _redis_client is None and not _redis_available:
        try:
            import redis.asyncio as redis
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/4")
            _redis_client = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # Test connection
            await _redis_client.ping()
            _redis_available = True
            logger.info(f"✅ Redis caching enabled: {redis_url}")
        except Exception as e:
            logger.warning(f"⚠️  Redis not available, using in-memory cache: {e}")
            _redis_available = False
            _redis_client = None
    
    return _redis_client

class TextGenerationRequest(BaseModel):
    prompt: str
    message: Optional[str] = None  # Alternative to prompt for chatbot use
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7
    model: Optional[str] = "tinyllama"  # TinyLlama-1.1B-Chat-v1.0
    system_prompt: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    use_cache: Optional[bool] = True  # Enable response caching
    use_pipeline: Optional[bool] = False  # Use pipeline for faster inference

class TextGenerationResponse(BaseModel):
    generated_text: str
    response: Optional[str] = None  # Alias for generated_text
    model_used: str
    tokens_generated: int
    processing_time_ms: float
    success: bool
    confidence: Optional[float] = 0.85

# Global model and pipeline cache
_model = None
_tokenizer = None
_text_pipeline = None
_response_cache = {}  # Simple in-memory cache (Redis recommended for production)

def _get_cache_key(request: TextGenerationRequest) -> str:
    """Generate cache key for request"""
    cache_data = {
        "prompt": request.message or request.prompt,
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "system_prompt": request.system_prompt
    }
    return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()

async def _get_model():
    """
    Load TinyLlama model on demand
    TinyLlama-1.1B-Chat-v1.0: Lightweight and memory efficient
    
    Production Considerations:
    - Uses GPU acceleration when available (CUDA)
    - FP16 precision on GPU for 2x speedup and 50% memory reduction
    - Auto device mapping for optimal GPU utilization
    - Consider upgrading to Phi-4 for better quality in production
    """
    global _model, _tokenizer, _text_pipeline
    
    if _model is None:
        model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        logger.info(f"Loading model: {model_name}")
        
        try:
            _tokenizer = AutoTokenizer.from_pretrained(model_name)
            _model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else "cpu",
                low_cpu_mem_usage=True
            )
            
            # Initialize pipeline for faster inference (optional)
            _text_pipeline = pipeline(
                "text-generation",
                model=_model,
                tokenizer=_tokenizer,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            device = next(_model.parameters()).device
            dtype = next(_model.parameters()).dtype
            logger.info(f"✅ TinyLlama loaded successfully on {device} with dtype {dtype}")
            
        except Exception as e:
            logger.error(f"Failed to load TinyLlama model: {e}")
            raise
    
    return _model, _tokenizer, _text_pipeline

@router.post("/generate", response_model=TextGenerationResponse)
async def generate_text(request: TextGenerationRequest) -> TextGenerationResponse:
    """
    Centralized text generation using TinyLlama-1.1B-Chat-v1.0
    
    Used by chatbot service and other services needing text generation.
    Supports both prompt-based and chat-based generation with optional caching.
    
    Performance:
    - CPU: ~24-30s per request (acceptable for background processing)
    - GPU (CUDA): ~2-5s per request (recommended for real-time chat)
    - Pipeline mode: Additional 20-30% speedup for batch requests
    
    Production Recommendations:
    - Deploy on GPU-enabled infrastructure for real-time chat
    - Enable Redis caching for common queries (set use_cache=True)
    - Consider upgrading to Phi-4 for improved response quality
    """
    start_time = time.time()
    
    try:
        # Check cache first (Redis if available, otherwise in-memory)
        if request.use_cache:
            cache_key = _get_cache_key(request)
            
            # Try Redis cache first
            redis_client = await _get_redis_client()
            if redis_client is not None:
                try:
                    redis_key = f"textgen:{cache_key}"
                    cached_data = await redis_client.get(redis_key)
                    if cached_data:
                        cached_response = json.loads(cached_data)
                        cached_response["from_cache"] = True
                        cached_response["cache_type"] = "redis"
                        logger.info(f"✅ Redis cache hit for request")
                        return TextGenerationResponse(**cached_response)
                except Exception as e:
                    logger.warning(f"Redis cache lookup failed: {e}")
            
            # Fall back to in-memory cache
            if cache_key in _response_cache:
                cached_response = _response_cache[cache_key].copy()
                cached_response["from_cache"] = True
                cached_response["cache_type"] = "memory"
                logger.info(f"✅ Memory cache hit for request")
                return TextGenerationResponse(**cached_response)
        
        # Load model and pipeline
        model, tokenizer, text_pipeline = await _get_model()
        
        # Determine the user message
        user_message = request.message or request.prompt
        
        # Build messages for chat template
        messages = []
        
        # Add system prompt if provided
        if request.system_prompt:
            messages.append({"role": "user", "content": request.system_prompt})
        
        # Add user message
        messages.append({"role": "user", "content": user_message})
        
        # Use pipeline for faster inference if requested
        if request.use_pipeline and text_pipeline is not None:
            # Pipeline-based generation (faster for real-time chat)
            prompt_text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            outputs = text_pipeline(
                prompt_text,
                max_new_tokens=request.max_tokens or 256,
                temperature=request.temperature or 0.7,
                do_sample=True if request.temperature > 0 else False,
                return_full_text=False
            )
            
            generated_text = outputs[0]['generated_text'].strip()
            tokens_generated = len(tokenizer.encode(generated_text))
            
        else:
            # Traditional model.generate approach (more control)
            inputs = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(model.device)
            
            # Generate response with GPU acceleration when available
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
            
            tokens_generated = outputs.shape[-1] - inputs["input_ids"].shape[-1]
        
        processing_time = (time.time() - start_time) * 1000
        
        # Build response
        response_data = {
            "generated_text": generated_text,
            "response": generated_text,  # Alias for chatbot compatibility
            "model_used": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            "tokens_generated": tokens_generated,
            "processing_time_ms": processing_time,
            "success": True,
            "confidence": 0.85
        }
        
        # Cache response if enabled (Redis preferred, in-memory fallback)
        if request.use_cache:
            cache_key = _get_cache_key(request)
            cache_ttl = int(os.getenv("TEXT_GEN_CACHE_TTL", "3600"))  # 1 hour default
            
            # Try Redis caching first
            redis_client = await _get_redis_client()
            if redis_client is not None:
                try:
                    redis_key = f"textgen:{cache_key}"
                    await redis_client.setex(
                        redis_key,
                        cache_ttl,
                        json.dumps(response_data)
                    )
                    logger.info(f"✅ Response cached in Redis (TTL: {cache_ttl}s)")
                except Exception as e:
                    logger.warning(f"Redis cache storage failed: {e}, falling back to memory")
                    _response_cache[cache_key] = response_data
            else:
                # Fall back to in-memory cache
                _response_cache[cache_key] = response_data
                logger.info(f"✅ Response cached in memory")
        
        return TextGenerationResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

@router.get("/health")
async def check_text_generation_health():
    """
    Check if TinyLlama text generation model is healthy and responsive
    Returns model information, device type, and performance characteristics
    """
    try:
        # Quick test generation
        model, tokenizer, pipeline = await _get_model()
        
        # Simple test with chat template
        messages = [{"role": "user", "content": "Hi"}]
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(model.device)
        
        start_time = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=5,
                temperature=0.1,
                do_sample=True
            )
        test_time = (time.time() - start_time) * 1000
        
        device = str(next(model.parameters()).device)
        dtype = str(next(model.parameters()).dtype)
        
        return {
            "model_available": True,
            "model_name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            "status": "healthy",
            "device": device,
            "dtype": dtype,
            "gpu_available": torch.cuda.is_available(),
            "pipeline_available": pipeline is not None,
            "cache_enabled": True,
            "test_inference_ms": round(test_time, 2),
            "production_notes": {
                "current_performance": "24-30s CPU, 2-5s GPU",
                "recommended_upgrade": "Phi-4 for better quality",
                "caching": "In-memory (Redis recommended for production)"
            }
        }
        
    except Exception as e:
        logger.error(f"TinyLlama health check failed: {e}")
        return {
            "model_available": False,
            "status": "unhealthy", 
            "error": str(e)
        }

@router.post("/clear_cache")
async def clear_response_cache():
    """
    Clear both Redis and in-memory response caches
    """
    global _response_cache
    
    memory_cache_size = len(_response_cache)
    _response_cache.clear()
    
    redis_cleared = 0
    redis_client = await _get_redis_client()
    if redis_client is not None:
        try:
            # Clear all textgen:* keys
            cursor = 0
            while True:
                cursor, keys = await redis_client.scan(cursor, match="textgen:*", count=100)
                if keys:
                    redis_cleared += await redis_client.delete(*keys)
                if cursor == 0:
                    break
            logger.info(f"✅ Cleared {redis_cleared} Redis cache entries")
        except Exception as e:
            logger.warning(f"Failed to clear Redis cache: {e}")
    
    return {
        "success": True,
        "memory_cache_cleared": memory_cache_size,
        "redis_cache_cleared": redis_cleared,
        "message": f"Cleared {memory_cache_size} memory entries and {redis_cleared} Redis entries"
    }

@router.get("/cache_stats")
async def get_cache_stats():
    """
    Get cache statistics for monitoring
    """
    memory_size = len(_response_cache)
    
    redis_size = 0
    redis_status = "unavailable"
    redis_client = await _get_redis_client()
    if redis_client is not None:
        try:
            cursor = 0
            while True:
                cursor, keys = await redis_client.scan(cursor, match="textgen:*", count=100)
                redis_size += len(keys)
                if cursor == 0:
                    break
            redis_status = "available"
        except Exception as e:
            redis_status = f"error: {str(e)}"
    
    return {
        "memory_cache_size": memory_size,
        "redis_cache_size": redis_size,
        "redis_status": redis_status,
        "cache_ttl_seconds": int(os.getenv("TEXT_GEN_CACHE_TTL", "3600")),
        "caching_enabled": True
    }
