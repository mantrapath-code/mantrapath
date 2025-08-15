"""
Voice Command Router Service for API Gateway V3 Enhanced
Handles voice command classification and routing to appropriate services
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
import structlog

from ..models.voice_models import (
    VoiceCommand,
    VoiceIntentType,
    VoiceRoutingRule,
    VoiceRoutingResult,
    VoiceProcessingMetrics,
    VoiceParameterExtractor
)

logger = structlog.get_logger(__name__)


class VoiceCommandRouter:
    """Router for voice commands to appropriate microservices"""
    
    def __init__(self):
        self.routing_rules: List[VoiceRoutingRule] = []
        self.metrics = VoiceProcessingMetrics()
        self.is_initialized = False
        self._initialize_default_rules()
    
    async def initialize(self):
        """Initialize the voice router"""
        if self.is_initialized:
            return
        
        logger.info("Initializing Voice Command Router...")
        
        # Load configuration and initialize rules
        await self._load_routing_configuration()
        
        self.is_initialized = True
        logger.info("Voice Command Router initialized successfully")
    
    def _initialize_default_rules(self):
        """Initialize default routing rules for voice commands"""
        default_rules = [
            # Mood tracking routes
            VoiceRoutingRule(
                intent=VoiceIntentType.MOOD_TRACKING,
                target_service="mood_service",
                endpoint_pattern="/mood/track",
                method="POST",
                required_parameters=[],
                optional_parameters=["mood", "intensity", "notes"],
                supported_languages=["en", "hi", "es", "fr", "de"],
                cultural_adaptations={
                    "indian_subcontinent": {
                        "greeting_style": "respectful",
                        "family_context": True,
                        "spiritual_elements": True
                    },
                    "western_europe": {
                        "privacy_focus": True,
                        "direct_approach": True,
                        "secular_approach": True
                    }
                },
                priority=1,
                timeout=5.0,
                confidence_threshold=0.6
            ),
            
            # Journal entry routes
            VoiceRoutingRule(
                intent=VoiceIntentType.JOURNAL_ENTRY,
                target_service="content_service",
                endpoint_pattern="/journal/entry",
                method="POST",
                required_parameters=["content"],
                optional_parameters=["mood", "tags", "private"],
                supported_languages=["en", "hi", "es", "fr", "de", "it", "pt"],
                cultural_adaptations={
                    "indian_subcontinent": {
                        "reflection_style": "contemplative",
                        "spiritual_references": True
                    }
                },
                priority=1,
                timeout=10.0,
                confidence_threshold=0.7
            ),
            
            # Chatbot query routes
            VoiceRoutingRule(
                intent=VoiceIntentType.CHATBOT_QUERY,
                target_service="chatbot_service",
                endpoint_pattern="/chat/voice",
                method="POST",
                required_parameters=["message"],
                optional_parameters=["context", "session_id"],
                supported_languages=["en", "hi", "es", "fr", "de", "it", "pt", "ru", "ja", "zh", "ko", "ar"],
                cultural_adaptations={
                    "indian_subcontinent": {
                        "response_style": "warm_respectful",
                        "cultural_references": True
                    },
                    "east_asia": {
                        "harmony_focus": True,
                        "collective_mindset": True
                    }
                },
                priority=2,
                timeout=8.0,
                confidence_threshold=0.5
            ),
            
            # Content request routes
            VoiceRoutingRule(
                intent=VoiceIntentType.CONTENT_REQUEST,
                target_service="content_service",
                endpoint_pattern="/content/search",
                method="GET",
                required_parameters=["query"],
                optional_parameters=["type", "duration", "difficulty"],
                supported_languages=["en", "hi", "es", "fr", "de", "it", "pt"],
                cultural_adaptations={
                    "indian_subcontinent": {
                        "content_style": "traditional_modern_blend",
                        "spiritual_focus": True
                    }
                },
                priority=1,
                timeout=5.0,
                confidence_threshold=0.6
            ),
            
            # Community action routes
            VoiceRoutingRule(
                intent=VoiceIntentType.COMMUNITY_ACTION,
                target_service="community_service",
                endpoint_pattern="/community/action",
                method="POST",
                required_parameters=["action"],
                optional_parameters=["group_id", "message"],
                supported_languages=["en", "hi", "es", "fr", "de"],
                cultural_adaptations={
                    "indian_subcontinent": {
                        "community_style": "family_oriented",
                        "respect_hierarchy": True
                    }
                },
                priority=2,
                timeout=7.0,
                confidence_threshold=0.7
            ),
            
            # Meditation control routes
            VoiceRoutingRule(
                intent=VoiceIntentType.MEDITATION_START,
                target_service="content_service",
                endpoint_pattern="/meditation/start",
                method="POST",
                required_parameters=[],
                optional_parameters=["type", "duration", "guide_language"],
                supported_languages=["en", "hi", "es", "fr", "de", "it", "pt", "ja", "zh"],
                cultural_adaptations={
                    "indian_subcontinent": {
                        "meditation_style": "traditional",
                        "sanskrit_terms": True
                    },
                    "east_asia": {
                        "meditation_style": "zen",
                        "mindfulness_focus": True
                    }
                },
                priority=1,
                timeout=5.0,
                confidence_threshold=0.8
            ),
            
            # Profile update routes
            VoiceRoutingRule(
                intent=VoiceIntentType.PROFILE_UPDATE,
                target_service="profile_service",
                endpoint_pattern="/profile/update",
                method="PATCH",
                required_parameters=["field"],
                optional_parameters=["value", "preferences"],
                supported_languages=["en", "hi", "es", "fr", "de"],
                cultural_adaptations={
                    "western_europe": {
                        "privacy_emphasis": True,
                        "data_protection": True
                    }
                },
                priority=2,
                timeout=5.0,
                confidence_threshold=0.7
            )
        ]
        
        self.routing_rules.extend(default_rules)
        logger.info(f"Initialized {len(default_rules)} default routing rules")
    
    async def _load_routing_configuration(self):
        """Load routing configuration from external sources"""
        # TODO: Load from configuration files, database, or service registry
        # For now, we use the default rules
        pass
    
    async def route_command(
        self,
        voice_command: VoiceCommand,
        user_context: Optional[Dict[str, Any]] = None
    ) -> VoiceRoutingResult:
        """Route a voice command to the appropriate service"""
        start_time = time.time()
        
        logger.info(
            "Routing voice command",
            intent=voice_command.intent,
            language=voice_command.language,
            confidence=voice_command.confidence
        )
        
        try:
            # Find matching routing rule
            matching_rule = await self._find_matching_rule(voice_command, user_context)
            
            if not matching_rule:
                # Handle unknown or unsupported commands
                return await self._handle_unknown_command(voice_command, start_time)
            
            # Extract parameters from voice command
            extracted_params = self._extract_parameters(voice_command, matching_rule)
            
            # Build target endpoint and request details
            target_endpoint = self._build_target_endpoint(matching_rule, extracted_params)
            headers = self._build_headers(voice_command, user_context)
            body = self._build_request_body(voice_command, extracted_params, matching_rule)
            query_params = self._build_query_params(extracted_params, matching_rule)
            
            routing_time = (time.time() - start_time) * 1000
            
            result = VoiceRoutingResult(
                rule=matching_rule,
                target_service=matching_rule.target_service,
                target_endpoint=target_endpoint,
                method=matching_rule.method,
                headers=headers,
                body=body,
                query_params=query_params,
                routing_time_ms=routing_time,
                success=True
            )
            
            # Record metrics
            self.metrics.add_command_result(
                intent=voice_command.intent or VoiceIntentType.UNKNOWN,
                language=voice_command.language or "unknown",
                processing_time=routing_time,
                confidence=voice_command.confidence,
                success=True
            )
            
            logger.info(
                "Voice command routed successfully",
                target_service=matching_rule.target_service,
                target_endpoint=target_endpoint,
                routing_time_ms=round(routing_time, 2)
            )
            
            return result
            
        except Exception as e:
            routing_time = (time.time() - start_time) * 1000
            
            # Record error metrics
            self.metrics.add_command_result(
                intent=voice_command.intent or VoiceIntentType.UNKNOWN,
                language=voice_command.language or "unknown",
                processing_time=routing_time,
                confidence=voice_command.confidence,
                success=False,
                error=str(e)
            )
            
            logger.exception(
                "Voice command routing failed",
                error=str(e),
                routing_time_ms=round(routing_time, 2)
            )
            
            return VoiceRoutingResult(
                rule=None,
                target_service="",
                target_endpoint="",
                method="POST",
                routing_time_ms=routing_time,
                success=False,
                error_message=str(e)
            )
    
    async def _find_matching_rule(
        self,
        voice_command: VoiceCommand,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[VoiceRoutingRule]:
        """Find the best matching routing rule for the voice command"""
        
        # If intent is not set, try to classify it
        if not voice_command.intent:
            voice_command.intent = await self._classify_intent(voice_command.text)
        
        # Find rules that match the command
        matching_rules = [
            rule for rule in self.routing_rules
            if rule.matches_command(voice_command)
        ]
        
        if not matching_rules:
            return None
        
        # Sort by priority (lower number = higher priority)
        matching_rules.sort(key=lambda rule: rule.priority)
        
        # Return the highest priority rule
        return matching_rules[0]
    
    async def _classify_intent(self, text: str) -> VoiceIntentType:
        """Classify the intent of a voice command"""
        text_lower = text.lower()
        
        # Simple keyword-based classification
        # In a real implementation, this would use ML models
        
        mood_keywords = ["feel", "mood", "emotion", "happy", "sad", "angry", "stressed"]
        if any(keyword in text_lower for keyword in mood_keywords):
            return VoiceIntentType.MOOD_TRACKING
        
        journal_keywords = ["write", "journal", "diary", "record", "note"]
        if any(keyword in text_lower for keyword in journal_keywords):
            return VoiceIntentType.JOURNAL_ENTRY
        
        meditation_start_keywords = ["start meditation", "begin meditation", "meditate"]
        if any(keyword in text_lower for keyword in meditation_start_keywords):
            return VoiceIntentType.MEDITATION_START
        
        content_keywords = ["show", "find", "search", "content", "meditation", "exercise"]
        if any(keyword in text_lower for keyword in content_keywords):
            return VoiceIntentType.CONTENT_REQUEST
        
        chat_keywords = ["ask", "question", "help", "advice", "guidance"]
        if any(keyword in text_lower for keyword in chat_keywords):
            return VoiceIntentType.CHATBOT_QUERY
        
        return VoiceIntentType.UNKNOWN
    
    def _extract_parameters(
        self,
        voice_command: VoiceCommand,
        rule: VoiceRoutingRule
    ) -> Dict[str, Any]:
        """Extract parameters from voice command based on routing rule"""
        # Start with existing parameters
        extracted = dict(voice_command.parameters)
        
        # Use the parameter extractor for additional extraction
        if voice_command.intent:
            general_params = VoiceParameterExtractor.extract_general_parameters(
                voice_command.text,
                voice_command.intent
            )
            extracted.update(general_params)
        
        return extracted
    
    def _build_target_endpoint(
        self,
        rule: VoiceRoutingRule,
        parameters: Dict[str, Any]
    ) -> str:
        """Build the target endpoint URL"""
        endpoint = rule.endpoint_pattern
        
        # Replace parameter placeholders in the endpoint pattern
        for param_name, param_value in parameters.items():
            placeholder = f"{{{param_name}}}"
            if placeholder in endpoint:
                endpoint = endpoint.replace(placeholder, str(param_value))
        
        return endpoint
    
    def _build_headers(
        self,
        voice_command: VoiceCommand,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Build headers for the routed request"""
        headers = {
            "Content-Type": "application/json",
            "X-Voice-Command": "true",
            "X-Voice-Text": voice_command.text[:500],  # Truncate long text
        }
        
        if voice_command.language:
            headers["X-Language"] = voice_command.language
        
        if voice_command.confidence is not None:
            headers["X-Voice-Confidence"] = str(voice_command.confidence)
        
        if voice_command.cultural_context:
            headers["X-Cultural-Context"] = voice_command.cultural_context
        
        if voice_command.session_id:
            headers["X-Session-ID"] = voice_command.session_id
        
        if user_context and "user_id" in user_context:
            headers["X-User-ID"] = user_context["user_id"]
        
        return headers
    
    def _build_request_body(
        self,
        voice_command: VoiceCommand,
        parameters: Dict[str, Any],
        rule: VoiceRoutingRule
    ) -> Optional[Dict[str, Any]]:
        """Build request body for the routed request"""
        if rule.method in ["GET", "DELETE"]:
            return None
        
        body = {
            "voice_command": {
                "text": voice_command.text,
                "intent": voice_command.intent.value if voice_command.intent else None,
                "language": voice_command.language,
                "confidence": voice_command.confidence,
                "timestamp": voice_command.timestamp
            },
            "parameters": parameters
        }
        
        # Add user context if available
        if voice_command.user_id:
            body["user_id"] = voice_command.user_id
        
        if voice_command.session_id:
            body["session_id"] = voice_command.session_id
        
        return body
    
    def _build_query_params(
        self,
        parameters: Dict[str, Any],
        rule: VoiceRoutingRule
    ) -> Dict[str, str]:
        """Build query parameters for GET requests"""
        if rule.method != "GET":
            return {}
        
        # Convert parameters to query string format
        query_params = {}
        for key, value in parameters.items():
            if key in rule.optional_parameters or key in rule.required_parameters:
                query_params[key] = str(value)
        
        return query_params
    
    async def _handle_unknown_command(
        self,
        voice_command: VoiceCommand,
        start_time: float
    ) -> VoiceRoutingResult:
        """Handle unknown or unsupported voice commands"""
        routing_time = (time.time() - start_time) * 1000
        
        logger.warning(
            "Unknown voice command",
            text=voice_command.text,
            intent=voice_command.intent,
            language=voice_command.language
        )
        
        # Route to chatbot service as fallback
        return VoiceRoutingResult(
            rule=None,
            target_service="chatbot_service",
            target_endpoint="/chat/fallback",
            method="POST",
            headers=self._build_headers(voice_command),
            body={
                "message": voice_command.text,
                "type": "unknown_voice_command",
                "original_intent": voice_command.intent.value if voice_command.intent else None
            },
            routing_time_ms=routing_time,
            success=True,
            fallback_used=True
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the voice router"""
        try:
            total_rules = len(self.routing_rules)
            success_rate = self.metrics.get_success_rate()
            
            healthy = (
                self.is_initialized and
                total_rules > 0 and
                success_rate >= 80.0  # At least 80% success rate
            )
            
            return {
                "status": "healthy" if healthy else "degraded",
                "initialized": self.is_initialized,
                "total_rules": total_rules,
                "metrics": self.metrics.to_dict(),
                "timestamp": time.time()
            }
        
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def detailed_health_check(self) -> Dict[str, Any]:
        """Detailed health check with comprehensive information"""
        basic_health = await self.health_check()
        
        # Add detailed rule information
        rule_details = []
        for rule in self.routing_rules:
            rule_details.append({
                "intent": rule.intent.value,
                "target_service": rule.target_service,
                "supported_languages": rule.supported_languages,
                "priority": rule.priority,
                "confidence_threshold": rule.confidence_threshold
            })
        
        return {
            **basic_health,
            "routing_rules": rule_details,
            "feature_support": {
                "intent_classification": True,
                "parameter_extraction": True,
                "cultural_adaptation": True,
                "fallback_handling": True,
                "multilingual_support": True
            }
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get routing metrics"""
        return self.metrics.to_dict()
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported voice intents"""
        return [rule.intent.value for rule in self.routing_rules]
    
    def get_supported_languages(self) -> List[str]:
        """Get list of all supported languages across all rules"""
        languages = set()
        for rule in self.routing_rules:
            languages.update(rule.supported_languages)
        return sorted(list(languages))
