"""API endpoints for mood operations."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.auth import verify_token, extract_user_id, get_current_user
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
        
        # Perform emotion analysis if description is provided
        if mood_data.description and mood_data.description.strip():
            try:
                analysis_result = await emotion_service.analyze_emotion(mood_data.description)
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