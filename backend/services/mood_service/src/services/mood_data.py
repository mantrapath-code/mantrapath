"""Mood data management service."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from shared.models import MoodEntry as MoodEntryModel
from src.models.database import MoodPatternModel, MoodContextModel
from src.models.schemas import (
    MoodCreateRequest, 
    MoodEntryResponse, 
    MoodAnalyticsOverview,
    MoodPatternsResponse,
    WeeklyPattern
)
from src.services.emotion_analysis import emotion_service

logger = logging.getLogger(__name__)


class MoodDataService:
    """Service for managing mood data operations."""
    
    def _mood_entry_to_response(self, mood_entry: MoodEntryModel) -> MoodEntryResponse:
        """Convert mood entry model to response format, mapping notes to description."""
        return MoodEntryResponse(
            id=mood_entry.id,
            user_id=mood_entry.user_id,
            input_text=mood_entry.description or "",  # Map description to input_text
            input_type="text",
            mood_score=mood_entry.mood_score,
            description=mood_entry.description,
            stress_level=mood_entry.stress_level,
            energy_level=mood_entry.energy_level,
            primary_emotion=mood_entry.primary_emotion,
            primary_sentiment=mood_entry.primary_sentiment,
            emotion_analysis=mood_entry.emotion_analysis,
            context_tags=mood_entry.context_tags,
            location=mood_entry.location,
            activity=mood_entry.activity,
            created_at=mood_entry.created_at,
            updated_at=mood_entry.updated_at
        )
    
    async def create_mood_entry(
        self, 
        db: Session, 
        user_id: str, 
        mood_data: MoodCreateRequest,
        emotion_analysis: Optional[Dict[str, Any]] = None
    ) -> MoodEntryResponse:
        """
        Create a new mood entry for a user.
        
        Args:
            db: Database session
            user_id: User identifier
            mood_data: Mood entry data
            emotion_analysis: Optional emotion analysis results
            
        Returns:
            Created mood entry
        """
        try:
            # Handle both legacy and new formats
            description = mood_data.description
            if not description and mood_data.notes:
                description = mood_data.notes
            if not description and mood_data.input_text:
                description = mood_data.input_text
            
            # Create mood entry
            mood_entry = MoodEntryModel(
                user_id=user_id,
                mood_score=mood_data.mood_score or 5,  # Default neutral mood
                description=description,
                stress_level=mood_data.stress_level or 5,
                energy_level=mood_data.energy_level or 5,
                context_tags=mood_data.context_tags,
                location=mood_data.location,
                activity=mood_data.activity
            )
            
            # Add emotion analysis if provided
            if emotion_analysis:
                mood_entry.primary_emotion = emotion_analysis.get("primary_emotion")
                mood_entry.primary_sentiment = emotion_analysis.get("primary_sentiment")
                mood_entry.emotion_analysis = emotion_analysis
            
            db.add(mood_entry)
            db.commit()
            db.refresh(mood_entry)
            
            logger.info(f"Created mood entry {mood_entry.id} for user {user_id}")
            
            return self._mood_entry_to_response(mood_entry)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create mood entry for user {user_id}: {e}")
            raise
    
    async def get_user_mood_entries(
        self, 
        db: Session, 
        user_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> List[MoodEntryResponse]:
        """
        Get mood entries for a user.
        
        Args:
            db: Database session
            user_id: User identifier
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            
        Returns:
            List of mood entries
        """
        try:
            entries = (
                db.query(MoodEntryModel)
                .filter(MoodEntryModel.user_id == user_id)
                .order_by(desc(MoodEntryModel.created_at))
                .offset(offset)
                .limit(limit)
                .all()
            )
            
            return [self._mood_entry_to_response(entry) for entry in entries]
            
        except Exception as e:
            logger.error(f"Failed to get mood entries for user {user_id}: {e}")
            raise
    
    async def get_mood_analytics_overview(
        self, 
        db: Session, 
        user_id: str
    ) -> MoodAnalyticsOverview:
        """
        Get analytics overview for a user's mood data.
        
        Args:
            db: Database session
            user_id: User identifier
            
        Returns:
            Analytics overview
        """
        try:
            # Get all entries for the user
            entries = (
                db.query(MoodEntryModel)
                .filter(MoodEntryModel.user_id == user_id)
                .order_by(MoodEntryModel.created_at.asc())
                .all()
            )
            
            if not entries:
                return MoodAnalyticsOverview(
                    total_entries=0,
                    average_mood=0.0,
                    mood_trend="stable",
                    stress_average=None,
                    energy_average=None,
                    mood_distribution={},
                    recent_patterns=[],
                    current_streak=0,
                    longest_streak=0,
                    emotion_distribution={},
                    improvement_trend=0.0
                )
            
            # Calculate basic statistics
            total_entries = len(entries)
            average_mood = sum(e.mood_score for e in entries) / total_entries
            
            # Calculate mood distribution by ranges
            mood_distribution = {}
            for entry in entries:
                score = entry.mood_score
                if score <= 3:
                    range_key = "Low (1-3)"
                elif score <= 5:
                    range_key = "Below Average (4-5)"
                elif score <= 7:
                    range_key = "Good (6-7)"
                else:
                    range_key = "Excellent (8-10)"
                
                mood_distribution[range_key] = mood_distribution.get(range_key, 0) + 1
            
            # Calculate emotion distribution
            emotion_distribution = {}
            for entry in entries:
                if entry.primary_emotion:
                    emotion = entry.primary_emotion
                    emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1
            
            # Calculate streaks (consecutive days with entries)
            current_streak, longest_streak = self._calculate_streaks(entries)
            
            # Calculate improvement trend (last 7 days vs previous 7 days)
            improvement_trend = self._calculate_improvement_trend(entries)
            
            # Convert trend to string format
            if improvement_trend > 0.2:
                mood_trend = "improving"
            elif improvement_trend < -0.2:
                mood_trend = "declining"
            else:
                mood_trend = "stable"
                
            # Calculate stress and energy averages
            stress_scores = [e.stress_level for e in entries if e.stress_level is not None]
            energy_scores = [e.energy_level for e in entries if e.energy_level is not None]

            return MoodAnalyticsOverview(
                total_entries=total_entries,
                average_mood=round(average_mood, 2),
                mood_trend=mood_trend,
                stress_average=round(sum(stress_scores) / len(stress_scores), 2) if stress_scores else None,
                energy_average=round(sum(energy_scores) / len(energy_scores), 2) if energy_scores else None,
                mood_distribution=mood_distribution,
                recent_patterns=[],
                current_streak=current_streak,
                longest_streak=longest_streak,
                emotion_distribution=emotion_distribution,
                last_entry_date=entries[-1].created_at if entries else None,
                improvement_trend=improvement_trend
            )
            
        except Exception as e:
            logger.error(f"Failed to get analytics overview for user {user_id}: {e}")
            raise
    
    def _calculate_streaks(self, entries: List[MoodEntryModel]) -> tuple[int, int]:
        """Calculate current and longest streaks."""
        if not entries:
            return 0, 0
        
        # Group entries by date
        dates = set()
        for entry in entries:
            dates.add(entry.created_at.date())
        
        sorted_dates = sorted(dates)
        
        # Calculate current streak
        current_streak = 0
        today = datetime.utcnow().date()
        current_date = today
        
        while current_date in dates:
            current_streak += 1
            current_date -= timedelta(days=1)
        
        # Calculate longest streak
        longest_streak = 0
        current_run = 1
        
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                current_run += 1
            else:
                longest_streak = max(longest_streak, current_run)
                current_run = 1
        
        longest_streak = max(longest_streak, current_run)
        
        return current_streak, longest_streak
    
    def _calculate_improvement_trend(self, entries: List[MoodEntryModel]) -> float:
        """Calculate mood improvement trend."""
        if len(entries) < 2:
            return 0.0
        
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)
        
        # Get recent entries (last 7 days)
        recent_entries = [
            e for e in entries 
            if e.created_at >= week_ago
        ]
        
        # Get previous entries (7-14 days ago)
        previous_entries = [
            e for e in entries 
            if two_weeks_ago <= e.created_at < week_ago
        ]
        
        if not recent_entries or not previous_entries:
            return 0.0
        
        recent_avg = sum(e.mood_score for e in recent_entries) / len(recent_entries)
        previous_avg = sum(e.mood_score for e in previous_entries) / len(previous_entries)
        
        # Normalize to -1 to 1 scale
        trend = (recent_avg - previous_avg) / 10.0
        return max(-1.0, min(1.0, trend))
    
    async def get_weekly_patterns(
        self, 
        db: Session, 
        user_id: str
    ) -> MoodPatternsResponse:
        """
        Get weekly mood patterns for a user.
        
        Args:
            db: Database session
            user_id: User identifier
            
        Returns:
            Weekly patterns analysis
        """
        try:
            # Get entries from last 12 weeks
            twelve_weeks_ago = datetime.utcnow() - timedelta(weeks=12)
            entries = (
                db.query(MoodEntryModel)
                .filter(
                    and_(
                        MoodEntryModel.user_id == user_id,
                        MoodEntryModel.created_at >= twelve_weeks_ago
                    )
                )
                .order_by(MoodEntryModel.created_at.asc())
                .all()
            )
            
            if not entries:
                return MoodPatternsResponse(
                    weekly_patterns=[],
                    insights=[],
                    recommendations=[],
                    trend_analysis={}
                )
            
            # Group by week
            weekly_data = {}
            for entry in entries:
                year, week_num, _ = entry.created_at.isocalendar()
                week_key = f"{year}-W{week_num:02d}"
                
                if week_key not in weekly_data:
                    weekly_data[week_key] = {
                        'scores': [],
                        'emotions': [],
                        'count': 0
                    }
                
                weekly_data[week_key]['scores'].append(entry.mood_score)
                weekly_data[week_key]['count'] += 1
                if entry.primary_emotion:
                    weekly_data[week_key]['emotions'].append(entry.primary_emotion)
            
            # Create weekly patterns
            weekly_patterns = []
            for week, data in weekly_data.items():
                avg_mood = sum(data['scores']) / len(data['scores'])
                
                # Find dominant emotion
                dominant_emotion = None
                if data['emotions']:
                    emotion_counts = {}
                    for emotion in data['emotions']:
                        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                    dominant_emotion = max(emotion_counts, key=emotion_counts.get)
                
                pattern = WeeklyPattern(
                    week=week,
                    average_mood=round(avg_mood, 2),
                    dominant_emotion=dominant_emotion,
                    entry_count=data['count']
                )
                weekly_patterns.append(pattern)
            
            # Sort by week
            weekly_patterns.sort(key=lambda x: x.week)
            
            # Generate insights and recommendations
            insights = self._generate_insights(weekly_patterns)
            recommendations = self._generate_recommendations(weekly_patterns)
            trend_analysis = self._analyze_trends(weekly_patterns)
            
            return MoodPatternsResponse(
                weekly_patterns=weekly_patterns,
                insights=insights,
                recommendations=recommendations,
                trend_analysis=trend_analysis
            )
            
        except Exception as e:
            logger.error(f"Failed to get weekly patterns for user {user_id}: {e}")
            raise
    
    def _generate_insights(self, patterns: List[WeeklyPattern]) -> List[Dict[str, Any]]:
        """Generate insights from weekly patterns."""
        insights = []
        
        if len(patterns) < 2:
            return insights
        
        # Trend analysis
        recent_avg = sum(p.average_mood for p in patterns[-4:]) / min(4, len(patterns))
        overall_avg = sum(p.average_mood for p in patterns) / len(patterns)
        
        if recent_avg > overall_avg + 0.5:
            insights.append({
                "type": "positive_trend",
                "severity": "low",
                "message": "Your mood has been improving recently",
                "data": {"recent_average": recent_avg, "overall_average": overall_avg}
            })
        elif recent_avg < overall_avg - 0.5:
            insights.append({
                "type": "concerning_trend",
                "severity": "moderate",
                "message": "Your mood has been declining recently",
                "data": {"recent_average": recent_avg, "overall_average": overall_avg}
            })
        
        # Consistency analysis
        mood_variance = sum((p.average_mood - overall_avg) ** 2 for p in patterns) / len(patterns)
        if mood_variance < 0.5:
            insights.append({
                "type": "stability",
                "severity": "low",
                "message": "Your mood has been relatively stable",
                "data": {"variance": mood_variance}
            })
        elif mood_variance > 2.0:
            insights.append({
                "type": "volatility",
                "severity": "moderate", 
                "message": "Your mood shows significant fluctuations",
                "data": {"variance": mood_variance}
            })
        
        return insights
    
    def _generate_recommendations(self, patterns: List[WeeklyPattern]) -> List[Dict[str, Any]]:
        """Generate recommendations based on patterns."""
        recommendations = []
        
        if not patterns:
            return recommendations
        
        recent_avg = sum(p.average_mood for p in patterns[-2:]) / min(2, len(patterns))
        
        if recent_avg < 4.0:
            recommendations.append({
                "type": "mood_improvement",
                "priority": "high",
                "title": "Focus on Mood Enhancement",
                "description": "Consider engaging in activities that typically boost your mood",
                "actions": [
                    "Practice mindfulness or meditation",
                    "Engage in physical exercise",
                    "Connect with supportive friends or family",
                    "Consider professional support if needed"
                ]
            })
        
        # Check for consistent patterns
        emotions = [p.dominant_emotion for p in patterns[-4:] if p.dominant_emotion]
        if emotions and len(set(emotions)) == 1:
            dominant = emotions[0]
            if dominant in ['sadness', 'fear', 'anger']:
                recommendations.append({
                    "type": "emotion_pattern",
                    "priority": "medium",
                    "title": f"Address Recurring {dominant.title()}",
                    "description": f"You've been experiencing {dominant} frequently",
                    "actions": [
                        "Identify triggers for this emotion",
                        "Develop coping strategies",
                        "Consider journaling about these feelings"
                    ]
                })
        
        return recommendations
    
    def _analyze_trends(self, patterns: List[WeeklyPattern]) -> Dict[str, Any]:
        """Analyze trends in weekly patterns."""
        if len(patterns) < 3:
            return {}
        
        # Calculate trend line slope
        x_values = list(range(len(patterns)))
        y_values = [p.average_mood for p in patterns]
        
        # Simple linear regression
        n = len(patterns)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        else:
            slope = 0
        
        trend_direction = "improving" if slope > 0.1 else "declining" if slope < -0.1 else "stable"
        
        return {
            "slope": slope,
            "direction": trend_direction,
            "strength": abs(slope),
            "recent_weeks": len(patterns),
            "current_trend": trend_direction
        }


# Global mood data service instance
mood_data_service = MoodDataService()