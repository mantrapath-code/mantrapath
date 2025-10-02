# models_service/api/emotion_routes.py
"""
Centralized emotion analysis using Phi-4 directly
Replaces Ollama dependency with lightweight Phi-4 implementation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/emotion", tags=["emotion"])

# Global model cache
_phi4_model = None
_phi4_tokenizer = None

async def _get_phi4_model():
    """Load Phi-4 model on demand"""
    global _phi4_model, _phi4_tokenizer
    
    if _phi4_model is None:
        model_name = "microsoft/phi-4"
        logger.info(f"Loading Phi-4 model for emotion analysis: {model_name}")
        
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
        logger.info("✅ Phi-4 model loaded for emotion analysis")
    
    return _phi4_model, _phi4_tokenizer

class EmotionRequest(BaseModel):
    text: str
    language: Optional[str] = "en"
    cultural_context: Optional[Dict[str, Any]] = None

class EmotionResponse(BaseModel):
    emotion: str
    confidence: float
    reasoning: str
    processing_time_ms: float
    model_used: str
    cultural_adaptation: Optional[Dict[str, Any]] = None

class BatchEmotionRequest(BaseModel):
    texts: List[str]
    language: Optional[str] = "en"
    cultural_context: Optional[Dict[str, Any]] = None

@router.post("/analyze", response_model=EmotionResponse)
async def analyze_emotion(request: EmotionRequest) -> EmotionResponse:
    """
    Centralized emotion analysis using Phi-4 directly
    Replaces Ollama dependency with direct model inference
    """
    start_time = time.time()
    
    try:
        # Load Phi-4 model
        model, tokenizer = await _get_phi4_model()
        
        # Create emotion analysis prompt
        prompt = f"""Analyze the emotion in this text and respond with only the emotion name and confidence score.

Text: "{request.text}"

Respond in this exact format:
Emotion: [emotion_name]
Confidence: [0.0-1.0]
Reasoning: [brief explanation]

Possible emotions: joy, sadness, anger, fear, surprise, disgust, neutral"""

        # Generate emotion analysis
        inputs = tokenizer(prompt, return_tensors="pt")
        
        # Move inputs to same device as model
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=100,
                temperature=0.3,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True
            )
        
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove input prompt from output
        response_text = response_text[len(prompt):].strip()
        
        # Parse the response (simple parsing)
        emotion = "neutral"
        confidence = 0.5
        reasoning = "Analysis completed"
        
        # Try to extract emotion and confidence from response
        lines = response_text.split('\n')
        for line in lines:
            if line.startswith('Emotion:'):
                emotion = line.split(':', 1)[1].strip().lower()
            elif line.startswith('Confidence:'):
                try:
                    confidence = float(line.split(':', 1)[1].strip())
                except:
                    confidence = 0.5
            elif line.startswith('Reasoning:'):
                reasoning = line.split(':', 1)[1].strip()
        
        processing_time = (time.time() - start_time) * 1000
        
        return EmotionResponse(
            emotion=emotion,
            confidence=confidence,
            reasoning=reasoning,
            processing_time_ms=processing_time,
            model_used="microsoft/phi-4",
            cultural_adaptation=None
        )
        
    except Exception as e:
        logger.error(f"Emotion analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Emotion analysis failed: {str(e)}")

@router.post("/analyze/batch", response_model=List[EmotionResponse])
async def analyze_emotions_batch(request: BatchEmotionRequest) -> List[EmotionResponse]:
    """
    Batch emotion analysis for multiple texts
    """
    results = []
    
    for text in request.texts:
        emotion_request = EmotionRequest(
            text=text,
            language=request.language,
            cultural_context=request.cultural_context
        )
        result = await analyze_emotion(emotion_request)
        results.append(result)
    
    return results

async def _apply_cultural_context(
    emotion_result: Dict[str, Any], 
    cultural_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Apply cultural context to emotion analysis
    """
    cultural_region = cultural_context.get("cultural_region", "western")
    
    # Cultural adaptations for different regions
    adaptations: Dict[str, Any] = {
        "interpretation": emotion_result["emotion"],
        "cultural_notes": [],
        "communication_suggestions": []
    }
    
    # Indian cultural context
    if "india" in cultural_region.lower():
        if emotion_result["emotion"] == "anger":
            adaptations["cultural_notes"].append(
                "In Indian culture, expressing anger directly may not be appropriate in many contexts"
            )
            adaptations["communication_suggestions"].append(
                "Consider addressing concerns with respectful dialogue"
            )
        elif emotion_result["emotion"] == "sadness":
            adaptations["cultural_notes"].append(
                "Family and community support are important in Indian culture"
            )
            adaptations["communication_suggestions"].append(
                "Sharing with trusted family or friends might be helpful"
            )
    
    # Japanese cultural context
    elif "japan" in cultural_region.lower():
        if emotion_result["emotion"] in ["anger", "frustration"]:
            adaptations["cultural_notes"].append(
                "In Japanese culture, maintaining harmony (wa) is valued"
            )
            adaptations["communication_suggestions"].append(
                "Consider indirect communication to address issues"
            )
    
    return adaptations
