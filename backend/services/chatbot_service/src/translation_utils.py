"""
Translation utilities for Chatbot Service
Provides wrapper functions for translation operations
"""
import logging
from typing import Optional
import httpx
from src.clients.translation_service_client import TranslationServiceClient

logger = logging.getLogger(__name__)

# Initialize translation client
translation_client = TranslationServiceClient()

async def translate_text_enhanced(
    text: str,
    source_language: str,
    target_language: str,
    http_client: httpx.AsyncClient
) -> str:
    """
    Enhanced text translation with fallback handling
    
    Args:
        text: Text to translate
        source_language: Source language code
        target_language: Target language code
        http_client: HTTP client for requests
        
    Returns:
        Translated text or original text if translation fails
    """
    try:
        if not translation_client.is_enabled:
            logger.debug("Translation service is disabled, returning original text")
            return text
            
        if source_language == target_language:
            return text
            
        result = await translation_client.translate_text(
            text=text,
            source_language=source_language,
            target_language=target_language,
            cultural_adaptation=True
        )
        
        if result and result.translated_text:
            return result.translated_text
        else:
            logger.warning(f"Translation returned empty result, using original text")
            return text
            
    except Exception as e:
        logger.error(f"Error in translate_text_enhanced: {e}", exc_info=True)
        return text

async def get_simplified_response(
    language: str,
    intervention_type: str,
    http_client: httpx.AsyncClient
) -> Optional[str]:
    """
    Get a simplified response in the target language
    
    Args:
        language: Target language code
        intervention_type: Type of intervention needed
        http_client: HTTP client for requests
        
    Returns:
        Simplified response or None if not available
    """
    try:
        # Simple predefined responses as fallback
        simple_responses = {
            "hi": {
                "meditation": "ध्यान करने का समय। एक गहरी सांस लें।",
                "breathing": "गहरी सांस लें। सांस अंदर लें... बाहर छोड़ें।",
                "affirmation": "आप मजबूत हैं। आप सक्षम हैं।",
                "default": "सब ठीक हो जाएगा। एक कदम एक समय पर।"
            },
            "es": {
                "meditation": "Es hora de meditar. Respira profundo.",
                "breathing": "Respira hondo. Inhala... Exhala.",
                "affirmation": "Eres fuerte. Eres capaz.",
                "default": "Todo estará bien. Un paso a la vez."
            },
            "fr": {
                "meditation": "Il est temps de méditer. Respirez profondément.",
                "breathing": "Respirez profondément. Inspirez... Expirez.",
                "affirmation": "Vous êtes fort. Vous êtes capable.",
                "default": "Tout ira bien. Un pas à la fois."
            }
        }
        
        if language in simple_responses:
            response_dict = simple_responses[language]
            return response_dict.get(intervention_type, response_dict.get("default"))
        
        return None
        
    except Exception as e:
        logger.error(f"Error in get_simplified_response: {e}", exc_info=True)
        return None
