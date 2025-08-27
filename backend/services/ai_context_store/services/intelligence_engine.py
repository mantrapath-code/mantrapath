"""
Intelligence Engine Service
Analyzes user context and generates intelligent insights and recommendations
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
import json

import sys
import os

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
service_root = os.path.dirname(current_dir)
backend_root = os.path.dirname(os.path.dirname(service_root))

sys.path.insert(0, backend_root)
sys.path.insert(0, service_root)

from models.context_models import (
    UserContext, ContextEntry, IntelligenceInsight, 
    ContextType, ContextPriority
)

logger = logging.getLogger(__name__)

class IntelligenceEngine:
    """
    AI Intelligence Engine for generating insights from user context
    """
    
    def __init__(self):
        self.is_running = False
        self.insights_cache: Dict[str, List[IntelligenceInsight]] = {}
        self.processing_queue: List[Dict[str, Any]] = []
        
        # Intelligence processing metrics
        self.insights_generated = 0
        self.processing_errors = 0
        
        logger.info("🧠 IntelligenceEngine initialized")
    
    async def start_intelligence_processing(self):
        """Start intelligence processing tasks"""
        self.is_running = True
        logger.info("🚀 Starting intelligence processing")
        
        # Start background processing tasks
        asyncio.create_task(self._periodic_intelligence_processing())
        asyncio.create_task(self._periodic_insight_cleanup())
    
    async def stop(self):
        """Stop the intelligence engine"""
        self.is_running = False
        logger.info("🛑 Stopping intelligence engine")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get intelligence engine metrics"""
        return {
            "insights_generated": self.insights_generated,
            "processing_errors": self.processing_errors,
            "cached_insights": sum(len(insights) for insights in self.insights_cache.values()),
            "processing_queue_size": len(self.processing_queue),
            "is_running": self.is_running
        }
    
    async def process_ml_insight(self, user_id: str, insight_data: Dict[str, Any]):
        """Process ML insight from ML service"""
        try:
            # Add to processing queue
            self.processing_queue.append({
                "type": "ml_insight",
                "user_id": user_id,
                "data": insight_data,
                "timestamp": datetime.now(timezone.utc)
            })
            
            logger.debug(f"🧠 Queued ML insight processing for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error processing ML insight: {e}")
    
    async def process_high_priority_update(self, user_id: str, context_entry: ContextEntry):
        """Process high priority context update immediately"""
        try:
            # Add to processing queue with priority
            self.processing_queue.insert(0, {
                "type": "high_priority_context",
                "user_id": user_id,
                "context_entry": context_entry,
                "timestamp": datetime.now(timezone.utc)
            })
            
            logger.debug(f"🔥 Queued high priority context processing for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error processing high priority update: {e}")
    
    async def generate_user_insights(self, user_id: str, user_context: UserContext) -> List[IntelligenceInsight]:
        """Generate comprehensive insights for a user"""
        try:
            insights = []
            
            # Generate mood-based insights
            if user_context.mood_context:
                mood_insights = await self._generate_mood_insights(user_id, user_context)
                insights.extend(mood_insights)
            
            # Generate community engagement insights
            if user_context.community_context:
                community_insights = await self._generate_community_insights(user_id, user_context)
                insights.extend(community_insights)
            
            # Generate communication preference insights
            if user_context.voice_context or user_context.notification_context:
                communication_insights = await self._generate_communication_insights(user_id, user_context)
                insights.extend(communication_insights)
            
            # Generate cultural insights
            if user_context.translation_context:
                cultural_insights = await self._generate_cultural_insights(user_id, user_context)
                insights.extend(cultural_insights)
            
            # Generate content personalization insights
            if user_context.content_context:
                content_insights = await self._generate_content_insights(user_id, user_context)
                insights.extend(content_insights)
            
            # Generate cross-service intelligence
            cross_service_insights = await self._generate_cross_service_insights(user_id, user_context)
            insights.extend(cross_service_insights)
            
            # Cache insights
            self.insights_cache[user_id] = insights
            self.insights_generated += len(insights)
            
            logger.debug(f"🎯 Generated {len(insights)} insights for user {user_id}")
            return insights
            
        except Exception as e:
            self.processing_errors += 1
            logger.error(f"❌ Error generating user insights: {e}")
            return []
    
    async def get_user_insights(self, user_id: str) -> List[IntelligenceInsight]:
        """Get cached insights for a user"""
        return self.insights_cache.get(user_id, [])
    
    # Private insight generation methods
    
    async def _generate_mood_insights(self, user_id: str, context: UserContext) -> List[IntelligenceInsight]:
        """Generate mood-based insights"""
        insights = []
        mood_ctx = context.mood_context
        
        if not mood_ctx:
            return insights
        
        try:
            # Mood trend insight
            if mood_ctx.mood_trend == "declining":
                insights.append(IntelligenceInsight(
                    user_id=user_id,
                    insight_type="mood_trend_warning",
                    confidence=0.8,
                    description="Your mood has been declining recently. Consider engaging in activities that typically boost your mood.",
                    recommendations=[
                        "Try meditation or mindfulness exercises",
                        "Engage with the community challenges",
                        "Review your journal entries for patterns",
                        "Consider adjusting your daily routine"
                    ],
                    supporting_data={
                        "current_mood": mood_ctx.mood_score,
                        "trend": mood_ctx.mood_trend,
                        "energy_level": mood_ctx.energy_level
                    },
                    priority=ContextPriority.HIGH,
                    tags=["mood", "wellbeing", "trend_analysis"]
                ))
            elif mood_ctx.mood_trend == "improving":
                insights.append(IntelligenceInsight(
                    user_id=user_id,
                    insight_type="mood_trend_positive",
                    confidence=0.9,
                    description="Great news! Your mood has been improving. Keep up the positive momentum.",
                    recommendations=[
                        "Continue current activities that are working well",
                        "Share your success with the community",
                        "Document what's working in your journal",
                        "Set new positive goals"
                    ],
                    supporting_data={
                        "current_mood": mood_ctx.mood_score,
                        "trend": mood_ctx.mood_trend,
                        "energy_level": mood_ctx.energy_level
                    },
                    priority=ContextPriority.NORMAL,
                    tags=["mood", "positive", "momentum"]
                ))
            
            # Energy level insights
            if mood_ctx.energy_level < 3:
                insights.append(IntelligenceInsight(
                    user_id=user_id,
                    insight_type="low_energy_alert",
                    confidence=0.7,
                    description="Your energy levels seem low. Consider focusing on restorative activities.",
                    recommendations=[
                        "Prioritize sleep quality",
                        "Try gentle physical activities",
                        "Consider energy-boosting nutrition",
                        "Schedule downtime and rest"
                    ],
                    supporting_data={"energy_level": mood_ctx.energy_level},
                    priority=ContextPriority.NORMAL,
                    tags=["energy", "wellbeing", "self_care"]
                ))
            
        except Exception as e:
            logger.error(f"❌ Error generating mood insights: {e}")
        
        return insights
    
    async def _generate_community_insights(self, user_id: str, context: UserContext) -> List[IntelligenceInsight]:
        """Generate community engagement insights"""
        insights = []
        community_ctx = context.community_context
        
        if not community_ctx:
            return insights
        
        try:
            # Low engagement insight
            if community_ctx.engagement_level == "low":
                insights.append(IntelligenceInsight(
                    user_id=user_id,
                    insight_type="low_community_engagement",
                    confidence=0.6,
                    description="You haven't been very active in the community lately. Connecting with others could boost your wellbeing.",
                    recommendations=[
                        "Join a community challenge",
                        "Share your experiences in a post",
                        "Comment on others' posts",
                        "Find topics that interest you"
                    ],
                    supporting_data={
                        "engagement_level": community_ctx.engagement_level,
                        "posts_created": community_ctx.posts_created,
                        "social_score": community_ctx.social_score
                    },
                    priority=ContextPriority.NORMAL,
                    tags=["community", "engagement", "social"]
                ))
            
            # Challenge participation insight
            if len(community_ctx.challenge_participation) > 0:
                insights.append(IntelligenceInsight(
                    user_id=user_id,
                    insight_type="active_challenger",
                    confidence=0.8,
                    description=f"You're actively participating in {len(community_ctx.challenge_participation)} challenges. Keep up the great work!",
                    recommendations=[
                        "Share your progress with others",
                        "Encourage fellow participants",
                        "Document your journey",
                        "Celebrate small wins"
                    ],
                    supporting_data={
                        "active_challenges": len(community_ctx.challenge_participation),
                        "challenge_list": community_ctx.challenge_participation
                    },
                    priority=ContextPriority.NORMAL,
                    tags=["challenges", "motivation", "achievement"]
                ))
            
        except Exception as e:
            logger.error(f"❌ Error generating community insights: {e}")
        
        return insights
    
    async def _generate_communication_insights(self, user_id: str, context: UserContext) -> List[IntelligenceInsight]:
        """Generate communication preference insights"""
        insights = []
        
        try:
            # Voice interaction insights
            if context.voice_context and context.voice_context.interaction_frequency > 5:
                insights.append(IntelligenceInsight(
                    user_id=user_id,
                    insight_type="voice_user_profile",
                    confidence=0.9,
                    description="You're an active voice user! Voice interactions could be your preferred way to engage with the app.",
                    recommendations=[
                        "Explore more voice commands",
                        "Use voice for journaling",
                        "Set up voice reminders",
                        "Try voice-guided meditations"
                    ],
                    supporting_data={
                        "interaction_frequency": context.voice_context.interaction_frequency,
                        "preferred_commands": context.voice_context.preferred_voice_commands
                    },
                    priority=ContextPriority.NORMAL,
                    tags=["voice", "interaction_preference", "personalization"]
                ))
            
            # Notification engagement insights
            if context.notification_context:
                high_engagement_types = [
                    notif_type for notif_type, rate in context.notification_context.engagement_rates.items()
                    if rate > 0.7
                ]
                
                if high_engagement_types:
                    insights.append(IntelligenceInsight(
                        user_id=user_id,
                        insight_type="notification_preferences",
                        confidence=0.8,
                        description=f"You engage most with {', '.join(high_engagement_types)} notifications. We'll prioritize these for you.",
                        recommendations=[
                            f"More {high_engagement_types[0]} notifications",
                            "Optimize notification timing",
                            "Reduce low-engagement notification types",
                            "Customize notification content"
                        ],
                        supporting_data={
                            "high_engagement_types": high_engagement_types,
                            "engagement_rates": context.notification_context.engagement_rates
                        },
                        priority=ContextPriority.NORMAL,
                        tags=["notifications", "engagement", "personalization"]
                    ))
            
        except Exception as e:
            logger.error(f"❌ Error generating communication insights: {e}")
        
        return insights
    
    async def _generate_cultural_insights(self, user_id: str, context: UserContext) -> List[IntelligenceInsight]:
        """Generate cultural and language insights"""
        insights = []
        translation_ctx = context.translation_context
        
        if not translation_ctx:
            return insights
        
        try:
            if translation_ctx.translation_frequency > 3:
                insights.append(IntelligenceInsight(
                    user_id=user_id,
                    insight_type="multilingual_user",
                    confidence=0.9,
                    description=f"You're actively using {len(set(translation_ctx.source_languages + translation_ctx.target_languages))} languages. We can provide culturally-aware content.",
                    recommendations=[
                        "Explore content in your preferred languages",
                        "Connect with multicultural community members",
                        "Share cultural perspectives",
                        "Access region-specific wellness practices"
                    ],
                    supporting_data={
                        "languages_used": list(set(translation_ctx.source_languages + translation_ctx.target_languages)),
                        "translation_frequency": translation_ctx.translation_frequency,
                        "cultural_preferences": translation_ctx.cultural_preferences
                    },
                    priority=ContextPriority.NORMAL,
                    tags=["multicultural", "language", "personalization"]
                ))
            
        except Exception as e:
            logger.error(f"❌ Error generating cultural insights: {e}")
        
        return insights
    
    async def _generate_content_insights(self, user_id: str, context: UserContext) -> List[IntelligenceInsight]:
        """Generate content personalization insights"""
        insights = []
        content_ctx = context.content_context
        
        if not content_ctx:
            return insights
        
        try:
            if len(content_ctx.content_preferences) > 0:
                top_preferences = content_ctx.content_preferences[:3]
                insights.append(IntelligenceInsight(
                    user_id=user_id,
                    insight_type="content_personalization",
                    confidence=0.8,
                    description=f"Your top content interests are: {', '.join(top_preferences)}. We'll curate more content in these areas.",
                    recommendations=[
                        f"Explore more {top_preferences[0]} content",
                        "Join discussions about your interests",
                        "Share content that resonates with you",
                        "Discover related topics"
                    ],
                    supporting_data={
                        "top_preferences": top_preferences,
                        "all_preferences": content_ctx.content_preferences,
                        "engagement_patterns": content_ctx.engagement_patterns
                    },
                    priority=ContextPriority.NORMAL,
                    tags=["content", "personalization", "interests"]
                ))
            
        except Exception as e:
            logger.error(f"❌ Error generating content insights: {e}")
        
        return insights
    
    async def _generate_cross_service_insights(self, user_id: str, context: UserContext) -> List[IntelligenceInsight]:
        """Generate insights from cross-service analysis"""
        insights = []
        
        try:
            # Holistic wellbeing insight
            completeness = context.context_completeness
            activity = context.activity_score
            
            if completeness > 0.7 and activity > 0.5:
                insights.append(IntelligenceInsight(
                    user_id=user_id,
                    insight_type="holistic_engagement",
                    confidence=0.9,
                    description="You're actively engaging across multiple aspects of wellbeing. This holistic approach is excellent for overall mental health.",
                    recommendations=[
                        "Continue your balanced approach",
                        "Consider becoming a community mentor",
                        "Share your strategies with others",
                        "Set new holistic goals"
                    ],
                    supporting_data={
                        "context_completeness": completeness,
                        "activity_score": activity,
                        "active_areas": self._get_active_context_areas(context)
                    },
                    priority=ContextPriority.HIGH,
                    tags=["holistic", "wellbeing", "engagement", "leadership"]
                ))
            elif completeness < 0.3:
                insights.append(IntelligenceInsight(
                    user_id=user_id,
                    insight_type="engagement_opportunity",
                    confidence=0.7,
                    description="There are several app features you haven't explored yet. Diversifying your engagement could enhance your wellbeing journey.",
                    recommendations=[
                        "Try voice interactions",
                        "Join community discussions",
                        "Explore content recommendations",
                        "Experiment with different features"
                    ],
                    supporting_data={
                        "context_completeness": completeness,
                        "missing_areas": self._get_missing_context_areas(context)
                    },
                    priority=ContextPriority.NORMAL,
                    tags=["exploration", "features", "engagement"]
                ))
            
        except Exception as e:
            logger.error(f"❌ Error generating cross-service insights: {e}")
        
        return insights
    
    def _get_active_context_areas(self, context: UserContext) -> List[str]:
        """Get list of active context areas"""
        active_areas = []
        if context.mood_context:
            active_areas.append("mood_tracking")
        if context.community_context:
            active_areas.append("community_engagement")
        if context.voice_context:
            active_areas.append("voice_interaction")
        if context.translation_context:
            active_areas.append("multilingual_support")
        if context.content_context:
            active_areas.append("content_consumption")
        if context.notification_context:
            active_areas.append("notification_engagement")
        return active_areas
    
    def _get_missing_context_areas(self, context: UserContext) -> List[str]:
        """Get list of missing context areas"""
        all_areas = ["mood_tracking", "community_engagement", "voice_interaction", 
                    "multilingual_support", "content_consumption", "notification_engagement"]
        active_areas = self._get_active_context_areas(context)
        return [area for area in all_areas if area not in active_areas]
    
    # Background processing methods
    
    async def _periodic_intelligence_processing(self):
        """Periodic task to process intelligence queue"""
        while self.is_running:
            try:
                if self.processing_queue:
                    # Process one item from queue
                    item = self.processing_queue.pop(0)
                    await self._process_intelligence_item(item)
                
                await asyncio.sleep(5)  # Process every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in periodic intelligence processing: {e}")
                await asyncio.sleep(10)
    
    async def _process_intelligence_item(self, item: Dict[str, Any]):
        """Process a single intelligence item"""
        try:
            item_type = item.get("type")
            user_id = item.get("user_id")
            
            if item_type == "ml_insight":
                # Process ML insight
                logger.debug(f"🧠 Processing ML insight for user {user_id}")
                # Here you would integrate with ML insights
                
            elif item_type == "high_priority_context":
                # Process high priority context update
                logger.debug(f"🔥 Processing high priority context for user {user_id}")
                # Trigger immediate insight generation if needed
                
        except Exception as e:
            self.processing_errors += 1
            logger.error(f"❌ Error processing intelligence item: {e}")
    
    async def _periodic_insight_cleanup(self):
        """Periodic task to clean up old insights"""
        while self.is_running:
            try:
                cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
                
                for user_id, insights in list(self.insights_cache.items()):
                    # Remove expired insights
                    fresh_insights = [
                        insight for insight in insights
                        if not insight.expires_at or insight.expires_at > cutoff
                    ]
                    
                    if len(fresh_insights) != len(insights):
                        self.insights_cache[user_id] = fresh_insights
                        logger.debug(f"🧹 Cleaned up expired insights for user {user_id}")
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"❌ Error in periodic insight cleanup: {e}")
                await asyncio.sleep(300)
