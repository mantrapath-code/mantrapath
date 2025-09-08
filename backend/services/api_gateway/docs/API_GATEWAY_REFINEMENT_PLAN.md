# API Gateway Service Refinement Plan

## Phase 1: Critical Issues Resolution

### 1. Port Configuration Standardization

#### Problem
- models-service port 8080 conflicts with gateway WebSocket port
- Configuration mismatches between service names and URLs

#### Solution
Update service configuration with standardized ports:

```python
# src/core/config.py - Updated Service Configuration
class ServiceConfig(BaseSettings):
    """Service registry configuration with standardized ports"""
    
    # Gateway Ports
    gateway_port: int = Field(default=8000)
    websocket_port: int = Field(default=8001)  # Changed from 8080
    metrics_port: int = Field(default=9090)
    
    # Standardized Service Ports (8010-8030 range)
    auth_service_url: str = Field(default="http://auth-service:8010")
    profile_service_url: str = Field(default="http://profile-service:8011")
    mood_service_url: str = Field(default="http://mood-service:8012")
    chatbot_service_url: str = Field(default="http://chatbot-service:8013")
    content_service_url: str = Field(default="http://content-service:8014")
    community_service_url: str = Field(default="http://community-service:8015")
    notification_service_url: str = Field(default="http://notification-service:8016")
    ml_service_url: str = Field(default="http://ml-service:8017")
    media_service_url: str = Field(default="http://media-service:8018")
    translation_service_url: str = Field(default="http://translation-service:8019")
    voice_service_url: str = Field(default="http://voice-service:8020")
    action_orchestrator_url: str = Field(default="http://action-orchestrator:8021")
    models_service_url: str = Field(default="http://models-service:8022")
```

#### Docker Compose Updates
```yaml
# backend/docker-compose.yml - Gateway Configuration
api-gateway:
  ports:
    - "8000:8000"  # Main API
    - "8001:8001"  # WebSocket (changed from 8080)
    - "9090:9090"  # Metrics
  environment:
    - WEBSOCKET_PORT=8001
    
# Models Service Configuration
models-service:
  ports:
    - "8022:8022"  # Changed from 8080
  environment:
    - MODELS_SERVICE_PORT=8022
```

### 2. Enhanced Service Registry

#### Current Issues
- Static service registration
- Basic health checking
- No service metadata

#### Improved Implementation
```python
# src/registry/enhanced_service_registry.py
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import aiohttp

@dataclass
class EnhancedServiceInstance:
    """Enhanced service instance with metadata"""
    id: str
    name: str
    url: str
    version: str
    health_endpoints: List[str]  # Multiple health check endpoints
    capabilities: List[str]      # Service capabilities
    load_score: float = 0.0     # Current load (0-1)
    response_time_avg: float = 0.0  # Average response time
    status: ServiceStatus = ServiceStatus.UNKNOWN
    metadata: Dict[str, Any] = field(default_factory=dict)
    
class EnhancedServiceRegistry:
    """Enhanced service registry with dynamic discovery"""
    
    def __init__(self):
        self._services: Dict[str, List[EnhancedServiceInstance]] = {}
        self._health_history: Dict[str, List[HealthCheckResult]] = {}
        self._load_metrics: Dict[str, float] = {}
    
    async def register_service_dynamically(self, service_info: Dict[str, Any]):
        """Register service from runtime discovery"""
        instance = EnhancedServiceInstance(
            id=service_info["id"],
            name=service_info["name"],
            url=service_info["url"],
            version=service_info.get("version", "unknown"),
            health_endpoints=service_info.get("health_endpoints", ["/health"]),
            capabilities=service_info.get("capabilities", [])
        )
        
        await self.register_service(instance)
    
    async def perform_advanced_health_check(self, service: EnhancedServiceInstance):
        """Perform health check on multiple endpoints"""
        results = []
        
        for endpoint in service.health_endpoints:
            result = await self._check_endpoint_health(service, endpoint)
            results.append(result)
        
        # Aggregate results
        healthy_endpoints = sum(1 for r in results if r.status == ServiceStatus.HEALTHY)
        service.status = (
            ServiceStatus.HEALTHY if healthy_endpoints > len(results) / 2
            else ServiceStatus.DEGRADED if healthy_endpoints > 0
            else ServiceStatus.UNHEALTHY
        )
        
        # Update metrics
        avg_response_time = sum(r.response_time for r in results) / len(results)
        service.response_time_avg = avg_response_time
        
        return results
    
    def get_healthy_services_with_load_balancing(self, service_name: str) -> List[EnhancedServiceInstance]:
        """Get healthy services sorted by load and performance"""
        if service_name not in self._services:
            return []
        
        healthy_services = [
            s for s in self._services[service_name]
            if s.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]
        ]
        
        # Sort by load score and response time
        return sorted(
            healthy_services,
            key=lambda s: (s.load_score, s.response_time_avg)
        )
```

