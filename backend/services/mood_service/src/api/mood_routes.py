"""API endpoints for mood operations."""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.auth import verify_token, extract_user_id, get_current_user
from shared.models import MoodEntry
from src.models.schemas import (
    MoodCreateRequest,
    MoodEntryResponse,
    EmotionAnalysisRequest,
    MoodAnalysisResult,
    MoodAnalyticsOverview,
    MoodPatternsResponse,
    MoodContextRequest,
    MoodContextResponse
)
from src.services import emotion_service, mood_data_service, memory_integration_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/mood", tags=["mood"])


@router.post("/entries", response_model=MoodEntryResponse)
async def create_mood_entry(
    mood_data: MoodCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new mood entry for the authenticated user.
    
    Automatically performs emotion analysis on the description if provided.
    """
    try:
        emotion_analysis = None
        
        # Prepare text for emotion analysis (handle both new and legacy formats)
        text_for_analysis = None
        if mood_data.input_text and mood_data.input_text.strip():
            text_for_analysis = mood_data.input_text
        elif mood_data.description and mood_data.description.strip():
            text_for_analysis = mood_data.description
        elif mood_data.notes and mood_data.notes.strip():
            text_for_analysis = mood_data.notes
        
        # Perform emotion analysis if text is provided
        if text_for_analysis:
            try:
                analysis_result = await emotion_service.analyze_emotion(text_for_analysis)
                emotion_analysis = analysis_result.model_dump()
            except Exception as e:
                logger.warning(f"Emotion analysis failed for mood entry: {e}")
        
        # Create mood entry
        mood_entry = await mood_data_service.create_mood_entry(
            db=db,
            user_id=current_user["user_id"],
            mood_data=mood_data,
            emotion_analysis=emotion_analysis
        )
        
        # Background task: notify chatbot about mood changes
        background_tasks.add_task(
            memory_integration_service.notify_chatbot_mood_change,
            user_id=current_user["user_id"],
            mood_entry=mood_entry.model_dump()
        )
        
        return mood_entry
        
    except Exception as e:
        logger.error(f"Failed to create mood entry: {e}")
        raise HTTPException(status_code=500, detail="Failed to create mood entry")


@router.get("/entries", response_model=List[MoodEntryResponse])
async def get_mood_entries(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get mood entries for the authenticated user.
    
    Parameters:
    - limit: Maximum number of entries to return (default: 50, max: 100)
    - offset: Number of entries to skip for pagination (default: 0)
    """
    try:
        # Validate parameters
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 1
        if offset < 0:
            offset = 0
        
        entries = await mood_data_service.get_user_mood_entries(
            db=db,
            user_id=current_user["user_id"],
            limit=limit,
            offset=offset
        )
        
        return entries
        
    except Exception as e:
        logger.error(f"Failed to get mood entries: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve mood entries")


@router.get("/entries/{entry_id}", response_model=MoodEntryResponse)
async def get_mood_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific mood entry by ID.
    
    Only returns the entry if it belongs to the authenticated user.
    """
    try:
        entry = db.query(MoodEntry).filter(
            MoodEntry.id == entry_id,
            MoodEntry.user_id == current_user["user_id"]
        ).first()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Mood entry not found")
        
        return MoodEntryResponse.model_validate(entry)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get mood entry: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve mood entry")


@router.put("/entries/{entry_id}", response_model=MoodEntryResponse)
async def update_mood_entry(
    entry_id: int,
    mood_data: MoodCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing mood entry.
    
    Only allows updating entries that belong to the authenticated user.
    """
    try:
        # Find the entry
        entry = db.query(MoodEntry).filter(
            MoodEntry.id == entry_id,
            MoodEntry.user_id == current_user["user_id"]
        ).first()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Mood entry not found")
        
        # Perform emotion analysis if description changed
        emotion_analysis = None
        if mood_data.description and mood_data.description.strip():
            try:
                analysis_result = await emotion_service.analyze_emotion(mood_data.description)
                emotion_analysis = analysis_result.model_dump()
            except Exception as e:
                logger.warning(f"Emotion analysis failed for mood entry update: {e}")
        
        # Update the entry
        entry.mood_score = mood_data.mood_score
        entry.description = mood_data.description
        entry.stress_level = mood_data.stress_level
        entry.energy_level = mood_data.energy_level
        entry.context_tags = mood_data.context_tags
        entry.location = mood_data.location
        entry.activity = mood_data.activity
        
        if emotion_analysis:
            entry.emotion_analysis = emotion_analysis
        
        entry.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entry)
        
        # Background task: notify chatbot about mood changes
        background_tasks.add_task(
            memory_integration_service.notify_chatbot_mood_change,
            user_id=current_user["user_id"],
            mood_entry=MoodEntryResponse.model_validate(entry).model_dump()
        )
        
        return MoodEntryResponse.model_validate(entry)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update mood entry: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update mood entry")


