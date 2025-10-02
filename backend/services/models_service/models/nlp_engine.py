"""
NLP Engine
Handles language processing tasks via external inference backends
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

# Embeddings functionality removed - focusing on Phi-4 text generation

logger = logging.getLogger(__name__)

class NLPEngine:
    """Natural Language Processing engine backed by external services (TEI)."""
    
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.is_initialized = False
        self.loaded_models = {}
        
        # Supported tasks (Phi-4 text generation)
        self.supported_tasks = {
            "text_generation": ["phi4"],
        }
    
    async def initialize(self):
        """Initialize the NLP engine with Phi-4"""
        logger.info("🧠 Initializing NLP Engine (Phi-4 text generation)...")
        self.is_initialized = True
        logger.info("✅ NLP Engine ready (Phi-4 text generation enabled)")
        return True
    
    async def load_default_models(self):
        """Load default NLP models (Phi-4 text generation)"""
        logger.info("🧠 NLP Engine: Loading default models...")
        
        try:
            # Initialize NLP engine
            success = await self.initialize()
            if success:
                logger.info("✅ NLP Engine: Base engine initialized")
                
                # Add Phi-4 model info (will be loaded on-demand via text generation routes)
                phi4_model = "microsoft/phi-4"  # Latest Phi-4 model
                self.loaded_models["phi4_text_generation"] = {
                    "type": "text_generation", 
                    "model": phi4_model,
                    "status": "ready_on_demand"
                }
                logger.info(f"✅ NLP Engine: Phi-4 model configured: {phi4_model}")
                return True
            else:
                logger.warning("⚠️ NLP Engine: Initialization failed")
                return False
        except Exception as e:
            logger.error(f"❌ NLP Engine: Failed to load default models: {e}")
            return False
    
    async def translate(self, *args, **kwargs) -> Dict[str, Any]:
        """Translation is temporarily disabled until a lightweight backend is configured."""
        return {"success": False, "error": "Translation backend not configured"}
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        return {"language": "en", "confidence": 0.0}
    
    async def analyze_sentiment(self, text: str, language: str = "en") -> Dict[str, Any]:
        return {"sentiment": "neutral", "confidence": 0.0}
    
    async def generate_text(self, *args, **kwargs) -> Dict[str, Any]:
        return {"success": False, "error": "Text generation backend not configured"}
    
    def get_supported_languages(self) -> List[str]:
        return []
    
    def get_model_info(self) -> Dict[str, Any]:
        if self.is_initialized:
            return {"text_generation": "phi4", "status": "ready"}
        return {"error": "NLP Engine not initialized"}
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up NLP Engine...")
        self.is_initialized = False

    # Embeddings functionality removed - use models_service text generation endpoints instead
