"""
Authentication Service - Handles user registration, login, and token management
"""
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, Union
import sys
import os
import asyncio
import threading
import uuid
from datetime import datetime, timedelta

# Add parent directories to path
sys.path.append('/app')
sys.path.append('/app/shared')

from shared.database import get_db, engine
from shared.models import User, UserProfile, Base
from shared.user_display import get_user_display_name, format_user_for_api
from shared.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    get_current_user,
    validate_password_strength,
    generate_verification_token,
    send_verification_email
)

# Create tables
Base.metadata.create_all(bind=engine)

# Check if email verification should be skipped (for local development)
SKIP_EMAIL_VERIFICATION = os.getenv("SKIP_EMAIL_VERIFICATION", "false").lower() == "true"

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
    first_name: str  # Required field
    last_name: str   # Required field

class UserLogin(BaseModel):
    email_or_username: str  # Can be either email or username
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: str
    username: str  # Keep for backward compatibility but won't be displayed
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    role: str
    display_name: str  # Unique 5-character identifier
    initials: str      # 2-character initials

class VerificationRequest(BaseModel):
    token: str

class RegistrationResponse(BaseModel):
    message: str
    user_id: str
    verification_required: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = None

# Cleanup function for unverified accounts
def cleanup_unverified_accounts():
    """Remove unverified accounts older than 5 minutes"""
    try:
        from shared.database import SessionLocal
        from shared.models import JournalEntry, MoodEntry, ChatSession, ChatMessage
        db = SessionLocal()
        
        # Calculate cutoff time (5 minutes ago)
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        
        # Find unverified accounts older than 5 minutes
        expired_users = db.query(User).filter(
            User.is_verified == False,
            User.created_at < cutoff_time
        ).all()
        
        if expired_users:
            print(f"🧹 Cleaning up {len(expired_users)} unverified accounts older than 5 minutes")
            
            for user in expired_users:
                try:
                    # Delete all related data first (to handle foreign key constraints)
                    
                    # Delete chat messages first (they reference chat sessions)
                    chat_sessions = db.query(ChatSession).filter(ChatSession.user_id == user.id).all()
                    for session in chat_sessions:
                        chat_messages = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).all()
                        for message in chat_messages:
                            db.delete(message)
                        db.delete(session)
                    
                    # Delete journal entries
                    journal_entries = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).all()
                    for entry in journal_entries:
                        db.delete(entry)
                    
                    # Delete mood entries
                    mood_entries = db.query(MoodEntry).filter(MoodEntry.user_id == user.id).all()
                    for entry in mood_entries:
                        db.delete(entry)
                    
                    # Delete associated profile
                    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
                    if profile:
                        db.delete(profile)
                    
                    # Finally delete user
                    db.delete(user)
                    print(f"   Removed unverified account: {user.email}")
                    
                except Exception as e:
                    print(f"   ❌ Error removing account {user.email}: {e}")
                    db.rollback()
            
            db.commit()
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

async def periodic_cleanup():
    """Run cleanup every 5 minutes"""
    while True:
        cleanup_unverified_accounts()
        await asyncio.sleep(300)  # 5 minutes

