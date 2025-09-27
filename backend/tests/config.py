"""Test configuration for service base URLs.

Provides environment-overridable URLs so tests do not hardcode localhost.

Override pattern:
    TEST_<SERVICE_KEY_UPPER>_URL
Fallback order:
    1. TEST_<KEY>_URL
    2. SERVICE_<KEY>_URL (shared with runtime overrides)
    3. Internal DNS (docker network) via shared.utils.service_urls
    4. Host localhost:<default_port> (only if HOST_FALLBACK=true)

Set HOST_FALLBACK=false (default) in containerized CI to avoid localhost.
"""
from __future__ import annotations
import os
from typing import Dict
from shared.utils.service_urls import service_url

# Map logical keys to a host-exposed default port for fallback when running directly on host.
_HOST_PORTS: Dict[str, int] = {
    "api_gateway": 8000,
    "auth": 8001,
    "profile": 8002,
    "mood": 8003,
    "chatbot": 8004,
    "translation": 8010,
    "community": 8006,
    "notification": 8007,
    "ml": 8008,
    "media": 8009,
    "content": 8010,  # content service shares port? adjust if different
    "voice": 8011,
    "action": 8012,
    "ai_context": 8013,
    "ai_events": 8014,
    "voice_events": 8015,
    "memory": 8017,
    "assistance": 8018,
}

HOST_FALLBACK = os.getenv("HOST_FALLBACK", "false").lower() == "true"  # Disabled by default to avoid localhost usage


def test_service_url(key: str) -> str:
    env_key = f"TEST_{key.upper()}_URL"
    if env_key in os.environ:
        return os.environ[env_key].rstrip('/')
    service_env = os.getenv(f"SERVICE_{key.upper()}_URL")
    if service_env:
        return service_env.rstrip('/')
    try:
        return service_url(key)
    except KeyError:
        pass
    # Host fallback intentionally disabled to enforce internal DNS usage.
    # Provide explicit TEST_<KEY>_URL or SERVICE_<KEY>_URL if needed when running outside containers.
    if HOST_FALLBACK and key in _HOST_PORTS:
        raise RuntimeError(
            "HOST_FALLBACK requested but disabled to prevent localhost hardcoding; set TEST_ or SERVICE_ env vars instead."
        )
    raise KeyError(f"Unknown test service key '{key}' and no fallback available")

# Convenience named constants for existing tests
API_BASE = test_service_url("api_gateway")
CHATBOT_DIRECT = test_service_url("chatbot")
PHI3_AGENT = test_service_url("translation")  # adjust if phi3 agent separate later
PROFILE_BASE = test_service_url("profile")
AUTH_BASE = test_service_url("auth")

__all__ = [
    "API_BASE",
    "CHATBOT_DIRECT",
    "PHI3_AGENT",
    "PROFILE_BASE",
    "AUTH_BASE",
    "test_service_url",
]
