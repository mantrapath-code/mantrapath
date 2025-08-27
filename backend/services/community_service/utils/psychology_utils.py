"""
Psychology-based utility functions for community service
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import re

from config.psychology_config import (
    WELLNESS_COLORS, MOOD_COLOR_MAPPING, PSYCHOLOGICAL_FOCUS_AREAS,
    DEFAULT_CALMING_THEME, INTERACTION_GUIDELINES, FEED_ALGORITHM_WEIGHTS
)


class PsychologyUtils:
    """Utility functions for psychology-based community features"""
    
    @staticmethod
    def get_mood_responsive_theme(current_mood: str, user_preferences: Optional[Dict] = None) -> Dict:
        """Get theme colors based on user's current mood"""
        base_theme = DEFAULT_CALMING_THEME.copy()
        
        if current_mood in MOOD_COLOR_MAPPING:
            mood_colors = MOOD_COLOR_MAPPING[current_mood]
            # Apply mood-specific colors
            if len(mood_colors) >= 3:
                base_theme["primary"] = WELLNESS_COLORS[mood_colors[0]]
                base_theme["secondary"] = WELLNESS_COLORS[mood_colors[1]]
                base_theme["accent"] = WELLNESS_COLORS[mood_colors[2]]
        
        # Apply user preferences if available
        if user_preferences and "preferred_colors" in user_preferences:
            for key, color in user_preferences["preferred_colors"].items():
                if key in base_theme:
                    base_theme[key] = color
        
        return base_theme
    
    @staticmethod
    def calculate_calming_score(content: str) -> float:
        """Calculate how calming a piece of content is (0.0 to 1.0)"""
        calming_keywords = [
            "peaceful", "calm", "breathe", "gentle", "soothing", "mindful",
            "meditation", "relax", "serene", "tranquil", "harmony", "balance",
            "support", "understanding", "compassion", "empathy", "healing"
        ]
        
        stress_keywords = [
            "stressed", "anxious", "panic", "worried", "overwhelmed", "crisis",
            "urgent", "emergency", "desperate", "breaking", "disaster"
        ]
        
        content_lower = content.lower()
        
        # Count calming words
        calming_count = sum(1 for word in calming_keywords if word in content_lower)
        
        # Count stress words (negative impact)
        stress_count = sum(1 for word in stress_keywords if word in content_lower)
        
        # Base score calculation
        total_words = len(content.split())
        if total_words == 0:
            return 0.5
        
        calming_ratio = calming_count / total_words
        stress_ratio = stress_count / total_words
        
        # Calculate score (0.0 to 1.0)
        score = 0.5 + (calming_ratio * 0.5) - (stress_ratio * 0.3)
        return max(0.0, min(1.0, score))
    
    @staticmethod
    def analyze_supportive_language(content: str) -> float:
        """Analyze how supportive the language is (0.0 to 1.0)"""
        encouraged_phrases = INTERACTION_GUIDELINES["supportive_language"]["encouraged"]
        discouraged_phrases = INTERACTION_GUIDELINES["supportive_language"]["discouraged"]
        
        content_lower = content.lower()
        
        encouraged_count = sum(1 for phrase in encouraged_phrases if phrase.lower() in content_lower)
        discouraged_count = sum(1 for phrase in discouraged_phrases if phrase.lower() in content_lower)
        
        # Additional supportive indicators
        empathy_indicators = ["feel", "understand", "hear you", "been there", "similar", "relate"]
        empathy_count = sum(1 for indicator in empathy_indicators if indicator in content_lower)
        
        # Calculate supportiveness
        total_indicators = encouraged_count + empathy_count
        negative_indicators = discouraged_count
        
        if total_indicators == 0 and negative_indicators == 0:
            return 0.5  # Neutral
        
        score = 0.5 + (total_indicators * 0.1) - (negative_indicators * 0.2)
        return max(0.0, min(1.0, score))
    
    @staticmethod
    def detect_crisis_indicators(content: str) -> Tuple[bool, List[str]]:
        """Detect potential crisis indicators in content"""
        crisis_keywords = INTERACTION_GUIDELINES["crisis_keywords"]
        
        content_lower = content.lower()
        detected_keywords = []
        
        for keyword in crisis_keywords:
            if keyword in content_lower:
                detected_keywords.append(keyword)
        
        # Additional patterns for crisis detection
        crisis_patterns = [
            r"want to die",
            r"kill myself",
            r"end my life",
            r"no way out",
            r"can't go on",
            r"hurt myself"
        ]
        
        for pattern in crisis_patterns:
            if re.search(pattern, content_lower):
                detected_keywords.append(f"pattern: {pattern}")
        
        is_crisis = len(detected_keywords) > 0
        return is_crisis, detected_keywords
    
    @staticmethod
    def generate_calming_prompt() -> str:
        """Generate a random calming prompt"""
        import random
        prompts = INTERACTION_GUIDELINES["calming_prompts"]
        return random.choice(prompts)
    
    @staticmethod
    def calculate_psychological_relevance(content: str, user_profile: Dict) -> float:
        """Calculate how psychologically relevant content is for a user"""
        if not user_profile.get("wellness_goals"):
            return 0.5
        
        content_lower = content.lower()
        user_goals = user_profile.get("wellness_goals", [])
        preferred_focus = user_profile.get("preferred_psychological_focus", [])
        
        relevance_score = 0.0
        
        # Check alignment with wellness goals
        for goal in user_goals:
            if goal.lower() in content_lower:
                relevance_score += 0.2
        
        # Check psychological focus alignment
        for focus in preferred_focus:
            if focus.lower() in content_lower:
                relevance_score += 0.3
        
        # Bonus for supportive content
        supportive_score = PsychologyUtils.analyze_supportive_language(content)
        relevance_score += supportive_score * 0.2
        
        return min(1.0, relevance_score)
    
    @staticmethod
    def get_time_based_theme_adjustment() -> Dict:
        """Adjust theme based on time of day for circadian wellness"""
        current_hour = datetime.now().hour
        
        if 22 <= current_hour or current_hour <= 6:  # Night time
            return {
                "adjustment": "darker",
                "primary": "#2C5282",  # Darker blue
                "background": "#1A1A1A",  # Very dark
                "text": "#E2E8F0"  # Light text
            }
        elif 6 < current_hour <= 10:  # Morning
            return {
                "adjustment": "energizing",
                "primary": WELLNESS_COLORS["gentle_teal"],
                "accent": WELLNESS_COLORS["warm_yellow"]
            }
        elif 18 <= current_hour < 22:  # Evening
            return {
                "adjustment": "calming",
                "primary": WELLNESS_COLORS["lavender"],
                "accent": WELLNESS_COLORS["soft_purple"]
            }
        else:  # Day time
            return {
                "adjustment": "balanced",
                "primary": WELLNESS_COLORS["calm_blue"],
                "secondary": WELLNESS_COLORS["sage_green"]
            }
    
    @staticmethod
    def calculate_feed_score(item_data: Dict, user_profile: Dict) -> float:
        """Calculate overall feed relevance score using weighted algorithm"""
        weights = FEED_ALGORITHM_WEIGHTS
        
        psychological_relevance = PsychologyUtils.calculate_psychological_relevance(
            item_data.get("content", ""), user_profile
        )
        calming_effect = item_data.get("calming_score", 0.5)
        
        # Calculate engagement prediction based on user patterns
        engagement_prediction = 0.5  # Default
        if user_profile.get("interaction_patterns"):
            # Simple engagement prediction based on historical data
            patterns = user_profile["interaction_patterns"]
            if item_data.get("content_type") in patterns.get("preferred_content_types", []):
                engagement_prediction = 0.8
        
        # Recency factor (newer content gets slight boost)
        created_at = item_data.get("created_at")
        if created_at:
            hours_old = (datetime.now() - created_at).total_seconds() / 3600
            recency_factor = max(0.1, 1.0 - (hours_old / 168))  # Decay over a week
        else:
            recency_factor = 0.5
        
        # Calculate weighted score
        total_score = (
            psychological_relevance * weights["psychological_relevance"] +
            calming_effect * weights["calming_effect"] +
            engagement_prediction * weights["community_engagement"] +
            recency_factor * weights["recency"]
        )
        
        return min(1.0, total_score)


