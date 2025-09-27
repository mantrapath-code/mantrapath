"""Centralized service URL resolution.

Provides helper functions to obtain internal (Docker network) service URLs
with optional environment overrides. This removes scattered hard-coded
"localhost:PORT" patterns across the codebase.

Usage:
    from shared.utils.service_urls import service_url
    profile_api = service_url("profile")

Environment Override Pattern (highest precedence):
    SERVICE_<UPPER_SERVICE_KEY>_URL
Example:
    export SERVICE_PROFILE_URL="http://custom-profile:9000"

Service Keys => Default Internal DNS URLs:
    api_gateway -> http://api-gateway:8000
    auth        -> http://auth-service:8001
    profile     -> http://profile-service:8002
    mood        -> http://mood-service:8003
    chatbot     -> http://chatbot-service:8004
    translation -> http://translation-service:8010  (NOTE: service port mapping)
    content     -> http://content-service:8005
    community   -> http://community-service:8006
    notification-> http://notification-service:8007
    ml          -> http://ml-service:8008
    media       -> http://media-service:8021
    voice       -> http://voice-service:8011
    action      -> http://action-orchestrator:8012
    ai_context  -> http://ai-context-store:8013
    ai_events   -> http://ai-event-processor:8014
    voice_events-> http://voice-event-processor:8015
    memory      -> http://memory-service:8017
    assistance  -> http://proactive-assistance-engine:8018
    models      -> http://models-service:8080         (internal-only models)

NOTE: Ports reflect current docker-compose; update here if compose changes.
"""
from __future__ import annotations
import os
from functools import lru_cache
from typing import Dict

_DEFAULTS: Dict[str, str] = {
    "api_gateway": "http://api-gateway:8000",
    "auth": "http://auth-service:8001",
    "profile": "http://profile-service:8002",
    "mood": "http://mood-service:8003",
    "chatbot": "http://chatbot-service:8004",
    "translation": "http://translation-service:8010",
    "content": "http://content-service:8005",
    "community": "http://community-service:8006",
    "notification": "http://notification-service:8007",
    "ml": "http://ml-service:8008",
    "media": "http://media-service:8021",
    "voice": "http://voice-service:8011",
    "action": "http://action-orchestrator:8012",
    "ai_context": "http://ai-context-store:8013",
    "ai_events": "http://ai-event-processor:8014",
    "voice_events": "http://voice-event-processor:8015",
    "memory": "http://memory-service:8017",
    "assistance": "http://proactive-assistance-engine:8018",
    "models": "http://models-service:8080",
}


def _env_key(key: str) -> str:
    return f"SERVICE_{key.upper()}_URL"


@lru_cache(maxsize=64)
def service_url(key: str) -> str:
    """Return resolved service URL for given logical key.

    Resolution order:
    1. SERVICE_<KEY>_URL env variable
    2. Internal defaults mapping
    3. Raises KeyError if unknown
    """
    if key not in _DEFAULTS:
        raise KeyError(f"Unknown service key '{key}'. Known: {sorted(_DEFAULTS)}")
    override = os.getenv(_env_key(key))
    return override.rstrip("/") if override else _DEFAULTS[key]


def all_service_urls() -> Dict[str, str]:
    """Return all resolved service URLs (with overrides applied)."""
    return {k: service_url(k) for k in _DEFAULTS}


if __name__ == "__main__":  # simple manual debug
    import json
    print(json.dumps(all_service_urls(), indent=2))