### 3. Improved Request Router

#### Enhanced Routing with Priority and Fallbacks
```python
# src/routing/enhanced_router.py
@dataclass
class EnhancedRouteRule:
    """Enhanced routing rule with advanced features"""
    path_pattern: str
    methods: List[HTTPMethod]
    service_name: str
    priority: int = 0                    # Higher number = higher priority
    fallback_service: Optional[str] = None
    cache_ttl: Optional[int] = None      # Response caching TTL
    rate_limit_override: Optional[int] = None
    request_transformer: Optional[str] = None  # Request transformation function
    response_transformer: Optional[str] = None # Response transformation function
    auth_required: bool = True
    permissions: List[str] = field(default_factory=list)  # Required permissions
    
class EnhancedRequestRouter:
    """Enhanced request router with priority and transformation"""
    
    def __init__(self):
        self._routes: List[EnhancedRouteRule] = []
        self._route_cache: Dict[str, EnhancedRouteRule] = {}
        self._transformers: Dict[str, Callable] = {}
    
    def find_route_with_priority(self, path: str, method: str) -> Optional[EnhancedRouteRule]:
        """Find route considering priority"""
        cache_key = f"{method}:{path}"
        
        if cache_key in self._route_cache:
            return self._route_cache[cache_key]
        
        matching_routes = []
        http_method = HTTPMethod(method.upper())
        
        for route in self._routes:
            if self._matches_pattern(path, route.path_pattern):
                if http_method in route.methods:
                    matching_routes.append(route)
        
        if not matching_routes:
            return None
        
        # Sort by priority (highest first)
        best_route = max(matching_routes, key=lambda r: r.priority)
        
        # Cache the result
        self._route_cache[cache_key] = best_route
        
        return best_route
    
    async def apply_request_transformation(self, route: EnhancedRouteRule, request: ProxyRequest):
        """Apply request transformation if configured"""
        if route.request_transformer and route.request_transformer in self._transformers:
            transformer = self._transformers[route.request_transformer]
            return await transformer(request)
        return request
    
    async def apply_response_transformation(self, route: EnhancedRouteRule, response: ProxyResponse):
        """Apply response transformation if configured"""
        if route.response_transformer and route.response_transformer in self._transformers:
            transformer = self._transformers[route.response_transformer]
            return await transformer(response)
        return response
```

### 4. Advanced Rate Limiting

#### Service and Endpoint Specific Limits
```python
# src/middleware/enhanced_rate_limiter.py
@dataclass
class RateLimitRule:
    """Rate limit rule for specific services/endpoints"""
    pattern: str                    # Path pattern
    requests_per_minute: int        # Requests per minute
    burst_capacity: int             # Burst capacity
    window_size: int = 60          # Window size in seconds
    cost_function: Optional[str] = None  # Cost calculation function

class EnhancedRateLimiter:
    """Enhanced rate limiter with service-specific rules"""
    
    def __init__(self):
        self._global_limiter = RateLimiter()
        self._service_rules: Dict[str, RateLimitRule] = {}
        self._endpoint_rules: List[RateLimitRule] = []
        self._cost_functions: Dict[str, Callable] = {}
    
    def add_service_rule(self, service_name: str, rule: RateLimitRule):
        """Add rate limit rule for specific service"""
        self._service_rules[service_name] = rule
    
    def add_endpoint_rule(self, rule: RateLimitRule):
        """Add rate limit rule for specific endpoint pattern"""
        self._endpoint_rules.append(rule)
    
    async def is_allowed_enhanced(
        self,
        identifier: str,
        path: str,
        service_name: str,
        request: ProxyRequest
    ) -> bool:
        """Enhanced rate limiting with service and endpoint specific rules"""
        
        # Check endpoint-specific rules first
        for rule in self._endpoint_rules:
            if self._matches_pattern(path, rule.pattern):
                cost = await self._calculate_cost(rule, request)
                return self._check_rate_limit(identifier, rule, cost)
        
        # Check service-specific rules
        if service_name in self._service_rules:
            rule = self._service_rules[service_name]
            cost = await self._calculate_cost(rule, request)
            return self._check_rate_limit(identifier, rule, cost)
        
        # Fall back to global rate limiting
        return self._global_limiter.is_allowed(identifier)
    
    async def _calculate_cost(self, rule: RateLimitRule, request: ProxyRequest) -> int:
        """Calculate request cost based on rule configuration"""
        if rule.cost_function and rule.cost_function in self._cost_functions:
            cost_func = self._cost_functions[rule.cost_function]
            return await cost_func(request)
        return 1
```

