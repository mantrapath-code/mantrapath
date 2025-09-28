"""API endpoints for journal operations - placeholder implementation."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.auth import get_current_user

logger = logging.getLogger(__name__)

# Create router with journal prefix to match API Gateway routing
router = APIRouter(prefix="/api/v1/journal", tags=["journal"])


@router.get("/")
async def get_journal_entries_root(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """
    Get journal entries for the authenticated user (root path).
    Handles frontend requests to /api/v1/journal/?limit=50
    """
    logger.info(f"Journal entries requested via root path by user {current_user['user_id']} (limit={limit}, offset={offset})")
    return []


@router.get("/entries")
async def get_journal_entries(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """
    Get journal entries for the authenticated user.
    Placeholder implementation - returns empty list until full journal service is implemented.
    """
    logger.info(f"Journal entries requested by user {current_user['user_id']}")
    return []


@router.post("/entries")
async def create_journal_entry(
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new journal entry.
    Placeholder implementation - returns not implemented message.
    """
    logger.info(f"Journal entry creation attempted by user {current_user['user_id']}")
    raise HTTPException(
        status_code=501, 
        detail="Journal functionality is planned for future release. Currently supports mood tracking."
    )


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