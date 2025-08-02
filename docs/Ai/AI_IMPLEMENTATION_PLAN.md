# 🚀 MantraPath Enhanced AI Implementation Plan
## Technical Implementation Guide for Personalized AI Architecture

### 📋 Implementation Overview

This document provides detailed technical implementation steps for the enhanced AI architecture, including code examples, database schemas, API specifications, and deployment configurations.

---

## 🏗️ Phase 1: Enhanced Chatbot Context Engine
### **Duration**: 3 Weeks | **Priority**: Critical

#### **Week 1: User Context Integration**

##### **1.1 Enhanced User Context Models**

```python
# File: backend/shared/models.py - Add new models

class UserContextSummary(Base):
    """Cached user context for AI services"""
    __tablename__ = "user_context_summaries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Personality and communication preferences
    personality_profile = Column(JSON)  # Big 5 traits, communication style
    writing_style = Column(JSON)  # Tone, vocabulary, themes
    mood_patterns = Column(JSON)  # Trends, triggers, cycles
    engagement_patterns = Column(JSON)  # Active times, preferred features
    crisis_indicators = Column(JSON)  # Risk factors, protective factors
    
    # Preferences
    preferred_language = Column(String, default="en")
    communication_style = Column(String, default="empathetic")  # empathetic, direct, casual
    ai_interaction_level = Column(String, default="full")  # minimal, moderate, full
    
    # Context metadata
    last_updated = Column(DateTime, default=datetime.utcnow)
    context_version = Column(String, default="1.0")
    data_sources = Column(JSON)  # Which services contributed to context
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConversationContext(Base):
    """Conversation memory for chatbot sessions"""
    __tablename__ = "conversation_contexts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    
    # Conversation insights
    key_topics = Column(JSON)  # Main discussion topics
    emotional_journey = Column(JSON)  # Mood changes during conversation
    support_requests = Column(JSON)  # Types of help requested
    breakthrough_moments = Column(JSON)  # Significant insights or progress
    
    # AI response tracking
    response_effectiveness = Column(JSON)  # User feedback on responses
    intervention_triggers = Column(JSON)  # What triggered AI interventions
    
    conversation_summary = Column(Text)  # AI-generated summary
    last_message_timestamp = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIPersonality(Base):
    """AI personality configurations for different users"""
    __tablename__ = "ai_personalities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    
    # AI behavior parameters
    empathy_level = Column(Float, default=0.8)  # 0.0 to 1.0
    directness_level = Column(Float, default=0.6)  # 0.0 to 1.0
    encouragement_style = Column(String, default="gentle")  # gentle, motivational, challenging
    humor_usage = Column(Float, default=0.3)  # 0.0 to 1.0
    
    # Response preferences
    response_length = Column(String, default="medium")  # short, medium, long
    question_frequency = Column(Float, default=0.5)  # How often to ask questions
    suggestion_style = Column(String, default="collaborative")  # directive, collaborative, exploratory
    
    # Conversation style
    greeting_style = Column(String, default="warm")  # formal, warm, casual, energetic
    farewell_style = Column(String, default="supportive")
    crisis_response_style = Column(String, default="immediate")  # immediate, gentle, referral
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

##### **1.2 User Context Engine Implementation**

```python
# File: backend/services/chatbot_service/context_engine.py

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session
from sqlalchemy import desc

from shared.models import (
    User, UserProfile, MoodEntry, JournalEntry, ChatMessage, 
    UserContextSummary, ConversationContext, AIPersonality
)
from shared.database import get_db

@dataclass
class UserContext:
    user_id: str
    profile: Dict[str, Any]
    mood_patterns: Dict[str, Any]
    writing_style: Dict[str, Any]
    conversation_history: Dict[str, Any]
    personality_profile: Dict[str, Any]
    current_state: Dict[str, Any]
    communication_preferences: Dict[str, Any]
    last_updated: datetime

