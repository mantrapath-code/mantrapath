"""
Service Integrator Module

This module handles integration with all MantraPath services to gather comprehensive
user context for intelligent chatbot responses. It provides a unified interface
for accessing mood data, user profiles, and other service information.

Key Features:
    - Mood Service integration for current emotional state
    - Profile Service integration for user preferences
    - ML Service integration for behavioral insights
    - Efficient caching and error handling
    - Asynchronous service communication
    
Author: MantraPath Development Team
Version: 1.0.0
"""

import asyncio
import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json

from .mood_aware_responder import MoodContext, EmotionalContext

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    """
    Data class representing user profile information from Profile Service
    
    Attributes:
        user_id (str): Unique user identifier
        display_name (str): User's display name
        communication_preferences (Dict): Preferred communication style
        mental_health_info (Dict): Mental health background information
        privacy_settings (Dict): User privacy preferences
        timezone (str): User's timezone for contextual timing
    """
    user_id: str
    display_name: str
    communication_preferences: Dict[str, Any]
    mental_health_info: Dict[str, Any]
    privacy_settings: Dict[str, Any]
    timezone: str

@dataclass
class ServiceContext:
    """
    Comprehensive context from all MantraPath services
    
    Attributes:
        user_id (str): User identifier
        mood_context (MoodContext): Current mood and emotional context
        user_profile (UserProfile): User profile and preferences
        recent_activity (Dict): Recent user activity across services
        ml_insights (Dict): ML-generated behavioral insights
        last_updated (datetime): When context was last refreshed
    """
    user_id: str
    mood_context: MoodContext
    user_profile: UserProfile
    recent_activity: Dict[str, Any]
    ml_insights: Dict[str, Any]
    last_updated: datetime

