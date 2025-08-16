"""
Intelligence API endpoints
Provides REST API for AI insights and intelligence operations
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
from models.context_models import IntelligenceInsight

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

@router.get("/insights/{user_id}", response_model=List[IntelligenceInsight])
async def get_user_insights(
    user_id: str,
    limit: int = Query(10, description="Maximum number of insights to return"),
    insight_type: Optional[str] = Query(None, description="Filter by insight type"),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-generated insights for a user
    """
    try:
        # Check authorization
        if str(current_user.id) != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this user's insights")
        
        if not intelligence_engine:
            raise HTTPException(status_code=500, detail="Intelligence engine not available")
        
        insights = await intelligence_engine.get_user_insights(user_id)
        
        # Filter by type if specified
        if insight_type:
            insights = [insight for insight in insights if insight.insight_type == insight_type]
        
        # Apply limit
        insights = insights[:limit]
        
        return insights
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting user insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user insights")

@router.post("/insights/{user_id}/generate")
async def generate_user_insights(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Generate new insights for a user
    """
    try:
        # Check authorization
        if str(current_user.id) != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to generate insights for this user")
        
        if not context_aggregator_service or not intelligence_engine:
            raise HTTPException(status_code=500, detail="Services not available")
        
        # Get user context
        user_context = await context_aggregator_service.get_user_context(user_id)
        
        if not user_context:
            raise HTTPException(status_code=404, detail="User context not found")
        
        # Generate insights
        insights = await intelligence_engine.generate_user_insights(user_id, user_context)
        
        return {
            "status": "success",
            "message": f"Generated {len(insights)} insights for user {user_id}",
            "insights_count": len(insights),
            "insights": insights[:5] if insights else []  # Return first 5 insights
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating user insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate user insights")

@router.get("/insights/{user_id}/summary")
async def get_insights_summary(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a summary of user insights
    """
    try:
        # Check authorization
        if str(current_user.id) != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this user's insights")
        
        if not intelligence_engine:
            raise HTTPException(status_code=500, detail="Intelligence engine not available")
        
        insights = await intelligence_engine.get_user_insights(user_id)
        
        # Categorize insights
        categories = {}
        priority_counts = {"low": 0, "normal": 0, "high": 0, "critical": 0}
        
        for insight in insights:
            # Count by type
            insight_type = insight.insight_type
            if insight_type not in categories:
                categories[insight_type] = 0
            categories[insight_type] += 1
            
            # Count by priority
            priority = insight.priority.value if hasattr(insight.priority, 'value') else str(insight.priority)
            if priority in priority_counts:
                priority_counts[priority] += 1
        
        # Get high priority insights
        high_priority_insights = [
            insight for insight in insights 
            if insight.priority.value in ["high", "critical"]
        ][:3]
        
        return {
            "user_id": user_id,
            "total_insights": len(insights),
            "categories": categories,
            "priority_breakdown": priority_counts,
            "high_priority_insights": [
                {
                    "type": insight.insight_type,
                    "description": insight.description,
                    "confidence": insight.confidence,
                    "priority": insight.priority.value
                }
                for insight in high_priority_insights
            ],
            "latest_insight": {
                "type": insights[0].insight_type,
                "description": insights[0].description,
                "timestamp": insights[0].timestamp
            } if insights else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting insights summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get insights summary")

@router.get("/insights/{user_id}/recommendations")
async def get_user_recommendations(
    user_id: str,
    limit: int = Query(5, description="Maximum number of recommendations"),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI recommendations for a user
    """
    try:
        # Check authorization
        if str(current_user.id) != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this user's recommendations")
        
        if not intelligence_engine:
            raise HTTPException(status_code=500, detail="Intelligence engine not available")
        
        insights = await intelligence_engine.get_user_insights(user_id)
        
        # Extract all recommendations
        all_recommendations = []
        for insight in insights:
            for rec in insight.recommendations:
                all_recommendations.append({
                    "recommendation": rec,
                    "insight_type": insight.insight_type,
                    "confidence": insight.confidence,
                    "priority": insight.priority.value,
                    "supporting_insight": insight.description
                })
        
        # Sort by priority and confidence
        priority_order = {"critical": 4, "high": 3, "normal": 2, "low": 1}
        all_recommendations.sort(
            key=lambda x: (
                priority_order.get(x["priority"], 0),
                x["confidence"]
            ),
            reverse=True
        )
        
        return {
            "user_id": user_id,
            "total_recommendations": len(all_recommendations),
            "recommendations": all_recommendations[:limit]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting user recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user recommendations")

@router.get("/intelligence/metrics")
async def get_intelligence_metrics():
    """
    Get intelligence engine metrics
    """
    try:
        if not intelligence_engine:
            raise HTTPException(status_code=500, detail="Intelligence engine not available")
        
        metrics = await intelligence_engine.get_metrics()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "intelligence_engine": metrics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting intelligence metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get intelligence metrics")

@router.get("/intelligence/status")
async def get_intelligence_status():
    """
    Get intelligence engine status
    """
    try:
        if not intelligence_engine:
            return {
                "status": "unavailable",
                "message": "Intelligence engine not available"
            }
        
        metrics = await intelligence_engine.get_metrics()
        
        status = "healthy"
        if metrics["processing_errors"] > metrics["insights_generated"] * 0.1:
            status = "degraded"
        elif not metrics["is_running"]:
            status = "stopped"
        
        return {
            "status": status,
            "message": f"Intelligence engine is {status}",
            "insights_generated": metrics["insights_generated"],
            "processing_errors": metrics["processing_errors"],
            "is_running": metrics["is_running"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting intelligence status: {e}")
        return {
            "status": "error",
            "message": "Failed to get intelligence status"
        }
