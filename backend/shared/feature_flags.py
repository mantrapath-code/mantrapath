"""Simple feature flag utilities.
Environment driven, minimal to avoid clutter.

Usage:
    from shared.feature_flags import feature_enabled
    if feature_enabled('USE_SERVER_UNIFIED_INSIGHTS'):
        ...
"""
from __future__ import annotations
import os
from functools import lru_cache
from typing import Optional, Dict

# Canonical flag names (documented)
KNOWN_FLAGS = {
    'USE_SERVER_UNIFIED_INSIGHTS': True,   # Enable unified backend aggregation endpoint (E2 Complete)
    'USE_EVENT_BUS_KAFKA': False,          # Future streaming integration 
    'USE_EVENT_BUS': True,                 # Enable EventBus for real-time features (E4)
    'USE_NATS_EVENT_BUS': True,            # Enable Enhanced (NATS-backed) Event Bus for V3 channels
    'ENABLE_TRANSLATION_MVP': False,       # Translation service stub
    'USE_ENHANCED_ML_INSIGHTS': True,      # Enable enhanced ML insights features
}

@lru_cache(maxsize=128)
def get_flag_bool(name: str, default: Optional[bool] = None) -> bool:
    if name in os.environ:
        val = os.environ[name].strip().lower()
        if val in ('1','true','yes','on','enable','enabled'): return True
        if val in ('0','false','no','off','disable','disabled'): return False
    if default is not None:
        return default
    return KNOWN_FLAGS.get(name, False)

def feature_enabled(name: str) -> bool:
    return get_flag_bool(name)

# Helper to expose all evaluated flags (for debugging)
def dump_flags() -> Dict[str, bool]:
    return {k: get_flag_bool(k) for k in KNOWN_FLAGS}
