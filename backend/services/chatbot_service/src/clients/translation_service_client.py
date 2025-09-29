"""
Translation Service Client for Chatbot Service
Provides cultural adaptation and multi-language translation capabilities
"""
import logging
from typing import Dict, Any, Optional, List
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TranslationResult:
    """Translation result from Translation Service"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    cultural_adaptations: List[str]

@dataclass
class CulturalContext:
    """Cultural context information"""
    region: str
    cultural_norms: Dict[str, str]
    communication_style: str
    sensitivity_factors: List[str]
    adaptation_suggestions: List[str]

@dataclass
class LanguageDetection:
    """Language detection result"""
    detected_language: str
    confidence: float
    alternative_languages: List[Dict[str, float]]

class TranslationServiceClient:
    """Client for communicating with Translation Service"""
    
    def __init__(self):
        import os
    self.translation_service_url = os.getenv("TRANSLATION_SERVICE_URL", "http://translation-service:8010")
        self.timeout = int(os.getenv("TRANSLATION_SERVICE_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("TRANSLATION_SERVICE_MAX_RETRIES", "3"))
        self.default_language = os.getenv("TRANSLATION_DEFAULT_LANGUAGE", "en")
        self.cultural_adaptation = os.getenv("TRANSLATION_CULTURAL_ADAPTATION", "true").lower() == "true"
        self.is_enabled = os.getenv("TRANSLATION_SERVICE_ENABLED", "true").lower() == "true"
        
        # Supported languages from MantraPath documentation
        self.supported_languages = {
            "en": "English",
            "hi": "Hindi", 
            "bn": "Bengali",
            "te": "Telugu",
            "ta": "Tamil",
            "ur": "Urdu",
            "gu": "Gujarati",
            "kn": "Kannada",
            "ml": "Malayalam",
            "mr": "Marathi",
            "pa": "Punjabi",
            "or": "Odia",
            "as": "Assamese",
            "ks": "Kashmiri",
            "sd": "Sindhi",
            "ne": "Nepali",
            "sa": "Sanskrit"
        }
        
        logger.info(f"Translation Service Client initialized - URL: {self.translation_service_url}, Enabled: {self.is_enabled}")
    
    async def health_check(self) -> bool:
        """Check if Translation Service is healthy"""
        if not self.is_enabled:
            return False
            
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.translation_service_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Translation Service health check failed: {e}")
            return False
    
    async def detect_language(
        self, 
        text: str,
        jwt_token: Optional[str] = None
    ) -> Optional[LanguageDetection]:
        """
        Detect language of input text
        
        Args:
            text: Text to analyze for language detection
            jwt_token: JWT token for authentication
            
        Returns:
            LanguageDetection object or None if failed
        """
        if not self.is_enabled:
            logger.debug("Translation Service is disabled, using basic language detection")
            return self._basic_language_detection(text)
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            payload = {
                "text": text
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.translation_service_url}/detect-language",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Add original text for fallback processing
                    data["original_text"] = text
                    return self._parse_language_detection(data)
                else:
                    logger.error(f"Language detection failed: {response.status_code} - {response.text}")
                    return self._basic_language_detection(text)
                    
        except Exception as e:
            logger.error(f"Error in language detection: {e}")
            return self._basic_language_detection(text)
    
    async def translate_text(
        self, 
        text: str, 
        target_language: str,
        source_language: Optional[str] = None,
        cultural_adaptation: bool = True,
        jwt_token: Optional[str] = None
    ) -> Optional[TranslationResult]:
        """
        Translate text to target language with cultural adaptation
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (auto-detect if None)
            cultural_adaptation: Apply cultural adaptations
            jwt_token: JWT token for authentication
            
        Returns:
            TranslationResult object or None if failed
        """
        if not self.is_enabled:
            logger.debug("Translation Service is disabled, returning original text")
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language=source_language or self.default_language,
                target_language=target_language,
                confidence=1.0,
                cultural_adaptations=[]
            )
            
        if target_language not in self.supported_languages:
            logger.warning(f"Unsupported target language: {target_language}")
            return None
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            payload = {
                "text": text,
                "target_language": target_language,
                "cultural_adaptation": cultural_adaptation and self.cultural_adaptation
            }
            
            if source_language:
                payload["source_language"] = source_language
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.translation_service_url}/translate",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_translation_result(data)
                else:
                    logger.error(f"Translation failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error in translation: {e}")
            return None
    
    async def get_cultural_context(
        self, 
        language: str,
        region: Optional[str] = None,
        jwt_token: Optional[str] = None
    ) -> Optional[CulturalContext]:
        """
        Get cultural context for a language/region
        
        Args:
            language: Language code
            region: Region code (optional)
            jwt_token: JWT token for authentication
            
        Returns:
            CulturalContext object or None if failed
        """
        if not self.is_enabled:
            logger.debug("Translation Service is disabled, using basic cultural context")
            return self._basic_cultural_context(language)
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            params = {"language": language}
            if region:
                params["region"] = region
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.translation_service_url}/api/cultural-context",
                    headers=headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_cultural_context(data)
                else:
                    logger.error(f"Cultural context request failed: {response.status_code} - {response.text}")
                    return self._basic_cultural_context(language)
                    
        except Exception as e:
            logger.error(f"Error getting cultural context: {e}")
            return self._basic_cultural_context(language)
    
    async def adapt_response_culturally(
        self, 
        response: str, 
        user_language: str,
        cultural_context: Optional[Dict[str, Any]] = None,
        jwt_token: Optional[str] = None
    ) -> str:
        """
        Adapt response for cultural appropriateness
        
        Args:
            response: Original response text
            user_language: User's language code
            cultural_context: Additional cultural context
            jwt_token: JWT token for authentication
            
        Returns:
            Culturally adapted response
        """
        if not self.is_enabled or not self.cultural_adaptation:
            logger.debug("Cultural adaptation is disabled, returning original response")
            return response
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            payload = {
                "text": response,
                "language": user_language,
                "context": cultural_context or {}
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response_obj = await client.post(
                    f"{self.translation_service_url}/api/cultural-adaptation",
                    headers=headers,
                    json=payload
                )
                
                if response_obj.status_code == 200:
                    data = response_obj.json()
                    return data.get("adapted_text", response)
                else:
                    logger.error(f"Cultural adaptation failed: {response_obj.status_code} - {response_obj.text}")
                    return response
                    
        except Exception as e:
            logger.error(f"Error in cultural adaptation: {e}")
            return response
    
    async def batch_translate(
        self, 
        texts: List[str], 
        target_language: str,
        source_language: Optional[str] = None,
        jwt_token: Optional[str] = None
    ) -> List[Optional[TranslationResult]]:
        """
        Translate multiple texts in batch
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language code (auto-detect if None)
            jwt_token: JWT token for authentication
            
        Returns:
            List of TranslationResult objects
        """
        if not self.is_enabled:
            logger.debug("Translation Service is disabled, returning original texts")
            return [TranslationResult(
                original_text=text,
                translated_text=text,
                source_language=source_language or self.default_language,
                target_language=target_language,
                confidence=1.0,
                cultural_adaptations=[]
            ) for text in texts]
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            payload = {
                "texts": texts,
                "target_language": target_language,
                "cultural_adaptation": self.cultural_adaptation
            }
            
            if source_language:
                payload["source_language"] = source_language
            
            async with httpx.AsyncClient(timeout=self.timeout * 2) as client:  # Longer timeout for batch
                response = await client.post(
                    f"{self.translation_service_url}/api/batch-translate",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return [self._parse_translation_result(result) for result in data.get("results", [])]
                else:
                    logger.error(f"Batch translation failed: {response.status_code} - {response.text}")
                    return [None] * len(texts)
                    
        except Exception as e:
            logger.error(f"Error in batch translation: {e}")
            return [None] * len(texts)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages"""
        return self.supported_languages.copy()
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if language is supported"""
        return language_code in self.supported_languages
    
    def _basic_language_detection(self, text: str) -> LanguageDetection:
        """Basic language detection fallback"""
        # Simple heuristic based on script detection
        text_lower = text.lower()
        
        # Hindi/Devanagari script detection
        if any('\u0900' <= char <= '\u097F' for char in text):
            return LanguageDetection(
                detected_language="hi",
                confidence=0.8,
                alternative_languages=[{"hi": 0.8}, {"ne": 0.2}]
            )
        
        # Arabic script (Urdu)
        if any('\u0600' <= char <= '\u06FF' for char in text):
            return LanguageDetection(
                detected_language="ur",
                confidence=0.8,
                alternative_languages=[{"ur": 0.8}, {"ar": 0.2}]
            )
        
        # Bengali script
        if any('\u0980' <= char <= '\u09FF' for char in text):
            return LanguageDetection(
                detected_language="bn",
                confidence=0.8,
                alternative_languages=[{"bn": 0.8}, {"as": 0.2}]
            )
        
        # Tamil script
        if any('\u0B80' <= char <= '\u0BFF' for char in text):
            return LanguageDetection(
                detected_language="ta",
                confidence=0.8,
                alternative_languages=[{"ta": 0.8}]
            )
        
        # Telugu script
        if any('\u0C00' <= char <= '\u0C7F' for char in text):
            return LanguageDetection(
                detected_language="te",
                confidence=0.8,
                alternative_languages=[{"te": 0.8}]
            )
        
        # Default to English
        return LanguageDetection(
            detected_language="en",
            confidence=0.6,
            alternative_languages=[{"en": 0.6}]
        )
    
    def _basic_cultural_context(self, language: str) -> CulturalContext:
        """Basic cultural context fallback"""
        cultural_contexts = {
            "hi": {
                "region": "India",
                "cultural_norms": {
                    "greeting": "Namaste",
                    "respect": "Use respectful language and honorifics",
                    "family": "Family relationships are highly valued"
                },
                "communication_style": "formal_respectful",
                "sensitivity_factors": ["religious_beliefs", "caste_considerations", "age_respect"],
                "adaptation_suggestions": ["Use respectful greetings", "Acknowledge family importance", "Show cultural sensitivity"]
            },
            "ur": {
                "region": "Pakistan/India",
                "cultural_norms": {
                    "greeting": "Assalam-o-Alaikum",
                    "respect": "Use formal address for elders",
                    "family": "Strong family bonds and respect for elders"
                },
                "communication_style": "formal_respectful",
                "sensitivity_factors": ["religious_practices", "gender_considerations", "elder_respect"],
                "adaptation_suggestions": ["Use Islamic greetings", "Show respect for traditions", "Be mindful of cultural values"]
            },
            "bn": {
                "region": "Bangladesh/India",
                "cultural_norms": {
                    "greeting": "Namaskar",
                    "respect": "Respect for elders and teachers",
                    "family": "Joint family system valued"
                },
                "communication_style": "warm_respectful",
                "sensitivity_factors": ["cultural_traditions", "language_pride", "family_values"],
                "adaptation_suggestions": ["Use local greetings", "Acknowledge cultural heritage", "Show family sensitivity"]
            }
        }
        
        default_context = {
            "region": "General",
            "cultural_norms": {
                "greeting": "Hello",
                "respect": "Be polite and respectful",
                "family": "Acknowledge personal relationships"
            },
            "communication_style": "friendly_professional",
            "sensitivity_factors": ["personal_beliefs", "cultural_background"],
            "adaptation_suggestions": ["Be culturally sensitive", "Use appropriate tone", "Respect individual values"]
        }
        
        context_data = cultural_contexts.get(language, default_context)
        
        return CulturalContext(
            region=context_data["region"],
            cultural_norms=context_data["cultural_norms"],
            communication_style=context_data["communication_style"],
            sensitivity_factors=context_data["sensitivity_factors"],
            adaptation_suggestions=context_data["adaptation_suggestions"]
        )
    
    def _parse_language_detection(self, data: Dict[str, Any]) -> LanguageDetection:
        """Parse language detection from API response"""
        detected_lang = data.get("detected_language", "en")
        confidence = data.get("confidence_score", data.get("confidence", 0.0))
        
        # If translation service returns "unknown", fall back to basic detection
        if detected_lang == "unknown" or confidence < 0.1:
            logger.warning(f"Translation service returned unknown/low confidence ({confidence}), using basic detection")
            return self._basic_language_detection(data.get("original_text", ""))
        
        return LanguageDetection(
            detected_language=detected_lang,
            confidence=confidence,
            alternative_languages=data.get("alternative_languages", [])
        )
    
    def _parse_translation_result(self, data: Dict[str, Any]) -> TranslationResult:
        """Parse translation result from API response"""
        return TranslationResult(
            original_text=data.get("original_text", ""),
            translated_text=data.get("translated_text", ""),
            source_language=data.get("source_language", ""),
            target_language=data.get("target_language", ""),
            confidence=data.get("confidence", 0.0),
            cultural_adaptations=data.get("cultural_adaptations", [])
        )
    
    def _parse_cultural_context(self, data: Dict[str, Any]) -> CulturalContext:
        """Parse cultural context from API response"""
        return CulturalContext(
            region=data.get("region", ""),
            cultural_norms=data.get("cultural_norms", {}),
            communication_style=data.get("communication_style", ""),
            sensitivity_factors=data.get("sensitivity_factors", []),
            adaptation_suggestions=data.get("adaptation_suggestions", [])
        )

# Global client instance
translation_service_client = TranslationServiceClient()
