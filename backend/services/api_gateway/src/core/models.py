"""
Core data models for API Gateway
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, AsyncIterator, Union, Callable
from enum import Enum
from datetime import datetime

class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"

class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"

@dataclass
class ServiceInstance:
    """Represents a single service instance"""
    id: str
    name: str
    url: str
    health_path: str = "/health"
    weight: int = 1
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    failure_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RouteRule:
    """Defines routing rules for requests"""
    path_pattern: str
    methods: List[HTTPMethod]
    service_name: str
    strip_prefix: bool = False
    timeout: int = 30
    retries: int = 3
    auth_required: bool = True
    rate_limit: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthCheckResult:
    """Result of a health check"""
    service_id: str
    status: ServiceStatus
    response_time: float
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class ProxyRequest:
    """Represents a request to be proxied"""
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: Optional[bytes] = None
    user_id: Optional[str] = None
    request_id: str = ""

@dataclass
class ProxyResponse:
    """Represents a response from a proxied service.
    For large audio/video or streaming responses, body can be empty and an async iterator provided.
    """
    status_code: int
    headers: Dict[str, str]
    body: bytes
    response_time: float
    service_name: str
    request_id: str
    streaming: bool = False
    stream_iterator: Optional[AsyncIterator[bytes]] = None  # When streaming is True

@dataclass
class CircuitBreakerState:
    """Circuit breaker state for a service"""
    service_name: str
    state: str  # "closed", "open", "half_open"
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None

@dataclass
class RateLimitState:
    """Rate limiting state"""
    identifier: str  # user_id, ip_address, etc.
    request_count: int = 0
    window_start: datetime = field(default_factory=datetime.now)
    blocked_until: Optional[datetime] = None
