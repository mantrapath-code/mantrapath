import asyncio
import pytest
import sys
import os
from datetime import datetime

from typing import List, Dict, Any

# Add the backend path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# V3 Enhanced bus
from shared.events import get_enhanced_event_bus, cleanup_enhanced_event_bus
from shared.events.enhanced_bus import V3EventChannels


@pytest.mark.asyncio
async def test_v3_mood_event_publish_subscribe():
    """Test that mood.entry.created events can be published and received"""
    bus = get_enhanced_event_bus()
    await bus.initialize()

    received: List[Dict[str, Any]] = []
    event = asyncio.Event()

    async def handler(e):
        received.append({
            "user_id": e.user_id,
            "data": e.data,
            "channel": e.channel,
        })
        event.set()

    await bus.subscribe(V3EventChannels.MOOD_ENTRY_CREATED, handler)

    payload = {
        "id": "test-mood-id",
        "user_id": "user-123",
        "mood_score": 7,
        "energy_level": 5,
        "stress_level": 3,
        "context_tags": ["work"],
        "created_at": "2025-08-16T12:00:00Z",
    }

    await bus.publish(V3EventChannels.MOOD_ENTRY_CREATED, payload, user_id="user-123")

    # Wait for message delivery
    await asyncio.wait_for(event.wait(), timeout=1.5)

    assert received, "No event received on V3 mood channel"
    msg = received[0]
    assert msg["channel"] == V3EventChannels.MOOD_ENTRY_CREATED
    assert msg["user_id"] == "user-123"
    assert msg["data"]["mood_score"] == 7


@pytest.mark.asyncio
async def test_v3_journal_event_publish_subscribe():
    """Test that journal.entry.created events can be published and received"""
    bus = get_enhanced_event_bus()
    await bus.initialize()

    received: List[Dict[str, Any]] = []
    event = asyncio.Event()

    async def handler(e):
        received.append(e.data)
        event.set()

    await bus.subscribe(V3EventChannels.JOURNAL_ENTRY_CREATED, handler)

    payload = {
        "id": "test-journal-id",
        "user_id": "user-abc",
        "title": "My Day",
        "content": "I felt grateful and happy today.",
        "sentiment_score": 0.6,
        "sentiment_label": "positive",
        "themes": ["happiness"],
        "created_at": "2025-08-16T13:00:00Z",
    }

    await bus.publish(V3EventChannels.JOURNAL_ENTRY_CREATED, payload, user_id="user-abc")

    await asyncio.wait_for(event.wait(), timeout=1.5)

    assert received and received[0]["sentiment_label"] == "positive"


@pytest.mark.asyncio
async def test_voice_intent_event_channel():
    """Test voice.intent_classified channel exists and works"""
    bus = get_enhanced_event_bus()
    await bus.initialize()

    received: List[Dict[str, Any]] = []
    event = asyncio.Event()

    async def handler(e):
        received.append(e.data)
        event.set()

    await bus.subscribe(V3EventChannels.VOICE_INTENT_CLASSIFIED, handler)

    payload = {
        "intent": "mood_check",
        "confidence_score": 0.85,
        "user_id": "user-voice-test",
    }

    await bus.publish(V3EventChannels.VOICE_INTENT_CLASSIFIED, payload, user_id="user-voice-test")

    await asyncio.wait_for(event.wait(), timeout=1.5)

    assert received and received[0]["intent"] == "mood_check"


@pytest.mark.asyncio 
async def test_dual_publish_simulation():
    """Test that dual publishing (legacy + V3) pattern works"""
    bus = get_enhanced_event_bus()
    await bus.initialize()

    v3_received = []
    legacy_received = []
    
    v3_event = asyncio.Event()
    legacy_event = asyncio.Event()

    async def v3_handler(e):
        v3_received.append(e.data)
        v3_event.set()

    async def legacy_handler(e):
        legacy_received.append(e.data)
        legacy_event.set()

    # Subscribe to both V3 and legacy-style channels
    await bus.subscribe(V3EventChannels.MOOD_ENTRY_CREATED, v3_handler)
    await bus.subscribe("mood_entry_created", legacy_handler)  # legacy pattern

    # Simulate dual publish
    mood_data = {
        "id": "dual-test",
        "user_id": "dual-user",
        "mood_score": 8,
        "created_at": datetime.now().isoformat()
    }

    # Publish to both channels (simulating dual-publish)
    await bus.publish(V3EventChannels.MOOD_ENTRY_CREATED, mood_data, user_id="dual-user")
    await bus.publish("mood_entry_created", mood_data, user_id="dual-user")

    # Wait for both
    await asyncio.wait_for(v3_event.wait(), timeout=1.0)
    await asyncio.wait_for(legacy_event.wait(), timeout=1.0)

    assert v3_received and v3_received[0]["mood_score"] == 8
    assert legacy_received and legacy_received[0]["mood_score"] == 8


@pytest.mark.asyncio
async def test_cleanup_enhanced_bus():
    """Ensure cleanup doesn't raise and resets global bus"""
    # Ensure cleanup doesn't raise and resets global bus
    await cleanup_enhanced_event_bus()
    # Getting it again should succeed
    bus = get_enhanced_event_bus()
    assert bus is not None
