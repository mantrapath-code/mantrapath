"""
Enhanced Community Service with Psychology-Based Features
Implements calming colors, unified community management, and personalized feeds
"""
from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import sys
import json
import asyncio

# Add parent directories to path
sys.path.append('/app')
sys.path.append('/app/shared')

from shared.database import get_db, engine
from shared.models import (
    CommunityForum, ForumThread, ThreadReply, ForumMembership, Like, Base, 
    Forum, ForumReply, User, UserProfile, CommunityEvent, Challenge, 
    EventParticipant, ChallengeParticipant, ChallengeProgress, EventComment,
    ChallengeComment, EventFeedback, ChallengeReflection, CommentLike, CommunityStats,
    ChallengeInvitation, ChallengeLeaderboard
)
from shared.auth import get_current_user
from psychology_models import (
    WellnessColors, PsychologicalFocus, CommunityHubType,
    CommunityThemeConfig, PersonalizedFeedPreferences, FeedItem,
    CommunityRecommendation, CalmingInteraction, ConversationStream,
    WellnessResource, CommunityAnalytics, CommunityHubResponse,
    PersonalizedFeedResponse, CommunityDashboardResponse,
    CreateCommunityHubRequest, FeedRequest, CommunityJoinRequest,
    CommunityPsychologyUtils
)

