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

from shared.database import get_database, engine
from shared.models import Forum, ForumThread, ForumReply, ForumMembership, Like, Base
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
class ForumResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    member_count: int
    is_joined: bool = False

class ThreadCreate(BaseModel):
    forum_id: str
    title: str
    content: str

class ThreadResponse(BaseModel):
    id: str
    forum_id: str
    title: str
    content: str
    author: str
    reply_count: int
    view_count: int
    created_at: datetime
    is_pinned: bool

class ReplyCreate(BaseModel):
    thread_id: str
    content: str
    parent_id: Optional[str] = None

class ReplyResponse(BaseModel):
    id: str
    thread_id: str
    content: str
    author: str
    created_at: datetime
    likes_count: int = 0

class LikeRequest(BaseModel):
    content_type: str  # 'thread' or 'reply'
    content_id: str

# Forum endpoints
@app.get("/forums", response_model=List[ForumResponse])
async def get_forums(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get all forums with membership status"""
    
    forums = db.query(Forum).all()
    
    # Get user's forum memberships
    memberships = db.query(ForumMembership).filter(
        ForumMembership.user_id == current_user["user_id"]
    ).all()
    
    member_forum_ids = {str(membership.forum_id) for membership in memberships}
    
    return [
        ForumResponse(
            id=str(forum.id),
            name=forum.name,
            description=forum.description,
            category=forum.category,
            member_count=forum.member_count,
            is_joined=str(forum.id) in member_forum_ids
        )
        for forum in forums
    ]

@app.post("/forums/{forum_id}/join")
async def join_forum(
    forum_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
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
    
    # Update member count
    forum = db.query(Forum).filter(Forum.id == forum_id).first()
    if forum:
        forum.member_count += 1
    
    db.commit()
    
    return {"message": "Successfully joined forum"}

@app.delete("/forums/{forum_id}/leave")
async def leave_forum(
    forum_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
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
    
    # Update member count
    forum = db.query(Forum).filter(Forum.id == forum_id).first()
    if forum and forum.member_count > 0:
        forum.member_count -= 1
    
    db.commit()
    
    return {"message": "Successfully left forum"}

# Thread endpoints
@app.get("/forums/{forum_id}/threads", response_model=List[ThreadResponse])
async def get_forum_threads(
    forum_id: str,
    limit: int = Query(20, le=50),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get threads in a forum"""
    
    threads = db.query(ForumThread).filter(
        ForumThread.forum_id == forum_id
    ).order_by(desc(ForumThread.is_pinned), desc(ForumThread.created_at)).limit(limit).all()
    
    return [
        ThreadResponse(
            id=str(thread.id),
            forum_id=str(thread.forum_id),
            title=thread.title,
            content=thread.content,
            author="Anonymous",  # TODO: Join with user table
            reply_count=thread.reply_count,
            view_count=thread.view_count,
            created_at=thread.created_at,
            is_pinned=thread.is_pinned
        )
        for thread in threads
    ]

@app.post("/forums/thread", response_model=ThreadResponse)
async def create_thread(
    thread_data: ThreadCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
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
    
    return ThreadResponse(
        id=str(thread.id),
        forum_id=str(thread.forum_id),
        title=thread.title,
        content=thread.content,
        author="You",
        reply_count=0,
        view_count=0,
        created_at=thread.created_at,
        is_pinned=False
    )

@app.get("/forums/thread/{thread_id}", response_model=ThreadResponse)
async def get_thread(
    thread_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get thread details and increment view count"""
    
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Increment view count
    thread.view_count += 1
    db.commit()
    
    return ThreadResponse(
        id=str(thread.id),
        forum_id=str(thread.forum_id),
        title=thread.title,
        content=thread.content,
        author="Anonymous",
        reply_count=thread.reply_count,
        view_count=thread.view_count,
        created_at=thread.created_at,
        is_pinned=thread.is_pinned
    )

# Reply endpoints
@app.post("/forums/thread/{thread_id}/reply", response_model=ReplyResponse)
async def create_reply(
    thread_id: str,
    reply_data: ReplyCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
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
    thread.reply_count += 1
    
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
async def like_content(
    like_data: LikeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Like thread or reply"""
    
    # Check if already liked
    existing = db.query(Like).filter(
        and_(
            Like.user_id == current_user["user_id"],
            Like.content_type == like_data.content_type,
            Like.content_id == like_data.content_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already liked this content")
    
    like = Like(
        user_id=current_user["user_id"],
        content_type=like_data.content_type,
        content_id=like_data.content_id
    )
    
    db.add(like)
    db.commit()
    
    return {"message": "Content liked successfully"}

@app.delete("/forums/like/{content_type}/{content_id}")
async def unlike_content(
    content_type: str,
    content_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
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

# Initialize default forums
@app.on_event("startup")
async def create_default_forums():
    """Create default forums if they don't exist"""
    db = next(get_database())
    
    existing_forums = db.query(Forum).count()
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
            forum = Forum(**forum_data)
            db.add(forum)
        
        db.commit()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "community-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)