"""
Test Load Balancer functionality
"""
import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from routing.load_balancer import (
    RoundRobinLoadBalancer,
    WeightedLoadBalancer,
    RandomLoadBalancer,
    LoadBalancerFactory
)
from core.models import ServiceInstance, ServiceStatus
from core.config import LoadBalancingStrategy

class TestLoadBalancers:
    """Test different load balancing strategies"""
    
    def setup_method(self):
        """Set up test data"""
        self.services = [
            ServiceInstance(
                id="service-1",
                name="test-service",
                url="http://test-service:8001",
                weight=1,
                status=ServiceStatus.HEALTHY
            ),
            ServiceInstance(
                id="service-2",
                name="test-service", 
                url="http://test-service:8002",
                weight=2,
                status=ServiceStatus.HEALTHY
            ),
            ServiceInstance(
                id="service-3",
                name="test-service",
                url="http://test-service:8003",
                weight=1,
                status=ServiceStatus.HEALTHY
            )
        ]
    
    def test_round_robin_balancer(self):
        """Test round robin load balancing"""
        balancer = RoundRobinLoadBalancer()
        
        # Test multiple selections follow round-robin pattern
        selections = []
        for _ in range(6):  # 2 complete rounds
            selected = balancer.select_instance(self.services)
            selections.append(selected.id)
        
        # Should cycle through services in order
        expected = ["service-1", "service-2", "service-3"] * 2
        assert selections == expected
    
    def test_weighted_balancer(self):
        """Test weighted load balancing"""
        balancer = WeightedLoadBalancer()
        
        # Test multiple selections
        selections = []
        for _ in range(100):
            selected = balancer.select_instance(self.services)
            selections.append(selected.id)
        
        # Service-2 should be selected more often due to higher weight
        service_2_count = selections.count("service-2")
        other_counts = selections.count("service-1") + selections.count("service-3")
        
        # Service-2 has weight 2, others have weight 1
        # So service-2 should be selected ~50% of the time
        assert service_2_count > other_counts / 2
    
    def test_random_balancer(self):
        """Test random load balancing"""
        balancer = RandomLoadBalancer()
        
        # Test multiple selections
        selections = set()
        for _ in range(50):
            selected = balancer.select_instance(self.services)
            selections.add(selected.id)
        
        # Should select from all services over time
        assert len(selections) > 1  # Should get variety
    
    def test_empty_services_list(self):
        """Test behavior with empty services list"""
        balancer = RoundRobinLoadBalancer()
        selected = balancer.select_instance([])
        assert selected is None
    
    def test_single_service(self):
        """Test behavior with single service"""
        balancer = RoundRobinLoadBalancer()
        single_service = [self.services[0]]
        
        for _ in range(5):
            selected = balancer.select_instance(single_service)
            assert selected.id == "service-1"
    
    def test_load_balancer_factory(self):
        """Test load balancer factory"""
        # Test round robin
        lb = LoadBalancerFactory.create_load_balancer(LoadBalancingStrategy.ROUND_ROBIN)
        assert isinstance(lb, RoundRobinLoadBalancer)
        
        # Test weighted
        lb = LoadBalancerFactory.create_load_balancer(LoadBalancingStrategy.WEIGHTED)
        assert isinstance(lb, WeightedLoadBalancer)
        
        # Test random
        lb = LoadBalancerFactory.create_load_balancer(LoadBalancingStrategy.RANDOM)
        assert isinstance(lb, RandomLoadBalancer)
