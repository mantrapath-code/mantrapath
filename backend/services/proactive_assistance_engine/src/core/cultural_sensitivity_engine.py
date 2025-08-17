"""
Cultural Sensitivity Engine

Ensures all proactive assistance respects cultural norms and preferences
by evaluating cultural appropriateness and adapting content accordingly.
"""

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
        cultural_profile: Dict[str, Any],
        intervention_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate cultural appropriateness of assistance content
        """
        try:
            primary_culture = cultural_profile.get("primary_culture", "unknown")
            communication_style = cultural_profile.get("communication_style", "neutral")
            
            # Step 1: Check cultural guidelines for assistance type
            cultural_guidelines = self.cultural_guidelines.get(primary_culture, {})
            
            # Step 2: Evaluate content appropriateness
            content_evaluation = await self._evaluate_content_appropriateness(
                intervention_analysis, cultural_guidelines
            )
            
            # Step 3: Check timing appropriateness
            timing_evaluation = await self._evaluate_timing_appropriateness(
                cultural_profile, intervention_analysis
            )
            
            # Step 4: Adapt content if needed
            adapted_content = await self._adapt_content_for_culture(
                intervention_analysis, cultural_profile, cultural_guidelines
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
                "cultural_considerations": cultural_guidelines.get("assistance_considerations", []),
                "primary_culture": primary_culture,
                "communication_style": communication_style
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
                },
                "intervention_adaptations": {
                    "crisis_intervention": "Include family notification options",
                    "proactive_support": "Emphasize community resources",
                    "gentle_check_in": "Use indirect, respectful language"
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
                },
                "intervention_adaptations": {
                    "crisis_intervention": "Emphasize personal safety and professional help",
                    "proactive_support": "Focus on individual coping strategies",
                    "gentle_check_in": "Be direct about support options"
                }
            },
            "high_context": {
                "assistance_considerations": [
                    "Use indirect communication",
                    "Respect implicit meanings",
                    "Consider relationship context",
                    "Avoid overly direct language"
                ],
                "communication_preferences": {
                    "directness": "indirect",
                    "context_level": "high",
                    "relationship_focus": "preferred"
                },
                "intervention_adaptations": {
                    "crisis_intervention": "Use gentle, indirect crisis language",
                    "proactive_support": "Emphasize relationship-based support",
                    "gentle_check_in": "Use very gentle, indirect language"
                }
            },
            "low_context": {
                "assistance_considerations": [
                    "Be direct and clear",
                    "Provide explicit information",
                    "Focus on facts and actions",
                    "Minimize implicit meanings"
                ],
                "communication_preferences": {
                    "directness": "direct",
                    "context_level": "low",
                    "action_focus": "preferred"
                },
                "intervention_adaptations": {
                    "crisis_intervention": "Provide clear, direct crisis instructions",
                    "proactive_support": "Give specific, actionable advice",
                    "gentle_check_in": "Ask direct questions about well-being"
                }
            }
        }
    
    async def _evaluate_content_appropriateness(
        self,
        intervention_analysis: Dict[str, Any],
        cultural_guidelines: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate if intervention content is culturally appropriate
        """
        try:
            intervention_type = intervention_analysis.get("intervention_type", "unknown")
            urgency_level = intervention_analysis.get("urgency_level", "none")
            
            # Get cultural adaptations for this intervention type
            intervention_adaptations = cultural_guidelines.get("intervention_adaptations", {})
            adaptation_text = intervention_adaptations.get(intervention_type, "")
            
            # Check communication style compatibility
            communication_prefs = cultural_guidelines.get("communication_preferences", {})
            directness = communication_prefs.get("directness", "neutral")
            
            # Score based on cultural fit
            content_score = 0.8  # Base score
            
            # Adjust for intervention type compatibility
            if adaptation_text:
                content_score += 0.1
            
            # Adjust for communication style
            if directness == "direct" and urgency_level in ["critical", "high"]:
                content_score += 0.1
            elif directness == "indirect" and urgency_level in ["low", "none"]:
                content_score += 0.1
            
            return {
                "appropriateness_score": min(1.0, content_score),
                "adaptation_available": bool(adaptation_text),
                "adaptation_text": adaptation_text,
                "communication_style_compatible": True,
                "intervention_type_supported": intervention_type in intervention_adaptations
            }
            
        except Exception as e:
            logger.error("Content appropriateness evaluation failed", error=str(e))
            return {
                "appropriateness_score": 0.5,
                "adaptation_available": False,
                "adaptation_text": "",
                "communication_style_compatible": False,
                "intervention_type_supported": False
            }
    
    async def _evaluate_timing_appropriateness(
        self,
        cultural_profile: Dict[str, Any],
        intervention_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate if timing is culturally appropriate
        """
        try:
            primary_culture = cultural_profile.get("primary_culture", "unknown")
            cultural_guidelines = self.cultural_guidelines.get(primary_culture, {})
            timing_prefs = cultural_guidelines.get("timing_preferences", {})
            
            # Check urgency override
            urgency_level = intervention_analysis.get("urgency_level", "none")
            urgency_override = urgency_level in ["critical", "high"]
            
            if urgency_override:
                return {
                    "appropriateness_score": 0.9,
                    "timing_considerations": ["Urgency overrides cultural timing restrictions"],
                    "can_proceed": True,
                    "urgency_override": True
                }
            
            # Evaluate timing preferences
            timing_score = 0.8  # Base score
            
            # Check family time respect
            if timing_prefs.get("family_time_respect", False):
                timing_score += 0.1
            
            # Check meal time awareness
            if timing_prefs.get("meal_time_awareness", False):
                timing_score += 0.1
            
            return {
                "appropriateness_score": min(1.0, timing_score),
                "timing_considerations": list(timing_prefs.keys()),
                "can_proceed": timing_score > 0.6,
                "urgency_override": False
            }
            
        except Exception as e:
            logger.error("Timing appropriateness evaluation failed", error=str(e))
            return {
                "appropriateness_score": 0.5,
                "timing_considerations": [],
                "can_proceed": False,
                "urgency_override": False
            }
    
    async def _adapt_content_for_culture(
        self,
        intervention_analysis: Dict[str, Any],
        cultural_profile: Dict[str, Any],
        cultural_guidelines: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adapt intervention content for cultural appropriateness
        """
        try:
            primary_culture = cultural_profile.get("primary_culture", "unknown")
            intervention_type = intervention_analysis.get("intervention_type", "unknown")
            
            # Get base content
            adapted_content = intervention_analysis.copy()
            
            # Apply cultural adaptations
            intervention_adaptations = cultural_guidelines.get("intervention_adaptations", {})
            adaptation_text = intervention_adaptations.get(intervention_type, "")
            
            if adaptation_text:
                adapted_content["cultural_adaptation"] = adaptation_text
                adapted_content["culturally_adapted"] = True
            else:
                adapted_content["culturally_adapted"] = False
            
            # Add cultural context
            adapted_content["cultural_context"] = {
                "primary_culture": primary_culture,
                "communication_style": cultural_profile.get("communication_style", "neutral"),
                "guidelines_applied": list(cultural_guidelines.keys())
            }
            
            return adapted_content
            
        except Exception as e:
            logger.error("Content cultural adaptation failed", error=str(e))
            return intervention_analysis
    
    def _create_fallback_cultural_evaluation(self) -> Dict[str, Any]:
        """
        Create fallback cultural evaluation when analysis fails
        """
        return {
            "culturally_appropriate": False,
            "appropriateness_score": 0.0,
            "content_evaluation": {
                "appropriateness_score": 0.0,
                "adaptation_available": False,
                "adaptation_text": "",
                "communication_style_compatible": False,
                "intervention_type_supported": False
            },
            "timing_evaluation": {
                "appropriateness_score": 0.0,
                "timing_considerations": [],
                "can_proceed": False,
                "urgency_override": False
            },
            "adapted_content": {},
            "cultural_considerations": ["Cultural evaluation failed"],
            "primary_culture": "unknown",
            "communication_style": "neutral"
        }
    
    async def get_cultural_guidelines(self, culture: str) -> Dict[str, Any]:
        """
        Get cultural guidelines for specific culture
        """
        return self.cultural_guidelines.get(culture, {})
    
    async def add_cultural_guidelines(self, culture: str, guidelines: Dict[str, Any]) -> bool:
        """
        Add or update cultural guidelines
        """
        try:
            self.cultural_guidelines[culture] = guidelines
            logger.info(f"Updated cultural guidelines for: {culture}")
            return True
            
        except Exception as e:
            logger.error("Failed to add cultural guidelines", error=str(e))
            return False
    
    async def get_supported_cultures(self) -> List[str]:
        """
        Get list of supported cultures
        """
        return list(self.cultural_guidelines.keys())
