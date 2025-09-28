"""
Request Proxy - Handles forwarding requests to backend services with connection pooling
"""
import logging
from typing import Optional, Dict, Any, AsyncIterator
from datetime import datetime
import httpx
from src.core.models import ProxyRequest, ProxyResponse, ServiceInstance
from src.core.config import gateway_config
from src.utils.connection_pool import get_connection_pool

logger = logging.getLogger(__name__)

class RequestProxy:
    """Handles proxying requests to backend services with enhanced connection management"""
    
    def __init__(self):
        self._connection_pool = get_connection_pool()
        self._default_timeout = gateway_config.health_check_timeout
    
    async def proxy_request(
        self,
        request: ProxyRequest,
        target_service: ServiceInstance,
        timeout: int = 30
    ) -> ProxyResponse:
        """Proxy a request to a target service using connection pooling"""
        start_time = datetime.now()
        
        try:
            # Get HTTP client from connection pool
            client = await self._connection_pool.get_client(target_service.name)
            
            # Construct target URL
            target_url = f"{target_service.url.rstrip('/')}{request.path}"
            
            # Prepare headers (exclude hop-by-hop headers)
            headers = self._prepare_headers(request.headers)
            
            # Add request tracking headers
            headers.update({
                'X-Request-ID': request.request_id,
                'X-Forwarded-By': 'mantrapath-gateway',
                'X-Gateway-Service': target_service.name,
                'X-Gateway-Timestamp': str(int(start_time.timestamp()))
            })
            
            # Create request with timeout
            request_timeout = httpx.Timeout(timeout)
            
            # Make the request using the pooled client
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=request.body,
                timeout=request_timeout
            )
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Prepare response headers (exclude hop-by-hop headers)
            response_headers = self._prepare_response_headers(dict(response.headers))

            # Decide if we should stream (audio or large payload)
            content_type = response_headers.get("Content-Type", "").lower()
            content_length_header = response_headers.get("Content-Length")
            should_stream = False
            try:
                if content_length_header and int(content_length_header) > 512_000:  # >500KB
                    should_stream = True
            except ValueError:
                pass
            if any(ct in content_type for ct in ["audio/", "video/", "application/octet-stream"]):
                # Stream audio/video by default unless tiny
                if content_length_header is None or should_stream or b"RIFF" in response.content[:8]:
                    should_stream = True

            if should_stream and hasattr(response, "aiter_bytes"):
                async def stream_iter() -> AsyncIterator[bytes]:  # type: ignore
                    async for chunk in response.aiter_bytes():
                        if chunk:
                            yield chunk
                proxy_response = ProxyResponse(
                    status_code=response.status_code,
                    headers=response_headers,
                    body=b"",  # Empty body when streaming
                    response_time=response_time,
                    service_name=target_service.name,
                    request_id=request.request_id,
                    streaming=True,
                    stream_iterator=stream_iter()
                )
            else:
                proxy_response = ProxyResponse(
                    status_code=response.status_code,
                    headers=response_headers,
                    body=response.content,
                    response_time=response_time,
                    service_name=target_service.name,
                    request_id=request.request_id,
                    streaming=False
                )
            
            # Log request details
            self._log_request(request, proxy_response, target_service)
            
            return proxy_response
                
        except httpx.TimeoutException:
            response_time = (datetime.now() - start_time).total_seconds()
            logger.warning(
                f"Request timeout for {target_service.name}: {request.method} {request.path} "
                f"(timeout: {timeout}s, actual: {response_time:.3f}s)"
            )
            
            return ProxyResponse(
                status_code=504,
                headers={"Content-Type": "application/json"},
                body=b'{"error": "Gateway Timeout", "message": "Service request timed out"}',
                response_time=response_time,
                service_name=target_service.name,
                request_id=request.request_id
            )
            
        except httpx.ConnectError:
            response_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Connection error to {target_service.name}: {target_service.url}")
            
            return ProxyResponse(
                status_code=503,
                headers={"Content-Type": "application/json"},
                body=b'{"error": "Service Unavailable", "message": "Cannot connect to service"}',
                response_time=response_time,
                service_name=target_service.name,
                request_id=request.request_id
            )
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Proxy error for {target_service.name}: {e}")
            
            return ProxyResponse(
                status_code=502,
                headers={"Content-Type": "application/json"},
                body=b'{"error": "Bad Gateway", "message": "Service error occurred"}',
                response_time=response_time,
                service_name=target_service.name,
                request_id=request.request_id
            )
    
    def _prepare_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Prepare headers for proxying (remove hop-by-hop headers)"""
        hop_by_hop_headers = {
            'connection', 'keep-alive', 'proxy-authenticate',
            'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade'
        }
        
        return {
            key: value for key, value in headers.items()
            if key.lower() not in hop_by_hop_headers
        }
    
    def _prepare_response_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Prepare response headers (remove hop-by-hop headers)"""
        hop_by_hop_headers = {
            'connection', 'keep-alive', 'proxy-authenticate',
            'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade'
        }
        
        clean_headers = {
            key: value for key, value in headers.items()
            if key.lower() not in hop_by_hop_headers
        }
        
        # Add gateway headers
        clean_headers['X-Gateway'] = 'mantrapath-gateway'
        clean_headers['X-Gateway-Version'] = '3.0.0'
        clean_headers['X-Processing-Time'] = str(datetime.now().timestamp())
        
        return clean_headers
    
    def _log_request(
        self,
        request: ProxyRequest,
        response: ProxyResponse,
        service: ServiceInstance
    ):
        """Log request details with enhanced information"""
        log_data = {
            "method": request.method,
            "path": request.path, 
            "service": service.name,
            "service_url": service.url,
            "status_code": response.status_code,
            "response_time": f"{response.response_time:.3f}s",
            "request_id": request.request_id
        }
        
        if response.status_code >= 400:
            log_level = logging.WARNING if response.status_code < 500 else logging.ERROR
            logger.log(
                log_level,
                f"Request failed: {request.method} {request.path} -> "
                f"{service.name} ({service.url}) | "
                f"Status: {response.status_code} | "
                f"Time: {response.response_time:.3f}s | "
                f"RequestID: {request.request_id}",
                extra=log_data
            )
        else:
            logger.info(
                f"Request successful: {request.method} {request.path} -> "
                f"{service.name} | "
                f"Status: {response.status_code} | "
                f"Time: {response.response_time:.3f}s | "
                f"RequestID: {request.request_id}",
                extra=log_data
            )
    
    async def health_check(self, service: ServiceInstance) -> bool:
        """Perform a health check on a service using connection pool"""
        try:
            client = await self._connection_pool.get_client(service.name)
            health_url = f"{service.url.rstrip('/')}{service.health_path}"
            
            # Use a shorter timeout for health checks
            health_timeout = httpx.Timeout(self._default_timeout)
            
            response = await client.get(health_url, timeout=health_timeout)
            is_healthy = response.status_code == 200
            
            logger.debug(f"Health check for {service.name}: {'✓' if is_healthy else '✗'} ({response.status_code})")
            return is_healthy
                
        except Exception as e:
            logger.debug(f"Health check failed for {service.name}: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup connection pool"""
        await self._connection_pool.close_all()
