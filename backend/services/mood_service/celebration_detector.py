"""
Celebration Detection System - Phase 1 Enhancement
Detects achievements and celebration moments to motivate users in their wellness journey
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import statistics

# Import shared models
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from shared.models import MoodEntry, CelebrationMoment, JournalEntry
from shared.database import get_db

class CelebrationData:
    """Data structure for celebration moments"""
    def __init__(self, celebration_type: str, title: str, message: str,
                 achievement_level: str = "bronze", reward_type: str = None, reward_data: Dict = None):
        self.celebration_type = celebration_type
        self.title = title
        self.message = message
        self.achievement_level = achievement_level
        self.reward_type = reward_type
        self.reward_data = reward_data or {}

class CelebrationMomentDetector:
    """Service for detecting celebration-worthy achievements and milestones"""
    
    def __init__(self):
        self.achievement_patterns = self._load_achievement_patterns()
        
    def _load_achievement_patterns(self) -> Dict[str, Any]:
        """Load achievement patterns and thresholds"""
        return {
            "improvement_streaks": {
                "3_day_improvement": {
                    "threshold": 3,
                    "level": "bronze",
                    "title": "3-Day Improvement Streak! 🌟",
                    "message": "Amazing! You've had 3 days of improving mood. Keep this positive momentum going!",
                    "reward": "insight_unlock"
                },
                "7_day_improvement": {
                    "threshold": 7,
                    "level": "silver",
                    "title": "Week-Long Improvement Streak! ✨",
                    "message": "Incredible! A full week of mood improvement shows your dedication to wellness.",
                    "reward": "feature_unlock"
                },
                "14_day_improvement": {
                    "threshold": 14,
                    "level": "gold",
                    "title": "Two-Week Transformation! 🏆",
                    "message": "Outstanding! Two weeks of consistent improvement is a major achievement!",
                    "reward": "premium_insight"
                }
            },
            "consistency_milestones": {
                "3_day_streak": {
                    "threshold": 3,
                    "level": "bronze",
                    "title": "3-Day Tracking Streak! 📊",
                    "message": "Great start! You're building a healthy habit of self-awareness.",
                    "reward": "encouragement"
                },
                "7_day_streak": {
                    "threshold": 7,
                    "level": "silver", 
                    "title": "One Week Strong! 🔥",
                    "message": "A full week of tracking! Your commitment to understanding yourself is inspiring.",
                    "reward": "weekly_insight"
                },
                "30_day_streak": {
                    "threshold": 30,
                    "level": "gold",
                    "title": "Monthly Master! 👑",
                    "message": "30 days of consistent tracking! You've built a powerful habit for life.",
                    "reward": "master_badge"
                }
            },
            "resilience_moments": {
                "bounce_back": {
                    "pattern": "low_to_high_recovery",
                    "level": "silver",
                    "title": "Resilience Demonstrated! 💪",
                    "message": "You bounced back from a difficult time - that's real strength and growth!",
                    "reward": "resilience_badge"
                },
                "stress_management": {
                    "pattern": "stress_reduction_success",
                    "level": "bronze",
                    "title": "Stress Conquered! 🧘",
                    "message": "You successfully managed rising stress levels. Your coping strategies are working!",
                    "reward": "coping_insight"
                }
            },
            "milestone_achievements": {
                "first_week": {
                    "threshold": 7,
                    "level": "bronze",
                    "title": "Welcome to Your Wellness Journey! 🌱",
                    "message": "You've completed your first week of mood tracking. The journey of self-discovery begins!",
                    "reward": "welcome_insights"
                },
                "mood_variety": {
                    "pattern": "emotional_range_exploration",
                    "level": "bronze",
                    "title": "Emotional Awareness Growing! 🎭",
                    "message": "You're exploring the full range of emotions - that's healthy emotional intelligence!",
                    "reward": "emotion_guide"
                }
            }
        }
    
    async def detect_celebrations(self, user_id: str, db: Session, 
                                 trigger_context: Dict[str, Any] = None) -> List[CelebrationData]:
        """Detect all potential celebration moments for a user"""
        
        celebrations = []
        
        # Get user's mood and journal entries for analysis
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(desc(MoodEntry.created_at)).limit(30).all()
        
        if not mood_entries:
            return celebrations
        
        # Check for improvement streaks
        improvement_celebrations = await self._detect_improvement_streaks(mood_entries)
        celebrations.extend(improvement_celebrations)
        
        # Check for consistency milestones
        consistency_celebrations = await self._detect_consistency_milestones(mood_entries)
        celebrations.extend(consistency_celebrations)
        
        # Check for resilience moments
        resilience_celebrations = await self._detect_resilience_moments(mood_entries)
        celebrations.extend(resilience_celebrations)
        
        # Check for milestone achievements
        milestone_celebrations = await self._detect_milestone_achievements(mood_entries, db, user_id)
        celebrations.extend(milestone_celebrations)
        
        # Store new celebrations in database
        await self._store_celebrations(user_id, celebrations, db)
        
        return celebrations
    
    async def _detect_improvement_streaks(self, entries: List[MoodEntry]) -> List[CelebrationData]:
        """Detect mood improvement streaks"""
        
        celebrations = []
        if len(entries) < 3:
            return celebrations
        
        # Look for consecutive days of improvement
        improvement_days = 0
        previous_mood = None
        
        for entry in reversed(entries[:14]):  # Check last 14 days
            if previous_mood is not None:
                if entry.mood_score > previous_mood:
                    improvement_days += 1
                else:
                    # Check if we have a streak to celebrate
                    if improvement_days >= 3:
                        celebration = self._create_improvement_celebration(improvement_days)
                        if celebration:
                            celebrations.append(celebration)
                    improvement_days = 0
            previous_mood = entry.mood_score
        
        # Check final streak
        if improvement_days >= 3:
            celebration = self._create_improvement_celebration(improvement_days)
            if celebration:
                celebrations.append(celebration)
        
        return celebrations
    
    def _create_improvement_celebration(self, streak_length: int) -> Optional[CelebrationData]:
        """Create celebration for improvement streak"""
        
        patterns = self.achievement_patterns["improvement_streaks"]
        
        if streak_length >= 14:
            pattern = patterns["14_day_improvement"]
        elif streak_length >= 7:
            pattern = patterns["7_day_improvement"]
        elif streak_length >= 3:
            pattern = patterns["3_day_improvement"]
        else:
            return None
        
        return CelebrationData(
            celebration_type="improvement_streak",
            title=pattern["title"],
            message=pattern["message"],
            achievement_level=pattern["level"],
            reward_type=pattern["reward"],
            reward_data={"streak_length": streak_length}
        )
    
    async def _detect_consistency_milestones(self, entries: List[MoodEntry]) -> List[CelebrationData]:
        """Detect tracking consistency milestones"""
        
        celebrations = []
        
        # Check for consecutive tracking days
        if len(entries) < 3:
            return celebrations
        
        # Count consecutive days of tracking
        consecutive_days = 1
        previous_date = entries[0].created_at.date()
        
        for entry in entries[1:]:
            entry_date = entry.created_at.date()
            if (previous_date - entry_date).days == 1:
                consecutive_days += 1
                previous_date = entry_date
            else:
                break
        
        # Create celebration based on streak length
        patterns = self.achievement_patterns["consistency_milestones"]
        
        celebration = None
        if consecutive_days >= 30:
            pattern = patterns["30_day_streak"]
            celebration = CelebrationData(
                celebration_type="consistency_streak",
                title=pattern["title"],
                message=pattern["message"],
                achievement_level=pattern["level"],
                reward_type=pattern["reward"],
                reward_data={"streak_length": consecutive_days}
            )
        elif consecutive_days >= 7:
            pattern = patterns["7_day_streak"]
            celebration = CelebrationData(
                celebration_type="consistency_streak",
                title=pattern["title"],
                message=pattern["message"],
                achievement_level=pattern["level"],
                reward_type=pattern["reward"],
                reward_data={"streak_length": consecutive_days}
            )
        elif consecutive_days >= 3:
            pattern = patterns["3_day_streak"]
            celebration = CelebrationData(
                celebration_type="consistency_streak",
                title=pattern["title"],
                message=pattern["message"],
                achievement_level=pattern["level"],
                reward_type=pattern["reward"],
                reward_data={"streak_length": consecutive_days}
            )
        
        if celebration:
            celebrations.append(celebration)
        
        return celebrations
    
    async def _detect_resilience_moments(self, entries: List[MoodEntry]) -> List[CelebrationData]:
        """Detect moments of resilience and recovery"""
        
        celebrations = []
        if len(entries) < 5:
            return celebrations
        
        # Look for bounce-back patterns (low mood followed by recovery)
        for i in range(len(entries) - 4):
            recent_window = entries[i:i+3]  # 3-day window
            older_window = entries[i+2:i+5]  # Previous 3-day window
            
            recent_avg = statistics.mean([e.mood_score for e in recent_window])
            older_avg = statistics.mean([e.mood_score for e in older_window])
            
            # Check for significant recovery
            if older_avg <= 4 and recent_avg >= 7:  # From low to high
                pattern = self.achievement_patterns["resilience_moments"]["bounce_back"]
                celebration = CelebrationData(
                    celebration_type="resilience",
                    title=pattern["title"],
                    message=pattern["message"],
                    achievement_level=pattern["level"],
                    reward_type=pattern["reward"],
                    reward_data={
                        "recovery_amount": recent_avg - older_avg,
                        "low_point": older_avg,
                        "recovery_point": recent_avg
                    }
                )
                celebrations.append(celebration)
                break  # Only celebrate one major recovery
        
        # Look for stress management success
        stress_entries = [e for e in entries[:7] if e.stress_level is not None]
        if len(stress_entries) >= 5:
            recent_stress = statistics.mean([e.stress_level for e in stress_entries[:3]])
            older_stress = statistics.mean([e.stress_level for e in stress_entries[3:]])
            
            if older_stress >= 7 and recent_stress <= 4:  # Significant stress reduction
                pattern = self.achievement_patterns["resilience_moments"]["stress_management"]
                celebration = CelebrationData(
                    celebration_type="stress_management",
                    title=pattern["title"],
                    message=pattern["message"],
                    achievement_level=pattern["level"],
                    reward_type=pattern["reward"],
                    reward_data={
                        "stress_reduction": older_stress - recent_stress
                    }
                )
                celebrations.append(celebration)
        
        return celebrations
    
    async def _detect_milestone_achievements(self, entries: List[MoodEntry], 
                                           db: Session, user_id: str) -> List[CelebrationData]:
        """Detect general milestone achievements"""
        
        celebrations = []
        
        # Check if this is their first week
        if len(entries) == 7:  # Exactly 7 entries might mean first week completion
            first_entry_date = entries[-1].created_at.date()
            latest_entry_date = entries[0].created_at.date()
            
            if (latest_entry_date - first_entry_date).days >= 6:  # At least a week span
                pattern = self.achievement_patterns["milestone_achievements"]["first_week"]
                celebration = CelebrationData(
                    celebration_type="first_week",
                    title=pattern["title"],
                    message=pattern["message"],
                    achievement_level=pattern["level"],
                    reward_type=pattern["reward"],
                    reward_data={"total_entries": len(entries)}
                )
                celebrations.append(celebration)
        
        # Check for emotional range exploration
        if len(entries) >= 10:
            mood_scores = [e.mood_score for e in entries[:10]]
            mood_range = max(mood_scores) - min(mood_scores)
            unique_moods = len(set(mood_scores))
            
            if mood_range >= 6 and unique_moods >= 5:  # Good emotional range
                pattern = self.achievement_patterns["milestone_achievements"]["mood_variety"]
                celebration = CelebrationData(
                    celebration_type="emotional_awareness",
                    title=pattern["title"],
                    message=pattern["message"],
                    achievement_level=pattern["level"],
                    reward_type=pattern["reward"],
                    reward_data={
                        "mood_range": mood_range,
                        "unique_moods": unique_moods
                    }
                )
                celebrations.append(celebration)
        
        return celebrations
    
    async def _store_celebrations(self, user_id: str, celebrations: List[CelebrationData], 
                                db: Session):
        """Store new celebrations in database"""
        
        for celebration in celebrations:
            # Check if this type of celebration was already given recently
            existing = db.query(CelebrationMoment).filter(
                CelebrationMoment.user_id == user_id,
                CelebrationMoment.celebration_type == celebration.celebration_type,
                CelebrationMoment.created_at >= datetime.utcnow() - timedelta(days=7)
            ).first()
            
            if not existing:  # Only create if not recently celebrated
                celebration_moment = CelebrationMoment(
                    user_id=user_id,
                    celebration_type=celebration.celebration_type,
                    title=celebration.title,
                    message=celebration.message,
                    achievement_level=celebration.achievement_level,
                    reward_type=celebration.reward_type,
                    reward_data=celebration.reward_data
                )
                
                db.add(celebration_moment)
        
        db.commit()
    
    async def get_pending_celebrations(self, user_id: str, db: Session) -> List[Dict[str, Any]]:
        """Get celebrations that haven't been shown to the user yet"""
        
        pending = db.query(CelebrationMoment).filter(
            CelebrationMoment.user_id == user_id,
            CelebrationMoment.is_shown == False
        ).order_by(desc(CelebrationMoment.created_at)).all()
        
        celebrations = []
        for celebration in pending:
            celebrations.append({
                "id": celebration.id,
                "type": celebration.celebration_type,
                "title": celebration.title,
                "message": celebration.message,
                "achievement_level": celebration.achievement_level,
                "reward_type": celebration.reward_type,
                "reward_data": celebration.reward_data,
                "created_at": celebration.created_at.isoformat()
            })
        
        return celebrations
    
    async def mark_celebrations_shown(self, user_id: str, celebration_ids: List[str], 
                                    db: Session):
        """Mark celebrations as shown to the user"""
        
        db.query(CelebrationMoment).filter(
            CelebrationMoment.user_id == user_id,
            CelebrationMoment.id.in_(celebration_ids)
        ).update(
            {"is_shown": True, "shown_at": datetime.utcnow()},
            synchronize_session=False
        )
        
        db.commit()
    
    async def get_celebration_stats(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get user's celebration statistics"""
        
        celebrations = db.query(CelebrationMoment).filter(
            CelebrationMoment.user_id == user_id
        ).all()
        
        stats = {
            "total_celebrations": len(celebrations),
            "by_type": {},
            "by_level": {},
            "recent_achievements": []
        }
        
        for celebration in celebrations:
            # Count by type
            if celebration.celebration_type not in stats["by_type"]:
                stats["by_type"][celebration.celebration_type] = 0
            stats["by_type"][celebration.celebration_type] += 1
            
            # Count by level
            if celebration.achievement_level not in stats["by_level"]:
                stats["by_level"][celebration.achievement_level] = 0
            stats["by_level"][celebration.achievement_level] += 1
            
            # Add recent achievements
            if celebration.created_at >= datetime.utcnow() - timedelta(days=30):
                stats["recent_achievements"].append({
                    "title": celebration.title,
                    "level": celebration.achievement_level,
                    "date": celebration.created_at.strftime("%Y-%m-%d")
                })
        
        return stats
