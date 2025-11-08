"""API endpoints for journal operations - placeholder implementation."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.auth import get_current_user
from shared.models import JournalEntry

logger = logging.getLogger(__name__)

# Create router with journal prefix to match API Gateway routing
router = APIRouter(prefix="/api/v1/journal", tags=["journal"])


def _serialize_journal_entry(entry: JournalEntry) -> dict:
    return {
        "id": entry.id,
        "user_id": entry.user_id,
        "title": entry.title,
        "content": entry.content,
        "mood_before": entry.mood_before,
        "mood_after": entry.mood_after,
        "sentiment_score": entry.sentiment_score,
        "sentiment_label": entry.sentiment_label,
        "themes": entry.themes,
        "is_private": entry.is_private,
        "word_count": entry.word_count,
        "reading_time": entry.reading_time,
        "entry_type": entry.entry_type,
        "video_analysis": entry.video_analysis,
        "created_at": entry.created_at,
        "updated_at": entry.updated_at,
    }


def _get_user_journal_entries(
    db: Session,
    user_id: str,
    limit: int,
    offset: int,
) -> List[dict]:
    # Guardrails
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == user_id)
        .order_by(JournalEntry.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_serialize_journal_entry(entry) for entry in entries]


@router.get("/")
async def get_journal_entries_root(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get journal entries for the authenticated user (root path).
    Handles frontend requests to /api/v1/journal/?limit=50
    """
    logger.info(
        "Journal entries requested via root path by user %s (limit=%s, offset=%s)",
        current_user["user_id"],
        limit,
        offset,
    )
    return _get_user_journal_entries(db, current_user["user_id"], limit, offset)


@router.post("/")
async def create_journal_entry_root(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new journal entry (root path).
    Handles frontend requests to POST /api/v1/journal/
    """
    from shared.models import JournalEntry
    from datetime import datetime
    
    body = await request.json()
    logger.info(f"Journal entry creation attempted via root path by user {current_user['user_id']}")
    
    # Extract fields from request
    entry_type = body.get('entry_type', 'text')
    video_analysis = body.get('video_analysis')
    
    # Create journal entry
    journal_entry = JournalEntry(
        user_id=current_user['user_id'],
        title=body.get('title'),
        content=body.get('content', ''),
        mood_before=body.get('mood_before'),
        mood_after=body.get('mood_after'),
        is_private=body.get('is_private', True),
        entry_type=entry_type,
        video_analysis=video_analysis,
        created_at=datetime.utcnow()
    )
    
    db.add(journal_entry)
    db.commit()
    db.refresh(journal_entry)
    
    logger.info(f"Journal entry created via root path: {journal_entry.id} by user {current_user['user_id']}")
    return journal_entry


@router.get("/entries")
async def get_journal_entries(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get journal entries for the authenticated user.
    """
    logger.info(
        "Journal entries requested by user %s (limit=%s, offset=%s)",
        current_user["user_id"],
        limit,
        offset,
    )
    return _get_user_journal_entries(db, current_user["user_id"], limit, offset)


@router.post("/entries")
async def create_journal_entry(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new journal entry.
    Supports both text and video journal entries.
    """
    from shared.models import JournalEntry
    from datetime import datetime
    
    body = await request.json()
    logger.info(f"Journal entry creation attempted by user {current_user['user_id']}")
    
    # Extract fields from request
    entry_type = body.get('entry_type', 'text')
    video_analysis = body.get('video_analysis')
    
    # Create journal entry
    journal_entry = JournalEntry(
        user_id=current_user['user_id'],
        title=body.get('title'),
        content=body.get('content', ''),
        mood_before=body.get('mood_before'),
        mood_after=body.get('mood_after'),
        is_private=body.get('is_private', True),
        entry_type=entry_type,
        video_analysis=video_analysis,
        created_at=datetime.utcnow()
    )
    
    db.add(journal_entry)
    db.commit()
    db.refresh(journal_entry)
    
    logger.info(f"Journal entry created: {journal_entry.id} by user {current_user['user_id']}")
    return journal_entry


@router.get("/entries/{entry_id}")
async def get_journal_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific journal entry by ID.
    Placeholder implementation.
    """
    logger.info(f"Journal entry {entry_id} requested by user {current_user['user_id']}")
    raise HTTPException(
        status_code=404, 
        detail="Journal entry not found. Journal functionality is not yet implemented."
    )


@router.put("/entries/{entry_id}")
async def update_journal_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a journal entry.
    Placeholder implementation.
    """
    logger.info(f"Journal entry {entry_id} update attempted by user {current_user['user_id']}")
    raise HTTPException(
        status_code=501,
        detail="Journal functionality is planned for future release."
    )


@router.delete("/entries/{entry_id}")
async def delete_journal_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a journal entry.
    Placeholder implementation.
    """
    logger.info(f"Journal entry {entry_id} deletion attempted by user {current_user['user_id']}")
    raise HTTPException(
        status_code=501,
        detail="Journal functionality is planned for future release."
    )