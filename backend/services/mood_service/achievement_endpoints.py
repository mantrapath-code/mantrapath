"""
E3 Achievement API endpoints for mood service integration
Simple achievement endpoints using existing mood service authentication
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

# Use existing mood service imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from shared.database import get_db
from shared.auth import get_current_user
from shared.models import User

# Import the achievements engine - fix the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
try:
    # Try to import the main achievements engine
    import achievements_engine
    from achievements_engine import AchievementsEngine
    print("✅ Main achievement engine imported successfully")
    ACHIEVEMENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import achievements_engine: {e}")
    # Fallback mock system - should only be used when main system is unavailable
    class AchievementsEngine:
        def __init__(self):
            pass
        def check_achievements(self, user_id: str, mood_data: dict):
            return []
        def get_user_achievements(self, user_id: str):
            return []
    achievements_engine = None
    ACHIEVEMENTS_AVAILABLE = False

# Create achievement router
achievement_router = APIRouter(prefix="/api/v1/achievements", tags=["achievements"])

@achievement_router.get("/")
async def get_user_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    E3 Unified Achievement System - Get all user achievements
    Consolidates server-side achievement logic with celebration integration
    """
    
    try:
        # Use the unified achievements engine
        achievement_data = await achievements_engine.get_user_achievements(
            str(current_user.id), db
        )
        
        return {
            "success": True,
            "data": achievement_data,
            "meta": {
                "total_achievements": len(achievement_data["achievements"]),
                "engine_version": "e3_unified",
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch achievements: {str(e)}"
        )

@achievement_router.get("/summary")
async def get_achievement_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get achievement summary for dashboard widgets"""
    
    try:
        # Get full achievement data
        achievement_data = await achievements_engine.get_user_achievements(
            str(current_user.id), db
        )
        
        # Return just the summary portion
        return {
            "success": True,
            "data": achievement_data["summary"],
            "celebration_stats": achievement_data["celebration_stats"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch achievement summary: {str(e)}"
        )

@achievement_router.post("/check")
async def trigger_achievement_check(
    trigger_event: str = "manual_check",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Trigger achievement progress check after user actions
    Detects newly unlocked achievements and creates celebrations
    """
    
    try:
        # Trigger achievement check
        new_achievements = await achievements_engine.trigger_achievement_check(
            str(current_user.id), trigger_event, db
        )
        
        return {
            "success": True,
            "data": {
                "new_achievements": new_achievements,
                "check_completed": True,
                "trigger_event": trigger_event
            },
            "meta": {
                "new_count": len(new_achievements),
                "check_timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check achievements: {str(e)}"
        )

@achievement_router.get("/{achievement_id}")
async def get_specific_achievement(
    achievement_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed information for a specific achievement"""
    
    try:
        # Get all user achievements
        all_achievements = await achievements_engine.get_user_achievements(
            str(current_user.id), db
        )
        
        # Find specific achievement
        achievement = all_achievements["achievements"].get(achievement_id)
        
        if not achievement:
            raise HTTPException(
                status_code=404,
                detail=f"Achievement {achievement_id} not found"
            )
        
        # Get achievement definition for additional context
        achievement_def = achievements_engine.achievement_definitions.get(achievement_id)
        
        # Enhanced achievement data
        enhanced_achievement = {
            **achievement,
            "progress_percentage": (achievement["progress"] / achievement["max_progress"]) * 100,
            "completion_status": "unlocked" if achievement["is_unlocked"] else "in_progress"
        }
        
        if achievement_def:
            enhanced_achievement["definition"] = {
                "criteria_function": achievement_def.criteria_function,
                "celebration_type": achievement_def.celebration_type,
            }
        
        return {
            "success": True,
            "data": enhanced_achievement
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch achievement: {str(e)}"
        )
