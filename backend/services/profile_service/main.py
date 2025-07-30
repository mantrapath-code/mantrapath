"""
Profile Service - User profiles, preferences, and settings management
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Dict, Any, List
from datetime import datetime, date
import uuid
from pydantic import BaseModel, UUID4, Field
import redis

# Import shared modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.database import get_db
from shared.auth import get_current_user, verify_user_access
from shared.models import User, UserProfile

app = FastAPI(
    title="MantraPath Profile Service",
    description="User profiles, preferences, and settings management", 
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for caching
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Pydantic models
class ProfileResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    bio: Optional[str]
    avatar_url: Optional[str]
    timezone: str
    date_of_birth: Optional[date]
    location: Optional[str]
    theme: str
    privacy_level: str
    created_at: datetime
    updated_at: datetime

class ProfileUpdate(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    date_of_birth: Optional[date] = None
    location: Optional[str] = None

class PreferencesResponse(BaseModel):
    email_notifications: bool
    push_notifications: bool
    mood_reminders: bool
    weekly_reports: bool

class PreferencesUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    mood_reminders: Optional[bool] = None
    weekly_reports: Optional[bool] = None

class ThemePreferences(BaseModel):
    theme: str = Field(..., pattern="^(light|dark|auto)$")

class PrivacyPreferences(BaseModel):
    privacy_level: str = Field(..., pattern="^(public|friends|private)$")

class ProfileCreate(BaseModel):
    bio: Optional[str] = None
    timezone: str = "UTC"
    theme: str = "light"
    privacy_level: str = "private"

class UserInfo(BaseModel):
    id: UUID4
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool

class ProfileSearchResult(BaseModel):
    user: UserInfo
    profile: ProfileResponse

# Profile management endpoints
@app.get("/api/profiles/me", response_model=ProfileResponse)
async def get_my_profile(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get current user's profile"""
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["user_id"]
    ).first()
    
    if not profile:
        # Create default profile if it doesn't exist
        profile = UserProfile(
            id=uuid.uuid4(),
            user_id=current_user["user_id"],
            timezone="UTC",
            theme="light",
            privacy_level="private",
            email_notifications=True,
            push_notifications=True,
            mood_reminders=True,
            weekly_reports=True
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        bio=profile.bio,
        avatar_url=profile.avatar_url,
        timezone=profile.timezone,
        date_of_birth=profile.date_of_birth,
        location=profile.location,
        theme=profile.theme,
        privacy_level=profile.privacy_level,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

@app.get("/api/profiles/{profile_id}", response_model=ProfileResponse)
async def get_profile_by_id(
    profile_id: UUID4,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get profile by ID (respects privacy settings)"""
    
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Check privacy permissions
    if profile.privacy_level == "private":
        if not verify_user_access(str(profile.user_id), current_user):
            raise HTTPException(status_code=403, detail="Profile is private")
    
    # For public and friends levels, show limited info unless it's the owner
    is_owner = str(profile.user_id) == current_user["user_id"]
    
    if not is_owner and profile.privacy_level != "public":
        # Return limited profile info
        return ProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            bio=None,  # Hide bio for non-public profiles
            avatar_url=profile.avatar_url,
            timezone=profile.timezone,
            date_of_birth=None,  # Hide birthday
            location=None,  # Hide location
            theme=profile.theme,
            privacy_level=profile.privacy_level,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
    
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        bio=profile.bio,
        avatar_url=profile.avatar_url,
        timezone=profile.timezone,
        date_of_birth=profile.date_of_birth,
        location=profile.location,
        theme=profile.theme,
        privacy_level=profile.privacy_level,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

@app.post("/api/profiles/", response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create profile for current user"""
    
    # Check if profile already exists
    existing_profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["user_id"]
    ).first()
    
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")
    
    # Create new profile
    profile = UserProfile(
        id=uuid.uuid4(),
        user_id=current_user["user_id"],
        bio=profile_data.bio,
        timezone=profile_data.timezone,
        theme=profile_data.theme,
        privacy_level=profile_data.privacy_level,
        email_notifications=True,
        push_notifications=True,
        mood_reminders=True,
        weekly_reports=True
    )
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        bio=profile.bio,
        avatar_url=profile.avatar_url,
        timezone=profile.timezone,
        date_of_birth=profile.date_of_birth,
        location=profile.location,
        theme=profile.theme,
        privacy_level=profile.privacy_level,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

@app.patch("/api/profiles/", response_model=ProfileResponse)
async def update_my_profile(
    profile_update: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update current user's profile"""
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["user_id"]
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update fields
    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    
    # Clear any cached profile data
    redis_client.delete(f"profile_cache:{current_user['user_id']}")
    
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        bio=profile.bio,
        avatar_url=profile.avatar_url,
        timezone=profile.timezone,
        date_of_birth=profile.date_of_birth,
        location=profile.location,
        theme=profile.theme,
        privacy_level=profile.privacy_level,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

@app.delete("/api/profiles/")
async def delete_my_profile(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete current user's profile"""
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["user_id"]
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db.delete(profile)
    db.commit()
    
    # Clear cached data
    redis_client.delete(f"profile_cache:{current_user['user_id']}")
    
    return {"message": "Profile deleted successfully"}

# Preferences endpoints
@app.get("/api/preferences/", response_model=PreferencesResponse)
async def get_preferences(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user preferences"""
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["user_id"]
    ).first()
    
    if not profile:
        # Return default preferences
        return PreferencesResponse(
            email_notifications=True,
            push_notifications=True,
            mood_reminders=True,
            weekly_reports=True
        )
    
    return PreferencesResponse(
        email_notifications=profile.email_notifications,
        push_notifications=profile.push_notifications,
        mood_reminders=profile.mood_reminders,
        weekly_reports=profile.weekly_reports
    )

@app.patch("/api/preferences/", response_model=PreferencesResponse)
async def update_preferences(
    preferences_update: PreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user preferences"""
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["user_id"]
    ).first()
    
    if not profile:
        # Create profile with preferences
        profile = UserProfile(
            id=uuid.uuid4(),
            user_id=current_user["user_id"],
            timezone="UTC",
            theme="light",
            privacy_level="private"
        )
        db.add(profile)
    
    # Update preferences
    update_data = preferences_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    
    return PreferencesResponse(
        email_notifications=profile.email_notifications,
        push_notifications=profile.push_notifications,
        mood_reminders=profile.mood_reminders,
        weekly_reports=profile.weekly_reports
    )

# Theme preferences
@app.get("/api/preferences/theme")
async def get_theme_preferences(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get theme preferences"""
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["user_id"]
    ).first()
    
    theme = profile.theme if profile else "light"
    
    return {"theme": theme}

@app.patch("/api/preferences/theme")
async def update_theme_preferences(
    theme_update: ThemePreferences,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update theme preferences"""
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["user_id"]
    ).first()
    
    if not profile:
        # Create profile with theme
        profile = UserProfile(
            id=uuid.uuid4(),
            user_id=current_user["user_id"],
            timezone="UTC",
            theme=theme_update.theme,
            privacy_level="private",
            email_notifications=True,
            push_notifications=True,
            mood_reminders=True,
            weekly_reports=True
        )
        db.add(profile)
    else:
        profile.theme = theme_update.theme
        profile.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Theme updated successfully", "theme": theme_update.theme}

# Privacy preferences
@app.get("/api/preferences/privacy")
async def get_privacy_preferences(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get privacy preferences"""
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["user_id"]
    ).first()
    
    privacy_level = profile.privacy_level if profile else "private"
    
    return {"privacy_level": privacy_level}

@app.patch("/api/preferences/privacy")
async def update_privacy_preferences(
    privacy_update: PrivacyPreferences,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update privacy preferences"""
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["user_id"]
    ).first()
    
    if not profile:
        # Create profile with privacy setting
        profile = UserProfile(
            id=uuid.uuid4(),
            user_id=current_user["user_id"],
            timezone="UTC",
            theme="light",
            privacy_level=privacy_update.privacy_level,
            email_notifications=True,
            push_notifications=True,
            mood_reminders=True,
            weekly_reports=True
        )
        db.add(profile)
    else:
        profile.privacy_level = privacy_update.privacy_level
        profile.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Privacy settings updated successfully", 
        "privacy_level": privacy_update.privacy_level
    }

# Profile search and discovery
@app.get("/api/profiles/search", response_model=List[ProfileSearchResult])
async def search_profiles(
    q: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Search public profiles"""
    
    # Only search public profiles
    profiles = db.query(UserProfile, User).join(User).filter(
        and_(
            UserProfile.privacy_level == "public",
            User.is_active == True,
            User.full_name.ilike(f"%{q}%")
        )
    ).offset(skip).limit(limit).all()
    
    results = []
    for profile, user in profiles:
        results.append(ProfileSearchResult(
            user=UserInfo(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified
            ),
            profile=ProfileResponse(
                id=profile.id,
                user_id=profile.user_id,
                bio=profile.bio,
                avatar_url=profile.avatar_url,
                timezone=profile.timezone,
                date_of_birth=None,  # Don't expose birthday in search
                location=profile.location,
                theme=profile.theme,
                privacy_level=profile.privacy_level,
                created_at=profile.created_at,
                updated_at=profile.updated_at
            )
        ))
    
    return results

# Profile statistics
@app.get("/api/profiles/stats")
async def get_profile_stats(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get profile completion and statistics"""
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["user_id"]
    ).first()
    
    if not profile:
        return {
            "completion_percentage": 20,  # Just basic account creation
            "missing_fields": ["bio", "avatar", "location", "date_of_birth"],
            "profile_views": 0,
            "last_updated": None
        }
    
    # Calculate completion percentage
    total_fields = 6  # bio, avatar, timezone, location, date_of_birth, theme
    completed_fields = 1  # timezone is always set
    
    if profile.bio:
        completed_fields += 1
    if profile.avatar_url:
        completed_fields += 1
    if profile.location:
        completed_fields += 1
    if profile.date_of_birth:
        completed_fields += 1
    if profile.theme:
        completed_fields += 1
    
    completion_percentage = (completed_fields / total_fields) * 100
    
    # Identify missing fields
    missing_fields = []
    if not profile.bio:
        missing_fields.append("bio")
    if not profile.avatar_url:
        missing_fields.append("avatar")
    if not profile.location:
        missing_fields.append("location")
    if not profile.date_of_birth:
        missing_fields.append("date_of_birth")
    
    return {
        "completion_percentage": round(completion_percentage, 1),
        "missing_fields": missing_fields,
        "profile_views": 0,  # Would be tracked separately
        "last_updated": profile.updated_at.isoformat() if profile.updated_at else None
    }

# Health check
@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "profile_service",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)