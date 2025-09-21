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

# Import embeddings_client with absolute import
try:
    from embeddings_integration import embeddings_client
except ImportError:
    # Add parent directory to sys.path and try again
    import sys
    import os
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from embeddings_integration import embeddings_client

logger = logging.getLogger(__name__)

class NLPEngine:
    """Natural Language Processing engine backed by external services (TEI)."""
    
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.is_initialized = False
        self.loaded_models = {}
        
        # Supported tasks (TEI for embeddings; others may be routed elsewhere)
        self.supported_tasks = {
            "embeddings": ["tei"],
        }
    
    async def initialize(self):
        """Initialize the NLP engine with Phi-3"""
        logger.info("🧠 Initializing NLP Engine (embeddings via TEI)...")
        self.is_initialized = True
        self.loaded_models["tei_embeddings"] = {"type": "embeddings", "backend": "tei"}
        logger.info("✅ NLP Engine ready (TEI embeddings enabled)")
        return True
    
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
            return {"embeddings_backend": "tei"}
        return {"error": "NLP Engine not initialized"}
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up NLP Engine...")
        self.is_initialized = False

    async def get_embeddings(self, text: str, model_name: str = "tei") -> Dict[str, Any]:
        """Get text embeddings via TEI server."""
        if not self.is_initialized:
            return {"success": False, "error": "NLP Engine not initialized"}

        inputs = [text]
        result = await embeddings_client.embed(inputs)
        return result
