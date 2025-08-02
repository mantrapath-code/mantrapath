"""
Community Service - Handles forums, threads, replies, and community interactions
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sys

# Add parent directories to path
sys.path.append('/app')
sys.path.append('/app/shared')

from shared.database import get_db, engine
from shared.models import (
    CommunityForum, ForumThread, ThreadReply, ForumMembership, Like, Base, 
    Forum, ForumReply, User, UserProfile, CommunityEvent, Challenge, 
    EventParticipant, ChallengeParticipant
)
from shared.auth import get_current_user

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MantraPath Community Service",
    description="Forums and community interaction service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AuthorResponse(BaseModel):
    id: str
    name: str
    avatar_url: Optional[str] = None
    badges: List[str] = []

class ForumResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    member_count: int
    thread_count: int = 0
    is_joined: bool = False
    tags: List[str] = []

class ThreadCreate(BaseModel):
    forum_id: str
    title: str
    content: str

class ThreadResponse(BaseModel):
    id: str
    forum_id: str
    forum_name: str
    title: str
    content: str
    author: AuthorResponse
    reply_count: int
    view_count: int
    like_count: int = 0
    is_liked: bool = False
    created_at: datetime
    updated_at: datetime
    is_pinned: bool = False
    tags: List[str] = []
    category: str = "general"
    is_bookmarked: bool = False

class ReplyCreate(BaseModel):
    content: str
    parent_id: Optional[str] = None

class ReplyResponse(BaseModel):
    id: str
    thread_id: str
    content: str
    author: AuthorResponse
    created_at: datetime
    like_count: int = 0
    is_liked: bool = False
    parent_id: Optional[str] = None

class LikeRequest(BaseModel):
    content_type: str  # 'thread' or 'reply'
    content_id: str

# Event models
class EventCreate(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    is_virtual: bool = True

class EventResponse(BaseModel):
    id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    is_virtual: bool
    participant_count: int
    is_participating: bool = False
    created_at: datetime

# Challenge models
class ChallengeCreate(BaseModel):
    title: str
    description: str
    category: str
    duration_days: int
    start_date: datetime
    end_date: datetime

class ChallengeResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    duration_days: int
    start_date: datetime
    end_date: datetime
    participant_count: int
    is_participating: bool = False
    created_at: datetime

# Forum endpoints
@app.get("/forums", response_model=List[ForumResponse])
async def get_forums(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all forums with membership status"""
    
    forums = db.query(CommunityForum).all()
    
    # Get user's forum memberships
    memberships = db.query(ForumMembership).filter(
        ForumMembership.user_id == current_user["user_id"]
    ).all()
    
    member_forum_ids = {str(membership.forum_id) for membership in memberships}
    
    # Calculate member counts and thread counts dynamically
    forum_responses = []
    for forum in forums:
        member_count = db.query(ForumMembership).filter(
            ForumMembership.forum_id == forum.id,
            ForumMembership.is_active == True
        ).count()
        
        thread_count = db.query(ForumThread).filter(
            ForumThread.forum_id == forum.id
        ).count()
        
        forum_responses.append(ForumResponse(
            id=str(forum.id),
            name=forum.name,
            description=forum.description,
            category=forum.category,
            member_count=member_count,
            thread_count=thread_count,
            is_joined=str(forum.id) in member_forum_ids,
            tags=[]  # TODO: Implement tags system
        ))
    
    return forum_responses

