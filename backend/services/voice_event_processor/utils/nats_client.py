"""
NATS Client for Voice Event Processor
"""

import logging
import nats
from nats.js import JetStreamContext
from typing import Optional

logger = logging.getLogger(__name__)

class NATSClient:
    """NATS connection client"""
    
    def __init__(self, servers: list = None):
        self.servers = servers or ["nats://localhost:4222"]
        self.nc: Optional[nats.NATS] = None
        self.js: Optional[JetStreamContext] = None
        
    async def connect(self):
        """Connect to NATS"""
        try:
            self.nc = await nats.connect(servers=self.servers)
            self.js = self.nc.jetstream()
            logger.info(f"Connected to NATS at {self.servers}")
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            raise
    
    async def close(self):
        """Close NATS connection"""
        if self.nc:
            await self.nc.close()
            logger.info("NATS connection closed")
    
    @property
    def is_connected(self) -> bool:
        """Check if NATS is connected"""
        return self.nc is not None and not self.nc.is_closed
    
    def jetstream(self) -> JetStreamContext:
        """Get JetStream context"""
        return self.js
