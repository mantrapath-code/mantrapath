# Story V3-BK-002: Test Strategy & Implementation Guide

## 🧪 Test Coverage Strategy

### Testing Pyramid for Enhanced API Gateway

```
                     E2E Tests (5%)
                   ▲ ┌─────────────────┐
                  ╱ ▲│ Voice Workflows │
                 ╱   │ Cultural Flows  │
                ╱    │ User Journeys   │
               ╱     └─────────────────┘
              ╱
             ╱      Integration Tests (25%)
            ╱      ┌─────────────────────────┐
           ╱       │ Service Communication  │
          ╱        │ WebSocket Streaming    │
         ╱         │ Context Propagation    │
        ╱          │ Cultural Adaptation    │
       ╱           └─────────────────────────┘
      ╱
     ╱             Unit Tests (70%)
    ╱             ┌──────────────────────────────────┐
   ╱              │ Voice Routing Logic              │
  ╱               │ AI Context Injection            │
 ╱                │ Cultural Context Management     │
╱                 │ WebSocket Management            │
▼                 │ Performance Optimization        │
                  └──────────────────────────────────┘
```

## 📋 Unit Tests (Target: 95% Coverage)

### 1. Voice Routing Tests

#### Test File: `tests/test_voice_routing.py`

```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

from middleware.voice_routing import VoiceRoutingMiddleware
from services.voice_router import VoiceRouter
from models.voice_models import VoiceCommand, VoiceIntentType

class TestVoiceRoutingMiddleware:
    """Test voice routing middleware functionality"""
    
    @pytest.fixture
    def voice_router(self):
        return VoiceRouter()
    
    @pytest.fixture
    def voice_middleware(self, voice_router):
        return VoiceRoutingMiddleware(voice_router)
    
    @pytest.mark.asyncio
    async def test_route_english_mood_command(self, voice_middleware):
        """Test routing English mood tracking command"""
        command = VoiceCommand(
            intent=VoiceIntentType.MOOD_TRACKING,
            confidence=0.95,
            language="en",
            parameters={"mood_value": "happy", "intensity": 8},
            raw_text="I'm feeling happy today"
        )
        
        result = await voice_middleware.route_command(command)
        
        assert result.target_service == "mood"
        assert result.endpoint == "/api/v1/mood/"
        assert result.method == "POST"
        assert result.parameters["mood_value"] == "happy"
    
    @pytest.mark.asyncio
    async def test_route_hindi_journal_command(self, voice_middleware):
        """Test routing Hindi journal entry command"""
        command = VoiceCommand(
            intent=VoiceIntentType.JOURNAL_ENTRY,
            confidence=0.88,
            language="hi",
            parameters={"action": "create", "topic": "आज का दिन"},
            raw_text="नई डायरी शुरू करें"
        )
        
        result = await voice_middleware.route_command(command)
        
        assert result.target_service == "mood"
        assert result.endpoint == "/api/v1/journal/"
        assert "आज का दिन" in result.parameters["content"]
    
    @pytest.mark.asyncio
    async def test_route_tamil_cultural_command(self, voice_middleware):
        """Test routing Tamil command with cultural context"""
        command = VoiceCommand(
            intent=VoiceIntentType.MOOD_TRACKING,
            confidence=0.90,
            language="ta",
            parameters={"mood_value": "மகிழ்ச்சி", "family_context": True},
            raw_text="நான் இன்று மகிழ்ச்சியாக இருக்கிறேன்",
            cultural_context="indian_subcontinent"
        )
        
        result = await voice_middleware.route_command(command)
        
        assert result.cultural_adaptations["region"] == "indian_subcontinent"
        assert result.parameters["family_context"] is True
    
    @pytest.mark.asyncio
    async def test_fallback_for_unknown_intent(self, voice_middleware):
        """Test fallback routing for unknown intent"""
        command = VoiceCommand(
            intent=VoiceIntentType.UNKNOWN,
            confidence=0.30,
            language="en",
            parameters={},
            raw_text="unclear voice command"
        )
        
        result = await voice_middleware.route_command(command)
        
        assert result.target_service == "chatbot"
        assert result.fallback_used is True
    
    @pytest.mark.asyncio
    async def test_language_detection_accuracy(self, voice_middleware):
        """Test language detection for various inputs"""
        test_cases = [
            ("I want to track my mood", "en"),
            ("मैं अपना मूड ट्रैक करना चाहता हूं", "hi"),
            ("Quiero rastrear mi estado de ánimo", "es"),
            ("Je veux suivre mon humeur", "fr"),
            ("நான் என் மனநிலையை கண்காணிக்க விரும்புகிறேன்", "ta")
        ]
        
        for text, expected_language in test_cases:
            detected = await voice_middleware.detect_language(text)
            assert detected == expected_language
    
    @pytest.mark.asyncio
    async def test_parameter_extraction_multilingual(self, voice_middleware):
        """Test parameter extraction across languages"""
        test_cases = [
            {
                "text": "My mood is 8 out of 10",
                "language": "en",
                "expected": {"mood_value": 8, "scale": 10}
            },
            {
                "text": "मेरा मूड 7 है",
                "language": "hi", 
                "expected": {"mood_value": 7}
            },
            {
                "text": "Mi estado de ánimo es bueno",
                "language": "es",
                "expected": {"mood_value": "bueno"}
            }
        ]
        
        for case in test_cases:
            params = await voice_middleware.extract_parameters(
                case["text"], case["language"]
            )
            assert params == case["expected"]
    
    def test_routing_rule_validation(self, voice_router):
        """Test routing rule validation"""
        rules = voice_router.get_routing_rules()
        
        # Ensure all intents have routing rules
        for intent in VoiceIntentType:
            if intent != VoiceIntentType.UNKNOWN:
                assert any(rule.intent == intent for rule in rules)
        
        # Ensure all rules have required fields
        for rule in rules:
            assert rule.target_service
            assert rule.endpoint_pattern
            assert isinstance(rule.supported_languages, list)
    
    @pytest.mark.parametrize("language", [
        "en", "hi", "es", "fr", "de", "it", "pt", "ru", "ja", "zh", "ko", "ar",
        "bn", "ta", "te", "gu", "mr", "pa", "ur", "ml", "kn", "as"
    ])
    @pytest.mark.asyncio
    async def test_all_supported_languages(self, voice_middleware, language):
        """Test that all declared languages are supported"""
        test_text = f"Test command in {language}"
        
        # Should not raise exception for any supported language
        try:
            await voice_middleware.process_voice_command(test_text, language)
        except UnsupportedLanguageError:
            pytest.fail(f"Language {language} should be supported")
```

