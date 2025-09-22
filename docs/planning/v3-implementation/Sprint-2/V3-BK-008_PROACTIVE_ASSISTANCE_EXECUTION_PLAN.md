# V3-BK-008: Proactive Assistance Engine - Comprehensive Execution Plan

**Story Status**: NOT IMPLEMENTED - Priority P0  
**Estimated Points**: 8 | **Assignee**: Mid Dev 2  
**Sprint**: Sprint 2 - Cross-Service Intelligence  
**Generated**: August 17, 2025

## Executive Summary

Based on comprehensive analysis of the existing backend services, the Proactive Assistance Engine requires building a **new dedicated service** that orchestrates existing AI capabilities into a cohesive proactive assistance system. While we have strong foundational components (AI Event Processor, Predictive Engine, Cultural Intelligence), we need to create the orchestration layer that provides timely, contextually relevant, and culturally sensitive assistance.

## Current State Analysis - DETAILED

### ✅ Available Foundation Components

#### 1. **PredictiveInterventionEngine** (ai_event_processor)
- **Location**: `/backend/services/ai_event_processor/core/predictive_engine.py`
- **Capabilities**:
  - Behavioral risk analysis with 85%+ accuracy target
  - Crisis detection with immediate intervention recommendations
  - Risk thresholds (critical: 0.9, high: 0.7, medium: 0.5, low: 0.3)
  - Optimal timing calculation framework
  - Comprehensive recommendation generation
- **Integration Points**: Redis storage, AI metrics, event publishing

#### 2. **Crisis Detection System** (Multiple Services)
- **ML Service**: `/backend/services/ml_service/main.py` - Crisis prediction API
- **Chatbot Service**: `/backend/services/chatbot_service/` - Real-time crisis detection
- **Capabilities**: Crisis prediction, safety assessment, intervention recommendations
- **Performance**: 87.3% accuracy, <2s response time

#### 3. **AI Context Store** (V3-BK-007 - IMPLEMENTED)
- **Location**: `/backend/services/ai_context_store/`
- **Capabilities**: Global user context aggregation, cross-service intelligence
- **API Endpoints**: User context retrieval, intelligence insights, recommendations

#### 4. **Cultural Intelligence** (V3-BK-005 - IMPLEMENTED)
- **Location**: `/backend/services/ai_event_processor/core/cultural_intelligence.py`
- **Capabilities**: Multi-language processing (25+ languages), cultural adaptation
- **Coverage**: 11+ cultural regions with 90%+ adaptation accuracy

#### 5. **Enhanced Event System** (IMPLEMENTED)
- **NATS JetStream**: Real-time event streaming
- **Event Types**: AI events, mood events, journal events, voice events
- **Performance**: <100ms event propagation, 99.9% reliability

### ❌ Missing Components - Implementation Required

#### 1. **Proactive Assistance Service** - MAIN GAP
- No dedicated service orchestrating proactive assistance
- No centralized assistance evaluation and delivery
- No user preference management for assistance

#### 2. **Contextual Help System** - NOT IMPLEMENTED
- No help content database or semantic matching
- No context-aware help recommendations
- No help content cultural adaptation

#### 3. **Comprehensive Timing System** - PARTIAL
- Basic timing calculation exists but not comprehensive
- No user receptiveness prediction
- No cultural timing preferences
- No activity state analysis for optimal timing

#### 4. **Assistance Delivery System** - NOT IMPLEMENTED
- No assistance delivery mechanisms
- No user feedback collection
- No assistance acceptance/rejection tracking

## Implementation Strategy - FOCUSED APPROACH

### Phase 1: Create Proactive Assistance Service (6h)
1. **New Service Architecture** (2h)
2. **Integration with Existing Components** (2h)
3. **Basic Assistance Orchestration** (2h)

### Phase 2: Enhanced Timing and Context (4h)
1. **Comprehensive Timing Prediction** (2h)
2. **Contextual Help System** (2h)

### Phase 3: Cultural Integration and Testing (2h)
1. **Cultural Sensitivity Integration** (1h)
2. **Comprehensive Testing** (1h)

**Total Estimated Time**: 12 hours (vs original 8-point estimate)
**Recommendation**: Request scope adjustment or additional sprint time

## Detailed Implementation Plan

### Task 1: Proactive Assistance Service Creation (6h)

#### 1.1: Service Architecture Setup (2h)

