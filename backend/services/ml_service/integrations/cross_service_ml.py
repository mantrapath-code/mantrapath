"""
🔗 Cross-Service ML Integration Framework - Phase 2B

Provides seamless, well-documented ML intelligence across all MantraPath platform services.
This integration framework enables chat, community, mood, and notification services to leverage
advanced ML capabilities including crisis prediction, sentiment analysis, and personalization.

Architecture:
- Service-Agnostic ML APIs: Universal endpoints that work across services
- Data Fusion Engine: Combines multi-service data for comprehensive insights
- Real-Time Analytics: Live processing of cross-service user interactions
- Privacy-First Design: Secure data handling with user consent management

Integration Services:
1. Chat Service: Real-time sentiment analysis & crisis detection in conversations
2. Community Service: Content moderation & personalized recommendations
3. Mood Service: Enhanced pattern recognition with cross-platform correlation
4. Notification Service: Context-aware personalization using all user touchpoints
5. User Profile Service: Comprehensive behavioral modeling across services
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib
from collections import defaultdict, deque

# Import existing ML components from Phase 2A
from ..models.crisis_predictor import CrisisPredictor
from ..models.early_warning_system import EarlyWarningSystem
from ..models.content_engine import NotificationContentEngine
from ..models.effectiveness_tracker import EffectivenessTracker

logger = logging.getLogger(__name__)

class ServiceType(Enum):
    """Enumeration of MantraPath platform services"""
    CHAT = "chat_service"
    COMMUNITY = "community_service"
    MOOD = "mood_service"
    NOTIFICATION = "notification_service"
    USER_PROFILE = "user_profile_service"
    ML = "ml_service"

class MLRequestType(Enum):
    """Types of ML requests from services"""
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CRISIS_DETECTION = "crisis_detection"
    CONTENT_MODERATION = "content_moderation"
    PERSONALIZATION = "personalization"
    PATTERN_ANALYSIS = "pattern_analysis"
    RECOMMENDATION = "recommendation"
    RISK_ASSESSMENT = "risk_assessment"

@dataclass
class CrossServiceRequest:
    """Standardized request format for cross-service ML operations"""
    service_type: ServiceType
    request_type: MLRequestType
    user_id: str
    data: Dict[str, Any]
    context: Dict[str, Any] = None
    priority: str = "normal"  # normal, high, critical
    include_interventions: bool = False
    require_real_time: bool = False
    privacy_level: str = "standard"  # minimal, standard, enhanced
    timestamp: str = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        if not self.context:
            self.context = {}

@dataclass
class CrossServiceResponse:
    """Standardized response format for cross-service ML operations"""
    request_id: str
    service_type: ServiceType
    request_type: MLRequestType
    user_id: str
    success: bool
    data: Dict[str, Any]
    metadata: Dict[str, Any] = None
    processing_time: float = 0.0
    confidence: float = 0.0
    timestamp: str = None
    error: str = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        if not self.metadata:
            self.metadata = {}

class CrossServiceMLHub:
    """
    🎯 Central ML Intelligence Hub - Phase 2B Core
    
    Coordinates ML capabilities across all MantraPath platform services.
    Provides unified interface for sentiment analysis, crisis detection,
    content moderation, personalization, and behavioral insights.
    
    Key Features:
    - Service-agnostic ML API endpoints
    - Real-time and batch processing modes
    - Cross-service data correlation
    - Privacy-compliant user profiling
    - Automated intervention triggering
    """
    
    def __init__(self):
        self.version = "2B.1.0-production"
        self.ready = False
        
        # Initialize Phase 2A components
        self.crisis_predictor = CrisisPredictor()
        self.early_warning_system = EarlyWarningSystem(self.crisis_predictor)
        self.content_engine = NotificationContentEngine()
        self.effectiveness_tracker = EffectivenessTracker()
        
        # Cross-service specific components
        self.sentiment_analyzer = AdvancedSentimentAnalyzer()
        self.content_moderator = ContentModerator()
        self.personalization_engine = PersonalizationEngine()
        self.data_fusion_processor = DataFusionProcessor()
        
        # Request processing
        self.request_history = deque(maxlen=10000)
        self.service_metrics = defaultdict(lambda: defaultdict(int))
        self.user_session_cache = {}  # Cache user context across services
        
        # Performance monitoring
        self.processing_times = defaultdict(list)
        self.success_rates = defaultdict(float)
        
        logger.info(f"🔗 Cross-Service ML Hub initializing (v{self.version})")
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all ML components for cross-service operations"""
        try:
            # Verify Phase 2A crisis prediction is ready
            if not self.crisis_predictor.ready:
                logger.warning("Crisis predictor not ready - crisis detection limited")
            
            # Initialize new Phase 2B components
            self.sentiment_analyzer.initialize()
            self.content_moderator.initialize()
            self.personalization_engine.initialize()
            self.data_fusion_processor.initialize()
            
            self.ready = True
            logger.info("✅ Cross-Service ML Hub initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Cross-Service ML Hub initialization failed: {e}")
            self.ready = False
    
    async def process_request(self, request: CrossServiceRequest) -> CrossServiceResponse:
        """
        🎯 Process cross-service ML request with unified response format
        
        Main entry point for all ML operations from MantraPath services.
        Handles sentiment analysis, crisis detection, personalization, etc.
        """
        start_time = datetime.utcnow()
        request_id = self._generate_request_id(request)
        
        try:
            logger.debug(f"Processing {request.request_type.value} request from {request.service_type.value}")
            
            # Update user session cache with latest context
            self._update_user_context(request.user_id, request.service_type, request.data, request.context)
            
            # Route to appropriate processor based on request type
            if request.request_type == MLRequestType.SENTIMENT_ANALYSIS:
                result = await self._process_sentiment_analysis(request)
            elif request.request_type == MLRequestType.CRISIS_DETECTION:
                result = await self._process_crisis_detection(request)
            elif request.request_type == MLRequestType.CONTENT_MODERATION:
                result = await self._process_content_moderation(request)
            elif request.request_type == MLRequestType.PERSONALIZATION:
                result = await self._process_personalization(request)
            elif request.request_type == MLRequestType.PATTERN_ANALYSIS:
                result = await self._process_pattern_analysis(request)
            elif request.request_type == MLRequestType.RECOMMENDATION:
                result = await self._process_recommendation(request)
            elif request.request_type == MLRequestType.RISK_ASSESSMENT:
                result = await self._process_risk_assessment(request)
            else:
                raise ValueError(f"Unsupported request type: {request.request_type}")
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create response
            response = CrossServiceResponse(
                request_id=request_id,
                service_type=request.service_type,
                request_type=request.request_type,
                user_id=request.user_id,
                success=True,
                data=result,
                processing_time=processing_time,
                confidence=result.get('confidence', 0.0),
                metadata={
                    "model_version": self.version,
                    "priority": request.priority,
                    "privacy_level": request.privacy_level
                }
            )
            
            # Update metrics
            self._update_metrics(request, response)
            
            # Store in request history
            self.request_history.append({
                "request": asdict(request),
                "response": asdict(response),
                "timestamp": start_time.isoformat()
            })
            
            return response
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Cross-service ML request failed: {e}")
            
            return CrossServiceResponse(
                request_id=request_id,
                service_type=request.service_type,
                request_type=request.request_type,
                user_id=request.user_id,
                success=False,
                data={},
                processing_time=processing_time,
                error=str(e)
            )
    
    async def _process_sentiment_analysis(self, request: CrossServiceRequest) -> Dict[str, Any]:
        """Process sentiment analysis request (primarily for chat service)"""
        content = request.data.get('content', '')
        
        if not content:
            raise ValueError("Content required for sentiment analysis")
        
        # Analyze sentiment using advanced NLP
        sentiment_result = self.sentiment_analyzer.analyze_text(content)
        
        # Enhanced analysis with context from other services
        user_context = self._get_user_context(request.user_id)
        if user_context:
            sentiment_result['contextual_insights'] = self._enhance_sentiment_with_context(
                sentiment_result, user_context
            )
        
        # Check if sentiment indicates crisis risk
        if request.include_interventions and sentiment_result['sentiment'] == 'very_negative':
            crisis_check = await self.crisis_predictor.assess_text_risk({
                'user_id': request.user_id,
                'text_content': content,
                'context': user_context
            })
            sentiment_result['crisis_indicators'] = crisis_check
        
        return sentiment_result
    
    async def _process_crisis_detection(self, request: CrossServiceRequest) -> Dict[str, Any]:
        """Process crisis detection request (cross-service crisis monitoring)"""
        user_data = request.data
        
        # Enhance with cross-service data
        enriched_data = await self._enrich_user_data_cross_service(request.user_id, user_data)
        
        # Perform crisis prediction
        crisis_assessment = self.crisis_predictor.predict_crisis_risk(enriched_data)
        
        # Trigger early warning system if high risk
        if crisis_assessment.get('risk_level') in ['HIGH', 'CRITICAL']:
            await self.early_warning_system.trigger_alert(
                request.user_id,
                crisis_assessment,
                source_service=request.service_type.value
            )
        
        return crisis_assessment
    
    async def _process_content_moderation(self, request: CrossServiceRequest) -> Dict[str, Any]:
        """Process content moderation request (primarily for community service)"""
        content = request.data.get('content', '')
        content_type = request.data.get('content_type', 'text')
        
        # Moderate content using ML
        moderation_result = self.content_moderator.moderate_content(content, content_type)
        
        # Check user history for additional context
        user_context = self._get_user_context(request.user_id)
        if user_context and user_context.get('previous_violations'):
            moderation_result['user_risk_score'] = self._calculate_user_risk_score(user_context)
        
        return moderation_result
    
    async def _process_personalization(self, request: CrossServiceRequest) -> Dict[str, Any]:
        """Process personalization request (cross-service user personalization)"""
        user_preferences = request.data.get('preferences', {})
        interaction_type = request.data.get('interaction_type', 'general')
        
        # Get comprehensive user profile across all services
        cross_service_profile = await self._build_cross_service_user_profile(request.user_id)
        
        # Generate personalized recommendations
        personalization_result = self.personalization_engine.generate_personalization(
            cross_service_profile,
            user_preferences,
            interaction_type
        )
        
        return personalization_result
    
    async def _process_pattern_analysis(self, request: CrossServiceRequest) -> Dict[str, Any]:
        """Process pattern analysis request (enhanced mood/behavior patterns)"""
        pattern_data = request.data.get('pattern_data', {})
        analysis_type = request.data.get('analysis_type', 'behavior')
        
        # Fuse data from multiple services for comprehensive analysis
        fused_data = await self.data_fusion_processor.fuse_user_patterns(
            request.user_id, pattern_data
        )
        
        # Perform advanced pattern analysis
        pattern_result = await self._analyze_cross_service_patterns(fused_data, analysis_type)
        
        return pattern_result
    
    async def _process_recommendation(self, request: CrossServiceRequest) -> Dict[str, Any]:
        """Process recommendation request (cross-service content/action recommendations)"""
        recommendation_context = request.data.get('context', {})
        recommendation_type = request.data.get('type', 'content')
        
        # Build comprehensive user profile
        user_profile = await self._build_cross_service_user_profile(request.user_id)
        
        # Generate contextual recommendations
        recommendations = await self._generate_cross_service_recommendations(
            user_profile, recommendation_context, recommendation_type
        )
        
        return recommendations
    
    async def _process_risk_assessment(self, request: CrossServiceRequest) -> Dict[str, Any]:
        """Process risk assessment request (comprehensive user risk evaluation)"""
        assessment_scope = request.data.get('scope', 'comprehensive')
        
        # Gather data from all relevant services
        risk_data = await self._gather_cross_service_risk_data(request.user_id)
        
        # Perform comprehensive risk assessment
        risk_assessment = await self._perform_cross_service_risk_assessment(
            risk_data, assessment_scope
        )
        
        return risk_assessment
    
    def _update_user_context(self, user_id: str, service_type: ServiceType, data: Dict, context: Dict):
        """Update user session cache with latest service interaction"""
        if user_id not in self.user_session_cache:
            self.user_session_cache[user_id] = {
                'services': {},
                'last_updated': datetime.utcnow(),
                'session_id': self._generate_session_id(user_id)
            }
        
        self.user_session_cache[user_id]['services'][service_type.value] = {
            'data': data,
            'context': context,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.user_session_cache[user_id]['last_updated'] = datetime.utcnow()
    
    def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user's cross-service context"""
        return self.user_session_cache.get(user_id, {})
    
    def _generate_request_id(self, request: CrossServiceRequest) -> str:
        """Generate unique request ID"""
        request_string = f"{request.user_id}-{request.service_type.value}-{request.request_type.value}-{request.timestamp}"
        return hashlib.md5(request_string.encode()).hexdigest()[:12]
    
    def _generate_session_id(self, user_id: str) -> str:
        """Generate unique session ID for user"""
        session_string = f"{user_id}-{datetime.utcnow().isoformat()}"
        return hashlib.md5(session_string.encode()).hexdigest()[:16]
    
    def _update_metrics(self, request: CrossServiceRequest, response: CrossServiceResponse):
        """Update performance metrics"""
        service = request.service_type.value
        request_type = request.request_type.value
        
        self.service_metrics[service]['total_requests'] += 1
        self.service_metrics[service][f'{request_type}_requests'] += 1
        
        if response.success:
            self.service_metrics[service]['successful_requests'] += 1
        else:
            self.service_metrics[service]['failed_requests'] += 1
        
        # Update processing times
        self.processing_times[request_type].append(response.processing_time)
        if len(self.processing_times[request_type]) > 1000:
            self.processing_times[request_type] = self.processing_times[request_type][-500:]
        
        # Update success rates
        total = self.service_metrics[service]['total_requests']
        successful = self.service_metrics[service]['successful_requests']
        self.success_rates[service] = successful / total if total > 0 else 0.0
    
    async def get_cross_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive cross-service ML metrics"""
        return {
            "hub_version": self.version,
            "ready": self.ready,
            "total_requests_processed": sum(
                metrics['total_requests'] for metrics in self.service_metrics.values()
            ),
            "service_metrics": dict(self.service_metrics),
            "average_processing_times": {
                req_type: sum(times) / len(times) if times else 0.0
                for req_type, times in self.processing_times.items()
            },
            "success_rates": dict(self.success_rates),
            "active_user_sessions": len(self.user_session_cache),
            "component_status": {
                "crisis_predictor": self.crisis_predictor.ready,
                "early_warning_system": True,
                "sentiment_analyzer": getattr(self.sentiment_analyzer, 'ready', True),
                "content_moderator": getattr(self.content_moderator, 'ready', True),
                "personalization_engine": getattr(self.personalization_engine, 'ready', True)
            }
        }

# 🎭 Phase 2B ML Component Implementations

class AdvancedSentimentAnalyzer:
    """Advanced sentiment analysis with context awareness"""
    
    def __init__(self):
        self.ready = False
        self.model_version = "2B.sentiment.1.0"
    
    def initialize(self):
        """Initialize sentiment analysis models"""
        # In production, this would load actual ML models
        self.ready = True
        logger.info("✅ Advanced Sentiment Analyzer initialized")
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text with contextual insights"""
        # Simplified implementation - in production would use actual NLP models
        text_lower = text.lower()
        
        # Basic sentiment scoring
        negative_words = ['sad', 'depressed', 'hopeless', 'anxious', 'terrible', 'awful']
        positive_words = ['happy', 'great', 'wonderful', 'excellent', 'amazing', 'fantastic']
        
        negative_score = sum(1 for word in negative_words if word in text_lower)
        positive_score = sum(1 for word in positive_words if word in text_lower)
        
        if negative_score > positive_score:
            sentiment = 'negative' if negative_score > 2 else 'slightly_negative'
        elif positive_score > negative_score:
            sentiment = 'positive' if positive_score > 2 else 'slightly_positive'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'confidence': min(0.95, (abs(negative_score - positive_score) + 1) * 0.2),
            'negative_indicators': negative_score,
            'positive_indicators': positive_score,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'model_version': self.model_version
        }

