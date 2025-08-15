"""
WebSocket Manager for MantraPath API Gateway V3
Manages WebSocket connections and real-time communication
"""

from typing import Dict, Any
from fastapi import WebSocket
import structlog

logger = structlog.get_logger(__name__)


class WebSocketManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize the WebSocket manager"""
        self.initialized = True
        logger.info("WebSocket Manager initialized")
    
    async def shutdown(self):
        """Shutdown the WebSocket manager"""
        # Close all connections
        for connection_id, websocket in self.connections.items():
            try:
                await websocket.close()
            except Exception as e:
                logger.warning("Error closing WebSocket connection", connection_id=connection_id, error=str(e))
        
        self.connections.clear()
        self.initialized = False
        logger.info("WebSocket Manager shutdown complete")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for WebSocket manager"""
        return {
            "status": "healthy" if self.initialized else "unhealthy",
            "initialized": self.initialized,
            "active_connections": len(self.connections)
        }
    
    async def register_connection(self, connection_id: str, websocket: WebSocket):
        """Register a new WebSocket connection"""
        self.connections[connection_id] = websocket
        logger.info("WebSocket connection registered", connection_id=connection_id)
    
    async def unregister_connection(self, connection_id: str):
        """Unregister a WebSocket connection"""
        if connection_id in self.connections:
            del self.connections[connection_id]
            logger.info("WebSocket connection unregistered", connection_id=connection_id)
    
    async def handle_voice_stream(self, connection_id: str, message: str):
        """Handle voice stream message"""
        if connection_id not in self.connections:
            logger.warning("Voice stream for unknown connection", connection_id=connection_id)
            return
        
        # Mock implementation - echo back for now
        websocket = self.connections[connection_id]
        try:
            await websocket.send_text(f"Echo: {message}")
        except Exception as e:
            logger.error("Error sending WebSocket message", connection_id=connection_id, error=str(e))