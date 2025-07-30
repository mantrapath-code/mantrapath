"""
Effectiveness Tracker - ML component for tracking notification effectiveness
Monitors user engagement and adapts notification strategies based on feedback
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)

class EffectivenessTracker:
    """Tracks notification effectiveness and provides feedback for ML model improvement"""
    
    def __init__(self):
        self.ready = True
        self.engagement_history = []
        self.effectiveness_metrics = {}
        self.adaptation_rules = self._initialize_adaptation_rules()
        
    def is_ready(self) -> bool:
        """Check if the tracker is ready"""
        return self.ready
    
    def _initialize_adaptation_rules(self) -> Dict[str, Any]:
        """Initialize rules for adapting notification strategies"""
        return {
            "low_engagement_threshold": 0.3,
            "high_engagement_threshold": 0.7,
            "min_data_points": 5,
            "adaptation_sensitivity": 0.1,
            "time_window_hours": 24,
            "effectiveness_weights": {
                "immediate_engagement": 0.4,
                "delayed_response": 0.3,
                "mood_impact": 0.3
            }
        }
    
    def track_engagement(self, engagement_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track user engagement with notifications
        
        Args:
            engagement_data: Dictionary containing engagement information
            
        Returns:
            Dictionary with tracking results and effectiveness updates
        """
        try:
            # Store engagement data
            engagement_record = {
                "notification_id": engagement_data["notification_id"],
                "user_id": engagement_data["user_id"],
                "engagement_type": engagement_data["engagement_type"],
                "engagement_time": engagement_data["engagement_time"],
                "subsequent_mood_change": engagement_data.get("subsequent_mood_change"),
                "notification_hour": engagement_data["engagement_time"].hour,
                "notification_day": engagement_data["engagement_time"].weekday(),
                "timestamp": datetime.utcnow()
            }
            
            self.engagement_history.append(engagement_record)
            
            # Limit history to prevent memory issues
            if len(self.engagement_history) > 10000:
                self.engagement_history = self.engagement_history[-5000:]
            
            # Calculate immediate effectiveness score
            effectiveness_score = self._calculate_effectiveness_score(engagement_record)
            
            # Update user-specific metrics
            user_id = engagement_data["user_id"]
            if user_id not in self.effectiveness_metrics:
                self.effectiveness_metrics[user_id] = {
                    "total_notifications": 0,
                    "engagement_count": 0,
                    "effectiveness_scores": [],
                    "hourly_effectiveness": defaultdict(list),
                    "type_effectiveness": defaultdict(list),
                    "last_updated": datetime.utcnow()
                }
            
            user_metrics = self.effectiveness_metrics[user_id]
            user_metrics["total_notifications"] += 1
            user_metrics["effectiveness_scores"].append(effectiveness_score)
            user_metrics["hourly_effectiveness"][engagement_record["notification_hour"]].append(effectiveness_score)
            user_metrics["last_updated"] = datetime.utcnow()
            
            if engagement_record["engagement_type"] != "ignored":
                user_metrics["engagement_count"] += 1
            
            # Generate adaptation recommendations
            adaptations = self._generate_adaptations(user_id)
            
            return {
                "tracking_success": True,
                "effectiveness_score": effectiveness_score,
                "user_engagement_rate": user_metrics["engagement_count"] / user_metrics["total_notifications"],
                "adaptations_recommended": adaptations,
                "total_data_points": len(self.engagement_history)
            }
            
        except Exception as e:
            logger.error(f"Error tracking engagement: {e}")
            return {
                "tracking_success": False,
                "error": str(e)
            }
    
    def _calculate_effectiveness_score(self, engagement_record: Dict[str, Any]) -> float:
        """Calculate effectiveness score for a single engagement"""
        # Base engagement scores
        engagement_scores = {
            "opened": 0.7,
            "acted_upon": 1.0,
            "dismissed": 0.3,
            "ignored": 0.0,
            "clicked": 0.8,
            "shared": 0.9
        }
        
        base_score = engagement_scores.get(engagement_record["engagement_type"], 0.5)
        
        # Adjust for mood impact if available
        mood_change = engagement_record.get("subsequent_mood_change")
        if mood_change is not None:
            # Positive mood change increases effectiveness
            mood_factor = min(1.0, max(0.0, (mood_change + 3) / 6))  # Normalize to 0-1
            base_score = (base_score * 0.7) + (mood_factor * 0.3)
        
        # Adjust for timing (some hours might be naturally more effective)
        time_factor = self._get_time_effectiveness_factor(engagement_record["notification_hour"])
        base_score *= time_factor
        
        return min(1.0, max(0.0, base_score))
    
    def _get_time_effectiveness_factor(self, hour: int) -> float:
        """Get time-based effectiveness factor"""
        # Based on general research about notification engagement
        if 8 <= hour <= 10:  # Morning peak
            return 1.1
        elif 12 <= hour <= 14:  # Lunch time
            return 0.9
        elif 15 <= hour <= 17:  # Afternoon
            return 1.0
        elif 18 <= hour <= 20:  # Evening
            return 1.1
        elif 21 <= hour <= 23:  # Late evening
            return 0.8
        else:  # Night/early morning
            return 0.6
    
    def _generate_adaptations(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate adaptation recommendations based on user's effectiveness data"""
        adaptations = []
        
        if user_id not in self.effectiveness_metrics:
            return adaptations
        
        user_metrics = self.effectiveness_metrics[user_id]
        
        # Check if enough data for meaningful adaptations
        if user_metrics["total_notifications"] < self.adaptation_rules["min_data_points"]:
            return adaptations
        
        # Calculate overall engagement rate
        engagement_rate = user_metrics["engagement_count"] / user_metrics["total_notifications"]
        
        # Low engagement adaptations
        if engagement_rate < self.adaptation_rules["low_engagement_threshold"]:
            adaptations.append({
                "type": "frequency_reduction",
                "reason": "Low engagement rate",
                "recommendation": "Reduce notification frequency by 30%",
                "priority": "high"
            })
            
            adaptations.append({
                "type": "content_variation",
                "reason": "Low engagement suggests content mismatch",
                "recommendation": "Try different notification styles",
                "priority": "medium"
            })
        
        # High engagement optimization
        elif engagement_rate > self.adaptation_rules["high_engagement_threshold"]:
            adaptations.append({
                "type": "timing_optimization",
                "reason": "High engagement - optimize timing",
                "recommendation": "Focus on most effective time slots",
                "priority": "medium"
            })
        
        # Analyze hourly effectiveness
        hourly_adaptations = self._analyze_hourly_effectiveness(user_metrics)
        adaptations.extend(hourly_adaptations)
        
        return adaptations
    
    def _analyze_hourly_effectiveness(self, user_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze effectiveness by hour and suggest timing adaptations"""
        adaptations = []
        hourly_data = user_metrics["hourly_effectiveness"]
        
        if len(hourly_data) < 3:  # Need data from multiple hours
            return adaptations
        
        # Calculate average effectiveness by hour
        hourly_averages = {}
        for hour, scores in hourly_data.items():
            if len(scores) >= 2:
                hourly_averages[hour] = statistics.mean(scores)
        
        if len(hourly_averages) < 2:
            return adaptations
        
        # Find best and worst performing hours
        best_hour = max(hourly_averages.keys(), key=lambda h: hourly_averages[h])
        worst_hour = min(hourly_averages.keys(), key=lambda h: hourly_averages[h])
        
        effectiveness_diff = hourly_averages[best_hour] - hourly_averages[worst_hour]
        
        if effectiveness_diff > 0.3:  # Significant difference
            adaptations.append({
                "type": "timing_shift",
                "reason": f"Hour {best_hour} performs {effectiveness_diff:.1f} better than hour {worst_hour}",
                "recommendation": f"Prioritize notifications around {best_hour}:00",
                "priority": "high",
                "data": {
                    "best_hour": best_hour,
                    "best_effectiveness": round(hourly_averages[best_hour], 2),
                    "worst_hour": worst_hour,
                    "worst_effectiveness": round(hourly_averages[worst_hour], 2)
                }
            })
        
        return adaptations
    
    def get_user_effectiveness_summary(self, user_id: str) -> Dict[str, Any]:
        """Get effectiveness summary for a specific user"""
        if user_id not in self.effectiveness_metrics:
            return {
                "user_id": user_id,
                "status": "insufficient_data",
                "recommendations": ["Continue using notifications to gather effectiveness data"]
            }
        
        user_metrics = self.effectiveness_metrics[user_id]
        
        # Calculate key metrics
        engagement_rate = user_metrics["engagement_count"] / user_metrics["total_notifications"]
        avg_effectiveness = statistics.mean(user_metrics["effectiveness_scores"]) if user_metrics["effectiveness_scores"] else 0
        
        # Determine effectiveness level
        if avg_effectiveness > 0.7:
            effectiveness_level = "high"
        elif avg_effectiveness > 0.4:
            effectiveness_level = "moderate"
        else:
            effectiveness_level = "low"
        
        # Find best performing hour
        hourly_data = user_metrics["hourly_effectiveness"]
        best_hour = None
        if hourly_data:
            hourly_averages = {
                hour: statistics.mean(scores) 
                for hour, scores in hourly_data.items() 
                if len(scores) >= 2
            }
            if hourly_averages:
                best_hour = max(hourly_averages.keys(), key=lambda h: hourly_averages[h])
        
        return {
            "user_id": user_id,
            "effectiveness_level": effectiveness_level,
            "engagement_rate": round(engagement_rate, 3),
            "average_effectiveness": round(avg_effectiveness, 3),
            "total_notifications": user_metrics["total_notifications"],
            "best_hour": best_hour,
            "data_quality": "good" if user_metrics["total_notifications"] >= 10 else "limited",
            "last_updated": user_metrics["last_updated"].isoformat(),
            "recommendations": self._get_user_recommendations(engagement_rate, avg_effectiveness)
        }
    
    def _get_user_recommendations(self, engagement_rate: float, avg_effectiveness: float) -> List[str]:
        """Get personalized recommendations based on user metrics"""
        recommendations = []
        
        if engagement_rate < 0.3:
            recommendations.append("Consider adjusting notification timing or frequency")
            recommendations.append("Try different types of notifications")
        elif engagement_rate > 0.7:
            recommendations.append("Great engagement! Consider slight frequency increase")
            recommendations.append("Your current notification strategy is working well")
        
        if avg_effectiveness < 0.4:
            recommendations.append("Focus on higher-impact notification content")
            recommendations.append("Review optimal timing preferences")
        elif avg_effectiveness > 0.7:
            recommendations.append("Excellent effectiveness! Maintain current approach")
        
        if not recommendations:
            recommendations.append("Continue current notification strategy")
            recommendations.append("Keep providing feedback to improve personalization")
        
        return recommendations
    
    def get_global_effectiveness_insights(self) -> Dict[str, Any]:
        """Get insights from all users' effectiveness data (anonymized)"""
        if not self.engagement_history:
            return {"status": "no_data"}
        
        # Analyze global patterns
        hourly_engagement = defaultdict(list)
        daily_engagement = defaultdict(list)
        type_engagement = defaultdict(list)
        
        for record in self.engagement_history:
            effectiveness = self._calculate_effectiveness_score(record)
            hourly_engagement[record["notification_hour"]].append(effectiveness)
            daily_engagement[record["notification_day"]].append(effectiveness)
            type_engagement[record["engagement_type"]].append(effectiveness)
        
        # Calculate global optimal hours
        hourly_averages = {
            hour: statistics.mean(scores)
            for hour, scores in hourly_engagement.items()
            if len(scores) >= 10  # Minimum sample size
        }
        
        optimal_hours = sorted(
            hourly_averages.keys(),
            key=lambda h: hourly_averages[h],
            reverse=True
        )[:3]
        
        return {
            "status": "success",
            "total_data_points": len(self.engagement_history),
            "optimal_hours_global": optimal_hours,
            "hourly_effectiveness": {
                hour: round(avg, 3)
                for hour, avg in hourly_averages.items()
            },
            "most_effective_engagement": max(type_engagement.keys(), key=lambda t: statistics.mean(type_engagement[t])) if type_engagement else "unknown",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def update_metrics(self) -> bool:
        """Update effectiveness metrics (background task)"""
        try:
            # Clean old data (older than 90 days)
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            self.engagement_history = [
                record for record in self.engagement_history
                if record["timestamp"] > cutoff_date
            ]
            
            # Update user metrics cleanup
            for user_id, metrics in list(self.effectiveness_metrics.items()):
                if metrics["last_updated"] < cutoff_date:
                    del self.effectiveness_metrics[user_id]
            
            logger.info(f"Updated effectiveness metrics. Active users: {len(self.effectiveness_metrics)}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the effectiveness tracker"""
        return {
            "tracker_type": "engagement_based_tracker",
            "total_engagement_records": len(self.engagement_history),
            "active_users": len(self.effectiveness_metrics),
            "adaptation_rules_count": len(self.adaptation_rules),
            "data_retention_days": 90,
            "effectiveness_calculation_factors": list(self.adaptation_rules["effectiveness_weights"].keys()),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def export_anonymized_insights(self) -> Dict[str, Any]:
        """Export anonymized insights for research and improvement"""
        global_insights = self.get_global_effectiveness_insights()
        
        # Additional anonymized statistics
        user_engagement_rates = []
        user_effectiveness_scores = []
        
        for metrics in self.effectiveness_metrics.values():
            if metrics["total_notifications"] >= 5:
                engagement_rate = metrics["engagement_count"] / metrics["total_notifications"]
                user_engagement_rates.append(engagement_rate)
                
                if metrics["effectiveness_scores"]:
                    avg_effectiveness = statistics.mean(metrics["effectiveness_scores"])
                    user_effectiveness_scores.append(avg_effectiveness)
        
        anonymized_stats = {
            "user_count": len(user_engagement_rates),
            "average_engagement_rate": statistics.mean(user_engagement_rates) if user_engagement_rates else 0,
            "average_effectiveness": statistics.mean(user_effectiveness_scores) if user_effectiveness_scores else 0,
            "engagement_rate_distribution": {
                "q25": statistics.quantiles(user_engagement_rates, n=4)[0] if len(user_engagement_rates) >= 4 else 0,
                "median": statistics.median(user_engagement_rates) if user_engagement_rates else 0,
                "q75": statistics.quantiles(user_engagement_rates, n=4)[2] if len(user_engagement_rates) >= 4 else 0
            }
        }
        
        return {
            "global_insights": global_insights,
            "anonymized_statistics": anonymized_stats,
            "export_timestamp": datetime.utcnow().isoformat()
        }
