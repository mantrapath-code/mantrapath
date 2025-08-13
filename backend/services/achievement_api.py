"""
E3 Achievement & Engagement Cohesion API Endpoints
Unified achievement system endpoints that consolidate server-side achievement logic
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import dependencies
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../shared'))

from shared.database import get_db
from shared.models import User
from services.auth_service import get_current_user
from services.achievements_engine import achievements_engine
from shared.achievement_models import UserAchievementProgress, UserAchievementEvent

# Create router
router = APIRouter(prefix="/api/v1/achievements", tags=["achievements"])

@router.get("/")
async def get_user_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive user achievement data
    
    Consolidates:
    - Achievement progress from all sources
    - Celebration statistics  
    - Progress tracking metadata
    - Summary analytics
    
    Returns unified achievement response compatible with existing frontend
    """
    
    try:
        # Use the unified achievements engine
        achievement_data = await achievements_engine.get_user_achievements(
            current_user.id, db
        )
        
        # Track API access event
        await _log_achievement_event(
            user_id=current_user.id,
            achievement_id="system",
            event_type="api_access",
            event_data={"endpoint": "get_user_achievements"},
            trigger_source="api_call",
            db=db
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

@router.get("/{achievement_id}")
async def get_specific_achievement(
    achievement_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed information for a specific achievement"""
    
    try:
        # Get all user achievements
        all_achievements = await achievements_engine.get_user_achievements(
            current_user.id, db
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
            "definition": {
                "criteria_function": achievement_def.criteria_function if achievement_def else None,
                "celebration_type": achievement_def.celebration_type if achievement_def else None,
            },
            "progress_percentage": (achievement["progress"] / achievement["max_progress"]) * 100,
            "completion_status": "unlocked" if achievement["is_unlocked"] else "in_progress"
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

@router.post("/check")
async def trigger_achievement_check(
    background_tasks: BackgroundTasks,
    trigger_event: str = "manual_check",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Manually trigger achievement progress check
    
    Used after user actions (mood entry, journal entry, etc.)
    to detect newly unlocked achievements
    """
    
    try:
        # Trigger achievement check
        new_achievements = await achievements_engine.trigger_achievement_check(
            current_user.id, trigger_event, db
        )
        
        # Log the check event
        await _log_achievement_event(
            user_id=current_user.id,
            achievement_id="system",
            event_type="achievement_check",
            event_data={
                "trigger_event": trigger_event,
                "new_achievements_count": len(new_achievements)
            },
            trigger_source=trigger_event,
            db=db
        )
        
        # If new achievements were unlocked, schedule celebration processing
        if new_achievements:
            background_tasks.add_task(
                _process_new_achievements,
                current_user.id,
                new_achievements,
                db
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

@router.get("/stats/summary")
async def get_achievement_summary_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get summary achievement statistics
    Optimized endpoint for dashboard widgets
    """
    
    try:
        # Get full achievement data
        achievement_data = await achievements_engine.get_user_achievements(
            current_user.id, db
        )
        
        # Extract summary statistics
        summary = achievement_data["summary"]
        celebration_stats = achievement_data["celebration_stats"]
        
        # Calculate additional metrics
        progress_distribution = {}
        for achievement in achievement_data["achievements"].values():
            progress_percent = int((achievement["progress"] / achievement["max_progress"]) * 100)
            range_key = f"{(progress_percent // 25) * 25}-{min(100, (progress_percent // 25 + 1) * 25 - 1)}%"
            progress_distribution[range_key] = progress_distribution.get(range_key, 0) + 1
        
        return {
            "success": True,
            "data": {
                "quick_stats": {
                    "total_achievements": summary["total_achievements"],
                    "unlocked_count": summary["unlocked_count"],
                    "average_progress": summary["average_progress"],
                    "recent_unlocks_count": len(summary["recent_unlocks"])
                },
                "level_distribution": summary["level_distribution"],
                "progress_distribution": progress_distribution,
                "celebration_summary": {
                    "total_celebrations": celebration_stats["total_celebrations"],
                    "by_level": celebration_stats["by_level"]
                },
                "engagement_metrics": {
                    "completion_rate": round((summary["unlocked_count"] / summary["total_achievements"]) * 100, 1),
                    "active_progress": summary["locked_count"],
                    "momentum_score": min(100, len(summary["recent_unlocks"]) * 20)  # Recent activity
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch achievement summary: {str(e)}"
        )

@router.get("/categories/{category}")
async def get_achievements_by_category(
    category: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get achievements filtered by category"""
    
    try:
        # Get all achievements
        all_achievements = await achievements_engine.get_user_achievements(
            current_user.id, db
        )
        
        # Filter by category
        category_achievements = {
            k: v for k, v in all_achievements["achievements"].items()
            if v["category"] == category
        }
        
        if not category_achievements:
            return {
                "success": True,
                "data": {
                    "achievements": {},
                    "category": category,
                    "message": f"No achievements found in category: {category}"
                }
            }
        
        # Calculate category statistics
        category_stats = {
            "total_in_category": len(category_achievements),
            "unlocked_in_category": len([a for a in category_achievements.values() if a["is_unlocked"]]),
            "average_progress_in_category": round(
                sum(a["progress"] / a["max_progress"] for a in category_achievements.values()) 
                / len(category_achievements) * 100, 1
            ) if category_achievements else 0
        }
        
        return {
            "success": True,
            "data": {
                "achievements": category_achievements,
                "category": category,
                "category_stats": category_stats
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch category achievements: {str(e)}"
        )

@router.get("/events/history")
async def get_achievement_event_history(
    limit: int = 50,
    event_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's achievement event history for analytics"""
    
    try:
        # Query achievement events
        query = db.query(UserAchievementEvent).filter(
            UserAchievementEvent.user_id == current_user.id
        )
        
        if event_type:
            query = query.filter(UserAchievementEvent.event_type == event_type)
            
        events = query.order_by(
            UserAchievementEvent.created_at.desc()
        ).limit(limit).all()
        
        # Format events
        formatted_events = []
        for event in events:
            formatted_events.append({
                "id": event.id,
                "achievement_id": event.achievement_id,
                "event_type": event.event_type,
                "event_data": event.event_data,
                "trigger_source": event.trigger_source,
                "progress_change": {
                    "before": event.progress_before,
                    "after": event.progress_after,
                    "unlock_occurred": event.was_unlocked_after and not event.was_unlocked_before
                },
                "timestamp": event.created_at.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "events": formatted_events,
                "total_returned": len(formatted_events),
                "filters": {
                    "event_type": event_type,
                    "limit": limit
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch achievement history: {str(e)}"
        )

# === BACKGROUND TASK FUNCTIONS ===

async def _process_new_achievements(user_id: str, new_achievements: List[Dict[str, Any]], db: Session):
    """Background task to process newly unlocked achievements"""
    
    for achievement in new_achievements:
        await _log_achievement_event(
            user_id=user_id,
            achievement_id=achievement["id"],
            event_type="unlock",
            event_data={
                "title": achievement["title"],
                "level": achievement["level"],
                "celebration_id": achievement.get("celebration_id")
            },
            trigger_source="achievement_unlock",
            progress_after=1,  # Unlocked
            was_unlocked_after=True,
            db=db
        )

async def _log_achievement_event(
    user_id: str,
    achievement_id: str,
    event_type: str,
    event_data: Dict[str, Any],
    trigger_source: str,
    progress_before: int = 0,
    progress_after: int = 0,
    was_unlocked_before: bool = False,
    was_unlocked_after: bool = False,
    db: Session = None
) -> None:
    """Log achievement event for analytics"""
    
    if not db:
        return
        
    try:
        event = UserAchievementEvent(
            user_id=user_id,
            achievement_id=achievement_id,
            event_type=event_type,
            event_data=event_data,
            trigger_source=trigger_source,
            progress_before=progress_before,
            progress_after=progress_after,
            was_unlocked_before=was_unlocked_before,
            was_unlocked_after=was_unlocked_after
        )
        
        db.add(event)
        db.commit()
        
    except Exception as e:
        # Log error but don't break the main flow
        print(f"Failed to log achievement event: {e}")
        db.rollback()

# Export router
achievement_router = router
