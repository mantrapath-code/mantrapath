"""
Anuvadini (Bhashini) Translator Engine
Integration with Indian Government's Bhashini platform for regional language translation
Free, no API key required, supports all 22 scheduled Indian languages
"""
import logging
import os
import asyncio
import httpx
import json
from typing import Dict, List, Optional, Any, Tuple
import time
from datetime import datetime, timedelta

from .base_translator import BaseTranslator, TranslationResult

logger = logging.getLogger(__name__)

class AnuvadiniTranslator(BaseTranslator):
    """
    Anuvadini (Bhashini) translator using Indian Government's free translation API
    Supports all 22 scheduled Indian languages as per the Constitution of India
    """
    
    def __init__(self, name: str = "anuvadini", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config or {})
        
        # Get configuration from config or environment variables
        self.api_key = (config.get("api_key") if config else None) or os.getenv("BHASHINI_API_KEY")
        self.user_id = (config.get("user_id") if config else None) or os.getenv("BHASHINI_USER_ID")
        
        # Bhashini API endpoints (public, no API key required)
        self.base_url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
        self.config_url = "https://meity.gov.in/bhashini/apis"
        
        # All 22 scheduled Indian languages supported by Bhashini
        self.supported_languages = {
            # Official languages of India (Hindi & English)
            'hi': 'Hindi',
            'en': 'English',
            
            # 22 Scheduled languages as per 8th Schedule of Indian Constitution
            'as': 'Assamese',     # অসমীয়া
            'bn': 'Bengali',      # বাংলা
            'gu': 'Gujarati',     # ગુજરાતી
            'kn': 'Kannada',      # ಕನ್ನಡ
            'ks': 'Kashmiri',     # کٲشُر
            'kok': 'Konkani',     # कोंकणी
            'ml': 'Malayalam',    # മലയാളം
            'mni': 'Manipuri',    # মৈতৈলোন্
            'mr': 'Marathi',      # मराठी
            'ne': 'Nepali',       # नेपाली
            'or': 'Odia',         # ଓଡ଼ିଆ
            'pa': 'Punjabi',      # ਪੰਜਾਬੀ
            'sa': 'Sanskrit',     # संस्कृत
            'sd': 'Sindhi',       # سنڌي
            'ta': 'Tamil',        # தமிழ்
            'te': 'Telugu',       # తెలుగు
            'ur': 'Urdu',         # اردو
            
            # Additional regional languages supported by Bhashini
            'brx': 'Bodo',        # बड़ो
            'doi': 'Dogri',       # डोगरी
            'mai': 'Maithili',    # मैथिली
            'sat': 'Santali',     # ᱥᱟᱱᱛᱟᱲᱤ
            
            # Common international languages for comparison
            'fr': 'French',
            'de': 'German',
            'es': 'Spanish',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ar': 'Arabic',
            'zh': 'Chinese',
            'ja': 'Japanese'
        }
        
        # Language priority mapping for best translation quality
        self.indian_languages = {
            'hi', 'bn', 'ta', 'te', 'ml', 'kn', 'gu', 'or', 'pa', 'as', 'mr', 'ur',
            'ks', 'kok', 'mni', 'ne', 'sa', 'sd', 'brx', 'doi', 'mai', 'sat'
        }
        
        # Cache for service configurations
        self.service_config_cache = {}
        self.cache_ttl = timedelta(hours=24)  # Cache configs for 24 hours
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
    async def initialize(self) -> bool:
        """Initialize the Anuvadini translator"""
        try:
            # Test connectivity to Bhashini services
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.config_url)
                if response.status_code == 200:
                    logger.info("Anuvadini/Bhashini API is accessible")
                    self.is_initialized = True
                    return True
                else:
                    logger.warning(f"Bhashini API returned status: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Failed to initialize Anuvadini translator: {str(e)}")
            
        # Still mark as initialized for offline/fallback mode
        self.is_initialized = True
        return True
    
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> TranslationResult:
        """
        Translate text using Bhashini API
        """
        start_time = time.time()
        
        # Validate language support
        if source_language not in self.supported_languages:
            return TranslationResult(
                translated_text=text,
                source_language=source_language,
                target_language=target_language,
                confidence_score=0.0,
                engine_name=self.name,
                processing_time_ms=int((time.time() - start_time) * 1000),
                metadata={"error": f"Source language {source_language} not supported"}
            )
        
        if target_language not in self.supported_languages:
            return TranslationResult(
                translated_text=text,
                source_language=source_language,
                target_language=target_language,
                confidence_score=0.0,
                engine_name=self.name,
                processing_time_ms=int((time.time() - start_time) * 1000),
                metadata={"error": f"Target language {target_language} not supported"}
            )
        
        # If source and target are the same, return original text
        if source_language == target_language:
            return TranslationResult(
                translated_text=text,
                source_language=source_language,
                target_language=target_language,
                confidence_score=1.0,
                engine_name=self.name,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        try:
            # Rate limiting
            await self._rate_limit()
            
            # Get service configuration for the language pair
            service_config = await self._get_service_config(source_language, target_language)
            
            if not service_config:
                # Fallback to basic translation mapping for common phrases
                translated_text = await self._fallback_translate(text, source_language, target_language)
                confidence = 0.6 if translated_text != text else 0.0
                
                return TranslationResult(
                    translated_text=translated_text,
                    source_language=source_language,
                    target_language=target_language,
                    confidence_score=confidence,
                    engine_name=self.name,
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    metadata={"error": "Service config not available, using fallback"}
                )
            
            # Prepare translation request
            translation_request = {
                "pipelineTasks": [
                    {
                        "taskType": "translation",
                        "config": service_config
                    }
                ],
                "inputData": {
                    "input": [{"source": text}]
                }
            }
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Add authentication if available
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            if self.user_id:
                headers["User-ID"] = self.user_id
            
            # Make translation request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    json=translation_request,
                    headers=headers
                )
                
                if response.status_code == 200:
                    result_data = response.json()
                    translated_text = self._extract_translation(result_data)
                    
                    # Calculate confidence based on response quality
                    confidence = self._calculate_confidence(text, translated_text, source_language, target_language)
                    
                    return TranslationResult(
                        translated_text=translated_text,
                        source_language=source_language,
                        target_language=target_language,
                        confidence_score=confidence,
                        engine_name=self.name,
                        processing_time_ms=int((time.time() - start_time) * 1000),
                        metadata={
                            "bhashini_response": True,
                            "service_provider": "MeitY Government of India"
                        }
                    )
                else:
                    logger.warning(f"Bhashini API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Anuvadini translation error: {str(e)}")
        
        # Fallback translation
        translated_text = await self._fallback_translate(text, source_language, target_language)
        confidence = 0.4 if translated_text != text else 0.0
        
        return TranslationResult(
            translated_text=translated_text,
            source_language=source_language,
            target_language=target_language,
            confidence_score=confidence,
            engine_name=self.name,
            processing_time_ms=int((time.time() - start_time) * 1000),
            metadata={"error": "API unavailable, using fallback"}
        )
    
    async def _rate_limit(self):
        """Implement rate limiting to respect API limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    async def _get_service_config(self, source_lang: str, target_lang: str) -> Optional[Dict[str, Any]]:
        """Get service configuration for language pair from cache or API"""
        cache_key = f"{source_lang}-{target_lang}"
        
        # Check cache first
        if cache_key in self.service_config_cache:
            config_data, timestamp = self.service_config_cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return config_data
        
        try:
            # For now, return a basic configuration
            # In production, this would fetch from Bhashini config API
            config = {
                "language": {
                    "sourceLanguage": source_lang,
                    "targetLanguage": target_lang
                },
                "serviceId": "ai4bharat/indictrans-v2-all-gpu",
                "modelId": "63e20f4f-6ade-4f98-8b05-3d58199408b5"
            }
            
            # Cache the configuration
            self.service_config_cache[cache_key] = (config, datetime.now())
            return config
            
        except Exception as e:
            logger.error(f"Failed to get service config: {str(e)}")
            return None
    
    def _extract_translation(self, response_data: Dict) -> str:
        """Extract translated text from Bhashini API response"""
        try:
            if "pipelineResponse" in response_data:
                pipeline_response = response_data["pipelineResponse"]
                if pipeline_response and len(pipeline_response) > 0:
                    output_data = pipeline_response[0].get("output", [])
                    if output_data and len(output_data) > 0:
                        return output_data[0].get("target", "")
            
            # Alternative response structure
            if "output" in response_data:
                output = response_data["output"]
                if isinstance(output, list) and len(output) > 0:
                    return output[0].get("target", "")
                elif isinstance(output, dict):
                    return output.get("target", "")
                    
        except Exception as e:
            logger.error(f"Error extracting translation from response: {str(e)}")
        
        return ""
    
    def _calculate_confidence(self, original: str, translated: str, source_lang: str, target_lang: str) -> float:
        """Calculate confidence score for translation"""
        if not translated or translated == original:
            return 0.0
        
        base_confidence = 0.85  # High confidence for Bhashini
        
        # Boost confidence for Indian language pairs (Bhashini's specialty)
        if source_lang in self.indian_languages or target_lang in self.indian_languages:
            base_confidence += 0.1
        
        # Reduce confidence for very short texts
        if len(original.strip()) < 3:
            base_confidence -= 0.2
        
        # Reduce confidence if translation looks suspicious
        if len(translated) < len(original) * 0.3 or len(translated) > len(original) * 3:
            base_confidence -= 0.15
        
        return min(max(base_confidence, 0.0), 1.0)
    
    async def _fallback_translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Fallback translation using basic dictionaries"""
        text_lower = text.lower().strip()
        
        # Common greetings and phrases
        common_phrases = {
            'en': {
                'hello': {'hi': 'नमस्ते', 'ta': 'வணக்கம்', 'te': 'నమస్కారం', 'bn': 'নমস্কার'},
                'thank you': {'hi': 'धन्यवाद', 'ta': 'நன்றி', 'te': 'ధన్యవాదాలు', 'bn': 'ধন্যবাদ'},
                'welcome': {'hi': 'स्वागत', 'ta': 'வரவேற்கிறோம்', 'te': 'స్వాగతం', 'bn': 'স্বাগতম'},
                'yes': {'hi': 'हाँ', 'ta': 'ஆம்', 'te': 'అవును', 'bn': 'হ্যাঁ'},
                'no': {'hi': 'नहीं', 'ta': 'இல்லை', 'te': 'లేదు', 'bn': 'না'},
                'good morning': {'hi': 'सुप्रभात', 'ta': 'காலை வணக்கம்', 'te': 'శుభోదయం', 'bn': 'সুপ্রভাত'},
                'good night': {'hi': 'शुभ रात्रि', 'ta': 'இனிய இரவு', 'te': 'శుభరాత్రి', 'bn': 'শুভ রাত্রি'}
            }
        }
        
        if source_lang in common_phrases and text_lower in common_phrases[source_lang]:
            if target_lang in common_phrases[source_lang][text_lower]:
                return common_phrases[source_lang][text_lower][target_lang]
        
        # Return original text if no translation found
        return text
    
    async def detect_language(self, text: str) -> str:
        """Detect language of the input text"""
        try:
            # Simple script-based detection for Indian languages
            
            # Devanagari script (Hindi, Marathi, Nepali, Sanskrit)
            if any('\u0900' <= char <= '\u097F' for char in text):
                return 'hi'  # Default to Hindi for Devanagari
            
            # Bengali script
            if any('\u0980' <= char <= '\u09FF' for char in text):
                return 'bn'
            
            # Tamil script
            if any('\u0B80' <= char <= '\u0BFF' for char in text):
                return 'ta'
            
            # Telugu script
            if any('\u0C00' <= char <= '\u0C7F' for char in text):
                return 'te'
            
            # Gujarati script
            if any('\u0A80' <= char <= '\u0AFF' for char in text):
                return 'gu'
            
            # Kannada script
            if any('\u0C80' <= char <= '\u0CFF' for char in text):
                return 'kn'
            
            # Malayalam script
            if any('\u0D00' <= char <= '\u0D7F' for char in text):
                return 'ml'
            
            # Odia script
            if any('\u0B00' <= char <= '\u0B7F' for char in text):
                return 'or'
            
            # Punjabi script (Gurmukhi)
            if any('\u0A00' <= char <= '\u0A7F' for char in text):
                return 'pa'
            
            # Arabic/Urdu script
            if any('\u0600' <= char <= '\u06FF' for char in text):
                return 'ur'
            
            # Default to English for Latin script
            return 'en'
            
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return 'en'
    
    async def health_check(self) -> bool:
        """Check if the translator is healthy"""
        try:
            # Simple test translation
            result = await self.translate("hello", "en", "hi")
            return result.confidence > 0.0
        except:
            return False
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes"""
        return list(self.supported_languages.keys())
    
    def supports_language_pair(self, source: str, target: str) -> bool:
        """Check if the engine supports the given language pair"""
        return source in self.supported_languages and target in self.supported_languages
    
    def is_indian_language(self, language_code: str) -> bool:
        """Check if language is an Indian language"""
        return language_code in self.indian_languages

    async def translate_batch(
        self,
        texts: List[str],
        source_language: str,
        target_language: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[TranslationResult]:
        """Translate multiple texts in a batch"""
        results = []
        for text in texts:
            result = await self.translate(text, source_language, target_language, domain, context)
            results.append(result)
        return results

    async def get_quality_score(
        self,
        original_text: str,
        translated_text: str,
        source_language: str,
        target_language: str
    ) -> float:
        """Calculate quality score for a translation"""
        if not translated_text or translated_text == original_text:
            return 0.5
        
        # Basic quality scoring
        base_score = 0.8
        
        # Bonus for Indian languages (Anuvadini's specialty)
        if source_language in self.indian_languages or target_language in self.indian_languages:
            base_score += 0.1
        
        return min(base_score, 1.0)