app = FastAPI(
    title="MantraPath Enhanced Community Service",
    description="Psychology-aware community service with calming design and unified experience",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Psychology-aware community service
class EnhancedCommunityService:
    """Enhanced community service with psychological wellness focus"""
    
    def __init__(self):
        self.wellness_colors = WellnessColors()
        self.psychology_utils = CommunityPsychologyUtils()
    
    async def get_personalized_theme(self, user_id: str, current_mood: str = None, 
                                   stress_level: float = 0.5) -> CommunityThemeConfig:
        """Get personalized theme based on user's psychological state"""
        
        # Get mood-appropriate colors
        mood_colors = self.wellness_colors.get_mood_colors(current_mood or "neutral")
        
        # Adjust for stress level
        if stress_level > 0.7:
            # High stress - prioritize most calming colors
            stress_colors = ["calm_blue", "sage_green", "lavender"]
            primary_colors = stress_colors
        else:
            primary_colors = mood_colors
        
        calming_score = self.wellness_colors.get_calming_score(primary_colors)
        
        return CommunityThemeConfig(
            primary_colors=primary_colors,
            mood_responsive=True,
            calming_score=calming_score,
            psychological_focus="general_wellness",
            time_based_adjustment=True,
            stress_response_colors=["calm_blue", "sage_green", "lavender"]
        )
    
    async def create_personalized_feed(self, user_id: str, preferences: Dict = None,
                                     mood_context: str = None) -> PersonalizedFeedResponse:
        """Create psychology-optimized personalized community feed"""
        
        # Get user's psychological profile (mock implementation)
        psychological_profile = {
            "anxiety_level": 0.3,
            "stress_level": 0.4,
            "social_preference": 0.7,
            "support_seeking": 0.8
        }
        
        # Generate feed items based on psychological relevance
        feed_items = []
        
        # Mock feed items with psychological scoring
        sample_items = [
            {
                "id": "feed_1",
                "content_type": "forum_post",
                "content_id": "post_123",
                "community_hub_id": "hub_anxiety_support",
                "title": "Breathing techniques that actually work",
                "preview": "I've been struggling with anxiety and found these breathing exercises really helpful...",
                "author": {"name": "Sarah M.", "id": "user_456"},
                "created_at": datetime.now() - timedelta(hours=2),
                "psychological_relevance_score": 0.9,
                "engagement_prediction": 0.8,
                "calming_effect_rating": 0.9,
                "interaction_count": 24,
                "urgency_level": "low",
                "wellness_tags": ["anxiety", "breathing", "techniques", "self-care"]
            },
            {
                "id": "feed_2", 
                "content_type": "challenge_update",
                "content_id": "challenge_234",
                "community_hub_id": "hub_mindfulness",
                "title": "7-Day Mindfulness Challenge - Day 3",
                "preview": "Today's focus: Mindful walking. Take 10 minutes to walk slowly and notice...",
                "author": {"name": "Mindfulness Community", "id": "community_mindfulness"},
                "created_at": datetime.now() - timedelta(hours=1),
                "psychological_relevance_score": 0.7,
                "engagement_prediction": 0.6,
                "calming_effect_rating": 0.8,
                "interaction_count": 12,
                "urgency_level": "low",
                "wellness_tags": ["mindfulness", "walking", "meditation", "challenge"]
            },
            {
                "id": "feed_3",
                "content_type": "event",
                "content_id": "event_345",
                "community_hub_id": "hub_support_group",
                "title": "Virtual Support Circle - Tonight 7PM",
                "preview": "Join us for a safe space to share and listen. All are welcome...",
                "author": {"name": "Support Team", "id": "support_facilitators"},
                "created_at": datetime.now() - timedelta(minutes=30),
                "psychological_relevance_score": 0.8,
                "engagement_prediction": 0.9,
                "calming_effect_rating": 0.7,
                "interaction_count": 8,
                "urgency_level": "medium",
                "wellness_tags": ["support", "community", "sharing", "virtual"]
            }
        ]
        
        # Convert to FeedItem objects and sort by psychological relevance
        for item in sample_items:
            feed_item = FeedItem(**item)
            feed_items.append(feed_item)
        
        # Sort by psychological relevance and engagement prediction
        feed_items.sort(key=lambda x: (x.psychological_relevance_score + x.engagement_prediction) / 2, 
                       reverse=True)
        
        # Generate wellness tips based on mood context
        wellness_tips = self.psychology_utils.generate_calming_suggestions(
            mood_context or "neutral", 
            psychological_profile.get("stress_level", 0.5)
        )
        
        # Generate community recommendations
        recommendations = [
            CommunityRecommendation(
                community_hub_id="hub_anxiety_support",
                name="Anxiety Support Circle",
                psychological_match_score=0.9,
                description="A supportive community for managing anxiety together",
                member_count=1247,
                activity_level="high",
                wellness_focus="anxiety_support",
                recommended_reason="High match for your wellness goals",
                calming_score=0.9,
                support_quality_rating=4.8
            ),
            CommunityRecommendation(
                community_hub_id="hub_mindfulness",
                name="Mindfulness Practice Hub",
                psychological_match_score=0.7,
                description="Daily mindfulness practices and meditation guidance",
                member_count=892,
                activity_level="medium",
                wellness_focus="mindfulness",
                recommended_reason="Great for developing calm awareness",
                calming_score=0.95,
                support_quality_rating=4.6
            )
        ]
        
        return PersonalizedFeedResponse(
            user_id=user_id,
            feed_items=feed_items,
            psychological_wellness_tips=wellness_tips,
            calming_suggestions=[
                "Your feed is optimized for calming interactions",
                "Take breaks between posts to breathe mindfully",
                "Remember: it's okay to step away if you need space"
            ],
            community_recommendations=recommendations,
            crisis_resources=[],  # Would include actual crisis resources
            mood_check_prompt="How are you feeling after browsing your community feed?"
        )
    
    async def get_calming_community_dashboard(self, user_id: str, 
                                            current_mood: str = None) -> CommunityDashboardResponse:
        """Get mood-responsive community dashboard"""
        
        # Get personalized theme
        theme_config = await self.get_personalized_theme(user_id, current_mood)
        
        # Get active communities with psychological focus
        active_communities = [
            CommunityHubResponse(
                id="hub_anxiety_support",
                name="Anxiety Support Circle", 
                description="A safe space for anxiety support and coping strategies",
                hub_type="support_group",
                psychological_focus="anxiety_support",
                member_count=1247,
                activity_level="high",
                wellness_score=4.2,
                calming_score=0.9,
                theme_config=theme_config,
                recent_activity=[],
                support_quality_rating=4.8,
                crisis_support_available=True
            ),
            CommunityHubResponse(
                id="hub_mindfulness",
                name="Mindfulness Practice Hub",
                description="Daily mindfulness and meditation community",
                hub_type="interest_based", 
                psychological_focus="mindfulness",
                member_count=892,
                activity_level="medium",
                wellness_score=4.5,
                calming_score=0.95,
                theme_config=theme_config,
                recent_activity=[],
                support_quality_rating=4.6,
                crisis_support_available=False
            )
        ]
        
        # Generate calming interactions
        suggested_interactions = [
            CalmingInteraction(
                interaction_type="gentle_check_in",
                calming_score=0.8,
                recommended_colors=theme_config.primary_colors,
                suggested_tone="warm and supportive",
                breathing_prompt="Take three deep breaths before engaging",
                mindfulness_tip="Notice your intention for joining the community today",
                supportive_language_suggestions=[
                    "I hear you and appreciate your sharing",
                    "Thank you for being vulnerable with us",
                    "You're not alone in this experience"
                ],
                crisis_escalation_threshold=0.8
            )
        ]
        
        return CommunityDashboardResponse(
            user_mood_context=current_mood or "neutral",
            recommended_colors=theme_config.primary_colors,
            calming_score=theme_config.calming_score,
            active_communities=active_communities,
            suggested_interactions=suggested_interactions,
            wellness_goals_progress={
                "anxiety_management": 0.7,
                "mindfulness_practice": 0.4,
                "social_connection": 0.8
            },
            support_network_status={
                "active_supporters": 12,
                "recent_interactions": 8,
                "crisis_contacts": 3
            },
            crisis_support_access={
                "hotline": "988",
                "text_support": "Text HOME to 741741",
                "emergency": "911"
            }
        )

# Initialize service
community_service = EnhancedCommunityService()

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Enhanced Community Service",
        "version": "2.0.0",
        "psychology_features": "enabled"
    }