@app.post("/forums/{forum_id}/join")
async def join_forum(
    forum_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a forum"""
    
    # Check if already a member
    existing = db.query(ForumMembership).filter(
        and_(
            ForumMembership.user_id == current_user["user_id"],
            ForumMembership.forum_id == forum_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already a member of this forum")
    
    # Create membership
    membership = ForumMembership(
        user_id=current_user["user_id"],
        forum_id=forum_id,
        role="member"
    )
    
    db.add(membership)
    db.commit()
    
    return {"message": "Successfully joined forum"}

@app.delete("/forums/{forum_id}/leave")
async def leave_forum(
    forum_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave a forum"""
    
    membership = db.query(ForumMembership).filter(
        and_(
            ForumMembership.user_id == current_user["user_id"],
            ForumMembership.forum_id == forum_id
        )
    ).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Not a member of this forum")
    
    db.delete(membership)
    db.commit()
    
    return {"message": "Successfully left forum"}

# Thread endpoints
@app.get("/forums/{forum_id}/threads", response_model=List[ThreadResponse])
async def get_forum_threads(
    forum_id: str,
    limit: int = Query(20, le=50),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get threads in a forum"""
    
    # Check if user is a member of the forum
    membership = db.query(ForumMembership).filter(
        and_(
            ForumMembership.user_id == current_user["user_id"],
            ForumMembership.forum_id == forum_id,
            ForumMembership.is_active == True
        )
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Must be a forum member to view threads")
    
    # Get forum info for forum_name
    forum = db.query(CommunityForum).filter(CommunityForum.id == forum_id).first()
    if not forum:
        raise HTTPException(status_code=404, detail="Forum not found")
    
    # Get threads for this forum with user data
    threads = db.query(ForumThread, User, UserProfile).outerjoin(
        User, ForumThread.author_id == User.id
    ).outerjoin(
        UserProfile, User.id == UserProfile.user_id
    ).filter(
        ForumThread.forum_id == forum_id
    ).order_by(desc(ForumThread.created_at)).limit(limit).all()
    
    thread_responses = []
    for thread_data in threads:
        thread, user, profile = thread_data
        
        # Get reply count
        reply_count = db.query(ThreadReply).filter(
            ThreadReply.thread_id == thread.id
        ).count()
        
        # Get like count and check if current user liked it
        like_count = db.query(Like).filter(
            and_(
                Like.content_type == "thread",
                Like.content_id == str(thread.id)
            )
        ).count()
        
        is_liked = db.query(Like).filter(
            and_(
                Like.user_id == current_user["user_id"],
                Like.content_type == "thread",
                Like.content_id == str(thread.id)
            )
        ).first() is not None
        
        # Create author object
        author_name = "Anonymous"
        author_avatar = None
        if user:
            author_name = f"{user.first_name} {user.last_name}".strip() or user.username
            if profile:
                author_avatar = profile.avatar_url
        
        author = AuthorResponse(
            id=str(user.id) if user else "anonymous",
            name=author_name,
            avatar_url=author_avatar,
            badges=[]  # TODO: Implement user badges system
        )
        
        thread_responses.append(ThreadResponse(
            id=str(thread.id),
            forum_id=str(thread.forum_id),
            forum_name=forum.name,
            title=thread.title,
            content=thread.content,
            author=author,
            reply_count=reply_count,
            view_count=thread.view_count,
            like_count=like_count,
            is_liked=is_liked,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
            is_pinned=thread.is_pinned,
            tags=[],  # TODO: Implement tags system
            category=forum.category,
            is_bookmarked=False  # TODO: Implement bookmarks system
        ))
    
    return thread_responses

@app.post("/forums/thread", response_model=ThreadResponse)
async def create_thread(
    thread_data: ThreadCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new thread"""
    
    # Verify user is member of forum
    membership = db.query(ForumMembership).filter(
        and_(
            ForumMembership.user_id == current_user["user_id"],
            ForumMembership.forum_id == thread_data.forum_id
        )
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Must be a member to create threads")
    
    thread = ForumThread(
        forum_id=thread_data.forum_id,
        author_id=current_user["user_id"],
        title=thread_data.title,
        content=thread_data.content
    )
    
    db.add(thread)
    db.commit()
    db.refresh(thread)
    
    # Get forum details
    forum = db.query(CommunityForum).filter(CommunityForum.id == thread_data.forum_id).first()
    if not forum:
        raise HTTPException(status_code=404, detail="Forum not found")
    
    # Get user details for author
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user["user_id"]).first()
    
    # Create author response
    author_name = "User"
    author_avatar = None
    
    if user:
        if user.username:
            author_name = user.username
        elif user.first_name or user.last_name:
            author_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        
        if user_profile and user_profile.avatar_url:
            author_avatar = user_profile.avatar_url
    
    author_response = AuthorResponse(
        id=str(user.id) if user else "anonymous",
        name=author_name,
        avatar_url=author_avatar,
        badges=[]
    )
    
    return ThreadResponse(
        id=str(thread.id),
        forum_id=str(thread.forum_id),
        forum_name=forum.name,
        title=thread.title,
        content=thread.content,
        author=author_response,
        reply_count=0,
        view_count=thread.view_count,
        like_count=0,
        is_liked=False,
        created_at=thread.created_at,
        updated_at=thread.updated_at,
        is_pinned=thread.is_pinned,
        tags=[],
        category=forum.category,
        is_bookmarked=False
    )

@app.get("/forums/thread/{thread_id}", response_model=ThreadResponse)
async def get_thread(
    thread_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get thread details and increment view count"""
    
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Increment view count
    db.query(ForumThread).filter(ForumThread.id == thread_id).update({
        ForumThread.view_count: ForumThread.view_count + 1
    })
    db.commit()
    
    # Get like count for this thread
    like_count = db.query(Like).filter(
        and_(
            Like.content_type == "thread",
            Like.content_id == str(thread.id)
        )
    ).count()
    
    # Check if current user liked this thread
    user_liked = db.query(Like).filter(
        and_(
            Like.user_id == current_user["user_id"],
            Like.content_type == "thread",
            Like.content_id == str(thread.id)
        )
    ).first() is not None
    
    return ThreadResponse(
        id=str(thread.id),
        forum_id=str(thread.forum_id),
        title=thread.title,
        content=thread.content,
        author="Anonymous",
        reply_count=thread.reply_count,
        view_count=thread.view_count + 1,  # Include the increment
        like_count=like_count,
        is_liked=user_liked,
        created_at=thread.created_at,
        is_pinned=thread.is_pinned
    )

# Reply endpoints
@app.post("/forums/thread/{thread_id}/reply", response_model=ReplyResponse)
async def create_reply(
    thread_id: str,
    reply_data: ReplyCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create reply to thread"""
    
    # Verify thread exists
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Verify user is member of forum
    membership = db.query(ForumMembership).filter(
        and_(
            ForumMembership.user_id == current_user["user_id"],
            ForumMembership.forum_id == thread.forum_id
        )
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Must be a member to reply")
    
    reply = ForumReply(
        thread_id=thread_id,
        author_id=current_user["user_id"],
        content=reply_data.content,
        parent_id=reply_data.parent_id
    )
    
    db.add(reply)
    
    # Update thread reply count
    db.query(ForumThread).filter(ForumThread.id == thread_id).update({
        ForumThread.reply_count: ForumThread.reply_count + 1
    })
    
    db.commit()
    db.refresh(reply)
    
    return ReplyResponse(
        id=str(reply.id),
        thread_id=str(reply.thread_id),
        content=reply.content,
        author="You",
        created_at=reply.created_at,
        likes_count=0
    )

# Like endpoints
@app.post("/forums/like")
async def toggle_like_content(
    like_data: LikeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle like/unlike for thread or reply"""
    
    # Check if already liked
    existing = db.query(Like).filter(
        and_(
            Like.user_id == current_user["user_id"],
            Like.content_type == like_data.content_type,
            Like.content_id == like_data.content_id
        )
    ).first()
    
    if existing:
        # Unlike: Remove existing like
        db.delete(existing)
        db.commit()
        
        # Get updated like count
        like_count = db.query(Like).filter(
            and_(
                Like.content_type == like_data.content_type,
                Like.content_id == like_data.content_id
            )
        ).count()
        
        return {
            "message": "Content unliked successfully",
            "liked": False,
            "like_count": like_count
        }
    else:
        # Like: Create new like
        like = Like(
            user_id=current_user["user_id"],
            content_type=like_data.content_type,
            content_id=like_data.content_id
        )
        
        db.add(like)
        db.commit()
        
        # Get updated like count
        like_count = db.query(Like).filter(
            and_(
                Like.content_type == like_data.content_type,
                Like.content_id == like_data.content_id
            )
        ).count()
        
        return {
            "message": "Content liked successfully",
            "liked": True,
            "like_count": like_count
        }

@app.get("/forums/like/{content_type}/{content_id}")
async def get_like_status(
    content_type: str,
    content_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get like status and count for content"""
    
    # Check if current user liked this content
    user_liked = db.query(Like).filter(
        and_(
            Like.user_id == current_user["user_id"],
            Like.content_type == content_type,
            Like.content_id == content_id
        )
    ).first() is not None
    
    # Get total like count
    like_count = db.query(Like).filter(
        and_(
            Like.content_type == content_type,
            Like.content_id == content_id
        )
    ).count()
    
    return {
        "liked": user_liked,
        "like_count": like_count
    }

@app.get("/forums/thread/{thread_id}/replies", response_model=List[ReplyResponse])
async def get_thread_replies(
    thread_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all replies for a thread"""
    
    # Get replies with user data
    replies = db.query(ForumReply, User, UserProfile).outerjoin(
        User, ForumReply.author_id == User.id
    ).outerjoin(
        UserProfile, User.id == UserProfile.user_id
    ).filter(
        ForumReply.thread_id == thread_id
    ).order_by(ForumReply.created_at).all()
    
    reply_responses = []
    for reply_data in replies:
        reply, user, profile = reply_data
        
        # Get like count for this reply
        like_count = db.query(Like).filter(
            and_(
                Like.content_type == "reply",
                Like.content_id == str(reply.id)
            )
        ).count()
        
        # Check if current user liked this reply
        is_liked = db.query(Like).filter(
            and_(
                Like.user_id == current_user["user_id"],
                Like.content_type == "reply",
                Like.content_id == str(reply.id)
            )
        ).first() is not None
        
        # Create author object
        author_name = "Anonymous"
        author_avatar = None
        if user:
            author_name = f"{user.first_name} {user.last_name}".strip() or user.username
            if profile:
                author_avatar = profile.avatar_url
        
        author = AuthorResponse(
            id=str(user.id) if user else "anonymous",
            name=author_name,
            avatar_url=author_avatar,
            badges=[]  # TODO: Implement user badges system
        )
        
        reply_responses.append(ReplyResponse(
            id=str(reply.id),
            thread_id=str(reply.thread_id),
            content=reply.content,
            author=author,
            created_at=reply.created_at,
            like_count=like_count,
            is_liked=is_liked,
            parent_id=str(reply.parent_id) if reply.parent_id else None
        ))
    
    return reply_responses

@app.delete("/forums/like/{content_type}/{content_id}")
async def unlike_content(
    content_type: str,
    content_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove like from content"""
    
    like = db.query(Like).filter(
        and_(
            Like.user_id == current_user["user_id"],
            Like.content_type == content_type,
            Like.content_id == content_id
        )
    ).first()
    
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    db.delete(like)
    db.commit()
    
    return {"message": "Like removed successfully"}

# User Statistics and Reputation
class UserStatsResponse(BaseModel):
    reputation: int
    forums_joined: int
    threads_liked: int
    threads_created: int
    replies_posted: int
    likes_received: int
    help_score: float

@app.get("/user/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's community statistics and reputation"""
    
    user_id = current_user["user_id"]
    
    # Count forums joined
    forums_joined = db.query(ForumMembership).filter(
        ForumMembership.user_id == user_id,
        ForumMembership.is_active == True
    ).count()
    
    # Count threads liked by user
    threads_liked = db.query(Like).filter(
        Like.user_id == user_id,
        Like.content_type == "thread"
    ).count()
    
    # Count threads created by user
    threads_created = db.query(ForumThread).filter(
        ForumThread.author_id == user_id
    ).count()
    
    # Count replies posted by user
    replies_posted = db.query(ThreadReply).filter(
        ThreadReply.author_id == user_id
    ).count()
    
    # Count likes received on user's content
    likes_on_threads = db.query(func.count(Like.id)).join(
        ForumThread, Like.content_id == ForumThread.id
    ).filter(
        Like.content_type == "thread",
        ForumThread.author_id == user_id
    ).scalar() or 0
    
    likes_on_replies = db.query(func.count(Like.id)).join(
        ThreadReply, Like.content_id == ThreadReply.id
    ).filter(
        Like.content_type == "reply",
        ThreadReply.author_id == user_id  
    ).scalar() or 0
    
    likes_received = likes_on_threads + likes_on_replies
    
    # Calculate reputation score
    reputation = (
        forums_joined * 5 +           # 5 points per forum joined
        threads_created * 10 +        # 10 points per thread created
        replies_posted * 3 +          # 3 points per reply
        likes_received * 2 +          # 2 points per like received
        threads_liked * 1             # 1 point per like given
    )
    
    # Calculate help score (0-10 scale)
    max_possible_score = max(100, reputation)  # Prevent division by zero
    help_score = min(10.0, (reputation / max_possible_score) * 10)
    
    return UserStatsResponse(
        reputation=reputation,
        forums_joined=forums_joined,
        threads_liked=threads_liked,
        threads_created=threads_created,
        replies_posted=replies_posted,
        likes_received=likes_received,
        help_score=round(help_score, 1)
    )

@app.get("/user/activity")
async def get_user_activity(
    limit: int = Query(10, le=50),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's recent community activity"""
    
    user_id = current_user["user_id"]
    
    # Get recent threads created by user
    recent_threads = db.query(ForumThread).filter(
        ForumThread.user_id == user_id
    ).order_by(desc(ForumThread.created_at)).limit(limit//2).all()
    
    # Get recent replies by user  
    recent_replies = db.query(ThreadReply).filter(
        ThreadReply.user_id == user_id
    ).order_by(desc(ThreadReply.created_at)).limit(limit//2).all()
    
    activity = []
    
    # Add threads to activity
    for thread in recent_threads:
        forum = db.query(CommunityForum).filter(CommunityForum.id == thread.forum_id).first()
        content = getattr(thread, 'content', '') or ""
        activity.append({
            "type": "thread_created",
            "id": str(thread.id),
            "title": getattr(thread, 'title', ''),
            "content": content[:200] + "..." if len(content) > 200 else content,
            "forum_name": getattr(forum, 'name', 'Unknown Forum') if forum else "Unknown Forum",
            "created_at": thread.created_at,
            "like_count": db.query(Like).filter(
                Like.content_type == "thread",
                Like.content_id == str(thread.id)
            ).count()
        })
    
    # Add replies to activity
    for reply in recent_replies:
        thread = db.query(ForumThread).filter(ForumThread.id == reply.thread_id).first()
        content = getattr(reply, 'content', '') or ""
        activity.append({
            "type": "reply_posted", 
            "id": str(reply.id),
            "content": content[:200] + "..." if len(content) > 200 else content,
            "thread_title": getattr(thread, 'title', 'Unknown Thread') if thread else "Unknown Thread",
            "created_at": reply.created_at,
            "like_count": db.query(Like).filter(
                Like.content_type == "reply",
                Like.content_id == str(reply.id)
            ).count()
        })
    
    # Sort by created_at descending
    activity.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {"activity": activity[:limit]}

# Initialize default forums
@app.on_event("startup")
async def create_default_forums():
    """Create default forums if they don't exist"""
    db = next(get_db())
    
    existing_forums = db.query(CommunityForum).count()
    if existing_forums == 0:
        default_forums = [
            {
                "name": "General Discussion",
                "description": "General wellness and mental health discussions",
                "category": "general"
            },
            {
                "name": "Anxiety Support",
                "description": "Support group for anxiety management",
                "category": "support"
            },
            {
                "name": "Mindfulness & Meditation",
                "description": "Share meditation practices and mindfulness tips",
                "category": "practice"
            },
            {
                "name": "Daily Check-ins",
                "description": "Share your daily wellness journey",
                "category": "checkin"
            }
        ]
        
        for forum_data in default_forums:
            forum = CommunityForum(**forum_data)
            db.add(forum)
        
        db.commit()
        print(f"Created {len(default_forums)} default forums")

# Events endpoints
@app.get("/forums/events", response_model=List[EventResponse])
async def get_events(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all community events"""
    events = db.query(CommunityEvent).order_by(desc(CommunityEvent.start_time)).all()
    
    # Get user's event participations
    participations = db.query(EventParticipant).filter(
        EventParticipant.user_id == current_user["user_id"]
    ).all()
    
    participating_event_ids = {str(p.event_id) for p in participations}
    
    event_responses = []
    for event in events:
        participant_count = db.query(EventParticipant).filter(
            EventParticipant.event_id == event.id
        ).count()
        
        event_responses.append(EventResponse(
            id=str(event.id),
            title=event.title,
            description=event.description,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location,
            is_virtual=event.is_virtual,
            participant_count=participant_count,
            is_participating=str(event.id) in participating_event_ids,
            created_at=event.created_at
        ))
    
    return event_responses

@app.post("/forums/events", response_model=EventResponse)
async def create_event(
    event_data: EventCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new community event"""
    event = CommunityEvent(
        title=event_data.title,
        description=event_data.description,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        location=event_data.location,
        is_virtual=event_data.is_virtual,
        created_by=current_user["user_id"]
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return EventResponse(
        id=str(event.id),
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        is_virtual=event.is_virtual,
        participant_count=0,
        is_participating=False,
        created_at=event.created_at
    )

@app.post("/forums/events/{event_id}/join")
async def join_event(
    event_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join an event"""
    # Check if event exists
    event = db.query(CommunityEvent).filter(CommunityEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if already participating
    existing = db.query(EventParticipant).filter(
        and_(
            EventParticipant.user_id == current_user["user_id"],
            EventParticipant.event_id == event_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already participating in this event")
    
    # Create participation record
    participation = EventParticipant(
        user_id=current_user["user_id"],
        event_id=event_id
    )
    
    db.add(participation)
    db.commit()
    
    return {"message": "Successfully joined event"}

@app.delete("/forums/events/{event_id}/leave")
async def leave_event(
    event_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave an event"""
    participation = db.query(EventParticipant).filter(
        and_(
            EventParticipant.user_id == current_user["user_id"],
            EventParticipant.event_id == event_id
        )
    ).first()
    
    if not participation:
        raise HTTPException(status_code=404, detail="Not participating in this event")
    
    db.delete(participation)
    db.commit()
    
    return {"message": "Successfully left event"}

# Challenges endpoints
@app.get("/forums/challenges", response_model=List[ChallengeResponse])
async def get_challenges(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all wellness challenges"""
    challenges = db.query(Challenge).order_by(desc(Challenge.start_date)).all()
    
    # Get user's challenge participations
    participations = db.query(ChallengeParticipant).filter(
        ChallengeParticipant.user_id == current_user["user_id"]
    ).all()
    
    participating_challenge_ids = {str(p.challenge_id) for p in participations}
    
    challenge_responses = []
    for challenge in challenges:
        participant_count = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.challenge_id == challenge.id
        ).count()
        
        challenge_responses.append(ChallengeResponse(
            id=str(challenge.id),
            title=challenge.title,
            description=challenge.description,
            category=challenge.category,
            duration_days=challenge.duration_days,
            start_date=challenge.start_date,
            end_date=challenge.end_date,
            participant_count=participant_count,
            is_participating=str(challenge.id) in participating_challenge_ids,
            created_at=challenge.created_at
        ))
    
    return challenge_responses

@app.post("/forums/challenges", response_model=ChallengeResponse)
async def create_challenge(
    challenge_data: ChallengeCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new wellness challenge"""
    challenge = Challenge(
        title=challenge_data.title,
        description=challenge_data.description,
        category=challenge_data.category,
        duration_days=challenge_data.duration_days,
        start_date=challenge_data.start_date,
        end_date=challenge_data.end_date,
        created_by=current_user["user_id"]
    )
    
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    
    return ChallengeResponse(
        id=str(challenge.id),
        title=challenge.title,
        description=challenge.description,
        category=challenge.category,
        duration_days=challenge.duration_days,
        start_date=challenge.start_date,
        end_date=challenge.end_date,
        participant_count=0,
        is_participating=False,
        created_at=challenge.created_at
    )

@app.post("/forums/challenges/{challenge_id}/join")
async def join_challenge(
    challenge_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a challenge"""
    # Check if challenge exists
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Check if already participating
    existing = db.query(ChallengeParticipant).filter(
        and_(
            ChallengeParticipant.user_id == current_user["user_id"],
            ChallengeParticipant.challenge_id == challenge_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already participating in this challenge")
    
    # Create participation record
    participation = ChallengeParticipant(
        user_id=current_user["user_id"],
        challenge_id=challenge_id
    )
    
    db.add(participation)
    db.commit()
    
    return {"message": "Successfully joined challenge"}

@app.delete("/forums/challenges/{challenge_id}/leave")
async def leave_challenge(
    challenge_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave a challenge"""
    participation = db.query(ChallengeParticipant).filter(
        and_(
            ChallengeParticipant.user_id == current_user["user_id"],
            ChallengeParticipant.challenge_id == challenge_id
        )
    ).first()
    
    if not participation:
        raise HTTPException(status_code=404, detail="Not participating in this challenge")
    
    db.delete(participation)
    db.commit()
    
    return {"message": "Successfully left challenge"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "community-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)