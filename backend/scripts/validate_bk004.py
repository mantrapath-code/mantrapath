#!/usr/bin/env python3
"""
BK-004 Integration Validation Script
Tests the complete event flow across services
"""

import asyncio
import sys
import os

# Add backend to path
backend_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, backend_path)

from shared.events.enhanced_bus import get_enhanced_event_bus, cleanup_enhanced_event_bus
from shared.events import V3EventChannels
from datetime import datetime, timezone

async def test_bk004_integration():
    """Test complete BK-004 implementation"""
    print("🚀 BK-004 Service Event Integration Validation")
    print("=" * 50)
    
    bus = get_enhanced_event_bus()
    await bus.initialize()
    
    # Track received events
    received_events = []
    
    async def event_handler(event):
        received_events.append({
            "channel": event.channel,
            "user_id": event.user_id,
            "timestamp": event.timestamp,
            "data_keys": list(event.data.keys())
        })
        print(f"📨 Received event: {event.channel} for user {event.user_id}")
    
    # Subscribe to all V3 channels
    channels = [
        V3EventChannels.MOOD_ENTRY_CREATED,
        V3EventChannels.JOURNAL_ENTRY_CREATED,
        V3EventChannels.VOICE_INTENT_CLASSIFIED
    ]
    
    for channel in channels:
        await bus.subscribe(channel, event_handler)
        print(f"📡 Subscribed to {channel}")
    
    print("\n🔄 Testing Event Publishing...")
    
    # Test 1: Mood Entry Event
    mood_payload = {
        "id": "test-mood-123",
        "user_id": "user-test",
        "mood_score": 8,
        "energy_level": 7,
        "stress_level": 3,
        "context_tags": ["work", "productivity"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sentiment": "positive"
    }
    
    await bus.publish(V3EventChannels.MOOD_ENTRY_CREATED, mood_payload, user_id="user-test")
    print("✅ Published mood entry event")
    
    # Test 2: Journal Entry Event
    journal_payload = {
        "id": "test-journal-456",
        "user_id": "user-test",
        "title": "Integration Test Journal",
        "content": "Testing the BK-004 event integration system.",
        "sentiment_score": 0.75,
        "sentiment_label": "positive",
        "themes": ["testing", "integration"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await bus.publish(V3EventChannels.JOURNAL_ENTRY_CREATED, journal_payload, user_id="user-test")
    print("✅ Published journal entry event")
    
    # Test 3: Voice Intent Event
    voice_payload = {
        "intent": "mood_inquiry",
        "confidence_score": 0.92,
        "user_id": "user-test",
        "transcript": "How am I feeling today?",
        "processing_time_ms": 150
    }
    
    await bus.publish(V3EventChannels.VOICE_INTENT_CLASSIFIED, voice_payload, user_id="user-test")
    print("✅ Published voice intent event")
    
    # Give events time to process
    await asyncio.sleep(0.1)
    
    print(f"\n📊 Results:")
    print(f"Events Published: 3")
    print(f"Events Received: {len(received_events)}")
    
    if len(received_events) == 3:
        print("✅ All events successfully processed!")
        for event in received_events:
            print(f"  📨 {event['channel']} - User: {event['user_id']}")
    else:
        print("❌ Event processing incomplete")
        return False
    
    # Test event bus health
    health = await bus.health_check()
    print(f"\n🏥 Event Bus Health: {health['status']}")
    print(f"📈 Performance Metrics:")
    if 'metrics' in health:
        print(f"  Total Events: {health['metrics'].get('total_events', 'N/A')}")
        print(f"  Error Count: {health['metrics'].get('error_count', 'N/A')}")
    else:
        print(f"  Event Metrics: {bus.event_metrics}")
    
    print(f"  NATS Connected: {bus.nats_connected}")
    print(f"  In-Memory Fallback: {'Active' if not bus.nats_connected else 'Standby'}")
    
    # Cleanup
    await cleanup_enhanced_event_bus()
    print("\n🧹 Cleanup completed")
    
    return True

async def main():
    """Main test runner"""
    try:
        success = await test_bk004_integration()
        if success:
            print("\n🎉 BK-004 Integration Test: PASSED")
            print("✨ Service Event Integration is working correctly!")
            return 0
        else:
            print("\n❌ BK-004 Integration Test: FAILED")
            return 1
    except Exception as e:
        print(f"\n💥 Integration test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
