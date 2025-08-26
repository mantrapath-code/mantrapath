"""
Interactions API - Handles user interaction recording and retrieval
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
from shared.models import UserInteraction
from services.memory_engine import MemoryEngine

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for API
class InteractionCreate(BaseModel):
    interaction_type: str = Field(..., description="Type of interaction (mood, journal, chat, etc.)")
    interaction_data: Dict[str, Any] = Field(..., description="Interaction data")
    source_service: str = Field(..., description="Source service name")
    session_id: Optional[str] = Field(None, description="Session ID if available")
    cultural_context: Optional[Dict[str, Any]] = Field(None, description="Cultural context")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class InteractionResponse(BaseModel):
    id: int
    user_id: str
    interaction_type: str
    interaction_data: Dict[str, Any]
    source_service: str
    session_id: Optional[str]
    cultural_context: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    timestamp: datetime
    processing_time_ms: Optional[float]
    confidence_score: Optional[float]
    quality_score: Optional[float]

    class Config:
        from_attributes = True

class InteractionQuery(BaseModel):
    interaction_type: Optional[str] = None
    source_service: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)

# Dependency to get Memory Engine
async def get_memory_engine() -> MemoryEngine:
    """Get Memory Engine instance"""
    # This would be injected from the main app
    from main import memory_engine
    if not memory_engine:
        raise HTTPException(status_code=503, detail="Memory Engine not available")
    return memory_engine

@router.post("/interactions", response_model=InteractionResponse)
async def create_interaction(
    interaction: InteractionCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """
    Record a new user interaction
    """
    try:
        # Record interaction
        recorded_interaction = await memory_engine.record_interaction(
            user_id=current_user.id,
            interaction_type=interaction.interaction_type,
            interaction_data=interaction.interaction_data,
            source_service=interaction.source_service,
            session_id=interaction.session_id,
            cultural_context=interaction.cultural_context,
            metadata=interaction.metadata
        )
        
        logger.info(f"📝 Created interaction {recorded_interaction.id} for user {current_user.id}")
        
        return InteractionResponse.from_orm(recorded_interaction)
        
    except Exception as e:
        logger.error(f"❌ Failed to create interaction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create interaction: {str(e)}")

@router.get("/interactions", response_model=List[InteractionResponse])
async def get_interactions(
    interaction_type: Optional[str] = Query(None, description="Filter by interaction type"),
    source_service: Optional[str] = Query(None, description="Filter by source service"),
    start_date: Optional[datetime] = Query(None, description="Filter from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter to this date"),
    limit: int = Query(100, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """
    Get user interactions with filtering options
    """
    try:
        interactions = await memory_engine.get_user_interactions(
            user_id=current_user.id,
            interaction_type=interaction_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        logger.info(f"📊 Retrieved {len(interactions)} interactions for user {current_user.id}")
        
        return [InteractionResponse.from_orm(interaction) for interaction in interactions]
        
    except Exception as e:
        logger.error(f"❌ Failed to get interactions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get interactions: {str(e)}")

@router.get("/interactions/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(
    interaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific interaction by ID
    """
    try:
        interaction = db.query(UserInteraction).filter(
            UserInteraction.id == interaction_id,
            UserInteraction.user_id == current_user.id,
            UserInteraction.is_deleted == False
        ).first()
        
        if not interaction:
            raise HTTPException(status_code=404, detail="Interaction not found")
        
        logger.info(f"📊 Retrieved interaction {interaction_id} for user {current_user.id}")
        
        return InteractionResponse.from_orm(interaction)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get interaction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get interaction: {str(e)}")