**Objective**: Create new dedicated service with proper FastAPI structure

**Implementation Steps**:

```bash
# Create service structure
mkdir -p /backend/services/proactive_assistance_engine/{src,tests,config}
mkdir -p /backend/services/proactive_assistance_engine/src/{core,api,integrations,models}
```

**Core Service File**:
```python
# File: backend/services/proactive_assistance_engine/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from contextlib import asynccontextmanager
import structlog
from src.core.assistance_orchestrator import ProactiveAssistanceOrchestrator

logger = structlog.get_logger(__name__)

# Global orchestrator
assistance_orchestrator: ProactiveAssistanceOrchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global assistance_orchestrator
    
    logger.info("Starting Proactive Assistance Engine")
    
    try:
        # Initialize orchestrator with existing service integrations
        assistance_orchestrator = ProactiveAssistanceOrchestrator()
        await assistance_orchestrator.initialize()
        
        logger.info("Proactive Assistance Engine started successfully")
        yield
        
    except Exception as e:
        logger.error("Failed to start Proactive Assistance Engine", error=str(e))
        raise
    finally:
        if assistance_orchestrator:
            await assistance_orchestrator.cleanup()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Proactive Assistance Engine",
        description="Real-time proactive assistance orchestration for MantraPath V3",
        version="1.0.0",
        lifespan=lifespan
    )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        if assistance_orchestrator is None:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        health_status = await assistance_orchestrator.get_health_status()
        return health_status
    
    @app.post("/api/v1/assistance/evaluate/{user_id}")
    async def evaluate_assistance_needs(user_id: str):
        """Evaluate and potentially trigger proactive assistance for user"""
        if assistance_orchestrator is None:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        assistance_evaluation = await assistance_orchestrator.evaluate_user_assistance_needs(user_id)
        return assistance_evaluation
    
    return app
```

#### 1.2: Core Orchestrator Implementation (2h)

**Objective**: Create the main orchestration engine that coordinates existing services

```python
# File: backend/services/proactive_assistance_engine/src/core/assistance_orchestrator.py
import asyncio
import httpx
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import structlog

from src.integrations.ai_event_processor_client import AIEventProcessorClient
from src.integrations.ai_context_store_client import AIContextStoreClient
from src.integrations.cultural_intelligence_client import CulturalIntelligenceClient
from src.models.assistance_models import AssistanceEvaluation, UserAssistanceNeeds

logger = structlog.get_logger(__name__)

class ProactiveAssistanceOrchestrator:
    """
    Main orchestrator for proactive assistance that coordinates existing services
    """
    
    def __init__(self):
        self.ai_event_client = None
        self.context_store_client = None
        self.cultural_client = None
        self.is_initialized = False
        
        # Assistance configuration
        self.assistance_config = {
            "evaluation_interval_minutes": 30,
            "min_assistance_gap_hours": 2,
            "cultural_sensitivity_threshold": 0.9,
            "timing_confidence_threshold": 0.7
        }
    
    async def initialize(self):
        """Initialize orchestrator with service clients"""
        try:
            # Initialize service clients
            self.ai_event_client = AIEventProcessorClient("http://localhost:8014")
            self.context_store_client = AIContextStoreClient("http://localhost:8016")
            self.cultural_client = CulturalIntelligenceClient("http://localhost:8017")
            
            # Test connections
            await self._test_service_connections()
            
            self.is_initialized = True
            logger.info("Proactive Assistance Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize orchestrator", error=str(e))
            raise
    
    async def evaluate_user_assistance_needs(self, user_id: str) -> AssistanceEvaluation:
        """
        Main method: Evaluate if user needs proactive assistance
        """
        try:
            if not self.is_initialized:
                raise RuntimeError("Orchestrator not initialized")
            
            logger.info("Evaluating assistance needs", user_id=user_id)
            
            # Step 1: Get user context from AI Context Store
            user_context = await self.context_store_client.get_user_context(user_id)
            
            # Step 2: Get intervention analysis from AI Event Processor
            intervention_analysis = await self.ai_event_client.analyze_intervention_needs(user_id)
            
            # Step 3: Evaluate timing appropriateness
            timing_evaluation = await self._evaluate_optimal_timing(user_id, user_context)
            
            # Step 4: Get cultural considerations
            cultural_evaluation = await self._evaluate_cultural_appropriateness(
                user_id, user_context, intervention_analysis
            )
            
            # Step 5: Make final assistance decision
            assistance_decision = await self._make_assistance_decision(
                user_id, intervention_analysis, timing_evaluation, cultural_evaluation
            )
            
            # Step 6: If assistance needed, prepare assistance content
            assistance_content = None
            if assistance_decision["should_provide_assistance"]:
                assistance_content = await self._prepare_assistance_content(
                    user_id, intervention_analysis, cultural_evaluation
                )
            
            # Create comprehensive evaluation result
            evaluation = AssistanceEvaluation(
                user_id=user_id,
                evaluation_timestamp=datetime.now(timezone.utc),
                intervention_analysis=intervention_analysis,
                timing_evaluation=timing_evaluation,
                cultural_evaluation=cultural_evaluation,
                assistance_decision=assistance_decision,
                assistance_content=assistance_content,
                confidence_score=assistance_decision.get("confidence", 0.0)
            )
            
            logger.info(
                "Assistance evaluation completed",
                user_id=user_id,
                assistance_needed=assistance_decision["should_provide_assistance"],
                confidence=assistance_decision.get("confidence", 0.0)
            )
            
            return evaluation
            
        except Exception as e:
            logger.error("Assistance evaluation failed", error=str(e), user_id=user_id)
            # Return safe fallback evaluation
            return self._create_fallback_evaluation(user_id)
```

