"""
Cultural Intelligence Client

HTTP client for integrating with the Cultural Intelligence service
to get cultural appropriateness evaluations and adaptations.
"""

import httpx
import structlog
from typing import Dict, Any

logger = structlog.get_logger(__name__)

class CulturalIntelligenceClient:
    """Client for Cultural Intelligence service integration"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def evaluate_cultural_appropriateness(
        self, 
        content: Dict[str, Any], 
        cultural_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate cultural appropriateness of content"""
        try:
            evaluation_data = {
                "content": content,
                "cultural_profile": cultural_profile
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/cultural/evaluate",
                json=evaluation_data
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error evaluating cultural appropriateness", status_code=e.response.status_code)
            return self._create_fallback_evaluation("HTTP error")
        except httpx.RequestError as e:
            logger.error("Request error evaluating cultural appropriateness", error=str(e))
            return self._create_fallback_evaluation("Request error")
        except Exception as e:
            logger.error("Failed to evaluate cultural appropriateness", error=str(e))
            return self._create_fallback_evaluation("Service error")
    
    async def adapt_content_for_culture(
        self, 
        content: Dict[str, Any], 
        target_culture: str
    ) -> Dict[str, Any]:
        """Adapt content for specific cultural context"""
        try:
            adaptation_data = {
                "content": content,
                "target_culture": target_culture
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/cultural/adapt",
                json=adaptation_data
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error("Failed to adapt content for culture", error=str(e))
            return {"adapted_content": content, "adaptations_applied": [], "error": str(e)}
    
    async def get_cultural_guidelines(self, culture: str) -> Dict[str, Any]:
        """Get cultural guidelines for specific culture"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/cultural/guidelines/{culture}"
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error("Failed to get cultural guidelines", error=str(e))
            return {"guidelines": {}, "error": str(e)}
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Check Cultural Intelligence service health"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error("Failed to get Cultural Intelligence health", error=str(e))
            return {"status": "unhealthy", "error": str(e)}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get Cultural Intelligence service metrics"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/metrics")
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error("Failed to get Cultural Intelligence metrics", error=str(e))
            return {"error": str(e)}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def _create_fallback_evaluation(self, reason: str) -> Dict[str, Any]:
        """Create safe fallback when service is unavailable"""
        return {
            "culturally_appropriate": False,
            "appropriateness_score": 0.0,
            "content_evaluation": {},
            "timing_evaluation": {},
            "adapted_content": None,
            "cultural_considerations": [],
            "fallback_reason": reason
        }