### 5. Enhanced Proxy with Connection Pooling

#### Improved HTTP Client Management
```python
# src/routing/enhanced_proxy.py
import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry

class EnhancedRequestProxy:
    """Enhanced request proxy with connection pooling and streaming"""
    
    def __init__(self):
        self._session_pool: Dict[str, aiohttp.ClientSession] = {}
        self._retry_options = ExponentialRetry(attempts=3)
    
    async def get_session(self, service_name: str) -> aiohttp.ClientSession:
        """Get or create session for service with connection pooling"""
        if service_name not in self._session_pool:
            connector = aiohttp.TCPConnector(
                limit=100,           # Total connection pool size
                limit_per_host=10,   # Connections per host
                ttl_dns_cache=300,   # DNS cache TTL
                use_dns_cache=True,
                keepalive_timeout=30
            )
            
            timeout = aiohttp.ClientTimeout(
                total=30,      # Total timeout
                connect=10,    # Connection timeout
                sock_read=20   # Socket read timeout
            )
            
            session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'MantraPath-Gateway/3.0',
                    'X-Gateway-Version': '3.0.0'
                }
            )
            
            self._session_pool[service_name] = session
        
        return self._session_pool[service_name]
    
    async def proxy_request_enhanced(
        self,
        request: ProxyRequest,
        target_service: EnhancedServiceInstance,
        stream_response: bool = False
    ) -> ProxyResponse:
        """Enhanced proxy with streaming and retry logic"""
        
        session = await self.get_session(target_service.name)
        retry_client = RetryClient(session, retry_options=self._retry_options)
        
        target_url = f"{target_service.url.rstrip('/')}{request.path}"
        headers = self._prepare_headers(request.headers)
        
        try:
            async with retry_client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                data=request.body
            ) as response:
                
                if stream_response:
                    return await self._stream_response(response, target_service, request)
                else:
                    body = await response.read()
                    return self._create_proxy_response(response, body, target_service, request)
                    
        except Exception as e:
            return self._create_error_response(e, target_service, request)
    
    async def _stream_response(
        self,
        response: aiohttp.ClientResponse,
        target_service: EnhancedServiceInstance,
        request: ProxyRequest
    ) -> ProxyResponse:
        """Stream large responses to prevent memory issues"""
        # Implementation for streaming responses
        pass
    
    async def cleanup_sessions(self):
        """Cleanup connection pools"""
        for session in self._session_pool.values():
            await session.close()
        self._session_pool.clear()
```

## Phase 2: Performance Optimizations

### 1. Response Caching Implementation

```python
# src/utils/response_cache.py
import json
import hashlib
from typing import Optional
import aioredis

class ResponseCache:
    """Response caching for GET requests"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self._redis = redis_client
        self._default_ttl = 300  # 5 minutes
    
    async def get_cached_response(
        self,
        method: str,
        path: str,
        query_params: Dict[str, str],
        user_id: Optional[str] = None
    ) -> Optional[ProxyResponse]:
        """Get cached response if available"""
        
        if method != "GET":
            return None
        
        cache_key = self._generate_cache_key(path, query_params, user_id)
        cached_data = await self._redis.get(cache_key)
        
        if cached_data:
            data = json.loads(cached_data)
            return ProxyResponse(**data)
        
        return None
    
    async def cache_response(
        self,
        response: ProxyResponse,
        method: str,
        path: str,
        query_params: Dict[str, str],
        user_id: Optional[str] = None,
        ttl: Optional[int] = None
    ):
        """Cache successful GET responses"""
        
        if method != "GET" or response.status_code >= 400:
            return
        
        cache_key = self._generate_cache_key(path, query_params, user_id)
        ttl = ttl or self._default_ttl
        
        # Convert response to cacheable format
        cache_data = {
            "status_code": response.status_code,
            "headers": response.headers,
            "body": response.body.decode('utf-8') if response.body else "",
            "response_time": response.response_time,
            "service_name": response.service_name,
            "request_id": response.request_id,
            "cached_at": datetime.now().isoformat()
        }
        
        await self._redis.setex(
            cache_key,
            ttl,
            json.dumps(cache_data)
        )
    
    def _generate_cache_key(
        self,
        path: str,
        query_params: Dict[str, str],
        user_id: Optional[str]
    ) -> str:
        """Generate cache key from request parameters"""
        key_parts = [path]
        
        if query_params:
            sorted_params = sorted(query_params.items())
            key_parts.append(json.dumps(sorted_params))
        
        if user_id:
            key_parts.append(f"user:{user_id}")
        
        key_string = "|".join(key_parts)
        return f"response_cache:{hashlib.sha256(key_string.encode()).hexdigest()}"
```