class CommunityAnalytics:
    """Analytics for community psychological wellness"""
    
    @staticmethod
    def calculate_community_wellness_score(conversations: List[Dict]) -> float:
        """Calculate overall wellness score for a community"""
        if not conversations:
            return 0.5
        
        total_calming = sum(conv.get("calming_score", 0.5) for conv in conversations)
        total_supportive = sum(
            PsychologyUtils.analyze_supportive_language(conv.get("content", ""))
            for conv in conversations
        )
        
        avg_calming = total_calming / len(conversations)
        avg_supportive = total_supportive / len(conversations)
        
        wellness_score = (avg_calming * 0.6) + (avg_supportive * 0.4)
        return min(1.0, wellness_score)
    
    @staticmethod
    def identify_community_mood_trends(conversations: List[Dict], time_window_hours: int = 24) -> Dict:
        """Identify mood trends in community conversations"""
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        recent_conversations = [
            conv for conv in conversations
            if conv.get("created_at", datetime.min) > cutoff_time
        ]
        
        if not recent_conversations:
            return {"trend": "neutral", "dominant_mood": "calm", "crisis_alerts": []}
        
        # Analyze mood indicators
        crisis_count = 0
        total_calming = 0
        mood_indicators = {"positive": 0, "negative": 0, "crisis": 0}
        
        for conv in recent_conversations:
            content = conv.get("content", "")
            
            # Check for crisis
            is_crisis, _ = PsychologyUtils.detect_crisis_indicators(content)
            if is_crisis:
                crisis_count += 1
                mood_indicators["crisis"] += 1
            
            # Calming score
            calming_score = conv.get("calming_score", 
                PsychologyUtils.calculate_calming_score(content))
            total_calming += calming_score
            
            if calming_score > 0.6:
                mood_indicators["positive"] += 1
            elif calming_score < 0.4:
                mood_indicators["negative"] += 1
        
        avg_calming = total_calming / len(recent_conversations)
        
        # Determine trend
        if crisis_count > len(recent_conversations) * 0.1:  # More than 10% crisis indicators
            trend = "crisis_alert"
        elif avg_calming > 0.7:
            trend = "positive"
        elif avg_calming < 0.3:
            trend = "concerning"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "avg_calming_score": avg_calming,
            "mood_indicators": mood_indicators,
            "crisis_count": crisis_count,
            "total_conversations": len(recent_conversations)
        }
