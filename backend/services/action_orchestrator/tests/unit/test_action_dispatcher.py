"""
Unit tests for Action Dispatcher
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import Response
import asyncio

from src.core.action_dispatcher import ActionDispatcher
from src.models import ServiceAction


class TestActionDispatcher:
    """Test ActionDispatcher functionality"""
    
    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client"""
        client = AsyncMock()
        return client
    
    @pytest.fixture
    def action_dispatcher(self, mock_http_client):
        """Create action dispatcher with mocked HTTP client"""
        dispatcher = ActionDispatcher()
        dispatcher.http_client = mock_http_client
        return dispatcher
    
    @pytest.fixture
    def sample_action(self):
        """Sample service action"""
        return ServiceAction(
            service_name="journal_service",
            action_type="create_entry",
            parameters={
                "title": "Test Entry",
                "content": "Test content",
                "user_id": "user123"
            },
            timeout_seconds=30
        )
    
    @pytest.mark.asyncio
    async def test_execute_action_success(self, action_dispatcher, sample_action, mock_http_client):
        """Test successful action execution"""
        # Mock successful response
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "id": "entry123"}
        mock_http_client.post.return_value = mock_response
        
        result = await action_dispatcher.execute_action(sample_action)
        
        assert result.success is True
        assert result.data["id"] == "entry123"
        assert result.execution_time > 0
        mock_http_client.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_action_http_error(self, action_dispatcher, sample_action, mock_http_client):
        """Test action execution with HTTP error"""
        # Mock error response
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_http_client.post.return_value = mock_response
        
        result = await action_dispatcher.execute_action(sample_action)
        
        assert result.success is False
        assert "500" in result.error_message
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_execute_action_timeout(self, action_dispatcher, sample_action, mock_http_client):
        """Test action execution timeout"""
        # Mock timeout
        mock_http_client.post.side_effect = asyncio.TimeoutError()
        
        result = await action_dispatcher.execute_action(sample_action)
        
        assert result.success is False
        assert "timeout" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_execute_action_with_retry_success(self, action_dispatcher, sample_action, mock_http_client):
        """Test action execution with retry mechanism - eventual success"""
        # First call fails, second succeeds
        mock_response_fail = MagicMock(spec=Response)
        mock_response_fail.status_code = 503
        mock_response_fail.text = "Service Unavailable"
        
        mock_response_success = MagicMock(spec=Response)
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"success": True, "id": "entry123"}
        
        mock_http_client.post.side_effect = [mock_response_fail, mock_response_success]
        
        result = await action_dispatcher.execute_action(sample_action)
        
        assert result.success is True
        assert result.data["id"] == "entry123"
        assert mock_http_client.post.call_count == 2
    
    @pytest.mark.asyncio
    async def test_execute_action_retry_exhausted(self, action_dispatcher, sample_action, mock_http_client):
        """Test action execution when all retries are exhausted"""
        # All calls fail
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 503
        mock_response.text = "Service Unavailable"
        mock_http_client.post.return_value = mock_response
        
        result = await action_dispatcher.execute_action(sample_action)
        
        assert result.success is False
        assert "retries exhausted" in result.error_message.lower()
        assert mock_http_client.post.call_count == sample_action.retry_count + 1  # Initial + retries
    
    def test_circuit_breaker_closed_state(self, action_dispatcher):
        """Test circuit breaker in closed state"""
        service = "test_service"
        state = action_dispatcher._get_circuit_breaker_state(service)
        
        assert state == "closed"
        assert action_dispatcher._should_allow_request(service) is True
    
    def test_circuit_breaker_open_state(self, action_dispatcher):
        """Test circuit breaker transitions to open state"""
        service = "test_service"
        
        # Simulate multiple failures to open circuit breaker
        for _ in range(action_dispatcher.circuit_breaker_threshold + 1):
            action_dispatcher._record_failure(service)
        
        assert action_dispatcher._get_circuit_breaker_state(service) == "open"
        assert action_dispatcher._should_allow_request(service) is False
    
    def test_circuit_breaker_half_open_state(self, action_dispatcher):
        """Test circuit breaker transitions to half-open state"""
        service = "test_service"
        
        # Open the circuit breaker
        for _ in range(action_dispatcher.circuit_breaker_threshold + 1):
            action_dispatcher._record_failure(service)
        
        # Simulate timeout passing
        action_dispatcher.circuit_breakers[service]["last_failure"] = 0
        
        assert action_dispatcher._get_circuit_breaker_state(service) == "half_open"
        assert action_dispatcher._should_allow_request(service) is True
    
    def test_circuit_breaker_success_resets_failures(self, action_dispatcher):
        """Test that successful requests reset failure count"""
        service = "test_service"
        
        # Record some failures
        for _ in range(2):
            action_dispatcher._record_failure(service)
        
        # Record success
        action_dispatcher._record_success(service)
        
        # Should reset failure count
        assert action_dispatcher.circuit_breakers[service]["failure_count"] == 0
        assert action_dispatcher._get_circuit_breaker_state(service) == "closed"
    
    def test_get_service_url_known_service(self, action_dispatcher):
        """Test getting URL for known service"""
        url = action_dispatcher._get_service_url("journal_service")
        assert url is not None
        assert "journal" in url.lower()
    
    def test_get_service_url_unknown_service(self, action_dispatcher):
        """Test getting URL for unknown service"""
        url = action_dispatcher._get_service_url("unknown_service")
        assert url is None
    
    def test_build_request_payload(self, action_dispatcher, sample_action):
        """Test building request payload"""
        payload = action_dispatcher._build_request_payload(sample_action)
        
        assert payload["action_type"] == "create_entry"
        assert payload["parameters"]["title"] == "Test Entry"
        assert payload["cultural_adaptations"] == sample_action.cultural_adaptations
        assert "timestamp" in payload
    
    def test_validate_response_success(self, action_dispatcher):
        """Test validating successful response"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": {"id": "123"}}
        
        is_valid, error = action_dispatcher._validate_response(mock_response)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_response_client_error(self, action_dispatcher):
        """Test validating client error response"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        is_valid, error = action_dispatcher._validate_response(mock_response)
        
        assert is_valid is False
        assert "400" in error
    
    def test_validate_response_server_error(self, action_dispatcher):
        """Test validating server error response"""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        is_valid, error = action_dispatcher._validate_response(mock_response)
        
        assert is_valid is False
        assert "500" in error
    
    def test_calculate_backoff_delay(self, action_dispatcher):
        """Test calculating exponential backoff delay"""
        # Test increasing delays
        delay1 = action_dispatcher._calculate_backoff_delay(1)
        delay2 = action_dispatcher._calculate_backoff_delay(2)
        delay3 = action_dispatcher._calculate_backoff_delay(3)
        
        assert delay1 < delay2 < delay3
        assert delay1 >= 1.0  # Base delay
        assert delay3 <= 16.0  # Max delay with exponential backoff
    
    @pytest.mark.asyncio
    async def test_execute_action_circuit_breaker_open(self, action_dispatcher, sample_action):
        """Test action execution when circuit breaker is open"""
        service = sample_action.service_name
        
        # Open the circuit breaker
        for _ in range(action_dispatcher.circuit_breaker_threshold + 1):
            action_dispatcher._record_failure(service)
        
        result = await action_dispatcher.execute_action(sample_action)
        
        assert result.success is False
        assert "circuit breaker open" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_execute_multiple_actions_parallel(self, action_dispatcher, mock_http_client):
        """Test executing multiple actions in parallel"""
        actions = [
            ServiceAction(
                service_name="journal_service",
                action_type="create_entry",
                parameters={"title": f"Entry {i}"}
            )
            for i in range(3)
        ]
        
        # Mock successful responses
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "id": "123"}
        mock_http_client.post.return_value = mock_response
        
        results = await action_dispatcher.execute_actions_parallel(actions)
        
        assert len(results) == 3
        assert all(result.success for result in results)
        assert mock_http_client.post.call_count == 3
    
    @pytest.mark.asyncio
    async def test_execute_actions_with_timeout_limit(self, action_dispatcher):
        """Test executing actions with global timeout limit"""
        action = ServiceAction(
            service_name="slow_service",
            action_type="slow_operation",
            parameters={},
            timeout_seconds=60  # Long timeout
        )
        
        # Mock slow response
        async def slow_post(*args, **kwargs):
            await asyncio.sleep(2)  # Simulate slow response
            mock_response = MagicMock(spec=Response)
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}
            return mock_response
        
        action_dispatcher.http_client.post = slow_post
        
        # Execute with short global timeout
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                action_dispatcher.execute_action(action),
                timeout=1.0
            )
    
    def test_get_circuit_breaker_stats(self, action_dispatcher):
        """Test getting circuit breaker statistics"""
        service = "test_service"
        
        # Record some failures and successes
        action_dispatcher._record_failure(service)
        action_dispatcher._record_failure(service)
        action_dispatcher._record_success(service)
        
        stats = action_dispatcher.get_circuit_breaker_stats()
        
        assert service in stats
        assert "state" in stats[service]
        assert "failure_count" in stats[service]
        assert "last_failure" in stats[service]
    
    def test_reset_circuit_breaker(self, action_dispatcher):
        """Test manually resetting circuit breaker"""
        service = "test_service"
        
        # Open the circuit breaker
        for _ in range(action_dispatcher.circuit_breaker_threshold + 1):
            action_dispatcher._record_failure(service)
        
        assert action_dispatcher._get_circuit_breaker_state(service) == "open"
        
        # Reset it
        action_dispatcher.reset_circuit_breaker(service)
        
        assert action_dispatcher._get_circuit_breaker_state(service) == "closed"
        assert action_dispatcher.circuit_breakers[service]["failure_count"] == 0
