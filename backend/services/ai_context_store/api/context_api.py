"""
Context API endpoints
Provides REST API for user context operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging

import sys
import os

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
service_root = os.path.dirname(current_dir)
backend_root = os.path.dirname(os.path.dirname(service_root))

sys.path.insert(0, backend_root)
sys.path.insert(0, service_root)

from shared.auth import get_current_user
from shared.models import User
from models.context_models import (
    UserContext, ContextQuery, ContextUpdate, ContextType,
    IntelligenceInsight
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Global references to services (will be injected)
context_aggregator_service = None
intelligence_engine = None

def set_services(aggregator, engine):
    """Set service references"""
    global context_aggregator_service, intelligence_engine
    context_aggregator_service = aggregator
    intelligence_engine = engine

@router.get("/user/{user_id}", response_model=UserContext)
async def get_user_context(
    user_id: str,
    include_history: bool = Query(False, description="Include context history"),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive user context
    """
    try:
        # Check authorization (users can only access their own context)
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this user's context")
        
        if not context_aggregator_service:
            raise HTTPException(status_code=500, detail="Context aggregator service not available")
        
        user_context = await context_aggregator_service.get_user_context(user_id, include_history)
        
        if not user_context:
            raise HTTPException(status_code=404, detail="User context not found")
        
        return user_context
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting user context: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user context")

@router.post("/update")
async def update_user_context(
    context_update: ContextUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update user context with new data
    """
    try:
        # Check authorization
        if current_user.id != context_update.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this user's context")
        
        if not context_aggregator_service:
            raise HTTPException(status_code=500, detail="Context aggregator service not available")
        
        success = await context_aggregator_service.update_user_context(
            context_update.user_id,
            context_update.context_type,
            context_update.data
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update user context")
        
        return {"status": "success", "message": "User context updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating user context: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user context")

@router.get("/user/{user_id}/summary")
async def get_context_summary(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a summary of user context
    """
    try:
        # Check authorization
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this user's context")
        
        if not context_aggregator_service:
            raise HTTPException(status_code=500, detail="Context aggregator service not available")
        
        user_context = await context_aggregator_service.get_user_context(user_id)
        
        if not user_context:
            return {
                "user_id": user_id,
                "context_completeness": 0.0,
                "activity_score": 0.0,
                "last_activity": None,
                "active_areas": [],
                "summary": "No context data available"
            }
        
        # Calculate active areas
        active_areas = []
        if user_context.mood_context:
            active_areas.append("mood_tracking")
        if user_context.community_context:
            active_areas.append("community_engagement")
        if user_context.voice_context:
            active_areas.append("voice_interaction")
        if user_context.translation_context:
            active_areas.append("multilingual_support")
        if user_context.content_context:
            active_areas.append("content_consumption")
        if user_context.notification_context:
            active_areas.append("notification_engagement")
        
        return {
            "user_id": user_id,
            "context_completeness": user_context.context_completeness,
            "activity_score": user_context.activity_score,
            "last_activity": user_context.last_activity,
            "last_updated": user_context.last_updated,
            "active_areas": active_areas,
            "summary": f"User is active in {len(active_areas)} out of 6 available areas"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting context summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get context summary")

@router.get("/user/{user_id}/completeness")
async def get_context_completeness(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get context completeness breakdown for a user
    """
    try:
        # Check authorization
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this user's context")
        
        if not context_aggregator_service:
            raise HTTPException(status_code=500, detail="Context aggregator service not available")
        
        user_context = await context_aggregator_service.get_user_context(user_id)
        
        completeness_breakdown = {
            "mood_context": bool(user_context.mood_context) if user_context else False,
            "community_context": bool(user_context.community_context) if user_context else False,
            "voice_context": bool(user_context.voice_context) if user_context else False,
            "translation_context": bool(user_context.translation_context) if user_context else False,
            "content_context": bool(user_context.content_context) if user_context else False,
            "notification_context": bool(user_context.notification_context) if user_context else False
        }
        
        total_score = sum(completeness_breakdown.values()) / len(completeness_breakdown)
        
        return {
            "user_id": user_id,
            "overall_completeness": total_score,
            "breakdown": completeness_breakdown,
            "missing_areas": [
                area.replace("_context", "") for area, present in completeness_breakdown.items() 
                if not present
            ],
            "recommendations": [
                "Try voice interactions" if not completeness_breakdown["voice_context"] else None,
                "Join community discussions" if not completeness_breakdown["community_context"] else None,
                "Explore content recommendations" if not completeness_breakdown["content_context"] else None,
                "Track your mood" if not completeness_breakdown["mood_context"] else None,
                "Enable notifications" if not completeness_breakdown["notification_context"] else None,
                "Use translation features" if not completeness_breakdown["translation_context"] else None
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting context completeness: {e}")
        raise HTTPException(status_code=500, detail="Failed to get context completeness")

@router.get("/user/{user_id}/activity")
async def get_user_activity(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get user activity metrics
    """
    try:
        # Check authorization
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this user's activity")
        
        if not context_aggregator_service:
            raise HTTPException(status_code=500, detail="Context aggregator service not available")
        
        user_context = await context_aggregator_service.get_user_context(user_id)
        
        if not user_context:
            return {
                "user_id": user_id,
                "activity_score": 0.0,
                "last_activity": None,
                "recent_activities": []
            }
        
        # Calculate recent activities
        recent_activities = []
        now = datetime.now(timezone.utc)
        
        contexts_with_timestamps = [
            ("mood", user_context.mood_context),
            ("community", user_context.community_context),
            ("voice", user_context.voice_context),
            ("translation", user_context.translation_context),
            ("content", user_context.content_context),
            ("notification", user_context.notification_context)
        ]
        
        for area, ctx in contexts_with_timestamps:
            if ctx and hasattr(ctx, 'timestamp'):
                hours_ago = (now - ctx.timestamp).total_seconds() / 3600
                if hours_ago < 24:  # Last 24 hours
                    recent_activities.append({
                        "area": area,
                        "timestamp": ctx.timestamp,
                        "hours_ago": round(hours_ago, 1)
                    })
        
        # Sort by most recent
        recent_activities.sort(key=lambda x: x["hours_ago"])
        
        return {
            "user_id": user_id,
            "activity_score": user_context.activity_score,
            "last_activity": user_context.last_activity,
            "recent_activities": recent_activities[:10],  # Top 10 most recent
            "total_recent_activities": len(recent_activities)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting user activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user activity")

@router.post("/user/{user_id}/refresh")
async def refresh_user_context(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Force refresh of user context and regenerate insights
    """
    try:
        # Check authorization
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to refresh this user's context")
        
        if not context_aggregator_service or not intelligence_engine:
            raise HTTPException(status_code=500, detail="Services not available")
        
        # Get current context
        user_context = await context_aggregator_service.get_user_context(user_id)
        
        if user_context:
            # Update aggregated insights
            await context_aggregator_service._update_aggregated_insights(user_context)
            
            # Save updated context
            await context_aggregator_service._save_user_context(user_context)
            
            # Generate new insights
            insights = await intelligence_engine.generate_user_insights(user_id, user_context)
            
            return {
                "status": "success",
                "message": "User context refreshed successfully",
                "context_completeness": user_context.context_completeness,
                "activity_score": user_context.activity_score,
                "insights_generated": len(insights)
            }
        else:
            return {
                "status": "success",
                "message": "No existing context found, ready for new data",
                "context_completeness": 0.0,
                "activity_score": 0.0,
                "insights_generated": 0
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error refreshing user context: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh user context")
