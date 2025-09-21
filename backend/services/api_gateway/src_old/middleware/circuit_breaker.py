"""
Circuit Breaker Middleware
"""
from typing import Dict
from datetime import datetime, timedelta
from enum import Enum
from src.core.models import CircuitBreakerState
from src.core.config import gateway_config

class CircuitState(str, Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """Circuit breaker implementation for service resilience"""
    
    def __init__(self):
        self._circuits: Dict[str, CircuitBreakerState] = {}
        self._failure_threshold = gateway_config.circuit_breaker_failure_threshold
        self._recovery_timeout = gateway_config.circuit_breaker_recovery_timeout
    
    def is_call_allowed(self, service_name: str) -> bool:
        """Check if a call to the service is allowed"""
        if not gateway_config.circuit_breaker_enabled:
            return True
        
        circuit = self._get_or_create_circuit(service_name)
        now = datetime.now()
        
        if circuit.state == CircuitState.CLOSED:
            # Normal operation - allow call
            return True
        
        elif circuit.state == CircuitState.OPEN:
            # Circuit is open - check if we should transition to half-open
            if circuit.next_attempt_time and now >= circuit.next_attempt_time:
                circuit.state = CircuitState.HALF_OPEN
                return True  # Allow one test call
            else:
                return False  # Still in open state
        
        elif circuit.state == CircuitState.HALF_OPEN:
            # Only allow one call at a time in half-open state
            return True
        
        return False
    
    def record_success(self, service_name: str):
        """Record a successful call"""
        circuit = self._get_or_create_circuit(service_name)
        
        if circuit.state == CircuitState.HALF_OPEN:
            # Success in half-open state - close the circuit
            circuit.state = CircuitState.CLOSED
            circuit.failure_count = 0
            circuit.last_failure_time = None
            circuit.next_attempt_time = None
        
        elif circuit.state == CircuitState.CLOSED:
            # Reset failure count on success
            circuit.failure_count = max(0, circuit.failure_count - 1)
    
    def record_failure(self, service_name: str):
        """Record a failed call"""
        circuit = self._get_or_create_circuit(service_name)
        circuit.failure_count += 1
        circuit.last_failure_time = datetime.now()
        
        if circuit.state == CircuitState.CLOSED:
            # Check if we should open the circuit
            if circuit.failure_count >= self._failure_threshold:
                circuit.state = CircuitState.OPEN
                circuit.next_attempt_time = datetime.now() + timedelta(
                    seconds=self._recovery_timeout
                )
        
        elif circuit.state == CircuitState.HALF_OPEN:
            # Failure in half-open state - back to open
            circuit.state = CircuitState.OPEN
            circuit.next_attempt_time = datetime.now() + timedelta(
                seconds=self._recovery_timeout
            )
    
    def get_circuit_state(self, service_name: str) -> CircuitBreakerState:
        """Get the current state of a circuit"""
        return self._get_or_create_circuit(service_name)
    
    def _get_or_create_circuit(self, service_name: str) -> CircuitBreakerState:
        """Get or create a circuit breaker state for a service"""
        if service_name not in self._circuits:
            self._circuits[service_name] = CircuitBreakerState(
                service_name=service_name,
                state=CircuitState.CLOSED,
                failure_count=0
            )
        
        return self._circuits[service_name]
    
    def get_all_circuits(self) -> Dict[str, CircuitBreakerState]:
        """Get all circuit breaker states"""
        return self._circuits.copy()
    
    def reset_circuit(self, service_name: str):
        """Manually reset a circuit breaker"""
        if service_name in self._circuits:
            circuit = self._circuits[service_name]
            circuit.state = CircuitState.CLOSED
            circuit.failure_count = 0
            circuit.last_failure_time = None
            circuit.next_attempt_time = None
