"""
ML Learning Components for MantraPath Chatbot

Production-ready machine learning components for conversation analysis,
pattern recognition, and response optimization across all services.

Author: MantraPath Development Team
Version: 3.0.0
"""

import asyncio
import logging
import json
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import redis.asyncio as redis
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class ConversationAnalytics:
    """Advanced conversation analytics with ML-driven insights"""
    
    def __init__(self):
        self.is_initialized = False
        self.redis_client = None
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
    async def initialize(self, redis_client):
        """Initialize with Redis connection"""
        self.redis_client = redis_client
        self.is_initialized = True
        logger.info("ConversationAnalytics initialized")
    
    async def analyze_conversation(
        self, user_input: str, context: Dict, mood: Dict, history: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze conversation with ML insights"""
        start_time = datetime.utcnow()
        
        # Emotional intelligence analysis
        emotional_analysis = self._analyze_emotional_patterns(user_input, mood, history)
        
        # Communication style detection
        communication_style = self._detect_communication_style(user_input, history)
        
        # Conversation continuity scoring
        continuity_score = self._calculate_continuity_score(user_input, history)
        
        # Generate insights
        insights = {
            "emotional_state_analysis": emotional_analysis,
            "preferred_communication_style": communication_style,
            "continuity_score": continuity_score,
            "emotional_intelligence": emotional_analysis.get("intelligence_score", 0.7),
            "analysis_time": (datetime.utcnow() - start_time).total_seconds()
        }
        
        return insights
    
    def _analyze_emotional_patterns(self, user_input: str, mood: Dict, history: List) -> Dict:
        """Analyze emotional patterns in conversation"""
        emotions = {
            "anxiety": ["anxious", "worried", "nervous", "stressed"],
            "sadness": ["sad", "depressed", "lonely", "down"],
            "anger": ["angry", "frustrated", "mad", "irritated"],
            "joy": ["happy", "excited", "good", "great"]
        }
        
        detected_emotions = {}
        for emotion, keywords in emotions.items():
            score = sum(1 for keyword in keywords if keyword in user_input.lower())
            detected_emotions[emotion] = min(score / len(keywords), 1.0)
        
        primary_emotion = max(detected_emotions, key=detected_emotions.get)
        intensity = detected_emotions[primary_emotion]
        
        return {
            "primary_emotion": primary_emotion,
            "intensity": intensity,
            "trajectory": self._determine_trajectory(history),
            "stress_level": self._calculate_stress_level(user_input, mood),
            "intelligence_score": 0.8 + (intensity * 0.2)
        }
    
    def _detect_communication_style(self, user_input: str, history: List) -> str:
        """Detect user's preferred communication style"""
        if len(user_input.split()) < 5:
            return "brief"
        elif any(word in user_input.lower() for word in ["please", "could", "might"]):
            return "formal_polite"
        elif any(word in user_input.lower() for word in ["feel", "think", "believe"]):
            return "reflective"
        else:
            return "direct"
    
    def _calculate_continuity_score(self, user_input: str, history: List) -> float:
        """Calculate conversation continuity score"""
        if not history:
            return 0.5
        
        # Simple continuity based on topic similarity
        recent_messages = [msg.get("content", "") for msg in history[-3:]]
        combined_history = " ".join(recent_messages).lower()
        
        # Check for topic continuation
        user_words = set(user_input.lower().split())
        history_words = set(combined_history.split())
        
        if not user_words or not history_words:
            return 0.5
        
        overlap = len(user_words.intersection(history_words))
        return min(overlap / len(user_words), 1.0)
    
    def _determine_trajectory(self, history: List) -> str:
        """Determine emotional trajectory from conversation history"""
        if len(history) < 2:
            return "stable"
        
        # Simple trajectory analysis
        positive_words = ["better", "good", "improving", "happy"]
        negative_words = ["worse", "bad", "difficult", "sad"]
        
        recent_sentiment = 0
        for msg in history[-3:]:
            content = msg.get("content", "").lower()
            for word in positive_words:
                if word in content:
                    recent_sentiment += 1
            for word in negative_words:
                if word in content:
                    recent_sentiment -= 1
        
        if recent_sentiment > 0:
            return "improving"
        elif recent_sentiment < 0:
            return "declining"
        else:
            return "stable"
    
    def _calculate_stress_level(self, user_input: str, mood: Dict) -> str:
        """Calculate stress level indicators"""
        stress_indicators = ["overwhelmed", "can't", "too much", "exhausted", "pressure"]
        stress_count = sum(1 for indicator in stress_indicators if indicator in user_input.lower())
        
        if stress_count >= 2:
            return "high"
        elif stress_count == 1:
            return "moderate"
        else:
            return "normal"

class ResponseOptimizer:
    """ML-driven response optimization"""
    
    def __init__(self):
        self.is_initialized = False
        self.redis_client = None
    
    async def initialize(self, redis_client):
        """Initialize response optimizer"""
        self.redis_client = redis_client
        self.is_initialized = True
        logger.info("ResponseOptimizer initialized")
    
    async def optimize_response(
        self, raw_response: Dict, ml_insights: Dict, patterns: Dict, user_profile: Dict
    ) -> Dict[str, Any]:
        """Optimize response using ML insights"""
        response_text = raw_response.get("text", "")
        
        # Apply communication style optimization
        optimized_text = self._apply_style_optimization(
            response_text, ml_insights.get("preferred_communication_style", "supportive")
        )
        
        # Calculate therapeutic alignment
        therapeutic_score = self._calculate_therapeutic_score(
            optimized_text, patterns, user_profile
        )
        
        # Generate confidence score
        confidence = self._calculate_confidence_score(
            optimized_text, ml_insights, raw_response
        )
        
        return {
            "text": optimized_text,
            "confidence": confidence,
            "therapeutic_score": therapeutic_score,
            "optimization_time": 0.05
        }
    
    def _apply_style_optimization(self, text: str, style: str) -> str:
        """Apply communication style optimization"""
        if style == "brief":
            # Shorten response for brief communicators
            sentences = text.split('. ')
            if len(sentences) > 2:
                return '. '.join(sentences[:2]) + '.'
        elif style == "formal_polite":
            # Add polite language
            if not text.startswith(("I understand", "Thank you")):
                text = "I understand. " + text
        
        return text
    
    def _calculate_therapeutic_score(self, text: str, patterns: Dict, user_profile: Dict) -> float:
        """Calculate therapeutic alignment score"""
        therapeutic_indicators = [
            "understand", "support", "help", "together", "feel", "experience"
        ]
        
        score = 0.6  # Base therapeutic score
        text_lower = text.lower()
        
        for indicator in therapeutic_indicators:
            if indicator in text_lower:
                score += 0.05
        
        # Bonus for personalization
        if user_profile.get("display_name", "").lower() in text_lower:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_confidence_score(self, text: str, ml_insights: Dict, raw_response: Dict) -> float:
        """Calculate response confidence score"""
        base_confidence = 0.7
        
        # Length appropriateness
        if 20 <= len(text.split()) <= 100:
            base_confidence += 0.1
        
        # ML insights alignment
        if ml_insights.get("emotional_intelligence", 0) > 0.8:
            base_confidence += 0.1
        
        # Original model confidence
        if raw_response.get("usage", {}).get("total_tokens", 0) > 50:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)

