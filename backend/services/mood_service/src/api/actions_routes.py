"""
Action Orchestrator Integration API Endpoints
Standardized /api/v1/actions endpoint for cross-service orchestration
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.auth import get_current_user
from src.models.schemas import (
    MoodCreateRequest,
    MoodEntryResponse,
    EmotionAnalysisRequest,
    MoodAnalysisResult
)
from src.services import emotion_service, mood_data_service, memory_integration_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["actions"])


@router.post("/actions")
async def handle_orchestrator_action(
    action_request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Standardized actions endpoint for Action Orchestrator integration.
    
    Handles various mood-related actions based on action_type:
    - validate_mood_entry: Validate mood entry data
    - save_mood_entry: Create a new mood entry
    - analyze_emotion: Analyze emotion in text
    - get_mood_analytics: Get mood analytics data
    """
    try:
        action_type = action_request.get("action_type")
        parameters = action_request.get("parameters", {})
        user_id = action_request.get("user_id")
        
        if not action_type:
            raise HTTPException(status_code=400, detail="action_type is required")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        logger.info(f"Processing action: {action_type} for user: {user_id}")
        
        # Create a mock current_user for compatibility
        current_user = {"user_id": user_id}
        
        if action_type == "validate_mood_entry":
            return await _validate_mood_entry(parameters, current_user)
            
        elif action_type == "save_mood_entry":
            return await _save_mood_entry(parameters, current_user, background_tasks, db)
            
        elif action_type == "analyze_emotion":
            return await _analyze_emotion(parameters, current_user, background_tasks, db)
            
        elif action_type == "get_mood_analytics":
            return await _get_mood_analytics(parameters, current_user, db)
            
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported action_type: {action_type}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Action processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Action processing failed: {str(e)}")


async def _validate_mood_entry(parameters: Dict[str, Any], current_user: Dict[str, str]) -> Dict[str, Any]:
    """Validate mood entry parameters"""
    try:
        mood_score = parameters.get("mood_score")
        description = parameters.get("description", "")
        
        # Validate mood score
        if mood_score is None:
            return {
                "valid": False,
                "error": "mood_score is required"
            }
        
        if not isinstance(mood_score, (int, float)) or not (1 <= mood_score <= 10):
            return {
                "valid": False,
                "error": "mood_score must be a number between 1 and 10"
            }
        
        # Validate description length
        if description and len(description) > 1000:
            return {
                "valid": False,
                "error": "description must be less than 1000 characters"
            }
        
        return {
            "valid": True,
            "validated_parameters": {
                "mood_score": mood_score,
                "description": description
            }
        }
        
    except Exception as e:
        logger.error(f"Mood entry validation failed: {e}")
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}"
        }


async def _save_mood_entry(
    parameters: Dict[str, Any], 
    current_user: Dict[str, str],
    background_tasks: BackgroundTasks,
    db: Session
) -> Dict[str, Any]:
    """Save a new mood entry"""
    try:
        mood_score = parameters.get("mood_score")
        description = parameters.get("description", "")
        
        if not mood_score:
            raise HTTPException(status_code=400, detail="mood_score is required")
        
        # Create mood entry request
        mood_data = MoodCreateRequest(
            mood_score=mood_score,
            description=description
        )
        
        # Perform emotion analysis if description provided
        emotion_analysis = None
        if description and description.strip():
            try:
                analysis_result = await emotion_service.analyze_emotion(description)
                emotion_analysis = analysis_result.model_dump()
            except Exception as e:
                logger.warning(f"Emotion analysis failed: {e}")
        
        # Create mood entry
        mood_entry = await mood_data_service.create_mood_entry(
            db=db,
            user_id=current_user["user_id"],
            mood_data=mood_data,
            emotion_analysis=emotion_analysis
        )
        
        # Background task: notify chatbot
        background_tasks.add_task(
            memory_integration_service.notify_chatbot_mood_change,
            user_id=current_user["user_id"],
            mood_entry=mood_entry.model_dump()
        )
        
        return {
            "success": True,
            "mood_entry_id": mood_entry.id,
            "mood_score": mood_entry.mood_score,
            "created_at": mood_entry.created_at.isoformat(),
            "emotion_analysis": emotion_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save mood entry: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save mood entry: {str(e)}")


async def _analyze_emotion(
    parameters: Dict[str, Any],
    current_user: Dict[str, str],
    background_tasks: BackgroundTasks,
    db: Session
) -> Dict[str, Any]:
    """Analyze emotion in text"""
    try:
        text = parameters.get("text")
        if not text:
            raise HTTPException(status_code=400, detail="text is required")
        
        # Perform emotion analysis
        analysis_result = await emotion_service.analyze_emotion(text)
        
        return {
            "success": True,
            "analysis": analysis_result.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze emotion: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze emotion: {str(e)}")


async def _get_mood_analytics(
    parameters: Dict[str, Any],
    current_user: Dict[str, str],
    db: Session
) -> Dict[str, Any]:
    """Get mood analytics data"""
    try:
        # Get recent mood entries for analytics
        entries = await mood_data_service.get_user_mood_entries(
            db=db,
            user_id=current_user["user_id"],
            limit=30,
            offset=0
        )
        
        if not entries:
            return {
                "success": True,
                "analytics": {
                    "total_entries": 0,
                    "average_mood": None,
                    "mood_trend": "insufficient_data"
                }
            }
        
        # Calculate basic analytics
        mood_scores = [entry.mood_score for entry in entries]
        average_mood = sum(mood_scores) / len(mood_scores)
        
        # Simple trend calculation
        if len(mood_scores) >= 2:
            recent_avg = sum(mood_scores[:10]) / min(10, len(mood_scores))
            older_avg = sum(mood_scores[-10:]) / min(10, len(mood_scores))
            trend = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "success": True,
            "analytics": {
                "total_entries": len(entries),
                "average_mood": round(average_mood, 2),
                "mood_trend": trend,
                "latest_entry": {
                    "mood_score": entries[0].mood_score,
                    "created_at": entries[0].created_at.isoformat()
                } if entries else None
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get mood analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get mood analytics: {str(e)}")


