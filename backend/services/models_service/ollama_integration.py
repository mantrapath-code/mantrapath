# models_service/ollama_integration.py
"""
Ollama Integration for Models Service
Replaces transformers-based text generation with Ollama backend
"""

import logging
import os
import httpx
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class OllamaClient:
    """Centralized Ollama client for all text generation needs"""
    
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
        self.default_model = "phi4"
        
    async def generate_text(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate text using Ollama instead of transformers"""
        model = model or self.default_model
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "generated_text": result.get("response", ""),
                        "model_used": model,
                        "tokens_generated": len(result.get("response", "").split()),
                        "success": True
                    }
                else:
                    logger.error(f"Ollama generation failed: {response.status_code}")
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Ollama client error: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_emotion_via_phi4(self, text: str) -> Dict[str, Any]:
        """Use Phi-4 for emotion analysis instead of separate emotion models"""
        prompt = f"""Analyze the emotion in this text and respond in JSON format:

Text: "{text}"

Respond with only a JSON object like this:
{{"emotion": "anger|joy|sadness|fear|surprise|disgust|neutral", "confidence": 0.85, "reasoning": "brief explanation"}}"""

        result = await self.generate_text(prompt, temperature=0.3)
        
        if result["success"]:
            try:
                # Parse JSON response from Phi-4
                response_text = result["generated_text"].strip()
                # Find JSON in response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_text = response_text[json_start:json_end]
                    emotion_data = json.loads(json_text)
                    return {
                        "emotion": emotion_data.get("emotion", "neutral"),
                        "confidence": emotion_data.get("confidence", 0.5),
                        "reasoning": emotion_data.get("reasoning", ""),
                        "processing_time_ms": 100,  # Placeholder
                        "model_used": "phi4_via_ollama"
                    }
            except json.JSONDecodeError:
                logger.warning("Failed to parse Phi-4 emotion response as JSON")
        
        # Fallback to neutral
        return {
            "emotion": "neutral",
            "confidence": 0.5,
            "reasoning": "Analysis failed, defaulting to neutral",
            "processing_time_ms": 100,
            "model_used": "phi4_via_ollama_fallback"
        }
    
    async def translate_via_phi4(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str
    ) -> Dict[str, Any]:
        """Use Phi-4 for translation instead of IndicTrans2"""
        
        # Language code mapping
        lang_names = {
            "en": "English", "hi": "Hindi", "bn": "Bengali", "ta": "Tamil",
            "te": "Telugu", "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada",
            "ml": "Malayalam", "pa": "Punjabi", "or": "Odia", "as": "Assamese",
            "ur": "Urdu", "ne": "Nepali", "sa": "Sanskrit", "es": "Spanish",
            "fr": "French", "de": "German", "it": "Italian", "pt": "Portuguese",
            "ru": "Russian", "zh": "Chinese", "ja": "Japanese", "ko": "Korean",
            "ar": "Arabic", "tr": "Turkish", "nl": "Dutch", "sv": "Swedish"
        }
        
        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)
        
        prompt = f"""Translate the following text from {source_name} to {target_name}. 
Provide only the translation, maintaining the original meaning and cultural context.

Text to translate: "{text}"

Translation:"""

        result = await self.generate_text(prompt, temperature=0.2)
        
        if result["success"]:
            translation = result["generated_text"].strip()
            # Remove any prefix like "Translation:" if present
            if translation.lower().startswith("translation:"):
                translation = translation[12:].strip()
            
            return {
                "translated_text": translation,
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence_score": 0.85,  # Phi-4 is generally reliable
                "model_used": "phi4_via_ollama",
                "method": "neural_translation"
            }
        
        return {
            "translated_text": text,  # Fallback to original
            "source_language": source_lang,
            "target_language": target_lang,
            "confidence_score": 0.0,
            "model_used": "phi4_via_ollama_fallback",
            "method": "fallback",
            "error": result.get("error", "Translation failed")
        }

# Global client instance
ollama_client = OllamaClient()
