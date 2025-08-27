#!/usr/bin/env python3
"""
Test script for Mood Service -> Memory Service integration
V3-BK-015: Memory Service Integration
"""

import asyncio
import json
import urllib.request
import urllib.parse
from typing import Dict, Any

class MemoryServiceIntegration:
    """Integration client for Memory Service communication using urllib"""
    
    def __init__(self, memory_service_url: str = "http://localhost:8017"):
        self.memory_service_url = memory_service_url
    
    async def send_mood_interaction(self, user_id: str, mood_data: Dict[str, Any]) -> bool:
        """Send mood entry to Memory Service for pattern analysis"""
        try:
            # Prepare data in correct format for Memory Service integration endpoint
            integration_data = {
                "mood_score": mood_data.get("mood_score"),
                "energy_level": mood_data.get("energy_level"),
                "stress_level": mood_data.get("stress_level"),
                "sleep_quality": mood_data.get("sleep_quality"),
                "notes": mood_data.get("notes", ""),
                "context_tags": mood_data.get("context_tags", []),
                "timestamp": mood_data.get("timestamp"),
                "source": "mood_service"
            }
            
            # Prepare request to correct integration endpoint
            url = f"{self.memory_service_url}/api/v1/integrations/mood?user_id={user_id}"
            data = json.dumps(integration_data).encode('utf-8')
            headers = {'Content-Type': 'application/json'}
            
            # Create request
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            
            # Make request (run in thread to avoid blocking)
            import asyncio
            import concurrent.futures
            
            def make_request():
                try:
                    with urllib.request.urlopen(req, timeout=5) as response:
                        result = response.read().decode('utf-8')
                        print(f"✅ Memory Service Response: {result}")
                        return response.status == 200
                except Exception as e:
                    print(f"❌ Request error: {e}")
                    return False
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(executor, make_request)
                return result
                    
        except Exception as e:
            print(f"❌ Memory Service integration error: {e}")
            return False

async def test_mood_memory_integration():
    """Test the mood to memory service integration"""
    print("🧪 Testing Mood Service -> Memory Service Integration")
    print("=" * 50)
    
    # Create integration client
    memory_integration = MemoryServiceIntegration()
    
    # Test mood data
    test_mood_data = {
        "mood_score": 8,
        "energy_level": 7,
        "stress_level": 3,
        "sleep_quality": 8,
        "notes": "Feeling great today! Had a productive morning and good coffee.",
        "context_tags": ["work", "morning", "coffee", "productive"],
        "timestamp": "2025-01-15T10:30:00Z"
    }
    
    test_user_id = "test_user_v3_bk_015"
    
    print(f"📊 Test Mood Data:")
    print(json.dumps(test_mood_data, indent=2))
    print(f"\n👤 User ID: {test_user_id}")
    print(f"\n🧠 Sending to Memory Service...")
    
    # Test the integration
    success = await memory_integration.send_mood_interaction(
        user_id=test_user_id,
        mood_data=test_mood_data
    )
    
    if success:
        print(f"\n✅ Memory Service Integration: SUCCESS")
        print("🎉 V3-BK-015 Memory Service Integration is working!")
    else:
        print(f"\n❌ Memory Service Integration: FAILED")
        print("🔧 V3-BK-015 Memory Service Integration needs debugging")

if __name__ == "__main__":
    asyncio.run(test_mood_memory_integration())
