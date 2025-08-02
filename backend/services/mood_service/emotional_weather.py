"""
Emotional Weather System - Phase 1 Enhancement
Provides predictive emotional insights using mood patterns and environmental context
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import statistics

# Import shared models
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from shared.models import MoodEntry, EmotionalWeatherForecast, EnvironmentalData
from shared.database import get_db

class WeatherRecommendation:
    """Structure for weather-based recommendations"""
    def __init__(self, recommendation_id: str, text: str, priority: str = "normal", 
                 action_type: str = "suggestion"):
        self.id = recommendation_id
        self.text = text
        self.priority = priority  # low, normal, high, urgent
        self.action_type = action_type  # suggestion, reminder, intervention

class EmotionalWeatherEngine:
    """Service for generating emotional weather forecasts and insights"""
    
    def __init__(self):
        self.weather_patterns = self._load_weather_patterns()
        
    def _load_weather_patterns(self) -> Dict[str, Any]:
        """Load weather pattern templates and thresholds"""
        return {
            "mood_ranges": {
                "sunny": (8, 10),      # High mood range
                "partly_cloudy": (6, 7.9),  # Moderate-high mood
                "cloudy": (4, 5.9),    # Moderate mood  
                "overcast": (2, 3.9),  # Low mood
                "stormy": (1, 1.9)     # Very low mood
            },
            "risk_factors": {
                "monday_blues": {
                    "condition": lambda day: day == 0,  # Monday
                    "description": "Monday transition stress",
                    "impact": 0.7
                },
                "weekend_anxiety": {
                    "condition": lambda day: day == 6,  # Sunday
                    "description": "Sunday evening anxiety",
                    "impact": 0.6
                },
                "late_night_vulnerability": {
                    "condition": lambda hour: hour >= 22 or hour <= 5,
                    "description": "Late night emotional vulnerability",
                    "impact": 0.8
                },
                "stress_accumulation": {
                    "condition": lambda stress_trend: stress_trend > 0.5,
                    "description": "Building stress levels",
                    "impact": 0.9
                }
            },
            "protective_factors": {
                "morning_energy": {
                    "condition": lambda hour, energy: 6 <= hour <= 10 and energy >= 7,
                    "description": "Morning high-energy period",
                    "boost": 0.6
                },
                "weekend_relief": {
                    "condition": lambda day: day >= 5,
                    "description": "Weekend relaxation opportunity",
                    "boost": 0.4
                },
                "positive_streak": {
                    "condition": lambda streak: streak >= 3,
                    "description": "Positive mood momentum",
                    "boost": 0.8
                },
                "consistent_tracking": {
                    "condition": lambda tracking_days: tracking_days >= 5,
                    "description": "Good self-awareness habits",
                    "boost": 0.3
                }
            }
        }
    
    async def analyze_mood_trends(self, user_id: str, db: Session, days: int = 14) -> Dict[str, Any]:
        """Analyze user's mood trends for weather prediction"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id,
            MoodEntry.created_at >= cutoff_date
        ).order_by(desc(MoodEntry.created_at)).all()
        
        if not entries:
            return {"trends": {}, "averages": {}, "patterns": {}}
        
        # Calculate basic trends
        mood_scores = [entry.mood_score for entry in entries]
        energy_levels = [entry.energy_level for entry in entries if entry.energy_level]
        stress_levels = [entry.stress_level for entry in entries if entry.stress_level]
        
        trends = {
            "mood_trend": self._calculate_trend(mood_scores),
            "energy_trend": self._calculate_trend(energy_levels) if energy_levels else 0,
            "stress_trend": self._calculate_trend(stress_levels) if stress_levels else 0
        }
        
        averages = {
            "avg_mood": statistics.mean(mood_scores) if mood_scores else 5,
            "avg_energy": statistics.mean(energy_levels) if energy_levels else 5,
            "avg_stress": statistics.mean(stress_levels) if stress_levels else 5
        }
        
        # Analyze weekly patterns
        weekly_patterns = self._analyze_weekly_patterns(entries)
        
        return {
            "trends": trends,
            "averages": averages,
            "patterns": weekly_patterns,
            "entry_count": len(entries),
            "tracking_consistency": len(entries) / days
        }
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend direction (-1 to 1, where 1 is improving, -1 is declining)"""
        if len(values) < 2:
            return 0
        
        # Simple linear trend calculation
        recent_avg = statistics.mean(values[:len(values)//2]) if len(values) >= 4 else values[0]
        older_avg = statistics.mean(values[len(values)//2:]) if len(values) >= 4 else statistics.mean(values[1:])
        
        if older_avg == 0:
            return 0
        
        trend = (recent_avg - older_avg) / max(older_avg, 1)  # Normalize by older average
        return max(-1, min(1, trend))  # Clamp to [-1, 1]
    
    def _analyze_weekly_patterns(self, entries: List[MoodEntry]) -> Dict[str, Any]:
        """Analyze patterns by day of week and time of day"""
        
        day_patterns = {}
        time_patterns = {}
        
        for entry in entries:
            day_of_week = entry.created_at.weekday()
            hour = entry.created_at.hour
            
            # Day of week patterns
            if day_of_week not in day_patterns:
                day_patterns[day_of_week] = []
            day_patterns[day_of_week].append(entry.mood_score)
            
            # Time of day patterns
            time_period = self._get_time_period(hour)
            if time_period not in time_patterns:
                time_patterns[time_period] = []
            time_patterns[time_period].append(entry.mood_score)
        
        # Calculate averages for each pattern
        day_averages = {day: statistics.mean(scores) for day, scores in day_patterns.items()}
        time_averages = {period: statistics.mean(scores) for period, scores in time_patterns.items()}
        
        return {
            "day_of_week": day_averages,
            "time_of_day": time_averages,
            "best_day": max(day_averages, key=day_averages.get) if day_averages else None,
            "challenging_day": min(day_averages, key=day_averages.get) if day_averages else None,
            "best_time": max(time_averages, key=time_averages.get) if time_averages else None
        }
    
    def _get_time_period(self, hour: int) -> str:
        """Convert hour to time period"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    async def generate_daily_forecast(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Generate comprehensive daily emotional weather forecast"""
        
        # Analyze user's mood trends
        analysis = await self.analyze_mood_trends(user_id, db)
        
        if not analysis["patterns"]:
            return self._generate_default_forecast()
        
        # Predict mood range for tomorrow
        predicted_range = self._predict_mood_range(analysis)
        
        # Identify risk and protective factors
        risk_factors = self._identify_risk_factors(analysis)
        protective_factors = self._identify_protective_factors(analysis)
        
        # Generate personalized recommendations
        recommendations = self._generate_recommendations(analysis, risk_factors, protective_factors)
        
        # Determine weather emoji and description
        weather_info = self._get_weather_metaphor(predicted_range)
        
        forecast = {
            "user_id": user_id,
            "forecast_date": datetime.utcnow() + timedelta(days=1),
            "predicted_mood_range": {
                "min": predicted_range[0],
                "max": predicted_range[1]
            },
            "weather_emoji": weather_info["emoji"],
            "weather_description": weather_info["description"],
            "risk_factors": risk_factors,
            "protective_factors": protective_factors,
            "recommendations": recommendations,
            "confidence_score": self._calculate_confidence_score(analysis)
        }
        
        # Store forecast in database
        await self._store_forecast(forecast, db)
        
        return forecast
    
    def _predict_mood_range(self, analysis: Dict[str, Any]) -> Tuple[float, float]:
        """Predict tomorrow's mood range based on patterns and trends"""
        
        base_mood = analysis["averages"]["avg_mood"]
        trend_adjustment = analysis["trends"]["mood_trend"] * 0.5  # Moderate trend impact
        
        # Consider day-of-week patterns
        tomorrow = datetime.utcnow() + timedelta(days=1)
        tomorrow_day = tomorrow.weekday()
        
        day_patterns = analysis["patterns"].get("day_of_week", {})
        if tomorrow_day in day_patterns:
            day_adjustment = (day_patterns[tomorrow_day] - base_mood) * 0.3
        else:
            day_adjustment = 0
        
        predicted_center = base_mood + trend_adjustment + day_adjustment
        predicted_center = max(1, min(10, predicted_center))  # Clamp to valid range
        
        # Calculate range based on user's mood volatility
        mood_scores = [analysis["averages"]["avg_mood"]]  # Simplified for Phase 1
        volatility = 1.5  # Default volatility
        
        min_mood = max(1, predicted_center - volatility)
        max_mood = min(10, predicted_center + volatility)
        
        return (round(min_mood, 1), round(max_mood, 1))
    
    def _identify_risk_factors(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors for tomorrow"""
        
        risks = []
        tomorrow = datetime.utcnow() + timedelta(days=1)
        
        # Check day-based risks
        if tomorrow.weekday() == 0:  # Monday
            risks.append("Monday transition stress - weekend to work shift")
        
        if tomorrow.weekday() == 6:  # Sunday
            risks.append("Sunday evening anxiety - anticipating week ahead")
        
        # Check trend-based risks
        if analysis["trends"]["stress_trend"] > 0.3:
            risks.append("Rising stress levels - consider stress management")
        
        if analysis["trends"]["mood_trend"] < -0.3:
            risks.append("Declining mood pattern - extra self-care needed")
        
        if analysis["averages"]["avg_energy"] < 4:
            risks.append("Low energy levels - may impact mood resilience")
        
        # Check consistency risks
        if analysis["tracking_consistency"] < 0.5:
            risks.append("Irregular tracking - harder to predict patterns")
        
        return risks
    
    def _identify_protective_factors(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify protective factors and strengths"""
        
        factors = []
        tomorrow = datetime.utcnow() + timedelta(days=1)
        
        # Check day-based protections
        if tomorrow.weekday() >= 5:  # Weekend
            factors.append("Weekend relaxation opportunity")
        
        # Check positive trends
        if analysis["trends"]["mood_trend"] > 0.2:
            factors.append("Positive mood momentum - keep it up!")
        
        if analysis["averages"]["avg_energy"] >= 7:
            factors.append("Good energy levels supporting emotional well-being")
        
        if analysis["trends"]["stress_trend"] < -0.2:
            factors.append("Decreasing stress - effective coping strategies")
        
        # Check consistency strengths
        if analysis["tracking_consistency"] >= 0.7:
            factors.append("Excellent self-awareness through consistent tracking")
        
        if analysis["patterns"].get("best_time"):
            best_time = analysis["patterns"]["best_time"]
            factors.append(f"Your {best_time} tends to be your strongest time of day")
        
        return factors
    
    def _generate_recommendations(self, analysis: Dict[str, Any], 
                                risks: List[str], protective_factors: List[str]) -> List[Dict[str, str]]:
        """Generate personalized recommendations based on analysis"""
        
        recommendations = []
        
        # Risk-based recommendations
        for risk in risks:
            if "Monday" in risk:
                recommendations.append({
                    "id": "monday_prep",
                    "text": "Sunday evening: Prepare for Monday with gentle planning and self-care",
                    "priority": "normal",
                    "type": "preparation"
                })
            elif "stress" in risk:
                recommendations.append({
                    "id": "stress_management",
                    "text": "Try a 5-minute breathing exercise or short walk to manage rising stress",
                    "priority": "high",
                    "type": "intervention"
                })
            elif "declining mood" in risk:
                recommendations.append({
                    "id": "mood_support",
                    "text": "Reach out to a friend, practice gratitude, or do something you enjoy",
                    "priority": "high", 
                    "type": "support"
                })
            elif "energy" in risk:
                recommendations.append({
                    "id": "energy_boost",
                    "text": "Focus on good sleep and consider energizing activities like light exercise",
                    "priority": "normal",
                    "type": "wellness"
                })
        
        # Strength-based recommendations
        if any("momentum" in factor for factor in protective_factors):
            recommendations.append({
                "id": "maintain_momentum",
                "text": "You're doing great! Continue what's working and celebrate small wins",
                "priority": "normal",
                "type": "encouragement"
            })
        
        # Time-based recommendations
        best_time = analysis["patterns"].get("best_time")
        if best_time:
            recommendations.append({
                "id": "optimal_timing",
                "text": f"Schedule important tasks during your strong {best_time} period",
                "priority": "normal",
                "type": "optimization"
            })
        
        # Default helpful recommendation
        if not recommendations:
            recommendations.append({
                "id": "general_wellness",
                "text": "Start tomorrow with intention - a moment of mindfulness or gratitude",
                "priority": "normal", 
                "type": "wellness"
            })
        
        return recommendations[:4]  # Limit to 4 recommendations
    
    def _get_weather_metaphor(self, mood_range: Tuple[float, float]) -> Dict[str, str]:
        """Get weather emoji and description based on predicted mood range"""
        
        avg_mood = (mood_range[0] + mood_range[1]) / 2
        
        if avg_mood >= 8:
            return {
                "emoji": "☀️",
                "description": "Sunny and bright emotional climate"
            }
        elif avg_mood >= 6:
            return {
                "emoji": "🌤️",
                "description": "Partly cloudy with sunny breaks"
            }
        elif avg_mood >= 4:
            return {
                "emoji": "⛅",
                "description": "Cloudy with mixed conditions"
            }
        elif avg_mood >= 2:
            return {
                "emoji": "🌧️",
                "description": "Overcast with some rough patches"
            }
        else:
            return {
                "emoji": "⛈️",
                "description": "Stormy weather - extra care needed"
            }
    
    def _calculate_confidence_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence in prediction based on data quality"""
        
        base_confidence = 0.5
        
        # More data = higher confidence
        if analysis["entry_count"] >= 14:
            base_confidence += 0.3
        elif analysis["entry_count"] >= 7:
            base_confidence += 0.2
        elif analysis["entry_count"] >= 3:
            base_confidence += 0.1
        
        # Consistent tracking = higher confidence
        if analysis["tracking_consistency"] >= 0.8:
            base_confidence += 0.2
        elif analysis["tracking_consistency"] >= 0.5:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _generate_default_forecast(self) -> Dict[str, Any]:
        """Generate default forecast for new users"""
        
        return {
            "forecast_date": datetime.utcnow() + timedelta(days=1),
            "predicted_mood_range": {"min": 4.0, "max": 7.0},
            "weather_emoji": "🌤️",
            "weather_description": "Partly cloudy - building your emotional awareness",
            "risk_factors": ["New to tracking - patterns still developing"],
            "protective_factors": ["Taking the first step toward self-awareness"],
            "recommendations": [
                {
                    "id": "start_tracking",
                    "text": "Continue tracking daily to build personalized insights",
                    "priority": "normal",
                    "type": "habit_building"
                }
            ],
            "confidence_score": 0.3
        }
    
    async def _store_forecast(self, forecast: Dict[str, Any], db: Session):
        """Store forecast in database for tracking accuracy"""
        
        weather_forecast = EmotionalWeatherForecast(
            user_id=forecast["user_id"],
            forecast_date=forecast["forecast_date"],
            predicted_mood_range=forecast["predicted_mood_range"],
            risk_factors=forecast["risk_factors"],
            protective_factors=forecast["protective_factors"],
            recommendations=forecast["recommendations"],
            confidence_score=forecast["confidence_score"]
        )
        
        db.add(weather_forecast)
        db.commit()
    
    async def get_weekly_weather_outlook(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Generate weekly emotional weather outlook"""
        
        analysis = await self.analyze_mood_trends(user_id, db, days=30)  # Look back further for weekly prediction
        
        weekly_outlook = []
        base_date = datetime.utcnow() + timedelta(days=1)
        
        for i in range(7):
            date = base_date + timedelta(days=i)
            day_name = date.strftime("%A")
            
            # Get day-specific patterns
            day_patterns = analysis["patterns"].get("day_of_week", {})
            if date.weekday() in day_patterns:
                day_mood = day_patterns[date.weekday()]
                weather_info = self._get_weather_metaphor((day_mood - 0.5, day_mood + 0.5))
            else:
                weather_info = {"emoji": "🌤️", "description": "Mixed conditions"}
            
            weekly_outlook.append({
                "date": date.strftime("%Y-%m-%d"),
                "day": day_name,
                "emoji": weather_info["emoji"],
                "description": weather_info["description"]
            })
        
        return {
            "user_id": user_id,
            "week_outlook": weekly_outlook,
            "confidence_score": self._calculate_confidence_score(analysis),
            "generated_at": datetime.utcnow().isoformat()
        }