### 2. Health-Aware Load Balancing

```python
# src/routing/health_aware_load_balancer.py
class HealthAwareLoadBalancer:
    """Load balancer that considers service health and performance"""
    
    def __init__(self):
        self._strategy = "weighted_health"
        self._health_weight = 0.6
        self._performance_weight = 0.4
    
    def select_instance(
        self,
        instances: List[EnhancedServiceInstance],
        request: Optional[ProxyRequest] = None
    ) -> Optional[EnhancedServiceInstance]:
        """Select best instance based on health and performance"""
        
        if not instances:
            return None
        
        if len(instances) == 1:
            return instances[0]
        
        # Calculate weighted scores
        scored_instances = []
        for instance in instances:
            score = self._calculate_instance_score(instance)
            scored_instances.append((instance, score))
        
        # Sort by score (highest first)
        scored_instances.sort(key=lambda x: x[1], reverse=True)
        
        # Use weighted random selection from top instances
        return self._weighted_random_selection(scored_instances[:3])
    
    def _calculate_instance_score(self, instance: EnhancedServiceInstance) -> float:
        """Calculate instance score based on health and performance"""
        
        # Health score (0-1)
        health_score = {
            ServiceStatus.HEALTHY: 1.0,
            ServiceStatus.DEGRADED: 0.5,
            ServiceStatus.UNHEALTHY: 0.0,
            ServiceStatus.UNKNOWN: 0.3
        }.get(instance.status, 0.0)
        
        # Performance score (0-1, inverted from response time)
        max_response_time = 1000  # 1 second
        performance_score = max(
            0.0,
            1.0 - (instance.response_time_avg / max_response_time)
        )
        
        # Load score (0-1, inverted from load)
        load_score = max(0.0, 1.0 - instance.load_score)
        
        # Weighted combination
        total_score = (
            health_score * self._health_weight +
            performance_score * self._performance_weight +
            load_score * 0.2
        )
        
        return total_score
```

## Phase 3: Security Enhancements

### 1. Enhanced Authentication and Authorization

```python
# src/middleware/enhanced_auth.py
class EnhancedAuthMiddleware:
    """Enhanced authentication with role-based access control"""
    
    def __init__(self):
        self._permission_cache: Dict[str, Set[str]] = {}
        self._role_permissions: Dict[str, Set[str]] = {
            "admin": {"*"},
            "user": {"read:profile", "write:profile", "read:content"},
            "guest": {"read:public"}
        }
    
    async def authenticate_and_authorize(
        self,
        credentials: HTTPAuthorizationCredentials,
        required_permissions: List[str]
    ) -> Dict[str, Any]:
        """Authenticate user and check permissions"""
        
        # Authenticate user
        user_context = await self._authenticate_user(credentials)
        
        # Check permissions
        if required_permissions:
            user_permissions = await self._get_user_permissions(user_context)
            
            for permission in required_permissions:
                if not self._has_permission(user_permissions, permission):
                    raise HTTPException(
                        status_code=403,
                        detail=f"Insufficient permissions: {permission} required"
                    )
        
        return user_context
    
    def _has_permission(self, user_permissions: Set[str], required: str) -> bool:
        """Check if user has required permission"""
        if "*" in user_permissions:
            return True
        
        if required in user_permissions:
            return True
        
        # Check wildcard permissions
        for perm in user_permissions:
            if perm.endswith("*"):
                prefix = perm[:-1]
                if required.startswith(prefix):
                    return True
        
        return False
```

### 2. Request Validation

