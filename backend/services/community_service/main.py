"""
MantraPath Community Service - Clean Implementation
"""
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import logging
import sys
import os

# Add parent directories to path
sys.path.append('/app')
sys.path.append('/app/shared')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import shared dependencies
from shared.database import get_db, engine
from shared.auth import get_current_user, verify_token
from shared.user_display import get_user_display_name as get_unique_display_name
# Event imports for community events
from shared.events import publish_community_post_created, publish_challenge_progress_updated
from shared.events import get_enhanced_event_bus, V3EventChannels
from shared.feature_flags import get_flag_bool
from shared.models import (
    Base, User, Challenge, CommunityEvent, CommunityForum,
    ForumThread, ThreadReply, Like, ForumMembership, EventComment
)
# Import additional models conditionally to handle missing models gracefully
try:
    from shared.models import (
        ChallengeProgress, ChallengeComment, ChallengeParticipant, EventParticipant
    )
except ImportError as e:
    print(f"⚠️  Warning: Could not import some models: {e}")
    # Create dummy classes for missing models as placeholders
    class ChallengeProgress:
        pass
    class ChallengeComment:
        pass
    class ChallengeParticipant:
        pass
    class EventParticipant:
        pass

# Create FastAPI app
app = FastAPI(title="MantraPath Community Service", version="2.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

def get_user_display_name(user_id: str, db: Session) -> tuple[str, str]:
    """Get user display name from database using unique identifier"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            unique_display = get_unique_display_name(user)
            return unique_display, unique_display
        return get_unique_display_name({'id': user_id}), get_unique_display_name({'id': user_id})
    except Exception as e:
        logger.warning(f"Could not fetch user {user_id}: {e}")
        fallback = get_unique_display_name({'id': user_id})
        return fallback, fallback

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "community", "timestamp": datetime.utcnow().isoformat()}

@app.get("/debug/auth")
async def debug_auth(request: Request):
    """Debug endpoint to check authentication headers"""
    headers = dict(request.headers)
    auth_header = headers.get("authorization", "No Authorization header")
    
    return {
        "authorization_header": auth_header,
        "has_bearer": auth_header.startswith("Bearer ") if auth_header != "No Authorization header" else False,
        "all_headers": {k: v for k, v in headers.items() if k.lower() in ['authorization', 'content-type', 'user-agent']},
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/debug/test-thread-creation")
async def test_thread_creation():
    """Debug endpoint to test ForumThread creation without authentication"""
    try:
        from shared.models import ForumThread
        
        # Test creating a ForumThread object
        test_thread = ForumThread(
            forum_id="test-forum-id",
            title="Test Thread",
            content="Test content",
            author_id="test-user-id"
        )
        
        return {
            "success": True,
            "message": "ForumThread object created successfully",
            "thread_id": test_thread.id,
            "forum_id": test_thread.forum_id,
            "title": test_thread.title,
            "author_id": test_thread.author_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.get("/user/stats")
async def get_user_stats(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user community statistics"""
    try:
        user_id = current_user.get('user_id')
        
        # Get challenges joined count
        challenges_joined = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.user_id == user_id
        ).count()
        
        # Get events joined count
        events_joined = db.query(EventParticipant).filter(
            EventParticipant.user_id == user_id
        ).count()
        
        # Get active challenges count (challenges user joined that are still active)
        active_challenges = db.query(ChallengeParticipant).join(
            Challenge, ChallengeParticipant.challenge_id == Challenge.id
        ).filter(
            ChallengeParticipant.user_id == user_id,
            Challenge.end_date > datetime.utcnow()
        ).count()
        
        # Get completed challenge progress count
        completed_activities = db.query(ChallengeProgress).filter(
            ChallengeProgress.user_id == user_id,
            ChallengeProgress.completed == True
        ).count()
        
        # Calculate basic engagement score
        engagement_score = min(100, (challenges_joined * 10) + (events_joined * 5) + (completed_activities * 2))
        
        return {
            "challenges_joined": challenges_joined,
            "events_joined": events_joined,
            "active_challenges": active_challenges,
            "completed_activities": completed_activities,
            "community_engagement_score": engagement_score
        }
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user stats")

