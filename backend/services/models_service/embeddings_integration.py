"""
Embeddings Integration for Models Service
Uses Hugging Face Text Embeddings Inference (TEI) server
"""

import os
import logging
from typing import Dict, Any, List, Optional

import httpx

logger = logging.getLogger(__name__)


class EmbeddingsClient:
    """Client for Hugging Face Text Embeddings Inference server."""

    def __init__(self):
        self.base_url = os.getenv("TEI_BASE_URL", "http://ext-embeddings-inference:80").rstrip("/")
        self.model_id = os.getenv("TEI_MODEL_ID", "google/embeddinggemma-300m")
        self.timeout_seconds = float(os.getenv("TEI_TIMEOUT_SECONDS", "15"))

    async def embed(self, inputs: List[str], model_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate embeddings for a list of input strings."""
        model = model_id or self.model_id

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/v1/embeddings",
                    json={
                        "model": model,
                        "input": inputs,
                    },
                )

                response.raise_for_status()
                data = response.json()

                # Normalize to a common structure
                vectors: List[List[float]] = []
                if isinstance(data, dict) and "data" in data:
                    # OpenAI-compatible TEI response
                    # data: [{"object":"embedding","embedding":[...],"index":0}, ...]
                    for item in data.get("data", []):
                        vectors.append(item.get("embedding", []))
                elif isinstance(data, list):
                    # Raw list of vectors
                    vectors = data
                else:
                    logger.error("Unexpected TEI response format: %s", str(data)[:200])
                    return {"success": False, "error": "Unexpected TEI response format"}

                return {
                    "success": True,
                    "embeddings": vectors,
                    "model": model,
                    "dimension": len(vectors[0]) if vectors else 0,
                    "count": len(vectors),
                }

        except httpx.HTTPError as http_err:
            logger.error("TEI HTTP error: %s", http_err)
            return {"success": False, "error": str(http_err)}
        except Exception as e:
            logger.error("TEI client error: %s", e)
            return {"success": False, "error": str(e)}


# Global instance
embeddings_client = EmbeddingsClient()