```python
# src/middleware/request_validator.py
from pydantic import BaseModel, ValidationError

class RequestValidator:
    """Validate incoming requests at gateway level"""
    
    def __init__(self):
        self._validation_rules: Dict[str, BaseModel] = {}
        self._max_body_size = 10 * 1024 * 1024  # 10MB
    
    async def validate_request(self, request: ProxyRequest, route: EnhancedRouteRule):
        """Validate request according to route rules"""
        
        # Size validation
        if request.body and len(request.body) > self._max_body_size:
            raise HTTPException(
                status_code=413,
                detail="Request body too large"
            )
        
        # Content type validation for POST/PUT
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not self._is_valid_content_type(content_type, route):
                raise HTTPException(
                    status_code=415,
                    detail="Unsupported content type"
                )
        
        # Path parameter validation
        await self._validate_path_parameters(request.path, route)
        
        # Query parameter validation
        await self._validate_query_parameters(request.query_params, route)
        
        # Body validation for JSON requests
        if request.body and "application/json" in request.headers.get("content-type", ""):
            await self._validate_json_body(request.body, route)
    
    def _is_valid_content_type(self, content_type: str, route: EnhancedRouteRule) -> bool:
        """Check if content type is allowed for the route"""
        allowed_types = route.metadata.get("allowed_content_types", [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data"
        ])
        
        return any(allowed in content_type for allowed in allowed_types)
```

## Phase 4: Monitoring and Observability

### 1. Distributed Tracing

```python
# src/utils/tracing.py
import opentelemetry
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

class DistributedTracing:
    """Distributed tracing implementation"""
    
    def __init__(self):
        self._tracer = trace.get_tracer(__name__)
        self._setup_tracing()
    
    def _setup_tracing(self):
        """Setup OpenTelemetry tracing"""
        trace.set_tracer_provider(TracerProvider())
        
        jaeger_exporter = JaegerExporter(
            agent_host_name="jaeger",
            agent_port=6831,
        )
        
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
    
    async def trace_request(self, request: ProxyRequest, route: EnhancedRouteRule):
        """Trace request through the gateway"""
        with self._tracer.start_as_current_span("gateway_request") as span:
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", request.path)
            span.set_attribute("service.name", route.service_name)
            span.set_attribute("request.id", request.request_id)
            
            # Add custom attributes
            span.set_attribute("gateway.version", "3.0.0")
            span.set_attribute("route.pattern", route.path_pattern)
            
            yield span
```

### 2. Metrics Collection

```python
# src/utils/metrics_collector.py
from prometheus_client import Counter, Histogram, Gauge
import time

class MetricsCollector:
    """Prometheus metrics collection"""
    
    def __init__(self):
        # Request metrics
        self.request_count = Counter(
            'gateway_requests_total',
            'Total gateway requests',
            ['method', 'service', 'status']
        )
        
        self.request_duration = Histogram(
            'gateway_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'service']
        )
        
        # Service health metrics
        self.service_health = Gauge(
            'gateway_service_health',
            'Service health status (1=healthy, 0=unhealthy)',
            ['service']
        )
        
        # Rate limiting metrics
        self.rate_limit_exceeded = Counter(
            'gateway_rate_limit_exceeded_total',
            'Rate limit exceeded count',
            ['identifier_type']
        )
    
    def record_request(
        self,
        method: str,
        service: str,
        status_code: int,
        duration: float
    ):
        """Record request metrics"""
        status_class = f"{status_code // 100}xx"
        
        self.request_count.labels(
            method=method,
            service=service,
            status=status_class
        ).inc()
        
        self.request_duration.labels(
            method=method,
            service=service
        ).observe(duration)
    
    def record_service_health(self, service: str, is_healthy: bool):
        """Record service health metrics"""
        self.service_health.labels(service=service).set(1 if is_healthy else 0)
```

## Implementation Timeline

### Week 1: Critical Fixes
- [ ] Fix port conflicts in docker-compose.yml
- [ ] Update service configuration with standardized ports
- [ ] Test service discovery and routing

### Week 2: Enhanced Routing
- [ ] Implement enhanced request router with priority
- [ ] Add request/response transformation support
- [ ] Update route rules with new features

### Week 3: Performance Optimization
- [ ] Implement connection pooling
- [ ] Add response caching
- [ ] Optimize health checking

### Week 4: Security Enhancement
- [ ] Add enhanced authentication middleware
- [ ] Implement request validation
- [ ] Add audit logging

### Week 5: Monitoring
- [ ] Setup distributed tracing
- [ ] Implement metrics collection
- [ ] Add performance dashboards

### Week 6: Testing and Documentation
- [ ] Comprehensive testing suite
- [ ] Update documentation
- [ ] Performance testing and optimization

This refinement plan addresses all critical issues identified in the analysis and provides a roadmap for transforming the API Gateway into a production-ready service orchestration platform.
