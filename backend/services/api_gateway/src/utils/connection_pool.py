"""
Enhanced HTTP Client with Connection Pooling
"""
import asyncio
import logging
from typing import Dict, Optional
import httpx
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ConnectionPool:
    """HTTP Connection Pool for Service Communication"""
    
    def __init__(self, 
                 max_connections: int = 100,
                 max_keepalive_connections: int = 20,
                 keepalive_expiry: int = 5,
                 timeout: int = 30):
        """Initialize connection pool with configuration"""
        self._max_connections = max_connections
        self._max_keepalive_connections = max_keepalive_connections
        self._keepalive_expiry = keepalive_expiry
        self._timeout = timeout
        
        # Service-specific clients
        self._clients: Dict[str, httpx.AsyncClient] = {}
        self._client_created_at: Dict[str, datetime] = {}
        
        # Default limits for all clients
        self._limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry
        )
        
        # Default timeout
        self._default_timeout = httpx.Timeout(timeout)
    
    async def get_client(self, service_name: str) -> httpx.AsyncClient:
        """Get or create HTTP client for service"""
        
        # Check if client exists and is still valid
        if service_name in self._clients:
            client_age = datetime.now() - self._client_created_at[service_name]
            if client_age < timedelta(hours=1):  # Refresh clients every hour
                return self._clients[service_name]
            else:
                # Close old client
                await self._clients[service_name].aclose()
                del self._clients[service_name]
                del self._client_created_at[service_name]
        
        # Create new client
        client = httpx.AsyncClient(
            limits=self._limits,
            timeout=self._default_timeout,
            headers={
                'User-Agent': f'MantraPath-Gateway/3.0-{service_name}',
                'X-Gateway-Version': '3.0.0',
                'X-Target-Service': service_name
            },
            follow_redirects=True
        )
        
        self._clients[service_name] = client
        self._client_created_at[service_name] = datetime.now()
        
        logger.debug(f"Created new HTTP client for service: {service_name}")
        return client
    
    async def close_all(self):
        """Close all HTTP clients"""
        for service_name, client in self._clients.items():
            try:
                await client.aclose()
                logger.debug(f"Closed HTTP client for service: {service_name}")
            except Exception as e:
                logger.warning(f"Error closing client for {service_name}: {e}")
        
        self._clients.clear()
        self._client_created_at.clear()
    
    async def cleanup_old_clients(self):
        """Cleanup clients that haven't been used recently"""
        cutoff_time = datetime.now() - timedelta(minutes=30)
        
        clients_to_remove = []
        for service_name, created_at in self._client_created_at.items():
            if created_at < cutoff_time:
                clients_to_remove.append(service_name)
        
        for service_name in clients_to_remove:
            try:
                await self._clients[service_name].aclose()
                del self._clients[service_name] 
                del self._client_created_at[service_name]
                logger.debug(f"Cleaned up old client for service: {service_name}")
            except Exception as e:
                logger.warning(f"Error cleaning up client for {service_name}: {e}")
    
    def get_client_stats(self) -> Dict[str, any]:
        """Get connection pool statistics"""
        return {
            "active_clients": len(self._clients),
            "max_connections": self._max_connections,
            "max_keepalive_connections": self._max_keepalive_connections,
            "services": list(self._clients.keys()),
            "oldest_client_age": min(
                (datetime.now() - created_at).total_seconds()
                for created_at in self._client_created_at.values()
            ) if self._client_created_at else 0
        }

# Global connection pool instance
_connection_pool: Optional[ConnectionPool] = None

def get_connection_pool() -> ConnectionPool:
    """Get global connection pool instance"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = ConnectionPool()
    return _connection_pool

async def cleanup_connection_pool():
    """Cleanup global connection pool"""
    global _connection_pool
    if _connection_pool:
        await _connection_pool.close_all()
        _connection_pool = None
