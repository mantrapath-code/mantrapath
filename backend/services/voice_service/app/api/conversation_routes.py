"""
Conversation Routes
Handles conversation flow, context-aware responses, and dialogue management
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from ..core.conversation_manager import ConversationManager
from ..core.context_processor import ContextProcessor
from ..core.models_client import ModelsServiceClient
from ..core.session_manager import SessionManager
from ..models.requests import ConversationRequest
from ..models.responses import ConversationResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/conversation", tags=["conversation"])

# Initialize components
conversation_manager = ConversationManager()
context_processor = ContextProcessor()
models_client = ModelsServiceClient()
session_manager = SessionManager()

@router.post("/chat", response_model=ConversationResponse)
async def chat(request: ConversationRequest):
    """
    Process conversation with context awareness and multi-language support
    """
    try:
        # Get or create session
        session_id = request.session_id
        if not session_id:
            session_id = conversation_manager.create_session(request.user_id)
        
        # Analyze sentiment
        sentiment_result = await models_client.analyze_sentiment(
            text=request.text,
            language=request.language if request.language != "auto" else "en"
        )
        
        # Process context
        session_context = conversation_manager.get_conversation_context(session_id)
        processed_context = context_processor.process_context(
            text=request.text,
            session_context=session_context,
            sentiment=sentiment_result.sentiment,
            confidence=sentiment_result.confidence
        )
        
        # Generate contextual response
        bot_response = conversation_manager.generate_contextual_response(
            session_id=session_id,
            user_input=request.text,
            sentiment=sentiment_result.sentiment,
            language=processed_context.language_detected
        )
        
        # Add conversation turn
        conversation_manager.add_turn(
            session_id=session_id,
            user_input=request.text,
            bot_response=bot_response,
            sentiment=sentiment_result.sentiment,
            confidence=sentiment_result.confidence,
            language=processed_context.language_detected
        )
        
        # Generate audio response if requested
        audio_response = None
        if request.voice_response:
            tts_result = await models_client.text_to_speech(
                text=bot_response,
                language=processed_context.language_detected
            )
            
            if tts_result.success:
                audio_response = {
                    "has_audio": True,
                    "duration": tts_result.duration,
                    "sample_rate": tts_result.sample_rate,
                    "model_used": tts_result.model_used
                }
        
        return ConversationResponse(
            success=True,
            user_input=request.text,
            bot_response=bot_response,
            sentiment_analysis={
                "sentiment": sentiment_result.sentiment,
                "confidence": sentiment_result.confidence,
                "scores": sentiment_result.scores
            },
            language_info={
                "detected": processed_context.language_detected,
                "confidence": processed_context.confidence,
                "adaptations": processed_context.cultural_adaptations
            },
            context_used=session_context,
            audio_response=audio_response,
            session_id=session_id,
            conversation_turn=len(session_context.get("recent_turns", []))
        )
        
    except Exception as e:
        logger.error(f"Conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/context")
async def get_conversation_context(session_id: str):
    """Get conversation context for a session"""
    try:
        context = conversation_manager.get_conversation_context(session_id)
        if not context:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return context
    except Exception as e:
        logger.error(f"Get context error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/patterns")
async def get_conversation_patterns(session_id: str):
    """Analyze conversation patterns for a session"""
    try:
        patterns = conversation_manager.detect_conversation_patterns(session_id)
        return patterns
    except Exception as e:
        logger.error(f"Pattern analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/sentiment-history")
async def get_sentiment_history(session_id: str, limit: int = 10):
    """Get sentiment history for a session"""
    try:
        history = conversation_manager.get_sentiment_history(session_id, limit)
        return {"sentiment_history": history}
    except Exception as e:
        logger.error(f"Sentiment history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/{session_id}/context")
async def update_conversation_context(session_id: str, context_update: dict):
    """Update conversation context"""
    try:
        success = conversation_manager.update_session_context(session_id, context_update)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"success": True, "message": "Context updated"}
    except Exception as e:
        logger.error(f"Update context error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_conversation_stats():
    """Get conversation statistics"""
    try:
        stats = conversation_manager.get_session_stats()
        return stats
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
