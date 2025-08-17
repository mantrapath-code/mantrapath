"""
Test suite for Contextual Help Engine

Comprehensive testing of the contextual help system that matches
user needs with appropriate assistance content.
"""

import pytest
from unittest.mock import AsyncMock, patch

from src.core.contextual_help_engine import ContextualHelpEngine

class TestContextualHelpEngine:
    """
    Test suite for the contextual help engine
    """
    
    @pytest.fixture
    def help_engine(self):
        """Create help engine instance for testing"""
        return ContextualHelpEngine()
    
    @pytest.fixture
    def sample_user_context(self):
        """Sample user context for testing"""
        return {
            "user_id": "test_user_123",
            "assistance_preferences": {
                "preferred_assistance_style": "gentle",
                "frequency": "moderate"
            }
        }
    
    @pytest.fixture
    def sample_intervention_analysis(self):
        """Sample intervention analysis for testing"""
        return {
            "intervention_needed": True,
            "intervention_type": "proactive_support",
            "urgency_level": "medium",
            "risk_factors": {"mood_decline": {"score": 0.7}}
        }
    
    @pytest.fixture
    def sample_cultural_evaluation(self):
        """Sample cultural evaluation for testing"""
        return {
            "primary_culture": "collectivist",
            "appropriateness_score": 0.85
        }
    
    @pytest.mark.asyncio
    async def test_find_contextual_help_success(self, help_engine, sample_user_context, sample_intervention_analysis, sample_cultural_evaluation):
        """Test successful contextual help finding"""
        result = await help_engine.find_contextual_help(
            sample_user_context, sample_intervention_analysis, sample_cultural_evaluation
        )
        
        assert result is not None
        assert len(result) > 0
        assert len(result) <= help_engine.help_matching_config["max_help_suggestions"]
        
        # Verify help content structure
        help_item = result[0]
        assert "id" in help_item
        assert "title" in help_item
        assert "content" in help_item
        assert "actions" in help_item
        assert "urgency" in help_item
    
    @pytest.mark.asyncio
    async def test_find_contextual_help_failure(self, help_engine):
        """Test contextual help finding when it fails"""
        # Mock failure by setting invalid data
        help_engine.help_content_db = None
        
        result = await help_engine.find_contextual_help({}, {}, {})
        
        assert result is not None
        assert len(result) > 0
        # Should return fallback content
        assert result[0]["fallback"] is True
    
    @pytest.mark.asyncio
    async def test_user_needs_analysis(self, help_engine, sample_intervention_analysis, sample_user_context):
        """Test user needs analysis"""
        result = await help_engine._analyze_user_needs(sample_intervention_analysis, sample_user_context)
        
        assert result is not None
        assert "primary_help_categories" in result
        assert "urgency_level" in result
        assert "risk_factors" in result
        assert "user_preferences" in result
        
        # Verify help categories
        assert "mood_support" in result["primary_help_categories"]
        assert result["urgency_level"] == "medium"
    
    @pytest.mark.asyncio
    async def test_user_needs_analysis_crisis_intervention(self, help_engine, sample_user_context):
        """Test user needs analysis for crisis intervention"""
        crisis_analysis = {
            "intervention_needed": True,
            "intervention_type": "crisis_intervention",
            "urgency_level": "critical"
        }
        
        result = await help_engine._analyze_user_needs(crisis_analysis, sample_user_context)
        
        assert "crisis_intervention" in result["primary_help_categories"]
        assert result["urgency_level"] == "critical"
    
    @pytest.mark.asyncio
    async def test_user_needs_analysis_gentle_check_in(self, help_engine, sample_user_context):
        """Test user needs analysis for gentle check-in"""
        check_in_analysis = {
            "intervention_needed": True,
            "intervention_type": "gentle_check_in",
            "urgency_level": "low"
        }
        
        result = await help_engine._analyze_user_needs(check_in_analysis, sample_user_context)
        
        assert "proactive_check_in" in result["primary_help_categories"]
        assert result["urgency_level"] == "low"
    
    @pytest.mark.asyncio
    async def test_user_needs_analysis_unknown_type(self, help_engine, sample_user_context):
        """Test user needs analysis for unknown intervention type"""
        unknown_analysis = {
            "intervention_needed": True,
            "intervention_type": "unknown_type",
            "urgency_level": "medium"
        }
        
        result = await help_engine._analyze_user_needs(unknown_analysis, sample_user_context)
        
        # Should default to proactive_check_in
        assert "proactive_check_in" in result["primary_help_categories"]
    
    @pytest.mark.asyncio
    async def test_help_content_matching(self, help_engine):
        """Test help content matching"""
        user_needs = {
            "primary_help_categories": ["mood_support"],
            "urgency_level": "low"
        }
        
        result = await help_engine._match_help_content(user_needs)
        
        assert result is not None
        assert len(result) > 0
        
        # Verify content matches category
        for item in result:
            assert item["urgency"] in ["low", "none"]
    
    @pytest.mark.asyncio
    async def test_help_content_matching_no_matches(self, help_engine):
        """Test help content matching when no specific matches found"""
        user_needs = {
            "primary_help_categories": ["unknown_category"],
            "urgency_level": "high"
        }
        
        result = await help_engine._match_help_content(user_needs)
        
        assert result is not None
        assert len(result) > 0
        # Should return general support content
        assert any("proactive_check_in" in item.get("id", "") for item in result)
    
    @pytest.mark.asyncio
    async def test_help_content_matching_failure(self, help_engine):
        """Test help content matching when it fails"""
        # Mock failure
        help_engine.help_content_db = None
        
        result = await help_engine._match_help_content({})
        
        assert result is not None
        assert len(result) > 0
        # Should return fallback content
        assert result[0]["fallback"] is True
    
    @pytest.mark.asyncio
    async def test_cultural_adaptation(self, help_engine, sample_cultural_evaluation):
        """Test cultural adaptation of help content"""
        help_content = [
            {
                "id": "test_001",
                "title": "Test Help",
                "content": "Test content",
                "actions": ["Action 1"],
                "urgency": "low",
                "cultural_adaptations": {
                    "collectivist": "Family emphasis",
                    "individualist": "Personal focus"
                }
            }
        ]
        
        result = await help_engine._adapt_help_for_culture(help_content, sample_cultural_evaluation)
        
        assert result is not None
        assert len(result) == 1
        
        adapted_item = result[0]
        assert adapted_item["cultural_adaptation_applied"] is True
        assert "Family emphasis" in adapted_item["content"]
    
    @pytest.mark.asyncio
    async def test_cultural_adaptation_no_adaptations(self, help_engine, sample_cultural_evaluation):
        """Test cultural adaptation when no adaptations available"""
        help_content = [
            {
                "id": "test_001",
                "title": "Test Help",
                "content": "Test content",
                "actions": ["Action 1"],
                "urgency": "low",
                "cultural_adaptations": {}
            }
        ]
        
        result = await help_engine._adapt_help_for_culture(help_content, sample_cultural_evaluation)
        
        assert result is not None
        assert len(result) == 1
        
        adapted_item = result[0]
        assert adapted_item["cultural_adaptation_applied"] is False
        assert adapted_item["content"] == "Test content"  # Unchanged
    
    @pytest.mark.asyncio
    async def test_cultural_adaptation_unknown_culture(self, help_engine):
        """Test cultural adaptation for unknown culture"""
        help_content = [
            {
                "id": "test_001",
                "title": "Test Help",
                "content": "Test content",
                "actions": ["Action 1"],
                "urgency": "low",
                "cultural_adaptations": {
                    "collectivist": "Family emphasis"
                }
            }
        ]
        
        cultural_evaluation = {"primary_culture": "unknown"}
        
        result = await help_engine._adapt_help_for_culture(help_content, cultural_evaluation)
        
        assert result is not None
        assert len(result) == 1
        
        adapted_item = result[0]
        assert adapted_item["cultural_adaptation_applied"] is False
    
    @pytest.mark.asyncio
    async def test_cultural_adaptation_failure(self, help_engine):
        """Test cultural adaptation when it fails"""
        help_content = [{"invalid": "content"}]
        cultural_evaluation = {"primary_culture": "collectivist"}
        
        result = await help_engine._adapt_help_for_culture(help_content, cultural_evaluation)
        
        # Should return original content if adaptation fails
        assert result == help_content
    
    @pytest.mark.asyncio
    async def test_help_prioritization(self, help_engine):
        """Test help suggestions prioritization"""
        help_content = [
            {
                "id": "high_priority",
                "title": "High Priority Help",
                "content": "High priority content",
                "actions": ["Action 1", "Action 2", "Action 3"],
                "urgency": "medium",
                "cultural_adaptation_applied": True
            },
            {
                "id": "low_priority",
                "title": "Low Priority Help",
                "content": "Low priority content",
                "actions": ["Action 1"],
                "urgency": "low",
                "cultural_adaptation_applied": False
            }
        ]
        
        user_needs = {
            "urgency_level": "medium",
            "user_preferences": {"preferred_assistance_style": "gentle"}
        }
        
        result = await help_engine._prioritize_help_suggestions(help_content, user_needs)
        
        assert result is not None
        assert len(result) == 2
        
        # High priority should come first
        assert result[0]["id"] == "high_priority"
        assert result[1]["id"] == "low_priority"
    
    @pytest.mark.asyncio
    async def test_help_prioritization_failure(self, help_engine):
        """Test help prioritization when it fails"""
        help_content = [{"invalid": "content"}]
        user_needs = {}
        
        result = await help_engine._prioritize_help_suggestions(help_content, user_needs)
        
        # Should return original content if prioritization fails
        assert result == help_content
    
    def test_help_relevance_scoring(self, help_engine):
        """Test help relevance score calculation"""
        help_content = {
            "urgency": "medium",
            "cultural_adaptation_applied": True,
            "actions": ["Action 1", "Action 2", "Action 3"],
            "content": "Gentle support content"
        }
        
        user_needs = {
            "urgency_level": "medium",
            "user_preferences": {"preferred_assistance_style": "gentle"}
        }
        
        score = help_engine._calculate_help_relevance_score(help_content, user_needs)
        
        # Expected score: 0.4 (urgency match) + 0.2 (cultural adaptation) + 0.2 (actions) + 0.1 (preference) = 0.9
        expected_score = 0.9
        assert abs(score - expected_score) < 0.01
    
    def test_help_relevance_scoring_no_match(self, help_engine):
        """Test help relevance scoring when no matches found"""
        help_content = {
            "urgency": "low",
            "cultural_adaptation_applied": False,
            "actions": ["Action 1"],
            "content": "Regular content"
        }
        
        user_needs = {
            "urgency_level": "high",
            "user_preferences": {"preferred_assistance_style": "direct"}
        }
        
        score = help_engine._calculate_help_relevance_score(help_content, user_needs)
        
        # Expected score: 0.1 (urgency mismatch) + 0.0 (no cultural adaptation) + 0.1 (few actions) + 0.0 (no preference match) = 0.2
        expected_score = 0.2
        assert abs(score - expected_score) < 0.01
    
    def test_help_relevance_scoring_failure(self, help_engine):
        """Test help relevance scoring when it fails"""
        help_content = {"invalid": "content"}
        user_needs = {}
        
        score = help_engine._calculate_help_relevance_score(help_content, user_needs)
        
        assert score == 0.5  # Fallback score
    
    def test_fallback_help_content(self, help_engine):
        """Test fallback help content generation"""
        fallback_content = help_engine._get_fallback_help_content()
        
        assert fallback_content is not None
        assert len(fallback_content) == 1
        
        fallback_item = fallback_content[0]
        assert fallback_item["id"] == "fallback_001"
        assert fallback_item["title"] == "General Support"
        assert fallback_item["fallback"] is True
        assert fallback_item["urgency"] == "none"
    
    @pytest.mark.asyncio
    async def test_add_help_content(self, help_engine):
        """Test adding new help content"""
        new_content = {
            "title": "New Help Content",
            "content": "New help content description",
            "actions": ["New Action 1", "New Action 2"],
            "urgency": "medium"
        }
        
        success = await help_engine.add_help_content("new_category", new_content)
        
        assert success is True
        
        # Verify content was added
        categories = await help_engine.get_help_categories()
        assert "new_category" in categories
        
        content = await help_engine.get_content_by_category("new_category")
        assert len(content) == 1
        assert content[0]["title"] == "New Help Content"
        assert "id" in content[0]  # Should have auto-generated ID
    
    @pytest.mark.asyncio
    async def test_add_help_content_with_id(self, help_engine):
        """Test adding help content with existing ID"""
        new_content = {
            "id": "custom_id_001",
            "title": "Custom ID Content",
            "content": "Content with custom ID",
            "actions": ["Action 1"],
            "urgency": "low"
        }
        
        success = await help_engine.add_help_content("custom_category", new_content)
        
        assert success is True
        
        # Verify custom ID was preserved
        content = await help_engine.get_content_by_category("custom_category")
        assert content[0]["id"] == "custom_id_001"
    
    @pytest.mark.asyncio
    async def test_add_help_content_failure(self, help_engine):
        """Test adding help content when it fails"""
        # Mock failure by setting invalid database
        help_engine.help_content_db = None
        
        new_content = {"title": "Test Content"}
        success = await help_engine.add_help_content("test_category", new_content)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_get_help_categories(self, help_engine):
        """Test getting help categories"""
        categories = await help_engine.get_help_categories()
        
        assert categories is not None
        assert len(categories) > 0
        assert "crisis_intervention" in categories
        assert "mood_support" in categories
        assert "proactive_check_in" in categories
        assert "behavioral_guidance" in categories
    
    @pytest.mark.asyncio
    async def test_get_content_by_category(self, help_engine):
        """Test getting content by category"""
        mood_content = await help_engine.get_content_by_category("mood_support")
        
        assert mood_content is not None
        assert len(mood_content) > 0
        
        # Verify content structure
        content_item = mood_content[0]
        assert "id" in content_item
        assert "title" in content_item
        assert "content" in content_item
        assert "actions" in content_item
        assert "urgency" in content_item
    
    @pytest.mark.asyncio
    async def test_get_content_by_unknown_category(self, help_engine):
        """Test getting content by unknown category"""
        content = await help_engine.get_content_by_category("unknown_category")
        
        assert content == []
    
    def test_help_content_initialization(self, help_engine):
        """Test help content database initialization"""
        assert help_engine.help_content_db is not None
        assert len(help_engine.help_content_db) > 0
        
        # Verify default categories exist
        assert "crisis_intervention" in help_engine.help_content_db
        assert "mood_support" in help_engine.help_content_db
        assert "proactive_check_in" in help_engine.help_content_db
        assert "behavioral_guidance" in help_engine.help_content_db
        
        # Verify content structure
        for category, content_list in help_engine.help_content_db.items():
            assert isinstance(content_list, list)
            for content_item in content_list:
                assert "id" in content_item
                assert "title" in content_item
                assert "content" in content_item
                assert "actions" in content_item
                assert "urgency" in content_item
                assert "cultural_adaptations" in content_item
    
    def test_help_matching_config(self, help_engine):
        """Test help matching configuration"""
        config = help_engine.help_matching_config
        
        assert config is not None
        assert "relevance_threshold" in config
        assert "max_help_suggestions" in config
        assert "cultural_adaptation_required" in config
        
        assert config["relevance_threshold"] == 0.6
        assert config["max_help_suggestions"] == 3
        assert config["cultural_adaptation_required"] is True
