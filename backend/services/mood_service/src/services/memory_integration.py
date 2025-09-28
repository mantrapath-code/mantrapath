"""Memory service integration for mood context."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import httpx
import asyncio

from src.core.config import settings
from shared.models import MoodEntry as MoodEntryModel
from src.models.database import MoodContextModel
from src.models.schemas import MoodContextRequest, MoodContextResponse
from src.services.emotion_analysis import emotion_service

logger = logging.getLogger(__name__)


class MemoryIntegrationService:
    """Service for integrating mood data with memory service and chatbot context."""
    
    def __init__(self):
        self.http_client = None
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=30.0)
        return self.http_client
    
    async def create_mood_context(
        self,
        db: Session,
        user_id: str,
        context_request: MoodContextRequest
    ) -> MoodContextResponse:
        """
        Create mood context summary for memory service integration.
        
        Args:
            db: Database session
            user_id: User identifier
            context_request: Context creation request
            
        Returns:
            Created mood context
        """
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=context_request.time_range_hours)
            
            # Get mood entries in the time range
            mood_entries = (
                db.query(MoodEntryModel)
                .filter(
                    MoodEntryModel.user_id == user_id,
                    MoodEntryModel.created_at >= start_time,
                    MoodEntryModel.created_at <= end_time
                )
                .order_by(MoodEntryModel.created_at.desc())
                .all()
            )
            
            if not mood_entries:
                # Create empty context
                context = MoodContextModel(
                    user_id=user_id,
                    session_id=context_request.session_id,
                    context_summary="No mood data available for the specified time period",
                    context_start=start_time,
                    context_end=end_time
                )
            else:
                # Calculate mood summary
                average_mood = sum(entry.mood_score for entry in mood_entries) / len(mood_entries)
                
                # Get emotion distribution
                emotions_data = []
                for entry in mood_entries:
                    if entry.emotion_analysis:
                        emotions_data.append(entry.emotion_analysis)
                
                emotion_summary = await emotion_service.get_emotion_summary(emotions_data)
                
                # Generate context summary
                context_summary = self._generate_context_summary(
                    mood_entries, 
                    average_mood, 
                    emotion_summary,
                    context_request.time_range_hours
                )
                
                # Create context record
                context = MoodContextModel(
                    user_id=user_id,
                    session_id=context_request.session_id,
                    context_summary=context_summary,
                    dominant_emotion=emotion_summary.get("dominant_emotion"),
                    average_mood_score=average_mood,
                    emotion_distribution=emotion_summary.get("emotion_distribution"),
                    context_start=start_time,
                    context_end=end_time
                )
            
            db.add(context)
            db.commit()
            db.refresh(context)
            
            logger.info(f"Created mood context {context.id} for user {user_id}")
            
            # Send to memory service if configured
            if settings.memory_service_url:
                await self._send_context_to_memory_service(context)
            
            return MoodContextResponse.model_validate(context)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create mood context for user {user_id}: {e}")
            raise
    
    def _generate_context_summary(
        self,
        mood_entries: List[MoodEntryModel],
        average_mood: float,
        emotion_summary: Dict[str, Any],
        time_range_hours: int
    ) -> str:
        """Generate human-readable context summary."""
        entry_count = len(mood_entries)
        dominant_emotion = emotion_summary.get("dominant_emotion", "neutral")
        dominant_sentiment = emotion_summary.get("dominant_sentiment", "neutral")
        
        # Time period description
        if time_range_hours <= 2:
            period_desc = "recent hours"
        elif time_range_hours <= 12:
            period_desc = "today"
        elif time_range_hours <= 24:
            period_desc = "past day"
        elif time_range_hours <= 48:
            period_desc = "past couple of days"
        else:
            days = time_range_hours // 24
            period_desc = f"past {days} days"
        
        # Mood level description
        if average_mood >= 8:
            mood_desc = "very positive"
        elif average_mood >= 6.5:
            mood_desc = "positive"
        elif average_mood >= 5:
            mood_desc = "neutral"
        elif average_mood >= 3.5:
            mood_desc = "somewhat low"
        else:
            mood_desc = "low"
        
        summary_parts = [
            f"Over the {period_desc}, the user has logged {entry_count} mood entries",
            f"with an average mood score of {average_mood:.1f}/10 ({mood_desc})"
        ]
        
        if dominant_emotion and dominant_emotion != "neutral":
            summary_parts.append(f"The dominant emotion has been {dominant_emotion} ({dominant_sentiment} sentiment)")
        
        # Add context about mood patterns
        if entry_count >= 3:
            recent_scores = [entry.mood_score for entry in mood_entries[:3]]
            if all(score >= recent_scores[0] for score in recent_scores):
                summary_parts.append("Mood appears to be stable or improving recently")
            elif all(score <= recent_scores[0] for score in recent_scores):
                summary_parts.append("Mood appears to be declining recently")
        
        return ". ".join(summary_parts) + "."
    
    async def _send_context_to_memory_service(self, context: MoodContextModel):
        """Send mood context to memory service."""
        try:
            client = await self._get_http_client()
            
            payload = {
                "user_id": context.user_id,
                "session_id": context.session_id,
                "context_type": "mood_summary",
                "context_data": {
                    "mood_context_id": context.id,
                    "summary": context.context_summary,
                    "dominant_emotion": context.dominant_emotion,
                    "average_mood_score": context.average_mood_score,
                    "emotion_distribution": context.emotion_distribution,
                    "time_period": {
                        "start": context.context_start.isoformat(),
                        "end": context.context_end.isoformat()
                    }
                },
                "metadata": {
                    "source": "mood_service",
                    "importance": "high" if context.average_mood_score and context.average_mood_score < 4 else "medium",
                    "timestamp": context.created_at.isoformat()
                }
            }
            
            response = await client.post(
                f"{settings.memory_service_url}/api/v1/context",
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully sent mood context {context.id} to memory service")
            else:
                logger.warning(f"Failed to send mood context to memory service: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error sending mood context to memory service: {e}")
    
    async def get_user_mood_contexts(
        self,
        db: Session,
        user_id: str,
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> List[MoodContextResponse]:
        """
        Get mood contexts for a user.
        
        Args:
            db: Database session
            user_id: User identifier
            session_id: Optional session filter
            limit: Maximum number of contexts to return
            
        Returns:
            List of mood contexts
        """
        try:
            query = db.query(MoodContextModel).filter(MoodContextModel.user_id == user_id)
            
            if session_id:
                query = query.filter(MoodContextModel.session_id == session_id)
            
            contexts = (
                query
                .order_by(MoodContextModel.created_at.desc())
                .limit(limit)
                .all()
            )
            
            return [MoodContextResponse.model_validate(context) for context in contexts]
            
        except Exception as e:
            logger.error(f"Failed to get mood contexts for user {user_id}: {e}")
            raise
    
    async def notify_chatbot_mood_change(
        self,
        user_id: str,
        mood_entry: Dict[str, Any],
        session_id: Optional[str] = None
    ):
        """
        Notify chatbot service about significant mood changes.
        
        Args:
            user_id: User identifier
            mood_entry: Mood entry data
            session_id: Optional session identifier
        """
        if not settings.chatbot_service_url:
            return
        
        try:
            # Check if mood change is significant
            mood_score = mood_entry.get("mood_score", 5)
            primary_emotion = mood_entry.get("primary_emotion")
            primary_sentiment = mood_entry.get("primary_sentiment")
            
            # Determine if this is a significant change that chatbot should know about
            should_notify = (
                mood_score <= 3 or  # Low mood
                primary_sentiment in ["negative"] or  # Negative sentiment
                primary_emotion in ["sadness", "fear", "anger", "grief", "nervousness"]  # Concerning emotions
            )
            
            if not should_notify:
                return
            
            client = await self._get_http_client()
            
            payload = {
                "user_id": user_id,
                "session_id": session_id,
                "event_type": "mood_update",
                "event_data": {
                    "mood_score": mood_score,
                    "primary_emotion": primary_emotion,
                    "primary_sentiment": primary_sentiment,
                    "description": mood_entry.get("description"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "requires_attention": mood_score <= 3
                },
                "metadata": {
                    "source": "mood_service",
                    "priority": "high" if mood_score <= 2 else "medium"
                }
            }
            
            response = await client.post(
                f"{settings.chatbot_service_url}/api/v1/events/mood-update",
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Notified chatbot about mood change for user {user_id}")
            else:
                logger.warning(f"Failed to notify chatbot about mood change: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error notifying chatbot about mood change: {e}")
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None


# Global memory integration service instance
memory_integration_service = MemoryIntegrationService()