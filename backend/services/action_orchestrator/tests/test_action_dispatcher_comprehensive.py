"""
Comprehensive tests for Action Dispatcher - targeting 80% coverage
"""
import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from src.core.action_dispatcher import ActionDispatcher


@pytest.mark.asyncio
class TestActionDispatcherComprehensive:
    """Comprehensive test suite for Action Dispatcher"""

    @pytest.fixture
    async def dispatcher(self):
        """Create action dispatcher instance"""
        dispatcher = ActionDispatcher()
        yield dispatcher
        await dispatcher.close()

    @pytest.fixture
    def mock_response(self):
        """Mock HTTP response"""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"status": "success", "data": {"result": "test"}}
        return response

    @pytest.fixture
    def mock_error_response(self):
        """Mock HTTP error response"""
        response = MagicMock()
        response.status_code = 500
        response.json.return_value = {"error": "Internal server error"}
        response.text = "Internal server error"
        return response

    async def test_initialization(self):
        """Test dispatcher initialization"""
        dispatcher = ActionDispatcher()
        
        assert hasattr(dispatcher, 'service_endpoints')
        assert hasattr(dispatcher, 'http_client')
        assert hasattr(dispatcher, 'circuit_breakers')
        assert isinstance(dispatcher.service_endpoints, dict)
        assert len(dispatcher.service_endpoints) > 0
        
        await dispatcher.close()

    async def test_service_endpoints_configuration(self, dispatcher):
        """Test service endpoint configuration"""
        endpoints = dispatcher.service_endpoints
        
        # Check required services are configured
        required_services = [
            "mood_service", "journal_service", "chatbot_service",
            "profile_service", "community_service", "analytics_service", "content_service"
        ]
        
        for service in required_services:
            assert service in endpoints
            assert "base_url" in endpoints[service]
            assert "timeout" in endpoints[service]
            assert "health_endpoint" in endpoints[service]

    async def test_dispatch_action_success(self, dispatcher, mock_response):
        """Test successful action dispatch"""
        with patch.object(dispatcher.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            result = await dispatcher.dispatch_action(
                service_name="mood_service",
                action_type="create_mood_entry",
                parameters={"mood": "happy", "notes": "test"},
                timeout_seconds=30,
                retry_count=3
            )
            
            assert result == {"status": "success", "data": {"result": "test"}}
            mock_post.assert_called_once()

    async def test_dispatch_action_unknown_service(self, dispatcher):
        """Test dispatch to unknown service"""
        with pytest.raises(Exception) as exc_info:
            await dispatcher.dispatch_action(
                service_name="unknown_service",
                action_type="test_action",
                parameters={}
            )
        
        assert "Unknown service: unknown_service" in str(exc_info.value)

    async def test_dispatch_action_circuit_breaker_open(self, dispatcher):
        """Test dispatch when circuit breaker is open"""
        # Manually set circuit breaker to open
        dispatcher.circuit_breakers["mood_service"] = {
            "state": "open",
            "failure_count": 10,
            "last_failure": time.time(),
            "failure_threshold": 5,
            "recovery_timeout": 60
        }
        
        with pytest.raises(Exception) as exc_info:
            await dispatcher.dispatch_action(
                service_name="mood_service",
                action_type="test_action",
                parameters={}
            )
        
        assert "currently unavailable (circuit breaker open)" in str(exc_info.value)

    async def test_dispatch_action_with_retries(self, dispatcher, mock_error_response):
        """Test action dispatch with retries"""
        with patch.object(dispatcher.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_error_response
            
            with pytest.raises(Exception) as exc_info:
                await dispatcher.dispatch_action(
                    service_name="mood_service",
                    action_type="test_action",
                    parameters={},
                    retry_count=2
                )
            
            # Should have been called 3 times (initial + 2 retries)
            assert mock_post.call_count == 3
            assert "failed after 3 attempts" in str(exc_info.value)

    async def test_dispatch_action_timeout(self, dispatcher):
        """Test action dispatch timeout"""
        with patch.object(dispatcher.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Timeout")
            
            with pytest.raises(Exception) as exc_info:
                await dispatcher.dispatch_action(
                    service_name="mood_service",
                    action_type="test_action",
                    parameters={},
                    retry_count=1
                )
            
            assert "Service timeout" in str(exc_info.value)

    async def test_dispatch_action_connection_error(self, dispatcher):
        """Test action dispatch connection error"""
        with patch.object(dispatcher.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.RequestError("Connection failed")
            
            with pytest.raises(Exception) as exc_info:
                await dispatcher.dispatch_action(
                    service_name="mood_service",
                    action_type="test_action",
                    parameters={},
                    retry_count=1
                )
            
            assert "Service connection error" in str(exc_info.value)

    async def test_execute_service_action_success(self, dispatcher, mock_response):
        """Test successful service action execution"""
        endpoint_config = {
            "base_url": "http://test-service:8000",
            "timeout": 30,
            "health_endpoint": "/health"
        }
        
        request_data = {
            "action_type": "test_action",
            "parameters": {"test": "data"},
            "timeout": 30
        }
        
        with patch.object(dispatcher.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            result = await dispatcher._execute_service_action(
                "test_service", endpoint_config, request_data, 30
            )
            
            assert result == {"status": "success", "data": {"result": "test"}}

    async def test_execute_service_action_error_response(self, dispatcher, mock_error_response):
        """Test service action execution with error response"""
        endpoint_config = {
            "base_url": "http://test-service:8000",
            "timeout": 30,
            "health_endpoint": "/health"
        }
        
        request_data = {
            "action_type": "test_action",
            "parameters": {"test": "data"},
            "timeout": 30
        }
        
        with patch.object(dispatcher.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_error_response
            
            with pytest.raises(Exception) as exc_info:
                await dispatcher._execute_service_action(
                    "test_service", endpoint_config, request_data, 30
                )
            
            assert "Service error: Internal server error" in str(exc_info.value)

    async def test_is_service_available_closed_circuit(self, dispatcher):
        """Test service availability with closed circuit breaker"""
        # Circuit breaker should be closed by default
        is_available = await dispatcher._is_service_available("mood_service")
        assert is_available is True

    async def test_is_service_available_open_circuit(self, dispatcher):
        """Test service availability with open circuit breaker"""
        # Set circuit breaker to open
        dispatcher.circuit_breakers["mood_service"] = {
            "state": "open",
            "failure_count": 10,
            "last_failure": time.time(),
            "failure_threshold": 5,
            "recovery_timeout": 60
        }
        
        is_available = await dispatcher._is_service_available("mood_service")
        assert is_available is False

    async def test_is_service_available_half_open_recovery(self, dispatcher):
        """Test service availability with half-open circuit recovery"""
        # Set circuit breaker to open with old timestamp
        old_timestamp = time.time() - 120  # 2 minutes ago
        dispatcher.circuit_breakers["mood_service"] = {
            "state": "open",
            "failure_count": 10,
            "last_failure": old_timestamp,
            "failure_threshold": 5,
            "recovery_timeout": 60
        }
        
        is_available = await dispatcher._is_service_available("mood_service")
        assert is_available is True
        # Should move to half-open state
        assert dispatcher.circuit_breakers["mood_service"]["state"] == "half_open"

    async def test_record_service_failure(self, dispatcher):
        """Test recording service failure"""
        # Initially no circuit breaker
        assert "test_service" not in dispatcher.circuit_breakers
        
        await dispatcher._record_service_failure("test_service")
        
        # Should create circuit breaker with failure recorded
        assert "test_service" in dispatcher.circuit_breakers
        assert dispatcher.circuit_breakers["test_service"]["failure_count"] == 1
        assert dispatcher.circuit_breakers["test_service"]["last_failure"] is not None

    async def test_record_service_failure_opens_circuit(self, dispatcher):
        """Test circuit breaker opens after threshold failures"""
        # Set up circuit breaker close to threshold
        dispatcher.circuit_breakers["test_service"] = {
            "state": "closed",
            "failure_count": 4,
            "last_failure": None,
            "failure_threshold": 5,
            "recovery_timeout": 60
        }
        
        # Record one more failure to cross threshold
        await dispatcher._record_service_failure("test_service")
        
        # Circuit breaker should be open
        assert dispatcher.circuit_breakers["test_service"]["state"] == "open"
        assert dispatcher.circuit_breakers["test_service"]["failure_count"] == 5

    async def test_mark_service_healthy_from_half_open(self, dispatcher):
        """Test marking service healthy from half-open state"""
        dispatcher.circuit_breakers["test_service"] = {
            "state": "half_open",
            "failure_count": 3,
            "last_failure": time.time(),
            "failure_threshold": 5,
            "recovery_timeout": 60
        }
        
        await dispatcher._mark_service_healthy("test_service")
        
        # Should move to closed and reset counters
        assert dispatcher.circuit_breakers["test_service"]["state"] == "closed"
        assert dispatcher.circuit_breakers["test_service"]["failure_count"] == 0
        assert dispatcher.circuit_breakers["test_service"]["last_failure"] is None

    async def test_mark_service_healthy_from_closed(self, dispatcher):
        """Test marking service healthy from closed state"""
        dispatcher.circuit_breakers["test_service"] = {
            "state": "closed",
            "failure_count": 2,
            "last_failure": time.time(),
            "failure_threshold": 5,
            "recovery_timeout": 60
        }
        
        await dispatcher._mark_service_healthy("test_service")
        
        # Should reset failure count
        assert dispatcher.circuit_breakers["test_service"]["state"] == "closed"
        assert dispatcher.circuit_breakers["test_service"]["failure_count"] == 0

    async def test_mark_service_unhealthy(self, dispatcher):
        """Test marking service as unhealthy"""
        await dispatcher._mark_service_unhealthy("test_service")
        
        # Should create/update circuit breaker to open state
        assert "test_service" in dispatcher.circuit_breakers
        assert dispatcher.circuit_breakers["test_service"]["state"] == "open"
        assert dispatcher.circuit_breakers["test_service"]["last_failure"] is not None

    async def test_health_check_service_success(self, dispatcher):
        """Test successful service health check"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        with patch.object(dispatcher.http_client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            
            is_healthy = await dispatcher.health_check_service("mood_service")
            assert is_healthy is True

    async def test_health_check_service_failure(self, dispatcher):
        """Test failed service health check"""
        with patch.object(dispatcher.http_client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Connection failed")
            
            is_healthy = await dispatcher.health_check_service("mood_service")
            assert is_healthy is False

    async def test_health_check_unknown_service(self, dispatcher):
        """Test health check for unknown service"""
        is_healthy = await dispatcher.health_check_service("unknown_service")
        assert is_healthy is False

    async def test_get_service_status(self, dispatcher):
        """Test getting service status"""
        with patch.object(dispatcher, 'health_check_service', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = True
            
            status = await dispatcher.get_service_status()
            
            assert isinstance(status, dict)
            # Should include all configured services
            for service_name in dispatcher.service_endpoints.keys():
                assert service_name in status
                assert "circuit_breaker_state" in status[service_name]
                assert "failure_count" in status[service_name]
                assert "health_check" in status[service_name]
                assert "available" in status[service_name]

    async def test_get_service_url(self, dispatcher):
        """Test getting service URL"""
        with patch('config.settings') as mock_settings:
            mock_settings.MOOD_SERVICE_URL = "http://mood:8003"
            mock_settings.CONTENT_SERVICE_URL = "http://content:8005"
            
            mood_url = dispatcher._get_service_url("mood_service")
            content_url = dispatcher._get_service_url("content_service")
            unknown_url = dispatcher._get_service_url("unknown_service")
            
            assert mood_url == "http://mood:8003"
            assert content_url == "http://content:8005"
            assert unknown_url == "http://localhost:8000"  # Default

    async def test_close(self, dispatcher):
        """Test closing dispatcher"""
        with patch.object(dispatcher.http_client, 'aclose', new_callable=AsyncMock) as mock_close:
            await dispatcher.close()
            mock_close.assert_called_once()

    async def test_dispatch_with_exponential_backoff(self, dispatcher):
        """Test exponential backoff in retry logic"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        with patch.object(dispatcher.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = [
                Exception("First failure"),
                Exception("Second failure"),
                mock_response  # Success on third try
            ]
            
            with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                result = await dispatcher.dispatch_action(
                    service_name="mood_service",
                    action_type="test_action",
                    parameters={},
                    retry_count=2
                )
                
                # Check that sleep was called for backoff
                assert mock_sleep.call_count == 2
                # Verify exponential backoff times
                sleep_calls = [call.args[0] for call in mock_sleep.call_args_list]
                assert sleep_calls[0] == 2  # 2^1
                assert sleep_calls[1] == 4  # 2^2
