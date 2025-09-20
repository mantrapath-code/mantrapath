"""
NLP Engine
Handles language processing tasks using Microsoft Phi-3 model
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from .phi3_engine import Phi3Engine

logger = logging.getLogger(__name__)

class NLPEngine:
    """Natural Language Processing engine powered by Microsoft Phi-3"""
    
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.phi3_engine = Phi3Engine()
        self.is_initialized = False
        self.loaded_models = {}  # Track loaded models
        
        # Supported tasks
        self.supported_tasks = {
            "translation": ["phi3"],
            "sentiment": ["phi3"],
            "language_detection": ["phi3"],
            "text_generation": ["phi3"]
        }
    
    async def initialize(self):
        """Initialize the NLP engine with Phi-3"""
        logger.info("🧠 Initializing NLP Engine with Phi-3 (non-blocking)...")

        # Offload heavy model loading to a background thread to avoid blocking the event loop
        try:
            import asyncio

            async def _init_async():
                return await self.phi3_engine.initialize()

            # phi3_engine.initialize() is async but internally performs heavy sync work.
            # Execute it in a separate thread context to keep the server responsive.
            success = await asyncio.to_thread(lambda: asyncio.run(_init_async()))
        except Exception as e:
            logger.error(f"❌ Error during Phi-3 engine init: {e}")
            success = False

        if success:
            self.is_initialized = True
            self.loaded_models["phi3"] = self.phi3_engine  # Track the loaded model
            logger.info("✅ NLP Engine with Phi-3 ready")
            return True
        else:
            logger.error("❌ Failed to initialize Phi-3 engine")
            return False
    
    async def load_default_models(self):
        """Load default NLP models (Phi-3) gracefully"""
        logger.info("🧠 Attempting to load default NLP models...")
        
        # Check if we're in minimal mode
        if os.environ.get("MODELS_SERVICE_MODE") == "minimal":
            logger.info("✅ NLP Engine initialized in minimal mode (models will load on-demand)")
            return True
        
        try:
            success = await self.initialize()
            if success:
                logger.info("✅ NLP Engine initialized successfully")
            else:
                logger.warning("⚠️ NLP Engine initialization failed - service will continue without NLP")
            return success
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize NLP engine: {e}")
            return False
    
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        model_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """Translate text between languages using Phi-3"""
        if not self.is_initialized:
            return {
                "success": False,
                "error": "NLP Engine not initialized",
                "translated_text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence_score": 0.0
            }
        
        try:
            result = await self.phi3_engine.translate(
                text=text,
                source_language=source_lang,
                target_language=target_lang
            )
            return result
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "translated_text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence_score": 0.0
            }
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language of text using Phi-3"""
        if not self.is_initialized:
            return {"language": "en", "confidence": 0.0}
        
        try:
            detected_lang = await self.phi3_engine.detect_language(text)
            return {
                "language": detected_lang,
                "confidence": 0.9
            }
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return {"language": "en", "confidence": 0.0}
    
    async def analyze_sentiment(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Analyze sentiment using Phi-3"""
        if not self.is_initialized:
            return {"sentiment": "neutral", "confidence": 0.0}
        
        try:
            result = await self.phi3_engine.analyze_sentiment(text, language)
            return result
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {"sentiment": "neutral", "confidence": 0.0}
    
    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate text using Phi-3"""
        if not self.is_initialized:
            return {"success": False, "error": "NLP Engine not initialized"}
        
        try:
            generated_text = await self.phi3_engine.generate_response(
                prompt, max_tokens, temperature
            )
            return {
                "success": True,
                "generated_text": generated_text
            }
        except Exception as e:
            logger.error(f"Text generation error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        if self.is_initialized:
            return list(self.phi3_engine.supported_languages.keys())
        return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        if self.is_initialized:
            return self.phi3_engine.get_model_info()
        return {"error": "NLP Engine not initialized"}
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up NLP Engine...")
        self.is_initialized = False
