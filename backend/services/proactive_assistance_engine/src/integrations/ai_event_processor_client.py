"""
AI Event Processor Client

HTTP client for integrating with the AI Event Processor service
to get intervention analysis and crisis detection.
"""

import httpx
import structlog
from typing import Dict, Any
from datetime import datetime

logger = structlog.get_logger(__name__)

class AIEventProcessorClient:
    """Client for AI Event Processor service integration"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def analyze_intervention_needs(self, user_id: str) -> Dict[str, Any]:
        """Get intervention analysis from AI Event Processor"""
        try:
            # Use the correct predictive engine endpoint
            response = await self.client.get(
                f"{self.base_url}/api/v1/predict/intervention/{user_id}"
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error getting intervention analysis", status_code=e.response.status_code, user_id=user_id)
            return self._create_fallback_analysis("HTTP error")
        except httpx.RequestError as e:
            logger.error("Request error getting intervention analysis", error=str(e), user_id=user_id)
            return self._create_fallback_analysis("Request error")
        except Exception as e:
            logger.error("Failed to get intervention analysis", error=str(e), user_id=user_id)
            return self._create_fallback_analysis("Service error")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Check AI Event Processor health"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error("Failed to get AI Event Processor health", error=str(e))
            return {"status": "unhealthy", "error": str(e)}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get AI Event Processor metrics"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/metrics")
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error("Failed to get AI Event Processor metrics", error=str(e))
            return {"error": str(e)}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def _create_fallback_analysis(self, reason: str) -> Dict[str, Any]:
        """Create safe fallback when service is unavailable"""
        return {
            "intervention_needed": False,
            "confidence": 0.0,
            "intervention_type": None,
            "urgency_level": "none",
            "recommended_actions": [],
            "risk_factors": {},
            "fallback_reason": reason,
            "timestamp": datetime.now().isoformat()
        }