# Start cleanup task in background
@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup"""
    print("🚀 Starting MantraPath Auth Service")
    print("🧹 Starting periodic cleanup for unverified accounts (every 5 minutes)")
    
    # Start cleanup task in background thread
    def run_cleanup():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(periodic_cleanup())
    
    cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
    cleanup_thread.start()

# Auth endpoints
@app.post("/register", response_model=RegistrationResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user with email verification"""
    
    # Validate password strength
    is_valid, error_message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        if existing_user.is_verified:
            # Verified user exists - cannot register again
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered and verified"
            )
        else:
            # Unverified user exists - check if it's recent (within 5 minutes)
            time_since_creation = datetime.utcnow() - existing_user.created_at
            if time_since_creation < timedelta(minutes=5):
                # Too recent - user must wait
                remaining_minutes = 5 - int(time_since_creation.total_seconds() / 60)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Please wait {remaining_minutes} more minute(s) before trying to register again, or check your email for the verification link."
                )
            else:
                # Old unverified account - remove it and allow re-registration
                print(f"🔄 Removing old unverified account for {user_data.email}")
                
                try:
                    # Delete all related data first (to handle foreign key constraints)
                    from shared.models import JournalEntry, MoodEntry, ChatSession, ChatMessage
                    
                    # Delete chat messages first (they reference chat sessions)
                    chat_sessions = db.query(ChatSession).filter(ChatSession.user_id == existing_user.id).all()
                    for session in chat_sessions:
                        chat_messages = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).all()
                        for message in chat_messages:
                            db.delete(message)
                        db.delete(session)
                    
                    # Delete journal entries
                    journal_entries = db.query(JournalEntry).filter(JournalEntry.user_id == existing_user.id).all()
                    for entry in journal_entries:
                        db.delete(entry)
                    
                    # Delete mood entries
                    mood_entries = db.query(MoodEntry).filter(MoodEntry.user_id == existing_user.id).all()
                    for entry in mood_entries:
                        db.delete(entry)
                    
                    # Delete associated profile
                    profile = db.query(UserProfile).filter(UserProfile.user_id == existing_user.id).first()
                    if profile:
                        db.delete(profile)
                    
                    # Delete user
                    db.delete(existing_user)
                    db.commit()
                    
                except Exception as e:
                    print(f"❌ Error removing old account: {e}")
                    db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Error removing old account. Please try again."
                    )

    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Generate verification token (only if email verification is not skipped)
    verification_token = None
    verification_expires = None
    is_verified = SKIP_EMAIL_VERIFICATION  # Skip verification if flag is set
    
    if not SKIP_EMAIL_VERIFICATION:
        verification_token = generate_verification_token()
        verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_verified=is_verified,
        verification_token=verification_token,
        verification_token_expires=verification_expires
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create profile
        profile = UserProfile(
            user_id=db_user.id
        )
        
        db.add(profile)
        db.commit()
        
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            if "username" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            elif "email" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )
    
    # Send verification email (only if email verification is not skipped)
    verification_required = not SKIP_EMAIL_VERIFICATION
    message = "Registration successful!"
    
    if not SKIP_EMAIL_VERIFICATION:
        user_display_name = f"{db_user.first_name} {db_user.last_name}".strip() or db_user.username
        email_sent = send_verification_email(
            db_user.email, 
            verification_token, 
            user_display_name
        )
        message = "Registration successful! Please check your email to verify your account."
        
        return RegistrationResponse(
            message=message,
            user_id=str(db_user.id),
            verification_required=verification_required
        )
    else:
        message = "Registration successful! You are now logged in."
        
        # Create tokens for immediate login when verification is skipped
        access_token = create_access_token(data={
            "sub": str(db_user.id),
            "email": db_user.email,
            "role": db_user.role
        })
        refresh_token = create_refresh_token(data={"sub": str(db_user.id)})
        
        # Return tokens in the response for immediate login
        return {
            "message": message,
            "user_id": str(db_user.id),
            "verification_required": verification_required,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

@app.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user with email or username"""
    
    # Try to find user by email or username
    user = db.query(User).filter(
        (User.email == user_data.email_or_username) | 
        (User.username == user_data.email_or_username)
    ).first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Only check email verification if not skipped
    if not SKIP_EMAIL_VERIFICATION and not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your email before logging in. Check your email for verification link."
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token, refresh_token=refresh_token)

@app.post("/verify-email")
async def verify_email(verification_data: VerificationRequest, db: Session = Depends(get_db)):
    """Verify user's email address"""
    
    user = db.query(User).filter(
        User.verification_token == verification_data.token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    if user.verification_token_expires and user.verification_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired. Please register again."
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Verify the user
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    db.commit()
    
    return {"message": "Email verified successfully! You can now log in."}

@app.post("/resend-verification")
async def resend_verification(email_data: dict, db: Session = Depends(get_db)):
    """Resend verification email"""
    
    email = email_data.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Generate new verification token
    verification_token = generate_verification_token()
    verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    user.verification_token = verification_token
    user.verification_token_expires = verification_expires
    db.commit()
    
    # Send verification email
    email_sent = send_verification_email(
        user.email, 
        verification_token, 
        user.username or user.first_name or "User"
    )
    
    if email_sent:
        return {"message": "Verification email sent successfully"}
    else:
        return {"message": "Verification email could not be sent. Please contact support."}

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
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    
    # Get user from database
    db = next(get_db())
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
async def get_current_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user information"""
    
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        first_name=user.first_name or "",
        last_name=user.last_name or "",
        is_active=user.is_active,
        is_verified=user.is_verified,
        role=user.role,
        display_name=get_user_display_name(user),
        initials=get_user_display_name(user)[:2]
    )

@app.post("/logout")
async def logout():
    """Logout user (token invalidation handled client-side)"""
    return {"message": "Successfully logged out"}

@app.post("/dev/login")
async def dev_login(db: Session = Depends(get_db)):
    """Development login endpoint - creates/logs in test user without email verification"""
    import os
    
    # Only allow in development mode
    if os.getenv("ENVIRONMENT", "development") == "production":
        raise HTTPException(status_code=404, detail="Not found")
    
    # Check for existing test user
    user = db.query(User).filter(
        (User.email == "testuser@mantrapath.com") | (User.username == "testuser")
    ).first()
    
    if not user:
        # Create test user
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email="testuser@mantrapath.com",
            username="testuser",
            password_hash=get_password_hash("TestPassword123!"),
            first_name="Test",
            last_name="User",
            is_active=True,
            is_verified=True,  # Skip email verification
            role="user"
        )
        db.add(user)
        
        # Create profile
        from shared.models import UserProfile
        profile = UserProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            bio="Development test user",
            timezone="UTC"
        )
        db.add(profile)
        db.commit()
    else:
        # Ensure user is verified and active
        user.is_verified = True
        user.is_active = True
        db.commit()
    
    # Generate tokens
    access_token = create_access_token(data={
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token, refresh_token=refresh_token)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)