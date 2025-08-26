"""
Patterns API - Handles mood pattern analysis and retrieval
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import logging

from shared.database import get_db
from shared.auth import get_current_user
from shared.models import User
from shared.models import MoodPattern, UserInteraction
from services.memory_engine import MemoryEngine

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for API
class PatternResponse(BaseModel):
    id: int
    user_id: str
    pattern_type: str
    pattern_data: Dict[str, Any]
    confidence_score: float
    frequency: Optional[str]
    intensity: Optional[float]
    stability: Optional[float]
    start_date: datetime
    end_date: datetime
    created_at: datetime
    updated_at: Optional[datetime]
    cultural_context: Optional[Dict[str, Any]]
    environmental_factors: Optional[Dict[str, Any]]
    triggers: Optional[Dict[str, Any]]
    is_active: bool

    class Config:
        from_attributes = True

class PatternAnalysisRequest(BaseModel):
    pattern_types: Optional[List[str]] = Field(default=["daily", "weekly", "trend"], description="Types of patterns to analyze")
    force_refresh: bool = Field(default=False, description="Force refresh of pattern analysis")

class PatternSummary(BaseModel):
    total_patterns: int
    active_patterns: int
    pattern_types: Dict[str, int]
    average_confidence: float
    most_stable_pattern: Optional[PatternResponse]
    recent_patterns: List[PatternResponse]

# Dependency to get Memory Engine
async def get_memory_engine() -> MemoryEngine:
    """Get Memory Engine instance"""
    from main import memory_engine
    if not memory_engine:
        raise HTTPException(status_code=503, detail="Memory Engine not available")
    return memory_engine

@router.post("/patterns/analyze", response_model=List[PatternResponse])
async def analyze_patterns(
    request: PatternAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """
    Trigger pattern analysis for the current user
    """
    try:
        # Clear cache if force refresh requested
        if request.force_refresh:
            from shared.redis_client import redis_client
            cache_key = f"mood_patterns:{current_user.id}"
            await redis_client.delete(cache_key)
        
        # Analyze patterns
        patterns = await memory_engine.analyze_mood_patterns(current_user.id)
        
        # Filter by requested pattern types if specified
        if request.pattern_types:
            patterns = [p for p in patterns if p.pattern_type in request.pattern_types]
        
        logger.info(f"🔍 Analyzed {len(patterns)} patterns for user {current_user.id}")
        
        return [PatternResponse.from_orm(pattern) for pattern in patterns]
        
    except Exception as e:
        logger.error(f"❌ Failed to analyze patterns: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze patterns: {str(e)}")

@router.get("/patterns", response_model=List[PatternResponse])
async def get_patterns(
    pattern_type: Optional[str] = Query(None, description="Filter by pattern type"),
    active_only: bool = Query(True, description="Only return active patterns"),
    min_confidence: float = Query(0.0, description="Minimum confidence score", ge=0.0, le=1.0),
    limit: int = Query(100, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's mood patterns with filtering options
    """
    try:
        query = db.query(MoodPattern).filter(
            MoodPattern.user_id == current_user.id,
            MoodPattern.is_deleted == False
        )
        
        if pattern_type:
            query = query.filter(MoodPattern.pattern_type == pattern_type)
        
        if active_only:
            query = query.filter(MoodPattern.is_active == True)
        
        if min_confidence > 0:
            query = query.filter(MoodPattern.confidence_score >= min_confidence)
        
        patterns = query.order_by(MoodPattern.created_at.desc())\
                       .offset(offset)\
                       .limit(limit)\
                       .all()
        
        logger.info(f"📊 Retrieved {len(patterns)} patterns for user {current_user.id}")
        
        return [PatternResponse.from_orm(pattern) for pattern in patterns]
        
    except Exception as e:
        logger.error(f"❌ Failed to get patterns: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get patterns: {str(e)}")