#### 1.3: Service Integration Clients (2h)

**Objective**: Create HTTP clients to integrate with existing services

```python
# File: backend/services/proactive_assistance_engine/src/integrations/ai_event_processor_client.py
import httpx
import structlog
from typing import Dict, Any

logger = structlog.get_logger(__name__)

class AIEventProcessorClient:
    """Client for AI Event Processor service integration"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def analyze_intervention_needs(self, user_id: str) -> Dict[str, Any]:
        """Get intervention analysis from AI Event Processor"""
        try:
            # Use existing predictive engine endpoint (need to add to AI Event Processor)
            response = await self.client.post(
                f"{self.base_url}/api/v1/intervention/analyze/{user_id}"
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error("Failed to get intervention analysis", error=str(e), user_id=user_id)
            return self._create_fallback_analysis()
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Check AI Event Processor health"""
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def _create_fallback_analysis(self) -> Dict[str, Any]:
        """Create safe fallback when service is unavailable"""
        return {
            "intervention_needed": False,
            "confidence": 0.0,
            "intervention_type": None,
            "urgency_level": "none",
            "recommended_actions": [],
            "risk_factors": {},
            "fallback_reason": "Service unavailable"
        }
```

```python
# File: backend/services/proactive_assistance_engine/src/integrations/ai_context_store_client.py
import httpx
import structlog
from typing import Dict, Any, Optional

logger = structlog.get_logger(__name__)

class AIContextStoreClient:
    """Client for AI Context Store service integration"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user context"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/context/user/{user_id}"
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error("Failed to get user context", error=str(e), user_id=user_id)
            return self._create_fallback_context(user_id)
    
    async def get_user_intelligence_insights(self, user_id: str) -> Dict[str, Any]:
        """Get AI intelligence insights for user"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/intelligence/insights/{user_id}"
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error("Failed to get intelligence insights", error=str(e), user_id=user_id)
            return {"insights": [], "confidence": 0.0}
    
    def _create_fallback_context(self, user_id: str) -> Dict[str, Any]:
        """Create minimal context when service unavailable"""
        return {
            "user_id": user_id,
            "mood_context": {"current_mood_score": 5.0, "mood_trend": "stable"},
            "behavioral_patterns": {},
            "cultural_profile": {"primary_culture": "unknown", "communication_style": "neutral"},
            "recent_interactions": [],
            "fallback_reason": "Context service unavailable"
        }
```

### Task 2: Timing Prediction Enhancement (2h)

#### 2.1: Comprehensive Timing System (2h)

**Objective**: Build comprehensive timing prediction using existing behavioral data

