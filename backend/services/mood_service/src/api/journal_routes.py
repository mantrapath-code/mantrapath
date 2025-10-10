"""API endpoints for journal operations."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from shared.database import get_db
from shared.auth import get_current_user
from shared.models import JournalEntry

logger = logging.getLogger(__name__)

# Create router with journal prefix to match API Gateway routing
router = APIRouter(prefix="/api/v1/journal", tags=["journal"])


class JournalCreateRequest(BaseModel):
    """Request schema for creating journal entries"""
    title: Optional[str] = None
    content: str
    mood_before: Optional[int] = None
    mood_after: Optional[int] = None
    is_private: Optional[bool] = True


class JournalEntryResponse(BaseModel):
    """Response schema for journal entries"""
    id: str
    title: Optional[str] = None
    content: str
    mood_before: Optional[int] = None
    mood_after: Optional[int] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    themes: List[str] = []
    is_private: bool = True
    created_at: str
    user_id: str

    class Config:
        from_attributes = True


@router.get("/")
async def get_journal_entries_root(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get journal entries for the authenticated user (root path).
    Handles frontend requests to /api/v1/journal/?limit=50
    """
    logger.info(f"Journal entries requested via root path by user {current_user['user_id']} (limit={limit}, offset={offset})")
    
    try:
        # Query journal entries from database
        query = db.query(JournalEntry).filter(
            JournalEntry.user_id == current_user['user_id']
        ).order_by(JournalEntry.created_at.desc())
        
        if offset > 0:
            query = query.offset(offset)
            
        entries = query.limit(limit).all()
        
        # Convert to response format
        response_entries = []
        for entry in entries:
            response_entries.append({
                "id": entry.id,
                "title": entry.title,
                "content": entry.content,
                "mood_before": entry.mood_before,
                "mood_after": entry.mood_after,
                "sentiment_score": entry.sentiment_score,
                "sentiment_label": entry.sentiment_label,
                "themes": entry.themes or [],
                "is_private": entry.is_private,
                "created_at": entry.created_at.isoformat() if entry.created_at else datetime.utcnow().isoformat(),
                "user_id": entry.user_id
            })
        
        logger.info(f"Returning {len(response_entries)} journal entries for user {current_user['user_id']}")
        return response_entries
        
    except Exception as e:
        logger.error(f"Error fetching journal entries: {e}")
        return []