### 2. AI Context Injection Tests

#### Test File: `tests/test_ai_context.py`

```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from middleware.ai_context import AIContextMiddleware
from services.context_manager import ContextManager
from models.context_models import AIContext, UserProfile, ConversationContext

class TestAIContextInjection:
    """Test AI context injection functionality"""
    
    @pytest.fixture
    def context_manager(self):
        return ContextManager()
    
    @pytest.fixture
    def ai_middleware(self, context_manager):
        return AIContextMiddleware(context_manager)
    
    @pytest.mark.asyncio
    async def test_graceful_context_injection(self, ai_middleware):
        """Test graceful context injection without errors"""
        mock_request = Mock()
        mock_request.headers = {}
        
        with patch.object(ai_middleware, 'extract_user_id', return_value="user123"):
            with patch.object(ai_middleware, 'build_ai_context') as mock_build:
                mock_context = Mock(spec=AIContext)
                mock_build.return_value = mock_context
                
                result = await ai_middleware.inject_context(mock_request)
                
                assert "X-AI-Context" in result.headers
                assert "X-Context-Version" in result.headers
    
    @pytest.mark.asyncio
    async def test_timeout_graceful_degradation(self, ai_middleware):
        """Test graceful degradation on context timeout"""
        mock_request = Mock()
        mock_request.headers = {}
        
        with patch.object(ai_middleware, 'extract_user_id', return_value="user123"):
            with patch.object(ai_middleware, 'build_ai_context') as mock_build:
                mock_build.side_effect = asyncio.TimeoutError()
                
                result = await ai_middleware.inject_context(mock_request)
                
                assert result.headers.get("X-AI-Context-Status") == "partial"
    
    @pytest.mark.asyncio
    async def test_error_graceful_degradation(self, ai_middleware):
        """Test graceful degradation on context errors"""
        mock_request = Mock()
        mock_request.headers = {}
        
        with patch.object(ai_middleware, 'extract_user_id', return_value="user123"):
            with patch.object(ai_middleware, 'build_ai_context') as mock_build:
                mock_build.side_effect = Exception("ML Service unavailable")
                
                result = await ai_middleware.inject_context(mock_request)
                
                assert result.headers.get("X-AI-Context-Status") == "failed"
    
    @pytest.mark.asyncio
    async def test_context_building_performance(self, context_manager):
        """Test context building performance within limits"""
        user_id = "user123"
        
        start_time = datetime.utcnow()
        context = await context_manager.build_ai_context(user_id)
        end_time = datetime.utcnow()
        
        duration = (end_time - start_time).total_seconds() * 1000
        assert duration < 50  # Must be under 50ms
    
    @pytest.mark.asyncio
    async def test_context_serialization(self, ai_middleware):
        """Test context serialization and deserialization"""
        context = AIContext(
            user_profile=UserProfile(
                user_id="user123",
                preferences={"language": "en"},
                personality_traits={"openness": 0.8},
                cultural_background="western_europe",
                languages=["en", "fr"],
                timezone="UTC",
                accessibility_needs=[]
            ),
            conversation=ConversationContext(
                session_id="session123",
                conversation_history=[],
                current_topic=None,
                emotional_state={"happiness": 0.7},
                intent_sequence=[],
                last_activity=datetime.utcnow()
            ),
            personalization=Mock(),
            real_time_insights={},
            cultural_adaptations={},
            confidence_scores={}
        )
        
        serialized = ai_middleware.serialize_context(context)
        deserialized = ai_middleware.deserialize_context(serialized)
        
        assert deserialized.user_profile.user_id == context.user_profile.user_id
        assert deserialized.conversation.session_id == context.conversation.session_id
    
    @pytest.mark.asyncio
    async def test_context_compression(self, ai_middleware):
        """Test context compression for large contexts"""
        large_context = Mock()
        large_context.conversation_history = [{"message": f"Message {i}"} for i in range(1000)]
        
        compressed = ai_middleware.compress_context(large_context)
        decompressed = ai_middleware.decompress_context(compressed)
        
        assert len(decompressed.conversation_history) <= 100  # Should be truncated
    
    @pytest.mark.asyncio
    async def test_cultural_context_integration(self, ai_middleware):
        """Test integration of cultural context with AI context"""
        mock_request = Mock()
        mock_request.headers = {"X-Cultural-Context": "indian_subcontinent"}
        
        with patch.object(ai_middleware, 'extract_user_id', return_value="user123"):
            context = await ai_middleware.build_context_with_culture(mock_request)
            
            assert context.cultural_adaptations["region"] == "indian_subcontinent"
```

