"""
Voice Service Session Management Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from app.core.session_manager import SessionManager
from app.models.requests import CreateSessionRequest, UpdateSessionRequest
from app.models.responses import SessionResponse, APIResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])

# Dependency to get session manager
def get_session_manager() -> SessionManager:
    return SessionManager()

@router.post("/", response_model=APIResponse[SessionResponse])
async def create_session(
    request: CreateSessionRequest,
    session_manager: SessionManager = Depends(get_session_manager)
) -> APIResponse[SessionResponse]:
    """Create a new voice conversation session."""
    try:
        session_id = session_manager.create_session(
            user_id=request.user_id,
            language=request.language,
            preferences=request.preferences
        )
        
        session_data = session_manager.get_session(session_id)
        session_response = SessionResponse(
            session_id=session_id,
            user_id=session_data["user_id"],
            language=session_data["language"],
            status=session_data["status"],
            created_at=session_data["created_at"],
            last_activity=session_data["last_activity"],
            preferences=session_data["preferences"],
            total_turns=session_data["total_turns"]
        )
        
        return APIResponse(
            success=True,
            data=session_response,
            message="Session created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}", response_model=APIResponse[SessionResponse])
async def get_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
) -> APIResponse[SessionResponse]:
    """Get session details."""
    try:
        session_data = session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_response = SessionResponse(
            session_id=session_id,
            user_id=session_data["user_id"],
            language=session_data["language"],
            status=session_data["status"],
            created_at=session_data["created_at"],
            last_activity=session_data["last_activity"],
            preferences=session_data["preferences"],
            total_turns=session_data["total_turns"]
        )
        
        return APIResponse(
            success=True,
            data=session_response,
            message="Session retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{session_id}", response_model=APIResponse[SessionResponse])
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    session_manager: SessionManager = Depends(get_session_manager)
) -> APIResponse[SessionResponse]:
    """Update session preferences."""
    try:
        success = session_manager.update_session(session_id, request.dict(exclude_unset=True))
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = session_manager.get_session(session_id)
        session_response = SessionResponse(
            session_id=session_id,
            user_id=session_data["user_id"],
            language=session_data["language"],
            status=session_data["status"],
            created_at=session_data["created_at"],
            last_activity=session_data["last_activity"],
            preferences=session_data["preferences"],
            total_turns=session_data["total_turns"]
        )
        
        return APIResponse(
            success=True,
            data=session_response,
            message="Session updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{session_id}", response_model=APIResponse[Dict[str, str]])
async def delete_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
) -> APIResponse[Dict[str, str]]:
    """Delete a session."""
    try:
        success = session_manager.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return APIResponse(
            success=True,
            data={"session_id": session_id},
            message="Session deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/history", response_model=APIResponse[List[Dict[str, Any]]])
async def get_session_history(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
) -> APIResponse[List[Dict[str, Any]]]:
    """Get conversation history for a session."""
    try:
        history = session_manager.get_conversation_history(session_id)
        if history is None:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return APIResponse(
            success=True,
            data=history,
            message="Session history retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