@router.post("/")
async def create_journal_entry_root(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new journal entry (root path).
    Handles frontend requests to POST /api/v1/journal/
    """
    logger.info(f"Journal entry creation via root path by user {current_user['user_id']}")
    
    try:
        # Parse request body
        body = await request.json()
        
        # Create journal entry request
        journal_data = JournalCreateRequest(
            title=body.get('title'),
            content=body.get('content', ''),
            mood_before=body.get('mood_before'),
            mood_after=body.get('mood_after'),
            is_private=body.get('is_private', True)
        )
        
        if not journal_data.content.strip():
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Create new journal entry
        journal_entry = JournalEntry(
            user_id=current_user['user_id'],
            title=journal_data.title,
            content=journal_data.content,
            mood_before=journal_data.mood_before,
            mood_after=journal_data.mood_after,
            is_private=journal_data.is_private,
            created_at=datetime.utcnow()
        )
        
        # Save to database
        db.add(journal_entry)
        db.commit()
        db.refresh(journal_entry)
        
        # Return created entry
        response = {
            "id": journal_entry.id,
            "title": journal_entry.title,
            "content": journal_entry.content,
            "mood_before": journal_entry.mood_before,
            "mood_after": journal_entry.mood_after,
            "sentiment_score": journal_entry.sentiment_score,
            "sentiment_label": journal_entry.sentiment_label,
            "themes": journal_entry.themes or [],
            "is_private": journal_entry.is_private,
            "created_at": journal_entry.created_at.isoformat(),
            "user_id": journal_entry.user_id
        }
        
        logger.info(f"Created journal entry {journal_entry.id} for user {current_user['user_id']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create journal entry: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create journal entry")


@router.get("/entries")
async def get_journal_entries(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get journal entries for the authenticated user.
    """
    logger.info(f"Journal entries requested by user {current_user['user_id']}")
    return await get_journal_entries_root(limit, offset, current_user, db)


@router.post("/entries")
async def create_journal_entry(
    journal_data: JournalCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new journal entry.
    """
    logger.info(f"Journal entry creation attempted by user {current_user['user_id']}")
    
    if not journal_data.content.strip():
        raise HTTPException(status_code=400, detail="Content is required")
    
    try:
        # Create new journal entry
        journal_entry = JournalEntry(
            user_id=current_user['user_id'],
            title=journal_data.title,
            content=journal_data.content,
            mood_before=journal_data.mood_before,
            mood_after=journal_data.mood_after,
            is_private=journal_data.is_private,
            created_at=datetime.utcnow()
        )
        
        # Save to database
        db.add(journal_entry)
        db.commit()
        db.refresh(journal_entry)
        
        # Return created entry
        return JournalEntryResponse(
            id=journal_entry.id,
            title=journal_entry.title,
            content=journal_entry.content,
            mood_before=journal_entry.mood_before,
            mood_after=journal_entry.mood_after,
            sentiment_score=journal_entry.sentiment_score,
            sentiment_label=journal_entry.sentiment_label,
            themes=journal_entry.themes or [],
            is_private=journal_entry.is_private,
            created_at=journal_entry.created_at.isoformat(),
            user_id=journal_entry.user_id
        )
        
    except Exception as e:
        logger.error(f"Failed to create journal entry: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create journal entry")


@router.get("/entries/{entry_id}")
async def get_journal_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific journal entry by ID.
    """
    logger.info(f"Journal entry {entry_id} requested by user {current_user['user_id']}")
    
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user['user_id']
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    return JournalEntryResponse(
        id=entry.id,
        title=entry.title,
        content=entry.content,
        mood_before=entry.mood_before,
        mood_after=entry.mood_after,
        sentiment_score=entry.sentiment_score,
        sentiment_label=entry.sentiment_label,
        themes=entry.themes or [],
        is_private=entry.is_private,
        created_at=entry.created_at.isoformat(),
        user_id=entry.user_id
    )


@router.put("/entries/{entry_id}")
async def update_journal_entry(
    entry_id: str,
    journal_data: JournalCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a journal entry.
    """
    logger.info(f"Journal entry {entry_id} update attempted by user {current_user['user_id']}")
    
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user['user_id']
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    try:
        # Update entry fields
        if journal_data.title is not None:
            entry.title = journal_data.title
        if journal_data.content:
            entry.content = journal_data.content
        if journal_data.mood_before is not None:
            entry.mood_before = journal_data.mood_before
        if journal_data.mood_after is not None:
            entry.mood_after = journal_data.mood_after
        if journal_data.is_private is not None:
            entry.is_private = journal_data.is_private
        
        db.commit()
        db.refresh(entry)
        
        return JournalEntryResponse(
            id=entry.id,
            title=entry.title,
            content=entry.content,
            mood_before=entry.mood_before,
            mood_after=entry.mood_after,
            sentiment_score=entry.sentiment_score,
            sentiment_label=entry.sentiment_label,
            themes=entry.themes or [],
            is_private=entry.is_private,
            created_at=entry.created_at.isoformat(),
            user_id=entry.user_id
        )
        
    except Exception as e:
        logger.error(f"Failed to update journal entry: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update journal entry")


@router.delete("/entries/{entry_id}")
async def delete_journal_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a journal entry.
    """
    logger.info(f"Journal entry {entry_id} deletion attempted by user {current_user['user_id']}")
    
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user['user_id']
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    try:
        db.delete(entry)
        db.commit()
        return {"message": "Journal entry deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete journal entry: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete journal entry")