### 3. Cultural Context Tests

#### Test File: `tests/test_cultural_context.py`

```python
import pytest
from middleware.cultural_context import CulturalContextMiddleware
from services.cultural_manager import CulturalManager
from models.context_models import CulturalContext, CulturalRegion

class TestCulturalContext:
    """Test cultural context propagation functionality"""
    
    @pytest.fixture
    def cultural_manager(self):
        return CulturalManager()
    
    @pytest.fixture
    def cultural_middleware(self, cultural_manager):
        return CulturalContextMiddleware(cultural_manager)
    
    @pytest.mark.parametrize("language,expected_region", [
        ("hi", CulturalRegion.INDIAN_SUBCONTINENT),
        ("ta", CulturalRegion.INDIAN_SUBCONTINENT),
        ("en", CulturalRegion.NORTH_AMERICA),  # Default for en
        ("fr", CulturalRegion.WESTERN_EUROPE),
        ("ja", CulturalRegion.EAST_ASIA),
        ("ar", CulturalRegion.MIDDLE_EAST)
    ])
    def test_language_to_region_mapping(self, cultural_manager, language, expected_region):
        """Test automatic region detection from language"""
        region = cultural_manager.detect_region_from_language(language)
        assert region == expected_region
    
    def test_cultural_adaptation_content(self, cultural_manager):
        """Test cultural adaptation of content"""
        base_content = {
            "greeting": "Hello",
            "mood_options": ["happy", "sad", "excited"]
        }
        
        adapted = cultural_manager.adapt_content(
            base_content, 
            CulturalRegion.INDIAN_SUBCONTINENT,
            "hi"
        )
        
        assert "नमस्ते" in adapted["greeting"]
        assert any("प्रसन्न" in option for option in adapted["mood_options"])
    
    def test_cultural_values_integration(self, cultural_manager):
        """Test Hofstede cultural dimensions integration"""
        context = cultural_manager.get_cultural_context(
            CulturalRegion.INDIAN_SUBCONTINENT, "IN"
        )
        
        # India typically has high power distance and collectivism
        assert context.cultural_values["power_distance"] > 0.7
        assert context.cultural_values["individualism"] < 0.4
    
    def test_religious_considerations(self, cultural_manager):
        """Test religious considerations in cultural context"""
        context = cultural_manager.get_cultural_context(
            CulturalRegion.INDIAN_SUBCONTINENT, "IN"
        )
        
        assert "hinduism" in context.religious_considerations
        assert "islam" in context.religious_considerations
    
    def test_communication_style_adaptation(self, cultural_manager):
        """Test communication style adaptation"""
        direct_style = cultural_manager.adapt_communication_style(
            "Please submit your mood entry",
            CulturalRegion.WESTERN_EUROPE
        )
        
        indirect_style = cultural_manager.adapt_communication_style(
            "Please submit your mood entry", 
            CulturalRegion.INDIAN_SUBCONTINENT
        )
        
        # Indian communication tends to be more indirect and polite
        assert len(indirect_style) > len(direct_style)
        assert "kindly" in indirect_style.lower() or "please" in indirect_style.lower()
    
    @pytest.mark.asyncio
    async def test_context_propagation_headers(self, cultural_middleware):
        """Test cultural context propagation via headers"""
        mock_request = Mock()
        mock_request.headers = {
            "Accept-Language": "hi-IN",
            "X-User-Region": "indian_subcontinent"
        }
        
        result = await cultural_middleware.propagate_context(mock_request)
        
        assert "X-Cultural-Context" in result.headers
        assert "X-Cultural-Region" in result.headers
        assert "X-Communication-Style" in result.headers
```

