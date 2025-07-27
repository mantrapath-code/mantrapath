"""
Community Service - Forums, discussions, and social features
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
from pydantic import BaseModel, UUID4
import json
import redis

# Import shared modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.database import get_db
from shared.auth import get_current_user, get_optional_user, require_moderator
from shared.models import (
    Forum, ForumThread, ForumPost, Like, User, UserProfile
)

app = FastAPI(
    title="MantraPath Community Service",
    description="Forums, discussions, and social features",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for caching
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Pydantic models
class ForumCreate(BaseModel):
    name: str
    description: str
    category: str
    is_public: bool = True
    requires_approval: bool = False

class ForumResponse(BaseModel):
    id: UUID4
    name: str
    description: str
    category: str
    is_public: bool
    thread_count: int
    member_count: int
    created_at: datetime

class ThreadCreate(BaseModel):
    forum_id: UUID4
    title: str
    content: str
    tags: Optional[List[str]] = []

class ThreadResponse(BaseModel):
    id: UUID4
    forum_id: UUID4
    title: str
    content: str
    author: Dict[str, Any]
    view_count: int
    reply_count: int
    like_count: int
    tags: List[str]
    is_pinned: bool
    is_locked: bool
    created_at: datetime

class PostCreate(BaseModel):
    thread_id: UUID4
    content: str

class PostResponse(BaseModel):
    id: UUID4
    thread_id: UUID4
    content: str
    author: Dict[str, Any]
    like_count: int
    created_at: datetime

class LikeCreate(BaseModel):
    content_type: str  # thread, post
    content_id: UUID4

class CommentCreate(BaseModel):
    content: str
    content_type: str
    content_id: UUID4

# Utility functions
def get_user_info(user_id: str, db: Session) -> Dict[str, Any]:
    """Get basic user info for display"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"id": user_id, "full_name": "Unknown User", "avatar_url": None}
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "avatar_url": profile.avatar_url if profile else None,
        "role": user.role
    }

def cache_forum_stats(forum_id: str, stats: Dict[str, Any]):
    """Cache forum statistics"""
    redis_client.setex(f"forum_stats:{forum_id}", 300, json.dumps(stats))

def get_cached_forum_stats(forum_id: str) -> Optional[Dict[str, Any]]:
    """Get cached forum statistics"""
    cached = redis_client.get(f"forum_stats:{forum_id}")
    return json.loads(cached) if cached else None

