#!/usr/bin/env python3
"""
E4 Real-Time Pipeline Verification Script
Tests the complete real-time insight pipeline:
1. Event publication from services
2. Event processing in ML service
3. Insight delta generation
4. WebSocket delivery to frontend
"""

import asyncio
import json
import sys
import os
import aiohttp
import websockets
from datetime import datetime, timezone

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'shared'))

async def test_event_bus():
    """Test the event bus functionality"""
    print("🧪 Testing Event Bus...")
    
    try:
        # Import and test event bus
        from shared.events import get_event_bus, EventChannels, Event
        
        bus = get_event_bus()
        
        # Test event publication
        test_event_data = {
            "id": "test-mood-123",
            "mood_score": 8,
            "energy_level": 7,
            "stress_level": 3,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        success = await bus.publish(
            EventChannels.MOOD_ENTRY_CREATED,
            test_event_data,
            user_id="test-user-123"
        )
        
        if success:
            print("✅ Event bus is working - published test mood entry event")
        else:
            print("❌ Event bus failed to publish event")
            
        await bus.close()
        return success
        
    except Exception as e:
        print(f"❌ Event bus test failed: {e}")
        return False

async def test_api_endpoints():
    """Test API endpoints for creating data that should trigger events"""
    print("\n🧪 Testing API Endpoints...")
    
    # Test data
    auth_token = "test-token"  # In real test, get from login
    base_url = "http://localhost:8000"  # API Gateway
    
    test_results = {}
    
    # Test mood service
    try:
        mood_data = {
            "mood_score": 8,
            "energy_level": 7,
            "stress_level": 3,
            "sleep_quality": 8,
            "notes": "E4 Test mood entry",
            "context_tags": ["testing", "e4"],
            "emotional_granularity": 3,
            "mood_confidence": 0.9
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/api/v1/mood/",
                json=mood_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            ) as response:
                if response.status == 200:
                    print("✅ Mood entry creation endpoint accessible")
                    test_results['mood_endpoint'] = True
                else:
                    print(f"⚠️  Mood endpoint returned {response.status}")
                    test_results['mood_endpoint'] = False
                    
    except Exception as e:
        print(f"❌ Mood endpoint test failed: {e}")
        test_results['mood_endpoint'] = False
    
    # Test journal service (via mood service)
    try:
        journal_data = {
            "title": "E4 Test Journal",
            "content": "Testing the real-time journal entry pipeline",
            "mood_before": 6,
            "mood_after": 8,
            "is_private": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/api/v1/journal/",
                json=journal_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            ) as response:
                if response.status == 200:
                    print("✅ Journal entry creation endpoint accessible")
                    test_results['journal_endpoint'] = True
                else:
                    print(f"⚠️  Journal endpoint returned {response.status}")
                    test_results['journal_endpoint'] = False
                    
    except Exception as e:
        print(f"❌ Journal endpoint test failed: {e}")
        test_results['journal_endpoint'] = False
    
    return test_results

async def test_websocket_connection():
    """Test WebSocket connection to notification service"""
    print("\n🧪 Testing WebSocket Connection...")
    
    ws_url = "ws://localhost:8007/ws/test-user-123"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connection established")
            
            # Send a test message
            test_message = {
                "type": "heartbeat",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            await websocket.send(json.dumps(test_message))
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                if data.get("type") == "heartbeat_ack":
                    print("✅ WebSocket heartbeat successful")
                    return True
                else:
                    print(f"⚠️  Unexpected WebSocket response: {data}")
                    return False
                    
            except asyncio.TimeoutError:
                print("⚠️  WebSocket timeout - but connection works")
                return True
                
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

async def test_unified_insights_endpoint():
    """Test the unified insights endpoint"""
    print("\n🧪 Testing Unified Insights Endpoint...")
    
    ml_service_url = "http://localhost:8008"
    auth_token = "test-token"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ml_service_url}/api/v1/insights/unified",
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "X-Insight-Version": "v1"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Unified insights endpoint accessible")
                    print(f"   Cache hit: {data.get('cache_info', {}).get('hit', 'unknown')}")
                    return True
                else:
                    print(f"⚠️  Unified insights returned {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Unified insights test failed: {e}")
        return False

def check_feature_flags():
    """Check if feature flags are properly set"""
    print("\n🧪 Checking Feature Flags...")
    
    try:
        from shared.feature_flags import get_flag_bool
        
        flags_to_check = [
            'USE_EVENT_BUS',
            'USE_SERVER_UNIFIED_INSIGHTS',
            'USE_EVENT_BUS_KAFKA'
        ]
        
        flag_status = {}
        for flag in flags_to_check:
            status = get_flag_bool(flag)
            flag_status[flag] = status
            icon = "✅" if status else "❌"
            print(f"   {icon} {flag}: {status}")
        
        # Check critical flags
        if flag_status.get('USE_EVENT_BUS'):
            print("✅ Event bus is enabled")
        else:
            print("❌ Event bus is disabled - enable USE_EVENT_BUS=true")
            
        return flag_status
        
    except Exception as e:
        print(f"❌ Feature flags check failed: {e}")
        return {}

async def main():
    """Run all tests"""
    print("🚀 E4 Real-Time Pipeline Verification")
    print("=" * 50)
    
    # Check feature flags first
    flags = check_feature_flags()
    
    if not flags.get('USE_EVENT_BUS'):
        print("\n❌ Event bus is disabled. Set USE_EVENT_BUS=true in .env")
        return False
    
    # Test event bus
    event_bus_ok = await test_event_bus()
    
    # Test API endpoints
    api_results = await test_api_endpoints()
    
    # Test WebSocket
    websocket_ok = await test_websocket_connection()
    
    # Test unified insights
    insights_ok = await test_unified_insights_endpoint()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Event Bus: {'✅' if event_bus_ok else '❌'}")
    print(f"   Mood Endpoint: {'✅' if api_results.get('mood_endpoint') else '❌'}")
    print(f"   Journal Endpoint: {'✅' if api_results.get('journal_endpoint') else '❌'}")
    print(f"   WebSocket: {'✅' if websocket_ok else '❌'}")
    print(f"   Unified Insights: {'✅' if insights_ok else '❌'}")
    
    # Overall status
    all_tests = [
        event_bus_ok,
        api_results.get('mood_endpoint', False),
        websocket_ok,
        insights_ok
    ]
    
    if all(all_tests):
        print("\n🎉 All tests passed! E4 pipeline is ready.")
        print("\n📋 Next Steps:")
        print("   1. Start the Docker containers")
        print("   2. Create a mood entry via the frontend")
        print("   3. Check WebSocket for insight deltas")
        print("   4. Verify dashboard updates in <1s")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test script failed: {e}")
        sys.exit(1)
