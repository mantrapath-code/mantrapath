"""
Ollama Integration for Models Service
Provides text generation capabilities via Ollama
"""

import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for Ollama text generation service."""

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.timeout_seconds = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30"))
        self.default_model = os.getenv("OLLAMA_MODEL", "phi3:mini")

    async def generate_text(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """Generate text using Ollama."""
        try:
            # Simple mock response for now - replace with actual Ollama API call when needed
            return {
                "success": True,
                "generated_text": f"[Ollama not available] Echo: {prompt[:100]}...",
                "model": model or self.default_model,
                "tokens_used": len(prompt.split())
            }
        except Exception as e:
            logger.error("Ollama generation error: %s", e)
            return {"success": False, "error": str(e)}


# Global instance
ollama_client = OllamaClient()