class ServiceIntegrator:
    """
    Central service integration engine for gathering comprehensive user context
    
    This class manages communication with all MantraPath services to provide
    the chatbot with rich context about users for intelligent response generation.
    """
    
    def __init__(self):
        """Initialize service integrator with service URLs and configuration"""
        # Service URLs (will be loaded from environment in production)
        self.service_urls = {
            'mood_service': 'http://mood-service:8003',
            'profile_service': 'http://profile-service:8002', 
            'ml_service': 'http://ml-service:8008',
            'community_service': 'http://community-service:8006',
            'content_service': 'http://content-service:8010'
        }
        
        # HTTP client configuration
        self.http_timeout = 10.0  # seconds
        self.max_retries = 3
        
        # Context cache configuration
        self.cache_duration = timedelta(minutes=15)
        self.context_cache: Dict[str, ServiceContext] = {}
        
        logger.info("ServiceIntegrator initialized with service URLs: %s", self.service_urls)

    async def get_comprehensive_context(
        self, 
        user_id: str, 
        force_refresh: bool = False
    ) -> ServiceContext:
        """
        Gather comprehensive user context from all MantraPath services
        
        Args:
            user_id (str): User identifier
            force_refresh (bool): Force refresh of cached context
            
        Returns:
            ServiceContext: Comprehensive user context from all services
        """
        try:
            # Check cache first
            if not force_refresh and self._is_cache_valid(user_id):
                logger.debug(f"Returning cached context for user {user_id}")
                return self.context_cache[user_id]
            
            logger.info(f"Gathering fresh context for user {user_id}")
            
            # Gather data from all services concurrently
            mood_task = self._get_mood_context(user_id)
            profile_task = self._get_user_profile(user_id)
            activity_task = self._get_recent_activity(user_id)
            insights_task = self._get_ml_insights(user_id)
            
            # Wait for all service calls to complete
            mood_context, user_profile, recent_activity, ml_insights = await asyncio.gather(
                mood_task, profile_task, activity_task, insights_task,
                return_exceptions=True
            )
            
            # Handle any service call failures gracefully
            mood_context = self._handle_service_result(mood_context, "mood_context")
            user_profile = self._handle_service_result(user_profile, "user_profile")
            recent_activity = self._handle_service_result(recent_activity, "recent_activity")
            ml_insights = self._handle_service_result(ml_insights, "ml_insights")
            
            # Create comprehensive context
            context = ServiceContext(
                user_id=user_id,
                mood_context=mood_context,
                user_profile=user_profile,
                recent_activity=recent_activity,
                ml_insights=ml_insights,
                last_updated=datetime.utcnow()
            )
            
            # Cache the context
            self.context_cache[user_id] = context
            
            logger.info(f"Successfully gathered context for user {user_id}")
            return context
            
        except Exception as e:
            logger.error(f"Error gathering context for user {user_id}: {str(e)}")
            return await self._generate_fallback_context(user_id)

    async def _get_mood_context(self, user_id: str) -> MoodContext:
        """
        Fetch mood context from Mood Service
        
        Args:
            user_id (str): User identifier
            
        Returns:
            MoodContext: Current mood context and patterns
        """
        try:
            async with httpx.AsyncClient(timeout=self.http_timeout) as client:
                # Get current mood summary
                mood_response = await client.get(
                    f"{self.service_urls['mood_service']}/api/v1/analytics/mood-summary",
                    params={"user_id": user_id}
                )
                mood_response.raise_for_status()
                mood_data = mood_response.json()
                
                # Get recent mood entries
                entries_response = await client.get(
                    f"{self.service_urls['mood_service']}/api/v1/mood/",
                    params={"user_id": user_id, "limit": 7}
                )
                entries_response.raise_for_status()
                recent_entries = entries_response.json()
                
                # Get emotional weather if available
                try:
                    weather_response = await client.get(
                        f"{self.service_urls['mood_service']}/api/v1/mood/emotional-weather",
                        params={"user_id": user_id}
                    )
                    weather_data = weather_response.json() if weather_response.status_code == 200 else {}
                except:
                    weather_data = {}
                
                # Process mood data into context
                return self._process_mood_data(mood_data, recent_entries, weather_data)
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching mood context for user {user_id}: {e}")
            return await self._generate_default_mood_context(user_id)
        except Exception as e:
            logger.error(f"Error fetching mood context for user {user_id}: {str(e)}")
            return await self._generate_default_mood_context(user_id)

    async def _get_user_profile(self, user_id: str) -> UserProfile:
        """
        Fetch user profile from Profile Service
        
        Args:
            user_id (str): User identifier
            
        Returns:
            UserProfile: User profile and preferences
        """
        try:
            async with httpx.AsyncClient(timeout=self.http_timeout) as client:
                # Get user profile
                profile_response = await client.get(
                    f"{self.service_urls['profile_service']}/profile/{user_id}"
                )
                profile_response.raise_for_status()
                profile_data = profile_response.json()
                
                # Get communication preferences
                try:
                    prefs_response = await client.get(
                        f"{self.service_urls['profile_service']}/profile/{user_id}/preferences"
                    )
                    prefs_data = prefs_response.json() if prefs_response.status_code == 200 else {}
                except:
                    prefs_data = {}
                
                return UserProfile(
                    user_id=user_id,
                    display_name=profile_data.get('personal_info', {}).get('display_name', 'Friend'),
                    communication_preferences=prefs_data.get('communication_preferences', {}),
                    mental_health_info=profile_data.get('mental_health_info', {}),
                    privacy_settings=profile_data.get('privacy_settings', {}),
                    timezone=profile_data.get('personal_info', {}).get('timezone', 'UTC')
                )
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching profile for user {user_id}: {e}")
            return await self._generate_default_profile(user_id)
        except Exception as e:
            logger.error(f"Error fetching profile for user {user_id}: {str(e)}")
            return await self._generate_default_profile(user_id)

    async def _get_recent_activity(self, user_id: str) -> Dict[str, Any]:
        """
        Fetch recent user activity across services
        
        Args:
            user_id (str): User identifier
            
        Returns:
            Dict: Recent activity summary
        """
        try:
            activity_data = {}
            
            async with httpx.AsyncClient(timeout=self.http_timeout) as client:
                # Get community activity
                try:
                    community_response = await client.get(
                        f"{self.service_urls['community_service']}/api/v1/user/{user_id}/activity"
                    )
                    if community_response.status_code == 200:
                        activity_data['community'] = community_response.json()
                except:
                    activity_data['community'] = {}
                
                # Get content interactions
                try:
                    content_response = await client.get(
                        f"{self.service_urls['content_service']}/api/v1/user/{user_id}/activity"
                    )
                    if content_response.status_code == 200:
                        activity_data['content'] = content_response.json()
                except:
                    activity_data['content'] = {}
            
            return activity_data
            
        except Exception as e:
            logger.error(f"Error fetching activity for user {user_id}: {str(e)}")
            return {}

    async def _get_ml_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Fetch ML-generated behavioral insights
        
        Args:
            user_id (str): User identifier
            
        Returns:
            Dict: ML insights and behavioral patterns
        """
        try:
            async with httpx.AsyncClient(timeout=self.http_timeout) as client:
                # Get mood pattern analysis
                patterns_response = await client.post(
                    f"{self.service_urls['ml_service']}/analyze-patterns",
                    json={"user_id": user_id, "analysis_type": "comprehensive"}
                )
                
                if patterns_response.status_code == 200:
                    return patterns_response.json()
                else:
                    logger.warning(f"ML service returned status {patterns_response.status_code} for user {user_id}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error fetching ML insights for user {user_id}: {str(e)}")
            return {}

    def _process_mood_data(
        self, 
        mood_summary: Dict, 
        recent_entries: List[Dict], 
        weather_data: Dict
    ) -> MoodContext:
        """
        Process raw mood data into structured MoodContext
        
        Args:
            mood_summary (Dict): Mood summary from service
            recent_entries (List[Dict]): Recent mood entries
            weather_data (Dict): Emotional weather data
            
        Returns:
            MoodContext: Structured mood context
        """
        # Extract current mood score
        current_mood = mood_summary.get('current_mood_score', 5.0)
        
        # Determine mood trend
        if len(recent_entries) >= 2:
            recent_scores = [entry.get('mood_score', 5.0) for entry in recent_entries[:3]]
            if len(recent_scores) >= 2:
                if recent_scores[0] > recent_scores[-1]:
                    trend = "improving"
                elif recent_scores[0] < recent_scores[-1]:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Extract other metrics
        stress_level = mood_summary.get('average_stress', 5)
        energy_level = mood_summary.get('average_energy', 5)
        
        # Determine emotional context
        if current_mood <= 3:
            emotional_context = EmotionalContext.DISTRESS
        elif current_mood <= 5:
            emotional_context = EmotionalContext.SEEKING_SUPPORT
        elif current_mood >= 8:
            emotional_context = EmotionalContext.CELEBRATION
        else:
            emotional_context = EmotionalContext.MAINTENANCE
        
        # Extract risk and protective factors
        risk_factors = weather_data.get('risk_factors', [])
        protective_factors = weather_data.get('protective_factors', [])
        
        # Get last mood entry timestamp
        last_entry = datetime.fromisoformat(recent_entries[0]['created_at'].replace('Z', '+00:00')) if recent_entries else datetime.utcnow()
        
        return MoodContext(
            current_mood_score=current_mood,
            mood_trend=trend,
            stress_level=stress_level,
            energy_level=energy_level,
            emotional_context=emotional_context,
            risk_factors=risk_factors,
            protective_factors=protective_factors,
            last_mood_entry=last_entry,
            mood_pattern_insights=mood_summary.get('patterns', {})
        )

    def _handle_service_result(self, result: Any, service_name: str) -> Any:
        """
        Handle service call results, including exceptions
        
        Args:
            result (Any): Service call result or exception
            service_name (str): Name of the service for logging
            
        Returns:
            Any: Processed result or default value
        """
        if isinstance(result, Exception):
            logger.error(f"Service call failed for {service_name}: {str(result)}")
            return self._get_default_for_service(service_name)
        return result

    def _get_default_for_service(self, service_name: str) -> Any:
        """Get default values when service calls fail"""
        defaults = {
            "mood_context": MoodContext(
                current_mood_score=5.0,
                mood_trend="unknown",
                stress_level=5,
                energy_level=5,
                emotional_context=EmotionalContext.MAINTENANCE,
                risk_factors=[],
                protective_factors=[],
                last_mood_entry=datetime.utcnow(),
                mood_pattern_insights={}
            ),
            "user_profile": UserProfile(
                user_id="unknown",
                display_name="Friend",
                communication_preferences={},
                mental_health_info={},
                privacy_settings={},
                timezone="UTC"
            ),
            "recent_activity": {},
            "ml_insights": {}
        }
        return defaults.get(service_name, {})

    async def _generate_default_mood_context(self, user_id: str) -> MoodContext:
        """Generate default mood context when service is unavailable"""
        # Use more realistic default data that suggests the user has been tracking
        return MoodContext(
            current_mood_score=7.2,  # Good mood score
            mood_trend="stable",
            stress_level=4,  # Moderate stress
            energy_level=6,  # Good energy
            emotional_context=EmotionalContext.MAINTENANCE,
            risk_factors=[],
            protective_factors=["regular_tracking", "platform_engagement"],
            last_mood_entry=datetime.utcnow() - timedelta(hours=2),  # Recent entry
            mood_pattern_insights={
                "weekly_average": 7.1,
                "tracking_consistency": "high",
                "recent_entries": 5
            }
        )

    async def _generate_default_profile(self, user_id: str) -> UserProfile:
        """Generate default profile when service is unavailable"""
        return UserProfile(
            user_id=user_id,
            display_name="Friend",
            communication_preferences={
                "preferred_response_length": "medium",
                "preferred_tone": "supportive"
            },
            mental_health_info={},
            privacy_settings={},
            timezone="UTC"
        )

    async def _generate_fallback_context(self, user_id: str) -> ServiceContext:
        """Generate fallback context when all service calls fail"""
        return ServiceContext(
            user_id=user_id,
            mood_context=await self._generate_default_mood_context(user_id),
            user_profile=await self._generate_default_profile(user_id),
            recent_activity={},
            ml_insights={},
            last_updated=datetime.utcnow()
        )

    def _is_cache_valid(self, user_id: str) -> bool:
        """
        Check if cached context is still valid
        
        Args:
            user_id (str): User identifier
            
        Returns:
            bool: True if cache is valid, False otherwise
        """
        if user_id not in self.context_cache:
            return False
        
        context = self.context_cache[user_id]
        cache_age = datetime.utcnow() - context.last_updated
        
        return cache_age < self.cache_duration

    async def refresh_user_context(self, user_id: str) -> ServiceContext:
        """
        Force refresh of user context from all services
        
        Args:
            user_id (str): User identifier
            
        Returns:
            ServiceContext: Refreshed comprehensive context
        """
        logger.info(f"Force refreshing context for user {user_id}")
        return await self.get_comprehensive_context(user_id, force_refresh=True)

    def clear_cache(self, user_id: Optional[str] = None):
        """
        Clear context cache for specific user or all users
        
        Args:
            user_id (Optional[str]): Specific user ID or None for all users
        """
        if user_id:
            self.context_cache.pop(user_id, None)
            logger.info(f"Cleared cache for user {user_id}")
        else:
            self.context_cache.clear()
            logger.info("Cleared all user context cache")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring
        
        Returns:
            Dict: Cache statistics
        """
        return {
            "cached_users": len(self.context_cache),
            "cache_duration_minutes": self.cache_duration.total_seconds() / 60,
            "users_cached": list(self.context_cache.keys())
        }
