"""
Session Manager
Handles user sessions, state persistence, and session lifecycle
"""
import logging
import redis
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import uuid
import os

logger = logging.getLogger(__name__)

@dataclass
class UserSession:
    """User session data structure"""
    session_id: str
    user_id: Optional[str]
    created_at: datetime
    last_activity: datetime
    preferences: Dict[str, Any]
    context: Dict[str, Any]
    conversation_id: Optional[str] = None
    is_active: bool = True
    voice_settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.voice_settings is None:
            self.voice_settings = {}

class SessionManager:
    """Manages user sessions with Redis persistence"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis_client = None
        self.session_timeout_hours = 24
        self.cleanup_interval_hours = 1
        self.key_prefix = "voice_session:"
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info("Connected to Redis for session management")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Fall back to in-memory storage
            self._sessions = {}
            logger.warning("Using in-memory session storage as fallback")
    
    def create_session(self, user_id: Optional[str] = None, 
                      preferences: Optional[Dict[str, Any]] = None) -> str:
        """Create a new user session"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            preferences=preferences or {},
            context={},
            voice_settings={
                "preferred_language": "en",
                "voice_speed": 1.0,
                "voice_pitch": 1.0,
                "preferred_voice": None
            }
        )
        
        self._store_session(session)
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Retrieve session by ID"""
        return self._load_session(session_id)
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Update allowed fields
        allowed_updates = ['preferences', 'context', 'voice_settings', 'conversation_id']
        for key, value in updates.items():
            if key in allowed_updates:
                setattr(session, key, value)
        
        session.last_activity = datetime.now()
        self._store_session(session)
        return True
    
    def update_preferences(self, session_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.preferences.update(preferences)
        session.last_activity = datetime.now()
        self._store_session(session)
        return True
    
    def update_voice_settings(self, session_id: str, voice_settings: Dict[str, Any]) -> bool:
        """Update voice-specific settings"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.voice_settings.update(voice_settings)
        session.last_activity = datetime.now()
        self._store_session(session)
        return True
    
    def update_context(self, session_id: str, context_update: Dict[str, Any]) -> bool:
        """Update session context"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.context.update(context_update)
        session.last_activity = datetime.now()
        self._store_session(session)
        return True
    
    def touch_session(self, session_id: str) -> bool:
        """Update last activity timestamp"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.last_activity = datetime.now()
        self._store_session(session)
        return True
    
    def end_session(self, session_id: str) -> bool:
        """End a session"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.is_active = False
        self._store_session(session)
        
        # Remove from active storage after grace period
        if self.redis_client:
            self.redis_client.expire(f"{self.key_prefix}{session_id}", 3600)  # 1 hour grace
        else:
            # For in-memory storage, remove immediately
            if session_id in self._sessions:
                del self._sessions[session_id]
        
        logger.info(f"Ended session {session_id}")
        return True
    
    def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[UserSession]:
        """Get all sessions for a user"""
        sessions = []
        
        if self.redis_client:
            # Search Redis for user sessions
            pattern = f"{self.key_prefix}*"
            keys = self.redis_client.keys(pattern)
            
            for key in keys:
                session_data = self.redis_client.get(key)
                if session_data:
                    try:
                        session_dict = json.loads(session_data)
                        if session_dict.get("user_id") == user_id:
                            if not active_only or session_dict.get("is_active", True):
                                session = self._dict_to_session(session_dict)
                                sessions.append(session)
                    except Exception as e:
                        logger.error(f"Error parsing session data: {e}")
        else:
            # Search in-memory storage
            for session in self._sessions.values():
                if session.user_id == user_id:
                    if not active_only or session.is_active:
                        sessions.append(session)
        
        return sessions
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        expired_count = 0
        cutoff_time = datetime.now() - timedelta(hours=self.session_timeout_hours)
        
        if self.redis_client:
            # Redis cleanup
            pattern = f"{self.key_prefix}*"
            keys = self.redis_client.keys(pattern)
            
            for key in keys:
                session_data = self.redis_client.get(key)
                if session_data:
                    try:
                        session_dict = json.loads(session_data)
                        last_activity = datetime.fromisoformat(session_dict.get("last_activity"))
                        if last_activity < cutoff_time:
                            self.redis_client.delete(key)
                            expired_count += 1
                    except Exception as e:
                        logger.error(f"Error during cleanup: {e}")
        else:
            # In-memory cleanup
            expired_sessions = []
            for session_id, session in self._sessions.items():
                if session.last_activity < cutoff_time:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self._sessions[session_id]
                expired_count += 1
        
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired sessions")
        
        return expired_count
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        if self.redis_client:
            pattern = f"{self.key_prefix}*"
            keys = self.redis_client.keys(pattern)
            total_sessions = len(keys)
            
            active_sessions = 0
            unique_users = set()
            
            for key in keys:
                session_data = self.redis_client.get(key)
                if session_data:
                    try:
                        session_dict = json.loads(session_data)
                        if session_dict.get("is_active", True):
                            active_sessions += 1
                        if session_dict.get("user_id"):
                            unique_users.add(session_dict["user_id"])
                    except Exception:
                        pass
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "unique_users": len(unique_users),
                "storage_type": "redis"
            }
        else:
            active_sessions = sum(1 for s in self._sessions.values() if s.is_active)
            unique_users = set(s.user_id for s in self._sessions.values() if s.user_id)
            
            return {
                "total_sessions": len(self._sessions),
                "active_sessions": active_sessions,
                "unique_users": len(unique_users),
                "storage_type": "memory"
            }
    
    def _store_session(self, session: UserSession):
        """Store session in persistent storage"""
        session_dict = self._session_to_dict(session)
        
        if self.redis_client:
            try:
                key = f"{self.key_prefix}{session.session_id}"
                session_json = json.dumps(session_dict, default=str)
                self.redis_client.setex(
                    key, 
                    timedelta(hours=self.session_timeout_hours), 
                    session_json
                )
            except Exception as e:
                logger.error(f"Failed to store session in Redis: {e}")
                # Fall back to memory storage
                if not hasattr(self, '_sessions'):
                    self._sessions = {}
                self._sessions[session.session_id] = session
        else:
            self._sessions[session.session_id] = session
    
    def _load_session(self, session_id: str) -> Optional[UserSession]:
        """Load session from persistent storage"""
        if self.redis_client:
            try:
                key = f"{self.key_prefix}{session_id}"
                session_data = self.redis_client.get(key)
                if session_data:
                    session_dict = json.loads(session_data)
                    return self._dict_to_session(session_dict)
            except Exception as e:
                logger.error(f"Failed to load session from Redis: {e}")
        else:
            return self._sessions.get(session_id)
        
        return None
    
    def _session_to_dict(self, session: UserSession) -> Dict[str, Any]:
        """Convert session to dictionary for storage"""
        session_dict = asdict(session)
        # Convert datetime objects to ISO format
        session_dict["created_at"] = session.created_at.isoformat()
        session_dict["last_activity"] = session.last_activity.isoformat()
        return session_dict
    
    def _dict_to_session(self, session_dict: Dict[str, Any]) -> UserSession:
        """Convert dictionary to session object"""
        # Convert ISO format back to datetime
        session_dict["created_at"] = datetime.fromisoformat(session_dict["created_at"])
        session_dict["last_activity"] = datetime.fromisoformat(session_dict["last_activity"])
        
        return UserSession(**session_dict)
    
    def health_check(self) -> Dict[str, Any]:
        """Check session manager health"""
        health_status = {
            "status": "healthy",
            "storage_type": "redis" if self.redis_client else "memory"
        }
        
        if self.redis_client:
            try:
                self.redis_client.ping()
                health_status["redis_connection"] = "active"
            except Exception as e:
                health_status["status"] = "degraded"
                health_status["redis_connection"] = "failed"
                health_status["error"] = str(e)
        
        # Add session stats
        health_status.update(self.get_session_stats())
        
        return health_status