```python
# File: backend/services/proactive_assistance_engine/src/core/timing_predictor.py
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger(__name__)

class ComprehensiveTimingPredictor:
    """
    Enhanced timing prediction system that uses existing behavioral data
    """
    
    def __init__(self):
        self.timing_config = {
            "min_gap_between_assistance_hours": 2,
            "preferred_time_windows": {
                "morning": {"start": 8, "end": 11, "weight": 0.8},
                "afternoon": {"start": 14, "end": 17, "weight": 0.9},
                "evening": {"start": 18, "end": 21, "weight": 0.7}
            },
            "cultural_timing_adaptations": {
                "collectivist": {"family_time_awareness": True, "respect_meal_times": True},
                "individualist": {"personal_schedule_focus": True, "work_hour_respect": True}
            }
        }
    
    async def evaluate_optimal_timing(
        self, 
        user_id: str, 
        user_context: Dict[str, Any],
        intervention_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate if current timing is optimal for proactive assistance
        """
        try:
            current_time = datetime.now(timezone.utc)
            
            # Step 1: Check recent assistance history
            recent_assistance_check = await self._check_recent_assistance_gap(user_id, current_time)
            
            # Step 2: Analyze user activity patterns
            activity_analysis = await self._analyze_current_activity_state(user_context, current_time)
            
            # Step 3: Cultural timing considerations
            cultural_timing = await self._evaluate_cultural_timing_appropriateness(
                user_context.get("cultural_profile", {}), current_time
            )
            
            # Step 4: Urgency override check
            urgency_override = intervention_analysis.get("urgency_level") in ["critical", "high"]
            
            # Step 5: Calculate overall timing score
            timing_score = await self._calculate_timing_appropriateness_score(
                recent_assistance_check, activity_analysis, cultural_timing, urgency_override
            )
            
            # Step 6: Make timing decision
            timing_decision = {
                "timing_appropriate": timing_score > 0.7 or urgency_override,
                "timing_confidence": timing_score,
                "can_proceed": timing_score > 0.5 or urgency_override,
                "recommended_delay_minutes": 0 if urgency_override else max(0, int((0.7 - timing_score) * 60))
            }
            
            return {
                "timing_evaluation": timing_decision,
                "recent_assistance_check": recent_assistance_check,
                "activity_analysis": activity_analysis,
                "cultural_timing": cultural_timing,
                "urgency_override": urgency_override,
                "timing_score": timing_score,
                "evaluation_timestamp": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error("Timing evaluation failed", error=str(e), user_id=user_id)
            return self._create_fallback_timing_evaluation()
    
    async def _analyze_current_activity_state(
        self, 
        user_context: Dict[str, Any], 
        current_time: datetime
    ) -> Dict[str, Any]:
        """
        Analyze user's current activity state for timing appropriateness
        """
        try:
            recent_interactions = user_context.get("recent_interactions", [])
            
            # Check recent platform activity
            last_interaction_time = None
            if recent_interactions:
                last_interaction = recent_interactions[-1]
                last_interaction_time = datetime.fromisoformat(
                    last_interaction.get("timestamp", current_time.isoformat())
                )
            
            # Calculate engagement level
            engagement_level = self._calculate_engagement_level(recent_interactions, current_time)
            
            # Check time of day appropriateness
            time_appropriateness = self._evaluate_time_of_day_appropriateness(current_time)
            
            # Determine if user seems available/receptive
            receptiveness_score = self._calculate_user_receptiveness(
                engagement_level, last_interaction_time, current_time
            )
            
            return {
                "engagement_level": engagement_level,
                "last_interaction_minutes_ago": (
                    (current_time - last_interaction_time).total_seconds() / 60
                    if last_interaction_time else None
                ),
                "time_of_day_appropriateness": time_appropriateness,
                "user_receptiveness_score": receptiveness_score,
                "activity_confidence": min(0.9, engagement_level + time_appropriateness) / 2
            }
            
        except Exception as e:
            logger.error("Activity analysis failed", error=str(e))
            return {"engagement_level": 0.5, "user_receptiveness_score": 0.5, "activity_confidence": 0.3}
```

### Task 3: Contextual Help System (2h)

#### 3.1: Help Content and Matching System (2h)

**Objective**: Create contextual help system with basic content matching

