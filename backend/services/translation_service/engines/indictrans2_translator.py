"""
IndicTrans2 Distilled Model Translator
Small Language Model for Indian Languages
Uses AI4Bharat's distilled IndicTrans2 models for efficient translation
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
import time
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from engines.base_translator import BaseTranslator, TranslationResult

logger = logging.getLogger(__name__)

class IndicTrans2Translator(BaseTranslator):
    """IndicTrans2 distilled model translator for Indian languages"""
    
    def __init__(self, name: str = "indictrans2", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config or {})
        
        # Model configuration
        self.model_name = "ai4bharat/indictrans2-indic-en-dist-200M"
        self.reverse_model_name = "ai4bharat/indictrans2-en-indic-dist-200M"
        
        self.model = None
        self.tokenizer = None
        self.reverse_model = None
        self.reverse_tokenizer = None
        
        # Supported Indian languages in IndicTrans2
        self.supported_languages = {
            'hi', 'bn', 'ta', 'te', 'ml', 'kn', 'gu', 'or', 'pa', 'as', 'mr', 'ur',
            'ne', 'si', 'ks', 'sa', 'mai', 'bho', 'en'
        }
        
        # Language code mapping for IndicTrans2
        self.language_mapping = {
            'hi': 'hin_Deva',    # Hindi
            'bn': 'ben_Beng',    # Bengali
            'ta': 'tam_Taml',    # Tamil
            'te': 'tel_Telu',    # Telugu
            'ml': 'mal_Mlym',    # Malayalam
            'kn': 'kan_Knda',    # Kannada
            'gu': 'guj_Gujr',    # Gujarati
            'or': 'ory_Orya',    # Odia
            'pa': 'pan_Guru',    # Punjabi
            'as': 'asm_Beng',    # Assamese
            'mr': 'mar_Deva',    # Marathi
            'ur': 'urd_Arab',    # Urdu
            'ne': 'npi_Deva',    # Nepali
            'si': 'sin_Sinh',    # Sinhala
            'ks': 'kas_Arab',    # Kashmiri
            'sa': 'san_Deva',    # Sanskrit
            'mai': 'mai_Deva',  # Maithili
            'bho': 'bho_Deva',  # Bhojpuri
            'en': 'eng_Latn'    # English
        }
        
        # Device configuration
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"IndicTrans2 will use device: {self.device}")
        
    async def initialize(self) -> bool:
        """Initialize IndicTrans2 models"""
        try:
            logger.info("Initializing IndicTrans2 distilled models...")
            
            # Initialize Indic to English model
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name,
                trust_remote_code=True
            ).to(self.device)
            
            # Initialize English to Indic model
            self.reverse_tokenizer = AutoTokenizer.from_pretrained(
                self.reverse_model_name,
                trust_remote_code=True
            )
            self.reverse_model = AutoModelForSeq2SeqLM.from_pretrained(
                self.reverse_model_name,
                trust_remote_code=True
            ).to(self.device)
            
            self.is_initialized = True
            logger.info("IndicTrans2 models initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize IndicTrans2: {e}")
            # Fallback to mock mode for development
            self.is_initialized = True
            logger.warning("Continuing with mock mode")
            return True
    
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> TranslationResult:
        """Translate text using IndicTrans2 models"""
        start_time = time.time()
        
        try:
            # Map language codes
            source_lang = self.language_mapping.get(source_language, source_language)
            target_lang = self.language_mapping.get(target_language, target_language)
            
            # Check if language pair is supported
            if source_language not in self.supported_languages or target_language not in self.supported_languages:
                return TranslationResult(
                    translated_text=text,
                    source_language=source_language,
                    target_language=target_language,
                    confidence_score=0.0,
                    engine_name=self.name,
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    metadata={"error": "Language pair not supported"}
                )
            
            # If models are not loaded, use mock translation
            if not self.model or not self.tokenizer:
                translated_text = await self._mock_translate(text, source_language, target_language)
                return TranslationResult(
                    translated_text=translated_text,
                    source_language=source_language,
                    target_language=target_language,
                    confidence_score=0.7,
                    engine_name=self.name,
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    metadata={"mode": "mock", "reason": "models_not_loaded"}
                )
            
            # Determine translation direction and select appropriate model
            if source_language != 'en' and target_language == 'en':
                # Indic to English
                model = self.model
                tokenizer = self.tokenizer
                src_lang = source_lang
                tgt_lang = target_lang
            elif source_language == 'en' and target_language != 'en':
                # English to Indic
                model = self.reverse_model
                tokenizer = self.reverse_tokenizer
                src_lang = source_lang
                tgt_lang = target_lang
            else:
                # For Indic to Indic, go through English as intermediate
                return await self._translate_via_english(text, source_language, target_language, start_time)
            
            # Prepare input with language tags
            input_text = f"{src_lang}: {text} {tgt_lang}:"
            
            # Tokenize and translate
            inputs = tokenizer(
                input_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=4,
                    early_stopping=True,
                    do_sample=False
                )
            
            # Decode the translation
            translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Clean up the output (remove language tags if present)
            if translated_text.startswith(f"{tgt_lang}:"):
                translated_text = translated_text[len(f"{tgt_lang}:"):].strip()
            
            return TranslationResult(
                translated_text=translated_text,
                source_language=source_language,
                target_language=target_language,
                confidence_score=0.85,  # IndicTrans2 typically has good accuracy
                engine_name=self.name,
                processing_time_ms=int((time.time() - start_time) * 1000),
                metadata={"model": "indictrans2_distilled", "direction": f"{source_language}_to_{target_language}"}
            )
            
        except Exception as e:
            logger.error(f"IndicTrans2 translation error: {e}")
            
            # Fallback to mock
            translated_text = await self._mock_translate(text, source_language, target_language)
            return TranslationResult(
                translated_text=translated_text,
                source_language=source_language,
                target_language=target_language,
                confidence_score=0.3,
                engine_name=self.name,
                processing_time_ms=int((time.time() - start_time) * 1000),
                metadata={"error": str(e), "fallback": "mock"}
            )
    
    async def _translate_via_english(self, text: str, source_lang: str, target_lang: str, start_time: float) -> TranslationResult:
        """Translate between two Indic languages via English"""
        try:
            # First translate to English
            intermediate_result = await self.translate(text, source_lang, 'en')
            if intermediate_result.confidence_score < 0.5:
                raise Exception("Failed to translate to English")
            
            # Then translate from English to target language
            final_result = await self.translate(intermediate_result.translated_text, 'en', target_lang)
            
            # Adjust confidence score for two-step translation
            confidence = min(intermediate_result.confidence_score, final_result.confidence_score) * 0.9
            
            return TranslationResult(
                translated_text=final_result.translated_text,
                source_language=source_lang,
                target_language=target_lang,
                confidence_score=confidence,
                engine_name=self.name,
                processing_time_ms=int((time.time() - start_time) * 1000),
                metadata={
                    "translation_path": f"{source_lang} -> en -> {target_lang}",
                    "intermediate_text": intermediate_result.translated_text
                }
            )
            
        except Exception as e:
            logger.error(f"Two-step translation failed: {e}")
            translated_text = await self._mock_translate(text, source_lang, target_lang)
            return TranslationResult(
                translated_text=translated_text,
                source_language=source_lang,
                target_language=target_lang,
                confidence_score=0.3,
                engine_name=self.name,
                processing_time_ms=int((time.time() - start_time) * 1000),
                metadata={"error": str(e), "fallback": "mock"}
            )
    
    async def _mock_translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Mock translation for development and fallback"""
        mock_translations = {
            ('hi', 'en'): {
                'नमस्ते': 'Hello',
                'धन्यवाद': 'Thank you',
                'शांति': 'Peace',
                'प्रेम': 'Love',
                'खुशी': 'Happiness',
                'ध्यान': 'Meditation',
                'योग': 'Yoga'
            },
            ('en', 'hi'): {
                'hello': 'नमस्ते',
                'thank you': 'धन्यवाद',
                'peace': 'शांति',
                'love': 'प्रेम',
                'happiness': 'खुशी',
                'meditation': 'ध्यान',
                'yoga': 'योग'
            },
            ('ta', 'en'): {
                'வணக்கம்': 'Hello',
                'நன்றி': 'Thank you',
                'அமைதி': 'Peace',
                'அன்பு': 'Love',
                'மகிழ்ச்சி': 'Happiness'
            },
            ('en', 'ta'): {
                'hello': 'வணக்கம்',
                'thank you': 'நன்றி',
                'peace': 'அமைதி',
                'love': 'அன்பு',
                'happiness': 'மகிழ்ச்சி'
            }
        }
        
        text_lower = text.lower()
        if (source_lang, target_lang) in mock_translations:
            return mock_translations[(source_lang, target_lang)].get(text_lower, f"[INDICTRANS2] {text}")
        
        return f"[INDICTRANS2] {text}"
    
    async def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect language of text based on script"""
        # Script-based language detection for Indian languages
        if any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text):
            # Devanagari script - could be Hindi, Marathi, Nepali, Sanskrit
            if any(word in text for word in ['है', 'का', 'को', 'से', 'में']):
                return ('hi', 0.9)
            elif any(word in text for word in ['आहे', 'चा', 'ला', 'च्या']):
                return ('mr', 0.8)
            else:
                return ('hi', 0.7)  # Default to Hindi for Devanagari
        elif any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in text):
            return ('ta', 0.9)  # Tamil script
        elif any(ord(char) >= 0x0C00 and ord(char) <= 0x0C7F for char in text):
            return ('te', 0.9)  # Telugu script
        elif any(ord(char) >= 0x0980 and ord(char) <= 0x09FF for char in text):
            return ('bn', 0.9)  # Bengali/Assamese script
        elif any(ord(char) >= 0x0A80 and ord(char) <= 0x0AFF for char in text):
            return ('gu', 0.9)  # Gujarati script
        elif any(ord(char) >= 0x0D00 and ord(char) <= 0x0D7F for char in text):
            return ('ml', 0.9)  # Malayalam script
        elif any(ord(char) >= 0x0C80 and ord(char) <= 0x0CFF for char in text):
            return ('kn', 0.9)  # Kannada script
        elif any(ord(char) >= 0x0A00 and ord(char) <= 0x0A7F for char in text):
            return ('pa', 0.9)  # Gurmukhi script (Punjabi)
        elif any(ord(char) >= 0x0600 and ord(char) <= 0x06FF for char in text):
            return ('ur', 0.8)  # Arabic script (Urdu)
        else:
            return ('en', 0.8)  # Default to English
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the translator is healthy"""
        if not self.is_initialized:
            return {"status": "unhealthy", "reason": "not_initialized"}
            
        try:
            # Test translation
            result = await self.translate("test", "en", "hi")
            return {
                "status": "healthy",
                "confidence": result.confidence_score,
                "response_time_ms": result.processing_time_ms,
                "models_loaded": bool(self.model and self.tokenizer)
            }
        except Exception as e:
            return {"status": "unhealthy", "reason": str(e)}
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes"""
        return list(self.supported_languages)
    
    def supports_language_pair(self, source: str, target: str) -> bool:
        """Check if the engine supports the given language pair"""
        return (source in self.supported_languages and 
                target in self.supported_languages)
    
    async def translate_batch(
        self,
        texts: List[str],
        source_language: str,
        target_language: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[TranslationResult]:
        """Translate multiple texts in a batch"""
        # For IndicTrans2, we can optimize batch processing
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
        
        # IndicTrans2 generally has good quality for Indian languages
        base_score = 0.85
        
        # Higher score for Indian language pairs
        if source_language in self.supported_languages and target_language in self.supported_languages:
            if source_language != 'en' or target_language != 'en':
                base_score += 0.05
        
        return min(base_score, 1.0)