# Forum endpoints
@app.get("/forums", response_model=List[ForumResponse])
async def get_forums(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get list of forums"""
    query = db.query(Forum)
    
    # Filter by category if provided
    if category:
        query = query.filter(Forum.category == category)
    
    # Only show public forums to non-authenticated users
    if not current_user:
        query = query.filter(Forum.is_public == True)
    
    forums = query.order_by(Forum.name).all()
    
    result = []
    for forum in forums:
        # Get or calculate stats
        stats = get_cached_forum_stats(str(forum.id))
        if not stats:
            thread_count = db.query(func.count(ForumThread.id)).filter(
                ForumThread.forum_id == forum.id
            ).scalar()
            
            # For member count, we'd need a forum_members table
            # For now, use unique thread authors as approximation
            member_count = db.query(func.count(func.distinct(ForumThread.user_id))).filter(
                ForumThread.forum_id == forum.id
            ).scalar()
            
            stats = {"thread_count": thread_count, "member_count": member_count}
            cache_forum_stats(str(forum.id), stats)
        
        result.append(ForumResponse(
            id=forum.id,
            name=forum.name,
            description=forum.description,
            category=forum.category,
            is_public=forum.is_public,
            thread_count=stats["thread_count"],
            member_count=stats["member_count"],
            created_at=forum.created_at
        ))
    
    return result

@app.post("/forums", response_model=ForumResponse)
async def create_forum(
    forum_data: ForumCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_moderator)
):
    """Create a new forum (moderator/admin only)"""
    forum = Forum(
        id=uuid.uuid4(),
        name=forum_data.name,
        description=forum_data.description,
        category=forum_data.category,
        is_public=forum_data.is_public,
        requires_approval=forum_data.requires_approval,
        moderator_ids=[current_user["user_id"]]
    )
    
    db.add(forum)
    db.commit()
    db.refresh(forum)
    
    return ForumResponse(
        id=forum.id,
        name=forum.name,
        description=forum.description,
        category=forum.category,
        is_public=forum.is_public,
        thread_count=0,
        member_count=0,
        created_at=forum.created_at
    )

@app.get("/forums/{forum_id}")
async def get_forum(
    forum_id: UUID4,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get forum details"""
    forum = db.query(Forum).filter(Forum.id == forum_id).first()
    if not forum:
        raise HTTPException(status_code=404, detail="Forum not found")
    
    # Check access permissions
    if not forum.is_public and not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return forum

# Thread endpoints
@app.get("/forums/{forum_id}/threads", response_model=List[ThreadResponse])
async def get_forum_threads(
    forum_id: UUID4,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at|reply_count|like_count|view_count)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get threads in a forum"""
    # Verify forum exists and user has access
    forum = db.query(Forum).filter(Forum.id == forum_id).first()
    if not forum:
        raise HTTPException(status_code=404, detail="Forum not found")
    
    if not forum.is_public and not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Build query
    query = db.query(ForumThread).filter(ForumThread.forum_id == forum_id)
    
    # Apply sorting
    sort_column = getattr(ForumThread, sort_by)
    if order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Apply pagination
    threads = query.offset(skip).limit(limit).all()
    
    # Format response
    result = []
    for thread in threads:
        author_info = get_user_info(str(thread.user_id), db)
        
        result.append(ThreadResponse(
            id=thread.id,
            forum_id=thread.forum_id,
            title=thread.title,
            content=thread.content,
            author=author_info,
            view_count=thread.view_count,
            reply_count=thread.reply_count,
            like_count=thread.like_count,
            tags=thread.tags or [],
            is_pinned=thread.is_pinned,
            is_locked=thread.is_locked,
            created_at=thread.created_at
        ))
    
    return result

@app.post("/forums/thread", response_model=ThreadResponse)
async def create_thread(
    thread_data: ThreadCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new forum thread"""
    # Verify forum exists
    forum = db.query(Forum).filter(Forum.id == thread_data.forum_id).first()
    if not forum:
        raise HTTPException(status_code=404, detail="Forum not found")
    
    # Check if user can post (forum might require approval)
    if forum.requires_approval and current_user.get("role") not in ["admin", "moderator"]:
        is_approved = False
    else:
        is_approved = True
    
    thread = ForumThread(
        id=uuid.uuid4(),
        forum_id=thread_data.forum_id,
        user_id=current_user["user_id"],
        title=thread_data.title,
        content=thread_data.content,
        tags=thread_data.tags,
        is_approved=is_approved
    )
    
    db.add(thread)
    db.commit()
    db.refresh(thread)
    
    # Update forum stats
    db.query(Forum).filter(Forum.id == thread_data.forum_id).update({
        "thread_count": Forum.thread_count + 1
    })
    db.commit()
    
    # Clear cache
    redis_client.delete(f"forum_stats:{thread_data.forum_id}")
    
    author_info = get_user_info(current_user["user_id"], db)
    
    return ThreadResponse(
        id=thread.id,
        forum_id=thread.forum_id,
        title=thread.title,
        content=thread.content,
        author=author_info,
        view_count=0,
        reply_count=0,
        like_count=0,
        tags=thread.tags or [],
        is_pinned=False,
        is_locked=False,
        created_at=thread.created_at
    )

@app.get("/forums/thread/{thread_id}", response_model=ThreadResponse)
async def get_thread(
    thread_id: UUID4,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get thread details"""
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Check forum access
    forum = db.query(Forum).filter(Forum.id == thread.forum_id).first()
    if not forum.is_public and not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Increment view count
    db.query(ForumThread).filter(ForumThread.id == thread_id).update({
        "view_count": ForumThread.view_count + 1
    })
    db.commit()
    
    author_info = get_user_info(str(thread.user_id), db)
    
    return ThreadResponse(
        id=thread.id,
        forum_id=thread.forum_id,
        title=thread.title,
        content=thread.content,
        author=author_info,
        view_count=thread.view_count + 1,  # Include the increment
        reply_count=thread.reply_count,
        like_count=thread.like_count,
        tags=thread.tags or [],
        is_pinned=thread.is_pinned,
        is_locked=thread.is_locked,
        created_at=thread.created_at
    )

@app.post("/forums/thread/{thread_id}/reply", response_model=PostResponse)
async def reply_to_thread(
    thread_id: UUID4,
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Reply to a forum thread"""
    # Verify thread exists and is not locked
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    if thread.is_locked:
        raise HTTPException(status_code=403, detail="Thread is locked")
    
    # Create post
    post = ForumPost(
        id=uuid.uuid4(),
        thread_id=thread_id,
        user_id=current_user["user_id"],
        content=post_data.content
    )
    
    db.add(post)
    
    # Update thread reply count
    db.query(ForumThread).filter(ForumThread.id == thread_id).update({
        "reply_count": ForumThread.reply_count + 1
    })
    
    db.commit()
    db.refresh(post)
    
    author_info = get_user_info(current_user["user_id"], db)
    
    return PostResponse(
        id=post.id,
        thread_id=post.thread_id,
        content=post.content,
        author=author_info,
        like_count=0,
        created_at=post.created_at
    )

# Like system
@app.post("/forums/like")
async def like_content(
    like_data: LikeCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Like a thread or post"""
    # Check if already liked
    existing_like = db.query(Like).filter(
        and_(
            Like.user_id == current_user["user_id"],
            Like.content_type == like_data.content_type,
            Like.content_id == like_data.content_id
        )
    ).first()
    
    if existing_like:
        raise HTTPException(status_code=400, detail="Already liked")
    
    # Create like
    like = Like(
        id=uuid.uuid4(),
        user_id=current_user["user_id"],
        content_type=like_data.content_type,
        content_id=like_data.content_id
    )
    
    db.add(like)
    
    # Update like count
    if like_data.content_type == "thread":
        db.query(ForumThread).filter(ForumThread.id == like_data.content_id).update({
            "like_count": ForumThread.like_count + 1
        })
    elif like_data.content_type == "post":
        db.query(ForumPost).filter(ForumPost.id == like_data.content_id).update({
            "like_count": ForumPost.like_count + 1
        })
    
    db.commit()
    
    return {"message": "Content liked successfully"}

@app.delete("/forums/like/{content_type}/{content_id}")
async def unlike_content(
    content_type: str,
    content_id: UUID4,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
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
    
    # Update like count
    if content_type == "thread":
        db.query(ForumThread).filter(ForumThread.id == content_id).update({
            "like_count": ForumThread.like_count - 1
        })
    elif content_type == "post":
        db.query(ForumPost).filter(ForumPost.id == content_id).update({
            "like_count": ForumPost.like_count - 1
        })
    
    db.commit()
    
    return {"message": "Like removed successfully"}

@app.get("/forums/like/{content_type}/{content_id}")
async def get_like_status(
    content_type: str,
    content_id: UUID4,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Check if user has liked content"""
    if not current_user:
        return {"liked": False}
    
    like = db.query(Like).filter(
        and_(
            Like.user_id == current_user["user_id"],
            Like.content_type == content_type,
            Like.content_id == content_id
        )
    ).first()
    
    return {"liked": bool(like)}

# Search
@app.get("/forums/search")
async def search_forums(
    q: str = Query(..., min_length=3),
    content_type: Optional[str] = Query(None, regex="^(thread|post|all)$"),
    forum_id: Optional[UUID4] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Search forum content"""
    results = {"threads": [], "posts": []}
    
    # Search threads
    if content_type in [None, "thread", "all"]:
        thread_query = db.query(ForumThread).filter(
            or_(
                ForumThread.title.ilike(f"%{q}%"),
                ForumThread.content.ilike(f"%{q}%")
            )
        )
        
        if forum_id:
            thread_query = thread_query.filter(ForumThread.forum_id == forum_id)
        
        # Only search public forums for non-authenticated users
        if not current_user:
            thread_query = thread_query.join(Forum).filter(Forum.is_public == True)
        
        threads = thread_query.offset(skip).limit(limit).all()
        
        for thread in threads:
            author_info = get_user_info(str(thread.user_id), db)
            results["threads"].append({
                "id": str(thread.id),
                "forum_id": str(thread.forum_id),
                "title": thread.title,
                "content": thread.content[:200] + "..." if len(thread.content) > 200 else thread.content,
                "author": author_info,
                "created_at": thread.created_at.isoformat()
            })
    
    # Search posts
    if content_type in [None, "post", "all"]:
        post_query = db.query(ForumPost).filter(
            ForumPost.content.ilike(f"%{q}%")
        )
        
        # Only search public forums
        if not current_user:
            post_query = post_query.join(ForumThread).join(Forum).filter(Forum.is_public == True)
        
        posts = post_query.offset(skip).limit(limit).all()
        
        for post in posts:
            author_info = get_user_info(str(post.user_id), db)
            results["posts"].append({
                "id": str(post.id),
                "thread_id": str(post.thread_id),
                "content": post.content[:200] + "..." if len(post.content) > 200 else post.content,
                "author": author_info,
                "created_at": post.created_at.isoformat()
            })
    
    return results

# Health check
@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "community_service",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)