@app.get("/forums")
async def get_forums(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all forums"""
    try:
        user_id = current_user.get('user_id')
        
        # Get all active forums from database
        forums = db.query(CommunityForum).order_by(CommunityForum.created_at.desc()).all()
        
        result = []
        for forum in forums:
            # Get creator info
            username, full_name = get_user_display_name(forum.created_by, db) if forum.created_by else ("System", "System Admin")
            
            # Calculate actual member count from ForumMembership
            member_count = db.query(ForumMembership).filter(
                ForumMembership.forum_id == forum.id,
                ForumMembership.is_active == True
            ).count()
            
            # Check if current user is a member
            is_joined = db.query(ForumMembership).filter(
                ForumMembership.user_id == user_id,
                ForumMembership.forum_id == forum.id,
                ForumMembership.is_active == True
            ).first() is not None
            
            # Count recent posts/challenges/events in this forum category
            recent_posts = db.query(ChallengeComment).join(
                Challenge, ChallengeComment.challenge_id == Challenge.id
            ).filter(
                Challenge.category == forum.category,
                ChallengeComment.created_at > datetime.utcnow() - timedelta(days=7)
            ).count()
            
            result.append({
                "id": forum.id,
                "name": forum.name,
                "description": forum.description,
                "category": forum.category,
                "color_theme": "calm_blue",  # Default theme
                "psychological_focus": ["general"],  # Default focus
                "member_count": member_count,
                "created_by": {"name": username, "full_name": full_name},
                "created_at": forum.created_at.isoformat(),
                "recent_posts": recent_posts,
                "is_joined": is_joined
            })
        
        # If no forums in database, create default ones
        if not result:
            # Create default forums in database
            default_forums_data = [
                {
                    "name": "Mindfulness & Meditation",
                    "description": "Share your mindfulness journey and meditation experiences",
                    "category": "mindfulness"
                },
                {
                    "name": "Challenge Support",
                    "description": "Get support and share experiences with ongoing challenges",
                    "category": "challenges"
                },
                {
                    "name": "General Discussion",
                    "description": "General wellness discussions and community support",
                    "category": "general"
                },
                {
                    "name": "Mental Health Support",
                    "description": "Safe space for mental health discussions and support",
                    "category": "mental-health"
                }
            ]
            
            for forum_data in default_forums_data:
                new_forum = CommunityForum(
                    name=forum_data["name"],
                    description=forum_data["description"],
                    category=forum_data["category"],
                    created_by=user_id  # Create as current user
                )
                db.add(new_forum)
            
            try:
                db.commit()
                logger.info("Created default forums")
                
                # Fetch the newly created forums
                forums = db.query(CommunityForum).order_by(CommunityForum.created_at.desc()).all()
                
                # Create some default threads for the forums
                from shared.models import ForumThread
                
                default_threads = [
                    {
                        "forum_category": "mindfulness",
                        "title": "Welcome to Mindfulness Discussions",
                        "content": "Share your mindfulness journey and experiences here. What techniques work best for you?"
                    },
                    {
                        "forum_category": "challenges",
                        "title": "Challenge Support & Motivation",
                        "content": "Need encouragement with your current challenges? Share your struggles and victories here!"
                    },
                    {
                        "forum_category": "general",
                        "title": "Welcome to the Community",
                        "content": "Introduce yourself and connect with other members of our wellness community."
                    }
                ]
                
                for forum in forums:
                    # Find matching default thread
                    thread_data = next((t for t in default_threads if t["forum_category"] == forum.category), None)
                    if thread_data:
                        try:
                            new_thread = ForumThread(
                                forum_id=forum.id,
                                title=thread_data["title"],
                                content=thread_data["content"],
                                author_id=user_id
                            )
                            db.add(new_thread)
                        except Exception as thread_error:
                            logger.warning(f"Could not create default thread: {thread_error}")
                
                try:
                    db.commit()
                    logger.info("Created default threads")
                except Exception as thread_commit_error:
                    logger.warning(f"Could not commit default threads: {thread_commit_error}")
                    db.rollback()
                
                for forum in forums:
                    username, full_name = get_user_display_name(forum.created_by, db)
                    
                    # Check if current user is a member of this forum
                    is_joined = db.query(ForumMembership).filter(
                        ForumMembership.user_id == user_id,
                        ForumMembership.forum_id == forum.id,
                        ForumMembership.is_active == True
                    ).first() is not None
                    
                    # Get actual member count
                    member_count = db.query(ForumMembership).filter(
                        ForumMembership.forum_id == forum.id,
                        ForumMembership.is_active == True
                    ).count() or 1
                    
                    result.append({
                        "id": forum.id,
                        "name": forum.name,
                        "description": forum.description,
                        "category": forum.category,
                        "color_theme": "calm_blue",
                        "psychological_focus": ["general"],
                        "member_count": member_count,
                        "created_by": {"name": username, "full_name": full_name},
                        "created_at": forum.created_at.isoformat(),
                        "recent_posts": 1,  # Now we have default threads
                        "is_joined": is_joined
                    })
                    
            except Exception as e:
                db.rollback()
                logger.error(f"Error creating default forums: {e}")
                # Return static defaults if database creation fails
                return [
                    {
                        "id": "forum-mindfulness",
                        "name": "Mindfulness & Meditation",
                        "description": "Share your mindfulness journey and meditation experiences",
                        "category": "mindfulness",
                        "color_theme": "calm_blue",
                        "psychological_focus": ["mindfulness", "stress-relief"],
                        "member_count": 1,
                        "created_by": {"name": "Community", "full_name": "Community Admin"},
                        "created_at": datetime.utcnow().isoformat(),
                        "recent_posts": 0,
                        "is_joined": False  # Default to false for static fallbacks
                    },
                    {
                        "id": "forum-challenges",
                        "name": "Challenge Support",
                        "description": "Get support and share experiences with ongoing challenges",
                        "category": "challenges",
                        "color_theme": "energy_orange",
                        "psychological_focus": ["motivation", "goal-setting"],
                        "member_count": 1,
                        "created_by": {"name": "Community", "full_name": "Community Admin"},
                        "created_at": datetime.utcnow().isoformat(),
                        "recent_posts": 0,
                        "is_joined": False  # Default to false for static fallbacks
                    }
                ]
        
        return result
    except Exception as e:
        logger.error(f"Error getting forums: {e}")
        raise HTTPException(status_code=500, detail="Failed to get forums")

@app.get("/forums/events")
async def get_events(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all community events"""
    try:
        user_id = current_user.get('user_id')
        
        # Get all active events from database
        events = db.query(CommunityEvent).filter(
            CommunityEvent.end_time > datetime.utcnow()  # Only get future events
        ).order_by(CommunityEvent.start_time.asc()).all()
        
        result = []
        for event in events:
            # Check if user is participating
            is_participating = db.query(EventParticipant).filter(
                EventParticipant.event_id == event.id,
                EventParticipant.user_id == user_id
            ).first() is not None
            
            # Get participant count
            participant_count = db.query(EventParticipant).filter(
                EventParticipant.event_id == event.id
            ).count()
            
            # Get comment count
            comment_count = db.query(EventComment).filter(
                EventComment.event_id == event.id
            ).count()
            
            # Get creator info
            username, full_name = get_user_display_name(event.created_by, db)
            
            result.append({
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "category": "general",  # Default category
                "event_type": "workshop",  # Default type
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "location": event.location,
                "meeting_link": event.location if event.is_virtual else None,  # Use location as meeting link for virtual events
                "max_participants": event.max_participants,
                "participant_count": participant_count,
                "comment_count": comment_count,
                "is_participating": is_participating,
                "created_by": {"name": username, "full_name": full_name},
                "created_at": event.created_at.isoformat()
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return []

@app.post("/forums/events/{event_id}/join")
async def join_event(event_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Join a community event"""
    try:
        user_id = current_user.get('user_id')
        logger.info(f"User {user_id} joining event {event_id}")
        
        # Check if event exists
        event = db.query(CommunityEvent).filter(
            CommunityEvent.id == event_id
        ).first()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Check if already participating
        existing = db.query(EventParticipant).filter(
            EventParticipant.event_id == event_id,
            EventParticipant.user_id == user_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Already participating in this event")
        
        # Check participant limit
        if event.max_participants:
            current_count = db.query(EventParticipant).filter(
                EventParticipant.event_id == event_id
            ).count()
            
            if current_count >= event.max_participants:
                raise HTTPException(status_code=400, detail="Event is full")
        
        # Add user to event
        new_participant = EventParticipant(
            event_id=event_id,
            user_id=user_id,
            joined_at=datetime.utcnow()
        )
        db.add(new_participant)
        db.commit()
        
        # Get updated participant count
        participant_count = db.query(EventParticipant).filter(
            EventParticipant.event_id == event_id
        ).count()
        
        return {
            "success": True,
            "message": "Successfully joined event",
            "participant_count": participant_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error joining event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to join event")

@app.delete("/forums/events/{event_id}/leave")
async def leave_event(event_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Leave a community event"""
    try:
        user_id = current_user.get('user_id')
        logger.info(f"User {user_id} leaving event {event_id}")
        
        # Remove user from event
        existing_participant = db.query(EventParticipant).filter(
            EventParticipant.event_id == event_id,
            EventParticipant.user_id == user_id
        ).first()
        
        if not existing_participant:
            raise HTTPException(status_code=400, detail="Not participating in this event")
        
        db.delete(existing_participant)
        db.commit()
        
        # Get updated participant count
        participant_count = db.query(EventParticipant).filter(
            EventParticipant.event_id == event_id
        ).count()
        
        return {
            "success": True,
            "message": "Successfully left event",
            "participant_count": participant_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error leaving event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to leave event")

@app.get("/forums/challenges")
async def get_challenges(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all challenges"""
    try:
        user_id = current_user.get('user_id')
        
        # Get all active challenges from database
        challenges = db.query(Challenge).filter(
            Challenge.end_date > datetime.utcnow()  # Only get active challenges
        ).order_by(Challenge.created_at.desc()).all()
        
        result = []
        for challenge in challenges:
            # Check if user is participating
            is_participating = db.query(ChallengeParticipant).filter(
                ChallengeParticipant.challenge_id == challenge.id,
                ChallengeParticipant.user_id == user_id
            ).first() is not None
            
            # Get participant count
            participant_count = db.query(ChallengeParticipant).filter(
                ChallengeParticipant.challenge_id == challenge.id
            ).count()
            
            # Get comment count
            comment_count = db.query(ChallengeComment).filter(
                ChallengeComment.challenge_id == challenge.id
            ).count()
            
            # Get creator info
            username, full_name = get_user_display_name(challenge.created_by, db)
            
            result.append({
                "id": challenge.id,
                "title": challenge.title,
                "description": challenge.description,
                "category": challenge.category,
                "duration_days": challenge.duration_days,
                "start_date": challenge.start_date.isoformat(),
                "end_date": challenge.end_date.isoformat() if challenge.end_date else None,
                "participant_count": participant_count,
                "comment_count": comment_count,
                "is_participating": is_participating,
                "created_by": {"name": username, "full_name": full_name},
                "created_at": challenge.created_at.isoformat()
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting challenges: {e}")
        return []

@app.post("/forums/challenges/{challenge_id}/join")
async def join_challenge(challenge_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Join a challenge"""
    try:
        user_id = current_user.get('user_id')
        logger.info(f"User {user_id} joining challenge {challenge_id}")
        
        # Check if challenge exists
        challenge = db.query(Challenge).filter(
            Challenge.id == challenge_id
        ).first()
        
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        # Check if already participating
        existing = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.challenge_id == challenge_id,
            ChallengeParticipant.user_id == user_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Already participating in this challenge")
        
        # Add user to challenge
        new_participant = ChallengeParticipant(
            challenge_id=challenge_id,
            user_id=user_id,
            joined_at=datetime.utcnow()
        )
        db.add(new_participant)
        db.commit()
        
        # Get updated participant count
        participant_count = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.challenge_id == challenge_id
        ).count()
        
        return {
            "success": True,
            "message": "Successfully joined challenge",
            "participant_count": participant_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error joining challenge {challenge_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to join challenge")

@app.post("/forums/challenges/{challenge_id}/leave")
async def leave_challenge(challenge_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Leave a challenge"""
    try:
        user_id = current_user.get('user_id')
        logger.info(f"User {user_id} leaving challenge {challenge_id}")
        
        # Find the participant record
        existing_participant = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.challenge_id == challenge_id,
            ChallengeParticipant.user_id == user_id
        ).first()
        
        if not existing_participant:
            raise HTTPException(status_code=400, detail="Not participating in this challenge")
        
        # First, delete any related progress records
        progress_records = db.query(ChallengeProgress).filter(
            ChallengeProgress.challenge_participant_id == existing_participant.id
        ).all()
        
        for progress in progress_records:
            db.delete(progress)
        
        # Then delete the participant record
        db.delete(existing_participant)
        db.commit()
        
        # Get updated participant count
        participant_count = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.challenge_id == challenge_id
        ).count()
        
        return {
            "success": True,
            "message": "Successfully left challenge", 
            "participant_count": participant_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error leaving challenge {challenge_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to leave challenge")

@app.get("/forums/challenges/{challenge_id}/progress")
async def get_challenge_progress(challenge_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's progress for a challenge"""
    try:
        user_id = current_user.get('user_id')
        
        # Check if user is participating in this challenge
        participant = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.challenge_id == challenge_id,
            ChallengeParticipant.user_id == user_id
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="Not participating in this challenge")
        
        # Get all progress entries for this user and challenge
        progress_entries = db.query(ChallengeProgress).filter(
            ChallengeProgress.challenge_id == challenge_id,
            ChallengeProgress.user_id == user_id
        ).order_by(ChallengeProgress.date.desc()).all()
        
        daily_completions = []
        for progress in progress_entries:
            daily_completions.append({
                "id": progress.id,
                "date": progress.date.isoformat(),
                "completed": progress.completed,
                "notes": progress.notes,
                "reflection": progress.reflection,
                "mood_rating": progress.mood_rating,
                "difficulty_rating": progress.difficulty_rating,
                "streak_count": progress.streak_count,
                "created_at": progress.created_at.isoformat()
            })
        
        # Calculate totals
        total_days = len(progress_entries)
        completed_days = sum(1 for p in progress_entries if p.completed)
        
        return {
            "daily_completions": daily_completions,
            "total_days": total_days,
            "completed_days": completed_days
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting challenge progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to get challenge progress")

@app.post("/forums/challenges/{challenge_id}/progress")
async def update_challenge_progress(
    challenge_id: str,
    progress_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update challenge progress for today"""
    try:
        user_id = current_user.get('user_id')
        logger.info(f"User {user_id} updating progress for challenge {challenge_id}")
        
        # Check if user is participating in this challenge, if not create participation
        participant = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.challenge_id == challenge_id,
            ChallengeParticipant.user_id == user_id
        ).first()
        
        if not participant:
            # Auto-join the user to the challenge if they're logging progress
            participant = ChallengeParticipant(
                challenge_id=challenge_id,
                user_id=user_id,
                joined_at=datetime.utcnow()
            )
            db.add(participant)
            db.commit()
            db.refresh(participant)
        
        today = datetime.utcnow().date()
        
        # Check if progress already exists for today
        existing_progress = db.query(ChallengeProgress).filter(
            ChallengeProgress.challenge_id == challenge_id,
            ChallengeProgress.user_id == user_id,
            ChallengeProgress.date == today
        ).first()
        
        # Calculate streak count
        previous_progress = db.query(ChallengeProgress).filter(
            ChallengeProgress.challenge_id == challenge_id,
            ChallengeProgress.user_id == user_id,
            ChallengeProgress.date < today,
            ChallengeProgress.completed == True
        ).order_by(ChallengeProgress.date.desc()).first()
        
        streak_count = 1
        if previous_progress and progress_data.get('completed', False):
            # Check for consecutive days
            yesterday = today - timedelta(days=1)
            if previous_progress.date == yesterday:
                streak_count = previous_progress.streak_count + 1
        elif not progress_data.get('completed', False):
            streak_count = 0
        
        if existing_progress:
            # Update existing progress
            existing_progress.completed = progress_data.get('completed', False)
            existing_progress.notes = progress_data.get('notes', '')
            existing_progress.reflection = progress_data.get('reflection', '')
            existing_progress.mood_rating = progress_data.get('mood_rating')
            existing_progress.difficulty_rating = progress_data.get('difficulty_rating')
            existing_progress.streak_count = streak_count
        else:
            # Create new progress entry
            new_progress = ChallengeProgress(
                challenge_participant_id=participant.id,
                challenge_id=challenge_id,
                user_id=user_id,
                date=today,
                completed=progress_data.get('completed', False),
                notes=progress_data.get('notes', ''),
                reflection=progress_data.get('reflection', ''),
                mood_rating=progress_data.get('mood_rating'),
                difficulty_rating=progress_data.get('difficulty_rating'),
                streak_count=streak_count
            )
            db.add(new_progress)
        
        db.commit()
        
        # 📤 E4: Publish challenge progress updated event for real-time pipeline
        if get_flag_bool('USE_EVENT_BUS'):
            progress_entry = existing_progress if existing_progress else new_progress
            # Publish challenge progress updated event
            try:
                bus = get_enhanced_event_bus()
                await bus.publish(
                    V3EventChannels.CHALLENGE_PROGRESS_UPDATED,
                    {
                        "challenge_id": challenge_id,
                        "user_id": user_id,
                        "completed": progress_data.get('completed', False),
                        "streak_count": streak_count,
                        "date": today.isoformat(),
                        "mood_rating": progress_data.get('mood_rating'),
                        "difficulty_rating": progress_data.get('difficulty_rating'),
                        "notes": progress_data.get('notes', ''),
                        "reflection": progress_data.get('reflection', '')
                    },
                    user_id=user_id
                )
                logger.info(f"Published challenge progress event for user {user_id}, challenge {challenge_id}")
            except Exception as e:
                logger.error(f"Failed to publish challenge progress event: {e}")
                # Don't fail the main operation if event publishing fails
            #         "date": today.isoformat(),
            #         "notes": progress_data.get('notes', ''),
            #         "mood_rating": progress_data.get('mood_rating'),
            #         "difficulty_rating": progress_data.get('difficulty_rating')
            #     }
            # )
            pass # Placeholder for now
        
        return {
            "success": True,
            "message": "Progress updated successfully",
            "streak_count": streak_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating challenge progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to update progress")

@app.get("/forums/challenges/{challenge_id}/comments")
async def get_challenge_comments(challenge_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get comments for a challenge"""
    try:
        # Get all comments for this challenge
        comments = db.query(ChallengeComment).filter(
            ChallengeComment.challenge_id == challenge_id
        ).order_by(ChallengeComment.created_at.desc()).all()
        
        result = []
        for comment in comments:
            # Get author info
            username, full_name = get_user_display_name(comment.user_id, db)
            
            result.append({
                "id": comment.id,
                "content": comment.content,
                "author": {
                    "id": comment.user_id,
                    "name": username,
                    "avatar_url": None,
                    "badges": []  # Could implement badges later
                },
                "created_at": comment.created_at.isoformat(),
                "like_count": comment.like_count,
                "is_liked": False,  # Could implement comment likes later
                "parent_id": comment.parent_id,
                "replies": []  # Could implement nested replies later
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting challenge comments: {e}")
        raise HTTPException(status_code=500, detail="Failed to get comments")

@app.post("/forums/challenges/{challenge_id}/comments")
async def add_challenge_comment(
    challenge_id: str,
    comment_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to a challenge"""
    try:
        user_id = current_user.get('user_id')
        
        # Check if challenge exists
        challenge = db.query(Challenge).filter(
            Challenge.id == challenge_id
        ).first()
        
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        # Create new comment
        new_comment = ChallengeComment(
            challenge_id=challenge_id,
            user_id=user_id,
            content=comment_data.get('content', ''),
            parent_id=comment_data.get('parent_id')
        )
        
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        # Get author info
        username, full_name = get_user_display_name(user_id, db)
        
        return {
            "id": new_comment.id,
            "content": new_comment.content,
            "author": {
                "id": user_id,
                "name": username,
                "avatar_url": None,
                "badges": []
            },
            "created_at": new_comment.created_at.isoformat(),
            "like_count": 0,
            "is_liked": False,
            "parent_id": new_comment.parent_id,
            "replies": []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding challenge comment: {e}")
        raise HTTPException(status_code=500, detail="Failed to add comment")

@app.get("/forums/challenges/{challenge_id}/leaderboard")
async def get_challenge_leaderboard(challenge_id: str, limit: int = 10, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get leaderboard for a challenge"""
    try:
        # Get challenge info for duration calculation
        challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        # Get all participants and their progress
        participants = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.challenge_id == challenge_id
        ).all()
        
        leaderboard_data = []
        
        for participant in participants:
            user_id = participant.user_id
            
            # Get username
            username, full_name = get_user_display_name(user_id, db)
            
            # Get user's progress data
            progress_entries = db.query(ChallengeProgress).filter(
                ChallengeProgress.challenge_id == challenge_id,
                ChallengeProgress.user_id == user_id
            ).all()
            
            # Calculate stats
            total_days = len(progress_entries)
            completed_days = sum(1 for p in progress_entries if p.completed)
            completion_percentage = (completed_days / challenge.duration_days * 100) if challenge.duration_days > 0 else 0
            
            # Get current streak
            current_streak = 0
            if progress_entries:
                latest_progress = max(progress_entries, key=lambda x: x.date)
                if latest_progress.completed:
                    current_streak = latest_progress.streak_count
            
            leaderboard_data.append({
                "user_id": user_id,
                "name": username,
                "username": username,
                "avatar_url": None,
                "completion_percentage": round(completion_percentage, 1),
                "completed_days": completed_days,
                "current_streak": current_streak,
                "joined_at": participant.joined_at.isoformat()
            })
        
        # Sort by completion percentage (descending), then by streak (descending)
        leaderboard_data.sort(key=lambda x: (x["completion_percentage"], x["current_streak"]), reverse=True)
        
        # Apply limit
        return leaderboard_data[:limit]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting challenge leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboard")

@app.post("/forums/events")
async def create_event(event_data: dict, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new community event"""
    try:
        user_id = current_user.get('user_id')
        
        # Create new event in database
        new_event = CommunityEvent(
            title=event_data.get('title'),
            description=event_data.get('description'),
            start_time=datetime.fromisoformat(event_data.get('start_time')),
            end_time=datetime.fromisoformat(event_data.get('end_time')),
            max_participants=event_data.get('max_participants'),
            location=event_data.get('location'),
            is_virtual=event_data.get('is_virtual', True),
            created_by=user_id
        )
        
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        
        username, full_name = get_user_display_name(user_id, db)
        
        return {
            "id": new_event.id,
            "title": new_event.title,
            "description": new_event.description,
            "category": "general",  # Default category
            "event_type": "workshop",  # Default type
            "start_time": new_event.start_time.isoformat(),
            "end_time": new_event.end_time.isoformat(),
            "location": new_event.location,
            "meeting_link": new_event.location if new_event.is_virtual else None,
            "max_participants": new_event.max_participants,
            "participant_count": 0,
            "is_participating": False,
            "created_by": {"name": username, "full_name": full_name},
            "created_at": new_event.created_at.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail="Failed to create event")

@app.post("/forums/challenges")
async def create_challenge(challenge_data: dict, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new challenge"""
    try:
        user_id = current_user.get('user_id')
        
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=challenge_data.get('duration_days', 30))
        
        # Create new challenge in database
        new_challenge = Challenge(
            title=challenge_data.get('title'),
            description=challenge_data.get('description'),
            category=challenge_data.get('category', 'mindfulness'),
            duration_days=challenge_data.get('duration_days', 30),
            start_date=start_date,
            end_date=end_date,
            created_by=user_id
        )
        
        db.add(new_challenge)
        db.commit()
        db.refresh(new_challenge)
        
        username, full_name = get_user_display_name(user_id, db)
        
        return {
            "id": new_challenge.id,
            "title": new_challenge.title,
            "description": new_challenge.description,
            "category": new_challenge.category,
            "duration_days": new_challenge.duration_days,
            "start_date": new_challenge.start_date.isoformat(),
            "end_date": new_challenge.end_date.isoformat(),
            "participant_count": 0,
            "comment_count": 0,
            "is_participating": False,
            "created_by": {"name": username, "full_name": full_name},
            "created_at": new_challenge.created_at.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating challenge: {e}")
        raise HTTPException(status_code=500, detail="Failed to create challenge")

# Import feed endpoints
try:
    from .feed_endpoints import get_community_feed, get_user_community_score
except ImportError:
    # Fallback if feed_endpoints module has issues
    def get_community_feed(*args, **kwargs):
        return []
    def get_user_community_score(*args, **kwargs):
        return {'total_score': 0, 'breakdown': {'participation': 0, 'engagement': 0, 'helpfulness': 0, 'consistency': 0}, 'level': 'New Member', 'next_level_threshold': 20}

@app.get("/feed")
async def community_feed(
    types: str = Query("thread,challenge,event"),
    time_range: str = Query("7d"),
    sort_by: str = Query("recent"),
    limit: int = Query(20),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get unified community feed"""
    return get_community_feed(current_user, db, types, time_range, sort_by, limit)

@app.get("/user/community-score")
async def user_community_score(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's community engagement score"""
    return get_user_community_score(current_user, db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

@app.get("/user/activity")
async def get_user_activity(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's community activity history"""
    try:
        user_id = current_user.get('user_id')
        
        activities = []
        
        # Get recent challenge progress
        recent_progress = db.query(ChallengeProgress).filter(
            ChallengeProgress.user_id == user_id
        ).order_by(ChallengeProgress.created_at.desc()).limit(10).all()
        
        for progress in recent_progress:
            challenge = db.query(Challenge).filter(Challenge.id == progress.challenge_id).first()
            if challenge:
                activities.append({
                    "id": f"progress-{progress.id}",
                    "type": "challenge_progress",
                    "title": f"Updated progress in '{challenge.title}'",
                    "description": f"Completed: {'Yes' if progress.completed else 'No'}",
                    "timestamp": progress.created_at.isoformat(),
                    "data": {
                        "challenge_id": challenge.id,
                        "challenge_title": challenge.title,
                        "completed": progress.completed,
                        "notes": progress.notes
                    }
                })
        
        # Get recent challenge joins
        recent_joins = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.user_id == user_id
        ).order_by(ChallengeParticipant.joined_at.desc()).limit(5).all()
        
        for join in recent_joins:
            challenge = db.query(Challenge).filter(Challenge.id == join.challenge_id).first()
            if challenge:
                activities.append({
                    "id": f"join-{join.challenge_id}",
                    "type": "challenge_joined",
                    "title": f"Joined challenge '{challenge.title}'",
                    "description": f"Started participating in {challenge.category} challenge",
                    "timestamp": join.joined_at.isoformat(),
                    "data": {
                        "challenge_id": challenge.id,
                        "challenge_title": challenge.title,
                        "category": challenge.category
                    }
                })
        
        # Get recent comments
        recent_comments = db.query(ChallengeComment).filter(
            ChallengeComment.user_id == user_id
        ).order_by(ChallengeComment.created_at.desc()).limit(5).all()
        
        for comment in recent_comments:
            challenge = db.query(Challenge).filter(Challenge.id == comment.challenge_id).first()
            if challenge:
                activities.append({
                    "id": f"comment-{comment.id}",
                    "type": "challenge_comment",
                    "title": f"Commented on '{challenge.title}'",
                    "description": comment.content[:100] + "..." if len(comment.content) > 100 else comment.content,
                    "timestamp": comment.created_at.isoformat(),
                    "data": {
                        "challenge_id": challenge.id,
                        "challenge_title": challenge.title,
                        "comment_content": comment.content
                    }
                })
        
        # Sort all activities by timestamp (newest first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "activities": activities[:20],  # Limit to 20 most recent activities
            "total_count": len(activities)
        }
        
    except Exception as e:
        logger.error(f"Error getting user activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user activity")

@app.post("/forums/{forum_id}/join")
async def join_forum(forum_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Join a community forum"""
    try:
        user_id = current_user.get('user_id')
        logger.info(f"User {user_id} joining forum {forum_id}")
        
        # Check if forum exists
        forum = db.query(CommunityForum).filter(
            CommunityForum.id == forum_id
        ).first()
        
        if not forum:
            raise HTTPException(status_code=404, detail="Forum not found")
        
        # Check if already a member
        existing_membership = db.query(ForumMembership).filter(
            ForumMembership.user_id == user_id,
            ForumMembership.forum_id == forum_id,
            ForumMembership.is_active == True
        ).first()
        
        if existing_membership:
            return {
                "success": True,
                "message": f"Already a member of {forum.name}",
                "forum_id": forum_id,
                "forum_name": forum.name,
                "is_joined": True
            }
        
        # Create forum membership
        membership = ForumMembership(
            user_id=user_id,
            forum_id=forum_id,
            role="member"
        )
        db.add(membership)
        db.commit()
        
        return {
            "success": True,
            "message": f"Successfully joined {forum.name}",
            "forum_id": forum_id,
            "forum_name": forum.name,
            "is_joined": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining forum {forum_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to join forum")

@app.delete("/forums/{forum_id}/leave")
async def leave_forum(forum_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Leave a community forum"""
    try:
        user_id = current_user.get('user_id')
        logger.info(f"User {user_id} leaving forum {forum_id}")
        
        # Check if forum exists
        forum = db.query(CommunityForum).filter(
            CommunityForum.id == forum_id
        ).first()
        
        if not forum:
            raise HTTPException(status_code=404, detail="Forum not found")
        
        # Find and deactivate membership
        membership = db.query(ForumMembership).filter(
            ForumMembership.user_id == user_id,
            ForumMembership.forum_id == forum_id,
            ForumMembership.is_active == True
        ).first()
        
        if not membership:
            return {
                "success": True,
                "message": f"You are not a member of {forum.name}",
                "forum_id": forum_id,
                "is_joined": False
            }
        
        # Deactivate membership
        membership.is_active = False
        db.commit()
        
        return {
            "success": True,
            "message": f"Successfully left {forum.name}",
            "forum_id": forum_id,
            "is_joined": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error leaving forum {forum_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to leave forum")

@app.post("/forums/thread")
async def create_forum_thread(
    thread_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new forum discussion thread"""
    try:
        user_id = current_user.get('user_id')
        logger.info(f"User {user_id} creating forum thread")
        
        # Check if forum exists
        forum_id = thread_data.get('forum_id')
        if forum_id:
            forum = db.query(CommunityForum).filter(
                CommunityForum.id == forum_id
            ).first()
            
            if not forum:
                raise HTTPException(status_code=404, detail="Forum not found")
        
        # Import ForumThread model if not already imported
        from shared.models import ForumThread
        
        # Create new thread with debug logging
        logger.info(f"Creating thread with data: title='{thread_data.get('title')}', forum_id='{forum_id}', author_id='{user_id}'")
        
        try:
            new_thread = ForumThread(
                forum_id=forum_id,
                title=thread_data.get('title'),
                content=thread_data.get('content', ''),
                author_id=user_id
            )
            
            logger.info("ForumThread object created successfully")
            
            db.add(new_thread)
            db.commit()
            db.refresh(new_thread)
            
            logger.info(f"Thread saved to database with ID: {new_thread.id}")
            
            # 📤 E4: Publish community post created event for real-time pipeline
            if get_flag_bool('USE_EVENT_BUS'):
                try:
                    bus = get_enhanced_event_bus()
                    await bus.publish(
                        V3EventChannels.COMMUNITY_POST_CREATED,
                        {
                            "id": new_thread.id,
                            "forum_id": new_thread.forum_id,
                            "title": new_thread.title,
                            "content": new_thread.content,
                            "post_type": "thread",
                            "author_id": user_id,
                            "created_at": new_thread.created_at.isoformat() if new_thread.created_at else None
                        },
                        user_id=user_id
                    )
                    logger.info(f"Published community post event for thread {new_thread.id}")
                except Exception as e:
                    logger.error(f"Failed to publish community post event: {e}")
                    # Don't fail the main operation if event publishing fails
            
        except Exception as thread_error:
            logger.error(f"Error creating ForumThread object: {thread_error}")
            logger.error(f"Thread data: {thread_data}")
            raise thread_error
        
        # Get creator info
        username, full_name = get_user_display_name(user_id, db)
        
        return {
            "id": new_thread.id,
            "forum_id": new_thread.forum_id,
            "title": new_thread.title,
            "content": new_thread.content,
            "category": forum.category if forum else "general",  # Add category
            "author": {
                "id": user_id,
                "name": username,
                "full_name": full_name
            },
            "created_at": new_thread.created_at.isoformat(),
            "reply_count": 0,
            "last_activity": new_thread.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating forum thread: {e}")
        raise HTTPException(status_code=500, detail="Failed to create thread")

@app.get("/forums/{forum_id}/threads")
async def get_forum_threads(
    forum_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
    format: str = Query("full", description="Response format: 'full' or 'array'")
):
    """Get threads for a specific forum"""
    try:
        # Check if forum exists
        forum = db.query(CommunityForum).filter(
            CommunityForum.id == forum_id
        ).first()
        
        if not forum:
            raise HTTPException(status_code=404, detail="Forum not found")
        
        # Import ForumThread model
        from shared.models import ForumThread
        
        # Get threads for this forum
        threads = db.query(ForumThread).filter(
            ForumThread.forum_id == forum_id
        ).order_by(ForumThread.created_at.desc()).offset(offset).limit(limit).all()
        
        result = []
        for thread in threads:
            # Get creator info
            username, full_name = get_user_display_name(thread.author_id, db)
            
            # Get actual reply count from ThreadReply table
            try:
                from shared.models import ThreadReply
                reply_count = db.query(ThreadReply).filter(
                    ThreadReply.thread_id == thread.id
                ).count()
            except Exception as e:
                logger.warning(f"Could not query ThreadReply for thread {thread.id}: {e}")
                reply_count = 0
            
            # Get like count and user like status
            user_id = current_user.get('user_id')
            like_count = db.query(Like).filter(
                Like.content_type == "thread",
                Like.content_id == thread.id
            ).count()
            
            is_liked = db.query(Like).filter(
                Like.user_id == user_id,
                Like.content_type == "thread",
                Like.content_id == thread.id
            ).first() is not None
            
            result.append({
                "id": thread.id,
                "title": thread.title,
                "content": thread.content,
                "category": forum.category,  # Add category directly to thread
                "author": {
                    "id": thread.author_id,
                    "name": username,
                    "full_name": full_name
                },
                "created_at": thread.created_at.isoformat(),
                "reply_count": reply_count,
                "like_count": like_count,
                "is_liked": is_liked,
                "last_activity": thread.updated_at.isoformat() if hasattr(thread, 'updated_at') else thread.created_at.isoformat(),
                "forum": {
                    "id": forum.id,
                    "name": forum.name,
                    "category": forum.category
                }
            })
        
        # Return format based on query parameter
        if format == "array":
            return result
        else:
            return {
                "threads": result,
                "forum": {
                    "id": forum.id,
                    "name": forum.name,
                    "description": forum.description,
                    "category": forum.category
                },
                "pagination": {
                    "offset": offset,
                    "limit": limit,
                    "total": len(result)
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting forum threads: {e}")
        raise HTTPException(status_code=500, detail="Failed to get forum threads")

@app.get("/forums/threads")
async def get_all_threads(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """Get all recent forum threads across all forums"""
    try:
        # Import ForumThread model
        from shared.models import ForumThread
        
        # Get recent threads from all forums
        threads = db.query(ForumThread).order_by(
            ForumThread.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        result = []
        for thread in threads:
            # Get creator info
            username, full_name = get_user_display_name(thread.author_id, db)
            
            # Get forum info
            forum = db.query(CommunityForum).filter(
                CommunityForum.id == thread.forum_id
            ).first()
            
            # Get like count and user like status
            user_id = current_user.get('user_id')
            like_count = db.query(Like).filter(
                Like.content_type == "thread",
                Like.content_id == thread.id
            ).count()
            
            is_liked = db.query(Like).filter(
                Like.user_id == user_id,
                Like.content_type == "thread",
                Like.content_id == thread.id
            ).first() is not None
            
            result.append({
                "id": thread.id,
                "title": thread.title,
                "content": thread.content,
                "category": forum.category if forum else "general",  # Add category directly to thread
                "author": {
                    "id": thread.author_id,
                    "name": username,
                    "full_name": full_name
                },
                "created_at": thread.created_at.isoformat(),
                "reply_count": 0,  # Placeholder
                "like_count": like_count,
                "is_liked": is_liked,
                "last_activity": thread.updated_at.isoformat() if hasattr(thread, 'updated_at') else thread.created_at.isoformat(),
                "forum": {
                    "id": forum.id if forum else None,
                    "name": forum.name if forum else "Unknown Forum",
                    "category": forum.category if forum else "general"
                }
            })
        
        # Return just the array that the frontend expects
        return result
        
    except Exception as e:
        logger.error(f"Error getting all threads: {e}")
        # Return empty array to prevent frontend errors
        return []

@app.get("/forums/thread/{thread_id}")
async def get_forum_thread(
    thread_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific forum thread with replies"""
    try:
        # Import models
        from shared.models import ForumThread, ThreadReply
        
        # Get the thread
        thread = db.query(ForumThread).filter(
            ForumThread.id == thread_id
        ).first()
        
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Get thread creator info
        username, full_name = get_user_display_name(thread.author_id, db)
        
        # Get replies for this thread
        try:
            replies = db.query(ThreadReply).filter(
                ThreadReply.thread_id == thread_id
            ).order_by(ThreadReply.created_at.asc()).all()
        except:
            # If ThreadReply table doesn't exist, return empty replies
            replies = []
        
        reply_list = []
        for reply in replies:
            reply_username, reply_full_name = get_user_display_name(reply.author_id, db)
            
            # Get like count and user like status for reply
            user_id = current_user.get('user_id')
            reply_like_count = db.query(Like).filter(
                Like.content_type == "reply",
                Like.content_id == reply.id
            ).count()
            
            reply_is_liked = db.query(Like).filter(
                Like.user_id == user_id,
                Like.content_type == "reply",
                Like.content_id == reply.id
            ).first() is not None
            
            reply_list.append({
                "id": reply.id,
                "content": reply.content,
                "author": {
                    "id": reply.author_id,
                    "name": reply_username,
                    "full_name": reply_full_name
                },
                "created_at": reply.created_at.isoformat(),
                "like_count": reply_like_count,
                "is_liked": reply_is_liked
            })
        
        # Get like count and user like status for the thread
        user_id = current_user.get('user_id')
        thread_like_count = db.query(Like).filter(
            Like.content_type == "thread",
            Like.content_id == thread.id
        ).count()
        
        thread_is_liked = db.query(Like).filter(
            Like.user_id == user_id,
            Like.content_type == "thread",
            Like.content_id == thread.id
        ).first() is not None
        
        return {
            "id": thread.id,
            "forum_id": thread.forum_id,
            "title": thread.title,
            "content": thread.content,
            "author": {
                "id": thread.author_id,
                "name": username,
                "full_name": full_name
            },
            "created_at": thread.created_at.isoformat(),
            "like_count": thread_like_count,
            "is_liked": thread_is_liked,
            "replies": reply_list,
            "reply_count": len(reply_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting forum thread: {e}")
        raise HTTPException(status_code=500, detail="Failed to get thread")

@app.post("/forums/thread/{thread_id}/reply")
async def reply_to_thread(
    thread_id: str,
    reply_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reply to a forum thread"""
    try:
        user_id = current_user.get('user_id')
        
        # Import models
        from shared.models import ForumThread, ThreadReply
        
        # Check if thread exists
        thread = db.query(ForumThread).filter(
            ForumThread.id == thread_id
        ).first()
        
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Create new reply
        try:
            new_reply = ThreadReply(
                thread_id=thread_id,
                content=reply_data.get('content', ''),
                author_id=user_id
            )
            
            db.add(new_reply)
            db.commit()
            db.refresh(new_reply)
            
            # Calculate updated reply count
            reply_count = db.query(ThreadReply).filter(
                ThreadReply.thread_id == thread_id
            ).count()
            
            # Get creator info
            username, full_name = get_user_display_name(user_id, db)
            
            return {
                "id": new_reply.id,
                "content": new_reply.content,
                "author": {
                    "id": user_id,
                    "name": username,
                    "full_name": full_name
                },
                "created_at": new_reply.created_at.isoformat(),
                "thread_reply_count": reply_count
            }
            
        except Exception as model_error:
            # If ThreadReply model doesn't work, return a mock response
            logger.warning(f"ThreadReply model error: {model_error}, returning mock response")
            username, full_name = get_user_display_name(user_id, db)
            
            return {
                "id": f"temp-reply-{datetime.utcnow().timestamp()}",
                "content": reply_data.get('content', ''),
                "author": {
                    "id": user_id,
                    "name": username,
                    "full_name": full_name
                },
                "created_at": datetime.utcnow().isoformat(),
                "thread_reply_count": 1
            }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error replying to thread: {e}")
        raise HTTPException(status_code=500, detail="Failed to create reply")

@app.get("/forums/events/{event_id}/comments")
async def get_event_comments(event_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get comments for an event"""
    try:
        # Check if event exists
        event = db.query(CommunityEvent).filter(
            CommunityEvent.id == event_id
        ).first()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Get all comments for this event
        comments = db.query(EventComment).filter(
            EventComment.event_id == event_id
        ).order_by(EventComment.created_at.desc()).all()
        
        result = []
        for comment in comments:
            # Get author info
            username, full_name = get_user_display_name(comment.user_id, db)
            
            # Get like count and user like status for the comment
            user_id = current_user.get('user_id')
            like_count = db.query(Like).filter(
                Like.content_type == "event_comment",
                Like.content_id == comment.id
            ).count()
            
            is_liked = db.query(Like).filter(
                Like.user_id == user_id,
                Like.content_type == "event_comment",
                Like.content_id == comment.id
            ).first() is not None
            
            result.append({
                "id": comment.id,
                "content": comment.content,
                "author": {
                    "id": comment.user_id,
                    "name": username,
                    "full_name": full_name,
                    "avatar_url": None,
                    "badges": []
                },
                "created_at": comment.created_at.isoformat(),
                "like_count": like_count,
                "is_liked": is_liked,
                "parent_id": comment.parent_id,
                "replies": []  # Could implement nested replies later
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event comments: {e}")
        raise HTTPException(status_code=500, detail="Failed to get event comments")

@app.post("/forums/events/{event_id}/comments")
async def add_event_comment(
    event_id: str,
    comment_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to an event"""
    try:
        user_id = current_user.get('user_id')
        
        # Check if event exists
        event = db.query(CommunityEvent).filter(
            CommunityEvent.id == event_id
        ).first()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Create new comment
        new_comment = EventComment(
            event_id=event_id,
            user_id=user_id,
            content=comment_data.get('content', ''),
            parent_id=comment_data.get('parent_id')
        )
        
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        # Get updated comment count
        comment_count = db.query(EventComment).filter(
            EventComment.event_id == event_id
        ).count()
        
        # Get author info
        username, full_name = get_user_display_name(user_id, db)
        
        return {
            "id": new_comment.id,
            "content": new_comment.content,
            "author": {
                "id": user_id,
                "name": username,
                "full_name": full_name,
                "avatar_url": None,
                "badges": []
            },
            "created_at": new_comment.created_at.isoformat(),
            "like_count": 0,
            "is_liked": False,
            "parent_id": new_comment.parent_id,
            "replies": [],
            "event_comment_count": comment_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding event comment: {e}")
        raise HTTPException(status_code=500, detail="Failed to add event comment")

@app.post("/forums/like")
async def toggle_content_like(
    like_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle like/unlike for content (thread, reply, etc.)"""
    try:
        user_id = current_user.get('user_id')
        content_type = like_data.get('content_type')  # 'thread', 'reply', etc.
        content_id = like_data.get('content_id')
        
        logger.info(f"User {user_id} toggling like for {content_type} {content_id}")
        
        # Check if user already liked this content
        existing_like = db.query(Like).filter(
            Like.user_id == user_id,
            Like.content_type == content_type,
            Like.content_id == content_id
        ).first()
        
        if existing_like:
            # Unlike: remove the like
            db.delete(existing_like)
            db.commit()
            
            return {
                "success": True,
                "liked": False,
                "message": "Content unliked"
            }
        else:
            # Like: add a new like
            new_like = Like(
                user_id=user_id,
                content_type=content_type,
                content_id=content_id
            )
            db.add(new_like)
            db.commit()
            
            return {
                "success": True,
                "liked": True,
                "message": "Content liked"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error toggling like: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle like")

@app.get("/forums/content/{content_type}/{content_id}/likes")
async def get_content_likes(
    content_type: str,
    content_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get like count and user's like status for content"""
    try:
        user_id = current_user.get('user_id')
        
        # Get total like count
        like_count = db.query(Like).filter(
            Like.content_type == content_type,
            Like.content_id == content_id
        ).count()
        
        # Check if current user liked this content
        user_liked = db.query(Like).filter(
            Like.user_id == user_id,
            Like.content_type == content_type,
            Like.content_id == content_id
        ).first() is not None
        
        return {
            "like_count": like_count,
            "is_liked": user_liked
        }
        
    except Exception as e:
        logger.error(f"Error getting content likes: {e}")
        raise HTTPException(status_code=500, detail="Failed to get content likes")

@app.get("/forums/thread/{thread_id}/replies")
async def get_thread_replies_only(
    thread_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get only the replies for a specific thread"""
    try:
        # Import models
        from shared.models import ThreadReply
        
        # Check if thread exists
        from shared.models import ForumThread
        thread = db.query(ForumThread).filter(
            ForumThread.id == thread_id
        ).first()
        
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Get replies for this thread
        try:
            replies = db.query(ThreadReply).filter(
                ThreadReply.thread_id == thread_id
            ).order_by(ThreadReply.created_at.asc()).all()
        except:
            # If ThreadReply table doesn't exist, return empty replies
            replies = []
        
        reply_list = []
        for reply in replies:
            reply_username, reply_full_name = get_user_display_name(reply.author_id, db)
            
            # Get like count and user like status for reply
            user_id = current_user.get('user_id')
            reply_like_count = db.query(Like).filter(
                Like.content_type == "reply",
                Like.content_id == reply.id
            ).count()
            
            reply_is_liked = db.query(Like).filter(
                Like.user_id == user_id,
                Like.content_type == "reply",
                Like.content_id == reply.id
            ).first() is not None
            
            reply_list.append({
                "id": reply.id,
                "content": reply.content,
                "author": {
                    "id": reply.author_id,
                    "name": reply_username,
                    "full_name": reply_full_name
                },
                "created_at": reply.created_at.isoformat(),
                "like_count": reply_like_count,
                "is_liked": reply_is_liked
            })
        
        return reply_list
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting thread replies: {e}")
        raise HTTPException(status_code=500, detail="Failed to get thread replies")
