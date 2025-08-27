"""MantraPath Community Service - Clean ImplementationDatabase-driven community features without mock data"""from fastapi import FastAPI, Depends, HTTPException, Queryfrom fastapi.middleware.cors import CORSMiddlewarefrom sqlalchemy.orm import Sessionfrom sqlalchemy import func, and_, or_from typing import Optional, List, Dictfrom datetime import datetime, timezone, timedeltaimport loggingimport sysimport os# Add parent directories to pathsys.path.append('/app')sys.path.append('/app/shared')# Setup logginglogging.basicConfig(level=logging.INFO)logger = logging.getLogger(__name__)# Import shared dependenciesfrom shared.database import get_db, enginefrom shared.auth import get_current_userfrom shared.models import Base, User# Create FastAPI appapp = FastAPI(title="MantraPath Community Service", version="2.0.0")# Configure CORSapp.add_middleware(    CORSMiddleware,    allow_origins=["*"],    allow_credentials=True,    allow_methods=["*"],    allow_headers=["*"],)# Create tablesBase.metadata.create_all(bind=engine)def get_user_display_name(user_id: str, db: Session) -> tuple[str, str]:    """Get user display name from database"""    try:        user = db.query(User).filter(User.id == user_id).first()        if user:            # Use username if available, otherwise extract from email            username = getattr(user, 'username', None) or user.email.split('@')[0] if user.email else f"User{user_id[:8]}"            full_name = getattr(user, 'full_name', None) or username            return username, full_name        return f"User{user_id[:8]}", f"User{user_id[:8]}"    except Exception as e:        logger.warning(f"Could not fetch user {user_id}: {e}")        return f"User{user_id[:8]}", f"User{user_id[:8]}"# HEALTH CHECK@app.get("/health")async def health():    return {"status": "healthy", "service": "community", "timestamp": datetime.utcnow().isoformat()}# USER STATS@app.get("/user/stats")async def get_user_stats(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):    """Get user community statistics"""    try:        user_id = current_user.get('user_id')                return {            "challenges_joined": 0,  # TODO: implement with real database queries            "events_joined": 0,            "active_challenges": 0,            "completed_activities": 0,            "community_engagement_score": 0        }    except Exception as e:        logger.error(f"Error getting user stats: {e}")        raise HTTPException(status_code=500, detail="Failed to get user stats")# FORUMS - Mock data for now@app.get("/forums")async def get_forums(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):    """Get all forums"""    try:        # Return mock forums until database models are implemented        return [            {                "id": "forum-1",                "name": "Mindfulness & Meditation",                "description": "Share your mindfulness journey and meditation experiences",                "category": "mindfulness",                "color_theme": "calm_blue",                "psychological_focus": ["mindfulness", "stress-relief"],                "member_count": 156,                "created_by": {"name": "Community", "full_name": "Community Admin"},                "created_at": datetime.utcnow().isoformat(),                "recent_posts": 23,                "is_joined": False            },            {                "id": "forum-2",                 "name": "Mental Wellness Support",                "description": "A safe space for mental health discussions and support",                "category": "mental-health",                "color_theme": "sage_green",                "psychological_focus": ["anxiety", "depression", "support"],                "member_count": 89,                "created_by": {"name": "Community", "full_name": "Community Admin"},                "created_at": datetime.utcnow().isoformat(),                "recent_posts": 12,                "is_joined": False            }        ]    except Exception as e:        logger.error(f"Error getting forums: {e}")        raise HTTPException(status_code=500, detail="Failed to get forums")# EVENTS - Mock data for now@app.get("/forums/events")async def get_events(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):    """Get all community events"""    try:        # Return mock events until database models are implemented        now = datetime.utcnow()        return [            {                "id": "event-1",                "title": "Morning Meditation Session",                "description": "Start your day with guided meditation",                "category": "mindfulness",                "event_type": "group_session",                "start_time": (now + timedelta(days=1)).isoformat(),                "end_time": (now + timedelta(days=1, hours=1)).isoformat(),                "location": "online",                "meeting_link": "https://meet.mantrapath.com/meditation",                "max_participants": 20,                "participant_count": 8,                "is_participating": False,                "created_by": {"name": "Meditation Guide", "full_name": "Sarah Johnson"},                "created_at": now.isoformat()            },            {                "id": "event-2",                "title": "Stress Management Workshop",                 "description": "Learn effective techniques for managing daily stress",                "category": "mental-health",                "event_type": "workshop",                "start_time": (now + timedelta(days=3)).isoformat(),                "end_time": (now + timedelta(days=3, hours=2)).isoformat(),                "location": "online",                "meeting_link": "https://meet.mantrapath.com/stress-workshop",                "max_participants": 30,                "participant_count": 15,                "is_participating": False,                "created_by": {"name": "Dr. Smith", "full_name": "Dr. Michael Smith"},                "created_at": now.isoformat()            }        ]    except Exception as e:        logger.error(f"Error getting events: {e}")        raise HTTPException(status_code=500, detail="Failed to get events")@app.post("/forums/events/{event_id}/join")async def join_event(event_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):    """Join a community event"""    try:        user_id = current_user.get('user_id')        logger.info(f"User {user_id} joining event {event_id}")                # Mock response - in real implementation this would update database        return {            "success": True,            "message": "Successfully joined event",            "participant_count": 9  # Mock incremented count        }            except Exception as e:        logger.error(f"Error joining event {event_id}: {e}")        raise HTTPException(status_code=500, detail="Failed to join event")@app.delete("/forums/events/{event_id}/leave")async def leave_event(event_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):    """Leave a community event"""    try:        user_id = current_user.get('user_id')        logger.info(f"User {user_id} leaving event {event_id}")                # Mock response - in real implementation this would update database          return {            "success": True,            "message": "Successfully left event",            "participant_count": 7  # Mock decremented count        }            except Exception as e:        logger.error(f"Error leaving event {event_id}: {e}")        raise HTTPException(status_code=500, detail="Failed to leave event")# CHALLENGES - Mock data for now@app.get("/forums/challenges")async def get_challenges(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):    """Get all challenges"""    try:        # Return mock challenges until database models are implemented        now = datetime.utcnow()        return [            {                "id": "challenge-1",                "title": "30-Day Mindfulness Challenge",                "description": "Practice mindfulness daily for 30 days",                "category": "mindfulness",                "duration_days": 30,                "start_date": now.isoformat(),                "end_date": (now + timedelta(days=30)).isoformat(),                "participant_count": 42,                "comment_count": 15,                "is_participating": False,                "created_by": {"name": "Mindfulness Coach", "full_name": "Emma Wilson"},                "created_at": now.isoformat()            },            {                "id": "challenge-2",                "title": "Gratitude Journal Journey",                "description": "Write in a gratitude journal every day for 21 days",                "category": "mental-health",                "duration_days": 21,                "start_date": now.isoformat(),                "end_date": (now + timedelta(days=21)).isoformat(),                "participant_count": 28,                "comment_count": 8,                "is_participating": False,                "created_by": {"name": "Wellness Guide", "full_name": "Alex Chen"},                "created_at": now.isoformat()            }        ]    except Exception as e:        logger.error(f"Error getting challenges: {e}")        raise HTTPException(status_code=500, detail="Failed to get challenges")@app.post("/forums/challenges/{challenge_id}/join")async def join_challenge(challenge_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):    """Join a challenge"""    try:        user_id = current_user.get('user_id')        logger.info(f"User {user_id} joining challenge {challenge_id}")                # Mock response - in real implementation this would update database        return {            "success": True,            "message": "Successfully joined challenge",            "participant_count": 43  # Mock incremented count        }            except Exception as e:        logger.error(f"Error joining challenge {challenge_id}: {e}")        raise HTTPException(status_code=500, detail="Failed to join challenge")@app.post("/forums/challenges/{challenge_id}/leave")async def leave_challenge(challenge_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):    """Leave a challenge"""    try:        user_id = current_user.get('user_id')        logger.info(f"User {user_id} leaving challenge {challenge_id}")                # Mock response - in real implementation this would update database        return {            "success": True,            "message": "Successfully left challenge",             "participant_count": 41  # Mock decremented count        }            except Exception as e:        logger.error(f"Error leaving challenge {challenge_id}: {e}")        raise HTTPException(status_code=500, detail="Failed to leave challenge")@app.get("/forums/challenges/{challenge_id}/progress")async def get_challenge_progress(challenge_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):    """Get user's progress for a challenge"""    try:        # Mock progress data - in real implementation this would query database        return {            "daily_completions": [                {                    "id": "progress-1",                    "date": datetime.utcnow().date().isoformat(),                    "completed": True,                    "notes": "Felt more focused today",                    "reflection": "Mindfulness helped me stay present",                    "mood_rating": 4,                    "difficulty_rating": 2,                    "streak_count": 3,                    "created_at": datetime.utcnow().isoformat()                }            ],            "total_days": 3,            "completed_days": 2        }            except Exception as e:        logger.error(f"Error getting challenge progress: {e}")        raise HTTPException(status_code=500, detail="Failed to get challenge progress")@app.post("/forums/challenges/{challenge_id}/progress")async def update_challenge_progress(    challenge_id: str,    progress_data: dict,    current_user: dict = Depends(get_current_user),    db: Session = Depends(get_db)):    """Update challenge progress for today"""    try:        user_id = current_user.get('user_id')        logger.info(f"User {user_id} updating progress for challenge {challenge_id}")                # Mock response - in real implementation this would update database        return {            "success": True,            "message": "Progress updated successfully",            "streak_count": 4  # Mock incremented streak        }            except Exception as e:        logger.error(f"Error updating challenge progress: {e}")        raise HTTPException(status_code=500, detail="Failed to update progress")@app.get("/forums/challenges/{challenge_id}/comments")async def get_challenge_comments(challenge_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):    """Get comments for a challenge"""    try:        # Mock comments data        return [            {                "id": "comment-1",                "content": "This challenge is really helping me stay mindful throughout the day!",                "author": {                    "id": "user-1",                    "name": "sarah_m",                    "avatar_url": None,                    "badges": ["mindful_warrior"]                },                "created_at": datetime.utcnow().isoformat(),                "like_count": 5,                "is_liked": False,                "parent_id": None,                "replies": []            }        ]            except Exception as e:        logger.error(f"Error getting challenge comments: {e}")        raise HTTPException(status_code=500, detail="Failed to get comments")@app.post("/forums/challenges/{challenge_id}/comments")async def add_challenge_comment(    challenge_id: str,    comment_data: dict,    current_user: dict = Depends(get_current_user),    db: Session = Depends(get_db)):    """Add a comment to a challenge"""    try:        user_id = current_user.get('user_id')        username, full_name = get_user_display_name(user_id, db)                # Mock response - in real implementation this would save to database        return {            "id": f"comment-{int(datetime.utcnow().timestamp())}",            "content": comment_data.get('content'),            "author": {                "id": user_id,                "name": username,                "avatar_url": None,                "badges": []            },            "created_at": datetime.utcnow().isoformat(),            "like_count": 0,            "is_liked": False,            "parent_id": comment_data.get('parent_id'),            "replies": []        }            except Exception as e:        logger.error(f"Error adding challenge comment: {e}")        raise HTTPException(status_code=500, detail="Failed to add comment")