### 4. WebSocket Tests

#### Test File: `tests/test_websocket.py`

```python
import pytest
import asyncio
import json
import base64
from unittest.mock import Mock, AsyncMock
from fastapi import WebSocket

from services.websocket_manager import EnhancedWebSocketManager

class TestWebSocketManager:
    """Test WebSocket management functionality"""
    
    @pytest.fixture
    def ws_manager(self):
        return EnhancedWebSocketManager()
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self, ws_manager):
        """Test WebSocket connection establishment"""
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        
        await ws_manager.connect(mock_websocket, "user123", "session456")
        
        mock_websocket.accept.assert_called_once()
        assert "user123:session456" in ws_manager.active_connections
    
    @pytest.mark.asyncio
    async def test_voice_streaming(self, ws_manager):
        """Test voice streaming functionality"""
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.send_json = AsyncMock()
        
        # Mock audio data
        audio_data = b"fake_audio_data"
        
        with patch.object(ws_manager, 'process_voice_chunk') as mock_process:
            mock_process.return_value = {
                "partial_transcription": "Hello",
                "confidence": 0.8,
                "command_complete": False
            }
            
            await ws_manager.handle_voice_stream(mock_websocket, "user123", audio_data)
            
            mock_websocket.send_json.assert_called()
            call_args = mock_websocket.send_json.call_args[0][0]
            assert call_args["type"] == "voice_transcription"
            assert call_args["data"]["text"] == "Hello"
    
    @pytest.mark.asyncio
    async def test_voice_command_completion(self, ws_manager):
        """Test voice command completion handling"""
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.send_json = AsyncMock()
        
        with patch.object(ws_manager, 'process_voice_chunk') as mock_process:
            mock_process.return_value = {
                "command_complete": True,
                "final_transcription": "Track my mood as happy",
                "intent": "mood_tracking",
                "parameters": {"mood_value": "happy"}
            }
            
            with patch.object(ws_manager, 'route_voice_command') as mock_route:
                await ws_manager.handle_voice_stream(
                    mock_websocket, "user123", b"audio"
                )
                
                mock_route.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connection_scaling(self, ws_manager):
        """Test WebSocket connection scaling"""
        # Simulate many connections
        connections = []
        for i in range(1000):
            mock_ws = Mock(spec=WebSocket)
            mock_ws.accept = AsyncMock()
            connections.append(mock_ws)
            
            await ws_manager.connect(mock_ws, f"user{i}", f"session{i}")
        
        assert len(ws_manager.active_connections) == 1000
        assert len(ws_manager.user_sessions) <= 1000  # Some users might have multiple sessions
    
    @pytest.mark.asyncio
    async def test_connection_cleanup(self, ws_manager):
        """Test connection cleanup on disconnect"""
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        
        await ws_manager.connect(mock_websocket, "user123", "session456")
        connection_key = "user123:session456"
        
        assert connection_key in ws_manager.active_connections
        
        await ws_manager.disconnect(connection_key)
        
        assert connection_key not in ws_manager.active_connections
```

