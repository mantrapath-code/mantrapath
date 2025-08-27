"""
Community Management Service
Handles community operations with psychology-based features
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import uuid

from models.community_models import (
    CommunityHub, CommunityConversation, ConversationReply, 
    CommunityReaction, CommunityContent, UserPsychologicalProfile,
    CommunityHubMembership, CommunityFeedItem
)
from utils.psychology_utils import PsychologyUtils, CommunityAnalytics
from config.psychology_config import DEFAULT_CALMING_THEME, PSYCHOLOGICAL_FOCUS_AREAS


class CommunityService:
    """Core community management with psychology-based features"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_community_hub(self, hub_data: Dict, creator_id: str) -> CommunityHub:
        """Create a new community hub with psychological configuration"""
        # Get creator's psychological profile for theme customization
        creator_profile = self.get_user_psychological_profile(creator_id)
        
        # Generate appropriate theme based on psychological focus
        psychological_focus = hub_data.get("psychological_focus", "general_wellness")
        color_theme = self._generate_hub_theme(psychological_focus, creator_profile)
        
        hub = CommunityHub(
            name=hub_data["name"],
            description=hub_data.get("description"),
            hub_type=hub_data.get("hub_type", "public"),
            psychological_focus=psychological_focus,
            color_theme=color_theme,
            created_by=creator_id
        )
        
        self.db.add(hub)
        self.db.flush()
        
        # Create membership for creator
        membership = CommunityHubMembership(
            user_id=creator_id,
            hub_id=hub.id,
            role="admin"
        )
        self.db.add(membership)
        
        # Initialize hub with welcome conversation
        welcome_conversation = self._create_welcome_conversation(hub.id, creator_id)
        self.db.add(welcome_conversation)
        
        self.db.commit()
        return hub
    
    def join_community_hub(self, hub_id: str, user_id: str) -> CommunityHubMembership:
        """Join a community hub with psychological onboarding"""
        # Check if already a member
        existing = self.db.query(CommunityHubMembership).filter(
            and_(
                CommunityHubMembership.hub_id == hub_id,
                CommunityHubMembership.user_id == user_id,
                CommunityHubMembership.is_active == True
            )
        ).first()
        
        if existing:
            return existing
        
        # Get user's psychological profile
        user_profile = self.get_user_psychological_profile(user_id)
        
        membership = CommunityHubMembership(
            user_id=user_id,
            hub_id=hub_id,
            psychological_preferences=user_profile.preferred_colors if user_profile else None
        )
        
        self.db.add(membership)
        
        # Update hub member count
        hub = self.db.query(CommunityHub).filter(CommunityHub.id == hub_id).first()
        if hub:
            hub.member_count += 1
        
        self.db.commit()
        return membership
    
    def create_conversation(self, conversation_data: Dict, author_id: str) -> CommunityConversation:
        """Create a conversation with psychological analysis"""
        content = conversation_data["content"]
        
        # Analyze content for psychological indicators
        calming_score = PsychologyUtils.calculate_calming_score(content)
        supportive_score = PsychologyUtils.analyze_supportive_language(content)
        is_crisis, crisis_indicators = PsychologyUtils.detect_crisis_indicators(content)
        
        # Determine psychological tone
        if supportive_score > 0.7:
            psychological_tone = "supportive"
        elif calming_score > 0.7:
            psychological_tone = "calming"
        elif calming_score < 0.3:
            psychological_tone = "concerning"
        else:
            psychological_tone = "neutral"
        
        conversation = CommunityConversation(
            hub_id=conversation_data["hub_id"],
            conversation_type=conversation_data.get("conversation_type", "forum"),
            title=conversation_data["title"],
            content=content,
            author_id=author_id,
            psychological_tone=psychological_tone,
            calming_score=calming_score,
            mood_tags=conversation_data.get("mood_tags", []),
            crisis_flag=is_crisis
        )
        
        self.db.add(conversation)
        self.db.flush()
        
        # If crisis detected, trigger support workflow
        if is_crisis:
            self._handle_crisis_conversation(conversation.id, author_id, crisis_indicators)
        
        # Update community feed
        self._add_to_community_feeds(conversation)
        
        self.db.commit()
        return conversation
    
    def create_reply(self, reply_data: Dict, author_id: str) -> ConversationReply:
        """Create a reply with psychological analysis"""
        content = reply_data["content"]
        
        # Analyze psychological aspects
        calming_score = PsychologyUtils.calculate_calming_score(content)
        supportive_score = PsychologyUtils.analyze_supportive_language(content)
        
        psychological_tone = "supportive" if supportive_score > 0.6 else "neutral"
        
        reply = ConversationReply(
            conversation_id=reply_data["conversation_id"],
            parent_reply_id=reply_data.get("parent_reply_id"),
            content=content,
            author_id=author_id,
            psychological_tone=psychological_tone,
            calming_score=calming_score,
            supportive_language_score=supportive_score
        )
        
        self.db.add(reply)
        
        # Update conversation reply count
        conversation = self.db.query(CommunityConversation).filter(
            CommunityConversation.id == reply_data["conversation_id"]
        ).first()
        if conversation:
            conversation.reply_count += 1
            conversation.updated_at = datetime.utcnow()
        
        self.db.commit()
        return reply
    
    def get_personalized_feed(self, user_id: str, limit: int = 20, **filters) -> List[Dict]:
        """Generate personalized community feed based on psychology"""
        user_profile = self.get_user_psychological_profile(user_id)
        
        # Get user's community memberships
        memberships = self.db.query(CommunityHubMembership).filter(
            and_(
                CommunityHubMembership.user_id == user_id,
                CommunityHubMembership.is_active == True
            )
        ).all()
        
        hub_ids = [m.hub_id for m in memberships]
        
        if not hub_ids:
            return []
        
        # Get recent conversations from user's communities
        conversations = self.db.query(CommunityConversation).filter(
            and_(
                CommunityConversation.hub_id.in_(hub_ids),
                CommunityConversation.is_active == True,
                CommunityConversation.created_at > datetime.utcnow() - timedelta(days=7)
            )
        ).order_by(desc(CommunityConversation.created_at)).limit(limit * 2).all()
        
        # Score and rank conversations
        scored_conversations = []
        for conv in conversations:
            score = PsychologyUtils.calculate_feed_score(
                {
                    "content": conv.content,
                    "content_type": conv.conversation_type,
                    "calming_score": conv.calming_score,
                    "created_at": conv.created_at
                },
                {
                    "wellness_goals": user_profile.wellness_goals if user_profile else [],
                    "preferred_psychological_focus": user_profile.preferred_psychological_focus if user_profile else [],
                    "interaction_patterns": user_profile.interaction_patterns if user_profile else {}
                }
            )
            
            scored_conversations.append({
                "conversation": conv,
                "score": score,
                "psychological_relevance": score
            })
        
        # Sort by score and return top items
        scored_conversations.sort(key=lambda x: x["score"], reverse=True)
        return scored_conversations[:limit]
    
    def get_user_psychological_profile(self, user_id: str) -> Optional[UserPsychologicalProfile]:
        """Get or create user's psychological profile"""
        profile = self.db.query(UserPsychologicalProfile).filter(
            UserPsychologicalProfile.user_id == user_id
        ).first()
        
        if not profile:
            # Create default profile
            profile = UserPsychologicalProfile(
                user_id=user_id,
                preferred_colors=DEFAULT_CALMING_THEME,
                interaction_patterns={},
                wellness_goals=[],
                crisis_support_preferences={},
                preferred_psychological_focus=["general_wellness"]
            )
            self.db.add(profile)
            self.db.commit()
        
        return profile
    
    def update_user_mood_theme(self, user_id: str, current_mood: str) -> Dict:
        """Update user's theme based on current mood"""
        profile = self.get_user_psychological_profile(user_id)
        
        # Generate mood-responsive theme
        new_theme = PsychologyUtils.get_mood_responsive_theme(
            current_mood, 
            {"preferred_colors": profile.preferred_colors} if profile else None
        )
        
        # Apply time-based adjustments
        time_adjustment = PsychologyUtils.get_time_based_theme_adjustment()
        new_theme.update(time_adjustment)
        
        # Update profile
        if profile:
            profile.current_mood_state = current_mood
            profile.last_mood_update = datetime.utcnow()
            profile.preferred_colors = new_theme
            self.db.commit()
        
        return new_theme
    
    def get_community_wellness_dashboard(self, hub_id: str) -> Dict:
        """Get wellness analytics for a community"""
        conversations = self.db.query(CommunityConversation).filter(
            and_(
                CommunityConversation.hub_id == hub_id,
                CommunityConversation.is_active == True,
                CommunityConversation.created_at > datetime.utcnow() - timedelta(days=7)
            )
        ).all()
        
        conversation_data = [
            {
                "content": conv.content,
                "calming_score": conv.calming_score,
                "created_at": conv.created_at,
                "crisis_flag": conv.crisis_flag
            }
            for conv in conversations
        ]
        
        wellness_score = CommunityAnalytics.calculate_community_wellness_score(conversation_data)
        mood_trends = CommunityAnalytics.identify_community_mood_trends(conversation_data)
        
        return {
            "wellness_score": wellness_score,
            "mood_trends": mood_trends,
            "total_conversations": len(conversations),
            "active_members": self.db.query(CommunityHubMembership).filter(
                and_(
                    CommunityHubMembership.hub_id == hub_id,
                    CommunityHubMembership.is_active == True,
                    CommunityHubMembership.last_active > datetime.utcnow() - timedelta(days=7)
                )
            ).count()
        }
    
    def _generate_hub_theme(self, psychological_focus: str, creator_profile: Optional[UserPsychologicalProfile]) -> Dict:
        """Generate appropriate theme for community hub"""
        base_theme = DEFAULT_CALMING_THEME.copy()
        
        # Customize based on psychological focus
        if psychological_focus == "anxiety_support":
            base_theme["primary"] = "#4A90E2"  # Calm blue
            base_theme["secondary"] = "#BB8FCE"  # Lavender
        elif psychological_focus == "depression_help":
            base_theme["primary"] = "#F39C12"  # Warm orange
            base_theme["secondary"] = "#5DADE2"  # Gentle teal
        elif psychological_focus == "mindfulness_practice":
            base_theme["primary"] = "#27AE60"  # Forest green
            base_theme["secondary"] = "#9B8CE8"  # Soft purple
        
        # Apply creator preferences if available
        if creator_profile and creator_profile.preferred_colors:
            for key, color in creator_profile.preferred_colors.items():
                if key in ["primary", "secondary", "accent"]:
                    base_theme[key] = color
        
        return base_theme
    
    def _create_welcome_conversation(self, hub_id: str, creator_id: str) -> CommunityConversation:
        """Create welcome conversation for new hub"""
        welcome_content = f"""
        Welcome to this supportive community space! 🌿
        
        This is a safe place where we can share our journeys, support each other, 
        and grow together. Here are some ways to get the most from this community:
        
        • Share your experiences with kindness and empathy
        • Listen actively and offer support when you can
        • Remember that everyone's journey is unique
        • Take care of your mental health first
        
        Let's create a space of healing and growth together. 💙
        """
        
        return CommunityConversation(
            hub_id=hub_id,
            conversation_type="announcement",
            title="Welcome to Our Community! 🌟",
            content=welcome_content.strip(),
            author_id=creator_id,
            psychological_tone="supportive",
            calming_score=0.9,
            is_pinned=True
        )
    
    def _handle_crisis_conversation(self, conversation_id: str, user_id: str, crisis_indicators: List[str]):
        """Handle crisis detection in conversations"""
        # This would trigger:
        # 1. Immediate notification to moderators
        # 2. Gentle automated response with resources
        # 3. Escalation to crisis support team if configured
        # 4. Follow-up check with user
        
        # For now, just log the crisis detection
        print(f"🚨 Crisis indicators detected in conversation {conversation_id}")
        print(f"User: {user_id}, Indicators: {crisis_indicators}")
        
        # Could integrate with external crisis support services
        # Could automatically provide crisis hotline numbers
        # Could notify designated community support moderators
    
    def _add_to_community_feeds(self, conversation: CommunityConversation):
        """Add conversation to relevant user feeds"""
        # Get all members of the community
        memberships = self.db.query(CommunityHubMembership).filter(
            and_(
                CommunityHubMembership.hub_id == conversation.hub_id,
                CommunityHubMembership.is_active == True
            )
        ).all()
        
        for membership in memberships:
            if membership.user_id != conversation.author_id:  # Don't add to author's feed
                feed_item = CommunityFeedItem(
                    user_id=membership.user_id,
                    hub_id=conversation.hub_id,
                    content_type="conversation",
                    content_id=conversation.id,
                    calming_effect_rating=conversation.calming_score
                )
                self.db.add(feed_item)
