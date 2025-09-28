"""
Enhanced Authentication Middleware for API Gateway
Uses the unified authentication system for consistent JWT handling
"""
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import sys
import os

# Add shared directory to path
sys.path.append('/app/shared')

try:
    from auth_unified import UnifiedAuth, AuthenticationError
except ImportError:
    # Fallback to old auth system if unified not available
    from auth import verify_token
    UnifiedAuth = None
    AuthenticationError = Exception

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthMiddleware:
    """Enhanced authentication middleware using unified auth system"""
    
    def __init__(self):
        if UnifiedAuth:
            self.auth = UnifiedAuth()
            self.use_unified = True
            logger.info("🚀 Using unified authentication system")
        else:
            self.use_unified = False
            logger.warning("⚠️ Falling back to legacy authentication system")
        
        self.security = HTTPBearer()
    
    def extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request headers"""
        try:
            authorization = request.headers.get("Authorization")
            if not authorization:
                return None
            
            if not authorization.startswith("Bearer "):
                return None
            
            return authorization[7:]  # Remove "Bearer " prefix
            
        except Exception as e:
            logger.error(f"❌ Token extraction error: {e}")
            return None
    
    def authenticate_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """Authenticate request and return user context"""
        try:
            # Extract token from request
            token = self.extract_token(request)
            if not token:
                logger.warning("❌ No token found in request")
                return None
            
            # Use unified auth system if available
            if self.use_unified:
                return self._authenticate_unified(token)
            else:
                return self._authenticate_legacy(token)
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return None
    
    def _authenticate_unified(self, token: str) -> Optional[Dict[str, Any]]:
        """Authenticate using unified auth system"""
        try:
            user_context = self.auth.extract_user_context(token)
            if user_context:
                logger.info(f"✅ Unified auth success for user: {user_context.get('user_id')}")
                return user_context
            
            logger.warning("❌ Unified auth failed - invalid token")
            return None
            
        except Exception as e:
            logger.error(f"❌ Unified auth error: {e}")
            return None
    
    def _authenticate_legacy(self, token: str) -> Optional[Dict[str, Any]]:
        """Authenticate using legacy auth system"""
        try:
            payload = verify_token(token)
            if not payload:
                logger.warning("❌ Legacy auth failed - invalid token")
                return None
            
            # Convert legacy payload to unified format
            user_context = {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "username": payload.get("username"),
                "role": payload.get("role", "user"),
                "is_verified": payload.get("is_verified", False),
                "permissions": ["read", "write_own"]  # Default permissions
            }
            
            logger.info(f"✅ Legacy auth success for user: {user_context.get('user_id')}")
            return user_context
            
        except Exception as e:
            logger.error(f"❌ Legacy auth error: {e}")
            return None
    
    def require_authentication(self, request: Request) -> Dict[str, Any]:
        """Require authentication and return user context or raise HTTPException"""
        user_context = self.authenticate_request(request)
        
        if not user_context:
            logger.warning("❌ Authentication required but failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_context
    
    def check_permissions(self, user_context: Dict[str, Any], required_permission: str) -> bool:
        """Check if user has required permission"""
        user_permissions = user_context.get("permissions", [])
        user_role = user_context.get("role", "user")
        
        # Admin has all permissions
        if user_role == "admin":
            return True
        
        # Check specific permissions
        if required_permission in user_permissions:
            return True
        
        logger.warning(f"❌ Permission denied - Required: {required_permission}, User has: {user_permissions}")
        return False
    
    def verify_resource_access(self, user_context: Dict[str, Any], resource_user_id: str) -> bool:
        """Verify user can access specific resource"""
        current_user_id = user_context.get("user_id")
        user_role = user_context.get("role", "user")
        
        # Admin and moderators can access any resource
        if user_role in ["admin", "moderator"]:
            return True
        
        # Users can only access their own resources
        return str(current_user_id) == str(resource_user_id)

# Create global middleware instance
auth_middleware = AuthMiddleware()

def get_auth_middleware() -> AuthMiddleware:
    """Get the global auth middleware instance"""
    return auth_middleware

# Helper functions for backward compatibility
def authenticate_user_from_request(request: Request) -> Optional[Dict[str, Any]]:
    """Authenticate user from request - returns None if auth fails"""
    return auth_middleware.authenticate_request(request)

def require_authentication_from_request(request: Request) -> Dict[str, Any]:
    """Require authentication from request - raises HTTPException if auth fails"""
    return auth_middleware.require_authentication(request)

def extract_token_from_request(request: Request) -> Optional[str]:
    """Extract token from request headers"""
    return auth_middleware.extract_token(request)