### 5. Performance Tests

#### Test File: `tests/test_performance.py`

```python
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

from middleware.performance import PerformanceMiddleware
from utils.cache_manager import IntelligentCacheManager

class TestPerformance:
    """Test performance optimization functionality"""
    
    @pytest.fixture
    def cache_manager(self):
        return IntelligentCacheManager()
    
    @pytest.fixture
    def performance_middleware(self, cache_manager):
        return PerformanceMiddleware(cache_manager)
    
    @pytest.mark.asyncio
    async def test_voice_routing_latency(self, performance_middleware):
        """Test voice routing meets latency requirements"""
        mock_command = Mock()
        mock_command.intent = "mood_tracking"
        mock_command.language = "en"
        
        start_time = time.time()
        await performance_middleware.route_voice_command(mock_command)
        end_time = time.time()
        
        latency_ms = (end_time - start_time) * 1000
        assert latency_ms < 50  # Must be under 50ms
    
    @pytest.mark.asyncio
    async def test_ai_context_injection_overhead(self, performance_middleware):
        """Test AI context injection overhead"""
        mock_request = Mock()
        
        # Test without AI context
        start_time = time.time()
        await performance_middleware.process_request_without_context(mock_request)
        baseline_time = time.time() - start_time
        
        # Test with AI context
        start_time = time.time()
        await performance_middleware.process_request_with_context(mock_request)
        context_time = time.time() - start_time
        
        overhead_ms = (context_time - baseline_time) * 1000
        assert overhead_ms < 20  # Must be under 20ms overhead
    
    @pytest.mark.asyncio
    async def test_cache_performance(self, cache_manager):
        """Test cache performance under load"""
        # Populate cache
        for i in range(100):
            await cache_manager.store_context(f"key{i}", Mock())
        
        # Test cache hits
        start_time = time.time()
        for i in range(100):
            await cache_manager.get_ai_context(f"user{i % 10}")  # Some cache hits
        end_time = time.time()
        
        avg_latency_ms = ((end_time - start_time) / 100) * 1000
        assert avg_latency_ms < 5  # Cache operations should be very fast
    
    @pytest.mark.asyncio
    async def test_concurrent_voice_processing(self, performance_middleware):
        """Test concurrent voice command processing"""
        async def process_voice_command():
            mock_command = Mock()
            mock_command.intent = "mood_tracking"
            mock_command.language = "en"
            return await performance_middleware.route_voice_command(mock_command)
        
        # Process 100 concurrent commands
        start_time = time.time()
        tasks = [process_voice_command() for _ in range(100)]
        await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        throughput = 100 / total_time
        assert throughput > 1000  # Should handle 1000+ requests/second
    
    @pytest.mark.asyncio
    async def test_websocket_message_latency(self, performance_middleware):
        """Test WebSocket message routing latency"""
        mock_websocket = Mock()
        mock_websocket.send_json = AsyncMock()
        
        start_time = time.time()
        await performance_middleware.route_websocket_message(
            mock_websocket, {"type": "voice_chunk", "data": "test"}
        )
        end_time = time.time()
        
        latency_ms = (end_time - start_time) * 1000
        assert latency_ms < 30  # Must be under 30ms
    
    def test_cache_hit_ratio(self, cache_manager):
        """Test cache hit ratio optimization"""
        # Simulate realistic access patterns
        for _ in range(1000):
            cache_manager.cache_stats["hits"] += 1
        for _ in range(100):
            cache_manager.cache_stats["misses"] += 1
        
        hit_ratio = cache_manager.cache_stats["hits"] / (
            cache_manager.cache_stats["hits"] + cache_manager.cache_stats["misses"]
        )
        
        assert hit_ratio > 0.8  # Should have >80% cache hit ratio
```

