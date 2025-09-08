"""
Rate limiting utilities for frontend engineer API access
"""

import time
import asyncio
from typing import Dict, Any, Optional
from collections import defaultdict, deque
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.permissions import get_rate_limit


class RateLimiter:
    """Rate limiter for frontend engineer API access"""
    
    def __init__(self):
        # Store rate limit data: {engineer_id: {endpoint: deque(timestamps)}}
        self.rate_limits: Dict[str, Dict[str, deque]] = defaultdict(lambda: defaultdict(deque))
        
        # Cleanup old entries every 5 minutes
        self.cleanup_interval = 300
        self.last_cleanup = time.time()
    
    async def check_limit(self, engineer_id: str, endpoint: str) -> bool:
        """Check if an engineer has exceeded rate limit for an endpoint"""
        try:
            current_time = time.time()
            
            # Cleanup old entries periodically
            if current_time - self.last_cleanup > self.cleanup_interval:
                await self._cleanup_old_entries()
                self.last_cleanup = current_time
            
            # Get rate limit for this endpoint and engineer
            rate_limit = get_rate_limit(engineer_id, endpoint)
            
            # Get current timestamps for this engineer and endpoint
            timestamps = self.rate_limits[engineer_id][endpoint]
            
            # Remove timestamps older than 1 minute
            cutoff_time = current_time - 60
            while timestamps and timestamps[0] < cutoff_time:
                timestamps.popleft()
            
            # Check if limit exceeded
            if len(timestamps) >= rate_limit:
                return False
            
            # Add current timestamp
            timestamps.append(current_time)
            
            return True
            
        except Exception as e:
            # If rate limiting fails, allow the request (fail open)
            print(f"Rate limiting error: {e}")
            return True
    
    async def get_remaining_requests(self, engineer_id: str, endpoint: str) -> Dict[str, Any]:
        """Get remaining requests for an engineer on an endpoint"""
        try:
            current_time = time.time()
            rate_limit = get_rate_limit(engineer_id, endpoint)
            
            timestamps = self.rate_limits[engineer_id][endpoint]
            
            # Remove old timestamps
            cutoff_time = current_time - 60
            while timestamps and timestamps[0] < cutoff_time:
                timestamps.popleft()
            
            remaining = max(0, rate_limit - len(timestamps))
            reset_time = current_time + 60
            
            return {
                "remaining": remaining,
                "limit": rate_limit,
                "reset_time": reset_time,
                "reset_in_seconds": 60
            }
            
        except Exception as e:
            return {
                "remaining": 0,
                "limit": 0,
                "reset_time": 0,
                "reset_in_seconds": 0,
                "error": str(e)
            }
    
    async def get_engineer_limits(self, engineer_id: str) -> Dict[str, Any]:
        """Get all rate limits for an engineer"""
        try:
            limits = {}
            current_time = time.time()
            
            for endpoint, timestamps in self.rate_limits[engineer_id].items():
                rate_limit = get_rate_limit(engineer_id, endpoint)
                
                # Remove old timestamps
                cutoff_time = current_time - 60
                while timestamps and timestamps[0] < cutoff_time:
                    timestamps.popleft()
                
                remaining = max(0, rate_limit - len(timestamps))
                reset_time = current_time + 60
                
                limits[endpoint] = {
                    "remaining": remaining,
                    "limit": rate_limit,
                    "used": len(timestamps),
                    "reset_time": reset_time,
                    "reset_in_seconds": 60
                }
            
            return limits
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _cleanup_old_entries(self) -> None:
        """Clean up old rate limit entries"""
        try:
            current_time = time.time()
            cutoff_time = current_time - 300  # 5 minutes
            
            # Clean up old timestamps
            for engineer_id in list(self.rate_limits.keys()):
                for endpoint in list(self.rate_limits[engineer_id].keys()):
                    timestamps = self.rate_limits[engineer_id][endpoint]
                    
                    # Remove old timestamps
                    while timestamps and timestamps[0] < cutoff_time:
                        timestamps.popleft()
                    
                    # Remove empty endpoint entries
                    if not timestamps:
                        del self.rate_limits[engineer_id][endpoint]
                
                # Remove empty engineer entries
                if not self.rate_limits[engineer_id]:
                    del self.rate_limits[engineer_id]
                    
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    async def reset_engineer_limits(self, engineer_id: str) -> bool:
        """Reset rate limits for an engineer (for admin purposes)"""
        try:
            if engineer_id in self.rate_limits:
                del self.rate_limits[engineer_id]
                return True
            return False
        except Exception as e:
            print(f"Reset error: {e}")
            return False
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide rate limiting statistics"""
        try:
            total_engineers = len(self.rate_limits)
            total_endpoints = sum(len(endpoints) for endpoints in self.rate_limits.values())
            
            # Count active rate limit entries
            active_entries = 0
            current_time = time.time()
            cutoff_time = current_time - 60
            
            for engineer_id in self.rate_limits:
                for endpoint in self.rate_limits[engineer_id]:
                    timestamps = self.rate_limits[engineer_id][endpoint]
                    active_entries += sum(1 for ts in timestamps if ts >= cutoff_time)
            
            return {
                "total_engineers": total_engineers,
                "total_endpoints": total_endpoints,
                "active_entries": active_entries,
                "last_cleanup": self.last_cleanup,
                "cleanup_interval": self.cleanup_interval
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def set_custom_limit(self, engineer_id: str, endpoint: str, limit: int) -> bool:
        """Set a custom rate limit for an engineer on an endpoint (for admin purposes)"""
        try:
            # This would typically update a database or configuration
            # For now, we'll just store it in memory
            self.rate_limits[engineer_id][endpoint] = deque(maxlen=limit)
            return True
        except Exception as e:
            print(f"Set custom limit error: {e}")
            return False