```python
# File: backend/services/proactive_assistance_engine/src/core/contextual_help_engine.py
import asyncio
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger(__name__)

class ContextualHelpEngine:
    """
    Contextual help system that matches user needs with appropriate assistance content
    """
    
    def __init__(self):
        # Initialize with basic help content database
        self.help_content_db = self._initialize_help_content()
        self.help_matching_config = {
            "relevance_threshold": 0.6,
            "max_help_suggestions": 3,
            "cultural_adaptation_required": True
        }
    
    async def find_contextual_help(
        self, 
        user_context: Dict[str, Any],
        intervention_analysis: Dict[str, Any],
        cultural_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Find contextually relevant help content based on user needs
        """
        try:
            # Step 1: Analyze user's current needs based on intervention analysis
            user_needs = await self._analyze_user_needs(intervention_analysis, user_context)
            
            # Step 2: Match needs to available help content
            relevant_help = await self._match_help_content(user_needs)
            
            # Step 3: Culturally adapt help content
            culturally_adapted_help = await self._adapt_help_for_culture(
                relevant_help, cultural_profile
            )
            
            # Step 4: Rank and filter help suggestions
            prioritized_help = await self._prioritize_help_suggestions(
                culturally_adapted_help, user_needs
            )
            
            return prioritized_help[:self.help_matching_config["max_help_suggestions"]]
            
        except Exception as e:
            logger.error("Contextual help matching failed", error=str(e))
            return self._get_fallback_help_content()
    
    def _initialize_help_content(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Initialize basic help content database
        """
        return {
            "crisis_intervention": [
                {
                    "id": "crisis_support_001",
                    "title": "Immediate Crisis Support",
                    "content": "You're not alone in this difficult moment. Immediate support is available.",
                    "actions": [
                        "Contact crisis helpline: 988",
                        "Reach out to trusted friend or family",
                        "Contact healthcare provider",
                        "Go to emergency room if in immediate danger"
                    ],
                    "urgency": "critical",
                    "cultural_adaptations": {
                        "collectivist": "Include family support emphasis",
                        "individualist": "Emphasize personal agency and professional help"
                    }
                }
            ],
            "mood_support": [
                {
                    "id": "mood_boost_001",
                    "title": "Gentle Mood Support",
                    "content": "I've noticed you might be going through a challenging time. Here are some gentle ways to support yourself.",
                    "actions": [
                        "Try a 5-minute breathing exercise",
                        "Write down three things you're grateful for",
                        "Take a short walk if possible",
                        "Reach out to someone you trust"
                    ],
                    "urgency": "low",
                    "cultural_adaptations": {
                        "collectivist": "Emphasize community and family support",
                        "individualist": "Focus on self-care and personal strategies"
                    }
                }
            ],
            "proactive_check_in": [
                {
                    "id": "check_in_001",
                    "title": "Gentle Check-In",
                    "content": "How are you feeling today? I'm here to support you on your wellness journey.",
                    "actions": [
                        "Share how you're feeling",
                        "Review your recent mood patterns",
                        "Set a small wellness goal for today",
                        "Connect with supportive resources"
                    ],
                    "urgency": "none",
                    "cultural_adaptations": {
                        "high_context": "Use more indirect, gentle language",
                        "low_context": "Be direct and clear about support options"
                    }
                }
            ]
        }
    
    async def _analyze_user_needs(
        self, 
        intervention_analysis: Dict[str, Any], 
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze user's current needs based on intervention analysis
        """
        intervention_type = intervention_analysis.get("intervention_type", "none")
        urgency_level = intervention_analysis.get("urgency_level", "none")
        risk_factors = intervention_analysis.get("risk_factors", {})
        
        # Map intervention analysis to help categories
        help_categories = []
        if intervention_type == "crisis_intervention":
            help_categories.append("crisis_intervention")
        elif intervention_type == "proactive_support":
            help_categories.append("mood_support")
        elif intervention_type == "gentle_check_in":
            help_categories.append("proactive_check_in")
        else:
            help_categories.append("proactive_check_in")  # Default
        
        return {
            "primary_help_categories": help_categories,
            "urgency_level": urgency_level,
            "risk_factors": risk_factors,
            "user_preferences": user_context.get("assistance_preferences", {})
        }
```

### Task 4: Cultural Sensitivity Integration (1h)

#### 4.1: Cultural Appropriateness System (1h)

