"""
Voice Command Router for Enhanced API Gateway V3
Routes voice commands to appropriate microservices
"""

import logging
import time
from typing import Dict, List, Optional, Any
from .models import VoiceIntentType, VoiceCommand, VoiceRoutingRule, VoiceRoutingResult
from .classifier import VoiceIntentClassifier

logger = logging.getLogger(__name__)


class VoiceCommandRouter:
    """Routes voice commands to appropriate microservices"""
    
    def __init__(self, intent_classifier: Optional[VoiceIntentClassifier] = None):
        self.intent_classifier = intent_classifier or VoiceIntentClassifier()
        self.routing_rules: List[VoiceRoutingRule] = []
        self._initialize_default_rules()
        self.routing_stats = {
            "total_requests": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "avg_processing_time": 0.0
        }
    
    def _initialize_default_rules(self):
        """Initialize default routing rules for voice commands"""
        default_rules = [
            # Mood tracking routes
            VoiceRoutingRule(
                intent=VoiceIntentType.MOOD_TRACKING,
                target_service="mood_service",
                endpoint_pattern="/mood/track",
                required_parameters=[],
                supported_languages=["en", "hi", "es", "fr", "de"],
                cultural_adaptations={
                    "indian_subcontinent": {
                        "greeting_style": "respectful",
                        "family_context": True
                    },
                    "western_europe": {
                        "privacy_focus": True,
                        "direct_approach": True
                    }
                },
                priority=1,
                timeout=5.0,
                retries=3
            ),
            
            # Journal entry routes
            VoiceRoutingRule(
                intent=VoiceIntentType.JOURNAL_ENTRY,
                target_service="content_service",
                endpoint_pattern="/journal/entries",
                required_parameters=[],
                supported_languages=["en", "hi", "es", "fr", "de", "ta", "te"],
                cultural_adaptations={
                    "indian_subcontinent": {
                        "prompt_style": "reflective",
                        "spiritual_themes": True
                    }
                },
                priority=1,
                timeout=10.0,
                retries=2
            ),
            
            # Chatbot query routes
            VoiceRoutingRule(
                intent=VoiceIntentType.CHATBOT_QUERY,
                target_service="chatbot_service",
                endpoint_pattern="/chat/message",
                required_parameters=[],
                supported_languages=["en", "hi", "es", "fr", "de", "zh", "ja", "ar"],
                cultural_adaptations={
                    "east_asia": {
                        "communication_style": "indirect",
                        "respect_hierarchy": True
                    },
                    "middle_east": {
                        "formal_address": True,
                        "cultural_sensitivity": True
                    }
                },
                priority=1,
                timeout=8.0,
                retries=3
            ),
            
            # Content request routes
            VoiceRoutingRule(
                intent=VoiceIntentType.CONTENT_REQUEST,
                target_service="content_service",
                endpoint_pattern="/content/search",
                required_parameters=[],
                supported_languages=["en", "hi", "es", "fr", "de", "pt", "ru"],
                cultural_adaptations={
                    "latin_america": {
                        "content_preference": "community_focused",
                        "family_values": True
                    }
                },
                priority=1,
                timeout=7.0,
                retries=2
            ),
            
            # Profile update routes
            VoiceRoutingRule(
                intent=VoiceIntentType.PROFILE_UPDATE,
                target_service="profile_service",
                endpoint_pattern="/profile/update",
                required_parameters=[],
                supported_languages=["en", "hi", "es", "fr", "de"],
                cultural_adaptations={},
                priority=2,
                timeout=5.0,
                retries=3
            ),
            
            # Community action routes
            VoiceRoutingRule(
                intent=VoiceIntentType.COMMUNITY_ACTION,
                target_service="community_service",
                endpoint_pattern="/community/action",
                required_parameters=[],
                supported_languages=["en", "hi", "es", "fr", "de"],
                cultural_adaptations={
                    "indian_subcontinent": {
                        "community_emphasis": True,
                        "collective_values": True
                    }
                },
                priority=1,
                timeout=6.0,
                retries=2
            ),
            
            # Analytics request routes
            VoiceRoutingRule(
                intent=VoiceIntentType.ANALYTICS_REQUEST,
                target_service="ml_service",
                endpoint_pattern="/analytics/insights",
                required_parameters=[],
                supported_languages=["en", "hi", "es", "fr", "de"],
                cultural_adaptations={},
                priority=3,
                timeout=10.0,
                retries=1
            )
        ]
        
        self.routing_rules.extend(default_rules)
        logger.info(f"Initialized {len(default_rules)} default voice routing rules")
    
    def route_voice_command(self, text: str, language: str, user_id: Optional[str] = None,
                          cultural_context: Optional[str] = None) -> VoiceRoutingResult:
        """
        Route a voice command to the appropriate service
        
        Args:
            text: Voice command text
            language: Language code
            user_id: Optional user ID
            cultural_context: Optional cultural context
            
        Returns:
            VoiceRoutingResult with routing information
        """
        start_time = time.time()
        self.routing_stats["total_requests"] += 1
        
        try:
            # Classify the intent
            command = self.intent_classifier.classify_intent(text, language, user_id)
            command.cultural_context = cultural_context
            
            # Find matching routing rule
            matching_rule = self._find_matching_rule(command)
            
            if not matching_rule:
                processing_time = (time.time() - start_time) * 1000
                self.routing_stats["failed_routes"] += 1
                return VoiceRoutingResult(
                    success=False,
                    target_service="unknown",
                    endpoint="",
                    error_message=f"No routing rule found for intent: {command.intent.value}",
                    processing_time_ms=processing_time
                )
            
            # Generate target endpoint
            endpoint = matching_rule.generate_endpoint(command)
            
            # Apply cultural adaptations
            adapted_endpoint = self._apply_cultural_adaptations(
                endpoint, command, matching_rule
            )
            
            processing_time = (time.time() - start_time) * 1000
            self.routing_stats["successful_routes"] += 1
            self._update_avg_processing_time(processing_time)
            
            result = VoiceRoutingResult(
                success=True,
                target_service=matching_rule.target_service,
                endpoint=adapted_endpoint,
                rule=matching_rule,
                processing_time_ms=processing_time
            )
            
            logger.info(
                f"Successfully routed voice command to {matching_rule.target_service}{adapted_endpoint} "
                f"(intent: {command.intent.value}, confidence: {command.confidence:.2f}, "
                f"time: {processing_time:.1f}ms)"
            )
            
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self.routing_stats["failed_routes"] += 1
            logger.error(f"Voice routing error: {e}", exc_info=True)
            
            return VoiceRoutingResult(
                success=False,
                target_service="error",
                endpoint="",
                error_message=str(e),
                processing_time_ms=processing_time
            )
    
    def _find_matching_rule(self, command: VoiceCommand) -> Optional[VoiceRoutingRule]:
        """Find the best matching routing rule for a command"""
        matching_rules = [rule for rule in self.routing_rules if rule.matches_command(command)]
        
        if not matching_rules:
            return None
        
        # Sort by priority (lower number = higher priority)
        matching_rules.sort(key=lambda r: r.priority)
        
        return matching_rules[0]
    
    def _apply_cultural_adaptations(self, endpoint: str, command: VoiceCommand, 
                                  rule: VoiceRoutingRule) -> str:
        """Apply cultural adaptations to the endpoint"""
        if not command.cultural_context or not rule.cultural_adaptations:
            return endpoint
        
        adaptations = rule.cultural_adaptations.get(command.cultural_context, {})
        
        # Add cultural parameters to endpoint
        if adaptations:
            separator = "?" if "?" not in endpoint else "&"
            cultural_params = []
            
            for key, value in adaptations.items():
                cultural_params.append(f"cultural_{key}={value}")
            
            if cultural_params:
                endpoint += separator + "&".join(cultural_params)
        
        return endpoint
    
    def _update_avg_processing_time(self, processing_time: float):
        """Update average processing time statistics"""
        total_successful = self.routing_stats["successful_routes"]
        current_avg = self.routing_stats["avg_processing_time"]
        
        # Calculate new average
        new_avg = ((current_avg * (total_successful - 1)) + processing_time) / total_successful
        self.routing_stats["avg_processing_time"] = new_avg
    
    def add_routing_rule(self, rule: VoiceRoutingRule):
        """Add a custom routing rule"""
        self.routing_rules.append(rule)
        # Sort by priority to maintain order
        self.routing_rules.sort(key=lambda r: r.priority)
        logger.info(f"Added routing rule for {rule.intent.value} -> {rule.target_service}")
    
    def remove_routing_rule(self, intent: VoiceIntentType, target_service: str) -> bool:
        """Remove a routing rule"""
        original_count = len(self.routing_rules)
        self.routing_rules = [
            rule for rule in self.routing_rules 
            if not (rule.intent == intent and rule.target_service == target_service)
        ]
        
        removed = len(self.routing_rules) < original_count
        if removed:
            logger.info(f"Removed routing rule for {intent.value} -> {target_service}")
        
        return removed
    
    def get_routing_rules_for_intent(self, intent: VoiceIntentType) -> List[VoiceRoutingRule]:
        """Get all routing rules for a specific intent"""
        return [rule for rule in self.routing_rules if rule.intent == intent]
    
    def get_supported_intents(self) -> List[VoiceIntentType]:
        """Get list of supported intents"""
        return list(set(rule.intent for rule in self.routing_rules))
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing statistics"""
        success_rate = 0.0
        if self.routing_stats["total_requests"] > 0:
            success_rate = (
                self.routing_stats["successful_routes"] / 
                self.routing_stats["total_requests"]
            ) * 100
        
        return {
            **self.routing_stats,
            "success_rate_percent": success_rate,
            "total_rules": len(self.routing_rules),
            "supported_intents": len(self.get_supported_intents())
        }
    
    def reset_statistics(self):
        """Reset routing statistics"""
        self.routing_stats = {
            "total_requests": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "avg_processing_time": 0.0
        }
        logger.info("Voice routing statistics reset")


class VoiceRoutingMiddleware:
    """Middleware for integrating voice routing into FastAPI"""
    
    def __init__(self, router: VoiceCommandRouter):
        self.router = router
    
    async def process_voice_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a voice request and return routing information"""
        try:
            text = request_data.get("text", "")
            language = request_data.get("language", "en")
            user_id = request_data.get("user_id")
            cultural_context = request_data.get("cultural_context")
            
            if not text.strip():
                return {
                    "success": False,
                    "error": "Empty voice text provided"
                }
            
            # Route the voice command
            result = self.router.route_voice_command(
                text=text,
                language=language,
                user_id=user_id,
                cultural_context=cultural_context
            )
            
            return result.to_dict()
            
        except Exception as e:
            logger.error(f"Voice routing middleware error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