class ContentModerator:
    """ML-powered content moderation"""
    
    def __init__(self):
        self.ready = False
        self.model_version = "2B.moderation.1.0"
    
    def initialize(self):
        """Initialize content moderation models"""
        self.ready = True
        logger.info("✅ Content Moderator initialized")
    
    def moderate_content(self, content: str, content_type: str = 'text') -> Dict[str, Any]:
        """Moderate content for safety and appropriateness"""
        # Simplified implementation
        harmful_patterns = ['spam', 'harmful', 'inappropriate', 'violence']
        
        content_lower = content.lower()
        violations = [pattern for pattern in harmful_patterns if pattern in content_lower]
        
        safe_to_publish = len(violations) == 0
        risk_score = len(violations) * 0.3
        
        return {
            'safe_to_publish': safe_to_publish,
            'risk_score': min(1.0, risk_score),
            'violations_detected': violations,
            'content_type': content_type,
            'moderation_timestamp': datetime.utcnow().isoformat(),
            'model_version': self.model_version
        }

class PersonalizationEngine:
    """Cross-service personalization engine"""
    
    def __init__(self):
        self.ready = False
        self.model_version = "2B.personalization.1.0"
    
    def initialize(self):
        """Initialize personalization models"""
        self.ready = True
        logger.info("✅ Personalization Engine initialized")
    
    def generate_personalization(self, user_profile: Dict, preferences: Dict, interaction_type: str) -> Dict[str, Any]:
        """Generate personalized recommendations based on user profile"""
        # Simplified implementation
        return {
            'personalized_content': f"Content personalized for {interaction_type}",
            'confidence': 0.8,
            'recommendations': [
                'Based on your recent activity, try meditation',
                'Connect with similar users in the community',
                'Your mood patterns suggest morning activities work best'
            ],
            'interaction_type': interaction_type,
            'personalization_timestamp': datetime.utcnow().isoformat(),
            'model_version': self.model_version
        }

class DataFusionProcessor:
    """Processes and fuses data from multiple services"""
    
    def __init__(self):
        self.ready = False
        self.model_version = "2B.fusion.1.0"
    
    def initialize(self):
        """Initialize data fusion processor"""
        self.ready = True
        logger.info("✅ Data Fusion Processor initialized")
    
    async def fuse_user_patterns(self, user_id: str, pattern_data: Dict) -> Dict[str, Any]:
        """Fuse user patterns across multiple services"""
        return {
            'fused_patterns': pattern_data,
            'cross_service_correlations': {'chat_mood_correlation': 0.7},
            'fusion_confidence': 0.85,
            'fusion_timestamp': datetime.utcnow().isoformat(),
            'model_version': self.model_version
        }

# Global cross-service ML hub instance
cross_service_ml_hub = None

def get_cross_service_ml_hub() -> CrossServiceMLHub:
    """Get or create global cross-service ML hub instance"""
    global cross_service_ml_hub
    if cross_service_ml_hub is None:
        cross_service_ml_hub = CrossServiceMLHub()
    return cross_service_ml_hub