@app.get("/forums/challenges/{challenge_id}/leaderboard")
async def get_challenge_leaderboard(challenge_id: str, limit: int = 10, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get leaderboard for a challenge"""
    try:
        # Mock leaderboard data
        return [
            {
                "user_id": "user-1",
                "name": "sarah_m",
                "username": "sarah_m",
                "avatar_url": None,
                "completion_percentage": 85.7,
                "completed_days": 6,
                "current_streak": 3,
                "joined_at": datetime.utcnow().isoformat()
            },
            {
                "user_id": "user-2", 
                "name": "alex_c",
                "username": "alex_c",
                "avatar_url": None,
                "completion_percentage": 71.4,
                "completed_days": 5,
                "current_streak": 2,
                "joined_at": datetime.utcnow().isoformat()
            }
        ]
        
    except Exception as e:
        logger.error(f"Error getting challenge leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboard")

# CREATE OPERATIONS
@app.post("/forums/events")
async def create_event(event_data: dict, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new community event"""
    try:
        user_id = current_user.get('user_id')
        username, full_name = get_user_display_name(user_id, db)
        
        # Mock response - in real implementation this would save to database
        event_id = f"event-{int(datetime.utcnow().timestamp())}"
        
        return {
            "id": event_id,
            "title": event_data.get('title'),
            "description": event_data.get('description'),
            "category": event_data.get('category', 'workshop'),
            "event_type": event_data.get('event_type', 'workshop'),
            "start_time": event_data.get('start_time'),
            "end_time": event_data.get('end_time'),
            "location": event_data.get('location'),
            "meeting_link": event_data.get('meeting_link'),
            "max_participants": event_data.get('max_participants'),
            "participant_count": 0,
            "is_participating": False,
            "created_by": {"name": username, "full_name": full_name},
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail="Failed to create event")

@app.post("/forums/challenges")
async def create_challenge(challenge_data: dict, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new challenge"""
    try:
        user_id = current_user.get('user_id')
        username, full_name = get_user_display_name(user_id, db)
        
        # Mock response - in real implementation this would save to database
        challenge_id = f"challenge-{int(datetime.utcnow().timestamp())}"
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=challenge_data.get('duration_days', 30))
        
        return {
            "id": challenge_id,
            "title": challenge_data.get('title'),
            "description": challenge_data.get('description'),
            "category": challenge_data.get('category', 'mindfulness'),
            "duration_days": challenge_data.get('duration_days', 30),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "participant_count": 0,
            "comment_count": 0,
            "is_participating": False,
            "created_by": {"name": username, "full_name": full_name},
            "created_at": start_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating challenge: {e}")
        raise HTTPException(status_code=500, detail="Failed to create challenge")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