@router.get("/patterns/{pattern_id}", response_model=PatternResponse)
async def get_pattern(
    pattern_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific pattern by ID
    """
    try:
        pattern = db.query(MoodPattern).filter(
            MoodPattern.id == pattern_id,
            MoodPattern.user_id == current_user.id,
            MoodPattern.is_deleted == False
        ).first()
        
        if not pattern:
            raise HTTPException(status_code=404, detail="Pattern not found")
        
        logger.info(f"📊 Retrieved pattern {pattern_id} for user {current_user.id}")
        
        return PatternResponse.from_orm(pattern)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get pattern: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pattern: {str(e)}")

@router.get("/patterns/summary", response_model=PatternSummary)
async def get_patterns_summary(
    days: int = Query(30, description="Number of days to analyze", le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a summary of user's patterns
    """
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Get patterns for the period
        patterns = db.query(MoodPattern).filter(
            MoodPattern.user_id == current_user.id,
            MoodPattern.created_at >= start_date,
            MoodPattern.is_deleted == False
        ).all()
        
        # Calculate summary statistics
        total_patterns = len(patterns)
        active_patterns = len([p for p in patterns if p.is_active])
        
        # Group by type
        pattern_types = {}
        for pattern in patterns:
            pattern_type = pattern.pattern_type
            pattern_types[pattern_type] = pattern_types.get(pattern_type, 0) + 1
        
        # Calculate average confidence
        confidences = [p.confidence_score for p in patterns if p.confidence_score is not None]
        average_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Find most stable pattern
        most_stable_pattern = None
        if patterns:
            stable_patterns = [p for p in patterns if p.stability is not None]
            if stable_patterns:
                most_stable_pattern = max(stable_patterns, key=lambda x: x.stability)
        
        # Get recent patterns (last 10)
        recent_patterns = db.query(MoodPattern).filter(
            MoodPattern.user_id == current_user.id,
            MoodPattern.is_deleted == False
        ).order_by(MoodPattern.created_at.desc()).limit(10).all()
        
        summary = PatternSummary(
            total_patterns=total_patterns,
            active_patterns=active_patterns,
            pattern_types=pattern_types,
            average_confidence=round(average_confidence, 3),
            most_stable_pattern=PatternResponse.from_orm(most_stable_pattern) if most_stable_pattern else None,
            recent_patterns=[PatternResponse.from_orm(p) for p in recent_patterns]
        )
        
        logger.info(f"📊 Generated pattern summary for user {current_user.id}")
        
        return summary
        
    except Exception as e:
        logger.error(f"❌ Failed to get pattern summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pattern summary: {str(e)}")

@router.get("/patterns/types/{pattern_type}/details")
async def get_pattern_type_details(
    pattern_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed analysis for a specific pattern type
    """
    try:
        patterns = db.query(MoodPattern).filter(
            MoodPattern.user_id == current_user.id,
            MoodPattern.pattern_type == pattern_type,
            MoodPattern.is_active == True,
            MoodPattern.is_deleted == False
        ).order_by(MoodPattern.confidence_score.desc()).all()
        
        if not patterns:
            raise HTTPException(status_code=404, detail=f"No active patterns found for type: {pattern_type}")
        
        # Analyze patterns of this type
        confidences = [p.confidence_score for p in patterns]
        intensities = [p.intensity for p in patterns if p.intensity is not None]
        stabilities = [p.stability for p in patterns if p.stability is not None]
        
        details = {
            "pattern_type": pattern_type,
            "total_patterns": len(patterns),
            "confidence_stats": {
                "min": min(confidences),
                "max": max(confidences),
                "average": sum(confidences) / len(confidences),
                "patterns_above_threshold": len([c for c in confidences if c > 0.7])
            },
            "intensity_stats": {
                "min": min(intensities) if intensities else None,
                "max": max(intensities) if intensities else None,
                "average": sum(intensities) / len(intensities) if intensities else None
            } if intensities else None,
            "stability_stats": {
                "min": min(stabilities) if stabilities else None,
                "max": max(stabilities) if stabilities else None,
                "average": sum(stabilities) / len(stabilities) if stabilities else None
            } if stabilities else None,
            "patterns": [PatternResponse.from_orm(p) for p in patterns[:5]]  # Top 5 patterns
        }
        
        # Add type-specific insights
        if pattern_type == "daily":
            # Analyze daily patterns
            peak_hours = []
            low_hours = []
            for pattern in patterns:
                pattern_data = pattern.pattern_data
                if isinstance(pattern_data, dict):
                    peak_hours.extend(pattern_data.get("peak_hours", []))
                    low_hours.extend(pattern_data.get("low_hours", []))
            
            details["daily_insights"] = {
                "common_peak_hours": list(set(peak_hours)),
                "common_low_hours": list(set(low_hours)),
                "most_common_peak": max(set(peak_hours), key=peak_hours.count) if peak_hours else None,
                "most_common_low": max(set(low_hours), key=low_hours.count) if low_hours else None
            }
        
        elif pattern_type == "weekly":
            # Analyze weekly patterns
            best_days = []
            challenging_days = []
            for pattern in patterns:
                pattern_data = pattern.pattern_data
                if isinstance(pattern_data, dict):
                    best_days.extend(pattern_data.get("best_days", []))
                    challenging_days.extend(pattern_data.get("challenging_days", []))
            
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            details["weekly_insights"] = {
                "best_days": [day_names[day] for day in set(best_days) if 0 <= day < 7],
                "challenging_days": [day_names[day] for day in set(challenging_days) if 0 <= day < 7],
                "most_common_best_day": day_names[max(set(best_days), key=best_days.count)] if best_days and max(best_days) < 7 else None,
                "most_common_challenging_day": day_names[max(set(challenging_days), key=challenging_days.count)] if challenging_days and max(challenging_days) < 7 else None
            }
        
        elif pattern_type == "trend":
            # Analyze trend patterns
            trends = []
            for pattern in patterns:
                pattern_data = pattern.pattern_data
                if isinstance(pattern_data, dict):
                    trends.append(pattern_data.get("trend_direction"))
            
            trend_counts = {}
            for trend in trends:
                if trend:
                    trend_counts[trend] = trend_counts.get(trend, 0) + 1
            
            details["trend_insights"] = {
                "trend_distribution": trend_counts,
                "dominant_trend": max(trend_counts.items(), key=lambda x: x[1])[0] if trend_counts else None,
                "improving_trends": trend_counts.get("improving", 0),
                "declining_trends": trend_counts.get("declining", 0),
                "stable_trends": trend_counts.get("stable", 0)
            }
        
        logger.info(f"📊 Generated {pattern_type} pattern details for user {current_user.id}")
        
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get pattern type details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pattern type details: {str(e)}")

@router.put("/patterns/{pattern_id}/activate")
async def activate_pattern(
    pattern_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Activate a pattern
    """
    try:
        pattern = db.query(MoodPattern).filter(
            MoodPattern.id == pattern_id,
            MoodPattern.user_id == current_user.id,
            MoodPattern.is_deleted == False
        ).first()
        
        if not pattern:
            raise HTTPException(status_code=404, detail="Pattern not found")
        
        pattern.is_active = True
        pattern.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        logger.info(f"✅ Activated pattern {pattern_id} for user {current_user.id}")
        
        return {"message": "Pattern activated successfully", "id": pattern_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to activate pattern: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to activate pattern: {str(e)}")

@router.put("/patterns/{pattern_id}/deactivate")
async def deactivate_pattern(
    pattern_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate a pattern
    """
    try:
        pattern = db.query(MoodPattern).filter(
            MoodPattern.id == pattern_id,
            MoodPattern.user_id == current_user.id,
            MoodPattern.is_deleted == False
        ).first()
        
        if not pattern:
            raise HTTPException(status_code=404, detail="Pattern not found")
        
        pattern.is_active = False
        pattern.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        logger.info(f"⏸️ Deactivated pattern {pattern_id} for user {current_user.id}")
        
        return {"message": "Pattern deactivated successfully", "id": pattern_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to deactivate pattern: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to deactivate pattern: {str(e)}")

@router.delete("/patterns/{pattern_id}")
async def delete_pattern(
    pattern_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a pattern
    """
    try:
        pattern = db.query(MoodPattern).filter(
            MoodPattern.id == pattern_id,
            MoodPattern.user_id == current_user.id,
            MoodPattern.is_deleted == False
        ).first()
        
        if not pattern:
            raise HTTPException(status_code=404, detail="Pattern not found")
        
        # Soft delete
        pattern.is_deleted = True
        pattern.is_active = False
        pattern.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        logger.info(f"🗑️ Deleted pattern {pattern_id} for user {current_user.id}")
        
        return {"message": "Pattern deleted successfully", "id": pattern_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete pattern: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete pattern: {str(e)}")

@router.get("/patterns/recommendations")
async def get_pattern_recommendations(
    current_user: User = Depends(get_current_user),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """
    Get personalized recommendations based on patterns
    """
    try:
        # Get user's patterns
        patterns = await memory_engine.analyze_mood_patterns(current_user.id)
        
        recommendations = []
        
        for pattern in patterns:
            if pattern.confidence_score < 0.7:
                continue  # Only recommend based on confident patterns
            
            if pattern.pattern_type == "daily":
                pattern_data = pattern.pattern_data
                if isinstance(pattern_data, dict):
                    peak_hours = pattern_data.get("peak_hours", [])
                    low_hours = pattern_data.get("low_hours", [])
                    
                    if peak_hours:
                        recommendations.append({
                            "type": "schedule_optimization",
                            "priority": "medium",
                            "title": "Optimize Your Peak Hours",
                            "description": f"You feel best around hours {peak_hours}. Consider scheduling important tasks during these times.",
                            "pattern_id": pattern.id,
                            "confidence": pattern.confidence_score
                        })
                    
                    if low_hours:
                        recommendations.append({
                            "type": "self_care",
                            "priority": "high",
                            "title": "Self-Care During Low Hours",
                            "description": f"You tend to feel lower around hours {low_hours}. Plan self-care activities during these times.",
                            "pattern_id": pattern.id,
                            "confidence": pattern.confidence_score
                        })
            
            elif pattern.pattern_type == "weekly":
                pattern_data = pattern.pattern_data
                if isinstance(pattern_data, dict):
                    challenging_days = pattern_data.get("challenging_days", [])
                    
                    if challenging_days:
                        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                        challenging_day_names = [day_names[day] for day in challenging_days if 0 <= day < 7]
                        
                        recommendations.append({
                            "type": "weekly_planning",
                            "priority": "medium",
                            "title": "Plan for Challenging Days",
                            "description": f"You tend to struggle on {', '.join(challenging_day_names)}. Consider planning lighter schedules or extra support.",
                            "pattern_id": pattern.id,
                            "confidence": pattern.confidence_score
                        })
            
            elif pattern.pattern_type == "trend":
                pattern_data = pattern.pattern_data
                if isinstance(pattern_data, dict):
                    trend_direction = pattern_data.get("trend_direction")
                    
                    if trend_direction == "declining":
                        recommendations.append({
                            "type": "intervention",
                            "priority": "high",
                            "title": "Mood Support Needed",
                            "description": "Your mood has been declining. Consider reaching out for support or trying new wellness activities.",
                            "pattern_id": pattern.id,
                            "confidence": pattern.confidence_score
                        })
                    elif trend_direction == "improving":
                        recommendations.append({
                            "type": "positive_reinforcement",
                            "priority": "low",
                            "title": "Keep Up the Great Work!",
                            "description": "Your mood is improving! Continue with the activities that are helping you feel better.",
                            "pattern_id": pattern.id,
                            "confidence": pattern.confidence_score
                        })
        
        # Sort by priority and confidence
        priority_order = {"high": 3, "medium": 2, "low": 1}
        recommendations.sort(key=lambda x: (priority_order.get(x["priority"], 0), x["confidence"]), reverse=True)
        
        logger.info(f"💡 Generated {len(recommendations)} pattern recommendations for user {current_user.id}")
        
        return {
            "total_recommendations": len(recommendations),
            "recommendations": recommendations[:10],  # Top 10 recommendations
            "based_on_patterns": len(patterns)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get pattern recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pattern recommendations: {str(e)}")
