"""
AI Context Store Client

HTTP client for integrating with the AI Context Store service
to get user context and intelligence insights.
"""

import httpx
import structlog
import os
import sys
from typing import Dict, Any

# Add backend path for shared auth
sys.path.append('/app')
sys.path.append('/app/shared')

from shared.auth import create_service_token

logger = structlog.get_logger(__name__)

class AIContextStoreClient:
    """Client for AI Context Store service integration"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.service_token = create_service_token("proactive_assistance_engine")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for service requests"""
        return {
            "Authorization": f"Bearer {self.service_token}",
            "Content-Type": "application/json"
        }
    
    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user context"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/context/user/{user_id}",
                headers=self._get_auth_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error getting user context", status_code=e.response.status_code, user_id=user_id)
            return self._create_fallback_context(user_id, "HTTP error")
        except httpx.RequestError as e:
            logger.error("Request error getting user context", error=str(e), user_id=user_id)
            return self._create_fallback_context(user_id, "Request error")
        except Exception as e:
            logger.error("Failed to get user context", error=str(e), user_id=user_id)
            return self._create_fallback_context(user_id, "Service error")
    
    async def get_user_intelligence_insights(self, user_id: str) -> Dict[str, Any]:
        """Get AI intelligence insights for user"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/intelligence/insights/{user_id}",
                headers=self._get_auth_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error("Failed to get intelligence insights", error=str(e), user_id=user_id)
            return {"insights": [], "confidence": 0.0, "error": str(e)}
    
    async def update_user_context(self, user_id: str, context_type: str, data: Dict[str, Any]) -> bool:
        """Update user context with new data"""
        try:
            update_data = {
                "user_id": user_id,
                "context_type": context_type,
                "data": data
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/context/update",
                json=update_data,
                headers=self._get_auth_headers()
            )
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error("Failed to update user context", error=str(e), user_id=user_id)
            return False
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Check AI Context Store health"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error("Failed to get AI Context Store health", error=str(e))
            return {"status": "unhealthy", "error": str(e)}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get AI Context Store metrics"""
        try:
            response = await self.client.get(f"{self.base_url}/metrics")
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error("Failed to get AI Context Store metrics", error=str(e))
            return {"error": str(e)}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def _create_fallback_context(self, user_id: str, reason: str) -> Dict[str, Any]:
        """Create minimal context when service unavailable"""
        return {
            "user_id": user_id,
            "mood_context": {"current_mood_score": 5.0, "mood_trend": "stable"},
            "behavioral_patterns": {},
            "cultural_profile": {"primary_culture": "unknown", "communication_style": "neutral"},
            "recent_interactions": [],
            "fallback_reason": reason,
            "timestamp": "2025-01-01T00:00:00Z"
        }
