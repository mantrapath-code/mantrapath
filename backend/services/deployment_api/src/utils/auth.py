"""
Authentication utilities for frontend engineers
"""

import jwt
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.permissions import get_engineer_permissions, check_permission


class FrontendEngineerAuth:
    """Frontend engineer authentication service"""
    
    def __init__(self):
        self.secret_key = "your-secret-key-change-in-production"
        self.algorithm = "HS256"
        self.token_expire_minutes = 60
        
        # Mock engineer database (in production, this would be a real database)
        self.engineers_db = {
            "fe_001": {
                "id": "fe_001",
                "name": "Frontend Engineer 1",
                "email": "fe1@example.com",
                "permission_level": "enhanced",
                "created_at": "2024-01-01T00:00:00Z",
                "last_active": "2024-01-01T00:00:00Z"
            },
            "fe_002": {
                "id": "fe_002",
                "name": "Frontend Engineer 2",
                "email": "fe2@example.com",
                "permission_level": "basic",
                "created_at": "2024-01-01T00:00:00Z",
                "last_active": "2024-01-01T00:00:00Z"
            },
            "fe_003": {
                "id": "fe_003",
                "name": "Frontend Engineer 3",
                "email": "fe3@example.com",
                "permission_level": "premium",
                "created_at": "2024-01-01T00:00:00Z",
                "last_active": "2024-01-01T00:00:00Z"
            }
        }
    
    async def authenticate(self, token: str) -> Dict[str, Any]:
        """Authenticate a frontend engineer using JWT token"""
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            engineer_id = payload.get("sub")
            if not engineer_id:
                raise ValueError("Invalid token: missing subject")
            
            # Check if engineer exists
            engineer = self.engineers_db.get(engineer_id)
            if not engineer:
                raise ValueError("Invalid token: engineer not found")
            
            # Check token expiration
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise ValueError("Token expired")
            
            # Get permissions for the engineer
            permissions = get_engineer_permissions(engineer_id)
            
            # Update last active timestamp
            engineer["last_active"] = datetime.utcnow().isoformat() + "Z"
            
            return {
                "id": engineer_id,
                "name": engineer["name"],
                "email": engineer["email"],
                "permission_level": engineer["permission_level"],
                "permissions": permissions,
                "authenticated_at": datetime.utcnow().isoformat() + "Z"
            }
            
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}")
        except Exception as e:
            raise ValueError(f"Authentication failed: {e}")
    
    async def create_token(self, engineer_id: str) -> str:
        """Create a JWT token for a frontend engineer"""
        try:
            # Check if engineer exists
            if engineer_id not in self.engineers_db:
                raise ValueError("Engineer not found")
            
            # Create token payload
            payload = {
                "sub": engineer_id,
                "exp": datetime.utcnow() + timedelta(minutes=self.token_expire_minutes),
                "iat": datetime.utcnow(),
                "type": "frontend_engineer"
            }
            
            # Generate JWT token
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
            
        except Exception as e:
            raise ValueError(f"Failed to create token: {e}")
    
    async def validate_permission(self, engineer_id: str, required_permission: str) -> bool:
        """Validate if an engineer has the required permission"""
        return check_permission(engineer_id, required_permission)
    
    async def get_engineer_info(self, engineer_id: str) -> Optional[Dict[str, Any]]:
        """Get engineer information"""
        return self.engineers_db.get(engineer_id)
    
    async def update_engineer_activity(self, engineer_id: str) -> None:
        """Update engineer's last activity timestamp"""
        if engineer_id in self.engineers_db:
            self.engineers_db[engineer_id]["last_active"] = datetime.utcnow().isoformat() + "Z"
    
    async def list_engineers(self) -> list:
        """List all frontend engineers (for admin purposes)"""
        return list(self.engineers_db.values())
    
    async def add_engineer(self, engineer_data: Dict[str, Any]) -> str:
        """Add a new frontend engineer"""
        engineer_id = f"fe_{len(self.engineers_db) + 1:03d}"
        
        self.engineers_db[engineer_id] = {
            "id": engineer_id,
            "name": engineer_data.get("name", "Unknown"),
            "email": engineer_data.get("email", ""),
            "permission_level": engineer_data.get("permission_level", "basic"),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "last_active": datetime.utcnow().isoformat() + "Z"
        }
        
        return engineer_id
    
    async def update_engineer_permissions(self, engineer_id: str, permission_level: str) -> bool:
        """Update engineer's permission level"""
        if engineer_id in self.engineers_db:
            self.engineers_db[engineer_id]["permission_level"] = permission_level
            return True
        return False
    
    async def remove_engineer(self, engineer_id: str) -> bool:
        """Remove a frontend engineer"""
        if engineer_id in self.engineers_db:
            del self.engineers_db[engineer_id]
            return True
        return False
