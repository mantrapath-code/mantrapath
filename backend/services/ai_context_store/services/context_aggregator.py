"""
Context Aggregator Service
Aggregates user context from multiple event sources and maintains unified user profiles
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict

import sys
import os

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
service_root = os.path.dirname(current_dir)
backend_root = os.path.dirname(os.path.dirname(service_root))

sys.path.insert(0, backend_root)
sys.path.insert(0, service_root)

from shared.redis_client import redis_client
from models.context_models import (
    UserContext, ContextEntry, ContextType, ContextPriority,
    MoodContext, CommunityContext, VoiceContext,
    TranslationContext, ContentContext, NotificationContext,
    ContextAggregator
)

# Import data collectors
from data_collectors.mood_data_collector import MoodDataCollector
from data_collectors.journal_data_collector import JournalDataCollector  
from data_collectors.community_data_collector import CommunityDataCollector

logger = logging.getLogger(__name__)

class ContextAggregatorService:
    """
    Service for aggregating and managing user context from multiple sources
    """
    
    def __init__(self):
        self.redis_client = redis_client
        self.context_cache: Dict[str, UserContext] = {}
        self.aggregation_rules = ContextAggregator()
        self.is_running = False
        
        # Context entry buffers for batch processing
        self.context_buffers: Dict[str, List[ContextEntry]] = defaultdict(list)
        self.buffer_flush_interval = 30  # seconds
        
        # Initialize data collectors
        self.mood_collector = MoodDataCollector()
        self.journal_collector = JournalDataCollector()
        self.community_collector = CommunityDataCollector()
        
        logger.info("🔄 ContextAggregatorService initialized with data collectors")
    
    async def initialize(self):
        """Initialize the service"""
        try:
            # Test Redis connection using executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self.redis_client.ping() if self.redis_client else None)
            logger.info("✅ Context aggregator connected to Redis")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed, using in-memory cache: {e}")
            self.redis_client = None
    
    async def add_context_entry(self, context_entry: ContextEntry) -> bool:
        """
        Add a new context entry for a user
        """
        try:
            user_id = context_entry.user_id
            
            # Add to buffer for batch processing
            self.context_buffers[user_id].append(context_entry)
            
            # If high priority, process immediately
            if context_entry.priority in [ContextPriority.HIGH, ContextPriority.CRITICAL]:
                await self._process_context_entries(user_id)
            
            # Store context entry
            await self._store_context_entry(context_entry)
            
            logger.debug(f"📝 Added context entry for user {user_id}: {context_entry.context_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding context entry: {e}")
            return False
    
    async def get_user_context(self, user_id: str, include_history: bool = False) -> Optional[UserContext]:
        """
        Get comprehensive user context
        """
        try:
            # Try cache first
            if user_id in self.context_cache:
                context = self.context_cache[user_id]
                
                # Check if context is recent (within 5 minutes)
                if context.last_updated and (
                    datetime.now(timezone.utc) - context.last_updated
                ).total_seconds() < 300:
                    return context
            
            # Load from Redis
            context = await self._load_user_context(user_id)
            if context:
                self.context_cache[user_id] = context
                return context
            
            # Create new context if not found
            return await self._create_user_context(user_id)
            
        except Exception as e:
            logger.error(f"❌ Error getting user context: {e}")
            return None

    async def collect_comprehensive_user_data(self, user_id: str, jwt_token: str) -> Optional[UserContext]:
        """
        Collect comprehensive user data from all services and create/update context
        
        Args:
            user_id: User ID to collect data for
            jwt_token: Authentication token for service calls
            
        Returns:
            Updated UserContext with fresh data from all services
        """
        try:
            logger.info(f"🔍 Collecting comprehensive data for user {user_id}")
            
            # Collect data from all sources in parallel
            mood_data_task = self.mood_collector.collect_user_mood_data(user_id, jwt_token)
            journal_data_task = self.journal_collector.collect_user_journal_data(user_id, jwt_token)
            community_data_task = self.community_collector.collect_user_community_data(user_id, jwt_token)
            
            # Wait for all collections to complete
            mood_data, journal_data, community_data = await asyncio.gather(
                mood_data_task,
                journal_data_task, 
                community_data_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(mood_data, Exception):
                logger.warning(f"Mood data collection failed: {mood_data}")
                mood_data = {}
            if isinstance(journal_data, Exception):
                logger.warning(f"Journal data collection failed: {journal_data}")
                journal_data = {}
            if isinstance(community_data, Exception):
                logger.warning(f"Community data collection failed: {community_data}")
                community_data = {}
            
            # Create or update user context
            context = await self.get_user_context(user_id) or await self._create_user_context(user_id)
            
            # Update context with collected data
            if mood_data and isinstance(mood_data, dict):
                await self.update_user_context(user_id, ContextType.MOOD, mood_data)
                
            if journal_data and isinstance(journal_data, dict):
                await self.update_user_context(user_id, ContextType.CONTENT, journal_data)
                
            if community_data and isinstance(community_data, dict):
                await self.update_user_context(user_id, ContextType.COMMUNITY, community_data)
            
            # Get the updated context or create if it doesn't exist
            updated_context = await self.get_user_context(user_id)
            if not updated_context:
                logger.warning(f"⚠️ No context found after updates, creating new context for user {user_id}")
                updated_context = await self._create_user_context(user_id)
                self.context_cache[user_id] = updated_context
            
            # Always update behavioral patterns and preferences with collected data
            all_data = {
                "mood_data": mood_data if isinstance(mood_data, dict) else {},
                "journal_data": journal_data if isinstance(journal_data, dict) else {},
                "community_data": community_data if isinstance(community_data, dict) else {}
            }
            
            logger.info(f"🔄 Generating behavioral patterns and preferences for user {user_id}")
            updated_context.behavioral_patterns = self._generate_behavioral_patterns(all_data)
            updated_context.preferences = self._generate_user_preferences(all_data)
            
            # Update context history
            self._update_context_history(updated_context, "comprehensive_data_collection", all_data)
            
            # Cache the enhanced context
            self.context_cache[user_id] = updated_context
            
            logger.info(f"🎯 Enhanced user context with behavioral patterns and preferences for user {user_id}")
            logger.info(f"📊 Behavioral patterns keys: {list(updated_context.behavioral_patterns.keys())}")
            logger.info(f"📊 Preferences keys: {list(updated_context.preferences.keys())}")
            logger.info(f"📊 Context history entries: {len(updated_context.context_history)}")
            
            logger.info(f"✅ Comprehensive data collection completed for user {user_id}")
            return updated_context
            
        except Exception as e:
            logger.error(f"❌ Error collecting comprehensive user data: {e}")
            return None
    
    async def update_user_context(self, user_id: str, context_type: ContextType, data: Dict[str, Any]) -> bool:
        """
        Update specific context type for a user
        """
        try:
            user_context = await self.get_user_context(user_id)
            if not user_context:
                user_context = await self._create_user_context(user_id)
            
            # Update specific context based on type
            updated = False
            if context_type == ContextType.MOOD:
                user_context.mood_context = self._update_mood_context(
                    user_context.mood_context, data
                )
                updated = True
            elif context_type == ContextType.COMMUNITY:
                user_context.community_context = self._update_community_context(
                    user_context.community_context, data
                )
                updated = True
            elif context_type == ContextType.VOICE:
                user_context.voice_context = self._update_voice_context(
                    user_context.voice_context, data
                )
                updated = True
            elif context_type == ContextType.TRANSLATION:
                user_context.translation_context = self._update_translation_context(
                    user_context.translation_context, data
                )
                updated = True
            elif context_type == ContextType.CONTENT:
                user_context.content_context = self._update_content_context(
                    user_context.content_context, data
                )
                updated = True
            elif context_type == ContextType.NOTIFICATION:
                user_context.notification_context = self._update_notification_context(
                    user_context.notification_context, data
                )
                updated = True
            
            if updated:
                user_context.last_updated = datetime.now(timezone.utc)
                user_context.last_activity = datetime.now(timezone.utc)
                
                # Update aggregated insights
                await self._update_aggregated_insights(user_context)
                
                # Save to cache and storage
                self.context_cache[user_id] = user_context
                await self._save_user_context(user_context)
                
                logger.debug(f"📊 Updated {context_type} context for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error updating user context: {e}")
            return False
    
    async def start_periodic_aggregation(self):
        """Start periodic context aggregation tasks"""
        self.is_running = True
        logger.info("🔄 Starting periodic context aggregation")
        
        # Start buffer processing task
        asyncio.create_task(self._periodic_buffer_processing())
        
        # Start context cleanup task
        asyncio.create_task(self._periodic_context_cleanup())
        
        # Start context health monitoring
        asyncio.create_task(self._periodic_health_monitoring())
    
    async def stop(self):
        """Stop the service"""
        self.is_running = False
        logger.info("🛑 Stopping context aggregator service")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        return {
            "cached_contexts": len(self.context_cache),
            "buffer_sizes": {
                user_id: len(entries) 
                for user_id, entries in self.context_buffers.items()
            },
            "total_buffered_entries": sum(len(entries) for entries in self.context_buffers.values()),
            "redis_connected": self.redis_client is not None
        }
    
    # Private methods
    
    async def _process_context_entries(self, user_id: str):
        """Process buffered context entries for a user"""
        if user_id not in self.context_buffers or not self.context_buffers[user_id]:
            return
        
        entries = self.context_buffers[user_id]
        self.context_buffers[user_id] = []
        
        for entry in entries:
            await self.update_user_context(
                user_id, 
                entry.context_type, 
                entry.processed_data or entry.raw_data
            )
    
    async def _store_context_entry(self, entry: ContextEntry):
        """Store individual context entry"""
        if self.redis_client:
            try:
                key = f"context_entry:{entry.user_id}:{entry.id}"
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: self.redis_client.setex(
                        key, 
                        entry.ttl or 86400,  # 24 hours default
                        json.dumps(entry.model_dump(), default=str)
                    )
                )
            except Exception as e:
                logger.error(f"❌ Error storing context entry to Redis: {e}")
    
    async def _load_user_context(self, user_id: str) -> Optional[UserContext]:
        """Load user context from storage"""
        if self.redis_client:
            try:
                key = f"user_context:{user_id}"
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: self.redis_client.get(key))
                if data:
                    return UserContext.model_validate_json(data)
            except Exception as e:
                logger.error(f"❌ Error loading user context from Redis: {e}")
        
        return None
    
    async def _save_user_context(self, context: UserContext):
        """Save user context to storage"""
        if self.redis_client:
            try:
                key = f"user_context:{context.user_id}"
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: self.redis_client.setex(
                        key,
                        86400,  # 24 hours
                        context.model_dump_json()
                    )
                )
            except Exception as e:
                logger.error(f"❌ Error saving user context to Redis: {e}")
    
    async def _create_user_context(self, user_id: str) -> UserContext:
        """Create new user context with populated fields"""
        return UserContext(
            user_id=user_id,
            last_updated=datetime.now(timezone.utc),
            behavioral_patterns=self._generate_behavioral_patterns({}),
            preferences=self._generate_user_preferences({}),
            context_history=[],
            last_activity=datetime.now(timezone.utc),
            activity_score=0.0,
            context_completeness=0.0
        )
    
    def _generate_behavioral_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate behavioral patterns from real user data"""
        patterns = {}
        
        # Extract mood patterns from real mood data
        mood_data = data.get("mood_data", {})
        if mood_data:
            mood_patterns = {}
            
            # Real mood statistics
            if "recent_average_mood" in mood_data:
                avg_mood = mood_data["recent_average_mood"]
                if avg_mood >= 7:
                    mood_patterns["typical_mood_range"] = "positive"
                elif avg_mood >= 5:
                    mood_patterns["typical_mood_range"] = "moderate"
                else:
                    mood_patterns["typical_mood_range"] = "low"
            
            # Real mood volatility from variance
            if "mood_patterns" in mood_data and "mood_variance" in mood_data["mood_patterns"]:
                variance = mood_data["mood_patterns"]["mood_variance"]
                if variance <= 1:
                    mood_patterns["mood_volatility"] = "stable"
                elif variance <= 2:
                    mood_patterns["mood_volatility"] = "moderate"
                else:
                    mood_patterns["mood_volatility"] = "high"
            
            # Extract mood trend
            if "mood_trend" in mood_data:
                mood_patterns["trend"] = mood_data["mood_trend"]
            
            # Extract collection methods
            collection_methods = []
            if "voice_entries" in mood_data and mood_data["voice_entries"] > 0:
                collection_methods.append("voice")
            if "total_entries" in mood_data:
                manual_entries = mood_data["total_entries"] - mood_data.get("voice_entries", 0)
                if manual_entries > 0:
                    collection_methods.append("manual")
            mood_patterns["preferred_input_methods"] = collection_methods
            
            # Extract frequency pattern
            if "total_entries" in mood_data and "days_tracked" in mood_data:
                frequency = mood_data["total_entries"] / max(mood_data["days_tracked"], 1)
                if frequency >= 2:
                    mood_patterns["tracking_frequency"] = "high"
                elif frequency >= 1:
                    mood_patterns["tracking_frequency"] = "daily"
                else:
                    mood_patterns["tracking_frequency"] = "irregular"
            
            patterns["mood_patterns"] = mood_patterns
        
        # Activity patterns from engagement data
        activity_patterns = {}
        total_entries = mood_data.get("total_entries", 0)
        if total_entries > 0:
            if total_entries >= 10:
                activity_patterns["engagement_level"] = "high"
            elif total_entries >= 5:
                activity_patterns["engagement_level"] = "moderate"
            else:
                activity_patterns["engagement_level"] = "low"
        
        # Days tracked pattern
        days_tracked = mood_data.get("days_tracked", 0)
        if days_tracked >= 7:
            activity_patterns["consistency"] = "excellent"
        elif days_tracked >= 3:
            activity_patterns["consistency"] = "good"
        elif days_tracked >= 1:
            activity_patterns["consistency"] = "starting"
        else:
            activity_patterns["consistency"] = "new_user"
        
        patterns["activity_patterns"] = activity_patterns
        
        # Communication patterns based on usage
        communication_patterns = {}
        
        # Preferred interaction style based on data richness
        latest_entry = mood_data.get("latest_entry", {})
        if latest_entry.get("notes"):
            communication_patterns["detail_preference"] = "detailed"
        else:
            communication_patterns["detail_preference"] = "concise"
        
        # Response to follow-ups
        if "follow_up_responses" in latest_entry:
            communication_patterns["engagement_with_suggestions"] = "responsive"
        else:
            communication_patterns["engagement_with_suggestions"] = "minimal"
        
        patterns["communication_patterns"] = communication_patterns
        
        return patterns
    
    def _generate_user_preferences(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate user preferences from real collected data"""
        preferences = {}
        
        mood_data = data.get("mood_data", {})
        
        # Language preferences (default to English for now)
        preferences["language"] = "en"
        
        # Communication style based on user behavior
        communication_style = "empathetic"  # Default
        latest_entry = mood_data.get("latest_entry", {})
        if latest_entry.get("notes"):
            communication_style = "detailed"
        preferences["communication_style"] = communication_style
        
        # Notification settings based on engagement patterns
        notification_settings = {}
        total_entries = mood_data.get("total_entries", 0)
        if total_entries >= 5:
            notification_settings["mood_reminders"] = True
            notification_settings["wellness_tips"] = True
        else:
            notification_settings["mood_reminders"] = True
            notification_settings["wellness_tips"] = False
        notification_settings["crisis_alerts"] = True  # Always enabled for safety
        preferences["notification_settings"] = notification_settings
        
        # Content preferences based on usage patterns
        content_preferences = {}
        
        # Determine preferred interaction methods
        voice_entries = mood_data.get("voice_entries", 0)
        total_entries = mood_data.get("total_entries", 0)
        if voice_entries > 0:
            content_preferences["voice_support"] = True
        else:
            content_preferences["voice_support"] = False
        
        # Mood tracking preferences
        avg_mood = mood_data.get("recent_average_mood", 5.0)
        if avg_mood >= 7:
            content_preferences["focus_area"] = "maintenance"
        elif avg_mood >= 5:
            content_preferences["focus_area"] = "improvement"
        else:
            content_preferences["focus_area"] = "support"
        
        # Stress management preferences
        avg_stress = mood_data.get("recent_average_stress", 5.0)
        if avg_stress >= 7:
            content_preferences["stress_support"] = "high_priority"
        elif avg_stress >= 5:
            content_preferences["stress_support"] = "moderate"
        else:
            content_preferences["stress_support"] = "low"
        
        preferences["content_preferences"] = content_preferences
        
        # Support preferences based on engagement
        support_preferences = {}
        
        # Intervention level based on consistency
        days_tracked = mood_data.get("days_tracked", 0)
        if days_tracked >= 7:
            support_preferences["intervention_level"] = "proactive"
        elif days_tracked >= 3:
            support_preferences["intervention_level"] = "moderate"
        else:
            support_preferences["intervention_level"] = "gentle"
        
        # Professional referral readiness
        if avg_mood < 4 or avg_stress > 8:
            support_preferences["professional_referral"] = "immediate"
        elif avg_mood < 5 or avg_stress > 6:
            support_preferences["professional_referral"] = "when_suggested"
        else:
            support_preferences["professional_referral"] = "when_needed"
        
        # Peer support based on engagement
        if total_entries >= 10:
            support_preferences["peer_support"] = True
            support_preferences["community_engagement"] = "active"
        elif total_entries >= 5:
            support_preferences["peer_support"] = True
            support_preferences["community_engagement"] = "moderate"
        else:
            support_preferences["peer_support"] = False
            support_preferences["community_engagement"] = "observer"
        
        preferences["support_preferences"] = support_preferences
        
        return preferences
    
    def _update_context_history(self, context: UserContext, action: str, data: Dict[str, Any]) -> None:
        """Update context history with new activity"""
        history_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "data_summary": {
                "mood_updated": "mood_data" in data,
                "community_updated": "community_data" in data,
                "journal_updated": "journal_data" in data
            }
        }
        
        # Keep only last 10 history entries
        if len(context.context_history) >= 10:
            context.context_history.pop(0)
        
        context.context_history.append(history_entry)
    
    def _update_mood_context(self, current: Optional[MoodContext], data: Dict[str, Any]) -> MoodContext:
        """Update mood context with new data"""
        logger.info(f"🔍 _update_mood_context received data keys: {list(data.keys())}")
        logger.info(f"🔍 Full data structure: {data}")
        
        if "mood_patterns" in data:
            logger.info(f"🔍 mood_patterns keys: {list(data['mood_patterns'].keys())}")
            if "recent_scores" in data["mood_patterns"]:
                logger.info(f"🔍 recent_scores: {data['mood_patterns']['recent_scores']}")
        
        mood_score = data.get("mood_score", 5.0)
        energy_level = data.get("energy_level", 5.0)
        
        # Extract recent moods from analytics data or mood_patterns
        recent_moods = []
        logger.info(f"🔍 Checking mood_patterns in data: {'mood_patterns' in data}")
        logger.info(f"🔍 mood_patterns type: {type(data.get('mood_patterns', 'NOT_FOUND'))}")
        
        if "mood_patterns" in data and isinstance(data["mood_patterns"], dict):
            recent_moods = data["mood_patterns"].get("recent_scores", [])
            logger.info(f"🔍 Found recent_moods from mood_patterns: {recent_moods}")
        elif "analytics" in data and isinstance(data["analytics"], dict):
            mood_patterns = data["analytics"].get("mood_patterns", {})
            if "recent_scores" in mood_patterns:
                recent_moods = mood_patterns["recent_scores"]
                logger.info(f"🔍 Found recent_moods from analytics: {recent_moods}")
        else:
            logger.info(f"🔍 No recent_moods found, recent_moods will be empty")
        
        logger.info(f"🔍 Final recent_moods before creating MoodContext: {recent_moods}")
        
        result = MoodContext(
            mood_score=mood_score,
            energy_level=energy_level,
            stress_level=data.get("stress_level"),
            sleep_quality=data.get("sleep_quality"),
            journal_sentiment=data.get("sentiment_score"),
            mood_trend=self._calculate_mood_trend(current, mood_score),
            recent_moods=recent_moods,
            timestamp=datetime.now(timezone.utc)
        )
        
        logger.info(f"🔍 Created MoodContext with recent_moods: {result.recent_moods}")
        return result
    
    def _update_community_context(self, current: Optional[CommunityContext], data: Dict[str, Any]) -> CommunityContext:
        """Update community context with new data"""
        if current:
            posts_created = current.posts_created + data.get("posts_increment", 0)
            interactions = current.interactions + data.get("interactions_increment", 0)
            challenge_participation = list(set(
                current.challenge_participation + data.get("challenges", [])
            ))
        else:
            posts_created = data.get("posts_created", 0)
            interactions = data.get("interactions", 0)
            challenge_participation = data.get("challenges", [])
        
        return CommunityContext(
            engagement_level=data.get("engagement_level", "moderate"),
            challenge_participation=challenge_participation,
            posts_created=posts_created,
            interactions=interactions,
            social_score=data.get("social_score", 0.5),
            preferred_topics=data.get("topics", []),
            timestamp=datetime.now(timezone.utc)
        )
    
    def _update_voice_context(self, current: Optional[VoiceContext], data: Dict[str, Any]) -> VoiceContext:
        """Update voice context with new data"""
        if current:
            interaction_frequency = current.interaction_frequency + 1
            preferred_commands = list(set(
                current.preferred_voice_commands + data.get("commands", [])
            ))
            intent_patterns = list(set(
                current.intent_patterns + data.get("intents", [])
            ))
        else:
            interaction_frequency = 1
            preferred_commands = data.get("commands", [])
            intent_patterns = data.get("intents", [])
        
        return VoiceContext(
            interaction_frequency=interaction_frequency,
            preferred_voice_commands=preferred_commands,
            speech_patterns=data.get("speech_patterns", {}),
            intent_patterns=intent_patterns,
            voice_sentiment=data.get("sentiment"),
            timestamp=datetime.now(timezone.utc)
        )
    
    def _update_translation_context(self, current: Optional[TranslationContext], data: Dict[str, Any]) -> TranslationContext:
        """Update translation context with new data"""
        if current:
            frequency = current.translation_frequency + 1
            source_langs = list(set(current.source_languages + data.get("source_languages", [])))
            target_langs = list(set(current.target_languages + data.get("target_languages", [])))
            content_types = list(set(current.content_types + data.get("content_types", [])))
        else:
            frequency = 1
            source_langs = data.get("source_languages", [])
            target_langs = data.get("target_languages", [])
            content_types = data.get("content_types", [])
        
        return TranslationContext(
            source_languages=source_langs,
            target_languages=target_langs,
            translation_frequency=frequency,
            content_types=content_types,
            cultural_preferences=data.get("cultural_preferences", {}),
            timestamp=datetime.now(timezone.utc)
        )
    
    def _update_content_context(self, current: Optional[ContentContext], data: Dict[str, Any]) -> ContentContext:
        """Update content context with new data"""
        if current:
            preferences = list(set(current.content_preferences + data.get("preferences", [])))
            content_types = list(set(current.content_types + data.get("content_types", [])))
            feedback = current.recommendation_feedback + data.get("feedback", [])
        else:
            preferences = data.get("preferences", [])
            content_types = data.get("content_types", [])
            feedback = data.get("feedback", [])
        
        return ContentContext(
            content_preferences=preferences,
            engagement_patterns=data.get("engagement_patterns", {}),
            recommendation_feedback=feedback,
            content_types=content_types,
            timestamp=datetime.now(timezone.utc)
        )
    
    def _update_notification_context(self, current: Optional[NotificationContext], data: Dict[str, Any]) -> NotificationContext:
        """Update notification context with new data"""
        if current:
            engagement_rates = {**current.engagement_rates, **data.get("engagement_rates", {})}
            optimal_timing = list(set(current.optimal_timing + data.get("optimal_timing", [])))
            notification_types = list(set(current.notification_types + data.get("types", [])))
        else:
            engagement_rates = data.get("engagement_rates", {})
            optimal_timing = data.get("optimal_timing", [])
            notification_types = data.get("types", [])
        
        return NotificationContext(
            delivery_preferences=data.get("delivery_preferences", {}),
            engagement_rates=engagement_rates,
            optimal_timing=optimal_timing,
            notification_types=notification_types,
            response_patterns=data.get("response_patterns", {}),
            timestamp=datetime.now(timezone.utc)
        )
    
    def _calculate_mood_trend(self, current: Optional[MoodContext], new_score: float) -> str:
        """Calculate mood trend"""
        if not current:
            return "stable"
        
        diff = new_score - current.mood_score
        if diff > 1:
            return "improving"
        elif diff < -1:
            return "declining"
        else:
            return "stable"
    
    async def _update_aggregated_insights(self, context: UserContext):
        """Update aggregated insights from all context components"""
        try:
            # Calculate context completeness
            completeness_score = 0.0
            total_components = 6
            
            if context.mood_context:
                completeness_score += 1
            if context.community_context:
                completeness_score += 1
            if context.voice_context:
                completeness_score += 1
            if context.translation_context:
                completeness_score += 1
            if context.content_context:
                completeness_score += 1
            if context.notification_context:
                completeness_score += 1
            
            context.context_completeness = completeness_score / total_components
            
            # Calculate activity score
            recent_contexts = 0
            now = datetime.now(timezone.utc)
            
            for ctx in [context.mood_context, context.community_context, 
                       context.voice_context, context.translation_context,
                       context.content_context, context.notification_context]:
                if ctx and (now - ctx.timestamp).total_seconds() < 3600:  # 1 hour
                    recent_contexts += 1
            
            context.activity_score = recent_contexts / total_components
            
            # Update user profile
            await self._build_user_profile(context)
            
        except Exception as e:
            logger.error(f"❌ Error updating aggregated insights: {e}")
    
    async def _build_user_profile(self, context: UserContext):
        """Build comprehensive user profile from all contexts"""
        profile = {}
        
        # Mood profile
        if context.mood_context:
            profile["mood"] = {
                "average_mood": context.mood_context.mood_score,
                "energy_level": context.mood_context.energy_level,
                "trend": context.mood_context.mood_trend
            }
        
        # Community profile
        if context.community_context:
            profile["community"] = {
                "engagement_level": context.community_context.engagement_level,
                "social_score": context.community_context.social_score,
                "active_challenges": len(context.community_context.challenge_participation)
            }
        
        # Communication preferences
        preferences = {}
        if context.voice_context:
            preferences["voice_enabled"] = context.voice_context.interaction_frequency > 0
        if context.translation_context:
            preferences["languages"] = {
                "source": context.translation_context.source_languages,
                "target": context.translation_context.target_languages
            }
        if context.notification_context:
            preferences["notifications"] = context.notification_context.delivery_preferences
        
        context.user_profile = profile
        context.preferences = preferences
    
    async def _periodic_buffer_processing(self):
        """Periodic task to process context buffers"""
        while self.is_running:
            try:
                for user_id in list(self.context_buffers.keys()):
                    if self.context_buffers[user_id]:
                        await self._process_context_entries(user_id)
                
                await asyncio.sleep(self.buffer_flush_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in periodic buffer processing: {e}")
                await asyncio.sleep(5)
    
    async def _periodic_context_cleanup(self):
        """Periodic task to clean up old context data"""
        while self.is_running:
            try:
                # Clean up cache entries older than 1 hour
                cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
                expired_users = []
                
                for user_id, context in self.context_cache.items():
                    if context.last_updated and context.last_updated < cutoff:
                        expired_users.append(user_id)
                
                for user_id in expired_users:
                    del self.context_cache[user_id]
                
                if expired_users:
                    logger.debug(f"🧹 Cleaned up {len(expired_users)} expired context cache entries")
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"❌ Error in periodic context cleanup: {e}")
                await asyncio.sleep(60)
    
    async def _periodic_health_monitoring(self):
        """Periodic task to monitor context health"""
        while self.is_running:
            try:
                # Monitor cache size
                cache_size = len(self.context_cache)
                buffer_size = sum(len(entries) for entries in self.context_buffers.values())
                
                logger.debug(f"📊 Context Health: {cache_size} cached contexts, {buffer_size} buffered entries")
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in periodic health monitoring: {e}")
                await asyncio.sleep(60)
