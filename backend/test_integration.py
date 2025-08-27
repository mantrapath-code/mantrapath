#!/usr/bin/env python3
"""
Models Service Integration Test
Tests the integration between Proactive Assistance Engine and Models Service
"""
import asyncio
import httpx
import json


async def test_models_integration():
    """Test the Models Service integration through Proactive Assistance Engine"""
    print("Testing Models Service Integration...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get('http://localhost:8018/api/v1/models/status')
            print(f"Models Integration Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Models Service Healthy: {data.get('models_service_healthy', False)}")
                print(f"Integration Enabled: {data.get('integration_enabled', False)}")
                print(f"Capabilities: {data.get('capabilities', [])}")
                return data.get('models_service_healthy', False)
        except Exception as e:
            print(f"Models Integration Error: {e}")
            return False
    return False


async def test_models_service_direct():
    """Test direct connection to Models Service"""
    print("Testing direct Models Service connection...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get('http://localhost:8085/health')
            print(f"Models Service Health: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Service: {data.get('service', 'unknown')}")
                print(f"Version: {data.get('version', 'unknown')}")
                return True
        except Exception as e:
            print(f"Models Service Error: {e}")
            return False
    return False


async def test_proactive_assistance_health():
    """Test Proactive Assistance Engine health"""
    print("Testing Proactive Assistance Engine health...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get('http://localhost:8018/health')
            print(f"Proactive Assistance Health: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Service Status: {data.get('status', 'unknown')}")
                print(f"Components: {data.get('components', {})}")
                return True
        except Exception as e:
            print(f"Proactive Assistance Error: {e}")
            return False
    return False


async def test_voice_assistance_endpoint():
    """Test voice assistance endpoint with Models Service integration"""
    print("Testing voice assistance endpoint...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test a simple voice assistance request
            test_data = {
                "audio_data": "test_audio_data",
                "language": "en",
                "context": {"session_id": "test_session"}
            }
            response = await client.post(
                'http://localhost:8018/api/v1/assistance/voice/test_user_123',
                json=test_data
            )
            print(f"Voice Assistance Status: {response.status_code}")
            if response.status_code in [200, 422]:  # 422 is expected for invalid test data
                return True
        except Exception as e:
            print(f"Voice Assistance Error: {e}")
            return False
    return False


async def run_comprehensive_tests():
    """Run all integration tests"""
    print("Starting Comprehensive Models Service Integration Test")
    print("=" * 60)
    
    # Test 1: Direct Models Service
    models_direct = await test_models_service_direct()
    print()
    
    # Test 2: Proactive Assistance Health
    proactive_health = await test_proactive_assistance_health()
    print()
    
    # Test 3: Models Integration Status
    integration_works = await test_models_integration()
    print()
    
    # Test 4: Voice Assistance Endpoint
    voice_endpoint = await test_voice_assistance_endpoint()
    print()
    
    print("=" * 60)
    print("Test Summary:")
    print(f"Models Service Direct: {'PASS' if models_direct else 'FAIL'}")
    print(f"Proactive Assistance Health: {'PASS' if proactive_health else 'FAIL'}")
    print(f"Models Integration: {'PASS' if integration_works else 'FAIL'}")
    print(f"Voice Assistance Endpoint: {'PASS' if voice_endpoint else 'FAIL'}")
    
    overall_success = models_direct and proactive_health and integration_works
    print(f"Overall Integration Status: {'SUCCESS' if overall_success else 'NEEDS WORK'}")
    
    if not integration_works and models_direct and proactive_health:
        print("\nDiagnosis: Services are running but integration configuration needs fixing")
    elif not models_direct:
        print("\nDiagnosis: Models Service is not accessible")
    elif not proactive_health:
        print("\nDiagnosis: Proactive Assistance Engine is not healthy")
    
    return overall_success


if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_tests())