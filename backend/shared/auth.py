"""
Shared authentication utilities and middleware
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import redis
import json
from uuid import UUID

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Redis for token blacklist and caching
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token security
security = HTTPBearer()

class AuthError(HTTPException):
    """Custom authentication error"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class PermissionError(HTTPException):
    """Custom permission error"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a new refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """Verify and decode a JWT token"""
    try:
        # Check if token is blacklisted
        if is_token_blacklisted(token):
            raise AuthError("Token has been revoked")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify token type
        if payload.get("type") != token_type:
            raise AuthError(f"Invalid token type. Expected {token_type}")
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise AuthError("Token has expired")
        
        return payload
    
    except JWTError as e:
        raise AuthError(f"Invalid token: {str(e)}")

def blacklist_token(token: str, expires_in: Optional[int] = None):
    """Add token to blacklist"""
    if expires_in is None:
        expires_in = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    
    redis_client.setex(f"blacklist:{token}", expires_in, "true")

def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    return redis_client.exists(f"blacklist:{token}")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise AuthError("Invalid token payload")
    
    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role", "user"),
        "full_name": payload.get("full_name"),
        "is_active": payload.get("is_active", True)
    }

def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user if token is provided, otherwise return None"""
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.split(" ")[1]
        payload = verify_token(token)
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role", "user"),
            "full_name": payload.get("full_name"),
            "is_active": payload.get("is_active", True)
        }
    except:
        return None

def require_role(required_role: str):
    """Decorator to require specific role"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role", "user")
        
        # Role hierarchy: admin > moderator > user
        role_hierarchy = {"admin": 3, "moderator": 2, "user": 1}
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 1)
        
        if user_level < required_level:
            raise PermissionError(f"Role '{required_role}' required")
        
        return current_user
    
    return role_checker

def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Require admin role"""
    return require_role("admin")(current_user)

def require_moderator(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Require moderator role or higher"""
    return require_role("moderator")(current_user)

def verify_user_access(resource_user_id: str, current_user: Dict[str, Any]) -> bool:
    """Verify user can access their own resources or is admin/moderator"""
    user_role = current_user.get("role", "user")
    current_user_id = current_user.get("user_id")
    
    # Admins and moderators can access any resource
    if user_role in ["admin", "moderator"]:
        return True
    
    # Users can only access their own resources
    return str(current_user_id) == str(resource_user_id)

# Token caching utilities
def cache_user_data(user_id: str, data: Dict[str, Any], expire_seconds: int = 300):
    """Cache user data in Redis"""
    redis_client.setex(f"user_cache:{user_id}", expire_seconds, json.dumps(data, default=str))

def get_cached_user_data(user_id: str) -> Optional[Dict[str, Any]]:
    """Get cached user data from Redis"""
    cached = redis_client.get(f"user_cache:{user_id}")
    if cached:
        return json.loads(cached)
    return None

def clear_user_cache(user_id: str):
    """Clear cached user data"""
    redis_client.delete(f"user_cache:{user_id}")

# Rate limiting utilities
def check_rate_limit(key: str, limit: int, window_seconds: int) -> bool:
    """Check if rate limit is exceeded"""
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, window_seconds)
    return current <= limit

def rate_limit(key_prefix: str, limit: int = 100, window_seconds: int = 60):
    """Rate limiting decorator"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract user ID or IP from request
            request = kwargs.get('request') or (args[0] if args else None)
            if hasattr(request, 'client'):
                identifier = request.client.host
            else:
                identifier = "anonymous"
            
            key = f"rate_limit:{key_prefix}:{identifier}"
            
            if not check_rate_limit(key, limit, window_seconds):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator