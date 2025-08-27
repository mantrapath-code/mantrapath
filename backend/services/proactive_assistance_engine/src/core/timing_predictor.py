"""
Comprehensive Timing Predictor

Enhanced timing prediction system that uses existing behavioral data
to determine optimal timing for proactive assistance delivery.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger(__name__)

class ComprehensiveTimingPredictor:
    """
    Enhanced timing prediction system that uses existing behavioral data
    """
    
    def __init__(self):
        self.timing_config: Dict[str, Any] = {
            "min_gap_between_assistance_hours": 2,
            "preferred_time_windows": {
                "morning": {"start": 8, "end": 11, "weight": 0.8},
                "afternoon": {"start": 14, "end": 17, "weight": 0.9},
                "evening": {"start": 18, "end": 21, "weight": 0.7}
            },
            "cultural_timing_adaptations": {
                "collectivist": {"family_time_awareness": True, "respect_meal_times": True},
                "individualist": {"personal_schedule_focus": True, "work_hour_respect": True}
            }
        }
    
    async def evaluate_optimal_timing(
        self, 
        user_id: str, 
        user_context: Dict[str, Any],
        intervention_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate if current timing is optimal for proactive assistance
        """
        try:
            current_time = datetime.now(timezone.utc)
            
            # Step 1: Check recent assistance history
            recent_assistance_check = await self._check_recent_assistance_gap(user_id, current_time)
            
            # Step 2: Analyze user activity patterns
            activity_analysis = await self._analyze_current_activity_state(user_context, current_time)
            
            # Step 3: Cultural timing considerations
            cultural_timing = await self._evaluate_cultural_timing_appropriateness(
                user_context.get("cultural_profile", {}), current_time
            )
            
            # Step 4: Urgency override check
            urgency_override = intervention_analysis.get("urgency_level") in ["critical", "high"]
            
            # Step 5: Calculate overall timing score
            timing_score = await self._calculate_timing_appropriateness_score(
                recent_assistance_check, activity_analysis, cultural_timing, urgency_override
            )
            
            # Step 6: Make timing decision
            timing_decision = {
                "timing_appropriate": timing_score > 0.7 or urgency_override,
                "timing_confidence": timing_score,
                "can_proceed": timing_score > 0.5 or urgency_override,
                "recommended_delay_minutes": 0 if urgency_override else max(0, int((0.7 - timing_score) * 60))
            }
            
            return {
                "timing_evaluation": timing_decision,
                "recent_assistance_check": recent_assistance_check,
                "activity_analysis": activity_analysis,
                "cultural_timing": cultural_timing,
                "urgency_override": urgency_override,
                "timing_score": timing_score,
                "evaluation_timestamp": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error("Timing evaluation failed", error=str(e), user_id=user_id)
            return self._create_fallback_timing_evaluation()
    
    async def _check_recent_assistance_gap(self, user_id: str, current_time: datetime) -> Dict[str, Any]:
        """Check if enough time has passed since last assistance"""
        try:
            # This would typically query a database for recent assistance history
            # For now, we'll simulate with a default gap
            min_gap_hours = self.timing_config["min_gap_between_assistance_hours"]
            
            # Simulate last assistance time (in real implementation, query database)
            last_assistance_time = current_time - timedelta(hours=min_gap_hours + 1)
            
            time_since_last = current_time - last_assistance_time
            hours_since_last = time_since_last.total_seconds() / 3600
            
            sufficient_gap = hours_since_last >= min_gap_hours
            
            return {
                "last_assistance_time": last_assistance_time.isoformat(),
                "hours_since_last": hours_since_last,
                "sufficient_gap": sufficient_gap,
                "gap_score": min(1.0, hours_since_last / min_gap_hours)
            }
            
        except Exception as e:
            logger.error("Failed to check recent assistance gap", error=str(e))
            return {
                "last_assistance_time": None,
                "hours_since_last": 0,
                "sufficient_gap": False,
                "gap_score": 0.0
            }
    
    async def _analyze_current_activity_state(
        self, 
        user_context: Dict[str, Any], 
        current_time: datetime
    ) -> Dict[str, Any]:
        """
        Analyze user's current activity state for timing appropriateness
        """
        try:
            recent_interactions = user_context.get("recent_interactions", [])
            
            # Check recent platform activity
            last_interaction_time = None
            if recent_interactions:
                last_interaction = recent_interactions[-1]
                last_interaction_time = datetime.fromisoformat(
                    last_interaction.get("timestamp", current_time.isoformat())
                )
            
            # Calculate engagement level
            engagement_level = self._calculate_engagement_level(recent_interactions, current_time)
            
            # Check time of day appropriateness
            time_appropriateness = self._evaluate_time_of_day_appropriateness(current_time)
            
            # Determine if user seems available/receptive
            receptiveness_score = self._calculate_user_receptiveness(
                engagement_level, last_interaction_time or current_time, current_time
            )
            
            return {
                "engagement_level": engagement_level,
                "last_interaction_minutes_ago": (
                    (current_time - last_interaction_time).total_seconds() / 60
                    if last_interaction_time else None
                ),
                "time_of_day_appropriateness": time_appropriateness,
                "user_receptiveness_score": receptiveness_score,
                "activity_confidence": min(0.9, engagement_level + time_appropriateness) / 2
            }
            
        except Exception as e:
            logger.error("Activity analysis failed", error=str(e))
            return {"engagement_level": 0.5, "user_receptiveness_score": 0.5, "activity_confidence": 0.3}
    
    async def _evaluate_cultural_timing_appropriateness(
        self, 
        cultural_profile: Dict[str, Any], 
        current_time: datetime
    ) -> Dict[str, Any]:
        """Evaluate cultural timing considerations"""
        try:
            primary_culture = cultural_profile.get("primary_culture", "unknown")
            cultural_guidelines = self.timing_config["cultural_timing_adaptations"].get(primary_culture, {})
            
            # Check meal time awareness for collectivist cultures
            meal_time_awareness = cultural_guidelines.get("respect_meal_times", False)
            meal_time_score = 1.0
            if meal_time_awareness:
                meal_time_score = self._evaluate_meal_time_appropriateness(current_time)
            
            # Check family time awareness
            family_time_awareness = cultural_guidelines.get("family_time_awareness", False)
            family_time_score = 1.0
            if family_time_awareness:
                family_time_score = self._evaluate_family_time_appropriateness(current_time)
            
            overall_cultural_score = (meal_time_score + family_time_score) / 2
            
            return {
                "primary_culture": primary_culture,
                "meal_time_appropriateness": meal_time_score,
                "family_time_appropriateness": family_time_score,
                "overall_cultural_score": overall_cultural_score,
                "cultural_guidelines_applied": list(cultural_guidelines.keys())
            }
            
        except Exception as e:
            logger.error("Cultural timing evaluation failed", error=str(e))
            return {
                "primary_culture": "unknown",
                "meal_time_appropriateness": 1.0,
                "family_time_appropriateness": 1.0,
                "overall_cultural_score": 1.0,
                "cultural_guidelines_applied": []
            }
    
    async def _calculate_timing_appropriateness_score(
        self,
        recent_assistance_check: Dict[str, Any],
        activity_analysis: Dict[str, Any],
        cultural_timing: Dict[str, Any],
        urgency_override: bool
    ) -> float:
        """Calculate overall timing appropriateness score"""
        try:
            if urgency_override:
                return 0.9  # High score for urgent situations
            
            # Weighted scoring
            gap_score = recent_assistance_check.get("gap_score", 0.0) * 0.3
            activity_score = activity_analysis.get("user_receptiveness_score", 0.5) * 0.4
            cultural_score = cultural_timing.get("overall_cultural_score", 1.0) * 0.3
            
            total_score = gap_score + activity_score + cultural_score
            
            return min(1.0, max(0.0, total_score))
            
        except Exception as e:
            logger.error("Timing score calculation failed", error=str(e))
            return 0.5
    
    def _calculate_engagement_level(self, recent_interactions: List[Dict[str, Any]], current_time: datetime) -> float:
        """Calculate user engagement level based on recent interactions"""
        try:
            if not recent_interactions:
                return 0.3  # Low engagement if no recent interactions
            
            # Count interactions in last 24 hours
            day_ago = current_time - timedelta(days=1)
            recent_count = sum(
                1 for interaction in recent_interactions
                if datetime.fromisoformat(interaction.get("timestamp", "2025-01-01T00:00:00")) > day_ago
            )
            
            # Normalize to 0-1 scale
            if recent_count == 0:
                return 0.3
            elif recent_count <= 2:
                return 0.5
            elif recent_count <= 5:
                return 0.7
            else:
                return 0.9
                
        except Exception as e:
            logger.error("Engagement level calculation failed", error=str(e))
            return 0.5
    
    def _evaluate_time_of_day_appropriateness(self, current_time: datetime) -> float:
        """Evaluate if current time is appropriate for assistance"""
        try:
            hour = current_time.hour
            
            # Check preferred time windows
            for window_config in self.timing_config["preferred_time_windows"].values():
                start_hour = window_config["start"]
                end_hour = window_config["end"]
                weight = window_config["weight"]
                
                if start_hour <= hour <= end_hour:
                    return weight
            
            # Outside preferred windows
            return 0.4
            
        except Exception as e:
            logger.error("Time of day evaluation failed", error=str(e))
            return 0.5
    
    def _calculate_user_receptiveness(
        self, 
        engagement_level: float, 
        last_interaction_time: datetime, 
        current_time: datetime
    ) -> float:
        """Calculate user receptiveness score"""
        try:
            if not last_interaction_time:
                return engagement_level * 0.7  # Lower score if no recent interaction
            
            # Time since last interaction (in hours)
            hours_since = (current_time - last_interaction_time).total_seconds() / 3600
            
            # Optimal receptiveness window: 1-4 hours since last interaction
            if 1 <= hours_since <= 4:
                time_factor = 1.0
            elif hours_since < 1:
                time_factor = 0.6  # Too recent
            else:
                time_factor = max(0.3, 1.0 - (hours_since - 4) * 0.1)  # Decay over time
            
            # Combine engagement and time factors
            receptiveness = (engagement_level * 0.6) + (time_factor * 0.4)
            
            return min(1.0, max(0.0, receptiveness))
            
        except Exception as e:
            logger.error("Receptiveness calculation failed", error=str(e))
            return 0.5
    
    def _evaluate_meal_time_appropriateness(self, current_time: datetime) -> float:
        """Evaluate if current time respects meal times"""
        try:
            hour = current_time.hour
            
            # Common meal times to avoid
            meal_times = [
                (6, 9),   # Breakfast
                (11, 14), # Lunch
                (17, 20)  # Dinner
            ]
            
            for start, end in meal_times:
                if start <= hour <= end:
                    return 0.3  # Lower score during meal times
            
            return 1.0  # Good score outside meal times
            
        except Exception as e:
            logger.error("Meal time evaluation failed", error=str(e))
            return 1.0
    
    def _evaluate_family_time_appropriateness(self, current_time: datetime) -> float:
        """Evaluate if current time respects family time"""
        try:
            hour = current_time.hour
            
            # Family time considerations (evening hours)
            if 18 <= hour <= 22:
                return 0.6  # Moderate score during family time
            elif 22 <= hour <= 6:
                return 0.2  # Low score during late night/early morning
            
            return 1.0  # Good score during other hours
            
        except Exception as e:
            logger.error("Family time evaluation failed", error=str(e))
            return 1.0
    
    def _create_fallback_timing_evaluation(self) -> Dict[str, Any]:
        """Create fallback timing evaluation when analysis fails"""
        return {
            "timing_evaluation": {
                "timing_appropriate": False,
                "timing_confidence": 0.0,
                "can_proceed": False,
                "recommended_delay_minutes": 60
            },
            "recent_assistance_check": {},
            "activity_analysis": {},
            "cultural_timing": {},
            "urgency_override": False,
            "timing_score": 0.0,
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        }