```python
# File: backend/services/proactive_assistance_engine/src/core/cultural_sensitivity_engine.py
import asyncio
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger(__name__)

class CulturalSensitivityEngine:
    """
    Ensures all proactive assistance respects cultural norms and preferences
    """
    
    def __init__(self):
        self.cultural_guidelines = self._initialize_cultural_guidelines()
        self.sensitivity_thresholds = {
            "minimum_cultural_confidence": 0.7,
            "require_adaptation": True,
            "respect_cultural_timing": True
        }
    
    async def evaluate_cultural_appropriateness(
        self,
        assistance_content: Dict[str, Any],
        cultural_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate and adapt assistance content for cultural appropriateness
        """
        try:
            primary_culture = cultural_profile.get("primary_culture", "unknown")
            communication_style = cultural_profile.get("communication_style", "neutral")
            
            # Step 1: Check cultural guidelines for assistance type
            cultural_guidelines = self.cultural_guidelines.get(primary_culture, {})
            
            # Step 2: Evaluate content appropriateness
            content_evaluation = await self._evaluate_content_appropriateness(
                assistance_content, cultural_guidelines
            )
            
            # Step 3: Check timing appropriateness
            timing_evaluation = await self._evaluate_timing_appropriateness(
                cultural_profile, assistance_content
            )
            
            # Step 4: Adapt content if needed
            adapted_content = await self._adapt_content_for_culture(
                assistance_content, cultural_profile, cultural_guidelines
            )
            
            # Step 5: Calculate overall cultural appropriateness score
            appropriateness_score = (
                content_evaluation["appropriateness_score"] * 0.6 +
                timing_evaluation["appropriateness_score"] * 0.4
            )
            
            return {
                "culturally_appropriate": appropriateness_score > self.sensitivity_thresholds["minimum_cultural_confidence"],
                "appropriateness_score": appropriateness_score,
                "content_evaluation": content_evaluation,
                "timing_evaluation": timing_evaluation,
                "adapted_content": adapted_content,
                "cultural_considerations": cultural_guidelines.get("assistance_considerations", [])
            }
            
        except Exception as e:
            logger.error("Cultural appropriateness evaluation failed", error=str(e))
            return self._create_fallback_cultural_evaluation()
    
    def _initialize_cultural_guidelines(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize cultural guidelines for assistance
        """
        return {
            "collectivist": {
                "assistance_considerations": [
                    "Emphasize family and community support",
                    "Respect hierarchical relationships",
                    "Consider collective decision-making preferences",
                    "Be mindful of face-saving concerns"
                ],
                "communication_preferences": {
                    "directness": "indirect",
                    "context_level": "high",
                    "family_involvement": "preferred"
                },
                "timing_preferences": {
                    "family_time_respect": True,
                    "meal_time_awareness": True,
                    "religious_time_consideration": True
                }
            },
            "individualist": {
                "assistance_considerations": [
                    "Emphasize personal agency and choice",
                    "Respect individual privacy",
                    "Focus on self-directed solutions",
                    "Provide clear, direct information"
                ],
                "communication_preferences": {
                    "directness": "direct",
                    "context_level": "low",
                    "professional_focus": "preferred"
                },
                "timing_preferences": {
                    "work_hour_respect": True,
                    "personal_schedule_focus": True,
                    "efficiency_valued": True
                }
            }
        }
```

### Task 5: Comprehensive Testing (1h)

#### 5.1: End-to-End Testing (1h)

