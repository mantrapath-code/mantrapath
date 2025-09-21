"""
Rate Limiting Middleware
"""
import hashlib
from typing import Dict, Optional
from datetime import datetime, timedelta
from src.core.models import RateLimitState
from src.core.config import gateway_config

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self):
        self._buckets: Dict[str, RateLimitState] = {}
        self._requests_per_minute = gateway_config.rate_limit_requests_per_minute
        self._burst_capacity = gateway_config.rate_limit_burst
        self._window_size = 60  # 1 minute window
    
    def is_allowed(self, identifier: str, cost: int = 1) -> bool:
        """Check if request is allowed under rate limit"""
        if not gateway_config.rate_limit_enabled:
            return True
        
        now = datetime.now()
        
        # Get or create bucket for this identifier
        if identifier not in self._buckets:
            self._buckets[identifier] = RateLimitState(
                identifier=identifier,
                request_count=0,
                window_start=now
            )
        
        bucket = self._buckets[identifier]
        
        # Check if we're in a new time window
        time_since_window_start = (now - bucket.window_start).total_seconds()
        if time_since_window_start >= self._window_size:
            # Reset the window
            bucket.window_start = now
            bucket.request_count = 0
            bucket.blocked_until = None
        
        # Check if currently blocked
        if bucket.blocked_until and now < bucket.blocked_until:
            return False
        
        # Check rate limit
        if bucket.request_count + cost <= self._requests_per_minute:
            bucket.request_count += cost
            return True
        else:
            # Rate limit exceeded, block for remainder of window
            window_end = bucket.window_start + timedelta(seconds=self._window_size)
            bucket.blocked_until = window_end
            return False
    
    def get_rate_limit_info(self, identifier: str) -> Dict[str, any]:
        """Get rate limit information for an identifier"""
        if identifier not in self._buckets:
            return {
                "limit": self._requests_per_minute,
                "remaining": self._requests_per_minute,
                "reset_time": datetime.now() + timedelta(seconds=self._window_size),
                "blocked": False
            }
        
        bucket = self._buckets[identifier]
        now = datetime.now()
        
        # Calculate remaining requests
        time_since_window_start = (now - bucket.window_start).total_seconds()
        if time_since_window_start >= self._window_size:
            remaining = self._requests_per_minute
            reset_time = now + timedelta(seconds=self._window_size)
        else:
            remaining = max(0, self._requests_per_minute - bucket.request_count)
            reset_time = bucket.window_start + timedelta(seconds=self._window_size)
        
        # Check if blocked
        blocked = bucket.blocked_until and now < bucket.blocked_until
        
        return {
            "limit": self._requests_per_minute,
            "remaining": remaining,
            "reset_time": reset_time,
            "blocked": blocked
        }
    
    def cleanup_old_buckets(self):
        """Clean up old rate limit buckets to prevent memory leaks"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self._window_size * 2)  # Keep extra buffer
        
        old_identifiers = [
            identifier for identifier, bucket in self._buckets.items()
            if bucket.window_start < cutoff
        ]
        
        for identifier in old_identifiers:
            del self._buckets[identifier]

def get_client_identifier(request_headers: Dict[str, str], user_id: Optional[str] = None) -> str:
    """Generate a unique identifier for rate limiting"""
    if user_id:
        # Use user ID for authenticated users
        return f"user:{user_id}"
    
    # Use IP address for anonymous users
    ip_address = (
        request_headers.get('x-forwarded-for', '').split(',')[0].strip() or
        request_headers.get('x-real-ip', '') or
        request_headers.get('remote-addr', 'unknown')
    )
    
    # Hash the IP for privacy
    hashed_ip = hashlib.sha256(ip_address.encode()).hexdigest()[:16]
    return f"ip:{hashed_ip}"