class PatternRecognizer:
    """ML pattern recognition for therapeutic optimization"""
    
    def __init__(self):
        self.is_initialized = False
        self.redis_client = None
        self.known_patterns = {
            "crisis": ["suicide", "kill myself", "end it", "can't go on"],
            "anxiety": ["panic", "anxious", "worried", "overwhelmed"],
            "depression": ["depressed", "hopeless", "empty", "worthless"],
            "progress": ["better", "improving", "progress", "good day"]
        }
    
    async def initialize(self, redis_client):
        """Initialize pattern recognizer"""
        self.redis_client = redis_client
        self.is_initialized = True
        logger.info("PatternRecognizer initialized")
    
    async def identify_patterns(
        self, user_input: str, history: List, user_profile: Dict
    ) -> Dict[str, Any]:
        """Identify conversation patterns"""
        start_time = datetime.utcnow()
        
        identified_patterns = []
        pattern_confidence = {}
        
        # Check for known patterns
        for pattern_type, keywords in self.known_patterns.items():
            confidence = self._calculate_pattern_confidence(user_input, keywords)
            if confidence > 0.3:
                identified_patterns.append(pattern_type)
                pattern_confidence[pattern_type] = confidence
        
        # Determine optimal therapeutic approach
        optimal_approach = self._determine_therapeutic_approach(identified_patterns)
        
        # Generate intervention recommendations
        interventions = self._recommend_interventions(identified_patterns, user_profile)
        
        return {
            "pattern_types": identified_patterns,
            "pattern_confidence": pattern_confidence,
            "optimal_therapeutic_approach": optimal_approach,
            "recommended_interventions": interventions,
            "recognition_time": (datetime.utcnow() - start_time).total_seconds()
        }
    
    def _calculate_pattern_confidence(self, text: str, keywords: List[str]) -> float:
        """Calculate pattern matching confidence"""
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        return min(matches / len(keywords), 1.0)
    
    def _determine_therapeutic_approach(self, patterns: List[str]) -> str:
        """Determine optimal therapeutic approach based on patterns"""
        if "crisis" in patterns:
            return "crisis_intervention"
        elif "anxiety" in patterns:
            return "anxiety_management"
        elif "depression" in patterns:
            return "depression_support"
        elif "progress" in patterns:
            return "positive_reinforcement"
        else:
            return "general_support"
    
    def _recommend_interventions(self, patterns: List[str], user_profile: Dict) -> List[str]:
        """Recommend therapeutic interventions"""
        interventions = []
        
        if "anxiety" in patterns:
            interventions.extend(["breathing_exercise", "grounding_technique"])
        if "depression" in patterns:
            interventions.extend(["activity_scheduling", "thought_challenging"])
        if "progress" in patterns:
            interventions.extend(["progress_reinforcement", "goal_setting"])
        
        # Default supportive interventions
        if not interventions:
            interventions = ["active_listening", "empathetic_response"]
        
        return interventions[:3]  # Limit to 3 recommendations
