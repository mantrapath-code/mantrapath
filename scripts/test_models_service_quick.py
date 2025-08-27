#!/usr/bin/env python3
"""
MantraPath Models Service - Quick Testing and Monitoring Script
============================================================

Simple script for quick health checks and basic functionality testing
of the Models Service. Use this for rapid development feedback.

Usage:
    python test_models_service_quick.py              # Basic health check
    python test_models_service_quick.py --full       # Full quick test
    python test_models_service_quick.py --monitor    # Continuous monitoring
    python test_models_service_quick.py --profile    # Performance profiling
"""

import asyncio
import aiohttp
import time
import json
import sys
from datetime import datetime
from pathlib import Path
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuickTester:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        
    async def quick_health_check(self):
        """Quick health check"""
        try:
            async with aiohttp.ClientSession() as session:
                start = time.time()
                async with session.get(f"{self.base_url}/health") as response:
                    duration = time.time() - start
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Service HEALTHY ({duration:.2f}s)")
                        print(f"   Status: {data.get('status')}")
                        print(f"   Service: {data.get('service')}")
                        return True
                    else:
                        print(f"❌ Service UNHEALTHY (HTTP {response.status})")
                        return False
        except Exception as e:
            print(f"❌ Service UNREACHABLE: {e}")
            return False
    
    async def quick_status_check(self):
        """Quick status check with model info"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"📊 SERVICE STATUS:")
                        print(f"   Service: {data.get('service')}")
                        print(f"   Hardware: {data.get('hardware', {}).get('cpu_count')} CPUs, {data.get('hardware', {}).get('memory_gb')}GB RAM")
                        print(f"   GPU: {'Yes' if data.get('hardware', {}).get('gpu_available') else 'No'}")
                        
                        models = data.get('models', {})
                        print(f"   Models Loaded: STT={models.get('stt_loaded', 0)}, TTS={models.get('tts_loaded', 0)}, NLP={models.get('nlp_loaded', 0)}")
                        
                        langs = data.get('supported_languages', {})
                        print(f"   Languages: STT={len(langs.get('stt', []))}, TTS={len(langs.get('tts', []))}")
                        return True
                    else:
                        print(f"❌ Status check failed (HTTP {response.status})")
                        return False
        except Exception as e:
            print(f"❌ Status check error: {e}")
            return False
    
    async def test_stt_endpoint(self):
        """Test STT endpoint availability"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/stt/languages") as response:
                    if response.status == 200:
                        data = await response.json()
                        langs = data.get('supported_languages', [])
                        print(f"🎤 STT: Available ({len(langs)} languages)")
                        if langs:
                            print(f"   Languages: {', '.join(langs[:5])}{'...' if len(langs) > 5 else ''}")
                        return True
                    else:
                        print(f"❌ STT: Unavailable (HTTP {response.status})")
                        return False
        except Exception as e:
            print(f"❌ STT error: {e}")
            return False
    
    async def test_tts_endpoint(self):
        """Test TTS endpoint availability"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/tts/languages") as response:
                    if response.status == 200:
                        data = await response.json()
                        langs = data.get('supported_languages', [])
                        print(f"🔊 TTS: Available ({len(langs)} languages)")
                        if langs:
                            print(f"   Languages: {', '.join(langs[:5])}{'...' if len(langs) > 5 else ''}")
                        return True
                    else:
                        print(f"❌ TTS: Unavailable (HTTP {response.status})")
                        return False
        except Exception as e:
            print(f"❌ TTS error: {e}")
            return False
    
    async def test_simple_tts(self):
        """Test simple TTS synthesis"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "text": "Hello world",
                    "language": "en"
                }
                async with session.post(f"{self.base_url}/api/v1/tts/synthesize", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success'):
                            print(f"🎵 TTS Synthesis: Working")
                            print(f"   Model: {data.get('model_used', 'Unknown')}")
                            print(f"   Duration: {data.get('duration', 'Unknown')}s")
                            return True
                        else:
                            print(f"❌ TTS Synthesis: Failed - {data.get('error')}")
                            return False
                    else:
                        print(f"❌ TTS Synthesis: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ TTS Synthesis error: {e}")
            return False
    
    async def performance_test(self):
        """Quick performance test"""
        print("⚡ Running performance test...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test concurrent health checks
                start = time.time()
                tasks = []
                for _ in range(5):
                    task = asyncio.create_task(session.get(f"{self.base_url}/health"))
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                duration = time.time() - start
                
                successful = sum(1 for r in responses if hasattr(r, 'status') and r.status == 200)
                
                # Close responses
                for response in responses:
                    if hasattr(response, 'close'):
                        response.close()
                
                print(f"📈 Performance: {successful}/5 requests succeeded in {duration:.2f}s")
                print(f"   Avg response time: {duration/5:.3f}s")
                
                return successful >= 4  # 80% success rate
                
        except Exception as e:
            print(f"❌ Performance test error: {e}")
            return False
    
    async def run_full_quick_test(self):
        """Run all quick tests"""
        print("🚀 Running Full Quick Test of Models Service")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.quick_health_check),
            ("Status Check", self.quick_status_check),
            ("STT Endpoint", self.test_stt_endpoint),
            ("TTS Endpoint", self.test_tts_endpoint),
            ("TTS Synthesis", self.test_simple_tts),
            ("Performance", self.performance_test)
        ]
        
        passed = 0
        total = len(tests)
        
        for name, test_func in tests:
            print(f"\n🧪 {name}:")
            try:
                result = await test_func()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ {name} failed: {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 SUMMARY: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests PASSED! Service is working perfectly.")
        elif passed >= total * 0.8:
            print("✅ Most tests PASSED. Service is working well.")
        else:
            print("⚠️  Some tests FAILED. Service may have issues.")
        
        return passed >= total * 0.8
    
    async def monitor_service(self, interval: int = 30):
        """Continuously monitor service health"""
        print(f"👁️  Monitoring service every {interval} seconds. Press Ctrl+C to stop.")
        print("=" * 60)
        
        consecutive_failures = 0
        
        try:
            while True:
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                try:
                    async with aiohttp.ClientSession() as session:
                        start = time.time()
                        async with session.get(f"{self.base_url}/health") as response:
                            duration = time.time() - start
                            
                            if response.status == 200:
                                print(f"[{timestamp}] ✅ HEALTHY ({duration:.3f}s)")
                                consecutive_failures = 0
                            else:
                                consecutive_failures += 1
                                print(f"[{timestamp}] ❌ UNHEALTHY (HTTP {response.status}) - Failures: {consecutive_failures}")
                                
                except Exception as e:
                    consecutive_failures += 1
                    print(f"[{timestamp}] ❌ UNREACHABLE ({e}) - Failures: {consecutive_failures}")
                
                if consecutive_failures >= 3:
                    print(f"🚨 WARNING: {consecutive_failures} consecutive failures detected!")
                
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")

async def main():
    parser = argparse.ArgumentParser(description="Quick Models Service Testing")
    parser.add_argument("--url", default="http://localhost:8080", help="Service URL")
    parser.add_argument("--full", action="store_true", help="Run full quick test suite")
    parser.add_argument("--monitor", action="store_true", help="Continuous monitoring mode")
    parser.add_argument("--interval", type=int, default=30, help="Monitoring interval in seconds")
    parser.add_argument("--profile", action="store_true", help="Performance profiling")
    
    args = parser.parse_args()
    
    tester = QuickTester(args.url)
    
    try:
        if args.monitor:
            await tester.monitor_service(args.interval)
        elif args.full:
            success = await tester.run_full_quick_test()
            return 0 if success else 1
        elif args.profile:
            print("⚡ Performance Profiling")
            await tester.performance_test()
        else:
            # Default: just health check
            success = await tester.quick_health_check()
            return 0 if success else 1
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
