"""
Request Proxy - Handles forwarding requests to backend services
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import httpx
from src.core.models import ProxyRequest, ProxyResponse, ServiceInstance
from src.core.config import gateway_config

logger = logging.getLogger(__name__)

class RequestProxy:
    """Handles proxying requests to backend services"""
    
    def __init__(self):
        self._client_timeout = httpx.Timeout(
            timeout=gateway_config.health_check_timeout,
            read=gateway_config.health_check_timeout,
            write=gateway_config.health_check_timeout
        )
    
    async def proxy_request(
        self,
        request: ProxyRequest,
        target_service: ServiceInstance,
        timeout: int = 30
    ) -> ProxyResponse:
        """Proxy a request to a target service"""
        start_time = datetime.now()
        
        try:
            # Construct target URL
            target_url = f"{target_service.url.rstrip('/')}{request.path}"
            
            # Prepare headers (exclude hop-by-hop headers)
            headers = self._prepare_headers(request.headers)
            
            # Add request ID for tracing
            headers['X-Request-ID'] = request.request_id
            headers['X-Forwarded-By'] = 'mantrapath-gateway'
            
            # Create HTTP client with custom timeout
            client_timeout = httpx.Timeout(timeout=timeout)
            
            async with httpx.AsyncClient(timeout=client_timeout) as client:
                # Make the request
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    params=request.query_params,
                    content=request.body
                )
                
                response_time = (datetime.now() - start_time).total_seconds()
                
                # Prepare response headers (exclude hop-by-hop headers)
                response_headers = self._prepare_response_headers(dict(response.headers))
                
                proxy_response = ProxyResponse(
                    status_code=response.status_code,
                    headers=response_headers,
                    body=response.content,
                    response_time=response_time,
                    service_name=target_service.name,
                    request_id=request.request_id
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
        clean_headers['X-Gateway-Version'] = '1.0.0'
        
        return clean_headers
    
    def _log_request(
        self,
        request: ProxyRequest,
        response: ProxyResponse,
        service: ServiceInstance
    ):
        """Log request details"""
        if response.status_code >= 400:
            log_level = logging.WARNING if response.status_code < 500 else logging.ERROR
            logger.log(
                log_level,
                f"Request failed: {request.method} {request.path} -> "
                f"{service.name} ({service.url}) | "
                f"Status: {response.status_code} | "
                f"Time: {response.response_time:.3f}s | "
                f"RequestID: {request.request_id}"
            )
        else:
            logger.info(
                f"Request successful: {request.method} {request.path} -> "
                f"{service.name} | "
                f"Status: {response.status_code} | "
                f"Time: {response.response_time:.3f}s | "
                f"RequestID: {request.request_id}"
            )
    
    async def health_check(self, service: ServiceInstance) -> bool:
        """Perform a health check on a service"""
        try:
            health_url = f"{service.url.rstrip('/')}{service.health_path}"
            
            async with httpx.AsyncClient(timeout=self._client_timeout) as client:
                response = await client.get(health_url)
                return response.status_code == 200
                
        except Exception as e:
            logger.debug(f"Health check failed for {service.name}: {e}")
            return False
