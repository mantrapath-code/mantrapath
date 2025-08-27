"""
Proactive Assistance Engine Client for Chatbot Service
Handles communication with Proactive Assistance Engine for proactive suggestions and interventions
"""
import os
import asyncio
import httpx
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

@dataclass
class ProactiveInsight:
    """Proactive insight from Assistance Engine"""
    id: str
    type: str  # suggestion, warning, intervention, insight
    priority: int  # 1-5, 5 being highest
    title: str
    message: str
    suggested_actions: List[str]
    confidence: float
    metadata: Dict[str, Any]

@dataclass
class UserRiskAssessment:
    """User risk assessment from Assistance Engine"""
    user_id: str
    risk_level: str  # low, medium, high, critical
    risk_factors: List[str]
    recommendations: List[str]
    intervention_required: bool
    assessment_timestamp: datetime

class ProactiveAssistanceEngineClient:
    """Client for communicating with Proactive Assistance Engine"""
    
    def __init__(self):
        """Initialize Proactive Assistance Engine client"""
        self.proactive_engine_url = os.getenv("PROACTIVE_ASSISTANCE_ENGINE_URL", "http://proactive-assistance-engine:8018")
        self.timeout = int(os.getenv("PROACTIVE_ASSISTANCE_ENGINE_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("PROACTIVE_ASSISTANCE_ENGINE_MAX_RETRIES", "3"))
        
        # Feature flags
        self.is_enabled = os.getenv("PROACTIVE_ASSISTANCE_ENGINE_ENABLED", "true").lower() == "true"
        
        logger.info(f"Proactive Assistance Engine Client initialized - URL: {self.proactive_engine_url}, Enabled: {self.is_enabled}")
    
    async def check_health(self) -> bool:
        """Check if Proactive Assistance Engine is healthy"""
        if not self.is_enabled:
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.proactive_engine_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Proactive Assistance Engine health check failed: {e}")
            return False
    
    # Alias for compatibility
    async def health_check(self) -> bool:
        """Alias for check_health for compatibility"""
        return await self.check_health()
    
    async def get_proactive_insights(
        self, 
        user_id: str, 
        session_id: str,
        current_message: str,
        user_context: Optional[Dict[str, Any]] = None,
        jwt_token: Optional[str] = None
    ) -> List[ProactiveInsight]:
        """Get proactive insights for user"""
        if not self.is_enabled:
            logger.debug("Proactive Assistance Engine is disabled, returning empty insights")
            return []
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            for attempt in range(self.max_retries):
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.post(
                            f"{self.proactive_engine_url}/api/v1/insights/analyze",
                            headers=headers,
                            json={
                                "user_id": user_id,
                                "session_id": session_id,
                                "current_message": current_message,
                                "user_context": user_context or {},
                                "timestamp": datetime.now().isoformat()
                            }
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            insights = []
                            
                            for insight_data in data.get("insights", []):
                                insight = ProactiveInsight(
                                    id=insight_data.get("id"),
                                    type=insight_data.get("type"),
                                    priority=insight_data.get("priority", 1),
                                    title=insight_data.get("title"),
                                    message=insight_data.get("message"),
                                    suggested_actions=insight_data.get("suggested_actions", []),
                                    confidence=insight_data.get("confidence", 0.5),
                                    metadata=insight_data.get("metadata", {})
                                )
                                insights.append(insight)
                            
                            logger.debug(f"Retrieved {len(insights)} proactive insights for user {user_id}")
                            return insights
                        else:
                            logger.warning(f"Proactive Assistance Engine returned status {response.status_code}")
                            return []
                            
                except httpx.TimeoutException:
                    logger.warning(f"Proactive Assistance Engine timeout on attempt {attempt + 1}")
                    if attempt == self.max_retries - 1:
                        return []
                    await asyncio.sleep(1 * (attempt + 1))
                    
        except Exception as e:
            logger.error(f"Error getting proactive insights: {e}")
            return []
    
    async def assess_user_risk(
        self, 
        user_id: str,
        recent_messages: List[str],
        user_context: Optional[Dict[str, Any]] = None,
        jwt_token: Optional[str] = None
    ) -> Optional[UserRiskAssessment]:
        """Assess user risk level"""
        if not self.is_enabled:
            logger.debug("Proactive Assistance Engine is disabled, returning None")
            return None
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            for attempt in range(self.max_retries):
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.post(
                            f"{self.proactive_engine_url}/api/v1/risk/assess",
                            headers=headers,
                            json={
                                "user_id": user_id,
                                "recent_messages": recent_messages,
                                "user_context": user_context or {},
                                "timestamp": datetime.now().isoformat()
                            }
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            assessment = UserRiskAssessment(
                                user_id=data.get("user_id"),
                                risk_level=data.get("risk_level"),
                                risk_factors=data.get("risk_factors", []),
                                recommendations=data.get("recommendations", []),
                                intervention_required=data.get("intervention_required", False),
                                assessment_timestamp=datetime.fromisoformat(data.get("assessment_timestamp"))
                            )
                            
                            logger.debug(f"Risk assessment completed for user {user_id}: {assessment.risk_level}")
                            return assessment
                        else:
                            logger.warning(f"Proactive Assistance Engine returned status {response.status_code}")
                            return None
                            
                except httpx.TimeoutException:
                    logger.warning(f"Proactive Assistance Engine timeout on attempt {attempt + 1}")
                    if attempt == self.max_retries - 1:
                        return None
                    await asyncio.sleep(1 * (attempt + 1))
                    
        except Exception as e:
            logger.error(f"Error assessing user risk: {e}")
            return None
    
    async def trigger_proactive_intervention(
        self, 
        user_id: str,
        intervention_type: str,
        priority: int = 3,
        metadata: Optional[Dict[str, Any]] = None,
        jwt_token: Optional[str] = None
    ) -> bool:
        """Trigger a proactive intervention"""
        if not self.is_enabled:
            logger.debug("Proactive Assistance Engine is disabled, skipping intervention")
            return True
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            for attempt in range(self.max_retries):
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.post(
                            f"{self.proactive_engine_url}/api/v1/interventions/trigger",
                            headers=headers,
                            json={
                                "user_id": user_id,
                                "intervention_type": intervention_type,
                                "priority": priority,
                                "metadata": metadata or {},
                                "timestamp": datetime.now().isoformat()
                            }
                        )
                        
                        if response.status_code == 200:
                            logger.debug(f"Intervention triggered successfully for user {user_id}")
                            return True
                        else:
                            logger.warning(f"Proactive Assistance Engine returned status {response.status_code}")
                            return False
                            
                except httpx.TimeoutException:
                    logger.warning(f"Proactive Assistance Engine timeout on attempt {attempt + 1}")
                    if attempt == self.max_retries - 1:
                        return False
                    await asyncio.sleep(1 * (attempt + 1))
                    
        except Exception as e:
            logger.error(f"Error triggering intervention: {e}")
            return False

# Global instance
proactive_assistance_engine_client = ProactiveAssistanceEngineClient()
