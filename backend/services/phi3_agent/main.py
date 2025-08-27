"""
Phi-3 Mini Agent Service
CPU-based implementation for local AI inference
"""

import asyncio
import logging
import os
import threading
import time
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global model and tokenizer
model = None
tokenizer = None
model_lock = threading.Lock()

class ChatCompletionRequest(BaseModel):
    model: str = "phi3-mini"
    messages: List[Dict[str, str]]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

class Phi3Agent:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = "microsoft/Phi-3-mini-4k-instruct"
        self.device = "cpu"
        self.max_length = 2048
        
    async def initialize(self):
        """Initialize the model and tokenizer"""
        try:
            logger.info(f"Loading Phi-3 Mini model on {self.device}...")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                cache_dir="/app/.cache/huggingface"
            )
            
            # Load model with CPU optimization
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=torch.float32,  # Use float32 for CPU
                device_map="cpu",
                cache_dir="/app/.cache/huggingface",
                low_cpu_mem_usage=True
            )
            
            # Set to evaluation mode
            self.model.eval()
            
            logger.info("Phi-3 Mini model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def format_chat_messages(self, messages: List[Dict[str, str]]) -> str:
        """Format messages for Phi-3 model"""
        formatted_prompt = ""
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                formatted_prompt += f"<|system|>\n{content}<|end|>\n"
            elif role == "user":
                formatted_prompt += f"<|user|>\n{content}<|end|>\n"
            elif role == "assistant":
                formatted_prompt += f"<|assistant|>\n{content}<|end|>\n"
        
        # Add assistant prompt for response
        formatted_prompt += "<|assistant|>\n"
        return formatted_prompt
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 512, 
        temperature: float = 0.7
    ) -> str:
        """Generate response using Phi-3 model"""
        
        if not self.model or not self.tokenizer:
            raise HTTPException(status_code=503, detail="Model not initialized")
        
        try:
            with model_lock:
                # Format the prompt
                formatted_prompt = self.format_chat_messages(messages)
                
                # Tokenize input
                inputs = self.tokenizer(
                    formatted_prompt,
                    return_tensors="pt",
                    truncation=True,
                    max_length=self.max_length - max_tokens
                )
                
                # Generate response
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs.input_ids,
                        max_new_tokens=max_tokens,
                        temperature=temperature,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        use_cache=True
                    )
                
                # Decode response
                response = self.tokenizer.decode(
                    outputs[0][inputs.input_ids.shape[1]:],
                    skip_special_tokens=True
                ).strip()
                
                # Clean up response
                if "<|end|>" in response:
                    response = response.split("<|end|>")[0].strip()
                
                return response
                
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

# Global agent instance
agent = Phi3Agent()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Phi-3 Agent Service...")
    success = await agent.initialize()
    if not success:
        logger.error("Failed to initialize agent")
        raise RuntimeError("Model initialization failed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Phi-3 Agent Service...")

# Create FastAPI app
app = FastAPI(
    title="Phi-3 Mini Agent",
    description="Local CPU-based Phi-3 Mini inference service",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if agent.model and agent.tokenizer:
        return {"status": "healthy", "model": "phi3-mini", "device": "cpu"}
    else:
        raise HTTPException(status_code=503, detail="Model not ready")

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""
    
    try:
        # Generate response
        response_text = await agent.generate_response(
            messages=request.messages,
            max_tokens=request.max_tokens or 512,
            temperature=request.temperature or 0.7
        )
        
        # Format response in OpenAI style
        response = ChatCompletionResponse(
            id=f"chatcmpl-{int(time.time())}",
            created=int(time.time()),
            model=request.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": len(str(request.messages)),
                "completion_tokens": len(response_text),
                "total_tokens": len(str(request.messages)) + len(response_text)
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/models")
async def list_models():
    """List available models"""
    return {
        "object": "list",
        "data": [
            {
                "id": "phi3-mini",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "microsoft"
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
