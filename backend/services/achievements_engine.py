"""
E3 Achievement & Engagement Cohesion Engine - Clean Implementation
Unified server-side achievement system consolidating existing celebration logic
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from dataclasses import dataclass
from datetime import date

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../shared'))

from shared.models import MoodEntry, CelebrationMoment, JournalEntry, User
from shared.database import get_db

@dataclass
class AchievementDefinition:
    """Standardized achievement definition"""
    id: str
    title: str
    description: str
    category: str
    level: str = "bronze"  # bronze, silver, gold, platinum
    max_progress: int = 1
    icon: str = "🎯"
    criteria_function: Optional[str] = None
    celebration_type: Optional[str] = None

@dataclass
class UserAchievementProgress:
    """User's progress on specific achievement"""
    achievement_id: str
    current_progress: int = 0
    is_unlocked: bool = False
    unlocked_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class AchievementsEngine:
    """Unified achievements engine consolidating all achievement logic"""
    
    def __init__(self):
        self.achievement_definitions = self._load_achievement_definitions()
        
    def _load_achievement_definitions(self) -> Dict[str, AchievementDefinition]:
        """Load all achievement definitions"""
        achievements = {}
        
        # === MOOD TRACKING ACHIEVEMENTS ===
        achievements["first_steps"] = AchievementDefinition(
            id="first_steps",
            title="First Steps",
            description="Log your first mood entry",
            category="getting-started",
            level="bronze",
            max_progress=1,
            icon="🎯",
            criteria_function="check_first_mood_entry"
        )
        
        achievements["week_warrior"] = AchievementDefinition(
            id="week_warrior", 
            title="Week Warrior",
            description="Log moods for 7 consecutive days",
            category="consistency",
            level="silver",
            max_progress=7,
            icon="🔥",
            criteria_function="check_mood_streak"
        )
        
        achievements["mood_master"] = AchievementDefinition(
            id="mood_master",
            title="Mood Master", 
            description="Reach 30 total mood entries",
            category="milestone",
            level="gold",
            max_progress=30,
            icon="👑",
            criteria_function="check_mood_milestone"
        )
        
        achievements["positive_vibes"] = AchievementDefinition(
            id="positive_vibes",
            title="Positive Vibes",
            description="Log 5 excellent moods in a row",
            category="streak",
            level="silver", 
            max_progress=5,
            icon="✨",
            criteria_function="check_positive_streak"
        )
        
        # === CELEBRATION-BASED ACHIEVEMENTS ===
        achievements["improvement_streak_3"] = AchievementDefinition(
            id="improvement_streak_3",
            title="3-Day Improvement Streak! 🌟",
            description="Amazing! You've had 3 days of improving mood.",
            category="improvement_streaks",
            level="bronze",
            max_progress=3,
            icon="🌟",
            criteria_function="check_improvement_streak",
            celebration_type="improvement_streak"
        )
        
        achievements["improvement_streak_7"] = AchievementDefinition(
            id="improvement_streak_7", 
            title="Week-Long Improvement Streak! ✨",
            description="Incredible! A full week of mood improvement.",
            category="improvement_streaks",
            level="silver",
            max_progress=7,
            icon="✨",
            criteria_function="check_improvement_streak",
            celebration_type="improvement_streak"
        )
        
        achievements["consistency_streak_3"] = AchievementDefinition(
            id="consistency_streak_3",
            title="3-Day Tracking Streak! 📊",
            description="Great start! You're building a healthy habit.",
            category="consistency_milestones",
            level="bronze", 
            max_progress=3,
            icon="📊",
            criteria_function="check_consistency_streak",
            celebration_type="consistency"
        )
        
        achievements["consistency_streak_30"] = AchievementDefinition(
            id="consistency_streak_30",
            title="Monthly Master! 👑",
            description="30 days of consistent tracking!",
            category="consistency_milestones",
            level="gold",
            max_progress=30,
            icon="👑", 
            criteria_function="check_consistency_streak",
            celebration_type="consistency"
        )
        
        # === CELEBRATION META-ACHIEVEMENTS ===
        achievements["bronze_collector"] = AchievementDefinition(
            id="bronze_collector",
            title="Bronze Achiever",
            description="Earn 3 bronze level achievements",
            category="celebration",
            level="bronze",
            max_progress=3,
            icon="🥉",
            criteria_function="check_celebration_collection"
        )
        
        achievements["silver_collector"] = AchievementDefinition(
            id="silver_collector", 
            title="Silver Achiever",
            description="Earn 3 silver level achievements",
            category="celebration",
            level="silver",
            max_progress=3,
            icon="🥈",
            criteria_function="check_celebration_collection"
        )
        
        achievements["gold_collector"] = AchievementDefinition(
            id="gold_collector",
            title="Gold Achiever", 
            description="Earn 3 gold level achievements",
            category="celebration",
            level="gold",
            max_progress=3,
            icon="🥇",
            criteria_function="check_celebration_collection"
        )
        
        return achievements

    async def get_user_achievements(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get comprehensive user achievement data"""
        
        achievement_progress = {}
        celebration_stats = await self._get_celebration_stats(user_id, db)
        
        for achievement_id, definition in self.achievement_definitions.items():
            progress = await self._calculate_achievement_progress(
                user_id, definition, db
            )
            
            achievement_progress[achievement_id] = {
                "id": achievement_id,
                "title": definition.title,
                "description": definition.description, 
                "category": definition.category,
                "level": definition.level,
                "progress": progress.current_progress,
                "max_progress": definition.max_progress,
                "is_unlocked": progress.is_unlocked,
                "unlocked_at": progress.unlocked_at.isoformat() if progress.unlocked_at else None,
                "icon": definition.icon,
                "metadata": progress.metadata
            }
        
        # Calculate summary statistics
        all_achievements = list(achievement_progress.values())
        unlocked_achievements = [a for a in all_achievements if a["is_unlocked"]]
        locked_achievements = [a for a in all_achievements if not a["is_unlocked"]]
        
        total_progress = sum(a["progress"] / a["max_progress"] for a in all_achievements)
        average_progress = (total_progress / len(all_achievements)) * 100 if all_achievements else 0
        
        # Level distribution
        level_counts = {}
        for achievement in unlocked_achievements:
            level = achievement["level"]
            level_counts[level] = level_counts.get(level, 0) + 1
            
        return {
            "achievements": achievement_progress,
            "summary": {
                "total_achievements": len(all_achievements),
                "unlocked_count": len(unlocked_achievements),
                "locked_count": len(locked_achievements),
                "average_progress": round(average_progress, 1),
                "level_distribution": level_counts,
                "recent_unlocks": [
                    a for a in unlocked_achievements 
                    if a["unlocked_at"] and 
                    datetime.fromisoformat(a["unlocked_at"]) >= datetime.now() - timedelta(days=30)
                ][:5]
            },
            "celebration_stats": celebration_stats
        }

    async def _calculate_achievement_progress(self, user_id: str, 
                                            definition: AchievementDefinition,
                                            db: Session) -> UserAchievementProgress:
        """Calculate progress for specific achievement"""
        
        if not definition.criteria_function:
            return UserAchievementProgress(definition.id)
            
        try:
            calc_method = getattr(self, definition.criteria_function)
            return await calc_method(user_id, definition, db)
        except AttributeError:
            return UserAchievementProgress(definition.id)

    # === ACHIEVEMENT CRITERIA FUNCTIONS ===
    
    async def check_first_mood_entry(self, user_id: str, definition: AchievementDefinition, 
                                   db: Session) -> UserAchievementProgress:
        """Check if user has logged first mood entry"""
        mood_count = db.query(MoodEntry).filter(MoodEntry.user_id == user_id).count()
        
        is_unlocked = mood_count > 0
        unlocked_at = None
        
        if is_unlocked:
            first_entry = db.query(MoodEntry).filter(
                MoodEntry.user_id == user_id
            ).order_by(MoodEntry.created_at).first()
            if first_entry:
                unlocked_at = first_entry.created_at
            
        return UserAchievementProgress(
            definition.id,
            current_progress=min(1, mood_count),
            is_unlocked=is_unlocked,
            unlocked_at=unlocked_at
        )

    async def check_mood_streak(self, user_id: str, definition: AchievementDefinition,
                              db: Session) -> UserAchievementProgress:
        """Check consecutive mood logging streak"""
        
        # Get all mood entries 
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(desc(MoodEntry.created_at)).all()
        
        if not mood_entries:
            return UserAchievementProgress(definition.id)
            
        # Calculate current streak by checking unique days
        dates = set()
        for entry in mood_entries:
            dates.add(entry.created_at.date())
            
        sorted_dates = sorted(dates, reverse=True)
        current_streak = self._calculate_consecutive_days_from_dates(sorted_dates)
        
        progress = min(current_streak, definition.max_progress)
        is_unlocked = current_streak >= definition.max_progress
        
        unlocked_at = None
        if is_unlocked and len(sorted_dates) >= definition.max_progress:
            # Find unlock date - when they achieved the streak
            unlock_date = sorted_dates[definition.max_progress - 1]
            # Find first entry on that date
            first_entry_on_date = db.query(MoodEntry).filter(
                MoodEntry.user_id == user_id,
                func.date(MoodEntry.created_at) == unlock_date
            ).order_by(MoodEntry.created_at).first()
            if first_entry_on_date:
                unlocked_at = first_entry_on_date.created_at
            
        return UserAchievementProgress(
            definition.id,
            current_progress=progress,
            is_unlocked=is_unlocked,
            unlocked_at=unlocked_at,
            metadata={"current_streak": current_streak}
        )

    async def check_mood_milestone(self, user_id: str, definition: AchievementDefinition,
                                 db: Session) -> UserAchievementProgress:
        """Check total mood entry milestone"""
        mood_count = db.query(MoodEntry).filter(MoodEntry.user_id == user_id).count()
        
        progress = min(mood_count, definition.max_progress)
        is_unlocked = mood_count >= definition.max_progress
        
        unlocked_at = None
        if is_unlocked:
            # Find the milestone entry date
            milestone_entry = db.query(MoodEntry).filter(
                MoodEntry.user_id == user_id
            ).order_by(MoodEntry.created_at).offset(definition.max_progress - 1).first()
            if milestone_entry:
                unlocked_at = milestone_entry.created_at
                
        return UserAchievementProgress(
            definition.id,
            current_progress=progress,
            is_unlocked=is_unlocked, 
            unlocked_at=unlocked_at,
            metadata={"total_entries": mood_count}
        )

    async def check_positive_streak(self, user_id: str, definition: AchievementDefinition,
                                  db: Session) -> UserAchievementProgress:
        """Check streak of high mood scores (8+ out of 10)"""
        
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(desc(MoodEntry.created_at)).all()
        
        if not mood_entries:
            return UserAchievementProgress(definition.id)
            
        # Count consecutive positive moods (score >= 8) - convert to Python int
        positive_streak = 0
        max_positive_streak = 0
        
        for entry in mood_entries:
            mood_score = int(entry.mood_score) if entry.mood_score else 0
            if mood_score >= 8:
                positive_streak += 1
                max_positive_streak = max(max_positive_streak, positive_streak)
            else:
                positive_streak = 0
                
        progress = min(max_positive_streak, definition.max_progress)
        is_unlocked = max_positive_streak >= definition.max_progress
        
        return UserAchievementProgress(
            definition.id,
            current_progress=progress,
            is_unlocked=is_unlocked,
            metadata={
                "current_positive_streak": positive_streak,
                "max_positive_streak": max_positive_streak
            }
        )

    async def check_improvement_streak(self, user_id: str, definition: AchievementDefinition,
                                     db: Session) -> UserAchievementProgress:
        """Check improvement streak (mood score increasing day over day)"""
        
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(MoodEntry.created_at).all()
        
        if len(mood_entries) < 2:
            return UserAchievementProgress(definition.id)
            
        # Calculate improvement streaks - convert to Python int for comparison
        improvement_streak = 0
        max_improvement_streak = 0
        
        for i in range(1, len(mood_entries)):
            current_score = int(mood_entries[i].mood_score) if mood_entries[i].mood_score else 0
            prev_score = int(mood_entries[i-1].mood_score) if mood_entries[i-1].mood_score else 0
            
            if current_score > prev_score:
                improvement_streak += 1
                max_improvement_streak = max(max_improvement_streak, improvement_streak)
            else:
                improvement_streak = 0
                
        target_streak = definition.max_progress
        progress = min(max_improvement_streak, target_streak)
        is_unlocked = max_improvement_streak >= target_streak
        
        return UserAchievementProgress(
            definition.id,
            current_progress=progress,
            is_unlocked=is_unlocked,
            metadata={
                "current_improvement_streak": improvement_streak,
                "max_improvement_streak": max_improvement_streak
            }
        )

    async def check_consistency_streak(self, user_id: str, definition: AchievementDefinition,
                                     db: Session) -> UserAchievementProgress:
        """Check consistency in mood tracking"""
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(desc(MoodEntry.created_at)).all()
        
        if not mood_entries:
            return UserAchievementProgress(definition.id)
            
        # Get unique dates and calculate streak
        dates = set()
        for entry in mood_entries:
            dates.add(entry.created_at.date())
            
        sorted_dates = sorted(dates, reverse=True)
        current_streak = self._calculate_consecutive_days_from_dates(sorted_dates)
        
        target_streak = definition.max_progress
        progress = min(current_streak, target_streak)
        is_unlocked = current_streak >= target_streak
        
        return UserAchievementProgress(
            definition.id,
            current_progress=progress,
            is_unlocked=is_unlocked,
            metadata={"current_streak": current_streak}
        )

    async def check_celebration_collection(self, user_id: str, definition: AchievementDefinition,
                                         db: Session) -> UserAchievementProgress:
        """Check collection of achievements by level"""
        
        # Get target level from achievement ID
        target_level = definition.id.replace("_collector", "")
        
        # Count celebrations of this level
        celebration_count = db.query(CelebrationMoment).filter(
            and_(
                CelebrationMoment.user_id == user_id,
                CelebrationMoment.achievement_level == target_level
            )
        ).count()
        
        progress = min(celebration_count, definition.max_progress)
        is_unlocked = celebration_count >= definition.max_progress
        
        return UserAchievementProgress(
            definition.id,
            current_progress=progress,
            is_unlocked=is_unlocked,
            metadata={f"{target_level}_count": celebration_count}
        )

    # === HELPER METHODS ===
    
    def _calculate_consecutive_days_from_dates(self, sorted_dates: List[date]) -> int:
        """Calculate consecutive days from sorted date list"""
        if not sorted_dates:
            return 0
            
        streak = 1
        current_date = sorted_dates[0]
        
        for i in range(1, len(sorted_dates)):
            expected_date = current_date - timedelta(days=1)
            if sorted_dates[i] == expected_date:
                streak += 1
                current_date = sorted_dates[i]
            else:
                break
                
        return streak

    async def _get_celebration_stats(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get celebration statistics for user"""
        
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
            
            # Add recent achievements (within last 30 days)
            if celebration.created_at >= datetime.now() - timedelta(days=30):
                stats["recent_achievements"].append({
                    "title": celebration.title,
                    "level": celebration.achievement_level,
                    "date": celebration.created_at.strftime("%Y-%m-%d")
                })
        
        return stats

    async def trigger_achievement_check(self, user_id: str, trigger_event: str, 
                                      db: Session) -> List[Dict[str, Any]]:
        """Check for newly unlocked achievements after user actions"""
        
        new_achievements = []
        
        # Get current achievement state
        current_achievements = await self.get_user_achievements(user_id, db)
        
        # Check for newly unlocked achievements (within last 5 minutes)
        for achievement_id, achievement_data in current_achievements["achievements"].items():
            if (achievement_data["is_unlocked"] and 
                achievement_data["unlocked_at"] and
                datetime.fromisoformat(achievement_data["unlocked_at"]) >= datetime.now() - timedelta(minutes=5)):
                
                # This is a newly unlocked achievement
                achievement_def = self.achievement_definitions.get(achievement_id)
                if achievement_def and achievement_def.celebration_type:
                    
                    # Create celebration moment 
                    celebration = CelebrationMoment(
                        user_id=user_id,
                        celebration_type=achievement_def.celebration_type,
                        title=achievement_def.title,
                        message=achievement_def.description,
                        achievement_level=achievement_def.level,
                        reward_type="achievement_unlock",
                        reward_data={"achievement_id": achievement_id}
                    )
                    
                    db.add(celebration)
                    db.commit()
                    
                    new_achievements.append({
                        "id": achievement_id,
                        "title": achievement_def.title,
                        "description": achievement_def.description,
                        "level": achievement_def.level,
                        "icon": achievement_def.icon,
                        "celebration_id": celebration.id
                    })
        
        return new_achievements

# Global instance for use across the application
achievements_engine = AchievementsEngine()