class UserContextEngine:
    def __init__(self):
        self.cache_duration = timedelta(hours=1)  # Cache context for 1 hour
    
    async def get_user_context(self, user_id: str, db: Session) -> UserContext:
        """Get comprehensive user context for AI interactions"""
        
        # Check cache first
        cached_context = self._get_cached_context(user_id, db)
        if cached_context and self._is_cache_valid(cached_context):
            return self._deserialize_context(cached_context)
        
        # Fetch fresh context from all services
        context = await self._build_fresh_context(user_id, db)
        
        # Cache the context
        await self._cache_context(user_id, context, db)
        
        return context
    
    async def _build_fresh_context(self, user_id: str, db: Session) -> UserContext:
        """Build fresh user context from all data sources"""
        
        # Fetch data in parallel
        tasks = await asyncio.gather(
            self._get_user_profile(user_id, db),
            self._analyze_mood_patterns(user_id, db),
            self._analyze_writing_style(user_id, db),
            self._get_conversation_insights(user_id, db),
            self._get_personality_profile(user_id, db),
            self._assess_current_state(user_id, db),
            return_exceptions=True
        )
        
        profile, mood_patterns, writing_style, conversation_history, personality_profile, current_state = tasks
        
        # Get communication preferences
        communication_preferences = await self._get_communication_preferences(user_id, db)
        
        return UserContext(
            user_id=user_id,
            profile=profile,
            mood_patterns=mood_patterns,
            writing_style=writing_style,
            conversation_history=conversation_history,
            personality_profile=personality_profile,
            current_state=current_state,
            communication_preferences=communication_preferences,
            last_updated=datetime.utcnow()
        )
    
    async def _get_user_profile(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get user profile information"""
        user = db.query(User).filter(User.id == user_id).first()
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        return {
            'first_name': user.first_name if user else 'Friend',
            'preferred_language': profile.timezone if profile else 'en',
            'timezone': profile.timezone if profile else 'UTC',
            'notifications_enabled': profile.notifications_enabled if profile else True,
            'privacy_mode': profile.privacy_mode if profile else False
        }
    
    async def _analyze_mood_patterns(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Analyze recent mood patterns"""
        # Get last 30 days of mood entries
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id,
            MoodEntry.created_at >= thirty_days_ago
        ).order_by(desc(MoodEntry.created_at)).all()
        
        if not mood_entries:
            return {'trend': 'neutral', 'stability': 'unknown', 'recent_scores': []}
        
        recent_scores = [entry.mood_score for entry in mood_entries[:7]]
        all_scores = [entry.mood_score for entry in mood_entries]
        
        # Calculate trend
        if len(recent_scores) >= 3:
            trend = 'improving' if recent_scores[0] > recent_scores[-1] else 'declining'
            if abs(recent_scores[0] - recent_scores[-1]) < 0.5:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        # Calculate stability (variance)
        import statistics
        stability = 'stable' if len(all_scores) > 1 and statistics.variance(all_scores) < 1.0 else 'variable'
        
        return {
            'trend': trend,
            'stability': stability,
            'recent_scores': recent_scores,
            'average_mood': statistics.mean(all_scores) if all_scores else 3.0,
            'common_triggers': self._extract_mood_triggers(mood_entries),
            'peak_times': self._identify_peak_mood_times(mood_entries)
        }
    
    async def _analyze_writing_style(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Analyze user's writing style from journal entries"""
        # Get recent journal entries
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        journal_entries = db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.created_at >= thirty_days_ago
        ).limit(20).all()
        
        if not journal_entries:
            return {'style': 'unknown', 'themes': [], 'complexity': 'medium'}
        
        # Analyze common themes and writing patterns
        all_content = ' '.join([entry.content for entry in journal_entries])
        themes = self._extract_themes(all_content)
        
        return {
            'style': 'reflective',  # This would be determined by NLP analysis
            'themes': themes,
            'complexity': 'medium',
            'word_count_average': sum(entry.word_count for entry in journal_entries) / len(journal_entries),
            'sentiment_trend': self._analyze_sentiment_trend(journal_entries)
        }
    
    async def _get_conversation_insights(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get insights from recent conversations"""
        # Get recent conversation context
        recent_context = db.query(ConversationContext).filter(
            ConversationContext.user_id == user_id
        ).order_by(desc(ConversationContext.updated_at)).first()
        
        if not recent_context:
            return {'key_topics': [], 'support_patterns': [], 'effectiveness_score': 0.5}
        
        return {
            'key_topics': recent_context.key_topics or [],
            'emotional_journey': recent_context.emotional_journey or [],
            'support_patterns': recent_context.support_requests or [],
            'effectiveness_score': 0.8,  # Would be calculated from user feedback
            'last_conversation': recent_context.last_message_timestamp
        }
    
    async def _get_personality_profile(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get or generate personality profile"""
        ai_personality = db.query(AIPersonality).filter(
            AIPersonality.user_id == user_id
        ).first()
        
        if not ai_personality:
            # Create default personality profile
            ai_personality = AIPersonality(
                user_id=user_id,
                empathy_level=0.8,
                directness_level=0.6,
                encouragement_style='gentle'
            )
            db.add(ai_personality)
            db.commit()
        
        return {
            'empathy_level': ai_personality.empathy_level,
            'directness_level': ai_personality.directness_level,
            'encouragement_style': ai_personality.encouragement_style,
            'humor_usage': ai_personality.humor_usage,
            'response_length': ai_personality.response_length
        }
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract common themes from text"""
        # This would use NLP to extract themes
        # For now, return mock themes
        common_words = ['growth', 'anxiety', 'gratitude', 'work', 'relationships', 'self-care']
        return common_words[:3]  # Return top 3 themes
    
    def _extract_mood_triggers(self, mood_entries: List[MoodEntry]) -> List[str]:
        """Extract common mood triggers from context tags"""
        all_tags = []
        for entry in mood_entries:
            if entry.context_tags:
                all_tags.extend(entry.context_tags)
        
        # Count frequency and return most common
        from collections import Counter
        if all_tags:
            return [tag for tag, count in Counter(all_tags).most_common(3)]
        return []
```

##### **1.3 Enhanced Response Generation**

```python
# File: backend/services/chatbot_service/response_generator.py

import openai
import json
from typing import Dict, Any, Optional
from datetime import datetime

class PersonalizedResponseGenerator:
    def __init__(self):
        self.openai_client = openai.OpenAI()
        self.crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'no point living',
            'better off dead', 'want to die', 'self harm', 'hurt myself'
        ]
    
    async def generate_response(
        self, 
        user_input: str, 
        context: UserContext,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate personalized response using user context"""
        
        # Check for crisis indicators first
        crisis_level = await self._assess_crisis_level(user_input, context)
        
        if crisis_level == 'high':
            return await self._generate_crisis_response(user_input, context)
        
        # Build context-aware prompt
        prompt = self._build_personalized_prompt(user_input, context, conversation_history)
        
        # Generate response
        try:
            response = await self._call_llm(prompt, context)
            return {
                'response': response,
                'message_type': 'personalized',
                'crisis_level': crisis_level,
                'breathing_exercise': self._check_for_breathing_request(user_input),
                'follow_up_suggestions': self._generate_follow_up_suggestions(context)
            }
        except Exception as e:
            # Fallback to safe response
            return await self._generate_fallback_response(user_input, context)
    
    def _build_personalized_prompt(
        self, 
        user_input: str, 
        context: UserContext,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Build context-aware prompt for LLM"""
        
        # Base personality
        name = context.profile.get('first_name', 'friend')
        empathy_level = context.personality_profile.get('empathy_level', 0.8)
        directness = context.personality_profile.get('directness_level', 0.6)
        
        # Recent context
        mood_trend = context.mood_patterns.get('trend', 'stable')
        recent_themes = ', '.join(context.writing_style.get('themes', []))
        
        # Conversation history summary
        history_context = ""
        if conversation_history:
            recent_messages = conversation_history[-3:]  # Last 3 exchanges
            history_context = f"\nRecent conversation:\n"
            for msg in recent_messages:
                history_context += f"{msg['sender']}: {msg['content'][:100]}...\n"
        
        prompt = f"""You are Mantra-Mitra, a compassionate AI mental health companion. You're talking with {name}.

User Context:
- Mood trend: {mood_trend}
- Recent journal themes: {recent_themes}
- Empathy preference: {empathy_level:.1f}/1.0 (higher = more empathetic)
- Directness preference: {directness:.1f}/1.0 (higher = more direct)
- Communication style: {context.communication_preferences.get('style', 'supportive')}

{history_context}

Current message: "{user_input}"

Respond as Mantra-Mitra with:
1. Deep understanding of {name}'s journey and context
2. Appropriate empathy level ({empathy_level:.1f}/1.0)
3. Appropriate directness ({directness:.1f}/1.0)
4. Reference to their recent patterns and themes when relevant
5. Warm, personalized support that feels genuine

Keep response focused, helpful, and emotionally intelligent."""

        return prompt
    
    async def _call_llm(self, prompt: str, context: UserContext) -> str:
        """Call LLM with privacy considerations"""
        
        # Use local model for high privacy users
        if context.profile.get('privacy_mode'):
            return await self._call_local_llm(prompt)
        
        # Use OpenAI for better responses
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are Mantra-Mitra, a compassionate AI mental health companion."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            # Fallback to simpler model
            return await self._call_local_llm(prompt)
    
    async def _assess_crisis_level(self, user_input: str, context: UserContext) -> str:
        """Assess crisis level in user input"""
        
        # Check for explicit crisis keywords
        input_lower = user_input.lower()
        if any(keyword in input_lower for keyword in self.crisis_keywords):
            return 'high'
        
        # Check context indicators
        recent_mood = context.current_state.get('recent_mood_score', 3)
        if recent_mood <= 2:
            return 'medium'
        
        return 'low'
    
    async def _generate_crisis_response(self, user_input: str, context: UserContext) -> Dict[str, Any]:
        """Generate immediate crisis response"""
        
        name = context.profile.get('first_name', 'friend')
        
        responses = [
            f"{name}, I'm really concerned about what you just shared. Your life has value and meaning, and I want to help you through this difficult time.",
            f"I hear that you're in a lot of pain right now, {name}. Please know that you're not alone, and there are people who can help.",
            f"{name}, thank you for trusting me with these feelings. This takes courage. Let's get you connected with someone who can provide immediate support."
        ]
        
        # Select appropriate response based on personality
        empathy_level = context.personality_profile.get('empathy_level', 0.8)
        response_index = min(int(empathy_level * len(responses)), len(responses) - 1)
        
        return {
            'response': responses[response_index],
            'message_type': 'crisis_support',
            'crisis_level': 'high',
            'crisis_resources': {
                'suicide_hotline': '988',
                'crisis_text_line': 'Text HOME to 741741',
                'emergency': '911'
            },
            'immediate_actions': [
                'Connect with crisis counselor',
                'Call emergency services if immediate danger',
                'Reach out to trusted friend or family member'
            ]
        }
```

#### **Week 2: Conversation Memory & Personality Adaptation**

##### **2.1 Conversation Memory System**

```python
# File: backend/services/chatbot_service/conversation_memory.py

class ConversationMemory:
    def __init__(self):
        self.short_term_limit = 10  # Remember last 10 exchanges
        self.key_moment_threshold = 0.8  # Emotional significance threshold
    
    async def update_conversation_context(
        self, 
        user_id: str, 
        session_id: str,
        user_message: str,
        ai_response: str,
        db: Session
    ):
        """Update conversation context with new exchange"""
        
        # Get or create conversation context
        context = db.query(ConversationContext).filter(
            ConversationContext.user_id == user_id,
            ConversationContext.session_id == session_id
        ).first()
        
        if not context:
            context = ConversationContext(
                user_id=user_id,
                session_id=session_id,
                key_topics=[],
                emotional_journey=[],
                support_requests=[],
                breakthrough_moments=[]
            )
            db.add(context)
        
        # Analyze the exchange
        exchange_analysis = await self._analyze_exchange(user_message, ai_response)
        
        # Update context
        context.key_topics = self._update_key_topics(context.key_topics, exchange_analysis['topics'])
        context.emotional_journey = self._update_emotional_journey(
            context.emotional_journey, 
            exchange_analysis['emotion']
        )
        
        # Detect breakthrough moments
        if exchange_analysis['significance'] > self.key_moment_threshold:
            context.breakthrough_moments.append({
                'timestamp': datetime.utcnow().isoformat(),
                'content': user_message[:200],
                'significance': exchange_analysis['significance'],
                'type': exchange_analysis['breakthrough_type']
            })
        
        context.last_message_timestamp = datetime.utcnow()
        context.updated_at = datetime.utcnow()
        
        db.commit()
        
        return context
    
    async def _analyze_exchange(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """Analyze conversation exchange for insights"""
        
        # Extract topics (simplified - would use NLP)
        topics = self._extract_topics(user_message)
        
        # Assess emotional content
        emotion = self._assess_emotion(user_message)
        
        # Determine significance
        significance = self._calculate_significance(user_message, emotion)
        
        # Detect breakthrough type
        breakthrough_type = self._detect_breakthrough_type(user_message)
        
        return {
            'topics': topics,
            'emotion': emotion,
            'significance': significance,
            'breakthrough_type': breakthrough_type
        }
    
    def _extract_topics(self, message: str) -> List[str]:
        """Extract conversation topics"""
        # Simplified topic extraction
        topic_keywords = {
            'anxiety': ['anxious', 'worried', 'nervous', 'panic'],
            'depression': ['sad', 'depressed', 'down', 'hopeless'],
            'relationships': ['partner', 'friend', 'family', 'relationship'],
            'work': ['job', 'work', 'career', 'boss', 'colleague'],
            'self_care': ['sleep', 'exercise', 'meditation', 'self-care']
        }
        
        message_lower = message.lower()
        detected_topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics
```

##### **2.2 Personality Adaptation Engine**

```python
# File: backend/services/chatbot_service/personality_adapter.py

class PersonalityAdapter:
    def __init__(self):
        self.adaptation_rate = 0.1  # How quickly to adapt to user feedback
    
    async def adapt_response(
        self, 
        base_response: str, 
        context: UserContext,
        user_feedback: Optional[Dict[str, Any]] = None
    ) -> str:
        """Adapt response based on user personality and preferences"""
        
        personality = context.personality_profile
        
        # Adjust empathy level
        if personality.get('empathy_level', 0.8) > 0.7:
            base_response = self._increase_empathy(base_response)
        
        # Adjust directness
        if personality.get('directness_level', 0.6) > 0.7:
            base_response = self._increase_directness(base_response)
        elif personality.get('directness_level', 0.6) < 0.4:
            base_response = self._soften_directness(base_response)
        
        # Adjust response length
        preferred_length = personality.get('response_length', 'medium')
        if preferred_length == 'short':
            base_response = self._shorten_response(base_response)
        elif preferred_length == 'long':
            base_response = self._expand_response(base_response, context)
        
        # Add humor if appropriate
        humor_level = personality.get('humor_usage', 0.3)
        if humor_level > 0.5 and context.current_state.get('mood_level', 3) > 3:
            base_response = self._add_light_humor(base_response)
        
        return base_response
    
    def _increase_empathy(self, response: str) -> str:
        """Increase empathetic language in response"""
        empathy_phrases = [
            "I can really understand how that feels.",
            "That sounds incredibly challenging.",
            "I hear the pain in what you're sharing.",
            "It's completely understandable to feel that way."
        ]
        
        # Add empathetic phrase if not already present
        if not any(phrase.lower() in response.lower() for phrase in empathy_phrases):
            return f"{empathy_phrases[0]} {response}"
        
        return response
    
    def _increase_directness(self, response: str) -> str:
        """Make response more direct and action-oriented"""
        # Replace tentative language with more direct language
        replacements = {
            'might want to consider': 'should',
            'perhaps try': 'try',
            'maybe think about': 'consider',
            'could be helpful': 'will help'
        }
        
        for tentative, direct in replacements.items():
            response = response.replace(tentative, direct)
        
        return response
    
    async def learn_from_feedback(
        self, 
        user_id: str, 
        response_id: str, 
        feedback: Dict[str, Any],
        db: Session
    ):
        """Learn from user feedback to improve personality matching"""
        
        # Get current personality settings
        ai_personality = db.query(AIPersonality).filter(
            AIPersonality.user_id == user_id
        ).first()
        
        if not ai_personality:
            return
        
        # Adjust based on feedback
        if feedback.get('too_long'):
            # User prefers shorter responses
            if ai_personality.response_length == 'long':
                ai_personality.response_length = 'medium'
            elif ai_personality.response_length == 'medium':
                ai_personality.response_length = 'short'
        
        if feedback.get('not_empathetic_enough'):
            # Increase empathy level
            ai_personality.empathy_level = min(1.0, ai_personality.empathy_level + self.adaptation_rate)
        
        if feedback.get('too_direct'):
            # Decrease directness
            ai_personality.directness_level = max(0.0, ai_personality.directness_level - self.adaptation_rate)
        
        ai_personality.updated_at = datetime.utcnow()
        db.commit()
```

#### **Week 3: Crisis Detection Integration**

##### **3.1 Enhanced Crisis Detection**

```python
# File: backend/services/chatbot_service/enhanced_crisis_detector.py

import re
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class CrisisAssessment:
    risk_level: str  # 'low', 'medium', 'high', 'immediate'
    confidence: float
    risk_factors: List[str]
    protective_factors: List[str]
    recommended_actions: List[str]
    urgency_score: float

class EnhancedCrisisDetector:
    def __init__(self):
        self.crisis_keywords = {
            'high_risk': [
                'kill myself', 'end it all', 'suicide', 'better off dead',
                'want to die', 'no point living', 'plan to hurt',
                'goodbye forever', 'final message'
            ],
            'medium_risk': [
                'hurt myself', 'self harm', 'cut myself', 'hate myself',
                'worthless', 'burden', 'disappear', 'give up'
            ],
            'low_risk': [
                'depressed', 'hopeless', 'empty', 'lonely', 'trapped',
                'overwhelmed', 'can\'t cope', 'too much'
            ]
        }
        
        self.protective_phrases = [
            'but i won\'t', 'getting help', 'talking to someone',
            'support system', 'therapy', 'medication', 'family',
            'friends care', 'things will get better'
        ]
    
    async def assess_crisis_risk(
        self, 
        user_input: str, 
        context: UserContext,
        conversation_history: List[Dict[str, str]] = None
    ) -> CrisisAssessment:
        """Comprehensive crisis risk assessment"""
        
        # Text-based risk assessment
        text_risk = self._assess_text_risk(user_input)
        
        # Context-based risk assessment
        context_risk = self._assess_context_risk(context)
        
        # Pattern-based risk assessment
        pattern_risk = self._assess_pattern_risk(conversation_history, context)
        
        # Combine assessments
        overall_risk = self._combine_risk_assessments(text_risk, context_risk, pattern_risk)
        
        return overall_risk
    
    def _assess_text_risk(self, text: str) -> Dict[str, Any]:
        """Assess risk based on text content"""
        text_lower = text.lower()
        
        risk_scores = {
            'high_risk': 0,
            'medium_risk': 0,
            'low_risk': 0
        }
        
        detected_keywords = []
        
        # Check for crisis keywords
        for risk_level, keywords in self.crisis_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    risk_scores[risk_level] += 1
                    detected_keywords.append(keyword)
        
        # Check for protective factors
        protective_factors = []
        for phrase in self.protective_phrases:
            if phrase in text_lower:
                protective_factors.append(phrase)
        
        # Calculate risk level
        if risk_scores['high_risk'] > 0:
            risk_level = 'high'
            confidence = 0.9
        elif risk_scores['medium_risk'] > 1:
            risk_level = 'medium'
            confidence = 0.7
        elif risk_scores['low_risk'] > 2:
            risk_level = 'medium'
            confidence = 0.6
        elif risk_scores['low_risk'] > 0:
            risk_level = 'low'
            confidence = 0.5
        else:
            risk_level = 'minimal'
            confidence = 0.8
        
        # Reduce risk if protective factors present
        if protective_factors and risk_level in ['medium', 'high']:
            confidence *= 0.7
        
        return {
            'risk_level': risk_level,
            'confidence': confidence,
            'detected_keywords': detected_keywords,
            'protective_factors': protective_factors
        }
    
    def _assess_context_risk(self, context: UserContext) -> Dict[str, Any]:
        """Assess risk based on user context"""
        
        risk_factors = []
        protective_factors = []
        
        # Mood pattern analysis
        mood_trend = context.mood_patterns.get('trend', 'stable')
        avg_mood = context.mood_patterns.get('average_mood', 3.0)
        
        if mood_trend == 'declining':
            risk_factors.append('declining_mood_trend')
        
        if avg_mood < 2.5:
            risk_factors.append('persistently_low_mood')
        elif avg_mood > 3.5:
            protective_factors.append('generally_positive_mood')
        
        # Social connection indicators
        conversation_history = context.conversation_history
        if conversation_history.get('support_patterns'):
            protective_factors.append('seeking_support')
        
        # Recent engagement
        last_conversation = conversation_history.get('last_conversation')
        if last_conversation:
            days_since = (datetime.utcnow() - last_conversation).days
            if days_since > 7:
                risk_factors.append('social_withdrawal')
        
        # Calculate context risk
        risk_score = len(risk_factors) - len(protective_factors)
        
        if risk_score >= 2:
            context_risk = 'high'
        elif risk_score >= 1:
            context_risk = 'medium'
        elif risk_score <= -1:
            context_risk = 'low'
        else:
            context_risk = 'baseline'
        
        return {
            'risk_level': context_risk,
            'risk_factors': risk_factors,
            'protective_factors': protective_factors
        }
    
    def _combine_risk_assessments(
        self, 
        text_risk: Dict[str, Any], 
        context_risk: Dict[str, Any],
        pattern_risk: Dict[str, Any]
    ) -> CrisisAssessment:
        """Combine all risk assessments into final assessment"""
        
        # Risk level mapping
        risk_levels = {'minimal': 0, 'low': 1, 'medium': 2, 'high': 3, 'immediate': 4}
        
        # Get highest risk level
        text_level = risk_levels.get(text_risk['risk_level'], 0)
        context_level = risk_levels.get(context_risk['risk_level'], 0)
        pattern_level = risk_levels.get(pattern_risk.get('risk_level', 'minimal'), 0)
        
        max_risk = max(text_level, context_level, pattern_level)
        
        # Map back to risk level
        level_names = ['minimal', 'low', 'medium', 'high', 'immediate']
        final_risk_level = level_names[min(max_risk, len(level_names) - 1)]
        
        # Calculate confidence
        confidences = [
            text_risk.get('confidence', 0.5),
            context_risk.get('confidence', 0.5),
            pattern_risk.get('confidence', 0.5)
        ]
        final_confidence = sum(confidences) / len(confidences)
        
        # Combine risk and protective factors
        all_risk_factors = (
            text_risk.get('detected_keywords', []) +
            context_risk.get('risk_factors', []) +
            pattern_risk.get('risk_factors', [])
        )
        
        all_protective_factors = (
            text_risk.get('protective_factors', []) +
            context_risk.get('protective_factors', []) +
            pattern_risk.get('protective_factors', [])
        )
        
        # Generate recommendations
        recommended_actions = self._generate_crisis_recommendations(final_risk_level)
        
        return CrisisAssessment(
            risk_level=final_risk_level,
            confidence=final_confidence,
            risk_factors=all_risk_factors,
            protective_factors=all_protective_factors,
            recommended_actions=recommended_actions,
            urgency_score=max_risk / 4.0
        )
    
    def _generate_crisis_recommendations(self, risk_level: str) -> List[str]:
        """Generate appropriate recommendations based on risk level"""
        
        recommendations = {
            'immediate': [
                'Contact emergency services (911)',
                'Go to nearest emergency room',
                'Call National Suicide Prevention Lifeline: 988',
                'Do not leave person alone'
            ],
            'high': [
                'Contact mental health professional immediately',
                'Call crisis hotline: 988',
                'Reach out to trusted friend or family member',
                'Consider safety planning'
            ],
            'medium': [
                'Schedule appointment with therapist',
                'Use crisis text line: Text HOME to 741741',
                'Practice grounding techniques',
                'Engage support network'
            ],
            'low': [
                'Consider speaking with counselor',
                'Practice self-care activities',
                'Maintain regular sleep schedule',
                'Stay connected with support system'
            ],
            'minimal': [
                'Continue regular self-care',
                'Monitor mood changes',
                'Maintain healthy routines'
            ]
        }
        
        return recommendations.get(risk_level, [])
```

---

## 🎯 Implementation Tasks for Week 1

### **Database Migration**

```sql
-- File: backend/database/migrations/001_add_ai_context_tables.sql

-- User Context Summary Table
CREATE TABLE user_context_summaries (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    personality_profile JSON,
    writing_style JSON,
    mood_patterns JSON,
    engagement_patterns JSON,
    crisis_indicators JSON,
    preferred_language VARCHAR(10) DEFAULT 'en',
    communication_style VARCHAR(20) DEFAULT 'empathetic',
    ai_interaction_level VARCHAR(20) DEFAULT 'full',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context_version VARCHAR(10) DEFAULT '1.0',
    data_sources JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Conversation Context Table
CREATE TABLE conversation_contexts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    session_id VARCHAR(36) NOT NULL,
    key_topics JSON,
    emotional_journey JSON,
    support_requests JSON,
    breakthrough_moments JSON,
    response_effectiveness JSON,
    intervention_triggers JSON,
    conversation_summary TEXT,
    last_message_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);

-- AI Personality Table
CREATE TABLE ai_personalities (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    empathy_level FLOAT DEFAULT 0.8,
    directness_level FLOAT DEFAULT 0.6,
    encouragement_style VARCHAR(20) DEFAULT 'gentle',
    humor_usage FLOAT DEFAULT 0.3,
    response_length VARCHAR(10) DEFAULT 'medium',
    question_frequency FLOAT DEFAULT 0.5,
    suggestion_style VARCHAR(20) DEFAULT 'collaborative',
    greeting_style VARCHAR(20) DEFAULT 'warm',
    farewell_style VARCHAR(20) DEFAULT 'supportive',
    crisis_response_style VARCHAR(20) DEFAULT 'immediate',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX idx_user_context_user_id ON user_context_summaries(user_id);
CREATE INDEX idx_conversation_context_user_id ON conversation_contexts(user_id);
CREATE INDEX idx_conversation_context_session_id ON conversation_contexts(session_id);
CREATE INDEX idx_ai_personality_user_id ON ai_personalities(user_id);
```

### **Enhanced Chatbot Service Updates**

```python
# File: backend/services/chatbot_service/main.py - Enhanced version

"""
Enhanced Chatbot Service - AI-powered conversational support with full user context
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
import json
import asyncio

# Add parent directories to path
sys.path.append('/app')
sys.path.append('/app/shared')

from shared.database import get_db, engine
from shared.models import ChatSession, ChatMessage, Base, UserContextSummary, ConversationContext
from shared.auth import get_current_user

# Import new context engine components
from context_engine import UserContextEngine
from response_generator import PersonalizedResponseGenerator
from conversation_memory import ConversationMemory
from personality_adapter import PersonalityAdapter
from enhanced_crisis_detector import EnhancedCrisisDetector

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MantraPath Enhanced Chatbot Service",
    description="AI chatbot with personalized support using complete user context",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize enhanced components
context_engine = UserContextEngine()
response_generator = PersonalizedResponseGenerator()
conversation_memory = ConversationMemory()
personality_adapter = PersonalityAdapter()
crisis_detector = EnhancedCrisisDetector()

# Enhanced Pydantic models
class EnhancedChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context_refresh: bool = False  # Force context refresh

class EnhancedChatResponse(BaseModel):
    response: str
    session_id: str
    message_type: str = "personalized"
    crisis_level: str = "low"
    personalization_score: float = 0.0
    breathing_exercise: Optional[dict] = None
    follow_up_suggestions: List[str] = []
    crisis_resources: Optional[Dict[str, str]] = None

class UserFeedback(BaseModel):
    message_id: str
    rating: int  # 1-5 rating
    feedback_type: str  # 'helpful', 'not_helpful', 'too_long', 'too_short', etc.
    comments: Optional[str] = None

# Enhanced chat endpoint
@app.post("/api/chatbot/enhanced/chat", response_model=EnhancedChatResponse)
async def enhanced_chat_with_bot(
    chat_request: EnhancedChatRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enhanced chat with full user context and personalization"""
    
    user_id = current_user["user_id"]
    
    # Get or create session
    session = await get_or_create_session(chat_request.session_id, user_id, db)
    
    # Get comprehensive user context
    user_context = await context_engine.get_user_context(user_id, db)
    
    # Get conversation history
    conversation_history = await get_conversation_history(session.id, db)
    
    # Assess crisis risk
    crisis_assessment = await crisis_detector.assess_crisis_risk(
        chat_request.message, 
        user_context, 
        conversation_history
    )
    
    # Save user message
    user_message = ChatMessage(
        session_id=session.id,
        sender="user",
        content=chat_request.message,
        message_type="text"
    )
    db.add(user_message)
    
    # Generate personalized response
    response_data = await response_generator.generate_response(
        chat_request.message,
        user_context,
        conversation_history
    )
    
    # Adapt response based on personality
    adapted_response = await personality_adapter.adapt_response(
        response_data['response'],
        user_context
    )
    
    # Save AI message
    ai_message = ChatMessage(
        session_id=session.id,
        sender="assistant",
        content=adapted_response,
        message_type=response_data['message_type'],
        metadata={
            "crisis_level": crisis_assessment.risk_level,
            "personalization_score": calculate_personalization_score(user_context),
            "crisis_assessment": {
                "risk_level": crisis_assessment.risk_level,
                "confidence": crisis_assessment.confidence,
                "risk_factors": crisis_assessment.risk_factors
            }
        }
    )
    db.add(ai_message)
    db.commit()
    
    # Update conversation memory in background
    background_tasks.add_task(
        conversation_memory.update_conversation_context,
        user_id, session.id, chat_request.message, adapted_response, db
    )
    
    return EnhancedChatResponse(
        response=adapted_response,
        session_id=str(session.id),
        message_type=response_data['message_type'],
        crisis_level=crisis_assessment.risk_level,
        personalization_score=calculate_personalization_score(user_context),
        breathing_exercise=response_data.get('breathing_exercise'),
        follow_up_suggestions=response_data.get('follow_up_suggestions', []),
        crisis_resources=response_data.get('crisis_resources') if crisis_assessment.risk_level == 'high' else None
    )

@app.post("/api/chatbot/feedback")
async def submit_feedback(
    feedback: UserFeedback,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback for AI response improvement"""
    
    user_id = current_user["user_id"]
    
    # Learn from feedback
    await personality_adapter.learn_from_feedback(
        user_id, 
        feedback.message_id, 
        {
            'rating': feedback.rating,
            'feedback_type': feedback.feedback_type,
            'comments': feedback.comments
        },
        db
    )
    
    return {"message": "Feedback received and will improve future responses"}

# Helper functions
async def get_or_create_session(session_id: Optional[str], user_id: str, db: Session) -> ChatSession:
    """Get existing session or create new one"""
    if session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()
        if session:
            return session
    
    # Create new session
    session = ChatSession(
        user_id=user_id,
        title="Enhanced Chat Session",
        session_type="personalized"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

async def get_conversation_history(session_id: str, db: Session) -> List[Dict[str, str]]:
    """Get recent conversation history"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.desc()).limit(10).all()
    
    return [
        {
            'sender': msg.sender,
            'content': msg.content,
            'timestamp': msg.created_at.isoformat()
        }
        for msg in reversed(messages)
    ]

def calculate_personalization_score(context) -> float:
    """Calculate how well personalized the response is"""
    # This would be more sophisticated in practice
    score = 0.5  # Base score
    
    if context.mood_patterns.get('trend') != 'unknown':
        score += 0.2
    
    if context.writing_style.get('themes'):
        score += 0.2
    
    if context.conversation_history.get('key_topics'):
        score += 0.1
    
    return min(score, 1.0)

# Health check
@app.get("/health")
async def health_check():
    """Enhanced health check with AI component status"""
    return {
        "status": "healthy",
        "service": "enhanced_chatbot_service",
        "version": "2.0.0",
        "timestamp": datetime.utcnow(),
        "components": {
            "context_engine": "ready",
            "response_generator": "ready",
            "conversation_memory": "ready",
            "personality_adapter": "ready",
            "crisis_detector": "ready"
        },
        "features": [
            "personalized_responses",
            "crisis_detection",
            "conversation_memory",
            "personality_adaptation",
            "user_feedback_learning"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
```

This completes the detailed implementation plan for Phase 1. The enhanced chatbot will now have:

1. **Complete User Context Awareness**: Access to mood patterns, journal themes, community behavior
2. **Personalized Response Generation**: Tailored responses based on user personality and preferences  
3. **Conversation Memory**: Maintains context across sessions and remembers important moments
4. **Crisis Detection**: Enhanced crisis monitoring using full user context
5. **Adaptive Personality**: Learns from user feedback to improve interaction style

The next phases will build upon this foundation to add the Journal Assistant Service and Intelligent Feeds Engine.
