"""
Analytics Routes for Mood Service

Provides comprehensive analytics and insights for user wellbeing tracking:
- Weekly and monthly mood patterns
- Emotion trends and correlations
- Stress and energy level analysis
- Personalized recommendations
- Goal tracking and progress monitoring
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from shared.database import get_db
from shared.auth import get_current_user
from shared.models import MoodEntry, JournalEntry
from ..models.schemas import (
    AnalyticsOverview,
    WeeklyPattern,
    EmotionTrend,
    MoodInsight,
    WellbeingScore,
    AnalyticsResponse
)
from ..services.mood_data import MoodDataService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/mood/analytics", tags=["analytics"])

# Initialize services
mood_data_service = MoodDataService()


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d, 1y"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics overview for the user
    
    Provides:
    - Overall wellbeing score
    - Mood trend analysis
    - Key insights and patterns
    - Progress indicators
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"Fetching analytics overview for user {user_id}, period: {period}")
        
        # Calculate date range
        end_date = datetime.utcnow()
        days = _parse_period(period)
        start_date = end_date - timedelta(days=days)
        
        # Get mood entries for the period
        mood_entries = db.query(MoodEntry).filter(
            and_(
                MoodEntry.user_id == user_id,
                MoodEntry.created_at >= start_date,
                MoodEntry.created_at <= end_date
            )
        ).order_by(MoodEntry.created_at.desc()).all()
        
        if not mood_entries:
            return _get_empty_analytics_overview()
        
        # Calculate wellbeing score
        wellbeing_score = await _calculate_wellbeing_score(mood_entries, db, user_id)
        
        # Analyze mood trends
        mood_trends = await _analyze_mood_trends(mood_entries)
        
        # Generate insights
        insights = await _generate_analytics_insights(mood_entries, db, user_id)
        
        # Calculate comprehensive statistics
        mood_scores = [entry.mood_score for entry in mood_entries if entry.mood_score is not None]
        average_mood = sum(mood_scores) / len(mood_scores) if mood_scores else 0
        
        stress_levels = [entry.stress_level for entry in mood_entries if entry.stress_level is not None]
        average_stress = sum(stress_levels) / len(stress_levels) if stress_levels else 0
        
        energy_levels = [entry.energy_level for entry in mood_entries if entry.energy_level is not None]
        average_energy = sum(energy_levels) / len(energy_levels) if energy_levels else 0
        
        # Calculate improvement trend (compare first half vs second half)
        improvement_trend = _calculate_improvement_trend(mood_entries)
        
        # Calculate mood distribution
        mood_distribution = _calculate_mood_distribution(mood_scores)
        
        # Get recent patterns
        recent_patterns = _analyze_recent_patterns(mood_entries)
        
        # Calculate emotion distribution
        emotion_distribution = _calculate_emotion_distribution(mood_entries)
        
        # Calculate streaks
        current_streak, longest_streak = _calculate_mood_streaks(mood_entries)
        
        # Get last entry date
        last_entry_date = max(entry.created_at for entry in mood_entries) if mood_entries else None
        
        return {
            "period": period,
            "wellbeing_score": wellbeing_score.model_dump() if wellbeing_score else None,
            "total_entries": len(mood_entries),
            "average_mood": round(average_mood, 1),
            "average_stress": round(average_stress, 1),
            "average_energy": round(average_energy, 1),
            "mood_trend": mood_trends,
            "stress_average": round(average_stress, 1),
            "energy_average": round(average_energy, 1),
            "improvement_trend": improvement_trend,
            "mood_distribution": mood_distribution,
            "recent_patterns": recent_patterns,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "emotion_distribution": emotion_distribution,
            "last_entry_date": last_entry_date.isoformat() if last_entry_date else None,
            "insights": [insight.model_dump() if hasattr(insight, 'model_dump') else insight for insight in insights],
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching analytics overview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics overview")


@router.get("/patterns/weekly", response_model=List[WeeklyPattern])
async def get_weekly_patterns(
    weeks: int = Query(12, description="Number of weeks to analyze", ge=1, le=52),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weekly mood patterns and trends
    
    Analyzes:
    - Weekly mood averages
    - Day-of-week patterns
    - Consistency metrics
    - Trend identification
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"Fetching weekly patterns for user {user_id}, weeks: {weeks}")
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(weeks=weeks)
        
        # Get mood entries for the period
        mood_entries = db.query(MoodEntry).filter(
            and_(
                MoodEntry.user_id == user_id,
                MoodEntry.created_at >= start_date,
                MoodEntry.created_at <= end_date
            )
        ).order_by(MoodEntry.created_at.asc()).all()
        
        logger.info(f"Found {len(mood_entries)} mood entries for analysis")
        
        if not mood_entries:
            return []
        
        # Group entries by week
        weekly_data = {}
        for entry in mood_entries:
            try:
                # Get Monday of the week (ISO week)
                week_start = entry.created_at - timedelta(days=entry.created_at.weekday())
                week_key = week_start.date()
                
                if week_key not in weekly_data:
                    weekly_data[week_key] = []
                weekly_data[week_key].append(entry)
            except Exception as e:
                logger.warning(f"Error processing entry {entry.id}: {e}")
                continue
        
        # Calculate weekly patterns
        weekly_patterns = []
        for week_start, entries in sorted(weekly_data.items()):
            try:
                week_end = week_start + timedelta(days=6)
                
                # Calculate weekly statistics
                mood_scores = [e.mood_score for e in entries if e.mood_score is not None]
                stress_levels = [e.stress_level for e in entries if e.stress_level is not None]
                energy_levels = [e.energy_level for e in entries if e.energy_level is not None]
                
                if mood_scores:
                    avg_mood = sum(mood_scores) / len(mood_scores)
                    avg_stress = sum(stress_levels) / len(stress_levels) if stress_levels else 0
                    avg_energy = sum(energy_levels) / len(energy_levels) if energy_levels else 0
                    
                    # Analyze day-of-week patterns
                    daily_patterns = _analyze_daily_patterns(entries)
                    
                    # Calculate consistency (lower variance = more consistent)
                    mood_variance = _calculate_variance(mood_scores)
                    consistency_score = max(0, 10 - mood_variance)  # Scale 0-10
                    
                    # Get dominant emotions safely
                    dominant_emotions = _get_dominant_emotions_safe(entries)
                    
                    weekly_patterns.append(WeeklyPattern(
                        week_start=datetime.combine(week_start, datetime.min.time()),
                        week_end=datetime.combine(week_end, datetime.min.time()),
                        average_mood=round(avg_mood, 1),
                        average_stress=round(avg_stress, 1),
                        average_energy=round(avg_energy, 1),
                        entry_count=len(entries),
                        daily_patterns=daily_patterns,
                        consistency_score=round(consistency_score, 1),
                        dominant_emotions=dominant_emotions
                    ))
            except Exception as e:
                logger.warning(f"Error processing week {week_start}: {e}")
                continue
        
        return weekly_patterns[-weeks:]  # Return most recent weeks
        
    except Exception as e:
        logger.error(f"Error fetching weekly patterns: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch weekly patterns")


@router.get("/emotions/trends", response_model=List[EmotionTrend])
async def get_emotion_trends(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get emotion trends and patterns over time
    
    Analyzes:
    - Emotion frequency changes
    - Emotional patterns
    - Trigger identification
    - Emotional growth insights
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"Fetching emotion trends for user {user_id}, period: {period}")
        
        # Calculate date range
        end_date = datetime.utcnow()
        days = _parse_period(period)
        start_date = end_date - timedelta(days=days)
        
        # Get mood entries with emotion analysis
        mood_entries = db.query(MoodEntry).filter(
            and_(
                MoodEntry.user_id == user_id,
                MoodEntry.created_at >= start_date,
                MoodEntry.created_at <= end_date
            )
        ).order_by(MoodEntry.created_at.asc()).all()
        
        if not mood_entries:
            return []
        
        # Analyze emotion trends
        emotion_data = {}
        
        for entry in mood_entries:
            # Process emotions (use emotion_analysis field)
            import json
            try:
                emotions = None
                if hasattr(entry, 'emotion_analysis') and entry.emotion_analysis:
                    emotions = json.loads(entry.emotion_analysis) if isinstance(entry.emotion_analysis, str) else entry.emotion_analysis
                elif hasattr(entry, 'emotions') and entry.emotions:
                    emotions = json.loads(entry.emotions) if isinstance(entry.emotions, str) else entry.emotions
                
                if emotions and isinstance(emotions, dict):
                    # Handle different emotion data formats
                    emotion_dict = emotions
                    if 'emotions' in emotions:  # If wrapped in emotions key
                        emotion_dict = emotions['emotions']
                    elif 'top_emotions' in emotions:  # If it's analysis result format
                        emotion_dict = {item['emotion']: item.get('confidence', 0.5) for item in emotions['top_emotions']}
                    
                    for emotion, intensity in emotion_dict.items():
                        if emotion not in emotion_data:
                            emotion_data[emotion] = {
                                'values': [],
                                'dates': [],
                                'total_occurrences': 0,
                                'avg_intensity': 0
                            }
                        
                        emotion_data[emotion]['values'].append(float(intensity))
                        emotion_data[emotion]['dates'].append(entry.created_at)
                        emotion_data[emotion]['total_occurrences'] += 1
                    
            except (json.JSONDecodeError, TypeError, AttributeError) as e:
                logger.debug(f"Could not process emotions for entry {entry.id}: {e}")
                continue        # Calculate trends
        emotion_trends = []
        for emotion, data in emotion_data.items():
            if data['total_occurrences'] >= 3:  # Only include emotions with sufficient data
                values = data['values']
                avg_intensity = sum(values) / len(values)
                
                # Calculate trend direction (simple linear trend)
                trend_direction = _calculate_trend_direction(values)
                
                # Calculate frequency (occurrences per week)
                weeks_in_period = days / 7
                frequency = data['total_occurrences'] / weeks_in_period
                
                emotion_trends.append(EmotionTrend(
                    emotion=emotion,
                    average_intensity=round(avg_intensity, 2),
                    frequency=round(frequency, 1),
                    trend_direction=trend_direction,
                    total_occurrences=data['total_occurrences'],
                    first_occurrence=min(data['dates']),
                    last_occurrence=max(data['dates'])
                ))
        
        # Sort by average intensity descending
        emotion_trends.sort(key=lambda x: x.average_intensity, reverse=True)
        
        return emotion_trends[:20]  # Return top 20 emotions
        
    except Exception as e:
        logger.error(f"Error fetching emotion trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch emotion trends")


@router.get("/insights", response_model=List[MoodInsight])
async def get_personalized_insights(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized insights and recommendations
    
    Provides:
    - Pattern-based insights
    - Personalized recommendations
    - Goal suggestions
    - Wellness tips
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"Generating personalized insights for user {user_id}")
        
        # Get recent mood data (last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        mood_entries = db.query(MoodEntry).filter(
            and_(
                MoodEntry.user_id == user_id,
                MoodEntry.created_at >= start_date
            )
        ).order_by(MoodEntry.created_at.desc()).all()
        
        # Get journal entries for additional context
        journal_entries = db.query(JournalEntry).filter(
            and_(
                JournalEntry.user_id == user_id,
                JournalEntry.created_at >= start_date
            )
        ).all()
        
        insights = await _generate_personalized_insights(mood_entries, journal_entries, db, user_id)
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate insights")


@router.get("/wellbeing-score", response_model=WellbeingScore)
async def get_wellbeing_score(
    period: str = Query("7d", description="Time period: 7d, 30d, 90d"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate comprehensive wellbeing score
    
    Factors:
    - Mood consistency
    - Stress management
    - Energy levels
    - Emotional balance
    - Engagement metrics
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"Calculating wellbeing score for user {user_id}, period: {period}")
        
        # Calculate date range
        end_date = datetime.utcnow()
        days = _parse_period(period)
        start_date = end_date - timedelta(days=days)
        
        mood_entries = db.query(MoodEntry).filter(
            and_(
                MoodEntry.user_id == user_id,
                MoodEntry.created_at >= start_date
            )
        ).all()
        
        if not mood_entries:
            return WellbeingScore(
                score=0,
                category="insufficient_data",
                components={},
                recommendations=[],
                period=period,
                calculated_at=datetime.utcnow()
            )
        
        # Calculate wellbeing score components
        score_components = await _calculate_detailed_wellbeing_score(mood_entries, db, user_id)
        
        # Calculate overall score (weighted average)
        weights = {
            'mood_stability': 0.25,
            'stress_management': 0.20,
            'energy_levels': 0.20,
            'emotional_balance': 0.15,
            'consistency': 0.10,
            'engagement': 0.10
        }
        
        overall_score = sum(score_components[component] * weight 
                          for component, weight in weights.items() 
                          if component in score_components)
        
        # Determine category
        if overall_score >= 8.0:
            category = "excellent"
        elif overall_score >= 6.5:
            category = "good"
        elif overall_score >= 5.0:
            category = "moderate"
        elif overall_score >= 3.5:
            category = "needs_attention"
        else:
            category = "concerning"
        
        # Generate recommendations
        recommendations = _generate_wellbeing_recommendations(score_components, category)
        
        return WellbeingScore(
            score=round(overall_score, 1),
            category=category,
            components=score_components,
            recommendations=recommendations,
            period=period,
            calculated_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error calculating wellbeing score: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate wellbeing score")


# Helper Functions

def _parse_period(period: str) -> int:
    """Parse period string to number of days"""
    period_map = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
        "1y": 365
    }
    return period_map.get(period, 30)


def _get_empty_analytics_overview() -> AnalyticsOverview:
    """Return empty analytics overview for users with no data"""
    return AnalyticsOverview(
        period="30d",
        wellbeing_score=WellbeingScore(
            score=0,
            category="insufficient_data",
            components={},
            recommendations=[],
            period="30d",
            calculated_at=datetime.utcnow()
        ),
        total_entries=0,
        average_mood=0,
        average_stress=0,
        average_energy=0,
        mood_trend="stable",
        insights=[],
        last_updated=datetime.utcnow()
    )


async def _calculate_wellbeing_score(mood_entries: List[MoodEntry], db: Session, user_id: str) -> WellbeingScore:
    """Calculate basic wellbeing score"""
    if not mood_entries:
        return WellbeingScore(
            score=0,
            category="insufficient_data",
            components={},
            recommendations=[],
            period="30d",
            calculated_at=datetime.utcnow()
        )
    
    # Simple calculation for now
    mood_scores = [entry.mood_score for entry in mood_entries if entry.mood_score]
    avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else 5.0
    
    return WellbeingScore(
        score=round(avg_mood, 1),
        category="moderate" if avg_mood >= 5 else "needs_attention",
        components={"mood_average": round(avg_mood, 1)},
        recommendations=["Continue tracking your mood regularly"],
        period="30d",
        calculated_at=datetime.utcnow()
    )


async def _analyze_mood_trends(mood_entries: List[MoodEntry]) -> str:
    """Analyze mood trend direction"""
    if len(mood_entries) < 3:
        return "stable"
    
    mood_scores = [entry.mood_score for entry in mood_entries if entry.mood_score]
    if not mood_scores:
        return "stable"
    
    # Simple trend analysis
    first_half = mood_scores[:len(mood_scores)//2]
    second_half = mood_scores[len(mood_scores)//2:]
    
    avg_first = sum(first_half) / len(first_half)
    avg_second = sum(second_half) / len(second_half)
    
    diff = avg_second - avg_first
    
    if diff > 0.5:
        return "improving"
    elif diff < -0.5:
        return "declining"
    else:
        return "stable"


async def _generate_analytics_insights(mood_entries: List[MoodEntry], db: Session, user_id: str) -> List[MoodInsight]:
    """Generate basic analytics insights"""
    insights = []
    
    if not mood_entries:
        return insights
    
    # Entry frequency insight
    days_with_entries = len(set(entry.created_at.date() for entry in mood_entries))
    total_days = 30  # Assuming 30-day period
    frequency_rate = days_with_entries / total_days
    
    if frequency_rate >= 0.8:
        insights.append(MoodInsight(
            type="positive",
            title="Excellent Tracking Consistency",
            message=f"You've been consistently tracking your mood {days_with_entries} out of {total_days} days. Keep up the great work!",
            actionable=False,
            priority="low",
            generated_at=datetime.utcnow()
        ))
    elif frequency_rate < 0.3:
        insights.append(MoodInsight(
            type="suggestion",
            title="Improve Tracking Frequency",
            message="Regular mood tracking helps identify patterns. Try setting a daily reminder to track your mood.",
            actionable=True,
            priority="medium",
            generated_at=datetime.utcnow()
        ))
    
    return insights


def _analyze_daily_patterns(entries: List[MoodEntry]) -> Dict[str, float]:
    """Analyze mood patterns by day of week"""
    daily_data = {str(i): [] for i in range(7)}  # 0=Monday, 6=Sunday
    
    for entry in entries:
        day_of_week = str(entry.created_at.weekday())
        if entry.mood_score:
            daily_data[day_of_week].append(entry.mood_score)
    
    daily_patterns = {}
    for day, scores in daily_data.items():
        if scores:
            daily_patterns[day] = round(sum(scores) / len(scores), 1)
        else:
            daily_patterns[day] = 0
    
    return daily_patterns


def _calculate_variance(values: List[float]) -> float:
    """Calculate variance of values"""
    if len(values) < 2:
        return 0
    
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance


def _get_dominant_emotions_safe(entries: List[MoodEntry]) -> List[str]:
    """Get dominant emotions for entries with safe error handling"""
    try:
        return _get_dominant_emotions(entries)
    except Exception as e:
        logger.debug(f"Error getting dominant emotions: {e}")
        # Fallback to primary emotions if available
        primary_emotions = []
        for entry in entries:
            if hasattr(entry, 'primary_emotion') and entry.primary_emotion:
                primary_emotions.append(entry.primary_emotion)
        
        if primary_emotions:
            # Return most common primary emotions
            from collections import Counter
            emotion_counts = Counter(primary_emotions)
            return [emotion for emotion, count in emotion_counts.most_common(3)]
        
        return []  # Return empty list if no emotions available

def _get_dominant_emotions(entries: List[MoodEntry]) -> List[str]:
    """Get dominant emotions for entries"""
    emotion_counts = {}
    
    for entry in entries:
        emotions = None
        if hasattr(entry, 'emotion_analysis') and entry.emotion_analysis:
            try:
                import json
                emotions = json.loads(entry.emotion_analysis) if isinstance(entry.emotion_analysis, str) else entry.emotion_analysis
            except (json.JSONDecodeError, TypeError):
                continue
        elif hasattr(entry, 'primary_emotion') and entry.primary_emotion:
            # Use primary emotion as fallback
            emotion_counts[entry.primary_emotion] = emotion_counts.get(entry.primary_emotion, 0) + 1
            continue
            
        if emotions and isinstance(emotions, dict):
            # Handle different emotion data formats
            emotion_dict = emotions
            if 'emotions' in emotions:
                emotion_dict = emotions['emotions']
            elif 'top_emotions' in emotions:
                emotion_dict = {item['emotion']: item.get('confidence', 0.5) for item in emotions['top_emotions']}
            
            for emotion, intensity in emotion_dict.items():
                if float(intensity) > 0.3:  # Only significant emotions
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    # Return top 3 emotions
    sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
    return [emotion for emotion, count in sorted_emotions[:3]]


def _calculate_trend_direction(values: List[float]) -> str:
    """Calculate trend direction from values"""
    if len(values) < 3:
        return "stable"
    
    # Simple linear trend
    first_third = sum(values[:len(values)//3]) / (len(values)//3)
    last_third = sum(values[-len(values)//3:]) / (len(values)//3)
    
    diff = last_third - first_third
    
    if diff > 0.1:
        return "increasing"
    elif diff < -0.1:
        return "decreasing"
    else:
        return "stable"


async def _generate_personalized_insights(
    mood_entries: List[MoodEntry], 
    journal_entries: List[JournalEntry], 
    db: Session, 
    user_id: str
) -> List[MoodInsight]:
    """Generate personalized insights based on user data"""
    insights = []
    
    # More sophisticated insights would be implemented here
    # For now, return basic insights
    
    if mood_entries:
        recent_mood = mood_entries[0].mood_score if mood_entries[0].mood_score else 5
        
        if recent_mood >= 8:
            insights.append(MoodInsight(
                type="positive",
                title="Great Mood Today!",
                message="Your recent mood scores show you're doing well. Consider what's working and try to maintain these positive patterns.",
                actionable=True,
                priority="low",
                generated_at=datetime.utcnow()
            ))
    
    return insights


async def _calculate_detailed_wellbeing_score(
    mood_entries: List[MoodEntry], 
    db: Session, 
    user_id: str
) -> Dict[str, float]:
    """Calculate detailed wellbeing score components"""
    components = {}
    
    if not mood_entries:
        return components
    
    # Mood stability (consistency)
    mood_scores = [entry.mood_score for entry in mood_entries if entry.mood_score]
    if mood_scores:
        variance = _calculate_variance(mood_scores)
        stability_score = max(0, 10 - variance)  # Higher variance = lower stability
        components["mood_stability"] = min(10, stability_score)
    
    # Stress management
    stress_levels = [entry.stress_level for entry in mood_entries if entry.stress_level]
    if stress_levels:
        avg_stress = sum(stress_levels) / len(stress_levels)
        stress_score = max(0, 10 - avg_stress)  # Lower stress = higher score
        components["stress_management"] = stress_score
    
    # Energy levels
    energy_levels = [entry.energy_level for entry in mood_entries if entry.energy_level]
    if energy_levels:
        avg_energy = sum(energy_levels) / len(energy_levels)
        components["energy_levels"] = avg_energy
    
    # Add other components as needed
    components["engagement"] = min(10, len(mood_entries) / 3)  # Engagement based on entry frequency
    
    return components


def _generate_wellbeing_recommendations(components: Dict[str, float], category: str) -> List[str]:
    """Generate wellbeing recommendations based on scores"""
    recommendations = []
    
    if category == "concerning":
        recommendations.append("Consider speaking with a mental health professional")
        recommendations.append("Focus on basic self-care: sleep, nutrition, and gentle exercise")
    elif category == "needs_attention":
        recommendations.append("Try incorporating stress-reduction techniques like deep breathing or meditation")
        recommendations.append("Maintain regular mood tracking to identify patterns")
    elif category == "moderate":
        recommendations.append("You're doing well! Consider setting specific wellness goals")
        recommendations.append("Explore new activities that bring you joy")
    else:  # good or excellent
        recommendations.append("Great work! Consider helping others or sharing your wellness strategies")
        recommendations.append("Continue your current positive practices")
    
    return recommendations


def _calculate_improvement_trend(mood_entries: List[MoodEntry]) -> float:
    """Calculate improvement trend by comparing first half to second half of entries."""
    if len(mood_entries) < 4:
        return 0.0
    
    # Sort by date
    sorted_entries = sorted(mood_entries, key=lambda x: x.created_at)
    
    mid_point = len(sorted_entries) // 2
    first_half = sorted_entries[:mid_point]
    second_half = sorted_entries[mid_point:]
    
    # Calculate average mood scores for each half
    first_half_scores = [entry.mood_score for entry in first_half if entry.mood_score is not None]
    second_half_scores = [entry.mood_score for entry in second_half if entry.mood_score is not None]
    
    if not first_half_scores or not second_half_scores:
        return 0.0
    
    first_avg = sum(first_half_scores) / len(first_half_scores)
    second_avg = sum(second_half_scores) / len(second_half_scores)
    
    # Return percentage improvement
    improvement = ((second_avg - first_avg) / first_avg) * 100 if first_avg != 0 else 0
    return round(improvement, 1)


def _calculate_mood_distribution(mood_scores: List[float]) -> dict:
    """Calculate distribution of mood scores."""
    if not mood_scores:
        return {}
    
    distribution = {
        "very_low": 0,    # 1-1.5
        "low": 0,         # 1.5-2.5
        "neutral": 0,     # 2.5-3.5
        "good": 0,        # 3.5-4.5
        "excellent": 0    # 4.5-5
    }
    
    for score in mood_scores:
        if score <= 1.5:
            distribution["very_low"] += 1
        elif score <= 2.5:
            distribution["low"] += 1
        elif score <= 3.5:
            distribution["neutral"] += 1
        elif score <= 4.5:
            distribution["good"] += 1
        else:
            distribution["excellent"] += 1
    
    # Convert to percentages
    total = len(mood_scores)
    return {key: round((count / total) * 100, 1) for key, count in distribution.items()}


def _analyze_recent_patterns(mood_entries: List[MoodEntry]) -> List[str]:
    """Analyze recent patterns in mood data."""
    if not mood_entries:
        return []
    
    patterns = []
    recent_entries = sorted(mood_entries, key=lambda x: x.created_at, reverse=True)[:7]  # Last 7 entries
    
    # Check for consistent good mood
    recent_scores = [entry.mood_score for entry in recent_entries if entry.mood_score is not None]
    if len(recent_scores) >= 3:
        if all(score >= 4.0 for score in recent_scores[-3:]):
            patterns.append("Consistently high mood in recent entries")
        elif all(score <= 2.0 for score in recent_scores[-3:]):
            patterns.append("Concerning pattern: low mood persisting")
    
    # Check stress patterns
    recent_stress = [entry.stress_level for entry in recent_entries if entry.stress_level is not None]
    if len(recent_stress) >= 3:
        if all(stress >= 4.0 for stress in recent_stress[-3:]):
            patterns.append("High stress levels detected recently")
        elif all(stress <= 2.0 for stress in recent_stress[-3:]):
            patterns.append("Low stress levels - good progress")
    
    # Check weekend vs weekday patterns
    weekend_scores = []
    weekday_scores = []
    
    for entry in recent_entries:
        if entry.mood_score is not None:
            weekday = entry.created_at.weekday()  # 0=Monday, 6=Sunday
            if weekday >= 5:  # Saturday or Sunday
                weekend_scores.append(entry.mood_score)
            else:
                weekday_scores.append(entry.mood_score)
    
    if weekend_scores and weekday_scores:
        weekend_avg = sum(weekend_scores) / len(weekend_scores)
        weekday_avg = sum(weekday_scores) / len(weekday_scores)
        
        if weekend_avg > weekday_avg + 0.5:
            patterns.append("Mood tends to be better on weekends")
        elif weekday_avg > weekend_avg + 0.5:
            patterns.append("Mood tends to be better on weekdays")
    
    return patterns[:3]  # Return top 3 patterns


def _calculate_emotion_distribution(mood_entries: List[MoodEntry]) -> dict:
    """Calculate distribution of emotions from emotion analysis."""
    if not mood_entries:
        return {}
    
    emotion_counts = {}
    
    for entry in mood_entries:
        if entry.emotion_analysis:
            # Parse emotion analysis (assuming it's JSON or comma-separated emotions)
            try:
                if isinstance(entry.emotion_analysis, str):
                    # Try parsing as JSON first
                    try:
                        import json
                        emotions_data = json.loads(entry.emotion_analysis)
                        if isinstance(emotions_data, dict):
                            for emotion, intensity in emotions_data.items():
                                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + intensity
                        elif isinstance(emotions_data, list):
                            for emotion in emotions_data:
                                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                    except:
                        # Fallback: treat as comma-separated
                        emotions = [e.strip().lower() for e in entry.emotion_analysis.split(',')]
                        for emotion in emotions:
                            if emotion:
                                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            except Exception:
                continue
    
    # Normalize to percentages
    if emotion_counts:
        total = sum(emotion_counts.values())
        return {emotion: round((count / total) * 100, 1) 
                for emotion, count in emotion_counts.items()}
    
    return {}


def _calculate_mood_streaks(mood_entries: List[MoodEntry]) -> tuple:
    """Calculate current and longest streaks of good mood (>= 3.5)."""
    if not mood_entries:
        return 0, 0
    
    sorted_entries = sorted(mood_entries, key=lambda x: x.created_at)
    mood_scores = [entry.mood_score for entry in sorted_entries if entry.mood_score is not None]
    
    if not mood_scores:
        return 0, 0
    
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    
    # Calculate streaks (good mood = >= 3.5)
    for score in reversed(mood_scores):  # Start from most recent
        if score >= 3.5:
            if current_streak == temp_streak:  # Still building current streak
                current_streak += 1
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            if current_streak == temp_streak:  # Current streak broken
                current_streak = 0
            temp_streak = 0
    
    return current_streak, longest_streak


@router.get("/emotional-weather", response_model=Dict[str, Any])
async def get_emotional_weather(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the user's current emotional weather forecast
    
    Provides:
    - Current emotional state summary
    - Mood forecast for today/tomorrow
    - Weather metaphor representation
    - Personalized emotional insights
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"Fetching emotional weather for user {user_id}")
        
        # Get recent mood entries (last 7 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        recent_entries = db.query(MoodEntry).filter(
            and_(
                MoodEntry.user_id == user_id,
                MoodEntry.created_at >= start_date,
                MoodEntry.created_at <= end_date
            )
        ).order_by(MoodEntry.created_at.desc()).limit(10).all()
        
        if not recent_entries:
            return {
                "weather_type": "unknown",
                "description": "Not enough data to determine emotional weather",
                "mood_forecast": "uncertain",
                "current_temperature": 0,
                "outlook": "Start tracking your moods to see your emotional weather!",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Calculate current emotional state
        latest_entry = recent_entries[0]
        mood_scores = [entry.mood_score for entry in recent_entries if entry.mood_score is not None]
        avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else 3.0
        
        stress_levels = [entry.stress_level for entry in recent_entries if entry.stress_level is not None]
        avg_stress = sum(stress_levels) / len(stress_levels) if stress_levels else 3.0
        
        energy_levels = [entry.energy_level for entry in recent_entries if entry.energy_level is not None]
        avg_energy = sum(energy_levels) / len(energy_levels) if energy_levels else 3.0
        
        # Determine weather type based on mood and stress
        weather_type = _determine_weather_type(avg_mood, avg_stress, avg_energy)
        description = _get_weather_description(weather_type, avg_mood, avg_stress)
        
        # Calculate mood forecast trend
        if len(mood_scores) >= 3:
            recent_trend = (mood_scores[0] + mood_scores[1]) / 2 - (mood_scores[-2] + mood_scores[-1]) / 2
            if recent_trend > 0.5:
                forecast = "improving"
            elif recent_trend < -0.5:
                forecast = "declining"
            else:
                forecast = "stable"
        else:
            forecast = "stable"
        
        # Generate outlook message
        outlook = _generate_weather_outlook(weather_type, forecast, avg_mood, avg_stress)
        
        # Calculate emotional temperature (0-100 scale)
        emotional_temp = int(((avg_mood - 1) / 4) * 100)
        
        return {
            "weather_type": weather_type,
            "description": description,
            "mood_forecast": forecast,
            "current_temperature": emotional_temp,
            "outlook": outlook,
            "metrics": {
                "average_mood": round(avg_mood, 1),
                "average_stress": round(avg_stress, 1),
                "average_energy": round(avg_energy, 1),
                "entries_analyzed": len(recent_entries)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching emotional weather: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch emotional weather")


def _determine_weather_type(mood: float, stress: float, energy: float) -> str:
    """Determine weather type based on mood, stress, and energy levels."""
    if mood >= 4.0 and stress <= 2.5 and energy >= 3.5:
        return "sunny"
    elif mood >= 3.5 and stress <= 3.0:
        return "partly-cloudy"
    elif mood <= 2.5 and stress >= 3.5:
        return "stormy"
    elif mood <= 3.0 and energy <= 2.5:
        return "cloudy"
    elif stress >= 4.0:
        return "turbulent"
    else:
        return "overcast"


def _get_weather_description(weather_type: str, mood: float, stress: float) -> str:
    """Get descriptive text for the weather type."""
    descriptions = {
        "sunny": f"Bright and positive! Your mood is shining at {mood:.1f}/5 with low stress levels.",
        "partly-cloudy": f"Generally good with some mixed feelings. Mood: {mood:.1f}/5.",
        "cloudy": f"Feeling a bit low with mood at {mood:.1f}/5. Some emotional clouds are present.",
        "overcast": f"Heavy emotional atmosphere with mood at {mood:.1f}/5 and stress at {stress:.1f}/5.",
        "stormy": f"Challenging times with low mood ({mood:.1f}/5) and high stress ({stress:.1f}/5).",
        "turbulent": f"High stress levels ({stress:.1f}/5) are creating emotional turbulence."
    }
    return descriptions.get(weather_type, "Mixed emotional conditions.")


def _generate_weather_outlook(weather_type: str, forecast: str, mood: float, stress: float) -> str:
    """Generate personalized outlook message."""
    if weather_type == "sunny":
        if forecast == "improving":
            return "Your emotional sunshine is getting even brighter! Keep up the positive momentum."
        else:
            return "Beautiful emotional weather continues. Enjoy this positive phase!"
    
    elif weather_type == "stormy":
        if forecast == "improving":
            return "The storm clouds are clearing. Better emotional weather ahead!"
        else:
            return "Riding through some rough emotional weather. Consider self-care activities."
    
    elif weather_type == "cloudy":
        if forecast == "improving":
            return "The clouds are starting to part. Brighter emotional days are coming."
        else:
            return "Some emotional clouds present. A good time for gentle activities and self-compassion."
    
    else:  # partly-cloudy, overcast, turbulent
        if forecast == "improving":
            return "Your emotional weather is shifting toward clearer skies."
        elif forecast == "declining":
            return "Some emotional weather changes ahead. Stay mindful of your wellbeing."
        else:
            return "Steady emotional conditions. A good time to maintain your current wellness practices."