"""
Contextual Help Engine

Contextual help system that matches user needs with appropriate assistance content
based on intervention analysis and cultural considerations.
"""

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
        cultural_evaluation: Dict[str, Any]
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
                relevant_help, cultural_evaluation
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
            ],
            "behavioral_guidance": [
                {
                    "id": "behavior_guidance_001",
                    "title": "Behavioral Support",
                    "content": "I've noticed some patterns that might be helpful to explore together.",
                    "actions": [
                        "Review your recent behaviors",
                        "Identify triggers and patterns",
                        "Practice mindfulness techniques",
                        "Consider professional guidance"
                    ],
                    "urgency": "medium",
                    "cultural_adaptations": {
                        "collectivist": "Include family and community perspectives",
                        "individualist": "Focus on personal growth and development"
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
        elif intervention_type == "behavioral_guidance":
            help_categories.append("behavioral_guidance")
        else:
            help_categories.append("proactive_check_in")  # Default
        
        return {
            "primary_help_categories": help_categories,
            "urgency_level": urgency_level,
            "risk_factors": risk_factors,
            "user_preferences": user_context.get("assistance_preferences", {})
        }
    
    async def _match_help_content(self, user_needs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Match user needs to available help content
        """
        try:
            matched_content = []
            primary_categories = user_needs.get("primary_help_categories", [])
            
            for category in primary_categories:
                if category in self.help_content_db:
                    category_content = self.help_content_db[category]
                    
                    # Filter by urgency level if specified
                    urgency_level = user_needs.get("urgency_level", "none")
                    if urgency_level != "none":
                        urgency_filtered = [
                            content for content in category_content
                            if content.get("urgency") == urgency_level or content.get("urgency") == "none"
                        ]
                        matched_content.extend(urgency_filtered)
                    else:
                        matched_content.extend(category_content)
            
            # If no specific matches, provide general support
            if not matched_content:
                matched_content = self.help_content_db.get("proactive_check_in", [])
            
            return matched_content
            
        except Exception as e:
            logger.error("Help content matching failed", error=str(e))
            return self._get_fallback_help_content()
    
    async def _adapt_help_for_culture(
        self, 
        help_content: List[Dict[str, Any]], 
        cultural_evaluation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Adapt help content for cultural appropriateness
        """
        try:
            adapted_content = []
            
            for content in help_content:
                adapted_item = content.copy()
                
                # Apply cultural adaptations if available
                cultural_adaptations = content.get("cultural_adaptations", {})
                if cultural_adaptations:
                    # Get primary culture from evaluation
                    primary_culture = cultural_evaluation.get("primary_culture", "unknown")
                    
                    if primary_culture in cultural_adaptations:
                        adaptation_text = cultural_adaptations[primary_culture]
                        adapted_item["content"] = f"{content['content']} {adaptation_text}"
                        adapted_item["cultural_adaptation_applied"] = True
                    else:
                        adapted_item["cultural_adaptation_applied"] = False
                else:
                    adapted_item["cultural_adaptation_applied"] = False
                
                adapted_content.append(adapted_item)
            
            return adapted_content
            
        except Exception as e:
            logger.error("Cultural adaptation failed", error=str(e))
            return help_content  # Return original content if adaptation fails
    
    async def _prioritize_help_suggestions(
        self, 
        help_content: List[Dict[str, Any]], 
        user_needs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Prioritize help suggestions based on relevance and user needs
        """
        try:
            # Calculate relevance scores for each help item
            scored_content = []
            
            for content in help_content:
                score = self._calculate_help_relevance_score(content, user_needs)
                scored_content.append((score, content))
            
            # Sort by score (highest first)
            scored_content.sort(key=lambda x: x[0], reverse=True)
            
            # Return content without scores
            return [content for score, content in scored_content]
            
        except Exception as e:
            logger.error("Help prioritization failed", error=str(e))
            return help_content
    
    def _calculate_help_relevance_score(
        self, 
        help_content: Dict[str, Any], 
        user_needs: Dict[str, Any]
    ) -> float:
        """
        Calculate relevance score for help content based on user needs
        """
        try:
            score = 0.0
            
            # Base score for urgency match
            content_urgency = help_content.get("urgency", "none")
            user_urgency = user_needs.get("urgency_level", "none")
            
            if content_urgency == user_urgency:
                score += 0.4
            elif content_urgency == "none":
                score += 0.2
            else:
                score += 0.1
            
            # Cultural adaptation bonus
            if help_content.get("cultural_adaptation_applied", False):
                score += 0.2
            
            # Content quality bonus
            actions_count = len(help_content.get("actions", []))
            if actions_count >= 3:
                score += 0.2
            elif actions_count >= 1:
                score += 0.1
            
            # User preference bonus
            user_preferences = user_needs.get("user_preferences", {})
            if user_preferences.get("preferred_assistance_style") == "gentle":
                if "gentle" in help_content.get("content", "").lower():
                    score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error("Help relevance scoring failed", error=str(e))
            return 0.5
    
    def _get_fallback_help_content(self) -> List[Dict[str, Any]]:
        """
        Get fallback help content when matching fails
        """
        return [
            {
                "id": "fallback_001",
                "title": "General Support",
                "content": "I'm here to support you. Please reach out if you need assistance.",
                "actions": [
                    "Contact support team",
                    "Review available resources",
                    "Take a moment to breathe"
                ],
                "urgency": "none",
                "cultural_adaptations": {},
                "fallback": True
            }
        ]
    
    async def add_help_content(self, category: str, content: Dict[str, Any]) -> bool:
        """
        Add new help content to the database
        """
        try:
            if category not in self.help_content_db:
                self.help_content_db[category] = []
            
            # Generate unique ID if not provided
            if "id" not in content:
                content["id"] = f"{category}_{len(self.help_content_db[category]) + 1:03d}"
            
            self.help_content_db[category].append(content)
            logger.info(f"Added help content to category: {category}")
            return True
            
        except Exception as e:
            logger.error("Failed to add help content", error=str(e))
            return False
    
    async def get_help_categories(self) -> List[str]:
        """
        Get list of available help categories
        """
        return list(self.help_content_db.keys())
    
    async def get_content_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all help content for a specific category
        """
        return self.help_content_db.get(category, [])
