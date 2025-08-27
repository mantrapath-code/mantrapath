"""
Test suite for Cultural Sensitivity Engine

Comprehensive testing of the cultural sensitivity system that ensures
all proactive assistance respects cultural norms and preferences.
"""

import pytest
from unittest.mock import AsyncMock, patch

from src.core.cultural_sensitivity_engine import CulturalSensitivityEngine

class TestCulturalSensitivityEngine:
    """
    Test suite for the cultural sensitivity engine
    """
    
    @pytest.fixture
    def cultural_engine(self):
        """Create cultural sensitivity engine instance for testing"""
        return CulturalSensitivityEngine()
    
    @pytest.fixture
    def sample_cultural_profile(self):
        """Sample cultural profile for testing"""
        return {
            "primary_culture": "collectivist",
            "communication_style": "indirect",
            "family_involvement": True,
            "hierarchical_respect": True
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
    async def test_evaluate_cultural_appropriateness_success(self, cultural_engine, sample_cultural_profile, sample_intervention_analysis):
        """Test successful cultural appropriateness evaluation"""
        result = await cultural_engine.evaluate_cultural_appropriateness(
            sample_cultural_profile, sample_intervention_analysis
        )
        
        assert result is not None
        assert "culturally_appropriate" in result
        assert "appropriateness_score" in result
        assert "content_evaluation" in result
        assert "timing_evaluation" in result
        assert "adapted_content" in result
        assert "cultural_considerations" in result
        assert "primary_culture" in result
        assert "communication_style" in result
        
        # Verify cultural profile mapping
        assert result["primary_culture"] == "collectivist"
        assert result["communication_style"] == "indirect"
        
        # Verify appropriateness score
        assert 0.0 <= result["appropriateness_score"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_evaluate_cultural_appropriateness_failure(self, cultural_engine):
        """Test cultural appropriateness evaluation when it fails"""
        # Mock failure by setting invalid data
        cultural_engine.cultural_guidelines = None
        
        result = await cultural_engine.evaluate_cultural_appropriateness({}, {})
        
        assert result is not None
        assert result["culturally_appropriate"] is False
        assert result["appropriateness_score"] == 0.0
        assert result["primary_culture"] == "unknown"
    
    @pytest.mark.asyncio
    async def test_content_appropriateness_evaluation(self, cultural_engine, sample_intervention_analysis):
        """Test content appropriateness evaluation"""
        cultural_guidelines = {
            "intervention_adaptations": {
                "proactive_support": "Include family support emphasis"
            },
            "communication_preferences": {
                "directness": "indirect"
            }
        }
        
        result = await cultural_engine._evaluate_content_appropriateness(
            sample_intervention_analysis, cultural_guidelines
        )
        
        assert result is not None
        assert "appropriateness_score" in result
        assert "adaptation_available" in result
        assert "adaptation_text" in result
        assert "communication_style_compatible" in result
        assert "intervention_type_supported" in result
        
        # Verify adaptation availability
        assert result["adaptation_available"] is True
        assert "family support emphasis" in result["adaptation_text"]
        assert result["intervention_type_supported"] is True
    
    @pytest.mark.asyncio
    async def test_content_appropriateness_no_adaptations(self, cultural_engine):
        """Test content appropriateness when no adaptations available"""
        intervention_analysis = {
            "intervention_type": "unknown_type",
            "urgency_level": "low"
        }
        
        cultural_guidelines = {
            "intervention_adaptations": {},
            "communication_preferences": {"directness": "neutral"}
        }
        
        result = await cultural_engine._evaluate_content_appropriateness(
            intervention_analysis, cultural_guidelines
        )
        
        assert result is not None
        assert result["adaptation_available"] is False
        assert result["adaptation_text"] == ""
        assert result["intervention_type_supported"] is False
    
    @pytest.mark.asyncio
    async def test_content_appropriateness_failure(self, cultural_engine):
        """Test content appropriateness evaluation when it fails"""
        result = await cultural_engine._evaluate_content_appropriateness({}, {})
        
        assert result is not None
        assert result["appropriateness_score"] == 0.5
        assert result["adaptation_available"] is False
        assert result["communication_style_compatible"] is False
    
    @pytest.mark.asyncio
    async def test_timing_appropriateness_evaluation(self, cultural_engine, sample_cultural_profile):
        """Test timing appropriateness evaluation"""
        intervention_analysis = {
            "urgency_level": "low"
        }
        
        result = await cultural_engine._evaluate_timing_appropriateness(
            sample_cultural_profile, intervention_analysis
        )
        
        assert result is not None
        assert "appropriateness_score" in result
        assert "timing_considerations" in result
        assert "can_proceed" in result
        assert "urgency_override" in result
        
        # Verify timing score
        assert 0.0 <= result["appropriateness_score"] <= 1.0
        assert result["urgency_override"] is False
    
    @pytest.mark.asyncio
    async def test_timing_appropriateness_urgency_override(self, cultural_engine, sample_cultural_profile):
        """Test timing appropriateness with urgency override"""
        intervention_analysis = {
            "urgency_level": "critical"
        }
        
        result = await cultural_engine._evaluate_timing_appropriateness(
            sample_cultural_profile, intervention_analysis
        )
        
        assert result is not None
        assert result["appropriateness_score"] == 0.9
        assert result["urgency_override"] is True
        assert result["can_proceed"] is True
        assert "Urgency overrides cultural timing restrictions" in result["timing_considerations"]
    
    @pytest.mark.asyncio
    async def test_timing_appropriateness_failure(self, cultural_engine):
        """Test timing appropriateness evaluation when it fails"""
        result = await cultural_engine._evaluate_timing_appropriateness({}, {})
        
        assert result is not None
        assert result["appropriateness_score"] == 0.5
        assert result["can_proceed"] is False
        assert result["urgency_override"] is False
    
    @pytest.mark.asyncio
    async def test_content_cultural_adaptation(self, cultural_engine, sample_cultural_profile):
        """Test content cultural adaptation"""
        intervention_analysis = {
            "intervention_type": "proactive_support",
            "confidence": 0.8
        }
        
        cultural_guidelines = {
            "intervention_adaptations": {
                "proactive_support": "Include family support emphasis"
            }
        }
        
        result = await cultural_engine._adapt_content_for_culture(
            intervention_analysis, sample_cultural_profile, cultural_guidelines
        )
        
        assert result is not None
        assert "cultural_adaptation" in result
        assert "culturally_adapted" in result
        assert "cultural_context" in result
        
        # Verify adaptation
        assert result["culturally_adapted"] is True
        assert "family support emphasis" in result["cultural_adaptation"]
        
        # Verify cultural context
        cultural_context = result["cultural_context"]
        assert cultural_context["primary_culture"] == "collectivist"
        assert cultural_context["communication_style"] == "indirect"
        assert "guidelines_applied" in cultural_context
    
    @pytest.mark.asyncio
    async def test_content_cultural_adaptation_no_adaptations(self, cultural_engine, sample_cultural_profile):
        """Test content cultural adaptation when no adaptations available"""
        intervention_analysis = {
            "intervention_type": "unknown_type"
        }
        
        cultural_guidelines = {
            "intervention_adaptations": {}
        }
        
        result = await cultural_engine._adapt_content_for_culture(
            intervention_analysis, sample_cultural_profile, cultural_guidelines
        )
        
        assert result is not None
        assert result["culturally_adapted"] is False
        assert "cultural_context" in result
    
    @pytest.mark.asyncio
    async def test_content_cultural_adaptation_failure(self, cultural_engine):
        """Test content cultural adaptation when it fails"""
        result = await cultural_engine._adapt_content_for_culture({}, {}, {})
        
        # Should return original content if adaptation fails
        assert result == {}
    
    def test_cultural_guidelines_initialization(self, cultural_engine):
        """Test cultural guidelines initialization"""
        assert cultural_engine.cultural_guidelines is not None
        assert len(cultural_engine.cultural_guidelines) > 0
        
        # Verify supported cultures
        supported_cultures = ["collectivist", "individualist", "high_context", "low_context"]
        for culture in supported_cultures:
            assert culture in cultural_engine.cultural_guidelines
        
        # Verify collectivist guidelines
        collectivist_guidelines = cultural_engine.cultural_guidelines["collectivist"]
        assert "assistance_considerations" in collectivist_guidelines
        assert "communication_preferences" in collectivist_guidelines
        assert "timing_preferences" in collectivist_guidelines
        assert "intervention_adaptations" in collectivist_guidelines
        
        # Verify assistance considerations
        considerations = collectivist_guidelines["assistance_considerations"]
        assert "Emphasize family and community support" in considerations
        assert "Respect hierarchical relationships" in considerations
        
        # Verify communication preferences
        comm_prefs = collectivist_guidelines["communication_preferences"]
        assert comm_prefs["directness"] == "indirect"
        assert comm_prefs["context_level"] == "high"
        assert comm_prefs["family_involvement"] == "preferred"
        
        # Verify timing preferences
        timing_prefs = collectivist_guidelines["timing_preferences"]
        assert timing_prefs["family_time_respect"] is True
        assert timing_prefs["meal_time_awareness"] is True
        assert timing_prefs["religious_time_consideration"] is True
        
        # Verify intervention adaptations
        adaptations = collectivist_guidelines["intervention_adaptations"]
        assert "crisis_intervention" in adaptations
        assert "proactive_support" in adaptations
        assert "gentle_check_in" in adaptations
    
    def test_individualist_guidelines(self, cultural_engine):
        """Test individualist cultural guidelines"""
        individualist_guidelines = cultural_engine.cultural_guidelines["individualist"]
        
        # Verify assistance considerations
        considerations = individualist_guidelines["assistance_considerations"]
        assert "Emphasize personal agency and choice" in considerations
        assert "Respect individual privacy" in considerations
        
        # Verify communication preferences
        comm_prefs = individualist_guidelines["communication_preferences"]
        assert comm_prefs["directness"] == "direct"
        assert comm_prefs["context_level"] == "low"
        assert comm_prefs["professional_focus"] == "preferred"
        
        # Verify timing preferences
        timing_prefs = individualist_guidelines["timing_preferences"]
        assert timing_prefs["work_hour_respect"] is True
        assert timing_prefs["personal_schedule_focus"] is True
        assert timing_prefs["efficiency_valued"] is True
    
    def test_high_context_guidelines(self, cultural_engine):
        """Test high context cultural guidelines"""
        high_context_guidelines = cultural_engine.cultural_guidelines["high_context"]
        
        # Verify assistance considerations
        considerations = high_context_guidelines["assistance_considerations"]
        assert "Use indirect communication" in considerations
        assert "Respect implicit meanings" in considerations
        
        # Verify communication preferences
        comm_prefs = high_context_guidelines["communication_preferences"]
        assert comm_prefs["directness"] == "indirect"
        assert comm_prefs["context_level"] == "high"
        assert comm_prefs["relationship_focus"] == "preferred"
    
    def test_low_context_guidelines(self, cultural_engine):
        """Test low context cultural guidelines"""
        low_context_guidelines = cultural_engine.cultural_guidelines["low_context"]
        
        # Verify assistance considerations
        considerations = low_context_guidelines["assistance_considerations"]
        assert "Be direct and clear" in considerations
        assert "Provide explicit information" in considerations
        
        # Verify communication preferences
        comm_prefs = low_context_guidelines["communication_preferences"]
        assert comm_prefs["directness"] == "direct"
        assert comm_prefs["context_level"] == "low"
        assert comm_prefs["action_focus"] == "preferred"
    
    def test_sensitivity_thresholds(self, cultural_engine):
        """Test cultural sensitivity thresholds"""
        thresholds = cultural_engine.sensitivity_thresholds
        
        assert thresholds is not None
        assert "minimum_cultural_confidence" in thresholds
        assert "require_adaptation" in thresholds
        assert "respect_cultural_timing" in thresholds
        
        assert thresholds["minimum_cultural_confidence"] == 0.7
        assert thresholds["require_adaptation"] is True
        assert thresholds["respect_cultural_timing"] is True
    
    def test_fallback_cultural_evaluation_creation(self, cultural_engine):
        """Test fallback cultural evaluation creation"""
        fallback_evaluation = cultural_engine._create_fallback_cultural_evaluation()
        
        assert fallback_evaluation is not None
        assert fallback_evaluation["culturally_appropriate"] is False
        assert fallback_evaluation["appropriateness_score"] == 0.0
        assert fallback_evaluation["primary_culture"] == "unknown"
        assert fallback_evaluation["communication_style"] == "neutral"
        
        # Verify content evaluation
        content_eval = fallback_evaluation["content_evaluation"]
        assert content_eval["appropriateness_score"] == 0.0
        assert content_eval["adaptation_available"] is False
        assert content_eval["communication_style_compatible"] is False
        assert content_eval["intervention_type_supported"] is False
        
        # Verify timing evaluation
        timing_eval = fallback_evaluation["timing_evaluation"]
        assert timing_eval["appropriateness_score"] == 0.0
        assert timing_eval["can_proceed"] is False
        assert timing_eval["urgency_override"] is False
        
        # Verify cultural considerations
        assert fallback_evaluation["cultural_considerations"] == ["Cultural evaluation failed"]
    
    @pytest.mark.asyncio
    async def test_get_cultural_guidelines(self, cultural_engine):
        """Test getting cultural guidelines for specific culture"""
        collectivist_guidelines = await cultural_engine.get_cultural_guidelines("collectivist")
        
        assert collectivist_guidelines is not None
        assert "assistance_considerations" in collectivist_guidelines
        assert "communication_preferences" in collectivist_guidelines
        assert "timing_preferences" in collectivist_guidelines
        assert "intervention_adaptations" in collectivist_guidelines
    
    @pytest.mark.asyncio
    async def test_get_cultural_guidelines_unknown_culture(self, cultural_engine):
        """Test getting cultural guidelines for unknown culture"""
        unknown_guidelines = await cultural_engine.get_cultural_guidelines("unknown_culture")
        
        assert unknown_guidelines == {}
    
    @pytest.mark.asyncio
    async def test_add_cultural_guidelines(self, cultural_engine):
        """Test adding new cultural guidelines"""
        new_guidelines = {
            "assistance_considerations": ["Test consideration"],
            "communication_preferences": {"directness": "neutral"},
            "timing_preferences": {"test_timing": True}
        }
        
        success = await cultural_engine.add_cultural_guidelines("test_culture", new_guidelines)
        
        assert success is True
        
        # Verify guidelines were added
        test_guidelines = await cultural_engine.get_cultural_guidelines("test_culture")
        assert test_guidelines == new_guidelines
    
    @pytest.mark.asyncio
    async def test_add_cultural_guidelines_failure(self, cultural_engine):
        """Test adding cultural guidelines when it fails"""
        # Mock failure by setting invalid guidelines
        cultural_engine.cultural_guidelines = None
        
        success = await cultural_engine.add_cultural_guidelines("test_culture", {})
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_get_supported_cultures(self, cultural_engine):
        """Test getting list of supported cultures"""
        supported_cultures = await cultural_engine.get_supported_cultures()
        
        assert supported_cultures is not None
        assert len(supported_cultures) > 0
        
        # Verify expected cultures are included
        expected_cultures = ["collectivist", "individualist", "high_context", "low_context"]
        for culture in expected_cultures:
            assert culture in supported_cultures
    
    def test_cultural_guidelines_structure(self, cultural_engine):
        """Test comprehensive cultural guidelines structure"""
        for culture, guidelines in cultural_engine.cultural_guidelines.items():
            # Verify required sections exist
            assert "assistance_considerations" in guidelines
            assert "communication_preferences" in guidelines
            assert "intervention_adaptations" in guidelines
            
            # Verify assistance considerations is a list
            assert isinstance(guidelines["assistance_considerations"], list)
            assert len(guidelines["assistance_considerations"]) > 0
            
            # Verify communication preferences structure
            comm_prefs = guidelines["communication_preferences"]
            assert "directness" in comm_prefs
            assert "context_level" in comm_prefs
            
            # Verify intervention adaptations structure
            adaptations = guidelines["intervention_adaptations"]
            assert isinstance(adaptations, dict)
            
            # Some cultures may have timing preferences
            if "timing_preferences" in guidelines:
                timing_prefs = guidelines["timing_preferences"]
                assert isinstance(timing_prefs, dict)
