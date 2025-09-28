"""
Unified Authentication System for MantraPath
Provides consistent JWT authentication across all services
"""
import jwt
import bcrypt
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security
security = HTTPBearer()

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass

class UnifiedAuth:
    """Unified authentication handler for all MantraPath services"""
    
    def __init__(self):
        self.secret_key = JWT_SECRET_KEY
        self.algorithm = JWT_ALGORITHM
        logger.info(f"🔐 UnifiedAuth initialized - Secret key length: {len(self.secret_key)}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt with 72-byte limit handling"""
        try:
            # Truncate password to 72 bytes (bcrypt limit)
            password_bytes = password.encode('utf-8')[:72]
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"❌ Password hashing error: {e}")
            raise AuthenticationError(f"Password hashing failed: {e}")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            # Truncate password to 72 bytes (bcrypt limit)
            password_bytes = plain_password.encode('utf-8')[:72]
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            logger.error(f"❌ Password verification error: {e}")
            return False
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token with consistent payload structure"""
        try:
            to_encode = data.copy()
            
            # Set expiration
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
            # Standardize token payload
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "access",
                "iss": "mantrapath-auth"
            })
            
            # Ensure sub field exists (user_id)
            if "sub" not in to_encode and "user_id" in to_encode:
                to_encode["sub"] = str(to_encode["user_id"])
            
            token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"✅ Access token created for user: {to_encode.get('sub', 'unknown')}")
            return token
            
        except Exception as e:
            logger.error(f"❌ Token creation error: {e}")
            raise AuthenticationError(f"Token creation failed: {e}")
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        try:
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "refresh",
                "iss": "mantrapath-auth"
            })
            
            # Ensure sub field exists
            if "sub" not in to_encode and "user_id" in to_encode:
                to_encode["sub"] = str(to_encode["user_id"])
            
            return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            
        except Exception as e:
            logger.error(f"❌ Refresh token creation error: {e}")
            raise AuthenticationError(f"Refresh token creation failed: {e}")
    
    def verify_token(self, token: str, expected_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token with comprehensive error handling"""
        try:
            # Log token verification attempt (first/last chars only for security)
            token_preview = f"{token[:10]}...{token[-10:]}" if len(token) > 20 else token
            logger.info(f"🔍 Verifying token: {token_preview}")
            
            # Decode and verify token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type if specified
            if expected_type and payload.get("type") != expected_type:
                logger.warning(f"❌ Token type mismatch - Expected: {expected_type}, Got: {payload.get('type')}")
                return None
            
            # Verify required fields
            if not payload.get("sub"):
                logger.warning("❌ Token missing 'sub' field")
                return None
            
            logger.info(f"✅ Token verified successfully for user: {payload.get('sub')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("❌ Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"❌ Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Token verification error: {e}")
            return None
    
    def extract_user_context(self, token: str) -> Optional[Dict[str, Any]]:
        """Extract user context from token"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "username": payload.get("username"),
            "role": payload.get("role", "user"),
            "is_verified": payload.get("is_verified", False),
            "permissions": self.get_user_permissions(payload.get("role", "user"))
        }
    
    def get_user_permissions(self, role: str) -> list:
        """Get user permissions based on role"""
        permission_map = {
            "admin": ["read", "write", "delete", "admin"],
            "moderator": ["read", "write", "moderate"],
            "user": ["read", "write_own"],
            "guest": ["read"]
        }
        return permission_map.get(role, ["read"])
    
    def require_auth(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """FastAPI dependency for required authentication"""
        try:
            token = credentials.credentials
            user_context = self.extract_user_context(token)
            
            if not user_context:
                logger.warning("❌ Authentication failed - invalid token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return user_context
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def optional_auth(self, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
        """FastAPI dependency for optional authentication"""
        if not credentials:
            return None
        
        try:
            token = credentials.credentials
            return self.extract_user_context(token)
        except Exception as e:
            logger.warning(f"⚠️ Optional auth failed: {e}")
            return None
    
    def require_role(self, required_role: str):
        """FastAPI dependency for role-based access control"""
        def role_checker(user_context: Dict[str, Any] = Depends(self.require_auth)) -> Dict[str, Any]:
            user_role = user_context.get("role", "user")
            
            # Define role hierarchy
            role_hierarchy = {"guest": 0, "user": 1, "moderator": 2, "admin": 3}
            
            user_level = role_hierarchy.get(user_role, 0)
            required_level = role_hierarchy.get(required_role, 3)
            
            if user_level < required_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required role: {required_role}"
                )
            
            return user_context
        
        return role_checker
    
    def verify_user_access(self, user_context: Dict[str, Any], resource_user_id: str) -> bool:
        """Verify user has access to a specific resource"""
        current_user_id = user_context.get("user_id")
        user_role = user_context.get("role", "user")
        
        # Admin and moderators can access any resource
        if user_role in ["admin", "moderator"]:
            return True
        
        # Users can only access their own resources
        return str(current_user_id) == str(resource_user_id)

# Create global instance
auth = UnifiedAuth()

# Export commonly used functions for backward compatibility
def hash_password(password: str) -> str:
    return auth.hash_password(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return auth.verify_password(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    return auth.create_access_token(data, expires_delta)

def create_refresh_token(data: Dict[str, Any]) -> str:
    return auth.create_refresh_token(data)

def verify_token(token: str, expected_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    return auth.verify_token(token, expected_type)

# FastAPI Dependencies
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    return auth.require_auth(credentials)

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    return auth.optional_auth(credentials)

def require_admin(user_context: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    return auth.require_role("admin")(user_context)

def require_moderator(user_context: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    return auth.require_role("moderator")(user_context)