## 🔗 Integration Tests

### Test File: `tests/integration/test_voice_workflow.py`

```python
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch

class TestVoiceWorkflowIntegration:
    """Integration tests for complete voice workflows"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_voice_mood_tracking(self):
        """Test complete voice mood tracking workflow"""
        # Simulate voice input
        voice_data = {
            "type": "voice_command",
            "data": {
                "text": "I'm feeling happy today, mood level 8",
                "language": "en",
                "confidence": 0.95
            }
        }
        
        with patch('services.voice_service.process_voice') as mock_voice:
            mock_voice.return_value = {
                "intent": "mood_tracking",
                "parameters": {"mood_value": "happy", "intensity": 8}
            }
            
            # Process through gateway
            response = await self.gateway.process_voice_command(voice_data)
            
            assert response.status_code == 200
            assert response.json()["success"] is True
            assert "mood_entry_id" in response.json()
    
    @pytest.mark.asyncio
    async def test_multilingual_cultural_adaptation(self):
        """Test multilingual input with cultural adaptation"""
        test_cases = [
            {
                "input": "मैं आज खुश हूं",
                "language": "hi",
                "expected_cultural_region": "indian_subcontinent"
            },
            {
                "input": "நான் இன்று மகிழ்ச்சியாக இருக்கிறேன்",
                "language": "ta", 
                "expected_cultural_region": "indian_subcontinent"
            },
            {
                "input": "Me siento feliz hoy",
                "language": "es",
                "expected_cultural_region": "latin_america"
            }
        ]
        
        for case in test_cases:
            response = await self.gateway.process_voice_command({
                "type": "voice_command",
                "data": {
                    "text": case["input"],
                    "language": case["language"]
                }
            })
            
            assert response.headers.get("X-Cultural-Region") == case["expected_cultural_region"]
    
    @pytest.mark.asyncio
    async def test_ai_context_propagation(self):
        """Test AI context propagation across services"""
        # First, establish user context
        await self.gateway.build_user_context("user123")
        
        # Then make a voice request
        response = await self.gateway.process_voice_command({
            "type": "voice_command",
            "data": {
                "text": "How am I doing this week?",
                "language": "en",
                "user_id": "user123"
            }
        })
        
        # Verify AI context was injected
        assert "X-AI-Context" in response.headers
        assert "personalization" in response.json()["data"]
```