@router.delete("/interactions/{interaction_id}")
async def delete_interaction(
    interaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete an interaction (mark as deleted)
    """
    try:
        interaction = db.query(UserInteraction).filter(
            UserInteraction.id == interaction_id,
            UserInteraction.user_id == current_user.id,
            UserInteraction.is_deleted == False
        ).first()
        
        if not interaction:
            raise HTTPException(status_code=404, detail="Interaction not found")
        
        # Soft delete
        interaction.is_deleted = True
        interaction.deleted_at = datetime.now(timezone.utc)
        
        db.commit()
        
        logger.info(f"🗑️ Deleted interaction {interaction_id} for user {current_user.id}")
        
        return {"message": "Interaction deleted successfully", "id": interaction_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete interaction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete interaction: {str(e)}")

@router.get("/interactions/stats/summary")
async def get_interaction_stats(
    days: int = Query(30, description="Number of days to analyze", le=365),
    current_user: User = Depends(get_current_user),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """
    Get interaction statistics summary
    """
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Get interactions for the period
        interactions = await memory_engine.get_user_interactions(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            limit=10000  # Get all for stats
        )
        
        # Calculate statistics
        total_interactions = len(interactions)
        
        # Group by type
        type_counts = {}
        for interaction in interactions:
            interaction_type = interaction.interaction_type
            type_counts[interaction_type] = type_counts.get(interaction_type, 0) + 1
        
        # Group by service
        service_counts = {}
        for interaction in interactions:
            service = interaction.source_service
            service_counts[service] = service_counts.get(service, 0) + 1
        
        # Calculate daily averages
        daily_average = total_interactions / days if days > 0 else 0
        
        # Most active day
        daily_counts = {}
        for interaction in interactions:
            day = interaction.timestamp.date()
            daily_counts[day] = daily_counts.get(day, 0) + 1
        
        most_active_day = max(daily_counts.items(), key=lambda x: x[1]) if daily_counts else None
        
        stats = {
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "total_interactions": total_interactions,
            "daily_average": round(daily_average, 2),
            "most_active_day": {
                "date": most_active_day[0].isoformat() if most_active_day else None,
                "count": most_active_day[1] if most_active_day else 0
            },
            "by_type": type_counts,
            "by_service": service_counts,
            "unique_types": len(type_counts),
            "unique_services": len(service_counts)
        }
        
        logger.info(f"📊 Generated interaction stats for user {current_user.id}")
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ Failed to get interaction stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get interaction stats: {str(e)}")

@router.get("/interactions/export")
async def export_interactions(
    format: str = Query("json", description="Export format (json, csv)"),
    start_date: Optional[datetime] = Query(None, description="Filter from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter to this date"),
    current_user: User = Depends(get_current_user),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """
    Export user interactions in various formats
    """
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Unsupported export format")
        
        # Get all interactions for the period
        interactions = await memory_engine.get_user_interactions(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            limit=10000  # Large limit for export
        )
        
        if format == "json":
            # Return JSON format
            export_data = {
                "user_id": current_user.id,
                "export_timestamp": datetime.now(timezone.utc).isoformat(),
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "total_interactions": len(interactions),
                "interactions": [
                    {
                        "id": interaction.id,
                        "interaction_type": interaction.interaction_type,
                        "interaction_data": interaction.interaction_data,
                        "source_service": interaction.source_service,
                        "timestamp": interaction.timestamp.isoformat(),
                        "cultural_context": interaction.cultural_context,
                        "metadata": interaction.metadata
                    }
                    for interaction in interactions
                ]
            }
            
            logger.info(f"📤 Exported {len(interactions)} interactions as JSON for user {current_user.id}")
            
            return export_data
        
        elif format == "csv":
            # For CSV, we'll return a simplified format
            # In a real implementation, you'd use pandas or similar
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "id", "timestamp", "interaction_type", "source_service", 
                "session_id", "interaction_data_summary"
            ])
            
            # Write data
            for interaction in interactions:
                writer.writerow([
                    interaction.id,
                    interaction.timestamp.isoformat(),
                    interaction.interaction_type,
                    interaction.source_service,
                    interaction.session_id or "",
                    str(interaction.interaction_data)[:100] + "..." if len(str(interaction.interaction_data)) > 100 else str(interaction.interaction_data)
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            logger.info(f"📤 Exported {len(interactions)} interactions as CSV for user {current_user.id}")
            
            return {"csv_data": csv_content, "total_interactions": len(interactions)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to export interactions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export interactions: {str(e)}")

@router.post("/interactions/bulk", response_model=List[InteractionResponse])
async def create_bulk_interactions(
    interactions: List[InteractionCreate],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """
    Create multiple interactions in bulk
    """
    try:
        if len(interactions) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 interactions per bulk request")
        
        created_interactions = []
        
        for interaction in interactions:
            recorded_interaction = await memory_engine.record_interaction(
                user_id=current_user.id,
                interaction_type=interaction.interaction_type,
                interaction_data=interaction.interaction_data,
                source_service=interaction.source_service,
                session_id=interaction.session_id,
                cultural_context=interaction.cultural_context,
                metadata=interaction.metadata
            )
            created_interactions.append(recorded_interaction)
        
        logger.info(f"📝 Created {len(created_interactions)} bulk interactions for user {current_user.id}")
        
        return [InteractionResponse.from_orm(interaction) for interaction in created_interactions]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create bulk interactions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create bulk interactions: {str(e)}")
