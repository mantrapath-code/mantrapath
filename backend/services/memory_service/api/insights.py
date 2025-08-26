"""
Insights API - Handles behavioral insights generation and retrieval
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
from shared.models import BehavioralInsight, UserInteraction, MoodPattern
from services.memory_engine import MemoryEngine

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for API
class InsightResponse(BaseModel):
    id: int
    user_id: str
    insight_type: str
    insight_data: Dict[str, Any]
    accuracy_score: float
    relevance_score: float
    urgency_level: str
    priority: int
    title: str
    description: Optional[str]
    recommendation: Optional[str]
    action_items: Optional[Dict[str, Any]]
    generated_at: datetime
    expires_at: Optional[datetime]
    delivered_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    cultural_context: Optional[Dict[str, Any]]
    status: str
    is_active: bool

    class Config:
        from_attributes = True

class InsightGenerationRequest(BaseModel):
    force_refresh: bool = Field(default=False, description="Force refresh of insights")
    insight_types: Optional[List[str]] = Field(default=None, description="Specific insight types to generate")
    priority_filter: Optional[str] = Field(default=None, description="Filter by urgency level")

class InsightFeedback(BaseModel):
    helpful: bool = Field(..., description="Was this insight helpful?")
    rating: int = Field(..., description="Rating from 1-5", ge=1, le=5)
    comments: Optional[str] = Field(None, description="Additional comments")

class InsightSummary(BaseModel):
    total_insights: int
    active_insights: int
    by_type: Dict[str, int]
    by_urgency: Dict[str, int]
    recent_insights: List[InsightResponse]
    pending_acknowledgments: int

# Dependency to get Memory Engine
async def get_memory_engine() -> MemoryEngine:
    """Get Memory Engine instance"""
    from main import memory_engine
    if not memory_engine:
        raise HTTPException(status_code=503, detail="Memory Engine not available")
    return memory_engine

@router.post("/insights/generate", response_model=List[InsightResponse])
async def generate_insights(
    request: InsightGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """
    Generate behavioral insights for the current user
    """
    try:
        # Clear cache if force refresh requested
        if request.force_refresh:
            from shared.redis_client import redis_client
            cache_keys = [
                f"insights:{current_user.id}:*",
                f"mood_patterns:{current_user.id}",
                f"cross_platform:{current_user.id}"
            ]
            for pattern in cache_keys:
                keys = await redis_client.keys(pattern)
                if keys:
                    await redis_client.delete(*keys)
        
        # Generate insights
        insights = await memory_engine.generate_behavioral_insights(current_user.id)
        
        # Filter by requested types if specified
        if request.insight_types:
            insights = [i for i in insights if i.insight_type in request.insight_types]
        
        # Filter by priority if specified
        if request.priority_filter:
            insights = [i for i in insights if i.urgency_level == request.priority_filter]
        
        logger.info(f"🔍 Generated {len(insights)} insights for user {current_user.id}")
        
        return [InsightResponse.model_validate(insight) for insight in insights]
        
    except Exception as e:
        logger.error(f"❌ Failed to generate insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

@router.get("/insights", response_model=List[InsightResponse])
async def get_insights(
    insight_type: Optional[str] = Query(None, description="Filter by insight type"),
    urgency_level: Optional[str] = Query(None, description="Filter by urgency level"),
    status: Optional[str] = Query(None, description="Filter by status"),
    active_only: bool = Query(True, description="Only return active insights"),
    limit: int = Query(100, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's behavioral insights with filtering options
    """
    try:
        query = db.query(BehavioralInsight).filter(
            BehavioralInsight.user_id == current_user.id,
            BehavioralInsight.is_deleted == False
        )
        
        if insight_type:
            query = query.filter(BehavioralInsight.insight_type == insight_type)
        
        if urgency_level:
            query = query.filter(BehavioralInsight.urgency_level == urgency_level)
        
        if status:
            query = query.filter(BehavioralInsight.status == status)
        
        if active_only:
            query = query.filter(BehavioralInsight.is_active == True)
        
        # Filter out expired insights
        current_time = datetime.now(timezone.utc)
        query = query.filter(
            (BehavioralInsight.expires_at.is_(None)) | 
            (BehavioralInsight.expires_at > current_time)
        )
        
        insights = query.order_by(
            BehavioralInsight.priority.desc(),
            BehavioralInsight.generated_at.desc()
        ).offset(offset).limit(limit).all()
        
        logger.info(f"📊 Retrieved {len(insights)} insights for user {current_user.id}")
        
        return [InsightResponse.model_validate(insight) for insight in insights]
        
    except Exception as e:
        logger.error(f"❌ Failed to get insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@router.get("/insights/{insight_id}", response_model=InsightResponse)
async def get_insight(
    insight_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific insight by ID
    """
    try:
        insight = db.query(BehavioralInsight).filter(
            BehavioralInsight.id == insight_id,
            BehavioralInsight.user_id == current_user.id,
            BehavioralInsight.is_deleted == False
        ).first()
        
        if not insight:
            raise HTTPException(status_code=404, detail="Insight not found")
        
        logger.info(f"📊 Retrieved insight {insight_id} for user {current_user.id}")
        
        return InsightResponse.model_validate(insight)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get insight: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get insight: {str(e)}")

@router.put("/insights/{insight_id}/acknowledge")
async def acknowledge_insight(
    insight_id: int,
    feedback: Optional[InsightFeedback] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Acknowledge that user has seen an insight
    """
    try:
        insight = db.query(BehavioralInsight).filter(
            BehavioralInsight.id == insight_id,
            BehavioralInsight.user_id == current_user.id,
            BehavioralInsight.is_deleted == False
        ).first()
        
        if not insight:
            raise HTTPException(status_code=404, detail="Insight not found")
        
        # Update acknowledgment
        insight.acknowledged_at = datetime.now(timezone.utc)
        insight.status = "acknowledged"
        
        # Add feedback if provided
        if feedback:
            feedback_data = {
                "helpful": feedback.helpful,
                "rating": feedback.rating,
                "comments": feedback.comments,
                "acknowledged_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Update user feedback
            current_feedback = insight.user_feedback or {}
            current_feedback.update(feedback_data)
            insight.user_feedback = current_feedback
            
            # Calculate effectiveness score based on rating
            insight.effectiveness_score = feedback.rating / 5.0
        
        db.commit()
        
        logger.info(f"✅ Acknowledged insight {insight_id} for user {current_user.id}")
        
        return {"message": "Insight acknowledged successfully", "id": insight_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to acknowledge insight: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge insight: {str(e)}")

@router.get("/insights/summary", response_model=InsightSummary)
async def get_insights_summary(
    days: int = Query(30, description="Number of days to analyze", le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a summary of user's insights
    """
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Get insights for the period
        insights = db.query(BehavioralInsight).filter(
            BehavioralInsight.user_id == current_user.id,
            BehavioralInsight.generated_at >= start_date,
            BehavioralInsight.is_deleted == False
        ).all()
        
        # Calculate summary statistics
        total_insights = len(insights)
        active_insights = len([i for i in insights if i.is_active])
        
        # Group by type
        by_type = {}
        for insight in insights:
            insight_type = insight.insight_type
            by_type[insight_type] = by_type.get(insight_type, 0) + 1
        
        # Group by urgency
        by_urgency = {}
        for insight in insights:
            urgency = insight.urgency_level
            by_urgency[urgency] = by_urgency.get(urgency, 0) + 1
        
        # Count pending acknowledgments
        pending_acknowledgments = len([
            i for i in insights 
            if i.acknowledged_at is None and i.is_active
        ])
        
        # Get recent insights (last 10)
        recent_insights = db.query(BehavioralInsight).filter(
            BehavioralInsight.user_id == current_user.id,
            BehavioralInsight.is_deleted == False
        ).order_by(BehavioralInsight.generated_at.desc()).limit(10).all()
        
        summary = InsightSummary(
            total_insights=total_insights,
            active_insights=active_insights,
            by_type=by_type,
            by_urgency=by_urgency,
            recent_insights=[InsightResponse.model_validate(i) for i in recent_insights],
            pending_acknowledgments=pending_acknowledgments
        )
        
        logger.info(f"📊 Generated insights summary for user {current_user.id}")
        
        return summary
        
    except Exception as e:
        logger.error(f"❌ Failed to get insights summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights summary: {str(e)}")

@router.get("/insights/cross-platform")
async def get_cross_platform_insights(
    current_user: User = Depends(get_current_user),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """
    Get cross-platform insights and aggregation data
    """
    try:
        # Get cross-platform summary
        summary = await memory_engine.get_cross_platform_summary(current_user.id)
        
        # Generate insights based on cross-platform data
        insights = []
        
        # Service usage insights
        if summary.get("service_breakdown"):
            total_interactions = summary.get("total_interactions", 0)
            service_breakdown = summary.get("service_breakdown", {})
            
            # Find dominant service
            if service_breakdown:
                dominant_service = max(service_breakdown.items(), key=lambda x: x[1]["interaction_count"])
                service_name, service_data = dominant_service
                usage_percentage = service_data["interaction_count"] / total_interactions if total_interactions > 0 else 0
                
                if usage_percentage > 0.6:  # More than 60% usage
                    insights.append({
                        "type": "service_usage",
                        "title": f"Heavy {service_name.replace('_', ' ').title()} Usage",
                        "description": f"You've used {service_name.replace('_', ' ')} for {usage_percentage:.1%} of your interactions.",
                        "recommendation": "Consider exploring other features to enhance your wellness journey.",
                        "priority": "medium",
                        "data": {
                            "dominant_service": service_name,
                            "usage_percentage": usage_percentage
                        }
                    })
            
            # Service diversity insights
            active_services = summary.get("active_services", 0)
            if active_services < 3 and total_interactions > 10:
                insights.append({
                    "type": "service_diversity",
                    "title": "Expand Your Wellness Toolkit",
                    "description": f"You're using {active_services} out of many available services.",
                    "recommendation": "Try exploring voice features, community support, or mood tracking to get more comprehensive insights.",
                    "priority": "low",
                    "data": {
                        "active_services": active_services,
                        "total_interactions": total_interactions
                    }
                })
        
        # Interaction frequency insights
        analysis_period = summary.get("analysis_period", {})
        days = analysis_period.get("days", 30)
        total_interactions = summary.get("total_interactions", 0)
        daily_average = total_interactions / days if days > 0 else 0
        
        if daily_average < 1 and total_interactions > 0:
            insights.append({
                "type": "engagement_frequency",
                "title": "Increase Engagement Frequency",
                "description": f"You're averaging {daily_average:.1f} interactions per day.",
                "recommendation": "Try setting daily reminders to check in with your mood or thoughts.",
                "priority": "medium",
                "data": {
                    "daily_average": daily_average,
                    "total_interactions": total_interactions
                }
            })
        elif daily_average > 5:
            insights.append({
                "type": "high_engagement",
                "title": "Great Engagement! 🎉",
                "description": f"You're very active with {daily_average:.1f} interactions per day.",
                "recommendation": "Your consistent engagement is helping us provide better insights. Keep it up!",
                "priority": "low",
                "data": {
                    "daily_average": daily_average,
                    "engagement_level": "high"
                }
            })
        
        result = {
            "cross_platform_summary": summary,
            "insights": insights,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"📊 Generated cross-platform insights for user {current_user.id}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to get cross-platform insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cross-platform insights: {str(e)}")

@router.put("/insights/{insight_id}/dismiss")
async def dismiss_insight(
    insight_id: int,
    reason: Optional[str] = Query(None, description="Reason for dismissing"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dismiss an insight (mark as not relevant)
    """
    try:
        insight = db.query(BehavioralInsight).filter(
            BehavioralInsight.id == insight_id,
            BehavioralInsight.user_id == current_user.id,
            BehavioralInsight.is_deleted == False
        ).first()
        
        if not insight:
            raise HTTPException(status_code=404, detail="Insight not found")
        
        # Update status
        insight.status = "dismissed"
        insight.is_active = False
        
        # Add dismissal reason to feedback
        dismissal_data = {
            "dismissed": True,
            "reason": reason,
            "dismissed_at": datetime.now(timezone.utc).isoformat()
        }
        
        current_feedback = insight.user_feedback or {}
        current_feedback.update(dismissal_data)
        insight.user_feedback = current_feedback
        
        db.commit()
        
        logger.info(f"❌ Dismissed insight {insight_id} for user {current_user.id}")
        
        return {"message": "Insight dismissed successfully", "id": insight_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to dismiss insight: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to dismiss insight: {str(e)}")

@router.get("/insights/types")
async def get_insight_types(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get available insight types and their descriptions
    """
    try:
        # Get insight types from user's data
        insight_types = db.query(BehavioralInsight.insight_type).filter(
            BehavioralInsight.user_id == current_user.id,
            BehavioralInsight.is_deleted == False
        ).distinct().all()
        
        # Define insight type descriptions
        type_descriptions = {
            "mood_optimization": "Recommendations for optimizing mood patterns",
            "mood_support": "Support suggestions for challenging mood periods",
            "positive_trend": "Recognition of positive mood trends",
            "mood_alert": "Alerts for concerning mood changes",
            "engagement_pattern": "Insights about platform usage patterns",
            "engagement_encouragement": "Encouragement for increased engagement",
            "cultural_adaptation": "Cultural context and adaptation insights",
            "service_usage": "Service usage pattern insights",
            "service_diversity": "Recommendations for exploring new features",
            "engagement_frequency": "Feedback on interaction frequency",
            "high_engagement": "Recognition of high engagement levels",
            "recommendation": "General wellness recommendations",
            "warning": "Important warnings or alerts",
            "trend": "Pattern and trend observations",
            "achievement": "Recognition of achievements and progress"
        }
        
        # Build response
        available_types = []
        for (insight_type,) in insight_types:
            available_types.append({
                "type": insight_type,
                "description": type_descriptions.get(insight_type, "Custom insight type"),
                "available": True
            })
        
        # Add other types that might be available but not yet generated
        for insight_type, description in type_descriptions.items():
            if insight_type not in [t["type"] for t in available_types]:
                available_types.append({
                    "type": insight_type,
                    "description": description,
                    "available": False
                })
        
        logger.info(f"📋 Retrieved insight types for user {current_user.id}")
        
        return {
            "insight_types": available_types,
            "total_types": len(available_types),
            "active_types": len([t for t in available_types if t["available"]])
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get insight types: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get insight types: {str(e)}")

@router.delete("/insights/{insight_id}")
async def delete_insight(
    insight_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete an insight
    """
    try:
        insight = db.query(BehavioralInsight).filter(
            BehavioralInsight.id == insight_id,
            BehavioralInsight.user_id == current_user.id,
            BehavioralInsight.is_deleted == False
        ).first()
        
        if not insight:
            raise HTTPException(status_code=404, detail="Insight not found")
        
        # Soft delete
        insight.is_deleted = True
        insight.is_active = False
        insight.status = "deleted"
        
        db.commit()
        
        logger.info(f"🗑️ Deleted insight {insight_id} for user {current_user.id}")
        
        return {"message": "Insight deleted successfully", "id": insight_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete insight: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete insight: {str(e)}")