@router.delete("/entries/{entry_id}")
async def delete_mood_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a mood entry.
    
    Only allows deleting entries that belong to the authenticated user.
    """
    try:
        # Find the entry
        entry = db.query(MoodEntry).filter(
            MoodEntry.id == entry_id,
            MoodEntry.user_id == current_user["user_id"]
        ).first()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Mood entry not found")
        
        # Delete the entry
        db.delete(entry)
        db.commit()
        
        return {"success": True, "message": "Mood entry deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete mood entry: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete mood entry")


@router.get("/analytics/overview", response_model=MoodAnalyticsOverview)
async def get_mood_analytics_overview(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get analytics overview for the authenticated user's mood data.
    
    Includes statistics like average mood, streaks, distributions, and trends.
    """
    try:
        analytics = await mood_data_service.get_mood_analytics_overview(
            db=db,
            user_id=current_user["user_id"]
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"Failed to get mood analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve mood analytics")


@router.get("/analytics/patterns", response_model=MoodPatternsResponse)
async def get_mood_patterns(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get weekly mood patterns and insights for the authenticated user.
    
    Analyzes trends, generates insights, and provides recommendations.
    """
    try:
        patterns = await mood_data_service.get_weekly_patterns(
            db=db,
            user_id=current_user["user_id"]
        )
        
        return patterns
        
    except Exception as e:
        logger.error(f"Failed to get mood patterns: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve mood patterns")


@router.post("/analyze", response_model=MoodAnalysisResult)
async def analyze_emotion(
    request: EmotionAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze emotions in text using AI.
    
    Optionally saves the analysis as a mood entry if include_mood_entry is True.
    """
    try:
        # Perform emotion analysis
        analysis_result = await emotion_service.analyze_emotion(request.text)
        
        # Optionally create mood entry
        if request.include_mood_entry:
            if not request.mood_score:
                raise HTTPException(
                    status_code=400,
                    detail="mood_score is required when include_mood_entry is True"
                )
            
            mood_data = MoodCreateRequest(
                mood_score=request.mood_score,
                description=request.text
            )
            
            mood_entry = await mood_data_service.create_mood_entry(
                db=db,
                user_id=current_user["user_id"],
                mood_data=mood_data,
                emotion_analysis=analysis_result.model_dump()
            )
            
            # Background task: notify chatbot
            background_tasks.add_task(
                memory_integration_service.notify_chatbot_mood_change,
                user_id=current_user["user_id"],
                mood_entry=mood_entry.model_dump()
            )
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze emotion: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze emotion")


@router.post("/context", response_model=MoodContextResponse)
async def create_mood_context(
    context_request: MoodContextRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create mood context summary for memory service integration.
    
    Summarizes mood data over a specified time period for chatbot context.
    """
    try:
        context = await memory_integration_service.create_mood_context(
            db=db,
            user_id=current_user["user_id"],
            context_request=context_request
        )
        
        return context
        
    except Exception as e:
        logger.error(f"Failed to create mood context: {e}")
        raise HTTPException(status_code=500, detail="Failed to create mood context")


@router.get("/context", response_model=List[MoodContextResponse])
async def get_mood_contexts(
    session_id: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get mood contexts for the authenticated user.
    
    Optionally filter by session_id for specific conversation contexts.
    """
    try:
        contexts = await memory_integration_service.get_user_mood_contexts(
            db=db,
            user_id=current_user["user_id"],
            session_id=session_id,
            limit=min(limit, 50)  # Cap at 50
        )
        
        return contexts
        
    except Exception as e:
        logger.error(f"Failed to get mood contexts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve mood contexts")


