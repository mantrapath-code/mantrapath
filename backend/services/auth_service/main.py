"""
Auth Service - Authentication, authorization, and user management
"""

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
from pydantic import BaseModel, EmailStr, UUID4, Field
import json
import redis

# Import shared modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.database import get_db
from shared.auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    verify_token, blacklist_token, get_current_user, require_admin,
    cache_user_data, clear_user_cache
)
from shared.models import User, UserProfile

app = FastAPI(
    title="MantraPath Auth Service",
    description="Authentication, authorization, and user management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for caching and sessions
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)

class UserResponse(BaseModel):
    id: UUID4
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None

# Core authentication endpoints
@app.post("/register", response_model=LoginResponse)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = hash_password(user_data.password)
    user = User(
        id=uuid.uuid4(),
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_verified=False,  # Require email verification
        role="user"
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create default profile
    profile = UserProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        theme="light",
        privacy_level="private",
        email_notifications=True,
        push_notifications=True,
        mood_reminders=True,
        weekly_reports=True
    )
    
    db.add(profile)
    db.commit()
    
    # Generate tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
        "is_active": user.is_active
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Cache user data
    cache_user_data(str(user.id), {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active
    })
    
    # Send verification email in background
    background_tasks.add_task(send_verification_email, user.email, str(user.id))
    
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        role=user.role,
        created_at=user.created_at
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=30 * 60,  # 30 minutes
        user=user_response
    )

@app.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login user"""
    
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Account is deactivated"
        )
    
    # Generate tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
        "is_active": user.is_active
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Cache user data
    cache_user_data(str(user.id), {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active
    })
    
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        role=user.role,
        created_at=user.created_at
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=30 * 60,  # 30 minutes
        user=user_response
    )

@app.post("/logout")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """Logout user (blacklist current token)"""
    
    # Blacklist the token
    blacklist_token(token)
    
    # Clear user cache
    clear_user_cache(current_user["user_id"])
    
    return {"message": "Successfully logged out"}

@app.post("/logout-all")
async def logout_all_devices(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout from all devices"""
    
    # In a real implementation, you'd track all user tokens
    # For now, just clear the user cache
    clear_user_cache(current_user["user_id"])
    
    return {"message": "Successfully logged out from all devices"}

@app.post("/refresh-token", response_model=TokenResponse)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    
    # Verify refresh token
    try:
        payload = verify_token(refresh_data.refresh_token, "refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        # Generate new access token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
            "is_active": user.is_active
        }
        
        access_token = create_access_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=30 * 60
        )
    
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.post("/revoke-token")
async def revoke_refresh_token(
    refresh_data: RefreshTokenRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Revoke refresh token"""
    
    # Blacklist the refresh token
    blacklist_token(refresh_data.refresh_token)
    
    return {"message": "Refresh token revoked successfully"}

@app.post("/validate")
async def validate_token(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Validate current token and return user info"""
    return {
        "valid": True,
        "user": current_user
    }

# User management endpoints
@app.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        role=user.role,
        created_at=user.created_at
    )

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID4,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user by ID (own profile or admin only)"""
    
    # Users can only view their own profile unless they're admin
    if str(user_id) != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        role=user.role,
        created_at=user.created_at
    )

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID4,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user (own profile or admin only)"""
    
    # Users can only update their own profile unless they're admin
    if str(user_id) != current_user["user_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Regular users can only update their name
    if current_user["role"] != "admin":
        if user_update.is_active is not None or user_update.role is not None:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Update user fields
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    
    if user_update.is_active is not None and current_user["role"] == "admin":
        user.is_active = user_update.is_active
    
    if user_update.role is not None and current_user["role"] == "admin":
        user.role = user_update.role
    
    db.commit()
    db.refresh(user)
    
    # Clear user cache
    clear_user_cache(str(user.id))
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        role=user.role,
        created_at=user.created_at
    )

@app.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Change user password"""
    
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not verify_password(password_data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    user.hashed_password = hash_password(password_data.new_password)
    db.commit()
    
    # Clear user cache to force re-authentication
    clear_user_cache(current_user["user_id"])
    
    return {"message": "Password changed successfully"}

# Password reset endpoints
@app.post("/password-reset/request")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    
    user = db.query(User).filter(User.email == reset_request.email).first()
    
    # Don't reveal if email exists or not
    message = "If the email address is registered, you will receive password reset instructions."
    
    if user:
        # Generate reset token
        reset_token = create_access_token(
            {"sub": str(user.id), "purpose": "password_reset"},
            expires_delta=timedelta(hours=1)  # 1 hour expiry
        )
        
        # Send reset email in background
        background_tasks.add_task(
            send_password_reset_email, 
            user.email, 
            reset_token
        )
    
    return {"message": message}

@app.post("/password-reset/confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Confirm password reset with token"""
    
    try:
        # Verify reset token
        payload = verify_token(reset_data.token)
        user_id = payload.get("sub")
        purpose = payload.get("purpose")
        
        if not user_id or purpose != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid reset token")
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        
        # Update password
        user.hashed_password = hash_password(reset_data.new_password)
        db.commit()
        
        # Clear user cache
        clear_user_cache(str(user.id))
        
        return {"message": "Password reset successfully"}
    
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

# Admin endpoints
@app.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    role: Optional[str] = None,
    active_only: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Get all users (admin only)"""
    
    query = db.query(User)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%")
            )
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if active_only is not None:
        query = query.filter(User.is_active == active_only)
    
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            role=user.role,
            created_at=user.created_at
        )
        for user in users
    ]

@app.post("/admin/users", response_model=UserResponse)
async def create_user_admin(
    user_data: UserCreate,
    role: str = "user",
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Create user (admin only)"""
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        id=uuid.uuid4(),
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        is_verified=True,  # Admin-created users are auto-verified
        role=role
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        role=user.role,
        created_at=user.created_at
    )

# Background tasks
async def send_verification_email(email: str, user_id: str):
    """Send email verification (placeholder)"""
    print(f"📧 Sending verification email to {email} for user {user_id}")
    # In real implementation: send email via SendGrid, SES, etc.

async def send_password_reset_email(email: str, reset_token: str):
    """Send password reset email (placeholder)"""
    print(f"📧 Sending password reset email to {email}")
    print(f"🔗 Reset link: /reset-password?token={reset_token}")
    # In real implementation: send email with reset link

# Health check
@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "auth_service",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)