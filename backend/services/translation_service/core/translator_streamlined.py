# translation_service/core/translator_streamlined.py
"""
Streamlined translator that uses centralized models service
Removes local IndicTrans2 dependencies
"""

import logging
import httpx
from typing import Dict, Any, Optional, List
import time

logger = logging.getLogger(__name__)

class StreamlinedTranslator:
    """
    Translator that uses centralized models service
    No local IndicTrans2 - all translation via models service (Phi-4)
    """
    
    def __init__(self):
        self.models_service_url = "http://models_service:8080"  # Internal docker network
        self.use_models_service = True  # Always true now
        self.timeout = 15.0  # Translation can take longer
        
        logger.info("StreamlinedTranslator initialized - using centralized models service")
    
    async def translate(
        self, 
        text: str, 
        source_language: str,
        target_language: str,
        context: Optional[str] = None,
        preserve_cultural_context: bool = True
    ) -> Dict[str, Any]:
        """
        Translate text using centralized models service (Phi-4 via Ollama)
        """
        try:
            # Prepare request for models service
            request_data = {
                "text": text,
                "source_language": source_language,
                "target_language": target_language,
                "context": context,
                "preserve_cultural_context": preserve_cultural_context
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.models_service_url}/api/v1/translation/translate",
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Convert to expected format
                    return {
                        "translated_text": result["translated_text"],
                        "source_language": result["source_language"],
                        "target_language": result["target_language"],
                        "confidence": result["confidence_score"],
                        "method": "phi4_ollama_neural",
                        "model_used": result["model_used"],
                        "processing_time_ms": result["processing_time_ms"],
                        "cultural_notes": result.get("cultural_notes"),
                        "service_source": "models_service_ollama",
                        "success": True
                    }
                else:
                    logger.error(f"Models service translation failed: {response.status_code}")
                    return await self._fallback_translation(text, source_language, target_language)
                    
        except Exception as e:
            logger.error(f"Models service connection failed: {e}")
            return await self._fallback_translation(text, source_language, target_language)
    
    async def batch_translate(
        self,
        texts: List[str],
        source_language: str,
        target_language: str,
        context: Optional[str] = None,
        preserve_cultural_context: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Translate multiple texts using centralized models service
        """
        try:
            request_data = {
                "texts": texts,
                "source_language": source_language,
                "target_language": target_language,
                "context": context,
                "preserve_cultural_context": preserve_cultural_context
            }
            
            async with httpx.AsyncClient(timeout=self.timeout * 2) as client:
                response = await client.post(
                    f"{self.models_service_url}/api/v1/translation/translate/batch",
                    json=request_data
                )
                
                if response.status_code == 200:
                    results = response.json()
                    return [
                        {
                            "translated_text": result["translated_text"],
                            "source_language": result["source_language"],
                            "target_language": result["target_language"],
                            "confidence": result["confidence_score"],
                            "method": "phi4_ollama_neural",
                            "model_used": result["model_used"],
                            "service_source": "models_service_ollama",
                            "success": True
                        }
                        for result in results
                    ]
                else:
                    logger.error(f"Batch translation failed: {response.status_code}")
                    # Fallback to individual translations
                    results = []
                    for text in texts:
                        result = await self._fallback_translation(text, source_language, target_language)
                        results.append(result)
                    return results
                    
        except Exception as e:
            logger.error(f"Batch translation failed: {e}")
            # Fallback to individual translations
            results = []
            for text in texts:
                result = await self._fallback_translation(text, source_language, target_language)
                results.append(result)
            return results
    
    async def _fallback_translation(
        self, 
        text: str, 
        source_language: str, 
        target_language: str
    ) -> Dict[str, Any]:
        """
        Simple fallback when models service is unavailable
        """
        # Very basic fallback - just return original with note
        return {
            "translated_text": text,  # Return original text
            "source_language": source_language,
            "target_language": target_language,
            "confidence": 0.0,
            "method": "fallback_no_translation",
            "model_used": "fallback",
            "processing_time_ms": 10,
            "cultural_notes": "Translation service unavailable - original text returned",
            "service_source": "local_fallback",
            "success": False,
            "error": "Models service unavailable"
        }
    
    async def get_supported_languages(self) -> Dict[str, List[str]]:
        """
        Get supported languages from models service
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.models_service_url}/api/v1/translation/languages"
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get supported languages: {response.status_code}")
                    return self._get_fallback_languages()
                    
        except Exception as e:
            logger.error(f"Failed to get supported languages: {e}")
            return self._get_fallback_languages()
    
    def _get_fallback_languages(self) -> Dict[str, List[str]]:
        """
        Fallback list of supported languages
        """
        return {
            "supported_languages": [
                "en", "hi", "bn", "ta", "te", "mr", "gu", "kn", "ml", "pa", 
                "or", "as", "ur", "ne", "sa", "es", "fr", "de", "it", "pt",
                "ru", "zh", "ja", "ko", "ar", "tr", "nl", "sv"
            ],
            "language_names": {
                "en": "English", "hi": "Hindi", "bn": "Bengali", "ta": "Tamil",
                "te": "Telugu", "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada",
                "ml": "Malayalam", "pa": "Punjabi", "or": "Odia", "as": "Assamese",
                "ur": "Urdu", "ne": "Nepali", "sa": "Sanskrit", "es": "Spanish",
                "fr": "French", "de": "German", "it": "Italian", "pt": "Portuguese",
                "ru": "Russian", "zh": "Chinese", "ja": "Japanese", "ko": "Korean",
                "ar": "Arabic", "tr": "Turkish", "nl": "Dutch", "sv": "Swedish"
            }
        }
