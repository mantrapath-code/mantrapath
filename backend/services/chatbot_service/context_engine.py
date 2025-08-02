"""
Enhanced User Context Engine for MantraPath Chatbot
Provides comprehensive user context from all services for personalized AI interactions
"""

import asyncio
import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from collections import Counter

# Import existing models
from shared.models import (
    User, UserProfile, MoodEntry, JournalEntry, ChatMessage, ChatSession,
    CommunityForum, ForumThread, ThreadReply, ForumMembership
)

logger = logging.getLogger(__name__)

@dataclass
class UserContext:
    """Comprehensive user context for AI interactions"""
    user_id: str
    profile: Dict[str, Any]
    mood_patterns: Dict[str, Any]
    writing_style: Dict[str, Any]
    community_behavior: Dict[str, Any]
    conversation_history: Dict[str, Any]
    current_state: Dict[str, Any]
    communication_preferences: Dict[str, Any]
    last_updated: datetime
    context_version: str = "1.0"

class UserContextEngine:
    """
    Central engine for gathering and processing comprehensive user context
    from all MantraPath services for personalized AI interactions
    """
    
    def __init__(self):
        self.cache_duration = timedelta(hours=1)
        self.context_cache = {}  # In-memory cache (use Redis in production)
    
    async def get_user_context(self, user_id: str, db: Session, force_refresh: bool = False) -> UserContext:
        """
        Get comprehensive user context for AI interactions
        
        Args:
            user_id: User ID to get context for
            db: Database session
            force_refresh: Force refresh context cache
            
        Returns:
            UserContext object with complete user information
        """
        
        # Check cache first
        if not force_refresh:
            cached_context = self._get_cached_context(user_id)
            if cached_context:
                return cached_context
        
        logger.info(f"Building fresh context for user {user_id}")
        
        try:
            # Gather data from all services in parallel
            context_data = await asyncio.gather(
                self._get_user_profile(user_id, db),
                self._analyze_mood_patterns(user_id, db),
                self._analyze_writing_style(user_id, db),
                self._analyze_community_behavior(user_id, db),
                self._get_conversation_insights(user_id, db),
                self._assess_current_state(user_id, db),
                return_exceptions=True
            )
            
            (profile, mood_patterns, writing_style, 
             community_behavior, conversation_history, current_state) = context_data
            
            # Handle any exceptions in data gathering
            profile = profile if not isinstance(profile, Exception) else self._get_default_profile()
            mood_patterns = mood_patterns if not isinstance(mood_patterns, Exception) else self._get_default_mood_patterns()
            writing_style = writing_style if not isinstance(writing_style, Exception) else self._get_default_writing_style()
            community_behavior = community_behavior if not isinstance(community_behavior, Exception) else self._get_default_community_behavior()
            conversation_history = conversation_history if not isinstance(conversation_history, Exception) else self._get_default_conversation_history()
            current_state = current_state if not isinstance(current_state, Exception) else self._get_default_current_state()
            
            # Generate communication preferences
            communication_preferences = self._generate_communication_preferences(
                profile, mood_patterns, community_behavior
            )
            
            # Create comprehensive context
            context = UserContext(
                user_id=user_id,
                profile=profile,
                mood_patterns=mood_patterns,
                writing_style=writing_style,
                community_behavior=community_behavior,
                conversation_history=conversation_history,
                current_state=current_state,
                communication_preferences=communication_preferences,
                last_updated=datetime.utcnow()
            )
            
            # Cache the context
            self._cache_context(user_id, context)
            
            logger.info(f"Successfully built context for user {user_id}")
            return context
            
        except Exception as e:
            logger.error(f"Error building context for user {user_id}: {e}")
            return self._get_fallback_context(user_id)
    
    async def _get_user_profile(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get user profile information"""
        
        user = db.query(User).filter(User.id == user_id).first()
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not user:
            logger.warning(f"User not found: {user_id}")
            return self._get_default_profile()
        
        return {
            'user_id': user_id,
            'first_name': user.first_name or 'Friend',
            'last_name': user.last_name or '',
            'email': user.email,
            'timezone': profile.timezone if profile else 'UTC',
            'preferred_language': 'en',  # Will be enhanced with actual language detection
            'notifications_enabled': profile.notifications_enabled if profile else True,
            'privacy_mode': profile.privacy_mode if profile else False,
            'theme_preference': profile.theme_preference if profile else 'default',
            'daily_reminder_enabled': profile.daily_reminder_enabled if profile else True,
            'daily_reminder_time': profile.daily_reminder_time if profile else '20:00',
            'account_age_days': (datetime.utcnow() - user.created_at).days,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
    
    async def _analyze_mood_patterns(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Analyze recent mood patterns and trends"""
        
        # Get mood entries from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id,
            MoodEntry.created_at >= thirty_days_ago
        ).order_by(desc(MoodEntry.created_at)).all()
        
        if not mood_entries:
            return self._get_default_mood_patterns()
        
        # Extract mood scores
        mood_scores = [entry.mood_score for entry in mood_entries]
        recent_scores = mood_scores[:7]  # Last 7 entries
        
        # Calculate statistics
        avg_mood = statistics.mean(mood_scores)
        recent_avg = statistics.mean(recent_scores) if recent_scores else avg_mood
        
        # Determine trend
        if len(recent_scores) >= 3:
            if recent_avg > avg_mood + 0.5:
                trend = 'improving'
            elif recent_avg < avg_mood - 0.5:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        # Calculate mood stability
        mood_variance = statistics.variance(mood_scores) if len(mood_scores) > 1 else 0
        stability = 'stable' if mood_variance < 1.0 else 'variable'
        
        # Extract common triggers and contexts
        all_tags = []
        energy_levels = []
        stress_levels = []
        
        for entry in mood_entries:
            if entry.context_tags:
                all_tags.extend(entry.context_tags)
            if entry.energy_level:
                energy_levels.append(entry.energy_level)
            if entry.stress_level:
                stress_levels.append(entry.stress_level)
        
        # Find most common triggers
        common_triggers = [tag for tag, count in Counter(all_tags).most_common(5)] if all_tags else []
        
        return {
            'trend': trend,
            'stability': stability,
            'average_mood': round(avg_mood, 2),
            'recent_average': round(recent_avg, 2),
            'mood_variance': round(mood_variance, 2),
            'total_entries': len(mood_entries),
            'recent_entries': len(recent_scores),
            'common_triggers': common_triggers,
            'average_energy': round(statistics.mean(energy_levels), 2) if energy_levels else 3.0,
            'average_stress': round(statistics.mean(stress_levels), 2) if stress_levels else 3.0,
            'last_mood_score': mood_scores[0] if mood_scores else 3,
            'last_entry_date': mood_entries[0].created_at.isoformat() if mood_entries else None
        }
    
    async def _analyze_writing_style(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Analyze user's writing style from journal entries"""
        
        # Get recent journal entries
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        journal_entries = db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.created_at >= thirty_days_ago
        ).order_by(desc(JournalEntry.created_at)).limit(20).all()
        
        if not journal_entries:
            return self._get_default_writing_style()
        
        # Analyze writing patterns
        total_words = sum(entry.word_count or 0 for entry in journal_entries)
        avg_word_count = total_words / len(journal_entries) if journal_entries else 0
        
        # Analyze sentiment patterns
        sentiment_scores = [entry.sentiment_score for entry in journal_entries if entry.sentiment_score is not None]
        avg_sentiment = statistics.mean(sentiment_scores) if sentiment_scores else 0.0
        
        # Extract common themes
        all_themes = []
        for entry in journal_entries:
            if entry.themes:
                all_themes.extend(entry.themes)
        
        common_themes = [theme for theme, count in Counter(all_themes).most_common(5)] if all_themes else []
        
        # Analyze mood impact
        mood_improvements = []
        for entry in journal_entries:
            if entry.mood_before and entry.mood_after:
                improvement = entry.mood_after - entry.mood_before
                mood_improvements.append(improvement)
        
        avg_mood_improvement = statistics.mean(mood_improvements) if mood_improvements else 0.0
        
        return {
            'total_entries': len(journal_entries),
            'avg_word_count': round(avg_word_count, 0),
            'avg_sentiment': round(avg_sentiment, 2),
            'common_themes': common_themes,
            'writing_frequency': len(journal_entries),  # entries in last 30 days
            'avg_mood_improvement': round(avg_mood_improvement, 2),
            'longest_entry': max((entry.word_count or 0) for entry in journal_entries),
            'shortest_entry': min((entry.word_count or 0) for entry in journal_entries),
            'private_entries_ratio': sum(1 for entry in journal_entries if entry.is_private) / len(journal_entries),
            'last_entry_date': journal_entries[0].created_at.isoformat() if journal_entries else None
        }
    
    async def _analyze_community_behavior(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Analyze user's community engagement patterns"""
        
        # Get forum memberships
        memberships = db.query(ForumMembership).filter(
            ForumMembership.user_id == user_id,
            ForumMembership.is_active == True
        ).all()
        
        # Get user's forum threads and replies
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        threads = db.query(ForumThread).filter(
            ForumThread.author_id == user_id,
            ForumThread.created_at >= thirty_days_ago
        ).all()
        
        replies = db.query(ThreadReply).filter(
            ThreadReply.author_id == user_id,
            ThreadReply.created_at >= thirty_days_ago
        ).all()
        
        if not memberships and not threads and not replies:
            return self._get_default_community_behavior()
        
        # Calculate engagement metrics
        total_posts = len(threads) + len(replies)
        forums_joined = len(memberships)
        
        # Analyze posting patterns
        thread_lengths = [len(thread.content) for thread in threads]
        reply_lengths = [len(reply.content) for reply in replies]
        
        avg_thread_length = statistics.mean(thread_lengths) if thread_lengths else 0
        avg_reply_length = statistics.mean(reply_lengths) if reply_lengths else 0
        
        # Determine engagement level
        if total_posts >= 10:
            engagement_level = 'high'
        elif total_posts >= 3:
            engagement_level = 'moderate'
        elif total_posts >= 1:
            engagement_level = 'low'
        else:
            engagement_level = 'minimal'
        
        return {
            'forums_joined': forums_joined,
            'threads_created': len(threads),
            'replies_posted': len(replies),
            'total_posts': total_posts,
            'engagement_level': engagement_level,
            'avg_thread_length': round(avg_thread_length, 0),
            'avg_reply_length': round(avg_reply_length, 0),
            'posting_frequency': total_posts,  # posts in last 30 days
            'most_active_forum': self._get_most_active_forum(user_id, db),
            'last_activity_date': max(
                [thread.created_at for thread in threads] + 
                [reply.created_at for reply in replies]
            ).isoformat() if (threads or replies) else None
        }
    
    async def _get_conversation_insights(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get insights from recent chatbot conversations"""
        
        # Get recent chat sessions
        recent_sessions = db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(desc(ChatSession.updated_at)).limit(5).all()
        
        if not recent_sessions:
            return self._get_default_conversation_history()
        
        # Get recent messages
        all_messages = []
        for session in recent_sessions:
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).order_by(desc(ChatMessage.created_at)).limit(10).all()
            all_messages.extend(messages)
        
        # Analyze conversation patterns
        user_messages = [msg for msg in all_messages if msg.sender == 'user']
        ai_messages = [msg for msg in all_messages if msg.sender == 'assistant']
        
        # Extract topics from user messages (simplified)
        user_content = ' '.join([msg.content for msg in user_messages])
        topics = self._extract_conversation_topics(user_content)
        
        # Calculate session metrics
        avg_session_length = len(all_messages) / len(recent_sessions) if recent_sessions else 0
        
        return {
            'total_sessions': len(recent_sessions),
            'total_messages': len(all_messages),
            'user_messages': len(user_messages),
            'ai_messages': len(ai_messages),
            'avg_session_length': round(avg_session_length, 1),
            'recent_topics': topics,
            'last_conversation': recent_sessions[0].updated_at.isoformat() if recent_sessions else None,
            'conversation_frequency': len(recent_sessions),  # sessions in recent time
            'preferred_session_type': self._get_preferred_session_type(recent_sessions)
        }
    
    async def _assess_current_state(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Assess user's current mental health state"""
        
        # Get most recent data points
        latest_mood = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(desc(MoodEntry.created_at)).first()
        
        latest_journal = db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id
        ).order_by(desc(JournalEntry.created_at)).first()
        
        latest_chat = db.query(ChatMessage).join(ChatSession).filter(
            ChatSession.user_id == user_id,
            ChatMessage.sender == 'user'
        ).order_by(desc(ChatMessage.created_at)).first()
        
        # Assess current state
        current_mood_score = latest_mood.mood_score if latest_mood else 3
        
        # Determine overall state
        if current_mood_score >= 4:
            overall_state = 'positive'
        elif current_mood_score >= 3:
            overall_state = 'neutral'
        elif current_mood_score >= 2:
            overall_state = 'concerning'
        else:
            overall_state = 'high_risk'
        
        # Check recent activity
        now = datetime.utcnow()
        days_since_mood = (now - latest_mood.created_at).days if latest_mood else None
        days_since_journal = (now - latest_journal.created_at).days if latest_journal else None
        days_since_chat = (now - latest_chat.created_at).days if latest_chat else None
        
        return {
            'current_mood_score': current_mood_score,
            'overall_state': overall_state,
            'days_since_mood_entry': days_since_mood,
            'days_since_journal_entry': days_since_journal,
            'days_since_chat': days_since_chat,
            'latest_mood_date': latest_mood.created_at.isoformat() if latest_mood else None,
            'latest_journal_date': latest_journal.created_at.isoformat() if latest_journal else None,
            'latest_chat_date': latest_chat.created_at.isoformat() if latest_chat else None,
            'engagement_recency': self._calculate_engagement_recency(days_since_mood, days_since_journal, days_since_chat)
        }
    
    def _generate_communication_preferences(
        self, 
        profile: Dict[str, Any], 
        mood_patterns: Dict[str, Any],
        community_behavior: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate communication preferences based on user data"""
        
        # Determine preferred communication style
        avg_mood = mood_patterns.get('average_mood', 3.0)
        engagement_level = community_behavior.get('engagement_level', 'minimal')
        
        # Base preferences
        if avg_mood >= 4.0:
            empathy_level = 0.7  # Less empathy needed for positive users
            encouragement_style = 'motivational'
        elif avg_mood >= 3.0:
            empathy_level = 0.8  # Balanced empathy
            encouragement_style = 'supportive'
        else:
            empathy_level = 0.9  # High empathy for struggling users
            encouragement_style = 'gentle'
        
        # Adjust based on community engagement
        if engagement_level == 'high':
            directness_level = 0.7  # Can handle more direct communication
            response_length = 'medium'
        elif engagement_level == 'moderate':
            directness_level = 0.6
            response_length = 'medium'
        else:
            directness_level = 0.4  # Gentler approach for less engaged users
            response_length = 'short'
        
        return {
            'empathy_level': empathy_level,
            'directness_level': directness_level,
            'encouragement_style': encouragement_style,
            'response_length': response_length,
            'communication_style': 'empathetic',  # Default style
            'humor_usage': 0.3,  # Conservative humor usage
            'question_frequency': 0.5,  # Balanced questioning
            'crisis_sensitivity': 'high' if avg_mood < 2.5 else 'medium'
        }
    
    # Helper methods for extracting insights
    def _extract_conversation_topics(self, content: str) -> List[str]:
        """Extract topics from conversation content"""
        topic_keywords = {
            'anxiety': ['anxious', 'worried', 'nervous', 'panic', 'stress'],
            'depression': ['sad', 'depressed', 'down', 'hopeless', 'empty'],
            'relationships': ['partner', 'friend', 'family', 'relationship', 'social'],
            'work': ['job', 'work', 'career', 'boss', 'colleague', 'workplace'],
            'self_care': ['sleep', 'exercise', 'meditation', 'self-care', 'routine'],
            'emotions': ['feeling', 'emotion', 'mood', 'feelings', 'emotional']
        }
        
        content_lower = content.lower()
        detected_topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics[:5]  # Return top 5 topics
    
    def _get_most_active_forum(self, user_id: str, db: Session) -> Optional[str]:
        """Get the forum where user is most active"""
        # This would involve more complex querying - simplified for now
        membership = db.query(ForumMembership).filter(
            ForumMembership.user_id == user_id
        ).first()
        
        if membership:
            forum = db.query(CommunityForum).filter(
                CommunityForum.id == membership.forum_id
            ).first()
            return forum.name if forum else None
        
        return None
    
    def _get_preferred_session_type(self, sessions: List[ChatSession]) -> str:
        """Determine preferred chat session type"""
        if not sessions:
            return 'general'
        
        session_types = [session.session_type for session in sessions]
        from collections import Counter
        most_common = Counter(session_types).most_common(1)
        return most_common[0][0] if most_common else 'general'
    
    def _calculate_engagement_recency(self, days_mood: Optional[int], days_journal: Optional[int], days_chat: Optional[int]) -> str:
        """Calculate overall engagement recency"""
        recent_days = [d for d in [days_mood, days_journal, days_chat] if d is not None]
        
        if not recent_days:
            return 'no_recent_activity'
        
        min_days = min(recent_days)
        
        if min_days <= 1:
            return 'very_recent'
        elif min_days <= 3:
            return 'recent'
        elif min_days <= 7:
            return 'somewhat_recent'
        else:
            return 'not_recent'
    
    # Cache management methods
    def _get_cached_context(self, user_id: str) -> Optional[UserContext]:
        """Get cached context if valid"""
        if user_id in self.context_cache:
            cached_data, timestamp = self.context_cache[user_id]
            if datetime.utcnow() - timestamp < self.cache_duration:
                return cached_data
        return None
    
    def _cache_context(self, user_id: str, context: UserContext):
        """Cache user context"""
        self.context_cache[user_id] = (context, datetime.utcnow())
    
    # Default/fallback methods
    def _get_default_profile(self) -> Dict[str, Any]:
        return {
            'first_name': 'Friend',
            'timezone': 'UTC',
            'preferred_language': 'en',
            'notifications_enabled': True,
            'privacy_mode': False
        }
    
    def _get_default_mood_patterns(self) -> Dict[str, Any]:
        return {
            'trend': 'unknown',
            'stability': 'unknown',
            'average_mood': 3.0,
            'total_entries': 0,
            'common_triggers': []
        }
    
    def _get_default_writing_style(self) -> Dict[str, Any]:
        return {
            'total_entries': 0,
            'avg_word_count': 0,
            'common_themes': [],
            'writing_frequency': 0
        }
    
    def _get_default_community_behavior(self) -> Dict[str, Any]:
        return {
            'forums_joined': 0,
            'engagement_level': 'minimal',
            'total_posts': 0
        }
    
    def _get_default_conversation_history(self) -> Dict[str, Any]:
        return {
            'total_sessions': 0,
            'recent_topics': [],
            'conversation_frequency': 0
        }
    
    def _get_default_current_state(self) -> Dict[str, Any]:
        return {
            'current_mood_score': 3,
            'overall_state': 'neutral',
            'engagement_recency': 'unknown'
        }
    
    def _get_fallback_context(self, user_id: str) -> UserContext:
        """Get minimal fallback context in case of errors"""
        return UserContext(
            user_id=user_id,
            profile=self._get_default_profile(),
            mood_patterns=self._get_default_mood_patterns(),
            writing_style=self._get_default_writing_style(),
            community_behavior=self._get_default_community_behavior(),
            conversation_history=self._get_default_conversation_history(),
            current_state=self._get_default_current_state(),
            communication_preferences={
                'empathy_level': 0.8,
                'directness_level': 0.6,
                'encouragement_style': 'supportive',
                'response_length': 'medium'
            },
            last_updated=datetime.utcnow()
        )
