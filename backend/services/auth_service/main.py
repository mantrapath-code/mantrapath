"""
Authentication Service - Handles user registration, login, and token management
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import sys
import os

# Add parent directories to path
sys.path.append('/app')
sys.path.append('/app/shared')

from shared.database import get_database, engine
from shared.models import User, UserProfile, Base
from shared.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    get_current_user
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MantraPath Auth Service",
    description="Authentication and user management service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    role: str

# Auth endpoints
@app.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_database)):
    """Register new user"""
    
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        is_verified=True  # Auto-verify for demo
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create profile
    profile = UserProfile(
        user_id=db_user.id,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    
    db.add(profile)
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={
        "sub": str(db_user.id),
        "email": db_user.email,
        "role": db_user.role
    })
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})
    
    return Token(access_token=access_token, refresh_token=refresh_token)

@app.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_database)):
    """Login user"""
    
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Create tokens
    access_token = create_access_token(data={
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token, refresh_token=refresh_token)

@app.post("/refresh-token", response_model=Token)
async def refresh_token(token_data: dict):
    """Refresh access token"""
    
    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token required"
        )
    
    # Verify refresh token
    payload = verify_token(refresh_token, "refresh")
    user_id = payload.get("sub")
    
    # Get user from database
    db = next(get_database())
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Create new tokens
    access_token = create_access_token(data={
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token, refresh_token=new_refresh_token)

@app.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_database)):
    """Get current user information"""
    
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        role=user.role
    )

@app.post("/logout")
async def logout():
    """Logout user (token invalidation handled client-side)"""
    return {"message": "Successfully logged out"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)