```python
# File: backend/services/proactive_assistance_engine/tests/test_proactive_assistance_integration.py
import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from src.core.assistance_orchestrator import ProactiveAssistanceOrchestrator
from src.models.assistance_models import AssistanceEvaluation

class TestProactiveAssistanceIntegration:
    """
    Integration tests for the complete proactive assistance system
    """
    
    @pytest.fixture
    async def assistance_orchestrator(self):
        """Create assistance orchestrator with mocked service clients"""
        orchestrator = ProactiveAssistanceOrchestrator()
        
        # Mock service clients
        orchestrator.ai_event_client = AsyncMock()
        orchestrator.context_store_client = AsyncMock()
        orchestrator.cultural_client = AsyncMock()
        orchestrator.is_initialized = True
        
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_complete_assistance_evaluation_flow(self, assistance_orchestrator):
        """Test complete assistance evaluation from start to finish"""
        
        # Setup mock responses
        user_id = "test_user_123"
        
        # Mock AI Context Store response
        assistance_orchestrator.context_store_client.get_user_context.return_value = {
            "user_id": user_id,
            "mood_context": {"current_mood_score": 3.0, "mood_trend": "declining"},
            "cultural_profile": {"primary_culture": "collectivist", "communication_style": "indirect"},
            "recent_interactions": [
                {"timestamp": datetime.now(timezone.utc).isoformat(), "service": "mood", "type": "entry"}
            ]
        }
        
        # Mock AI Event Processor response
        assistance_orchestrator.ai_event_client.analyze_intervention_needs.return_value = {
            "intervention_needed": True,
            "confidence": 0.85,
            "intervention_type": "proactive_support",
            "urgency_level": "medium",
            "recommended_actions": ["Gentle check-in", "Mood support resources"],
            "risk_factors": {"mood_decline": {"score": 0.7}}
        }
        
        # Execute assistance evaluation
        evaluation = await assistance_orchestrator.evaluate_user_assistance_needs(user_id)
        
        # Verify evaluation structure
        assert isinstance(evaluation, AssistanceEvaluation)
        assert evaluation.user_id == user_id
        assert evaluation.intervention_analysis["intervention_needed"] is True
        assert evaluation.confidence_score > 0.0
        
        # Verify service interactions
        assistance_orchestrator.context_store_client.get_user_context.assert_called_once_with(user_id)
        assistance_orchestrator.ai_event_client.analyze_intervention_needs.assert_called_once_with(user_id)
        
    @pytest.mark.asyncio
    async def test_cultural_sensitivity_integration(self, assistance_orchestrator):
        """Test that cultural considerations are properly integrated"""
        
        user_id = "test_user_cultural"
        
        # Setup cultural context
        assistance_orchestrator.context_store_client.get_user_context.return_value = {
            "user_id": user_id,
            "cultural_profile": {"primary_culture": "collectivist", "communication_style": "high_context"}
        }
        
        assistance_orchestrator.ai_event_client.analyze_intervention_needs.return_value = {
            "intervention_needed": True,
            "intervention_type": "gentle_check_in",
            "urgency_level": "low"
        }
        
        evaluation = await assistance_orchestrator.evaluate_user_assistance_needs(user_id)
        
        # Verify cultural considerations are included
        assert "cultural_evaluation" in evaluation.model_dump()
        assert evaluation.cultural_evaluation is not None
        
    @pytest.mark.asyncio
    async def test_timing_appropriateness_evaluation(self, assistance_orchestrator):
        """Test timing evaluation functionality"""
        
        user_id = "test_user_timing"
        
        # Setup context with recent interaction
        recent_time = datetime.now(timezone.utc).isoformat()
        assistance_orchestrator.context_store_client.get_user_context.return_value = {
            "user_id": user_id,
            "recent_interactions": [{"timestamp": recent_time, "service": "chat"}]
        }
        
        assistance_orchestrator.ai_event_client.analyze_intervention_needs.return_value = {
            "intervention_needed": True,
            "urgency_level": "low"
        }
        
        evaluation = await assistance_orchestrator.evaluate_user_assistance_needs(user_id)
        
        # Verify timing evaluation is included
        assert "timing_evaluation" in evaluation.model_dump()
        assert evaluation.timing_evaluation is not None
        
    @pytest.mark.asyncio
    async def test_crisis_intervention_urgency_override(self, assistance_orchestrator):
        """Test that crisis situations override timing restrictions"""
        
        user_id = "test_user_crisis"
        
        assistance_orchestrator.context_store_client.get_user_context.return_value = {
            "user_id": user_id,
            "mood_context": {"current_mood_score": 1.0}
        }
        
        # Crisis situation
        assistance_orchestrator.ai_event_client.analyze_intervention_needs.return_value = {
            "intervention_needed": True,
            "intervention_type": "crisis_intervention",
            "urgency_level": "critical",
            "confidence": 0.95
        }
        
        evaluation = await assistance_orchestrator.evaluate_user_assistance_needs(user_id)
        
        # Verify crisis intervention can proceed regardless of timing
        assert evaluation.assistance_decision["should_provide_assistance"] is True
        assert evaluation.timing_evaluation["urgency_override"] is True
        
    @pytest.mark.asyncio
    async def test_service_failure_graceful_degradation(self, assistance_orchestrator):
        """Test graceful degradation when services are unavailable"""
        
        user_id = "test_user_degradation"
        
        # Simulate service failure
        assistance_orchestrator.context_store_client.get_user_context.side_effect = Exception("Service unavailable")
        
        evaluation = await assistance_orchestrator.evaluate_user_assistance_needs(user_id)
        
        # Should still return evaluation, but with lower confidence
        assert isinstance(evaluation, AssistanceEvaluation)
        assert evaluation.user_id == user_id
        assert evaluation.confidence_score < 0.5  # Lower confidence due to service unavailability
```

