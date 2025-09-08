"""
Access control configuration for frontend engineers
"""

from typing import Dict, Any

# Frontend Engineer Permission Levels
FRONTEND_ENGINEER_PERMISSIONS = {
    "basic": {
        "api_docs": "read",
        "service_health": "read",
        "model_status": "read",
        "api_testing": "limited",
        "rate_limit": 100,  # requests per minute
        "features": [
            "view_api_documentation",
            "view_service_health",
            "view_model_training_status",
            "limited_api_testing"
        ]
    },
    "enhanced": {
        "api_docs": "read",
        "service_health": "read",
        "model_status": "read",
        "api_testing": "full",
        "rate_limit": 500,  # requests per minute
        "features": [
            "view_api_documentation",
            "view_service_health",
            "view_model_training_status",
            "full_api_testing",
            "view_usage_metrics"
        ]
    },
    "premium": {
        "api_docs": "read",
        "service_health": "read",
        "model_status": "read",
        "api_testing": "full",
        "advanced_features": "read",
        "rate_limit": 1000,  # requests per minute
        "features": [
            "view_api_documentation",
            "view_service_health",
            "view_model_training_status",
            "full_api_testing",
            "view_usage_metrics",
            "advanced_analytics",
            "custom_dashboards",
            "priority_support"
        ]
    }
}

# Service-specific permissions
SERVICE_PERMISSIONS = {
    "voice_service": {
        "endpoints": [
            "POST /api/voice/stt",
            "POST /api/voice/tts",
            "GET /api/voice/models",
            "GET /api/voice/languages"
        ],
        "required_permission": "basic"
    },
    "community_service": {
        "endpoints": [
            "GET /api/community/challenges",
            "GET /api/community/events",
            "GET /api/community/leaderboard",
            "POST /api/community/join"
        ],
        "required_permission": "basic"
    },
    "ml_service": {
        "endpoints": [
            "GET /api/ml/models",
            "GET /api/ml/performance",
            "POST /api/ml/predict"
        ],
        "required_permission": "enhanced"
    },
    "models_service": {
        "endpoints": [
            "GET /api/models/status",
            "GET /api/models/training",
            "GET /api/models/deployment"
        ],
        "required_permission": "enhanced"
    },
    "auth_service": {
        "endpoints": [
            "POST /api/auth/login",
            "POST /api/auth/register",
            "POST /api/auth/refresh",
            "GET /api/auth/profile"
        ],
        "required_permission": "basic"
    }
}

# Rate limiting configuration per endpoint
ENDPOINT_RATE_LIMITS = {
    "/api/docs": {
        "basic": 50,
        "enhanced": 200,
        "premium": 500
    },
    "/api/models/status": {
        "basic": 30,
        "enhanced": 100,
        "premium": 300
    },
    "/api/health/services": {
        "basic": 60,
        "enhanced": 200,
        "premium": 600
    },
    "/api/testing/test-endpoint": {
        "basic": 10,
        "enhanced": 50,
        "premium": 150
    },
    "/api/usage/metrics": {
        "basic": 20,
        "enhanced": 100,
        "premium": 300
    }
}

# Feature flags for different permission levels
FEATURE_FLAGS = {
    "basic": {
        "real_time_updates": False,
        "advanced_analytics": False,
        "custom_dashboards": False,
        "priority_support": False,
        "beta_features": False
    },
    "enhanced": {
        "real_time_updates": True,
        "advanced_analytics": False,
        "custom_dashboards": False,
        "priority_support": False,
        "beta_features": False
    },
    "premium": {
        "real_time_updates": True,
        "advanced_analytics": True,
        "custom_dashboards": True,
        "priority_support": True,
        "beta_features": True
    }
}

# API testing limitations
API_TESTING_LIMITATIONS = {
    "basic": {
        "max_requests_per_test": 5,
        "max_concurrent_tests": 1,
        "test_timeout": 30,
        "allowed_endpoints": ["GET", "POST"],
        "blocked_endpoints": ["DELETE", "PUT", "PATCH"]
    },
    "enhanced": {
        "max_requests_per_test": 20,
        "max_concurrent_tests": 3,
        "test_timeout": 60,
        "allowed_endpoints": ["GET", "POST", "PUT"],
        "blocked_endpoints": ["DELETE", "PATCH"]
    },
    "premium": {
        "max_requests_per_test": 50,
        "max_concurrent_tests": 5,
        "test_timeout": 120,
        "allowed_endpoints": ["GET", "POST", "PUT", "PATCH"],
        "blocked_endpoints": ["DELETE"]
    }
}

# Data access restrictions
DATA_ACCESS_RESTRICTIONS = {
    "basic": {
        "sensitive_data": False,
        "user_data": False,
        "system_metrics": False,
        "performance_data": False,
        "error_logs": False
    },
    "enhanced": {
        "sensitive_data": False,
        "user_data": False,
        "system_metrics": True,
        "performance_data": True,
        "error_logs": False
    },
    "premium": {
        "sensitive_data": False,
        "user_data": False,
        "system_metrics": True,
        "performance_data": True,
        "error_logs": True
    }
}

def get_permission_level(engineer_id: str) -> str:
    """
    Get permission level for a frontend engineer
    This would typically query a database or external service
    """
    # For now, return basic access
    # In production, this would check against a user database
    return "basic"


def check_permission(engineer_id: str, required_permission: str) -> bool:
    """
    Check if an engineer has the required permission level
    """
    current_level = get_permission_level(engineer_id)
    
    permission_hierarchy = {
        "basic": 1,
        "enhanced": 2,
        "premium": 3
    }
    
    return permission_hierarchy.get(current_level, 0) >= permission_hierarchy.get(required_permission, 0)


def get_engineer_permissions(engineer_id: str) -> Dict[str, Any]:
    """
    Get complete permissions for a frontend engineer
    """
    level = get_permission_level(engineer_id)
    return FRONTEND_ENGINEER_PERMISSIONS.get(level, FRONTEND_ENGINEER_PERMISSIONS["basic"])


def get_rate_limit(engineer_id: str, endpoint: str) -> int:
    """
    Get rate limit for an engineer on a specific endpoint
    """
    level = get_permission_level(engineer_id)
    endpoint_limits = ENDPOINT_RATE_LIMITS.get(endpoint, {})
    return endpoint_limits.get(level, endpoint_limits.get("basic", 100))

