"""
Memory Service Client for Chatbot Service
Handles communication with Memory Service for conversation history and context management
"""
import os
import json
import asyncio
import httpx
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Memory entry from Memory Service"""
    id: str
    session_id: str
    user_id: str
    content: str
    entry_type: str
    importance: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class ConversationSummary:
    """Conversation summary from Memory Service"""
    session_id: str
    summary: str
    key_topics: List[str]
    emotional_state: str
    important_moments: List[Dict[str, Any]]
    created_at: datetime

class MemoryServiceClient:
    """Client for communicating with Memory Service"""
    
    def __init__(self):
        """Initialize Memory Service client"""
        self.memory_service_url = os.getenv("MEMORY_SERVICE_URL", "http://memory-service:8017")
        self.timeout = int(os.getenv("MEMORY_SERVICE_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("MEMORY_SERVICE_MAX_RETRIES", "3"))
        
        # Feature flags
        self.is_enabled = os.getenv("MEMORY_SERVICE_ENABLED", "true").lower() == "true"
        
        logger.info(f"Memory Service Client initialized - URL: {self.memory_service_url}, Enabled: {self.is_enabled}")
    
    async def check_health(self) -> bool:
        """Check if Memory Service is healthy"""
        if not self.is_enabled:
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.memory_service_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Memory Service health check failed: {e}")
            return False
    
    # Alias for compatibility
    async def health_check(self) -> bool:
        """Alias for check_health for compatibility"""
        return await self.check_health()
    
    async def store_conversation_memory(
        self, 
        session_id: str, 
        user_id: str, 
        message: str, 
        response: str,
        emotion: Optional[str] = None,
        importance: float = 0.5,
        jwt_token: Optional[str] = None
    ) -> bool:
        """Store conversation memory entry"""
        if not self.is_enabled:
            logger.debug("Memory Service is disabled, skipping memory storage")
            return True
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            for attempt in range(self.max_retries):
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response_data = await client.post(
                            f"{self.memory_service_url}/api/v1/memory/conversation",
                            headers=headers,
                            json={
                                "session_id": session_id,
                                "user_id": user_id,
                                "user_message": message,
                                "bot_response": response,
                                "emotion": emotion,
                                "importance": importance,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        )
                        
                        if response_data.status_code == 200:
                            logger.debug(f"Memory stored successfully for session {session_id}")
                            return True
                        else:
                            logger.warning(f"Memory Service returned status {response_data.status_code}")
                            return False
                            
                except httpx.TimeoutException:
                    logger.warning(f"Memory Service timeout on attempt {attempt + 1}")
                    if attempt == self.max_retries - 1:
                        return False
                    await asyncio.sleep(1 * (attempt + 1))
                    
        except Exception as e:
            logger.error(f"Error storing conversation memory: {e}")
            return False
    
    async def get_conversation_context(
        self, 
        session_id: str, 
        user_id: str,
        limit: int = 5,
        jwt_token: Optional[str] = None
    ) -> List[MemoryEntry]:
        """Get conversation context from memory"""
        if not self.is_enabled:
            logger.debug("Memory Service is disabled, returning empty context")
            return []
            
        try:
            headers = {}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            for attempt in range(self.max_retries):
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.get(
                            f"{self.memory_service_url}/api/v1/memory/conversation/{session_id}",
                            headers=headers,
                            params={"limit": limit}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            entries = []
                            
                            for entry_data in data.get("memories", []):
                                entry = MemoryEntry(
                                    id=entry_data.get("id"),
                                    session_id=entry_data.get("session_id"),
                                    user_id=entry_data.get("user_id"),
                                    content=entry_data.get("content"),
                                    entry_type=entry_data.get("entry_type"),
                                    importance=entry_data.get("importance", 0.5),
                                    timestamp=datetime.fromisoformat(entry_data.get("timestamp")),
                                    metadata=entry_data.get("metadata", {})
                                )
                                entries.append(entry)
                            
                            logger.debug(f"Retrieved {len(entries)} memory entries for session {session_id}")
                            return entries
                        else:
                            logger.warning(f"Memory Service returned status {response.status_code}")
                            return []
                            
                except httpx.TimeoutException:
                    logger.warning(f"Memory Service timeout on attempt {attempt + 1}")
                    if attempt == self.max_retries - 1:
                        return []
                    await asyncio.sleep(1 * (attempt + 1))
                    
        except Exception as e:
            logger.error(f"Error retrieving conversation context: {e}")
            return []
    
    async def get_conversation_summary(
        self, 
        session_id: str,
        jwt_token: Optional[str] = None
    ) -> Optional[ConversationSummary]:
        """Get conversation summary from memory"""
        if not self.is_enabled:
            logger.debug("Memory Service is disabled, returning None")
            return None
            
        try:
            headers = {}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            for attempt in range(self.max_retries):
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.get(
                            f"{self.memory_service_url}/api/v1/memory/summary/{session_id}",
                            headers=headers
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            summary = ConversationSummary(
                                session_id=data.get("session_id"),
                                summary=data.get("summary"),
                                key_topics=data.get("key_topics", []),
                                emotional_state=data.get("emotional_state"),
                                important_moments=data.get("important_moments", []),
                                created_at=datetime.fromisoformat(data.get("created_at"))
                            )
                            
                            logger.debug(f"Retrieved conversation summary for session {session_id}")
                            return summary
                        else:
                            logger.warning(f"Memory Service returned status {response.status_code}")
                            return None
                            
                except httpx.TimeoutException:
                    logger.warning(f"Memory Service timeout on attempt {attempt + 1}")
                    if attempt == self.max_retries - 1:
                        return None
                    await asyncio.sleep(1 * (attempt + 1))
                    
        except Exception as e:
            logger.error(f"Error retrieving conversation summary: {e}")
            return None

# Global instance
memory_service_client = MemoryServiceClient()