## 📊 Load & Performance Tests

### Test File: `tests/load/test_load.py`

```python
import pytest
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

class TestLoadPerformance:
    """Load and performance tests"""
    
    @pytest.mark.load
    async def test_high_volume_voice_commands(self):
        """Test handling high volume of voice commands"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(1000):
                task = session.post(
                    "http://localhost:8000/voice/command",
                    json={
                        "text": f"Track mood {i % 10}",
                        "language": "en",
                        "user_id": f"user{i % 100}"
                    }
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyze results
            success_count = sum(1 for r in responses if not isinstance(r, Exception))
            success_rate = success_count / len(responses)
            
            assert success_rate > 0.95  # 95% success rate required
    
    @pytest.mark.load
    async def test_websocket_scaling(self):
        """Test WebSocket connection scaling"""
        connections = []
        
        for i in range(1000):
            ws = await websockets.connect(
                f"ws://localhost:8000/ws/user{i}"
            )
            connections.append(ws)
        
        # Send messages through all connections
        for i, ws in enumerate(connections):
            await ws.send(json.dumps({
                "type": "voice_chunk",
                "data": {"sequence": i}
            }))
        
        # Verify all connections are still active
        active_count = sum(1 for ws in connections if not ws.closed)
        assert active_count == 1000
```

## 📈 Test Automation & CI/CD

### GitHub Actions Workflow: `.github/workflows/v3-gateway-tests.yml`

```yaml
name: V3 Gateway Tests

on:
  push:
    paths:
      - 'backend/services/api_gateway/**'
      - 'planning/v3-implementation/**'
  pull_request:
    paths:
      - 'backend/services/api_gateway/**'

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend/services/api_gateway
          pip install -r requirements.txt
          pip install -r test-requirements.txt
      
      - name: Run unit tests
        run: |
          cd backend/services/api_gateway
          pytest tests/unit/ -v --cov=. --cov-report=xml --cov-report=html
          
      - name: Check coverage
        run: |
          cd backend/services/api_gateway
          coverage report --fail-under=95

  integration-tests:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7
        ports:
          - 6379:6379
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Start microservices
        run: |
          docker-compose -f backend/docker-compose.yml up -d
          
      - name: Wait for services
        run: sleep 30
      
      - name: Run integration tests
        run: |
          cd backend/services/api_gateway
          pytest tests/integration/ -v --timeout=300
          
  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run performance benchmarks
        run: |
          cd backend/services/api_gateway
          pytest tests/performance/ -v --benchmark-only
          
      - name: Validate performance targets
        run: |
          # Check that latency targets are met
          python scripts/validate_performance.py

  load-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Run load tests
        run: |
          cd backend/services/api_gateway
          pytest tests/load/ -v -m load
```

## ✅ Test Coverage Goals

### Coverage Targets by Component

| Component | Unit Test Coverage | Integration Coverage | Performance Tests |
|-----------|-------------------|---------------------|------------------|
| Voice Routing | 98% | 100% critical paths | ✅ Latency benchmarks |
| AI Context | 95% | 100% service integration | ✅ Overhead analysis |
| Cultural Context | 90% | 100% regional variants | ✅ Adaptation performance |
| WebSocket Manager | 95% | 100% streaming protocols | ✅ Scaling tests |
| Performance Utils | 90% | 100% cache integration | ✅ Throughput benchmarks |

### Quality Gates

1. **Unit Tests**: 95% coverage minimum
2. **Integration Tests**: All critical paths covered
3. **Performance Tests**: All latency targets met
4. **Load Tests**: Handle 1000+ concurrent requests
5. **Cultural Tests**: All 25+ languages validated
6. **Voice Tests**: All intent types covered
7. **Security Tests**: Authentication & authorization validated
8. **Error Handling**: All failure scenarios tested

This comprehensive test strategy ensures that Story V3-BK-002 delivers robust, performant, and culturally-aware voice routing capabilities that meet enterprise standards.
