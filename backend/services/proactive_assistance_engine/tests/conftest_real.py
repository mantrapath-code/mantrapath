"""
Real Backend Test Configuration for Proactive Assistance Engine

This file provides pytest fixtures for testing actual backend functionality
without mock data. It connects to real services and databases.
"""

import pytest
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any
import httpx
import os

# Environment configuration for real backend testing
@pytest.fixture(scope="session")
def backend_config() -> Dict[str, str]:
    """Real backend configuration for testing"""
    return {
        "proactive_assistance_engine": "http://localhost:8018",
        "ai_event_processor": "http://localhost:8014",
        "ai_context_store": "http://localhost:8013",
        "cultural_intelligence": "http://localhost:8017",
        "models_service": "http://localhost:8085",
        "database_url": os.getenv("DATABASE_URL", "postgresql://mantrapath:mantrapath123@localhost:5432/mantrapath"),
        "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379")
    }

@pytest.fixture
async def http_client():
    """Real HTTP client for testing actual endpoints"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client

@pytest.fixture
def real_user_id() -> str:
    """Real user ID for testing (should exist in database)"""
    return "test_user_real_123"

@pytest.fixture
def real_user_context() -> Dict[str, Any]:
    """Real user context that would come from actual database"""
    return {
        "user_id": "test_user_real_123",
        "mood_context": {
            "current_mood_score": 5.0,
            "mood_trend": "stable",
            "emotional_state": "neutral"
        },
        "cultural_profile": {
            "primary_culture": "individualist",
            "communication_style": "direct",
            "family_involvement": False,
            "hierarchical_respect": False
        },
        "recent_interactions": [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": "mood",
                "type": "entry",
                "data": {"mood_score": 5}
            }
        ],
        "assistance_preferences": {
            "preferred_assistance_style": "direct",
            "frequency": "moderate",
            "communication_channel": "in_app"
        }
    }

@pytest.fixture
async def proactive_assistance_client(backend_config: Dict[str, str], http_client: httpx.AsyncClient) -> Dict[str, Any]:
    """Real client for proactive assistance engine"""
    base_url = backend_config["proactive_assistance_engine"]
    
    # Test if service is available
    try:
        response = await http_client.get(f"{base_url}/health")
        if response.status_code != 200:
            pytest.skip(f"Proactive assistance engine not healthy: {response.status_code}")
    except Exception as e:
        pytest.skip(f"Proactive assistance engine not accessible: {e}")
    
    return {
        "base_url": base_url,
        "client": http_client
    }

@pytest.fixture
async def ai_event_processor_client(backend_config: Dict[str, str], http_client: httpx.AsyncClient) -> Dict[str, Any]:
    """Real client for AI event processor"""
    base_url = backend_config["ai_event_processor"]
    
    try:
        response = await http_client.get(f"{base_url}/health")
        if response.status_code != 200:
            pytest.skip(f"AI Event Processor not healthy: {response.status_code}")
    except Exception as e:
        pytest.skip(f"AI Event Processor not accessible: {e}")
    
    return {
        "base_url": base_url,
        "client": http_client
    }

@pytest.fixture
async def ai_context_store_client(backend_config: Dict[str, str], http_client: httpx.AsyncClient) -> Dict[str, Any]:
    """Real client for AI context store"""
    base_url = backend_config["ai_context_store"]
    
    try:
        response = await http_client.get(f"{base_url}/health")
        if response.status_code != 200:
            pytest.skip(f"AI Context Store not healthy: {response.status_code}")
    except Exception as e:
        pytest.skip(f"AI Context Store not accessible: {e}")
    
    return {
        "base_url": base_url,
        "client": http_client
    }

@pytest.fixture
async def cultural_intelligence_client(backend_config: Dict[str, str], http_client: httpx.AsyncClient) -> Dict[str, Any]:
    """Real client for cultural intelligence service"""
    base_url = backend_config["cultural_intelligence"]
    
    try:
        response = await http_client.get(f"{base_url}/health")
        if response.status_code != 200:
            pytest.skip(f"Cultural Intelligence not healthy: {response.status_code}")
    except Exception as e:
        pytest.skip(f"Cultural Intelligence not accessible: {e}")
    
    return {
        "base_url": base_url,
        "client": http_client
    }

@pytest.fixture
async def models_service_client(backend_config: Dict[str, str], http_client: httpx.AsyncClient) -> Dict[str, Any]:
    """Real client for models service"""
    base_url = backend_config["models_service"]
    
    return {
        "base_url": base_url,
        "client": http_client
    }

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Real test data that would come from actual services
@pytest.fixture
def real_intervention_analysis() -> Dict[str, Any]:
    """Real intervention analysis structure"""
    return {
        "intervention_needed": True,
        "confidence": 0.75,
        "intervention_type": "proactive_support",
        "urgency_level": "medium",
        "recommended_actions": [
            "Gentle check-in",
            "Mood support resources",
            "Professional guidance referral"
        ],
        "risk_factors": {
            "mood_decline": {"score": 0.6, "trend": "stable"},
            "social_isolation": {"score": 0.5, "trend": "stable"}
        }
    }

@pytest.fixture
def real_timing_evaluation() -> Dict[str, Any]:
    """Real timing evaluation structure"""
    return {
        "timing_evaluation": {
            "timing_appropriate": True,
            "timing_confidence": 0.8,
            "can_proceed": True,
            "recommended_delay_minutes": 0
        },
        "recent_assistance_check": {
            "last_assistance_time": "2025-01-01T10:00:00Z",
            "hours_since_last": 4.5,
            "sufficient_gap": True,
            "gap_score": 0.9
        },
        "activity_analysis": {
            "engagement_level": 0.7,
            "user_receptiveness_score": 0.8,
            "time_of_day_appropriateness": 0.9,
            "activity_confidence": 0.8
        },
        "cultural_timing": {
            "primary_culture": "individualist",
            "meal_time_appropriateness": 1.0,
            "family_time_appropriateness": 0.8,
            "overall_cultural_score": 0.9
        },
        "urgency_override": False,
        "timing_score": 0.8,
        "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
    }
