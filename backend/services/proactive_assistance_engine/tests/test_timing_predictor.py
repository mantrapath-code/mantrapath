"""
Test suite for Comprehensive Timing Predictor

Comprehensive testing of the timing prediction system that determines
optimal timing for proactive assistance delivery.
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone, timedelta

from src.core.timing_predictor import ComprehensiveTimingPredictor

class TestComprehensiveTimingPredictor:
    """
    Test suite for the comprehensive timing predictor
    """
    
    @pytest.fixture
    def timing_predictor(self):
        """Create timing predictor instance for testing"""
        return ComprehensiveTimingPredictor()
    
    @pytest.fixture
    def sample_user_context(self):
        """Sample user context for testing"""
        return {
            "cultural_profile": {
                "primary_culture": "collectivist",
                "communication_style": "indirect"
            },
            "recent_interactions": [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "service": "mood",
                    "type": "entry"
                }
            ]
        }
    
    @pytest.fixture
    def sample_intervention_analysis(self):
        """Sample intervention analysis for testing"""
        return {
            "intervention_needed": True,
            "intervention_type": "proactive_support",
            "urgency_level": "medium",
            "confidence": 0.8
        }
    
    @pytest.mark.asyncio
    async def test_evaluate_optimal_timing_success(self, timing_predictor, sample_user_context, sample_intervention_analysis):
        """Test successful timing evaluation"""
        user_id = "test_user_123"
        
        result = await timing_predictor.evaluate_optimal_timing(
            user_id, sample_user_context, sample_intervention_analysis
        )
        
        assert result is not None
        assert "timing_evaluation" in result
        assert "recent_assistance_check" in result
        assert "activity_analysis" in result
        assert "cultural_timing" in result
        assert "timing_score" in result
        assert "evaluation_timestamp" in result
        
        # Verify timing evaluation structure
        timing_eval = result["timing_evaluation"]
        assert "timing_appropriate" in timing_eval
        assert "timing_confidence" in timing_eval
        assert "can_proceed" in timing_eval
        assert "recommended_delay_minutes" in timing_eval
    
    @pytest.mark.asyncio
    async def test_evaluate_optimal_timing_failure(self, timing_predictor):
        """Test timing evaluation when analysis fails"""
        user_id = "test_user_123"
        user_context = {}
        intervention_analysis = {}
        
        result = await timing_predictor.evaluate_optimal_timing(
            user_id, user_context, intervention_analysis
        )
        
        assert result is not None
        assert result["timing_evaluation"]["timing_appropriate"] is False
        assert result["timing_evaluation"]["timing_confidence"] == 0.0
        assert result["timing_evaluation"]["can_proceed"] is False
    
    @pytest.mark.asyncio
    async def test_recent_assistance_gap_check(self, timing_predictor):
        """Test recent assistance gap checking"""
        user_id = "test_user_123"
        current_time = datetime.now(timezone.utc)
        
        result = await timing_predictor._check_recent_assistance_gap(user_id, current_time)
        
        assert result is not None
        assert "last_assistance_time" in result
        assert "hours_since_last" in result
        assert "sufficient_gap" in result
        assert "gap_score" in result
        
        # Verify gap calculation
        assert result["hours_since_last"] > 0
        assert result["sufficient_gap"] is True
        assert 0.0 <= result["gap_score"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_recent_assistance_gap_failure(self, timing_predictor):
        """Test recent assistance gap check when it fails"""
        user_id = "test_user_123"
        current_time = datetime.now(timezone.utc)
        
        # Mock failure by setting invalid configuration
        timing_predictor.timing_config = None
        
        result = await timing_predictor._check_recent_assistance_gap(user_id, current_time)
        
        assert result is not None
        assert result["last_assistance_time"] is None
        assert result["hours_since_last"] == 0
        assert result["sufficient_gap"] is False
        assert result["gap_score"] == 0.0
    
    @pytest.mark.asyncio
    async def test_activity_state_analysis(self, timing_predictor, sample_user_context):
        """Test current activity state analysis"""
        current_time = datetime.now(timezone.utc)
        
        result = await timing_predictor._analyze_current_activity_state(sample_user_context, current_time)
        
        assert result is not None
        assert "engagement_level" in result
        assert "last_interaction_minutes_ago" in result
        assert "time_of_day_appropriateness" in result
        assert "user_receptiveness_score" in result
        assert "activity_confidence" in result
        
        # Verify engagement level calculation
        assert 0.0 <= result["engagement_level"] <= 1.0
        assert 0.0 <= result["user_receptiveness_score"] <= 1.0
        assert 0.0 <= result["activity_confidence"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_activity_state_analysis_no_interactions(self, timing_predictor):
        """Test activity state analysis when user has no recent interactions"""
        user_context = {"recent_interactions": []}
        current_time = datetime.now(timezone.utc)
        
        result = await timing_predictor._analyze_current_activity_state(user_context, current_time)
        
        assert result is not None
        assert result["engagement_level"] == 0.3  # Default low engagement
        assert result["last_interaction_minutes_ago"] is None
    
    @pytest.mark.asyncio
    async def test_activity_state_analysis_failure(self, timing_predictor):
        """Test activity state analysis when it fails"""
        user_context = {"recent_interactions": [{"invalid": "data"}]}
        current_time = datetime.now(timezone.utc)
        
        result = await timing_predictor._analyze_current_activity_state(user_context, current_time)
        
        assert result is not None
        assert result["engagement_level"] == 0.5  # Fallback value
        assert result["user_receptiveness_score"] == 0.5
        assert result["activity_confidence"] == 0.3
    
    @pytest.mark.asyncio
    async def test_cultural_timing_appropriateness(self, timing_predictor, sample_user_context):
        """Test cultural timing appropriateness evaluation"""
        current_time = datetime.now(timezone.utc)
        
        result = await timing_predictor._evaluate_cultural_timing_appropriateness(
            sample_user_context["cultural_profile"], current_time
        )
        
        assert result is not None
        assert "primary_culture" in result
        assert "meal_time_appropriateness" in result
        assert "family_time_appropriateness" in result
        assert "overall_cultural_score" in result
        assert "cultural_guidelines_applied" in result
        
        assert result["primary_culture"] == "collectivist"
        assert 0.0 <= result["overall_cultural_score"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_cultural_timing_unknown_culture(self, timing_predictor):
        """Test cultural timing evaluation for unknown culture"""
        cultural_profile = {"primary_culture": "unknown"}
        current_time = datetime.now(timezone.utc)
        
        result = await timing_predictor._evaluate_cultural_timing_appropriateness(
            cultural_profile, current_time
        )
        
        assert result is not None
        assert result["primary_culture"] == "unknown"
        assert result["overall_cultural_score"] == 1.0  # Default score
        assert result["cultural_guidelines_applied"] == []
    
    @pytest.mark.asyncio
    async def test_cultural_timing_failure(self, timing_predictor):
        """Test cultural timing evaluation when it fails"""
        cultural_profile = None
        current_time = datetime.now(timezone.utc)
        
        result = await timing_predictor._evaluate_cultural_timing_appropriateness(
            cultural_profile, current_time
        )
        
        assert result is not None
        assert result["primary_culture"] == "unknown"
        assert result["overall_cultural_score"] == 1.0
    
    @pytest.mark.asyncio
    async def test_timing_appropriateness_score_calculation(self, timing_predictor):
        """Test timing appropriateness score calculation"""
        recent_assistance_check = {"gap_score": 0.8}
        activity_analysis = {"user_receptiveness_score": 0.7}
        cultural_timing = {"overall_cultural_score": 0.9}
        urgency_override = False
        
        score = await timing_predictor._calculate_timing_appropriateness_score(
            recent_assistance_check, activity_analysis, cultural_timing, urgency_override
        )
        
        # Expected: (0.8 * 0.3) + (0.7 * 0.4) + (0.9 * 0.3) = 0.24 + 0.28 + 0.27 = 0.79
        expected_score = 0.79
        assert abs(score - expected_score) < 0.01
    
    @pytest.mark.asyncio
    async def test_timing_score_urgency_override(self, timing_predictor):
        """Test timing score calculation with urgency override"""
        recent_assistance_check = {"gap_score": 0.3}
        activity_analysis = {"user_receptiveness_score": 0.4}
        cultural_timing = {"overall_cultural_score": 0.5}
        urgency_override = True
        
        score = await timing_predictor._calculate_timing_appropriateness_score(
            recent_assistance_check, activity_analysis, cultural_timing, urgency_override
        )
        
        assert score == 0.9  # High score for urgent situations
    
    @pytest.mark.asyncio
    async def test_timing_score_calculation_failure(self, timing_predictor):
        """Test timing score calculation when it fails"""
        recent_assistance_check = {}
        activity_analysis = {}
        cultural_timing = {}
        urgency_override = False
        
        score = await timing_predictor._calculate_timing_appropriateness_score(
            recent_assistance_check, activity_analysis, cultural_timing, urgency_override
        )
        
        assert score == 0.5  # Fallback score
    
    def test_engagement_level_calculation(self, timing_predictor):
        """Test user engagement level calculation"""
        current_time = datetime.now(timezone.utc)
        
        # Test with no interactions
        recent_interactions = []
        engagement = timing_predictor._calculate_engagement_level(recent_interactions, current_time)
        assert engagement == 0.3
        
        # Test with few interactions
        recent_interactions = [
            {"timestamp": (current_time - timedelta(hours=12)).isoformat()}
        ]
        engagement = timing_predictor._calculate_engagement_level(recent_interactions, current_time)
        assert engagement == 0.5
        
        # Test with many interactions
        recent_interactions = [
            {"timestamp": (current_time - timedelta(hours=6)).isoformat()},
            {"timestamp": (current_time - timedelta(hours=4)).isoformat()},
            {"timestamp": (current_time - timedelta(hours=2)).isoformat()},
            {"timestamp": (current_time - timedelta(hours=1)).isoformat()},
            {"timestamp": (current_time - timedelta(minutes=30)).isoformat()}
        ]
        engagement = timing_predictor._calculate_engagement_level(recent_interactions, current_time)
        assert engagement == 0.9
    
    def test_engagement_level_calculation_failure(self, timing_predictor):
        """Test engagement level calculation when it fails"""
        current_time = datetime.now(timezone.utc)
        recent_interactions = [{"invalid": "timestamp"}]
        
        engagement = timing_predictor._calculate_engagement_level(recent_interactions, current_time)
        assert engagement == 0.5  # Fallback value
    
    def test_time_of_day_appropriateness(self, timing_predictor):
        """Test time of day appropriateness evaluation"""
        # Test morning time
        morning_time = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0)
        appropriateness = timing_predictor._evaluate_time_of_day_appropriateness(morning_time)
        assert appropriateness == 0.8  # Morning weight
        
        # Test afternoon time
        afternoon_time = datetime.now(timezone.utc).replace(hour=15, minute=0, second=0, microsecond=0)
        appropriateness = timing_predictor._evaluate_time_of_day_appropriateness(afternoon_time)
        assert appropriateness == 0.9  # Afternoon weight
        
        # Test evening time
        evening_time = datetime.now(timezone.utc).replace(hour=19, minute=0, second=0, microsecond=0)
        appropriateness = timing_predictor._evaluate_time_of_day_appropriateness(evening_time)
        assert appropriateness == 0.7  # Evening weight
        
        # Test night time
        night_time = datetime.now(timezone.utc).replace(hour=23, minute=0, second=0, microsecond=0)
        appropriateness = timing_predictor._evaluate_time_of_day_appropriateness(night_time)
        assert appropriateness == 0.4  # Outside preferred windows
    
    def test_time_of_day_evaluation_failure(self, timing_predictor):
        """Test time of day evaluation when it fails"""
        # Mock failure by setting invalid configuration
        timing_predictor.timing_config = None
        
        current_time = datetime.now(timezone.utc)
        appropriateness = timing_predictor._evaluate_time_of_day_appropriateness(current_time)
        assert appropriateness == 0.5  # Fallback value
    
    def test_user_receptiveness_calculation(self, timing_predictor):
        """Test user receptiveness score calculation"""
        engagement_level = 0.8
        current_time = datetime.now(timezone.utc)
        
        # Test with no last interaction
        receptiveness = timing_predictor._calculate_user_receptiveness(
            engagement_level, None, current_time
        )
        expected = engagement_level * 0.7  # 0.8 * 0.7 = 0.56
        assert abs(receptiveness - expected) < 0.01
        
        # Test with recent interaction (1-4 hours ago - optimal window)
        last_interaction = current_time - timedelta(hours=2)
        receptiveness = timing_predictor._calculate_user_receptiveness(
            engagement_level, last_interaction, current_time
        )
        expected = (engagement_level * 0.6) + (1.0 * 0.4)  # (0.8 * 0.6) + (1.0 * 0.4) = 0.88
        assert abs(receptiveness - expected) < 0.01
        
        # Test with very recent interaction (too recent)
        last_interaction = current_time - timedelta(minutes=30)
        receptiveness = timing_predictor._calculate_user_receptiveness(
            engagement_level, last_interaction, current_time
        )
        expected = (engagement_level * 0.6) + (0.6 * 0.4)  # (0.8 * 0.6) + (0.6 * 0.4) = 0.72
        assert abs(receptiveness - expected) < 0.01
        
        # Test with old interaction (decay over time)
        last_interaction = current_time - timedelta(hours=8)
        receptiveness = timing_predictor._calculate_user_receptiveness(
            engagement_level, last_interaction, current_time
        )
        # Should be lower due to time decay
        assert receptiveness < 0.8
    
    def test_user_receptiveness_calculation_failure(self, timing_predictor):
        """Test user receptiveness calculation when it fails"""
        engagement_level = 0.8
        current_time = datetime.now(timezone.utc)
        last_interaction = "invalid_timestamp"
        
        receptiveness = timing_predictor._calculate_user_receptiveness(
            engagement_level, last_interaction, current_time
        )
        assert receptiveness == 0.5  # Fallback value
    
    def test_meal_time_appropriateness(self, timing_predictor):
        """Test meal time appropriateness evaluation"""
        # Test breakfast time
        breakfast_time = datetime.now(timezone.utc).replace(hour=7, minute=0, second=0, microsecond=0)
        appropriateness = timing_predictor._evaluate_meal_time_appropriateness(breakfast_time)
        assert appropriateness == 0.3  # Lower score during meal time
        
        # Test lunch time
        lunch_time = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
        appropriateness = timing_predictor._evaluate_meal_time_appropriateness(lunch_time)
        assert appropriateness == 0.3  # Lower score during meal time
        
        # Test dinner time
        dinner_time = datetime.now(timezone.utc).replace(hour=18, minute=0, second=0, microsecond=0)
        appropriateness = timing_predictor._evaluate_meal_time_appropriateness(dinner_time)
        assert appropriateness == 0.3  # Lower score during meal time
        
        # Test non-meal time
        non_meal_time = datetime.now(timezone.utc).replace(hour=14, minute=0, second=0, microsecond=0)
        appropriateness = timing_predictor._evaluate_meal_time_appropriateness(non_meal_time)
        assert appropriateness == 1.0  # Good score outside meal times
    
    def test_meal_time_evaluation_failure(self, timing_predictor):
        """Test meal time evaluation when it fails"""
        current_time = "invalid_time"
        appropriateness = timing_predictor._evaluate_meal_time_appropriateness(current_time)
        assert appropriateness == 1.0  # Fallback value
    
    def test_family_time_appropriateness(self, timing_predictor):
        """Test family time appropriateness evaluation"""
        # Test family time (evening)
        family_time = datetime.now(timezone.utc).replace(hour=20, minute=0, second=0, microsecond=0)
        appropriateness = timing_predictor._evaluate_family_time_appropriateness(family_time)
        assert appropriateness == 0.6  # Moderate score during family time
        
        # Test late night
        late_night = datetime.now(timezone.utc).replace(hour=23, minute=0, second=0, microsecond=0)
        appropriateness = timing_predictor._evaluate_family_time_appropriateness(late_night)
        assert appropriateness == 0.2  # Low score during late night
        
        # Test early morning
        early_morning = datetime.now(timezone.utc).replace(hour=3, minute=0, second=0, microsecond=0)
        appropriateness = timing_predictor._evaluate_family_time_appropriateness(early_morning)
        assert appropriateness == 0.2  # Low score during early morning
        
        # Test other hours
        other_time = datetime.now(timezone.utc).replace(hour=15, minute=0, second=0, microsecond=0)
        appropriateness = timing_predictor._evaluate_family_time_appropriateness(other_time)
        assert appropriateness == 1.0  # Good score during other hours
    
    def test_family_time_evaluation_failure(self, timing_predictor):
        """Test family time evaluation when it fails"""
        current_time = "invalid_time"
        appropriateness = timing_predictor._evaluate_family_time_appropriateness(current_time)
        assert appropriateness == 1.0  # Fallback value
    
    def test_fallback_timing_evaluation_creation(self, timing_predictor):
        """Test fallback timing evaluation creation"""
        fallback_evaluation = timing_predictor._create_fallback_timing_evaluation()
        
        assert fallback_evaluation is not None
        assert fallback_evaluation["timing_evaluation"]["timing_appropriate"] is False
        assert fallback_evaluation["timing_evaluation"]["timing_confidence"] == 0.0
        assert fallback_evaluation["timing_evaluation"]["can_proceed"] is False
        assert fallback_evaluation["timing_evaluation"]["recommended_delay_minutes"] == 60
        assert fallback_evaluation["urgency_override"] is False
        assert fallback_evaluation["timing_score"] == 0.0
        assert "evaluation_timestamp" in fallback_evaluation
