"""
ML Service Client for Chatbot Service
Provides crisis detection, intelligence insights, and behavioral analysis
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
import httpx
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CrisisAssessment:
    """Crisis assessment result"""
    risk_level: str  # low, medium, high, critical
    confidence: float
    risk_score: float
    indicators: List[str]
    recommended_actions: List[str]
    immediate_intervention: bool

@dataclass
class UserInsight:
    """User behavioral insight"""
    insight_type: str
    confidence: float
    description: str
    patterns: Dict[str, Any]
    recommendations: List[str]
    trend_direction: str  # improving, stable, declining

@dataclass
class Intervention:
    """Intervention recommendation"""
    intervention_type: str
    priority: str  # low, medium, high, urgent
    description: str
    action_items: List[str]
    expected_outcome: str
    confidence: float

@dataclass
class ConversationEffectiveness:
    """Conversation effectiveness analysis"""
    effectiveness_score: float
    engagement_level: str
    user_satisfaction: float
    goal_achievement: Dict[str, bool]
    improvement_suggestions: List[str]

class MLServiceClient:
    """Client for communicating with ML Service"""
    
    def __init__(self):
        import os
        self.ml_service_url = os.getenv("ML_SERVICE_URL", "http://ml-service:8008")
        self.timeout = int(os.getenv("ML_SERVICE_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("ML_SERVICE_MAX_RETRIES", "3"))
        self.crisis_threshold = float(os.getenv("ML_CRISIS_THRESHOLD", "0.7"))
        self.intervention_threshold = float(os.getenv("ML_INTERVENTION_THRESHOLD", "0.6"))
        self.pattern_analysis_enabled = os.getenv("ML_PATTERN_ANALYSIS_ENABLED", "true").lower() == "true"
        self.is_enabled = os.getenv("ML_SERVICE_ENABLED", "true").lower() == "true"
        
        logger.info(f"ML Service Client initialized - URL: {self.ml_service_url}, Enabled: {self.is_enabled}")
    
    async def health_check(self) -> bool:
        """Check if ML Service is healthy"""
        if not self.is_enabled:
            return False
            
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.ml_service_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"ML Service health check failed: {e}")
            return False
    
    async def assess_crisis_risk(
        self, 
        message: str, 
        user_context: Optional[Dict[str, Any]] = None,
        jwt_token: Optional[str] = None
    ) -> Optional[CrisisAssessment]:
        """
        Assess crisis risk for user message using ML Service
        
        Args:
            message: User message to analyze
            user_context: Additional user context
            jwt_token: JWT token for authentication
            
        Returns:
            CrisisAssessment object or None if failed
        """
        if not self.is_enabled:
            logger.debug("ML Service is disabled, performing basic crisis assessment")
            return self._basic_crisis_assessment(message)
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            payload = {
                "text": message,
                "context": user_context or {},
                "threshold": self.crisis_threshold
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ml_service_url}/crisis/predict-risk",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_crisis_assessment(data)
                else:
                    logger.error(f"Crisis assessment failed: {response.status_code} - {response.text}")
                    return self._basic_crisis_assessment(message)
                    
        except Exception as e:
            logger.error(f"Error in crisis assessment: {e}")
            return self._basic_crisis_assessment(message)
    
    async def get_user_insights(
        self, 
        user_id: str, 
        insight_type: str = "comprehensive",
        jwt_token: Optional[str] = None
    ) -> List[UserInsight]:
        """
        Get ML-powered user insights
        
        Args:
            user_id: User ID to analyze
            insight_type: Type of insights to retrieve
            jwt_token: JWT token for authentication
            
        Returns:
            List of UserInsight objects
        """
        if not self.is_enabled:
            logger.debug("ML Service is disabled, returning empty insights")
            return []
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            params = {"insight_type": insight_type}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.ml_service_url}/api/v1/insights/unified",
                    headers=headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_user_insights(data.get("insights", []))
                else:
                    logger.error(f"Get user insights failed: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting user insights: {e}")
            return []
    
    async def predict_user_needs(
        self, 
        user_context: Dict[str, Any],
        jwt_token: Optional[str] = None
    ) -> List[str]:
        """
        Predict user needs based on context using ML Service
        
        Args:
            user_context: User context for prediction
            jwt_token: JWT token for authentication
            
        Returns:
            List of predicted user needs
        """
        if not self.is_enabled:
            logger.debug("ML Service is disabled, using basic need prediction")
            return self._basic_need_prediction(user_context)
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            payload = {
                "context": user_context,
                "prediction_type": "user_needs"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ml_service_url}/ml/predict",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("predicted_needs", [])
                else:
                    logger.error(f"User needs prediction failed: {response.status_code} - {response.text}")
                    return self._basic_need_prediction(user_context)
                    
        except Exception as e:
            logger.error(f"Error predicting user needs: {e}")
            return self._basic_need_prediction(user_context)
    
    async def recommend_interventions(
        self, 
        user_state: Dict[str, Any],
        jwt_token: Optional[str] = None
    ) -> List[Intervention]:
        """
        Get intervention recommendations from ML Service
        
        Args:
            user_state: Current user state for recommendations
            jwt_token: JWT token for authentication
            
        Returns:
            List of Intervention objects
        """
        if not self.is_enabled:
            logger.debug("ML Service is disabled, using basic interventions")
            return self._basic_interventions(user_state)
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            payload = {
                "user_state": user_state,
                "threshold": self.intervention_threshold
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ml_service_url}/ml/recommend-interventions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_interventions(data.get("interventions", []))
                else:
                    logger.error(f"Intervention recommendations failed: {response.status_code} - {response.text}")
                    return self._basic_interventions(user_state)
                    
        except Exception as e:
            logger.error(f"Error getting intervention recommendations: {e}")
            return self._basic_interventions(user_state)
    
    async def analyze_conversation_effectiveness(
        self, 
        session_id: str,
        jwt_token: Optional[str] = None
    ) -> Optional[ConversationEffectiveness]:
        """
        Analyze conversation effectiveness using ML Service
        
        Args:
            session_id: Session ID to analyze
            jwt_token: JWT token for authentication
            
        Returns:
            ConversationEffectiveness object or None if failed
        """
        if not self.is_enabled:
            logger.debug("ML Service is disabled, using basic effectiveness analysis")
            return self._basic_effectiveness_analysis()
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.ml_service_url}/ml/conversation-effectiveness/{session_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_conversation_effectiveness(data)
                else:
                    logger.error(f"Conversation effectiveness analysis failed: {response.status_code} - {response.text}")
                    return self._basic_effectiveness_analysis()
                    
        except Exception as e:
            logger.error(f"Error analyzing conversation effectiveness: {e}")
            return self._basic_effectiveness_analysis()
    
    def _basic_crisis_assessment(self, message: str) -> CrisisAssessment:
        """Basic crisis assessment fallback"""
        message_lower = message.lower()
        
        # Crisis keywords
        critical_keywords = ["suicide", "kill myself", "end my life", "want to die"]
        high_risk_keywords = ["harm", "hurt myself", "can't go on", "no point"]
        medium_risk_keywords = ["hopeless", "worthless", "give up", "despair"]
        
        if any(keyword in message_lower for keyword in critical_keywords):
            return CrisisAssessment(
                risk_level="critical",
                confidence=0.9,
                risk_score=0.95,
                indicators=["suicidal ideation"],
                recommended_actions=["immediate_professional_help", "crisis_hotline"],
                immediate_intervention=True
            )
        elif any(keyword in message_lower for keyword in high_risk_keywords):
            return CrisisAssessment(
                risk_level="high",
                confidence=0.8,
                risk_score=0.8,
                indicators=["self-harm indicators"],
                recommended_actions=["professional_help", "safety_planning"],
                immediate_intervention=True
            )
        elif any(keyword in message_lower for keyword in medium_risk_keywords):
            return CrisisAssessment(
                risk_level="medium",
                confidence=0.7,
                risk_score=0.6,
                indicators=["emotional distress"],
                recommended_actions=["supportive_conversation", "coping_strategies"],
                immediate_intervention=False
            )
        else:
            return CrisisAssessment(
                risk_level="low",
                confidence=0.6,
                risk_score=0.2,
                indicators=[],
                recommended_actions=["continue_conversation"],
                immediate_intervention=False
            )
    
    def _basic_need_prediction(self, user_context: Dict[str, Any]) -> List[str]:
        """Basic need prediction fallback"""
        needs = []
        
        # Analyze mood patterns
        mood_history = user_context.get("mood_history", [])
        if mood_history:
            recent_moods = [entry.get("mood_score", 5) for entry in mood_history[-5:]]
            avg_mood = sum(recent_moods) / len(recent_moods) if recent_moods else 5
            
            if avg_mood < 4:
                needs.extend(["emotional_support", "mood_improvement"])
            elif avg_mood > 7:
                needs.extend(["maintain_positivity", "goal_setting"])
        
        # Analyze conversation patterns
        conversation_patterns = user_context.get("conversation_patterns", {})
        if conversation_patterns.get("frequent_topics", []):
            frequent_topics = conversation_patterns["frequent_topics"]
            if "stress" in frequent_topics:
                needs.append("stress_management")
            if "anxiety" in frequent_topics:
                needs.append("anxiety_support")
            if "relationships" in frequent_topics:
                needs.append("relationship_guidance")
        
        return needs or ["general_support"]
    
    def _basic_interventions(self, user_state: Dict[str, Any]) -> List[Intervention]:
        """Basic intervention recommendations fallback"""
        interventions = []
        
        # Default supportive intervention
        interventions.append(Intervention(
            intervention_type="supportive_conversation",
            priority="medium",
            description="Provide empathetic and supportive conversation",
            action_items=["active_listening", "validation", "encouragement"],
            expected_outcome="Improved mood and sense of connection",
            confidence=0.7
        ))
        
        # Check for mood-based interventions
        if user_state.get("current_mood_score", 5) < 4:
            interventions.append(Intervention(
                intervention_type="mood_improvement",
                priority="high",
                description="Focus on mood improvement strategies",
                action_items=["mood_tracking", "positive_activities", "coping_strategies"],
                expected_outcome="Stabilized and improved mood",
                confidence=0.8
            ))
        
        return interventions
    
    def _basic_effectiveness_analysis(self) -> ConversationEffectiveness:
        """Basic conversation effectiveness analysis fallback"""
        return ConversationEffectiveness(
            effectiveness_score=0.7,
            engagement_level="medium",
            user_satisfaction=0.7,
            goal_achievement={"supportive_conversation": True},
            improvement_suggestions=["More personalized responses", "Better context awareness"]
        )
    
    def _parse_crisis_assessment(self, data: Dict[str, Any]) -> CrisisAssessment:
        """Parse crisis assessment from API response"""
        return CrisisAssessment(
            risk_level=data.get("risk_level", "low"),
            confidence=data.get("confidence", 0.0),
            risk_score=data.get("risk_score", 0.0),
            indicators=data.get("indicators", []),
            recommended_actions=data.get("recommended_actions", []),
            immediate_intervention=data.get("immediate_intervention", False)
        )
    
    def _parse_user_insights(self, insights_data: List[Dict[str, Any]]) -> List[UserInsight]:
        """Parse user insights from API response"""
        insights = []
        for insight_data in insights_data:
            try:
                insight = UserInsight(
                    insight_type=insight_data.get("type", "general"),
                    confidence=insight_data.get("confidence", 0.0),
                    description=insight_data.get("description", ""),
                    patterns=insight_data.get("patterns", {}),
                    recommendations=insight_data.get("recommendations", []),
                    trend_direction=insight_data.get("trend_direction", "stable")
                )
                insights.append(insight)
            except Exception as e:
                logger.error(f"Error parsing user insight: {e}")
                continue
        
        return insights
    
    def _parse_interventions(self, interventions_data: List[Dict[str, Any]]) -> List[Intervention]:
        """Parse interventions from API response"""
        interventions = []
        for intervention_data in interventions_data:
            try:
                intervention = Intervention(
                    intervention_type=intervention_data.get("type", "general"),
                    priority=intervention_data.get("priority", "medium"),
                    description=intervention_data.get("description", ""),
                    action_items=intervention_data.get("action_items", []),
                    expected_outcome=intervention_data.get("expected_outcome", ""),
                    confidence=intervention_data.get("confidence", 0.0)
                )
                interventions.append(intervention)
            except Exception as e:
                logger.error(f"Error parsing intervention: {e}")
                continue
        
        return interventions
    
    def _parse_conversation_effectiveness(self, data: Dict[str, Any]) -> ConversationEffectiveness:
        """Parse conversation effectiveness from API response"""
        return ConversationEffectiveness(
            effectiveness_score=data.get("effectiveness_score", 0.0),
            engagement_level=data.get("engagement_level", "medium"),
            user_satisfaction=data.get("user_satisfaction", 0.0),
            goal_achievement=data.get("goal_achievement", {}),
            improvement_suggestions=data.get("improvement_suggestions", [])
        )

# Global client instance
ml_service_client = MLServiceClient()