## Service Integration Points

### Required API Endpoints in Existing Services

#### 1. AI Event Processor (Port 8014)
**NEW ENDPOINT NEEDED**:
```python
@app.post("/api/v1/intervention/analyze/{user_id}")
async def analyze_intervention_needs_endpoint(user_id: str):
    """Expose predictive intervention analysis"""
    if not predictive_engine:
        raise HTTPException(status_code=503, detail="Predictive engine not available")
    
    analysis_result = await predictive_engine.analyze_intervention_needs(user_id)
    return analysis_result
```

#### 2. AI Context Store (Port 8016) - ALREADY EXISTS
- `GET /api/v1/context/user/{user_id}` ✅
- `GET /api/v1/intelligence/insights/{user_id}` ✅

### Event Integration

#### Subscribe to Events:
- `mood.entry_created` - Trigger assistance evaluation
- `journal.entry_created` - Trigger assistance evaluation  
- `voice.crisis_detected` - Immediate assistance evaluation
- `chat.crisis_detected` - Immediate assistance evaluation

#### Publish Events:
- `assistance.evaluation_completed` - Assistance evaluation result
- `assistance.triggered` - Assistance provided to user
- `assistance.user_response` - User acceptance/rejection tracking

## Deployment and Configuration

### Service Configuration
```yaml
# File: backend/services/proactive_assistance_engine/config/assistance.yaml
proactive_assistance:
  evaluation:
    interval_minutes: 30
    min_gap_between_assistance_hours: 2
    cultural_sensitivity_threshold: 0.9
    timing_confidence_threshold: 0.7
  
  timing:
    preferred_windows:
      morning: {start: 8, end: 11, weight: 0.8}
      afternoon: {start: 14, end: 17, weight: 0.9}  
      evening: {start: 18, end: 21, weight: 0.7}
  
  cultural:
    adaptation_required: true
    minimum_confidence: 0.7
    supported_cultures: ["collectivist", "individualist"]
  
  integration:
    ai_event_processor_url: "http://localhost:8014"
    ai_context_store_url: "http://localhost:8016"
    timeout_seconds: 30
```

### Docker Configuration
```dockerfile
# File: backend/services/proactive_assistance_engine/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8018

CMD ["uvicorn", "main:create_app", "--host", "0.0.0.0", "--port", "8018", "--reload"]
```

## Testing Strategy

### Test Categories
1. **Unit Tests** (2h): Individual components
2. **Integration Tests** (1h): Service interactions  
3. **End-to-End Tests** (30min): Complete assistance flows
4. **Performance Tests** (30min): Response time validation
5. **Cultural Sensitivity Tests** (1h): Cultural appropriateness validation

### Success Criteria
- [ ] >85% intervention detection accuracy (using existing predictive engine)
- [ ] >75% timing prediction accuracy  
- [ ] <10% false positive rate
- [ ] <500ms assistance evaluation time
- [ ] >90% cultural appropriateness score

## Risk Mitigation

### High-Priority Risks
1. **Scope Creep**: Stick to orchestration, leverage existing services
2. **Service Dependencies**: Implement graceful degradation for all service calls
3. **Cultural Sensitivity**: Start with basic adaptations, iterate based on feedback
4. **Performance**: Use async/await throughout, implement caching for repeated calls

### Success Dependencies
1. **AI Event Processor endpoint**: Need to expose predictive engine via API
2. **Testing Infrastructure**: Need test data for cultural scenarios
3. **User Feedback Mechanism**: For continuous improvement of assistance appropriateness

## Updated Sprint Estimation

**Original Estimate**: 8 story points  
**Updated Estimate**: 12-14 story points (6 days for Mid Dev 2)

**Recommendation**: 
1. Focus on core orchestration and basic help matching for Sprint 2
2. Advanced cultural adaptation and help content expansion for Sprint 3
3. Request additional development time or split into two stories

## Next Steps
1. **Immediate**: Create service structure and basic orchestration
2. **Week 1**: Implement timing and cultural sensitivity  
3. **Week 2**: Testing and refinement
4. **Week 3**: Integration with frontend and user feedback collection

---

*This execution plan provides a realistic, implementable approach to the Proactive Assistance Engine that leverages existing services while creating the missing orchestration layer.*
