"""
Shared utilities for API Gateway integration
"""
import sys
import os

# Add shared directory to path for importing shared modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

try:
    from auth import verify_token, decode_token
    from models import User
    from redis_client import get_redis_client
    from database import get_db_connection
except ImportError as e:
    print(f"Warning: Could not import shared modules: {e}")
    print("Gateway will run with limited shared functionality")

def get_user_from_token(token: str) -> dict:
    """Extract user information from JWT token using shared auth utilities"""
    try:
        payload = decode_token(token)
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "username": payload.get("username"),
            "is_verified": payload.get("is_verified", False)
        }
    except Exception:
        return None

def validate_service_token(token: str) -> bool:
    """Validate service-to-service authentication token"""
    try:
        return verify_token(token)
    except Exception:
        return False

def get_cached_data(key: str):
    """Get data from Redis cache using shared Redis client"""
    try:
        redis_client = get_redis_client()
        return redis_client.get(key)
    except Exception:
        return None

def set_cached_data(key: str, value: str, ttl: int = 300):
    """Set data in Redis cache using shared Redis client"""
    try:
        redis_client = get_redis_client()
        return redis_client.setex(key, ttl, value)
    except Exception:
        return False