@app.get("/community-hubs/{user_id}/personalized")
async def get_personalized_community_hubs(
    user_id: str,
    mood: Optional[str] = Query(None, description="Current user mood"),
    stress_level: Optional[float] = Query(None, description="Current stress level 0-1"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get psychologically matched community hubs for user"""
    
    try:
        dashboard = await community_service.get_calming_community_dashboard(
            user_id, mood
        )
        return {
            "success": True,
            "community_hubs": dashboard.active_communities,
            "theme_config": {
                "colors": dashboard.recommended_colors,
                "calming_score": dashboard.calming_score
            },
            "wellness_context": dashboard.user_mood_context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting community hubs: {str(e)}")

@app.post("/community-feeds/create")
async def create_personalized_feed(
    feed_request: FeedRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create psychology-optimized community feed"""
    
    try:
        feed_response = await community_service.create_personalized_feed(
            feed_request.user_id,
            feed_request.content_preferences,
            feed_request.mood_context
        )
        return {
            "success": True,
            "feed": feed_response,
            "psychology_insights": {
                "calming_optimization": True,
                "crisis_support_ready": len(feed_response.crisis_resources) > 0,
                "wellness_tips_count": len(feed_response.psychological_wellness_tips)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating feed: {str(e)}")

@app.get("/communities/{community_id}/calming-dashboard")
async def get_calming_community_dashboard_endpoint(
    community_id: str,
    user_id: str = Query(..., description="User ID for personalization"),
    mood: Optional[str] = Query(None, description="Current mood context"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mood-responsive community dashboard"""
    
    try:
        dashboard = await community_service.get_calming_community_dashboard(user_id, mood)
        return {
            "success": True,
            "dashboard": dashboard,
            "psychology_features": {
                "mood_responsive": True,
                "crisis_support": dashboard.crisis_support_access,
                "calming_score": dashboard.calming_score
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dashboard: {str(e)}")

@app.get("/wellness-colors/mood/{mood}")
async def get_mood_colors(mood: str):
    """Get calming colors for specific mood"""
    
    try:
        colors = WellnessColors.get_mood_colors(mood)
        calming_score = WellnessColors.get_calming_score(colors)
        
        return {
            "success": True,
            "mood": mood,
            "recommended_colors": colors,
            "color_hex_values": {color: WellnessColors.CALM_PALETTE[color] for color in colors},
            "calming_score": calming_score,
            "psychology_explanation": f"These colors are selected to provide psychological comfort for {mood} mood"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting mood colors: {str(e)}")

@app.post("/communities/join-with-support")
async def join_community_with_psychological_support(
    join_request: CommunityJoinRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join community with psychological consideration and support setup"""
    
    try:
        # Here you would implement the actual community joining logic
        # with psychological profiling and support network setup
        
        return {
            "success": True,
            "message": "Successfully joined community with psychological support",
            "community_id": join_request.community_hub_id,
            "support_features": {
                "crisis_support_enabled": True,
                "mood_tracking_integrated": True,
                "calming_interactions_available": True,
                "wellness_goal_alignment": True
            },
            "next_steps": [
                "Complete your wellness profile",
                "Set your community interaction preferences", 
                "Connect with support buddies",
                "Explore calming community features"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error joining community: {str(e)}")

@app.get("/psychology/crisis-detection/{user_id}")
async def check_crisis_indicators(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check for crisis indicators and provide appropriate resources"""
    
    try:
        # This would implement actual crisis detection logic
        # analyzing user interactions, mood patterns, language use
        
        crisis_level = "low"  # "low", "medium", "high", "critical"
        
        response = {
            "success": True,
            "user_id": user_id,
            "crisis_level": crisis_level,
            "immediate_support_needed": False,
            "resources": [],
            "support_contacts": {
                "crisis_hotline": "988",
                "text_support": "Text HOME to 741741",
                "emergency": "911"
            }
        }
        
        if crisis_level in ["high", "critical"]:
            response["immediate_support_needed"] = True
            response["automated_interventions"] = [
                "Crisis counselor notification sent",
                "Emergency contacts alerted",
                "Calming resources provided"
            ]
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking crisis indicators: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
