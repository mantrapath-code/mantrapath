"""
Memory Engine - Core logic for user interaction tracking and behavioral analysis
Handles pattern analysis, insight generation, and cross-platform aggregation
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
import json
import statistics
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
import numpy as np
from collections import defaultdict, Counter

from shared.database import SessionLocal
from shared.redis_client import redis_client
from shared.models import UserInteraction, MoodPattern, BehavioralInsight, MemorySession, MemoryAggregation

logger = logging.getLogger(__name__)

class MemoryEngine:
    """
    Core Memory Engine for processing user interactions and generating insights
    """
    
    def __init__(self):
        self.is_initialized = False
        self.stats = {
            "interactions_processed": 0,
            "patterns_analyzed": 0,
            "insights_generated": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Configuration
        self.config = {
            "pattern_analysis_window_days": 30,
            "insight_generation_threshold": 10,  # minimum interactions for insights
            "cache_ttl_seconds": 3600,  # 1 hour
            "batch_size": 100,
            "max_patterns_per_user": 50,
            "cultural_adaptation_enabled": True
        }
        
        # Pattern detection thresholds
        self.thresholds = {
            "mood_stability": 0.7,
            "pattern_confidence": 0.6,
            "insight_relevance": 0.5,
            "cultural_sensitivity": 0.8
        }

    async def initialize(self):
        """Initialize the Memory Engine"""
        try:
            logger.info("🧠 Initializing Memory Engine...")
            
            # Test database connection
            with SessionLocal() as db:
                db.execute("SELECT 1")
            
            # Test Redis connection
            await redis_client.ping()
            
            # Initialize any required data structures
            await self._initialize_pattern_algorithms()
            await self._initialize_insight_generators()
            
            self.is_initialized = True
            logger.info("✅ Memory Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Memory Engine initialization failed: {e}")
            raise

    def is_ready(self) -> bool:
        """Check if Memory Engine is ready"""
        return self.is_initialized

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Memory Engine cleanup started")
        self.is_initialized = False
        logger.info("✅ Memory Engine cleanup completed")

    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return self.stats.copy()

    async def record_interaction(
        self, 
        user_id: str, 
        interaction_type: str, 
        interaction_data: Dict[str, Any],
        source_service: str,
        session_id: Optional[str] = None,
        cultural_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UserInteraction:
        """
        Record a new user interaction
        """
        try:
            with SessionLocal() as db:
                # Create interaction record
                interaction = UserInteraction(
                    user_id=user_id,
                    interaction_type=interaction_type,
                    interaction_data=interaction_data,
                    source_service=source_service,
                    session_id=session_id,
                    cultural_context=cultural_context or {},
                    metadata=metadata or {},
                    timestamp=datetime.now(timezone.utc)
                )
                
                db.add(interaction)
                db.commit()
                db.refresh(interaction)
                
                self.stats["interactions_processed"] += 1
                
                # Update session if provided
                if session_id:
                    await self._update_session(db, session_id, user_id, interaction)
                
                # Trigger async analysis
                asyncio.create_task(self._analyze_new_interaction(interaction))
                
                # Invalidate relevant caches
                await self._invalidate_user_caches(user_id)
                
                logger.info(f"📝 Recorded interaction: {interaction_type} for user {user_id}")
                return interaction
                
        except Exception as e:
            logger.error(f"❌ Failed to record interaction: {e}")
            raise

    async def get_user_interactions(
        self,
        user_id: str,
        interaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[UserInteraction]:
        """
        Retrieve user interactions with filtering
        """
        try:
            # Try cache first
            cache_key = f"interactions:{user_id}:{interaction_type}:{start_date}:{end_date}:{limit}:{offset}"
            cached_result = await redis_client.get(cache_key)
            
            if cached_result:
                self.stats["cache_hits"] += 1
                return json.loads(cached_result)
            
            self.stats["cache_misses"] += 1
            
            with SessionLocal() as db:
                query = db.query(UserInteraction).filter(
                    UserInteraction.user_id == user_id,
                    UserInteraction.is_deleted == False
                )
                
                if interaction_type:
                    query = query.filter(UserInteraction.interaction_type == interaction_type)
                
                if start_date:
                    query = query.filter(UserInteraction.timestamp >= start_date)
                
                if end_date:
                    query = query.filter(UserInteraction.timestamp <= end_date)
                
                interactions = query.order_by(desc(UserInteraction.timestamp))\
                                  .offset(offset)\
                                  .limit(limit)\
                                  .all()
                
                # Cache result
                await redis_client.setex(
                    cache_key, 
                    self.config["cache_ttl_seconds"], 
                    json.dumps([self._serialize_interaction(i) for i in interactions])
                )
                
                return interactions
                
        except Exception as e:
            logger.error(f"❌ Failed to get user interactions: {e}")
            raise

    async def analyze_mood_patterns(self, user_id: str) -> List[MoodPattern]:
        """
        Analyze mood patterns for a user
        """
        try:
            # Check for existing recent analysis
            cache_key = f"mood_patterns:{user_id}"
            cached_patterns = await redis_client.get(cache_key)
            
            if cached_patterns:
                self.stats["cache_hits"] += 1
                return json.loads(cached_patterns)
            
            self.stats["cache_misses"] += 1
            
            with SessionLocal() as db:
                # Get recent mood interactions
                end_date = datetime.now(timezone.utc)
                start_date = end_date - timedelta(days=self.config["pattern_analysis_window_days"])
                
                mood_interactions = db.query(UserInteraction).filter(
                    UserInteraction.user_id == user_id,
                    UserInteraction.interaction_type.in_(["mood", "journal", "chat"]),
                    UserInteraction.timestamp >= start_date,
                    UserInteraction.is_deleted == False
                ).order_by(UserInteraction.timestamp).all()
                
                if len(mood_interactions) < self.config["insight_generation_threshold"]:
                    return []
                
                # Analyze patterns
                patterns = await self._detect_mood_patterns(user_id, mood_interactions, db)
                
                self.stats["patterns_analyzed"] += 1
                
                # Cache results
                await redis_client.setex(
                    cache_key,
                    self.config["cache_ttl_seconds"],
                    json.dumps([self._serialize_pattern(p) for p in patterns])
                )
                
                return patterns
                
        except Exception as e:
            logger.error(f"❌ Failed to analyze mood patterns: {e}")
            raise

    async def generate_behavioral_insights(self, user_id: str) -> List[BehavioralInsight]:
        """
        Generate behavioral insights for a user
        """
        try:
            # Get recent patterns and interactions
            patterns = await self.analyze_mood_patterns(user_id)
            interactions = await self.get_user_interactions(
                user_id, 
                start_date=datetime.now(timezone.utc) - timedelta(days=7)
            )
            
            if not patterns and len(interactions) < self.config["insight_generation_threshold"]:
                return []
            
            insights = []
            
            with SessionLocal() as db:
                # Generate different types of insights
                insights.extend(await self._generate_mood_insights(user_id, patterns, interactions, db))
                insights.extend(await self._generate_engagement_insights(user_id, interactions, db))
                insights.extend(await self._generate_cultural_insights(user_id, interactions, db))
                
                # Save insights to database
                for insight in insights:
                    db.add(insight)
                
                db.commit()
                
                self.stats["insights_generated"] += len(insights)
                
                # Invalidate caches
                await self._invalidate_user_caches(user_id)
                
                logger.info(f"🔍 Generated {len(insights)} insights for user {user_id}")
                return insights
                
        except Exception as e:
            logger.error(f"❌ Failed to generate behavioral insights: {e}")
            raise

    async def get_cross_platform_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get cross-platform interaction summary
        """
        try:
            cache_key = f"cross_platform:{user_id}"
            cached_summary = await redis_client.get(cache_key)
            
            if cached_summary:
                self.stats["cache_hits"] += 1
                return json.loads(cached_summary)
            
            self.stats["cache_misses"] += 1
            
            with SessionLocal() as db:
                end_date = datetime.now(timezone.utc)
                start_date = end_date - timedelta(days=30)
                
                # Aggregate by source service
                service_stats = db.query(
                    UserInteraction.source_service,
                    func.count(UserInteraction.id).label('count'),
                    func.avg(UserInteraction.quality_score).label('avg_quality')
                ).filter(
                    UserInteraction.user_id == user_id,
                    UserInteraction.timestamp >= start_date,
                    UserInteraction.is_deleted == False
                ).group_by(UserInteraction.source_service).all()
                
                # Aggregate by interaction type
                type_stats = db.query(
                    UserInteraction.interaction_type,
                    func.count(UserInteraction.id).label('count'),
                    func.avg(UserInteraction.confidence_score).label('avg_confidence')
                ).filter(
                    UserInteraction.user_id == user_id,
                    UserInteraction.timestamp >= start_date,
                    UserInteraction.is_deleted == False
                ).group_by(UserInteraction.interaction_type).all()
                
                # Build summary
                summary = {
                    "user_id": user_id,
                    "analysis_period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "days": 30
                    },
                    "service_breakdown": {
                        stat.source_service: {
                            "interaction_count": stat.count,
                            "avg_quality": float(stat.avg_quality or 0)
                        } for stat in service_stats
                    },
                    "type_breakdown": {
                        stat.interaction_type: {
                            "interaction_count": stat.count,
                            "avg_confidence": float(stat.avg_confidence or 0)
                        } for stat in type_stats
                    },
                    "total_interactions": sum(stat.count for stat in service_stats),
                    "active_services": len(service_stats),
                    "interaction_types": len(type_stats)
                }
                
                # Cache results
                await redis_client.setex(
                    cache_key,
                    self.config["cache_ttl_seconds"],
                    json.dumps(summary)
                )
                
                return summary
                
        except Exception as e:
            logger.error(f"❌ Failed to get cross-platform summary: {e}")
            raise

    # Private helper methods
    
    async def _initialize_pattern_algorithms(self):
        """Initialize pattern detection algorithms"""
        # Load any ML models or configuration needed for pattern detection
        pass

    async def _initialize_insight_generators(self):
        """Initialize insight generation algorithms"""
        # Load any ML models or configuration needed for insight generation
        pass

    async def _analyze_new_interaction(self, interaction: UserInteraction):
        """Async analysis of new interaction"""
        try:
            # Check if we should trigger pattern analysis
            with SessionLocal() as db:
                recent_count = db.query(func.count(UserInteraction.id)).filter(
                    UserInteraction.user_id == interaction.user_id,
                    UserInteraction.timestamp >= datetime.now(timezone.utc) - timedelta(hours=1)
                ).scalar()
                
                # Trigger analysis if we have enough recent interactions
                if recent_count >= 5:
                    await self.analyze_mood_patterns(interaction.user_id)
                    await self.generate_behavioral_insights(interaction.user_id)
                    
        except Exception as e:
            logger.error(f"❌ Failed to analyze new interaction: {e}")

    async def _update_session(self, db: Session, session_id: str, user_id: str, interaction: UserInteraction):
        """Update session with new interaction"""
        try:
            session = db.query(MemorySession).filter(
                MemorySession.session_id == session_id
            ).first()
            
            if not session:
                # Create new session
                session = MemorySession(
                    session_id=session_id,
                    user_id=user_id,
                    start_time=interaction.timestamp,
                    interaction_count=1
                )
                db.add(session)
            else:
                # Update existing session
                session.interaction_count += 1
                session.end_time = interaction.timestamp
                if session.start_time:
                    session.duration_seconds = int(
                        (interaction.timestamp - session.start_time).total_seconds()
                    )
            
            db.commit()
            
        except Exception as e:
            logger.error(f"❌ Failed to update session: {e}")

    async def _detect_mood_patterns(
        self, 
        user_id: str, 
        interactions: List[UserInteraction], 
        db: Session
    ) -> List[MoodPattern]:
        """Detect mood patterns from interactions"""
        patterns = []
        
        try:
            # Extract mood values from interactions
            mood_data = []
            for interaction in interactions:
                if 'mood_score' in interaction.interaction_data:
                    mood_data.append({
                        'timestamp': interaction.timestamp,
                        'score': float(interaction.interaction_data['mood_score']),
                        'cultural_context': interaction.cultural_context or {}
                    })
            
            if len(mood_data) < 5:
                return patterns
            
            # Detect daily patterns
            daily_pattern = await self._analyze_daily_pattern(user_id, mood_data, db)
            if daily_pattern:
                patterns.append(daily_pattern)
            
            # Detect weekly patterns
            weekly_pattern = await self._analyze_weekly_pattern(user_id, mood_data, db)
            if weekly_pattern:
                patterns.append(weekly_pattern)
            
            # Detect trend patterns
            trend_pattern = await self._analyze_trend_pattern(user_id, mood_data, db)
            if trend_pattern:
                patterns.append(trend_pattern)
            
        except Exception as e:
            logger.error(f"❌ Failed to detect mood patterns: {e}")
        
        return patterns

    async def _analyze_daily_pattern(
        self, 
        user_id: str, 
        mood_data: List[Dict], 
        db: Session
    ) -> Optional[MoodPattern]:
        """Analyze daily mood patterns"""
        try:
            # Group by hour of day
            hourly_moods = defaultdict(list)
            for data in mood_data:
                hour = data['timestamp'].hour
                hourly_moods[hour].append(data['score'])
            
            # Calculate averages for each hour
            hourly_averages = {}
            for hour, scores in hourly_moods.items():
                if len(scores) >= 3:  # Minimum data points
                    hourly_averages[hour] = statistics.mean(scores)
            
            if len(hourly_averages) < 4:  # Need at least 4 hours of data
                return None
            
            # Calculate pattern confidence
            score_variance = statistics.variance(hourly_averages.values())
            confidence = min(1.0, len(hourly_averages) / 24 * (1 - score_variance))
            
            if confidence < self.thresholds["pattern_confidence"]:
                return None
            
            # Create pattern
            pattern_data = {
                "hourly_averages": hourly_averages,
                "peak_hours": [h for h, s in hourly_averages.items() if s > 0.7],
                "low_hours": [h for h, s in hourly_averages.items() if s < 0.3],
                "variance": score_variance,
                "data_points": len(mood_data)
            }
            
            pattern = MoodPattern(
                user_id=user_id,
                pattern_type="daily",
                pattern_data=pattern_data,
                confidence_score=confidence,
                frequency="daily",
                start_date=min(d['timestamp'] for d in mood_data).date(),
                end_date=max(d['timestamp'] for d in mood_data).date()
            )
            
            db.add(pattern)
            return pattern
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze daily pattern: {e}")
            return None

    async def _analyze_weekly_pattern(
        self, 
        user_id: str, 
        mood_data: List[Dict], 
        db: Session
    ) -> Optional[MoodPattern]:
        """Analyze weekly mood patterns"""
        try:
            # Group by day of week
            weekly_moods = defaultdict(list)
            for data in mood_data:
                day_of_week = data['timestamp'].weekday()  # 0=Monday, 6=Sunday
                weekly_moods[day_of_week].append(data['score'])
            
            # Calculate averages for each day
            daily_averages = {}
            for day, scores in weekly_moods.items():
                if len(scores) >= 2:  # Minimum data points
                    daily_averages[day] = statistics.mean(scores)
            
            if len(daily_averages) < 5:  # Need at least 5 days of data
                return None
            
            # Calculate pattern confidence
            score_variance = statistics.variance(daily_averages.values())
            confidence = min(1.0, len(daily_averages) / 7 * (1 - score_variance))
            
            if confidence < self.thresholds["pattern_confidence"]:
                return None
            
            # Create pattern
            pattern_data = {
                "daily_averages": daily_averages,
                "best_days": [d for d, s in daily_averages.items() if s > 0.7],
                "challenging_days": [d for d, s in daily_averages.items() if s < 0.3],
                "variance": score_variance,
                "data_points": len(mood_data)
            }
            
            pattern = MoodPattern(
                user_id=user_id,
                pattern_type="weekly",
                pattern_data=pattern_data,
                confidence_score=confidence,
                frequency="weekly",
                start_date=min(d['timestamp'] for d in mood_data).date(),
                end_date=max(d['timestamp'] for d in mood_data).date()
            )
            
            db.add(pattern)
            return pattern
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze weekly pattern: {e}")
            return None

    async def _analyze_trend_pattern(
        self, 
        user_id: str, 
        mood_data: List[Dict], 
        db: Session
    ) -> Optional[MoodPattern]:
        """Analyze mood trend patterns"""
        try:
            if len(mood_data) < 10:  # Need sufficient data for trend analysis
                return None
            
            # Sort by timestamp
            sorted_data = sorted(mood_data, key=lambda x: x['timestamp'])
            scores = [d['score'] for d in sorted_data]
            
            # Calculate trend using linear regression
            x = list(range(len(scores)))
            slope = np.polyfit(x, scores, 1)[0]
            
            # Determine trend direction and strength
            trend_strength = abs(slope)
            trend_direction = "improving" if slope > 0 else "declining" if slope < 0 else "stable"
            
            confidence = min(1.0, trend_strength * 2)  # Scale appropriately
            
            if confidence < self.thresholds["pattern_confidence"]:
                return None
            
            # Create pattern
            pattern_data = {
                "slope": float(slope),
                "trend_direction": trend_direction,
                "trend_strength": float(trend_strength),
                "starting_score": scores[0],
                "ending_score": scores[-1],
                "score_change": scores[-1] - scores[0],
                "data_points": len(scores)
            }
            
            pattern = MoodPattern(
                user_id=user_id,
                pattern_type="trend",
                pattern_data=pattern_data,
                confidence_score=confidence,
                frequency="continuous",
                start_date=sorted_data[0]['timestamp'].date(),
                end_date=sorted_data[-1]['timestamp'].date()
            )
            
            db.add(pattern)
            return pattern
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze trend pattern: {e}")
            return None

    async def _generate_mood_insights(
        self,
        user_id: str,
        patterns: List[MoodPattern],
        interactions: List[UserInteraction],
        db: Session
    ) -> List[BehavioralInsight]:
        """Generate mood-related insights"""
        insights = []
        
        try:
            for pattern in patterns:
                if pattern.pattern_type == "daily" and pattern.confidence_score > 0.7:
                    # Daily pattern insights
                    peak_hours = pattern.pattern_data.get("peak_hours", [])
                    low_hours = pattern.pattern_data.get("low_hours", [])
                    
                    if peak_hours:
                        insight = BehavioralInsight(
                            user_id=user_id,
                            insight_type="mood_optimization",
                            title=f"Your mood peaks around {min(peak_hours)}:00",
                            description=f"You tend to feel best during hours {peak_hours}. Consider scheduling important activities during these times.",
                            recommendation="Plan your most important tasks during your peak mood hours.",
                            accuracy_score=pattern.confidence_score,
                            relevance_score=0.8,
                            urgency_level="medium",
                            priority=5,
                            insight_data={
                                "peak_hours": peak_hours,
                                "pattern_id": pattern.id,
                                "pattern_type": "daily"
                            }
                        )
                        insights.append(insight)
                    
                    if low_hours:
                        insight = BehavioralInsight(
                            user_id=user_id,
                            insight_type="mood_support",
                            title=f"You may need extra support around {min(low_hours)}:00",
                            description=f"Your mood tends to be lower during hours {low_hours}. Consider self-care activities during these times.",
                            recommendation="Schedule relaxation or mindfulness activities during your challenging hours.",
                            accuracy_score=pattern.confidence_score,
                            relevance_score=0.8,
                            urgency_level="medium",
                            priority=6,
                            insight_data={
                                "low_hours": low_hours,
                                "pattern_id": pattern.id,
                                "pattern_type": "daily"
                            }
                        )
                        insights.append(insight)
                
                elif pattern.pattern_type == "trend" and pattern.confidence_score > 0.6:
                    # Trend insights
                    trend_direction = pattern.pattern_data.get("trend_direction")
                    score_change = pattern.pattern_data.get("score_change", 0)
                    
                    if trend_direction == "improving":
                        insight = BehavioralInsight(
                            user_id=user_id,
                            insight_type="positive_trend",
                            title="Your mood is improving! 📈",
                            description=f"Your mood has improved by {score_change:.1f} points over the recent period.",
                            recommendation="Keep up the great work! Continue with the activities that are helping you feel better.",
                            accuracy_score=pattern.confidence_score,
                            relevance_score=0.9,
                            urgency_level="low",
                            priority=4,
                            insight_data={
                                "trend_direction": trend_direction,
                                "score_change": score_change,
                                "pattern_id": pattern.id
                            }
                        )
                        insights.append(insight)
                    
                    elif trend_direction == "declining" and abs(score_change) > 0.3:
                        insight = BehavioralInsight(
                            user_id=user_id,
                            insight_type="mood_alert",
                            title="Your mood needs attention 🤗",
                            description=f"Your mood has declined by {abs(score_change):.1f} points recently.",
                            recommendation="Consider reaching out for support or engaging in activities that usually help you feel better.",
                            accuracy_score=pattern.confidence_score,
                            relevance_score=0.9,
                            urgency_level="high",
                            priority=8,
                            insight_data={
                                "trend_direction": trend_direction,
                                "score_change": score_change,
                                "pattern_id": pattern.id
                            }
                        )
                        insights.append(insight)
        
        except Exception as e:
            logger.error(f"❌ Failed to generate mood insights: {e}")
        
        return insights

    async def _generate_engagement_insights(
        self,
        user_id: str,
        interactions: List[UserInteraction],
        db: Session
    ) -> List[BehavioralInsight]:
        """Generate engagement-related insights"""
        insights = []
        
        try:
            if len(interactions) < 5:
                return insights
            
            # Analyze engagement patterns
            service_counts = Counter(i.source_service for i in interactions)
            total_interactions = len(interactions)
            
            # Most used service
            most_used_service = service_counts.most_common(1)[0]
            service_name, service_count = most_used_service
            
            if service_count / total_interactions > 0.6:  # Dominant service usage
                insight = BehavioralInsight(
                    user_id=user_id,
                    insight_type="engagement_pattern",
                    title=f"You're most engaged with {service_name.replace('_', ' ').title()}",
                    description=f"You've used {service_name.replace('_', ' ')} for {service_count} out of {total_interactions} recent interactions.",
                    recommendation="Consider exploring other features that might also benefit your wellness journey.",
                    accuracy_score=0.8,
                    relevance_score=0.6,
                    urgency_level="low",
                    priority=3,
                    insight_data={
                        "dominant_service": service_name,
                        "usage_percentage": service_count / total_interactions,
                        "total_interactions": total_interactions
                    }
                )
                insights.append(insight)
            
            # Check for low engagement
            if total_interactions < 3:  # Very low engagement
                insight = BehavioralInsight(
                    user_id=user_id,
                    insight_type="engagement_encouragement",
                    title="We'd love to see you more often! 👋",
                    description="You haven't been very active recently. Regular check-ins can help maintain your wellness journey.",
                    recommendation="Try setting a daily reminder to check in with your mood or thoughts.",
                    accuracy_score=0.9,
                    relevance_score=0.7,
                    urgency_level="medium",
                    priority=5,
                    insight_data={
                        "interaction_count": total_interactions,
                        "engagement_level": "low"
                    }
                )
                insights.append(insight)
        
        except Exception as e:
            logger.error(f"❌ Failed to generate engagement insights: {e}")
        
        return insights

    async def _generate_cultural_insights(
        self,
        user_id: str,
        interactions: List[UserInteraction],
        db: Session
    ) -> List[BehavioralInsight]:
        """Generate cultural adaptation insights"""
        insights = []
        
        try:
            if not self.config["cultural_adaptation_enabled"]:
                return insights
            
            # Analyze cultural context patterns
            cultural_contexts = [
                i.cultural_context for i in interactions 
                if i.cultural_context and isinstance(i.cultural_context, dict)
            ]
            
            if not cultural_contexts:
                return insights
            
            # Check for cultural preferences
            languages = [ctx.get('language') for ctx in cultural_contexts if ctx.get('language')]
            if languages:
                primary_language = Counter(languages).most_common(1)[0][0]
                
                if primary_language != 'en':  # Non-English primary language
                    insight = BehavioralInsight(
                        user_id=user_id,
                        insight_type="cultural_adaptation",
                        title=f"Cultural Support in {primary_language.upper()}",
                        description=f"We notice you prefer {primary_language}. Our platform supports cultural context in your language.",
                        recommendation="Explore culturally adapted content and recommendations designed for your background.",
                        accuracy_score=0.8,
                        relevance_score=0.9,
                        urgency_level="low",
                        priority=4,
                        insight_data={
                            "primary_language": primary_language,
                            "cultural_support_available": True
                        }
                    )
                    insights.append(insight)
        
        except Exception as e:
            logger.error(f"❌ Failed to generate cultural insights: {e}")
        
        return insights

    async def _invalidate_user_caches(self, user_id: str):
        """Invalidate Redis caches for a user"""
        try:
            # Get all cache keys for this user
            patterns = [
                f"interactions:{user_id}:*",
                f"mood_patterns:{user_id}",
                f"cross_platform:{user_id}",
                f"insights:{user_id}:*"
            ]
            
            for pattern in patterns:
                keys = await redis_client.keys(pattern)
                if keys:
                    await redis_client.delete(*keys)
                    
        except Exception as e:
            logger.error(f"❌ Failed to invalidate caches: {e}")

    def _serialize_interaction(self, interaction: UserInteraction) -> Dict[str, Any]:
        """Serialize interaction for JSON storage"""
        return {
            "id": interaction.id,
            "user_id": interaction.user_id,
            "interaction_type": interaction.interaction_type,
            "interaction_data": interaction.interaction_data,
            "source_service": interaction.source_service,
            "timestamp": interaction.timestamp.isoformat(),
            "cultural_context": interaction.cultural_context,
            "metadata": interaction.metadata
        }

    def _serialize_pattern(self, pattern: MoodPattern) -> Dict[str, Any]:
        """Serialize pattern for JSON storage"""
        return {
            "id": pattern.id,
            "user_id": pattern.user_id,
            "pattern_type": pattern.pattern_type,
            "pattern_data": pattern.pattern_data,
            "confidence_score": pattern.confidence_score,
            "start_date": pattern.start_date.isoformat(),
            "end_date": pattern.end_date.isoformat()
        }
