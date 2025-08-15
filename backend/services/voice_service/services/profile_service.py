"""
Voice Profile Service
Manages user voice profiles, preferences, and voice cloning data
"""
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from core.models import VoiceProfile, VoicePreferences, VoiceResponse, AudioData
from core.exceptions import VoiceProfileError, VoiceServiceError, AuthenticationError
from config.settings import voice_config

logger = logging.getLogger(__name__)

class VoiceProfileService:
    """Service for managing user voice profiles and preferences"""
    
    def __init__(self):
        # In-memory storage for demo - in production use database
        self.voice_profiles: Dict[str, VoiceProfile] = {}
        self.user_preferences: Dict[str, VoicePreferences] = {}
        self.voice_samples: Dict[str, List[AudioData]] = {}
        self.profile_stats = {
            "total_profiles": 0,
            "active_profiles": 0,
            "voice_clones_created": 0,
            "preferences_updated": 0
        }
    
    async def create_voice_profile(
        self,
        user_id: str,
        profile_name: str,
        language: str = "en",
        voice_samples: Optional[List[AudioData]] = None,
        **metadata
    ) -> VoiceResponse:
        """Create a new voice profile for a user"""
        
        try:
            # Check if profile already exists
            existing_profiles = await self.get_user_profiles(user_id)
            for profile in existing_profiles:
                if profile.profile_name == profile_name:
                    raise VoiceProfileError(f"Profile '{profile_name}' already exists for user")
            
            profile_id = str(uuid.uuid4())
            
            # Create voice profile
            voice_profile = VoiceProfile(
                profile_id=profile_id,
                user_id=user_id,
                profile_name=profile_name,
                language=language,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True,
                voice_characteristics={
                    "pitch_range": "normal",
                    "speaking_rate": "normal",
                    "tone": "neutral",
                    **metadata
                },
                training_status="pending" if voice_samples else "not_started"
            )
            
            # Store profile
            self.voice_profiles[profile_id] = voice_profile
            
            # Store voice samples if provided
            if voice_samples:
                self.voice_samples[profile_id] = voice_samples
                voice_profile.training_status = "in_progress"
                # In production, trigger voice cloning training here
                voice_profile.training_progress = 0.1
            
            # Update stats
            self.profile_stats["total_profiles"] += 1
            self.profile_stats["active_profiles"] += 1
            
            logger.info(f"Created voice profile {profile_id} for user {user_id}")
            
            return VoiceResponse(
                success=True,
                message=f"Voice profile '{profile_name}' created successfully",
                data={
                    "profile": voice_profile.dict(),
                    "samples_provided": len(voice_samples) if voice_samples else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create voice profile: {e}")
            if isinstance(e, VoiceServiceError):
                raise e
            else:
                raise VoiceProfileError(f"Profile creation failed: {str(e)}")
    
    async def get_voice_profile(
        self,
        user_id: str,
        profile_id: str
    ) -> Optional[VoiceProfile]:
        """Get a specific voice profile"""
        
        profile = self.voice_profiles.get(profile_id)
        
        if not profile:
            return None
        
        if profile.user_id != user_id:
            raise AuthenticationError("Access denied to voice profile")
        
        return profile
    
    async def get_user_profiles(
        self,
        user_id: str,
        active_only: bool = False
    ) -> List[VoiceProfile]:
        """Get all voice profiles for a user"""
        
        user_profiles = [
            profile for profile in self.voice_profiles.values()
            if profile.user_id == user_id
        ]
        
        if active_only:
            user_profiles = [p for p in user_profiles if p.is_active]
        
        # Sort by created date (newest first)
        user_profiles.sort(key=lambda x: x.created_at, reverse=True)
        
        return user_profiles
    
    async def update_voice_profile(
        self,
        user_id: str,
        profile_id: str,
        updates: Dict[str, Any]
    ) -> VoiceResponse:
        """Update a voice profile"""
        
        try:
            profile = await self.get_voice_profile(user_id, profile_id)
            
            if not profile:
                raise VoiceProfileError(f"Voice profile {profile_id} not found")
            
            # Update allowed fields
            allowed_fields = {
                'profile_name', 'language', 'is_active', 
                'voice_characteristics', 'settings'
            }
            
            updated_fields = []
            for field, value in updates.items():
                if field in allowed_fields:
                    setattr(profile, field, value)
                    updated_fields.append(field)
            
            profile.updated_at = datetime.utcnow()
            
            logger.info(f"Updated voice profile {profile_id} fields: {updated_fields}")
            
            return VoiceResponse(
                success=True,
                message="Voice profile updated successfully",
                data={
                    "profile": profile.dict(),
                    "updated_fields": updated_fields
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to update voice profile: {e}")
            if isinstance(e, VoiceServiceError):
                raise e
            else:
                raise VoiceProfileError(f"Profile update failed: {str(e)}")
    
    async def delete_voice_profile(
        self,
        user_id: str,
        profile_id: str
    ) -> VoiceResponse:
        """Delete a voice profile"""
        
        try:
            profile = await self.get_voice_profile(user_id, profile_id)
            
            if not profile:
                raise VoiceProfileError(f"Voice profile {profile_id} not found")
            
            # Remove profile and associated data
            del self.voice_profiles[profile_id]
            
            if profile_id in self.voice_samples:
                del self.voice_samples[profile_id]
            
            # Update stats
            self.profile_stats["active_profiles"] -= 1
            
            logger.info(f"Deleted voice profile {profile_id} for user {user_id}")
            
            return VoiceResponse(
                success=True,
                message="Voice profile deleted successfully",
                data={"profile_id": profile_id}
            )
            
        except Exception as e:
            logger.error(f"Failed to delete voice profile: {e}")
            if isinstance(e, VoiceServiceError):
                raise e
            else:
                raise VoiceProfileError(f"Profile deletion failed: {str(e)}")
    
    async def add_voice_samples(
        self,
        user_id: str,
        profile_id: str,
        voice_samples: List[AudioData]
    ) -> VoiceResponse:
        """Add voice samples to a profile for training"""
        
        try:
            profile = await self.get_voice_profile(user_id, profile_id)
            
            if not profile:
                raise VoiceProfileError(f"Voice profile {profile_id} not found")
            
            # Validate samples
            total_duration = 0
            for sample in voice_samples:
                if sample.duration:
                    total_duration += sample.duration
            
            if total_duration < voice_config.MIN_TRAINING_DURATION:
                raise VoiceProfileError(
                    f"Insufficient audio for training. Need at least "
                    f"{voice_config.MIN_TRAINING_DURATION} seconds"
                )
            
            # Store samples
            if profile_id not in self.voice_samples:
                self.voice_samples[profile_id] = []
            
            self.voice_samples[profile_id].extend(voice_samples)
            
            # Update profile training status
            profile.training_status = "in_progress"
            profile.training_progress = min(0.8, len(self.voice_samples[profile_id]) * 0.1)
            profile.updated_at = datetime.utcnow()
            
            logger.info(f"Added {len(voice_samples)} voice samples to profile {profile_id}")
            
            return VoiceResponse(
                success=True,
                message="Voice samples added successfully",
                data={
                    "samples_added": len(voice_samples),
                    "total_samples": len(self.voice_samples[profile_id]),
                    "training_progress": profile.training_progress
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to add voice samples: {e}")
            if isinstance(e, VoiceServiceError):
                raise e
            else:
                raise VoiceProfileError(f"Sample addition failed: {str(e)}")
    
    async def start_voice_training(
        self,
        user_id: str,
        profile_id: str
    ) -> VoiceResponse:
        """Start voice cloning training for a profile"""
        
        try:
            profile = await self.get_voice_profile(user_id, profile_id)
            
            if not profile:
                raise VoiceProfileError(f"Voice profile {profile_id} not found")
            
            if profile_id not in self.voice_samples or not self.voice_samples[profile_id]:
                raise VoiceProfileError("No voice samples available for training")
            
            samples = self.voice_samples[profile_id]
            total_duration = sum(s.duration or 0 for s in samples)
            
            if total_duration < voice_config.MIN_TRAINING_DURATION:
                raise VoiceProfileError(
                    f"Insufficient audio for training. Need at least "
                    f"{voice_config.MIN_TRAINING_DURATION} seconds, have {total_duration}"
                )
            
            # Start training process (mock implementation)
            profile.training_status = "training"
            profile.training_progress = 0.2
            profile.training_started_at = datetime.utcnow()
            profile.updated_at = datetime.utcnow()
            
            # Update stats
            self.profile_stats["voice_clones_created"] += 1
            
            logger.info(f"Started voice training for profile {profile_id}")
            
            return VoiceResponse(
                success=True,
                message="Voice training started successfully",
                data={
                    "profile": profile.dict(),
                    "estimated_completion": "2-4 hours",
                    "samples_used": len(samples)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to start voice training: {e}")
            if isinstance(e, VoiceServiceError):
                raise e
            else:
                raise VoiceProfileError(f"Training start failed: {str(e)}")
    
    async def get_training_status(
        self,
        user_id: str,
        profile_id: str
    ) -> VoiceResponse:
        """Get voice training status for a profile"""
        
        try:
            profile = await self.get_voice_profile(user_id, profile_id)
            
            if not profile:
                raise VoiceProfileError(f"Voice profile {profile_id} not found")
            
            # Mock training progress
            if profile.training_status == "training":
                # Simulate progress over time
                if profile.training_started_at:
                    elapsed = datetime.utcnow() - profile.training_started_at
                    progress = min(1.0, 0.2 + (elapsed.total_seconds() / 7200))  # Complete in 2 hours
                    profile.training_progress = progress
                    
                    if progress >= 1.0:
                        profile.training_status = "completed"
                        profile.is_trained = True
                        profile.training_completed_at = datetime.utcnow()
            
            return VoiceResponse(
                success=True,
                message="Training status retrieved",
                data={
                    "profile_id": profile_id,
                    "training_status": profile.training_status,
                    "training_progress": profile.training_progress,
                    "is_trained": profile.is_trained,
                    "started_at": profile.training_started_at.isoformat() if profile.training_started_at else None,
                    "completed_at": profile.training_completed_at.isoformat() if profile.training_completed_at else None
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get training status: {e}")
            if isinstance(e, VoiceServiceError):
                raise e
            else:
                raise VoiceProfileError(f"Status retrieval failed: {str(e)}")
    
    async def get_user_preferences(
        self,
        user_id: str
    ) -> Optional[VoicePreferences]:
        """Get user voice preferences"""
        
        return self.user_preferences.get(user_id)
    
    async def update_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> VoiceResponse:
        """Update user voice preferences"""
        
        try:
            current_prefs = self.user_preferences.get(user_id)
            
            if not current_prefs:
                current_prefs = VoicePreferences(
                    user_id=user_id,
                    default_language="en",
                    preferred_voice="default",
                    volume_level=0.8,
                    speech_rate=1.0,
                    created_at=datetime.utcnow()
                )
            
            # Update preferences
            for field, value in preferences.items():
                if hasattr(current_prefs, field):
                    setattr(current_prefs, field, value)
            
            current_prefs.updated_at = datetime.utcnow()
            self.user_preferences[user_id] = current_prefs
            
            # Update stats
            self.profile_stats["preferences_updated"] += 1
            
            logger.info(f"Updated voice preferences for user {user_id}")
            
            return VoiceResponse(
                success=True,
                message="Voice preferences updated successfully",
                data={"preferences": current_prefs.dict()}
            )
            
        except Exception as e:
            logger.error(f"Failed to update preferences: {e}")
            raise VoiceProfileError(f"Preferences update failed: {str(e)}")
    
    async def get_profile_analytics(
        self,
        user_id: str,
        profile_id: Optional[str] = None
    ) -> VoiceResponse:
        """Get analytics for user voice profiles"""
        
        try:
            user_profiles = await self.get_user_profiles(user_id)
            
            if profile_id:
                user_profiles = [p for p in user_profiles if p.profile_id == profile_id]
            
            analytics = {
                "total_profiles": len(user_profiles),
                "active_profiles": len([p for p in user_profiles if p.is_active]),
                "trained_profiles": len([p for p in user_profiles if p.is_trained]),
                "languages_covered": list(set(p.language for p in user_profiles)),
                "training_in_progress": len([p for p in user_profiles if p.training_status == "training"]),
                "profiles": [
                    {
                        "profile_id": p.profile_id,
                        "profile_name": p.profile_name,
                        "language": p.language,
                        "is_trained": p.is_trained,
                        "training_status": p.training_status,
                        "created_at": p.created_at.isoformat(),
                        "usage_count": getattr(p, 'usage_count', 0)
                    }
                    for p in user_profiles
                ]
            }
            
            return VoiceResponse(
                success=True,
                message="Profile analytics retrieved",
                data=analytics
            )
            
        except Exception as e:
            logger.error(f"Failed to get profile analytics: {e}")
            raise VoiceProfileError(f"Analytics retrieval failed: {str(e)}")
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get voice profile service statistics"""
        
        return {
            "total_profiles": self.profile_stats["total_profiles"],
            "active_profiles": self.profile_stats["active_profiles"],
            "voice_clones_created": self.profile_stats["voice_clones_created"],
            "preferences_updated": self.profile_stats["preferences_updated"],
            "supported_languages": list(voice_config.SUPPORTED_LANGUAGES.keys()),
            "training_config": {
                "min_duration_seconds": voice_config.MIN_TRAINING_DURATION,
                "max_samples": getattr(voice_config, 'MAX_TRAINING_SAMPLES', 50),
                "supported_formats": voice_config.SUPPORTED_AUDIO_FORMATS
            }
        }
    
    async def cleanup_inactive_profiles(
        self,
        inactive_days: int = 90
    ) -> int:
        """Clean up inactive voice profiles"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=inactive_days)
        cleaned_profiles = 0
        
        profiles_to_remove = []
        for profile_id, profile in self.voice_profiles.items():
            if (not profile.is_active and 
                profile.updated_at < cutoff_date and 
                profile.training_status in ["failed", "cancelled"]):
                profiles_to_remove.append(profile_id)
        
        # Remove inactive profiles
        for profile_id in profiles_to_remove:
            del self.voice_profiles[profile_id]
            if profile_id in self.voice_samples:
                del self.voice_samples[profile_id]
            cleaned_profiles += 1
        
        if cleaned_profiles > 0:
            logger.info(f"Cleaned up {cleaned_profiles} inactive voice profiles")
            self.profile_stats["active_profiles"] -= cleaned_profiles
        
        return cleaned_profiles
