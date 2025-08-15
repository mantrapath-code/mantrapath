"""
Service Integration Manager
Handles integration with other MantraPath microservices
"""
import httpx
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from core.models import VoiceResponse, ServiceHealthStatus
from core.exceptions import ServiceIntegrationError, AuthenticationError
from config.settings import voice_config

logger = logging.getLogger(__name__)

class ServiceIntegrationManager:
    """Manager for integrating with other MantraPath services"""
    
    def __init__(self):
        self.service_urls = {
            "auth": voice_config.AUTH_SERVICE_URL,
            "profile": voice_config.PROFILE_SERVICE_URL,
            "content": voice_config.CONTENT_SERVICE_URL,
            "community": voice_config.COMMUNITY_SERVICE_URL,
            "translation": voice_config.TRANSLATION_SERVICE_URL,
            "notification": voice_config.NOTIFICATION_SERVICE_URL,
            "media": voice_config.MEDIA_SERVICE_URL,
            "mood": voice_config.MOOD_SERVICE_URL,
            "api_gateway": voice_config.API_GATEWAY_URL
        }
        
        self.service_health: Dict[str, ServiceHealthStatus] = {}
        self.integration_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "requests_by_service": {},
            "start_time": datetime.utcnow()
        }
        
        # Initialize HTTP client
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )
    
    async def verify_user_authentication(
        self,
        token: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify user authentication with Auth Service"""
        
        try:
            self._update_request_stats("auth")
            
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{self.service_urls['auth']}/verify"
            
            response = await self.http_client.post(url, headers=headers)
            
            if response.status_code == 200:
                auth_data = response.json()
                
                # Validate user_id if provided
                if user_id and auth_data.get("user_id") != user_id:
                    raise AuthenticationError("Token user ID mismatch")
                
                self._update_success_stats("auth")
                return auth_data
            else:
                self._update_failure_stats("auth")
                raise AuthenticationError(f"Authentication failed: {response.text}")
                
        except httpx.RequestError as e:
            self._update_failure_stats("auth")
            logger.error(f"Auth service request failed: {e}")
            raise ServiceIntegrationError(f"Auth service unavailable: {str(e)}")
    
    async def get_user_profile(
        self,
        user_id: str,
        token: str
    ) -> Dict[str, Any]:
        """Get user profile from Profile Service"""
        
        try:
            self._update_request_stats("profile")
            
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{self.service_urls['profile']}/user/{user_id}"
            
            response = await self.http_client.get(url, headers=headers)
            
            if response.status_code == 200:
                self._update_success_stats("profile")
                return response.json()
            else:
                self._update_failure_stats("profile")
                logger.error(f"Profile service error: {response.text}")
                return {"error": "Profile not found"}
                
        except httpx.RequestError as e:
            self._update_failure_stats("profile")
            logger.error(f"Profile service request failed: {e}")
            return {"error": "Profile service unavailable"}
    
    async def get_user_preferences(
        self,
        user_id: str,
        token: str
    ) -> Dict[str, Any]:
        """Get user preferences from Profile Service"""
        
        try:
            self._update_request_stats("profile")
            
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{self.service_urls['profile']}/user/{user_id}/preferences"
            
            response = await self.http_client.get(url, headers=headers)
            
            if response.status_code == 200:
                self._update_success_stats("profile")
                return response.json()
            else:
                self._update_failure_stats("profile")
                logger.error(f"Profile preferences error: {response.text}")
                return {"default_language": "en", "voice_enabled": True}
                
        except httpx.RequestError as e:
            self._update_failure_stats("profile")
            logger.error(f"Profile service request failed: {e}")
            return {"default_language": "en", "voice_enabled": True}
    
    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str = "auto",
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Translate text using Translation Service"""
        
        try:
            self._update_request_stats("translation")
            
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            data = {
                "text": text,
                "target_language": target_language,
                "source_language": source_language
            }
            
            url = f"{self.service_urls['translation']}/translate"
            response = await self.http_client.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                self._update_success_stats("translation")
                return response.json()
            else:
                self._update_failure_stats("translation")
                logger.error(f"Translation service error: {response.text}")
                return {"error": "Translation failed", "original_text": text}
                
        except httpx.RequestError as e:
            self._update_failure_stats("translation")
            logger.error(f"Translation service request failed: {e}")
            return {"error": "Translation service unavailable", "original_text": text}
    
    async def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "voice",
        token: Optional[str] = None
    ) -> bool:
        """Send notification via Notification Service"""
        
        try:
            self._update_request_stats("notification")
            
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            data = {
                "user_id": user_id,
                "title": title,
                "message": message,
                "type": notification_type,
                "source": "voice_service"
            }
            
            url = f"{self.service_urls['notification']}/send"
            response = await self.http_client.post(url, json=data, headers=headers)
            
            if response.status_code in [200, 201]:
                self._update_success_stats("notification")
                return True
            else:
                self._update_failure_stats("notification")
                logger.error(f"Notification service error: {response.text}")
                return False
                
        except httpx.RequestError as e:
            self._update_failure_stats("notification")
            logger.error(f"Notification service request failed: {e}")
            return False
    
    async def log_user_activity(
        self,
        user_id: str,
        activity_type: str,
        activity_data: Dict[str, Any],
        token: Optional[str] = None
    ) -> bool:
        """Log user activity for analytics"""
        
        try:
            self._update_request_stats("community")
            
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            data = {
                "user_id": user_id,
                "activity_type": f"voice_{activity_type}",
                "activity_data": activity_data,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "voice_service"
            }
            
            url = f"{self.service_urls['community']}/activity/log"
            response = await self.http_client.post(url, json=data, headers=headers)
            
            if response.status_code in [200, 201]:
                self._update_success_stats("community")
                return True
            else:
                self._update_failure_stats("community")
                logger.error(f"Activity logging error: {response.text}")
                return False
                
        except httpx.RequestError as e:
            self._update_failure_stats("community")
            logger.error(f"Activity logging request failed: {e}")
            return False
    
    async def get_content_metadata(
        self,
        content_id: str,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get content metadata from Content Service"""
        
        try:
            self._update_request_stats("content")
            
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            url = f"{self.service_urls['content']}/content/{content_id}"
            response = await self.http_client.get(url, headers=headers)
            
            if response.status_code == 200:
                self._update_success_stats("content")
                return response.json()
            else:
                self._update_failure_stats("content")
                logger.error(f"Content service error: {response.text}")
                return {"error": "Content not found"}
                
        except httpx.RequestError as e:
            self._update_failure_stats("content")
            logger.error(f"Content service request failed: {e}")
            return {"error": "Content service unavailable"}
    
    async def update_mood_tracking(
        self,
        user_id: str,
        mood_data: Dict[str, Any],
        token: Optional[str] = None
    ) -> bool:
        """Update mood tracking with voice-derived emotions"""
        
        try:
            self._update_request_stats("mood")
            
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            data = {
                "user_id": user_id,
                "mood_data": mood_data,
                "source": "voice_analysis",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            url = f"{self.service_urls['mood']}/mood/update"
            response = await self.http_client.post(url, json=data, headers=headers)
            
            if response.status_code in [200, 201]:
                self._update_success_stats("mood")
                return True
            else:
                self._update_failure_stats("mood")
                logger.error(f"Mood service error: {response.text}")
                return False
                
        except httpx.RequestError as e:
            self._update_failure_stats("mood")
            logger.error(f"Mood service request failed: {e}")
            return False
    
    async def store_audio_file(
        self,
        audio_data: bytes,
        filename: str,
        user_id: str,
        token: Optional[str] = None
    ) -> Optional[str]:
        """Store audio file using Media Service"""
        
        try:
            self._update_request_stats("media")
            
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            files = {
                "file": (filename, audio_data, "audio/wav")
            }
            
            data = {
                "user_id": user_id,
                "category": "voice",
                "source": "voice_service"
            }
            
            url = f"{self.service_urls['media']}/upload"
            response = await self.http_client.post(
                url, 
                files=files, 
                data=data, 
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                self._update_success_stats("media")
                result = response.json()
                return result.get("file_id")
            else:
                self._update_failure_stats("media")
                logger.error(f"Media service error: {response.text}")
                return None
                
        except httpx.RequestError as e:
            self._update_failure_stats("media")
            logger.error(f"Media service request failed: {e}")
            return None
    
    async def check_service_health(
        self,
        service_name: str
    ) -> ServiceHealthStatus:
        """Check health of a specific service"""
        
        try:
            if service_name not in self.service_urls:
                return ServiceHealthStatus(
                    service_name=service_name,
                    status="unknown",
                    message="Service not configured"
                )
            
            url = f"{self.service_urls[service_name]}/health"
            response = await self.http_client.get(url, timeout=5.0)
            
            if response.status_code == 200:
                health_data = response.json()
                status = ServiceHealthStatus(
                    service_name=service_name,
                    status="healthy",
                    response_time_ms=response.elapsed.total_seconds() * 1000,
                    last_check=datetime.utcnow(),
                    details=health_data
                )
            else:
                status = ServiceHealthStatus(
                    service_name=service_name,
                    status="unhealthy",
                    message=f"HTTP {response.status_code}",
                    last_check=datetime.utcnow()
                )
            
            self.service_health[service_name] = status
            return status
            
        except httpx.RequestError as e:
            status = ServiceHealthStatus(
                service_name=service_name,
                status="unreachable",
                message=str(e),
                last_check=datetime.utcnow()
            )
            self.service_health[service_name] = status
            return status
    
    async def check_all_services_health(self) -> Dict[str, ServiceHealthStatus]:
        """Check health of all configured services"""
        
        health_checks = {}
        
        for service_name in self.service_urls.keys():
            health_checks[service_name] = await self.check_service_health(service_name)
        
        return health_checks
    
    async def register_with_api_gateway(
        self,
        service_info: Dict[str, Any]
    ) -> bool:
        """Register voice service with API Gateway"""
        
        try:
            self._update_request_stats("api_gateway")
            
            data = {
                "service_name": "voice_service",
                "service_url": service_info.get("service_url"),
                "health_endpoint": service_info.get("health_endpoint", "/health"),
                "version": service_info.get("version", "1.0.0"),
                "capabilities": service_info.get("capabilities", []),
                "supported_routes": service_info.get("supported_routes", [])
            }
            
            url = f"{self.service_urls['api_gateway']}/registry/register"
            response = await self.http_client.post(url, json=data)
            
            if response.status_code in [200, 201]:
                self._update_success_stats("api_gateway")
                logger.info("Successfully registered with API Gateway")
                return True
            else:
                self._update_failure_stats("api_gateway")
                logger.error(f"API Gateway registration failed: {response.text}")
                return False
                
        except httpx.RequestError as e:
            self._update_failure_stats("api_gateway")
            logger.error(f"API Gateway registration request failed: {e}")
            return False
    
    def _update_request_stats(self, service_name: str) -> None:
        """Update request statistics"""
        self.integration_stats["total_requests"] += 1
        if service_name not in self.integration_stats["requests_by_service"]:
            self.integration_stats["requests_by_service"][service_name] = {
                "total": 0, "successful": 0, "failed": 0
            }
        self.integration_stats["requests_by_service"][service_name]["total"] += 1
    
    def _update_success_stats(self, service_name: str) -> None:
        """Update success statistics"""
        self.integration_stats["successful_requests"] += 1
        self.integration_stats["requests_by_service"][service_name]["successful"] += 1
    
    def _update_failure_stats(self, service_name: str) -> None:
        """Update failure statistics"""
        self.integration_stats["failed_requests"] += 1
        self.integration_stats["requests_by_service"][service_name]["failed"] += 1
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get service integration statistics"""
        
        uptime = datetime.utcnow() - self.integration_stats["start_time"]
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "total_requests": self.integration_stats["total_requests"],
            "successful_requests": self.integration_stats["successful_requests"],
            "failed_requests": self.integration_stats["failed_requests"],
            "success_rate": (
                self.integration_stats["successful_requests"] / 
                max(1, self.integration_stats["total_requests"])
            ),
            "requests_by_service": self.integration_stats["requests_by_service"],
            "configured_services": list(self.service_urls.keys()),
            "service_health": {
                name: status.dict() for name, status in self.service_health.items()
            }
        }
    
    async def close(self) -> None:
        """Close HTTP client and cleanup resources"""
        await self.http_client.aclose()
        logger.info("Service integration manager closed")
