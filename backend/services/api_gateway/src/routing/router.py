"""
Request Router - Routes incoming requests to appropriate services
"""
import re
from typing import List, Optional
from src.core.models import RouteRule, HTTPMethod

class RequestRouter:
    """Routes requests based on path patterns and rules"""
    
    def __init__(self):
        self._routes: List[RouteRule] = []
        self._initialize_default_routes()
    
    def _initialize_default_routes(self):
        """Initialize default routing rules"""
        default_routes = [
            # Auth Service Routes
            RouteRule(
                path_pattern=r"^/auth/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE],
                service_name="auth",
                strip_prefix=True,  # Strip /auth prefix
                timeout=30,
                retries=3,
                auth_required=False  # Auth endpoints don't require auth
            ),
            RouteRule(
                path_pattern=r"^/(register|login|logout|refresh-token|verify-email|resend-verification)/?$",
                methods=[HTTPMethod.POST],
                service_name="auth",
                strip_prefix=False,
                timeout=30,
                retries=3,
                auth_required=False
            ),
            RouteRule(
                path_pattern=r"^/me/?$",
                methods=[HTTPMethod.GET, HTTPMethod.PUT],
                service_name="auth",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            
            # Profile Service Routes
            RouteRule(
                path_pattern=r"^/profile/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE],
                service_name="profile",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            RouteRule(
                path_pattern=r"^/users/.*",
                methods=[HTTPMethod.GET, HTTPMethod.PUT],
                service_name="profile",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            # API profiles route
            RouteRule(
                path_pattern=r"^/api/profiles/.*",
                methods=[HTTPMethod.GET, HTTPMethod.PUT],
                service_name="profile",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            # User stats routes
            RouteRule(
                path_pattern=r"^/user/stats/?$",
                methods=[HTTPMethod.GET],
                service_name="profile",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            # Notifications routes with different patterns
            RouteRule(
                path_pattern=r"^/notify/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE],
                service_name="notification",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            
            # Action Orchestrator Service Routes
            RouteRule(
                path_pattern=r"^/api/v1/orchestrate.*",
                methods=[HTTPMethod.POST],
                service_name="action-orchestrator",
                strip_prefix=False,
                timeout=60,
                retries=2,
                auth_required=True
            ),
            RouteRule(
                path_pattern=r"^/api/v1/workflow/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE],
                service_name="action-orchestrator",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            RouteRule(
                path_pattern=r"^/api/v1/intents.*",
                methods=[HTTPMethod.GET],
                service_name="action-orchestrator",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            RouteRule(
                path_pattern=r"^/api/v1/cultural-contexts.*",
                methods=[HTTPMethod.GET],
                service_name="action-orchestrator",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            
            # Mood Service Routes
            RouteRule(
                path_pattern=r"^/mood/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE],
                service_name="mood",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            
            # API v1 Routes for Mood and Analytics
            RouteRule(
                path_pattern=r"^/api/v1/mood/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE],
                service_name="mood",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            RouteRule(
                path_pattern=r"^/api/v1/analytics/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST],
                service_name="mood",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            RouteRule(
                path_pattern=r"^/api/v1/journal/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE],
                service_name="mood",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            
            # Chatbot Service Routes
            RouteRule(
                path_pattern=r"^/chat/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE],
                service_name="chatbot",
                strip_prefix=False,
                timeout=60,  # Longer timeout for AI processing
                retries=1,   # Fewer retries for AI calls
                auth_required=True
            ),
            
            # Chatbot Service API Routes
            RouteRule(
                path_pattern=r"^/api/chatbot/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE],
                service_name="chatbot",
                strip_prefix=False,
                timeout=60,  # Longer timeout for AI processing
                retries=1,   # Fewer retries for AI calls
                auth_required=True
            ),
            
            # Content Service Routes
            RouteRule(
                path_pattern=r"^/content/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE],
                service_name="content",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            RouteRule(
                path_pattern=r"^/journal/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE],
                service_name="content",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            
            # Community Service Routes
            RouteRule(
                path_pattern=r"^/community/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE],
                service_name="community",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            
            # Notification Service Routes
            RouteRule(
                path_pattern=r"^/notifications/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE],
                service_name="notification",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            
            # ML Service Routes
            RouteRule(
                path_pattern=r"^/ml/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST],
                service_name="ml",
                strip_prefix=False,
                timeout=120,  # Longer timeout for ML processing
                retries=1,
                auth_required=True
            ),
            
            # Media Service Routes
            RouteRule(
                path_pattern=r"^/media/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE],
                service_name="media",
                strip_prefix=False,
                timeout=60,  # Longer timeout for media uploads
                retries=2,
                auth_required=True
            ),
            
            # Translation Service Routes
            RouteRule(
                path_pattern=r"^/translate/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST],
                service_name="translation",
                strip_prefix=False,
                timeout=30,
                retries=2,
                auth_required=True
            ),
            
            # Voice Service Routes
            RouteRule(
                path_pattern=r"^/voice/.*",
                methods=[HTTPMethod.GET, HTTPMethod.POST],
                service_name="voice",
                strip_prefix=True,  # Strip /voice prefix before forwarding to voice service
                timeout=60,  # Longer timeout for voice processing
                retries=1,
                auth_required=True  # Re-enabled
            ),
        ]
        
        self._routes.extend(default_routes)
    
    def add_route(self, route: RouteRule):
        """Add a new routing rule"""
        self._routes.append(route)
    
    def remove_route(self, path_pattern: str):
        """Remove a routing rule by path pattern"""
        self._routes = [r for r in self._routes if r.path_pattern != path_pattern]
    
    def find_route(self, path: str, method: str) -> Optional[RouteRule]:
        """Find the appropriate route for a given path and method"""
        http_method = HTTPMethod(method.upper())
        
        for route in self._routes:
            if self._matches_pattern(path, route.path_pattern):
                if http_method in route.methods:
                    return route
        
        return None
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches the pattern"""
        try:
            return bool(re.match(pattern, path))
        except re.error:
            # If pattern is invalid, treat as literal string
            return path.startswith(pattern)
    
    def get_all_routes(self) -> List[RouteRule]:
        """Get all registered routes"""
        return self._routes.copy()
    
    def get_routes_for_service(self, service_name: str) -> List[RouteRule]:
        """Get all routes for a specific service"""
        return [route for route in self._routes if route.service_name == service_name]
