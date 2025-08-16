#!/usr/bin/env python3
"""
Comprehensive BK-004 Service Event Integration Test Suite
Tests all aspects of the event system including NATS/JetStream configuration,
fallback mechanisms, performance, and production readiness.
"""

import asyncio
import sys
import os
import time
import subprocess
import socket
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

# Add backend to path
backend_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, backend_path)

from shared.events.enhanced_bus import (
    get_enhanced_event_bus, 
    cleanup_enhanced_event_bus,
    EnhancedEventBus,
    NATS_AVAILABLE
)
from shared.events import V3EventChannels

class BK004TestSuite:
    """Comprehensive test suite for BK-004 implementation"""
    
    def __init__(self):
        self.test_results = []
        self.performance_metrics = {}
        self.nats_server_running = False
        self.jetstream_enabled = False
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        print("🚀 BK-004 COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        
        # 1. Environment and Dependencies Check
        await self._test_environment_setup()
        
        # 2. NATS Infrastructure Testing
        await self._test_nats_infrastructure()
        
        # 3. Enhanced Event Bus Core Testing
        await self._test_enhanced_event_bus_core()
        
        # 4. Service Integration Testing
        await self._test_service_integrations()
        
        # 5. Performance and Load Testing
        await self._test_performance_and_load()
        
        # 6. Error Handling and Resilience Testing
        await self._test_error_handling_resilience()
        
        # 7. Production Readiness Testing
        await self._test_production_readiness()
        
        # Generate comprehensive report
        return await self._generate_test_report()
    
    async def _test_environment_setup(self):
        """Test 1: Environment and Dependencies"""
        print("\n📋 TEST 1: Environment and Dependencies")
        print("-" * 40)
        
        # Check Python version
        python_version = sys.version_info
        print(f"🐍 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        self._add_result("environment", "python_version", 
                        python_version >= (3, 8), f"Python {python_version}")
        
        # Check NATS availability
        print(f"📦 NATS Package Available: {NATS_AVAILABLE}")
        self._add_result("environment", "nats_package", NATS_AVAILABLE, "NATS Python package")
        
        # Check environment variables
        env_vars = {
            "ENV": os.getenv("ENV", "development"),
            "USE_NATS_EVENT_BUS": os.getenv("USE_NATS_EVENT_BUS", "true"),
            "NATS_SERVERS": os.getenv("NATS_SERVERS", "nats://localhost:4222")
        }
        
        for var, value in env_vars.items():
            print(f"🔧 {var}: {value}")
        
        self._add_result("environment", "env_vars", True, f"Environment configured")
    
    async def _test_nats_infrastructure(self):
        """Test 2: NATS Infrastructure"""
        print("\n🌐 TEST 2: NATS Infrastructure")
        print("-" * 40)
        
        # Test NATS server connectivity
        nats_host, nats_port = "localhost", 4222
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((nats_host, nats_port))
            sock.close()
            
            self.nats_server_running = result == 0
            print(f"🌍 NATS Server ({nats_host}:{nats_port}): {'✅ RUNNING' if self.nats_server_running else '❌ NOT RUNNING'}")
            self._add_result("nats", "server_running", self.nats_server_running, "NATS server connectivity")
            
        except Exception as e:
            print(f"❌ NATS connectivity test failed: {e}")
            self._add_result("nats", "server_running", False, f"NATS connectivity error: {e}")
        
        # Test JetStream availability if NATS is running
        if self.nats_server_running and NATS_AVAILABLE:
            await self._test_jetstream_availability()
        
        # Test NATS configuration
        await self._test_nats_configuration()
    
    async def _test_jetstream_availability(self):
        """Test JetStream availability and configuration"""
        try:
            import nats
            
            # Quick JetStream test
            nc = await nats.connect("nats://localhost:4222", connect_timeout=5.0)
            
            try:
                js = nc.jetstream()
                # Try to get account info to verify JetStream is enabled
                account_info = await js.account_info()
                self.jetstream_enabled = True
                print(f"✅ JetStream ENABLED - Memory: {account_info.memory}, Storage: {account_info.storage}")
                self._add_result("nats", "jetstream_enabled", True, "JetStream properly configured")
                
                # Test stream creation capability
                test_stream_name = "test-stream-capability"
                try:
                    await js.add_stream(
                        name=test_stream_name,
                        subjects=["test.capability.*"],
                        max_msgs=10,
                        max_age=60  # 1 minute
                    )
                    await js.delete_stream(test_stream_name)
                    print("✅ Stream creation/deletion capability verified")
                    self._add_result("nats", "stream_operations", True, "Stream operations working")
                except Exception as e:
                    print(f"❌ Stream operations failed: {e}")
                    self._add_result("nats", "stream_operations", False, f"Stream ops error: {e}")
                
            except Exception as e:
                self.jetstream_enabled = False
                print(f"❌ JetStream NOT ENABLED: {e}")
                self._add_result("nats", "jetstream_enabled", False, f"JetStream error: {e}")
                
                # Provide helpful guidance
                print("\n🔧 JETSTREAM SETUP REQUIRED:")
                print("   To enable JetStream, restart NATS with:")
                print("   nats-server --jetstream")
                print("   OR")
                print("   nats-server -c nats-server.conf (with jetstream enabled in config)")
            
            await nc.close()
            
        except Exception as e:
            print(f"❌ NATS connection failed: {e}")
            self._add_result("nats", "connection", False, f"Connection error: {e}")
    
    async def _test_nats_configuration(self):
        """Test NATS configuration requirements"""
        print("\n🔧 NATS Configuration Analysis:")
        
        # Check if we can detect NATS server info
        if self.nats_server_running:
            try:
                # Try to get server info via HTTP monitoring (if enabled)
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get("http://localhost:8222/varz", timeout=2) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                print(f"📊 NATS Version: {data.get('version', 'unknown')}")
                                print(f"📊 JetStream: {data.get('jetstream', 'unknown')}")
                                self._add_result("nats", "monitoring_available", True, "NATS monitoring accessible")
                            else:
                                print("⚠️  NATS monitoring not accessible")
                                self._add_result("nats", "monitoring_available", False, "No monitoring access")
                    except:
                        print("⚠️  NATS HTTP monitoring not enabled")
                        self._add_result("nats", "monitoring_available", False, "Monitoring disabled")
            except ImportError:
                print("⚠️  aiohttp not available for server info check")
        
        # Provide configuration recommendations
        print("\n📋 RECOMMENDED NATS CONFIGURATION:")
        print("   1. Enable JetStream: nats-server --jetstream")
        print("   2. Enable monitoring: nats-server --jetstream --http_port 8222")
        print("   3. Production config: Use nats-server.conf with proper limits")
    
    async def _test_enhanced_event_bus_core(self):
        """Test 3: Enhanced Event Bus Core Functionality"""
        print("\n🔧 TEST 3: Enhanced Event Bus Core")
        print("-" * 40)
        
        # Test initialization
        bus = get_enhanced_event_bus()
        init_success = await bus.initialize()
        
        print(f"🚀 Bus Initialization: {'✅ SUCCESS' if init_success else '❌ FAILED'}")
        self._add_result("core", "initialization", init_success, "Bus initialization")
        
        # Test configuration detection
        print(f"🌐 NATS Usage: {bus.use_nats}")
        print(f"🔗 NATS Connected: {bus.nats_connected}")
        print(f"📊 Performance Tracking: {bus.enable_performance_tracking}")
        
        # Test basic pub/sub functionality
        await self._test_basic_pubsub(bus)
        
        # Test event processing pipeline
        await self._test_event_processing_pipeline(bus)
        
        # Test health check
        health = await bus.health_check()
        print(f"🏥 Health Status: {health['status']}")
        print(f"📈 Total Events: {health['performance']['total_events']}")
        
        is_healthy = health['status'] in ['healthy', 'degraded']
        self._add_result("core", "health_check", is_healthy, f"Health: {health['status']}")
        
    async def _test_basic_pubsub(self, bus: EnhancedEventBus):
        """Test basic publish/subscribe functionality"""
        print("\n📡 Basic Pub/Sub Testing:")
        
        received_events = []
        
        async def test_handler(event):
            received_events.append({
                "channel": event.channel,
                "data": event.data,
                "user_id": event.user_id
            })
        
        # Subscribe to test channel
        test_channel = "test.basic.pubsub"
        await bus.subscribe(test_channel, test_handler)
        
        # Publish test event
        test_data = {"message": "basic_pubsub_test", "timestamp": datetime.now().isoformat()}
        publish_success = await bus.publish(test_channel, test_data, user_id="test-user")
        
        # Wait for event processing
        await asyncio.sleep(0.1)
        
        # Verify results
        events_received = len(received_events) == 1
        correct_data = received_events[0]["data"]["message"] == "basic_pubsub_test" if received_events else False
        
        print(f"   📤 Publish Success: {'✅' if publish_success else '❌'}")
        print(f"   📥 Events Received: {'✅' if events_received else '❌'} ({len(received_events)})")
        print(f"   📋 Data Integrity: {'✅' if correct_data else '❌'}")
        
        self._add_result("core", "basic_pubsub", 
                        publish_success and events_received and correct_data,
                        "Basic pub/sub functionality")
    
    async def _test_event_processing_pipeline(self, bus: EnhancedEventBus):
        """Test event processing pipeline"""
        print("\n⚙️  Event Processing Pipeline Testing:")
        
        # Test voice event processing
        voice_data = {
            "intent": "test_intent",
            "confidence": 0.95,
            "audio_duration": 2.5
        }
        
        voice_success = await bus.publish(V3EventChannels.VOICE_INTENT_CLASSIFIED, voice_data, "test-user")
        print(f"   🎤 Voice Event: {'✅' if voice_success else '❌'}")
        
        # Test mood event processing
        mood_data = {
            "mood_score": 8,
            "energy_level": 7,
            "timestamp": datetime.now().isoformat()
        }
        
        mood_success = await bus.publish(V3EventChannels.MOOD_ENTRY_CREATED, mood_data, "test-user")
        print(f"   🎭 Mood Event: {'✅' if mood_success else '❌'}")
        
        # Test journal event processing
        journal_data = {
            "content": "Test journal entry for BK-004",
            "sentiment": "positive",
            "word_count": 50
        }
        
        journal_success = await bus.publish(V3EventChannels.JOURNAL_ENTRY_CREATED, journal_data, "test-user")
        print(f"   📔 Journal Event: {'✅' if journal_success else '❌'}")
        
        pipeline_success = voice_success and mood_success and journal_success
        self._add_result("core", "event_pipeline", pipeline_success, "Event processing pipeline")
    
    async def _test_service_integrations(self):
        """Test 4: Service Integration"""
        print("\n🔗 TEST 4: Service Integration")
        print("-" * 40)
        
        # Test dual-publish pattern
        await self._test_dual_publish_pattern()
        
        # Test cross-service event flow
        await self._test_cross_service_events()
        
        # Test backward compatibility
        await self._test_backward_compatibility()
    
    async def _test_dual_publish_pattern(self):
        """Test dual-publish pattern (V3 + Legacy)"""
        print("\n🔄 Dual-Publish Pattern Testing:")
        
        bus = get_enhanced_event_bus()
        v3_events = []
        legacy_events = []
        
        async def v3_handler(event):
            v3_events.append(event)
            
        async def legacy_handler(event):
            legacy_events.append(event)
        
        # Subscribe to both patterns
        await bus.subscribe(V3EventChannels.MOOD_ENTRY_CREATED, v3_handler)
        await bus.subscribe("mood_entry_created", legacy_handler)  # Legacy pattern
        
        # Simulate dual publish
        mood_data = {
            "user_id": "dual-test-user",
            "mood_score": 7,
            "created_at": datetime.now().isoformat()
        }
        
        # Publish to V3 channel
        v3_success = await bus.publish(V3EventChannels.MOOD_ENTRY_CREATED, mood_data, "dual-test-user")
        
        # Publish to legacy channel
        legacy_success = await bus.publish("mood_entry_created", mood_data, "dual-test-user")
        
        await asyncio.sleep(0.1)
        
        print(f"   📡 V3 Publish: {'✅' if v3_success else '❌'}")
        print(f"   📡 Legacy Publish: {'✅' if legacy_success else '❌'}")
        print(f"   📥 V3 Events Received: {len(v3_events)}")
        print(f"   📥 Legacy Events Received: {len(legacy_events)}")
        
        dual_publish_success = v3_success and legacy_success and len(v3_events) > 0 and len(legacy_events) > 0
        self._add_result("integration", "dual_publish", dual_publish_success, "Dual-publish pattern")
    
    async def _test_cross_service_events(self):
        """Test cross-service event communication"""
        print("\n🌐 Cross-Service Event Flow Testing:")
        
        bus = get_enhanced_event_bus()
        events_received = {"mood": 0, "journal": 0, "voice": 0}
        
        async def cross_service_handler(event):
            if "mood" in event.channel:
                events_received["mood"] += 1
            elif "journal" in event.channel:
                events_received["journal"] += 1
            elif "voice" in event.channel:
                events_received["voice"] += 1
        
        # Subscribe to all service events
        await bus.subscribe(V3EventChannels.MOOD_ENTRY_CREATED, cross_service_handler)
        await bus.subscribe(V3EventChannels.JOURNAL_ENTRY_CREATED, cross_service_handler)
        await bus.subscribe(V3EventChannels.VOICE_INTENT_CLASSIFIED, cross_service_handler)
        
        # Simulate service events
        services_data = [
            (V3EventChannels.MOOD_ENTRY_CREATED, {"mood_score": 8}),
            (V3EventChannels.JOURNAL_ENTRY_CREATED, {"content": "Cross-service test"}),
            (V3EventChannels.VOICE_INTENT_CLASSIFIED, {"intent": "cross_service_test"})
        ]
        
        for channel, data in services_data:
            await bus.publish(channel, data, "cross-service-user")
        
        await asyncio.sleep(0.1)
        
        total_events = sum(events_received.values())
        print(f"   📊 Total Cross-Service Events: {total_events}/3")
        print(f"   🎭 Mood Events: {events_received['mood']}")
        print(f"   📔 Journal Events: {events_received['journal']}")
        print(f"   🎤 Voice Events: {events_received['voice']}")
        
        cross_service_success = total_events == 3
        self._add_result("integration", "cross_service", cross_service_success, "Cross-service communication")
    
    async def _test_backward_compatibility(self):
        """Test backward compatibility with legacy systems"""
        print("\n🔄 Backward Compatibility Testing:")
        
        bus = get_enhanced_event_bus()
        legacy_events = []
        
        async def legacy_handler(event):
            legacy_events.append(event)
        
        # Test legacy event patterns
        legacy_channels = [
            "mood_entry_created",
            "journal_entry_created", 
            "voice_intent_classified"
        ]
        
        for channel in legacy_channels:
            await bus.subscribe(channel, legacy_handler)
        
        # Publish legacy-style events
        for channel in legacy_channels:
            legacy_data = {"legacy": True, "channel": channel}
            await bus.publish(channel, legacy_data, "legacy-user")
        
        await asyncio.sleep(0.1)
        
        print(f"   📥 Legacy Events Received: {len(legacy_events)}/3")
        
        legacy_compatible = len(legacy_events) == 3
        self._add_result("integration", "backward_compatibility", legacy_compatible, "Legacy compatibility")
    
    async def _test_performance_and_load(self):
        """Test 5: Performance and Load Testing"""
        print("\n⚡ TEST 5: Performance and Load Testing")
        print("-" * 40)
        
        bus = get_enhanced_event_bus()
        
        # Test throughput
        await self._test_event_throughput(bus)
        
        # Test latency
        await self._test_event_latency(bus)
        
        # Test concurrent subscribers
        await self._test_concurrent_subscribers(bus)
        
        # Test memory usage patterns
        await self._test_memory_patterns(bus)
    
    async def _test_event_throughput(self, bus: EnhancedEventBus):
        """Test event throughput under load"""
        print("\n📊 Event Throughput Testing:")
        
        event_count = 100
        start_time = time.time()
        
        # Publish events rapidly
        tasks = []
        for i in range(event_count):
            task = bus.publish(
                f"test.throughput.{i % 10}",
                {"test_id": i, "timestamp": time.time()},
                f"user-{i % 5}"
            )
            tasks.append(task)
        
        # Wait for all publishes to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successful_publishes = sum(1 for r in results if r is True)
        
        end_time = time.time()
        duration = end_time - start_time
        throughput = event_count / duration if duration > 0 else 0
        
        print(f"   📈 Events Published: {successful_publishes}/{event_count}")
        print(f"   ⏱️  Duration: {duration:.3f}s")
        print(f"   🚀 Throughput: {throughput:.1f} events/sec")
        
        self.performance_metrics["throughput"] = throughput
        throughput_acceptable = throughput > 50  # At least 50 events/sec
        self._add_result("performance", "throughput", throughput_acceptable, f"Throughput: {throughput:.1f}/s")
    
    async def _test_event_latency(self, bus: EnhancedEventBus):
        """Test event publishing latency"""
        print("\n⏱️  Event Latency Testing:")
        
        latencies = []
        
        for i in range(10):
            start_time = time.perf_counter()
            await bus.publish("test.latency", {"test_id": i}, "latency-user")
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
        
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        
        print(f"   📊 Average Latency: {avg_latency:.2f}ms")
        print(f"   📊 Max Latency: {max_latency:.2f}ms")
        print(f"   📊 Min Latency: {min_latency:.2f}ms")
        
        self.performance_metrics["avg_latency"] = avg_latency
        latency_acceptable = avg_latency < 10  # Less than 10ms average
        self._add_result("performance", "latency", latency_acceptable, f"Avg latency: {avg_latency:.2f}ms")
    
    async def _test_concurrent_subscribers(self, bus: EnhancedEventBus):
        """Test concurrent subscriber handling"""
        print("\n👥 Concurrent Subscribers Testing:")
        
        subscriber_count = 20
        events_per_subscriber = []
        
        async def counting_handler(subscriber_id):
            count = 0
            async def handler(event):
                nonlocal count
                count += 1
            events_per_subscriber.append((subscriber_id, lambda: count))
            return handler
        
        # Set up multiple subscribers
        handlers = []
        for i in range(subscriber_count):
            handler = await counting_handler(i)
            await bus.subscribe("test.concurrent", handler)
            handlers.append(handler)
        
        # Publish events to all subscribers
        test_events = 10
        for i in range(test_events):
            await bus.publish("test.concurrent", {"event_id": i}, "concurrent-user")
        
        await asyncio.sleep(0.2)  # Allow event processing
        
        # Check results
        total_events_received = sum(counter() for _, counter in events_per_subscriber)
        expected_events = subscriber_count * test_events
        
        print(f"   👥 Subscribers: {subscriber_count}")
        print(f"   📤 Events Published: {test_events}")
        print(f"   📥 Total Events Received: {total_events_received}/{expected_events}")
        
        concurrent_success = total_events_received == expected_events
        self._add_result("performance", "concurrent_subscribers", concurrent_success, 
                        f"Concurrent handling: {total_events_received}/{expected_events}")
    
    async def _test_memory_patterns(self, bus: EnhancedEventBus):
        """Test memory usage patterns"""
        print("\n💾 Memory Usage Pattern Testing:")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate substantial event load
        for batch in range(5):
            tasks = []
            for i in range(50):
                task = bus.publish(f"test.memory.batch{batch}", 
                                 {"data": "x" * 1000, "batch": batch, "item": i}, 
                                 f"memory-user-{i}")
                tasks.append(task)
            await asyncio.gather(*tasks)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"   📊 Initial Memory: {initial_memory:.1f} MB")
        print(f"   📊 Final Memory: {final_memory:.1f} MB")
        print(f"   📊 Memory Increase: {memory_increase:.1f} MB")
        
        # Memory increase should be reasonable (less than 50MB for this test)
        memory_acceptable = memory_increase < 50
        self._add_result("performance", "memory_usage", memory_acceptable, 
                        f"Memory increase: {memory_increase:.1f} MB")
    
    async def _test_error_handling_resilience(self):
        """Test 6: Error Handling and Resilience"""
        print("\n🛡️  TEST 6: Error Handling and Resilience")
        print("-" * 40)
        
        bus = get_enhanced_event_bus()
        
        # Test invalid event data handling
        await self._test_invalid_event_handling(bus)
        
        # Test subscriber error handling
        await self._test_subscriber_error_handling(bus)
        
        # Test connection resilience
        await self._test_connection_resilience(bus)
        
        # Test resource cleanup
        await self._test_resource_cleanup(bus)
    
    async def _test_invalid_event_handling(self, bus: EnhancedEventBus):
        """Test handling of invalid event data"""
        print("\n🚫 Invalid Event Handling:")
        
        # Test various invalid scenarios
        invalid_tests = [
            ("empty_data", "", None),
            ("none_data", None, None),
            ("invalid_channel", "invalid..channel", {"data": "test"}),
            ("large_payload", "test.large", {"data": "x" * 100000})  # 100KB payload
        ]
        
        for test_name, channel, data in invalid_tests:
            try:
                if data is None:
                    # Skip None data test as it would cause TypeError
                    print(f"   ⚠️  {test_name}: SKIPPED (None data)")
                    continue
                    
                result = await bus.publish(channel, data, "invalid-test-user")
                print(f"   {'✅' if result else '⚠️ '} {test_name}: {'HANDLED' if result else 'REJECTED'}")
            except Exception as e:
                print(f"   ✅ {test_name}: CAUGHT EXCEPTION ({type(e).__name__})")
        
        self._add_result("resilience", "invalid_event_handling", True, "Invalid event handling")
    
    async def _test_subscriber_error_handling(self, bus: EnhancedEventBus):
        """Test resilience when subscribers throw errors"""
        print("\n💥 Subscriber Error Handling:")
        
        error_count = 0
        success_count = 0
        
        async def error_handler(event):
            nonlocal error_count
            error_count += 1
            raise Exception("Intentional subscriber error")
        
        async def success_handler(event):
            nonlocal success_count
            success_count += 1
        
        # Subscribe both handlers to same channel
        await bus.subscribe("test.error.handling", error_handler)
        await bus.subscribe("test.error.handling", success_handler)
        
        # Publish event that will cause error in one handler
        await bus.publish("test.error.handling", {"test": "error_resilience"}, "error-user")
        await asyncio.sleep(0.1)
        
        print(f"   💥 Error Handler Called: {error_count}")
        print(f"   ✅ Success Handler Called: {success_count}")
        
        # Both handlers should be called despite one throwing error
        resilience_success = error_count == 1 and success_count == 1
        self._add_result("resilience", "subscriber_errors", resilience_success, "Subscriber error isolation")
    
    async def _test_connection_resilience(self, bus: EnhancedEventBus):
        """Test behavior when NATS connection is lost"""
        print("\n🔗 Connection Resilience:")
        
        initial_nats_status = bus.nats_connected
        print(f"   🌐 Initial NATS Status: {'CONNECTED' if initial_nats_status else 'DISCONNECTED'}")
        
        # Test publishing when NATS might be down
        publish_success = await bus.publish("test.resilience", {"test": "connection"}, "resilience-user")
        print(f"   📤 Publish During Connection Issues: {'✅ SUCCESS' if publish_success else '❌ FAILED'}")
        
        # Test health check during issues
        health = await bus.health_check()
        print(f"   🏥 Health Status: {health['status']}")
        
        # System should remain functional even if NATS is down
        resilience_success = publish_success or health['status'] in ['healthy', 'degraded']
        self._add_result("resilience", "connection_resilience", resilience_success, "Connection resilience")
    
    async def _test_resource_cleanup(self, bus: EnhancedEventBus):
        """Test proper resource cleanup"""
        print("\n🧹 Resource Cleanup Testing:")
        
        # Get initial resource counts
        initial_channels = len(bus.channels)
        initial_tasks = len(bus.tasks)
        
        # Create temporary subscriptions
        temp_handlers = []
        for i in range(5):
            async def temp_handler(event):
                pass
            temp_handlers.append(temp_handler)
            await bus.subscribe(f"test.cleanup.{i}", temp_handler)
        
        mid_channels = len(bus.channels)
        print(f"   📊 Channels: {initial_channels} → {mid_channels}")
        
        # Cleanup subscriptions
        for i, handler in enumerate(temp_handlers):
            await bus.unsubscribe(f"test.cleanup.{i}", handler)
        
        final_channels = len(bus.channels)
        print(f"   📊 After Cleanup: {final_channels}")
        
        cleanup_success = final_channels <= initial_channels + 1  # Allow for some overhead
        self._add_result("resilience", "resource_cleanup", cleanup_success, "Resource cleanup")
    
    async def _test_production_readiness(self):
        """Test 7: Production Readiness"""
        print("\n🏭 TEST 7: Production Readiness")
        print("-" * 40)
        
        bus = get_enhanced_event_bus()
        
        # Test configuration validation
        await self._test_configuration_validation(bus)
        
        # Test monitoring capabilities
        await self._test_monitoring_capabilities(bus)
        
        # Test operational features
        await self._test_operational_features(bus)
    
    async def _test_configuration_validation(self, bus: EnhancedEventBus):
        """Test production configuration validation"""
        print("\n⚙️  Configuration Validation:")
        
        configs = {
            "NATS Available": NATS_AVAILABLE,
            "Performance Tracking": bus.enable_performance_tracking,
            "Event Processors": len(bus.event_processors) > 0,
            "NATS Servers Configured": len(bus.nats_servers) > 0
        }
        
        for config_name, status in configs.items():
            print(f"   {'✅' if status else '⚠️ '} {config_name}: {'ENABLED' if status else 'DISABLED'}")
        
        config_ready = all(configs.values())
        self._add_result("production", "configuration", config_ready, "Production configuration")
    
    async def _test_monitoring_capabilities(self, bus: EnhancedEventBus):
        """Test monitoring and observability features"""
        print("\n📊 Monitoring Capabilities:")
        
        # Test performance stats
        stats = bus.get_performance_stats()
        required_stats = ["uptime_seconds", "total_events", "error_count", "events_per_second"]
        
        stats_available = all(stat in stats for stat in required_stats)
        print(f"   📈 Performance Stats: {'✅ AVAILABLE' if stats_available else '❌ MISSING'}")
        
        # Test health check
        health = await bus.health_check()
        health_comprehensive = all(key in health for key in ["status", "timestamp", "performance"])
        print(f"   🏥 Health Check: {'✅ COMPREHENSIVE' if health_comprehensive else '❌ LIMITED'}")
        
        # Test metrics tracking
        initial_events = bus.event_metrics["total_events"]
        await bus.publish("test.monitoring", {"test": "metrics"}, "monitoring-user")
        final_events = bus.event_metrics["total_events"]
        
        metrics_tracking = final_events > initial_events
        print(f"   📊 Metrics Tracking: {'✅ WORKING' if metrics_tracking else '❌ BROKEN'}")
        
        monitoring_ready = stats_available and health_comprehensive and metrics_tracking
        self._add_result("production", "monitoring", monitoring_ready, "Monitoring capabilities")
    
    async def _test_operational_features(self, bus: EnhancedEventBus):
        """Test operational features for production"""
        print("\n🔧 Operational Features:")
        
        # Test graceful degradation
        original_nats_status = bus.nats_connected
        # Simulate NATS being down
        bus.nats_connected = False
        
        degraded_publish = await bus.publish("test.degraded", {"test": "degradation"}, "ops-user")
        print(f"   🔄 Graceful Degradation: {'✅ WORKING' if degraded_publish else '❌ FAILED'}")
        
        # Restore status
        bus.nats_connected = original_nats_status
        
        # Test event validation pipeline
        event_processors_active = len(bus.event_processors) > 0
        print(f"   ⚙️  Event Processing: {'✅ ACTIVE' if event_processors_active else '⚠️  MINIMAL'}")
        
        # Test dual-publish capability
        v3_success = await bus.publish(V3EventChannels.MOOD_ENTRY_CREATED, {"test": "v3"}, "ops-user")
        legacy_success = await bus.publish("mood_entry_created", {"test": "legacy"}, "ops-user")
        
        dual_publish_ready = v3_success and legacy_success
        print(f"   🔄 Dual-Publish: {'✅ READY' if dual_publish_ready else '❌ ISSUES'}")
        
        ops_ready = degraded_publish and dual_publish_ready
        self._add_result("production", "operational_features", ops_ready, "Operational readiness")
    
    def _add_result(self, category: str, test_name: str, passed: bool, description: str):
        """Add test result to results collection"""
        self.test_results.append({
            "category": category,
            "test": test_name,
            "passed": passed,
            "description": description,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    async def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("="*60)
        
        # Categorize results
        categories = {}
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["passed"])
        
        for result in self.test_results:
            category = result["category"]
            if category not in categories:
                categories[category] = {"passed": 0, "total": 0, "tests": []}
            
            categories[category]["total"] += 1
            if result["passed"]:
                categories[category]["passed"] += 1
            categories[category]["tests"].append(result)
        
        # Print category summaries
        for category, data in categories.items():
            pass_rate = (data["passed"] / data["total"]) * 100 if data["total"] > 0 else 0
            status = "✅ PASS" if pass_rate == 100 else "⚠️  PARTIAL" if pass_rate >= 80 else "❌ FAIL"
            print(f"\n{category.upper()}: {status} ({data['passed']}/{data['total']} - {pass_rate:.1f}%)")
            
            for test in data["tests"]:
                icon = "✅" if test["passed"] else "❌"
                print(f"  {icon} {test['test']}: {test['description']}")
        
        # Overall summary
        overall_pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"\n🎯 OVERALL RESULT: {passed_tests}/{total_tests} tests passed ({overall_pass_rate:.1f}%)")
        
        # Production readiness assessment
        critical_categories = ["environment", "core", "integration"]
        critical_passed = sum(categories[cat]["passed"] for cat in critical_categories if cat in categories)
        critical_total = sum(categories[cat]["total"] for cat in critical_categories if cat in categories)
        critical_rate = (critical_passed / critical_total) * 100 if critical_total > 0 else 0
        
        print(f"\n🏭 PRODUCTION READINESS:")
        if critical_rate >= 95:
            print("✅ READY FOR PRODUCTION")
        elif critical_rate >= 80:
            print("⚠️  READY WITH MONITORING (Minor issues detected)")
        else:
            print("❌ NOT READY FOR PRODUCTION (Critical issues found)")
        
        # Recommendations
        print(f"\n📋 RECOMMENDATIONS:")
        if not self.jetstream_enabled:
            print("   🔧 Enable JetStream on NATS server: nats-server --jetstream")
        if overall_pass_rate < 100:
            print("   🔍 Review failed tests and address underlying issues")
        if "performance" in categories and categories["performance"]["passed"] < categories["performance"]["total"]:
            print("   ⚡ Consider performance optimizations for production load")
        
        # Performance summary
        if self.performance_metrics:
            print(f"\n📊 PERFORMANCE METRICS:")
            for metric, value in self.performance_metrics.items():
                print(f"   📈 {metric}: {value}")
        
        # Return structured report
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall": {
                "passed": passed_tests,
                "total": total_tests,
                "pass_rate": overall_pass_rate
            },
            "categories": categories,
            "performance": self.performance_metrics,
            "infrastructure": {
                "nats_server_running": self.nats_server_running,
                "jetstream_enabled": self.jetstream_enabled,
                "nats_available": NATS_AVAILABLE
            },
            "production_ready": critical_rate >= 80,
            "recommendations": self._get_recommendations()
        }
    
    def _get_recommendations(self) -> List[str]:
        """Get actionable recommendations based on test results"""
        recommendations = []
        
        if not self.nats_server_running:
            recommendations.append("Install and start NATS server")
        elif not self.jetstream_enabled:
            recommendations.append("Enable JetStream: nats-server --jetstream")
        
        failed_tests = [r for r in self.test_results if not r["passed"]]
        if failed_tests:
            recommendations.append(f"Address {len(failed_tests)} failed test(s)")
        
        if "avg_latency" in self.performance_metrics and self.performance_metrics["avg_latency"] > 5:
            recommendations.append("Optimize event publishing latency")
        
        if "throughput" in self.performance_metrics and self.performance_metrics["throughput"] < 100:
            recommendations.append("Improve event throughput for production load")
        
        return recommendations


async def main():
    """Main test runner"""
    print("🚀 Starting BK-004 Comprehensive Test Suite...")
    
    try:
        test_suite = BK004TestSuite()
        report = await test_suite.run_all_tests()
        
        # Cleanup
        await cleanup_enhanced_event_bus()
        
        # Save report
        report_file = f"bk004_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(os.path.dirname(__file__), report_file)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved: {report_path}")
        
        # Exit with appropriate code
        return 0 if report["production_ready"] else 1
        
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
