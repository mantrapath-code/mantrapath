"""
Load Balancer - Distributes requests across healthy service instances
"""
import random
from typing import List, Optional
from abc import ABC, abstractmethod
from src.core.models import ServiceInstance
from src.core.config import LoadBalancingStrategy, gateway_config

class LoadBalancer(ABC):
    """Abstract base class for load balancers"""
    
    @abstractmethod
    def select_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """Select a service instance from the list"""
        pass

class RoundRobinLoadBalancer(LoadBalancer):
    """Round-robin load balancing strategy"""
    
    def __init__(self):
        self._counters = {}
    
    def select_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        if not instances:
            return None
        
        service_name = instances[0].name
        if service_name not in self._counters:
            self._counters[service_name] = 0
        
        index = self._counters[service_name] % len(instances)
        self._counters[service_name] += 1
        
        return instances[index]

class WeightedLoadBalancer(LoadBalancer):
    """Weighted load balancing strategy"""
    
    def select_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        if not instances:
            return None
        
        total_weight = sum(instance.weight for instance in instances)
        if total_weight == 0:
            return random.choice(instances)
        
        # Generate a random number between 0 and total_weight
        rand_weight = random.randint(1, total_weight)
        
        cumulative_weight = 0
        for instance in instances:
            cumulative_weight += instance.weight
            if cumulative_weight >= rand_weight:
                return instance
        
        return instances[-1]  # Fallback

class LeastConnectionsLoadBalancer(LoadBalancer):
    """Least connections load balancing strategy"""
    
    def __init__(self):
        self._connections = {}
    
    def select_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        if not instances:
            return None
        
        # For now, we'll use a simple implementation
        # In a real implementation, we'd track active connections
        min_connections = float('inf')
        selected_instance = None
        
        for instance in instances:
            connections = self._connections.get(instance.id, 0)
            if connections < min_connections:
                min_connections = connections
                selected_instance = instance
        
        return selected_instance or instances[0]
    
    def increment_connections(self, instance_id: str):
        """Increment connection count for an instance"""
        self._connections[instance_id] = self._connections.get(instance_id, 0) + 1
    
    def decrement_connections(self, instance_id: str):
        """Decrement connection count for an instance"""
        if instance_id in self._connections:
            self._connections[instance_id] = max(0, self._connections[instance_id] - 1)

class RandomLoadBalancer(LoadBalancer):
    """Random load balancing strategy"""
    
    def select_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        if not instances:
            return None
        return random.choice(instances)

class LoadBalancerFactory:
    """Factory for creating load balancers"""
    
    @staticmethod
    def create_load_balancer(strategy: LoadBalancingStrategy) -> LoadBalancer:
        """Create a load balancer based on strategy"""
        if strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return RoundRobinLoadBalancer()
        elif strategy == LoadBalancingStrategy.WEIGHTED:
            return WeightedLoadBalancer()
        elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return LeastConnectionsLoadBalancer()
        elif strategy == LoadBalancingStrategy.RANDOM:
            return RandomLoadBalancer()
        else:
            # Default to round-robin
            return RoundRobinLoadBalancer()
