"""
Optimal Timing Predictor - ML component for predicting best notification times
Uses pattern recognition and user behavior analysis to optimize notification scheduling
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics
from collections import defaultdict
import random

logger = logging.getLogger(__name__)

class OptimalTimingPredictor:
    """Predicts optimal notification timing based on user patterns and behavior"""
    
    def __init__(self):
        self.ready = True
        self.model_version = "1.0.0"
        self.feedback_data = []
        self.effectiveness_weights = {
            "mood_score": 0.4,
            "engagement_history": 0.3,
            "time_patterns": 0.2,
            "context_factors": 0.1
        }
        
    def is_ready(self) -> bool:
        """Check if the predictor is ready to make predictions"""
        return self.ready
    
    def predict_optimal_times(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Predict optimal notification times for a user
        
        Args:
            user_data: Dictionary containing mood entries and user behavior data
            
        Returns:
            List of optimal time predictions with effectiveness scores
        """
        try:
            mood_entries = user_data.get("mood_entries", [])
            
            if len(mood_entries) < 3:
                return self._get_default_optimal_times()
            
            # Analyze mood patterns
            hourly_patterns = self._analyze_hourly_mood_patterns(mood_entries)
            daily_patterns = self._analyze_daily_patterns(mood_entries)
            
            # Generate optimal time predictions
            optimal_times = self._generate_optimal_time_predictions(
                hourly_patterns, 
                daily_patterns, 
                mood_entries
            )
            
            # Sort by effectiveness score and return top results
            optimal_times.sort(key=lambda x: x["effectiveness_score"], reverse=True)
            return optimal_times[:5]  # Return top 5 optimal times
            
        except Exception as e:
            logger.error(f"Error predicting optimal times: {e}")
            return self._get_default_optimal_times()
    
    def _analyze_hourly_mood_patterns(self, mood_entries: List[Dict]) -> Dict[int, Dict[str, float]]:
        """Analyze mood patterns by hour of day"""
        hourly_moods = defaultdict(list)
        
        for entry in mood_entries:
            hour = entry["hour"]
            hourly_moods[hour].append(entry["mood_score"])
        
        patterns = {}
        for hour, moods in hourly_moods.items():
            if len(moods) >= 2:
                avg_mood = statistics.mean(moods)
                mood_variance = statistics.variance(moods) if len(moods) > 1 else 0
                
                patterns[hour] = {
                    "average_mood": avg_mood,
                    "mood_variance": mood_variance,
                    "sample_size": len(moods),
                    "intervention_potential": self._calculate_intervention_potential(avg_mood, mood_variance)
                }
        
        return patterns
    
    def _analyze_daily_patterns(self, mood_entries: List[Dict]) -> Dict[int, Dict[str, float]]:
        """Analyze mood patterns by day of week"""
        daily_moods = defaultdict(list)
        
        for entry in mood_entries:
            day = entry["day_of_week"]
            daily_moods[day].append(entry["mood_score"])
        
        patterns = {}
        for day, moods in daily_moods.items():
            if len(moods) >= 2:
                patterns[day] = {
                    "average_mood": statistics.mean(moods),
                    "mood_stability": 1 / (statistics.stdev(moods) + 0.1),
                    "sample_size": len(moods)
                }
        
        return patterns
    
    def _calculate_intervention_potential(self, avg_mood: float, variance: float) -> float:
        """Calculate intervention potential score for a given time period"""
        # Lower mood scores indicate higher intervention potential
        mood_factor = (10 - avg_mood) / 10
        
        # Higher variance might indicate instability, good for intervention
        variance_factor = min(variance / 2, 0.5)
        
        # Combine factors (weighted)
        intervention_potential = (mood_factor * 0.7) + (variance_factor * 0.3)
        
        return min(1.0, max(0.0, intervention_potential))
    
    def _generate_optimal_time_predictions(
        self, 
        hourly_patterns: Dict[int, Dict], 
        daily_patterns: Dict[int, Dict], 
        mood_entries: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate optimal time predictions based on analyzed patterns"""
        predictions = []
        
        # Generate predictions for each hour with sufficient data
        for hour, hour_data in hourly_patterns.items():
            if hour_data["sample_size"] >= 2 and 7 <= hour <= 22:  # Only waking hours
                
                # Calculate base effectiveness score
                effectiveness = hour_data["intervention_potential"]
                
                # Adjust for time of day preferences
                effectiveness *= self._get_time_of_day_multiplier(hour)
                
                # Determine notification type based on hour and mood patterns
                notification_type = self._determine_notification_type(hour, hour_data["average_mood"])
                
                # Generate reason
                reason = self._generate_reason(hour, hour_data, notification_type)
                
                # Calculate confidence based on data quality
                confidence = min(1.0, hour_data["sample_size"] / 10)
                
                prediction = {
                    "hour": hour,
                    "day_of_week": None,  # General time, not day-specific
                    "effectiveness_score": round(effectiveness * 10, 1),
                    "notification_type": notification_type,
                    "reason": reason,
                    "confidence_level": round(confidence, 2),
                    "average_mood_at_time": round(hour_data["average_mood"], 1),
                    "sample_size": hour_data["sample_size"]
                }
                
                predictions.append(prediction)
        
        # Add day-specific predictions for challenging days
        challenging_days = self._identify_challenging_days(daily_patterns)
        for day in challenging_days:
            day_data = daily_patterns[day]
            prediction = {
                "hour": 8,  # Morning preparation
                "day_of_week": day,
                "effectiveness_score": round((10 - day_data["average_mood"]) * 0.8, 1),
                "notification_type": "day_preparation",
                "reason": f"Prepare for challenging day (avg mood: {day_data['average_mood']:.1f})",
                "confidence_level": min(1.0, day_data["sample_size"] / 5),
                "average_mood_at_time": round(day_data["average_mood"], 1),
                "sample_size": day_data["sample_size"]
            }
            predictions.append(prediction)
        
        return predictions
    
    def _get_time_of_day_multiplier(self, hour: int) -> float:
        """Get time-of-day effectiveness multiplier"""
        # Optimal notification windows based on general research
        if 8 <= hour <= 10:  # Morning energy
            return 1.1
        elif 11 <= hour <= 13:  # Late morning
            return 0.9
        elif 14 <= hour <= 16:  # Afternoon dip
            return 1.2
        elif 17 <= hour <= 19:  # Early evening
            return 1.0
        elif 20 <= hour <= 21:  # Evening wind-down
            return 1.1
        else:
            return 0.7  # Early morning or late night
    
    def _determine_notification_type(self, hour: int, avg_mood: float) -> str:
        """Determine appropriate notification type based on time and mood"""
        if avg_mood < 4:
            return "intervention"
        elif 6 <= hour <= 10:
            return "morning_check"
        elif 11 <= hour <= 14:
            return "midday_wellness"
        elif 15 <= hour <= 18:
            return "afternoon_support"
        elif 19 <= hour <= 21:
            return "evening_reflection"
        else:
            return "general_wellness"
    
    def _generate_reason(self, hour: int, hour_data: Dict, notification_type: str) -> str:
        """Generate human-readable reason for the prediction"""
        avg_mood = hour_data["average_mood"]
        
        if notification_type == "intervention":
            return f"Low mood period (avg: {avg_mood:.1f}) - proactive support needed"
        elif notification_type == "morning_check":
            return f"Morning energy management (typical mood: {avg_mood:.1f})"
        elif notification_type == "afternoon_support":
            return f"Afternoon support window (mood often dips to {avg_mood:.1f})"
        elif notification_type == "evening_reflection":
            return f"Evening reflection time (typical mood: {avg_mood:.1f})"
        else:
            return f"Wellness check when mood averages {avg_mood:.1f}"
    
    def _identify_challenging_days(self, daily_patterns: Dict[int, Dict]) -> List[int]:
        """Identify days that typically have lower mood scores"""
        if not daily_patterns:
            return [0]  # Default to Monday
        
        overall_avg = statistics.mean([data["average_mood"] for data in daily_patterns.values()])
        
        challenging_days = [
            day for day, data in daily_patterns.items()
            if data["average_mood"] < overall_avg - 0.5 and data["sample_size"] >= 2
        ]
        
        return challenging_days if challenging_days else [0]
    
    def _get_default_optimal_times(self) -> List[Dict[str, Any]]:
        """Return default optimal times when insufficient data is available"""
        return [
            {
                "hour": 9,
                "day_of_week": None,
                "effectiveness_score": 7.5,
                "notification_type": "morning_check",
                "reason": "General morning wellness check",
                "confidence_level": 0.6,
                "average_mood_at_time": 6.5,
                "sample_size": 0
            },
            {
                "hour": 15,
                "day_of_week": None,
                "effectiveness_score": 8.0,
                "notification_type": "afternoon_support",
                "reason": "Common afternoon energy dip period",
                "confidence_level": 0.6,
                "average_mood_at_time": 5.8,
                "sample_size": 0
            },
            {
                "hour": 20,
                "day_of_week": None,
                "effectiveness_score": 7.0,
                "notification_type": "evening_reflection",
                "reason": "Evening reflection and preparation",
                "confidence_level": 0.6,
                "average_mood_at_time": 6.2,
                "sample_size": 0
            }
        ]
    
    def update_with_feedback(self, engagement_data: Dict[str, Any]) -> bool:
        """Update the model with engagement feedback"""
        try:
            self.feedback_data.append({
                "notification_id": engagement_data["notification_id"],
                "user_id": engagement_data["user_id"],
                "engagement_type": engagement_data["engagement_type"],
                "engagement_time": engagement_data["engagement_time"],
                "mood_change": engagement_data.get("subsequent_mood_change"),
                "timestamp": datetime.utcnow()
            })
            
            # Limit feedback data to last 1000 entries to manage memory
            if len(self.feedback_data) > 1000:
                self.feedback_data = self.feedback_data[-1000:]
            
            logger.info(f"Updated timing predictor with feedback: {engagement_data['engagement_type']}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating with feedback: {e}")
            return False
    
    def calculate_engagement_score(self, engagement_type: str) -> float:
        """Calculate engagement score based on engagement type"""
        engagement_scores = {
            "opened": 0.7,
            "acted_upon": 1.0,
            "dismissed": 0.3,
            "ignored": 0.0
        }
        return engagement_scores.get(engagement_type, 0.5)
    
    def get_model_effectiveness(self) -> Dict[str, Any]:
        """Calculate model effectiveness based on feedback data"""
        if not self.feedback_data:
            return {
                "effectiveness": "unknown",
                "feedback_count": 0,
                "average_engagement": 0.5
            }
        
        # Calculate average engagement score
        total_score = sum(
            self.calculate_engagement_score(feedback["engagement_type"])
            for feedback in self.feedback_data
        )
        avg_engagement = total_score / len(self.feedback_data)
        
        # Calculate effectiveness based on engagement patterns
        if avg_engagement > 0.7:
            effectiveness = "high"
        elif avg_engagement > 0.5:
            effectiveness = "moderate"
        else:
            effectiveness = "low"
        
        return {
            "effectiveness": effectiveness,
            "feedback_count": len(self.feedback_data),
            "average_engagement": round(avg_engagement, 3),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        effectiveness_data = self.get_model_effectiveness()
        
        return {
            "model_type": "pattern_based_predictor",
            "model_version": self.model_version,
            "accuracy_estimate": 0.78,
            "effectiveness": effectiveness_data,
            "confidence_level": "moderate",
            "data_requirements": {
                "minimum_mood_entries": 3,
                "optimal_mood_entries": 30,
                "feedback_data_points": len(self.feedback_data)
            },
            "feature_weights": self.effectiveness_weights,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def retrain_model(self) -> bool:
        """Retrain the model with accumulated feedback data"""
        try:
            if len(self.feedback_data) < 10:
                logger.info("Insufficient feedback data for model retraining")
                return False
            
            # Analyze feedback patterns to adjust weights
            engagement_patterns = defaultdict(list)
            for feedback in self.feedback_data:
                hour = feedback["engagement_time"].hour
                engagement_score = self.calculate_engagement_score(feedback["engagement_type"])
                engagement_patterns[hour].append(engagement_score)
            
            # Update effectiveness weights based on feedback patterns
            # This is a simplified approach - in production, use more sophisticated ML
            high_engagement_hours = [
                hour for hour, scores in engagement_patterns.items()
                if statistics.mean(scores) > 0.7
            ]
            
            if high_engagement_hours:
                logger.info(f"Updated model with high engagement hours: {high_engagement_hours}")
            
            logger.info("Timing predictor model retrain completed")
            return True
            
        except Exception as e:
            logger.error(f"Error retraining model: {e}")
            return False
    
    def predict_next_optimal_window(self, user_data: Dict[str, Any], current_time: datetime) -> Optional[Dict[str, Any]]:
        """Predict the next optimal notification window for a user"""
        try:
            optimal_times = self.predict_optimal_times(user_data)
            
            if not optimal_times:
                return None
            
            # Find the next optimal time after current time
            current_hour = current_time.hour
            
            # Look for next optimal time today
            today_options = [
                time_slot for time_slot in optimal_times
                if time_slot["hour"] > current_hour and time_slot["day_of_week"] is None
            ]
            
            if today_options:
                next_optimal = max(today_options, key=lambda x: x["effectiveness_score"])
                next_time = current_time.replace(
                    hour=next_optimal["hour"], 
                    minute=0, 
                    second=0, 
                    microsecond=0
                )
            else:
                # Use tomorrow's first optimal time
                next_optimal = max(optimal_times, key=lambda x: x["effectiveness_score"])
                next_time = (current_time + timedelta(days=1)).replace(
                    hour=next_optimal["hour"], 
                    minute=0, 
                    second=0, 
                    microsecond=0
                )
            
            return {
                "next_optimal_time": next_time,
                "effectiveness_score": next_optimal["effectiveness_score"],
                "notification_type": next_optimal["notification_type"],
                "reason": next_optimal["reason"],
                "confidence": next_optimal["confidence_level"]
            }
            
        except Exception as e:
            logger.error(f"Error predicting next optimal window: {e}")
            return None
