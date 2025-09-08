"""
Microsoft Phi-3 Engine
Lightweight multilingual model for translation and various NLP tasks
"""

import asyncio
import json
import logging
import torch
from typing import Dict, List, Optional, Any, Union
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    pipeline,
    GenerationConfig
)
import time

logger = logging.getLogger(__name__)

class Phi3Engine:
    """Microsoft Phi-3 multilingual engine for translation and NLP tasks"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.generation_pipeline = None
        self.is_loaded = False
        
        # Model configuration
        self.model_name = "microsoft/Phi-3-mini-4k-instruct"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Supported languages (Phi-3 supports many languages)
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi', 
            'bn': 'Bengali',
            'ta': 'Tamil',
            'te': 'Telugu',
            'ml': 'Malayalam',
            'kn': 'Kannada',
            'gu': 'Gujarati',
            'mr': 'Marathi',
            'pa': 'Punjabi',
            'or': 'Odia',
            'as': 'Assamese',
            'ur': 'Urdu',
            'ne': 'Nepali',
            'sa': 'Sanskrit',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ru': 'Russian',
            'ar': 'Arabic'
        }
        
    async def initialize(self) -> bool:
        """Initialize Phi-3 model"""
        try:
            logger.info("🤖 Loading Microsoft Phi-3 model...")
            start_time = time.time()
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto" if self.device == "cuda" else None,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                trust_remote_code=True
            )
            
            # Create generation pipeline
            self.generation_pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
            self.is_loaded = True
            elapsed_time = time.time() - start_time
            logger.info(f"✅ Phi-3 model loaded successfully in {elapsed_time:.2f}s on {self.device}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load Phi-3 model: {e}")
            return False
    
    def _create_translation_prompt(self, text: str, source_lang: str, target_lang: str) -> str:
        """Create a translation prompt for Phi-3"""
        source_name = self.supported_languages.get(source_lang, source_lang)
        target_name = self.supported_languages.get(target_lang, target_lang)
        
        prompt = f"""<|system|>
You are a professional translator. Translate the given text accurately while preserving meaning, tone, and cultural context. Only return the translated text, nothing else.
<|end|>
<|user|>
Translate this {source_name} text to {target_name}:
"{text}"
<|end|>
<|assistant|>
"""
        return prompt
    
    def _create_detection_prompt(self, text: str) -> str:
        """Create a language detection prompt for Phi-3"""
        supported_langs = ", ".join([f"{code} ({name})" for code, name in self.supported_languages.items()])
        
        prompt = f"""<|system|>
You are a language detection expert. Identify the language of the given text and respond with only the 2-letter language code from this list: {supported_langs}
<|end|>
<|user|>
What language is this text: "{text}"
<|end|>
<|assistant|>
"""
        return prompt
    
    async def translate(
        self,
        text: str,
        source_language: str = "auto",
        target_language: str = "en",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Translate text using Phi-3"""
        if not self.is_loaded:
            return {
                "success": False,
                "error": "Phi-3 model not loaded",
                "translated_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "confidence_score": 0.0
            }
        
        try:
            start_time = time.time()
            
            # Auto-detect language if needed
            if source_language == "auto":
                detected_lang = await self.detect_language(text)
                source_language = detected_lang
            
            # Skip translation if source and target are the same
            if source_language == target_language:
                return {
                    "success": True,
                    "translated_text": text,
                    "source_language": source_language,
                    "target_language": target_language,
                    "confidence_score": 1.0,
                    "processing_time_ms": int((time.time() - start_time) * 1000)
                }
            
            # Create translation prompt
            prompt = self._create_translation_prompt(text, source_language, target_language)
            
            # Generate translation
            generation_config = GenerationConfig(
                max_new_tokens=256,
                temperature=0.1,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            outputs = self.generation_pipeline(
                prompt,
                generation_config=generation_config,
                return_full_text=False
            )
            
            # Extract translated text
            translated_text = outputs[0]['generated_text'].strip()
            
            # Clean up the output (remove any system artifacts)
            if translated_text.startswith('"') and translated_text.endswith('"'):
                translated_text = translated_text[1:-1]
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                "success": True,
                "translated_text": translated_text,
                "source_language": source_language,
                "target_language": target_language,
                "confidence_score": 0.9,  # Phi-3 is generally high quality
                "processing_time_ms": processing_time,
                "engine": "phi3"
            }
            
        except Exception as e:
            logger.error(f"Phi-3 translation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "translated_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "confidence_score": 0.0
            }
    
    async def detect_language(self, text: str) -> str:
        """Detect language using Phi-3"""
        if not self.is_loaded:
            return "en"  # Default fallback
        
        try:
            prompt = self._create_detection_prompt(text)
            
            generation_config = GenerationConfig(
                max_new_tokens=10,
                temperature=0.1,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            outputs = self.generation_pipeline(
                prompt,
                generation_config=generation_config,
                return_full_text=False
            )
            
            detected = outputs[0]['generated_text'].strip().lower()
            
            # Extract language code (first 2 characters if valid)
            for lang_code in self.supported_languages.keys():
                if lang_code in detected:
                    return lang_code
            
            # Default to English if detection fails
            return "en"
            
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return "en"
    
    async def analyze_sentiment(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Analyze sentiment using Phi-3"""
        if not self.is_loaded:
            return {"sentiment": "neutral", "confidence": 0.0}
        
        try:
            prompt = f"""<|system|>
You are a sentiment analysis expert. Analyze the sentiment of the given text and respond with only one word: positive, negative, or neutral.
<|end|>
<|user|>
Analyze the sentiment of this text: "{text}"
<|end|>
<|assistant|>
"""
            
            generation_config = GenerationConfig(
                max_new_tokens=10,
                temperature=0.1,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            outputs = self.generation_pipeline(
                prompt,
                generation_config=generation_config,
                return_full_text=False
            )
            
            sentiment = outputs[0]['generated_text'].strip().lower()
            
            # Map to standard sentiment values
            if "positive" in sentiment:
                return {"sentiment": "positive", "confidence": 0.8}
            elif "negative" in sentiment:
                return {"sentiment": "negative", "confidence": 0.8}
            else:
                return {"sentiment": "neutral", "confidence": 0.7}
                
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {"sentiment": "neutral", "confidence": 0.0}
    
    async def generate_response(
        self, 
        prompt: str, 
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> str:
        """Generate text response using Phi-3"""
        if not self.is_loaded:
            return "Model not loaded"
        
        try:
            generation_config = GenerationConfig(
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            outputs = self.generation_pipeline(
                prompt,
                generation_config=generation_config,
                return_full_text=False
            )
            
            return outputs[0]['generated_text'].strip()
            
        except Exception as e:
            logger.error(f"Text generation error: {e}")
            return f"Error: {str(e)}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "is_loaded": self.is_loaded,
            "supported_languages": self.supported_languages,
            "supported_tasks": [
                "translation",
                "language_detection", 
                "sentiment_analysis",
                "text_generation"
            ]
        }
