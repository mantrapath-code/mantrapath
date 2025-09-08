"""
Phi-4 Agent Service using Ollama
High-performance AI agent for MantraPath using locally running Phi-4 via Ollama
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any
import json
import httpx
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextGenerationRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    model: Optional[str] = "phi4"

class TextGenerationResponse(BaseModel):
    generated_text: str
    model_used: str
    tokens_generated: int
    generation_time: float
    timestamp: str

class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str
    model: Optional[str] = "phi4"

class TranslationResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
    confidence_score: float
    model_used: str
    timestamp: str

class Phi4Agent:
    """Phi-4 Agent using Ollama for local inference"""
    
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
        self.model_name = "phi4"
        self.is_initialized = False
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def initialize(self):
        """Initialize the Phi-4 agent and verify Ollama connection"""
        try:
            logger.info("Initializing Phi-4 Agent with Ollama...")
            
            # Check if Ollama is running
            response = await self.client.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models = response.json()
                available_models = [model["name"] for model in models.get("models", [])]
                logger.info(f"Available Ollama models: {available_models}")
                
                # Check if phi4 model is available
                if any("phi4" in model.lower() or "phi-4" in model.lower() for model in available_models):
                    logger.info("✅ Phi-4 model found in Ollama")
                    self.is_initialized = True
                    return True
                else:
                    logger.warning("⚠️ Phi-4 model not found. Available models: " + ", ".join(available_models))
                    # Try to use the first available model as fallback
                    if available_models:
                        self.model_name = available_models[0]
                        logger.info(f"Using fallback model: {self.model_name}")
                        self.is_initialized = True
                        return True
                    else:
                        logger.error("❌ No models available in Ollama")
                        return False
            else:
                logger.error(f"❌ Failed to connect to Ollama: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Phi-4 agent: {e}")
            return False

    async def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate text using Phi-4 via Ollama"""
        if not self.is_initialized:
            raise HTTPException(status_code=503, detail="Phi-4 agent not initialized")
        
        start_time = datetime.now()
        
        try:
            # Prepare Ollama request
            ollama_request = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            # Make request to Ollama
            response = await self.client.post(
                f"{self.ollama_url}/api/generate",
                json=ollama_request
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "")
                
                generation_time = (datetime.now() - start_time).total_seconds()
                
                return {
                    "generated_text": generated_text,
                    "model_used": self.model_name,
                    "tokens_generated": len(generated_text.split()),
                    "generation_time": generation_time,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                raise HTTPException(status_code=500, detail=f"Ollama API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Text generation error: {e}")
            raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

    async def translate(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Translate text using Phi-4 via Ollama"""
        # Create translation prompt
        prompt = f"""<|system|>
You are a professional translator. Translate the given text accurately while preserving meaning, tone, and cultural context. Only return the translated text, nothing else.
<|end|>
<|user|>
Translate this {source_lang} text to {target_lang}:
"{text}"
<|end|>
<|assistant|>
"""
        
        try:
            result = await self.generate_text(prompt, max_tokens=1000, temperature=0.3)
            translated_text = result["generated_text"].strip()
            
            return {
                "translated_text": translated_text,
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence_score": 0.9,  # Phi-4 typically has high confidence
                "model_used": self.model_name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.aclose()

# Global agent instance
phi4_agent: Optional[Phi4Agent] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global phi4_agent
    
    # Startup
    logger.info("🚀 Starting Phi-4 Agent Service...")
    
    try:
        phi4_agent = Phi4Agent()
        success = await phi4_agent.initialize()
        
        if not success:
            logger.error("❌ Failed to initialize Phi-4 agent")
            raise RuntimeError("Model initialization failed")
        
        logger.info("✅ Phi-4 Agent Service initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start Phi-4 Agent Service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Phi-4 Agent Service...")
    if phi4_agent:
        await phi4_agent.cleanup()
    logger.info("✅ Phi-4 Agent Service shutdown complete")

# FastAPI app
app = FastAPI(
    title="Phi-4 Agent Service",
    description="AI Agent Service using Phi-4 via Ollama for MantraPath",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "phi4-agent",
        "model_initialized": phi4_agent.is_initialized if phi4_agent else False,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/models")
async def get_available_models():
    """Get available models"""
    if not phi4_agent or not phi4_agent.is_initialized:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return {
        "current_model": phi4_agent.model_name,
        "ollama_url": phi4_agent.ollama_url,
        "status": "ready"
    }

@app.post("/generate", response_model=TextGenerationResponse)
async def generate_text(request: TextGenerationRequest):
    """Generate text using Phi-4"""
    if not phi4_agent or not phi4_agent.is_initialized:
        raise HTTPException(status_code=503, detail="Phi-4 agent not initialized")
    
    try:
        result = await phi4_agent.generate_text(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return TextGenerationResponse(**result)
        
    except Exception as e:
        logger.error(f"Text generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Translate text using Phi-4"""
    if not phi4_agent or not phi4_agent.is_initialized:
        raise HTTPException(status_code=503, detail="Phi-4 agent not initialized")
    
    try:
        result = await phi4_agent.translate(
            text=request.text,
            source_lang=request.source_language,
            target_lang=request.target_language
        )
        
        return TranslationResponse(**result)
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_completion(request: TextGenerationRequest):
    """Chat completion using Phi-4"""
    if not phi4_agent or not phi4_agent.is_initialized:
        raise HTTPException(status_code=503, detail="Phi-4 agent not initialized")
    
    # Format as chat prompt
    chat_prompt = f"""<|system|>
You are a helpful AI assistant for MantraPath, a mental health and wellness platform. Provide supportive, empathetic, and helpful responses.
<|end|>
<|user|>
{request.prompt}
<|end|>
<|assistant|>
"""
    
    try:
        result = await phi4_agent.generate_text(
            prompt=chat_prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return TextGenerationResponse(**result)
        
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PHI4_AGENT_PORT", "8010"))
    host = os.getenv("PHI4_AGENT_HOST", "0.0.0.0")
    
    logger.info(f"Starting Phi-4 Agent Service on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
