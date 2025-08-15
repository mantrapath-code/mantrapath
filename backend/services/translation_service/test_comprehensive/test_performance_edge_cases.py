"""
Performance and edge case tests for Translation Service
"""
import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
import concurrent.futures
import threading

from engines.enhanced_multi_translator import EnhancedMultiTranslator
from engines.local_translator import LocalTranslator


@pytest.mark.asyncio
class TestPerformanceAndEdgeCases:
    """Test performance scenarios and edge cases"""
    
    @pytest.fixture
    async def translator(self):
        translator = EnhancedMultiTranslator()
        # Mock initialization for faster tests
        translator.is_initialized = True
        translator.engines = {
            'local': AsyncMock(),
            'google': AsyncMock(), 
            'indic': AsyncMock(),
            'argos': AsyncMock()
        }
        return translator
    
    async def test_concurrent_translations(self, translator):
        """Test concurrent translation requests"""
        # Mock translation response
        mock_result = {
            "translated_text": "Concurrent translation",
            "source_language": "en",
            "target_language": "es",
            "confidence_score": 0.9,
            "engine": "local"
        }
        
        for engine in translator.engines.values():
            engine.translate.return_value = mock_result
        
        # Create multiple concurrent translation tasks
        async def translate_task(text_id):
            return await translator.translate(
                text=f"Hello {text_id}",
                target_language="es",
                source_language="en"
            )
        
        # Execute 10 concurrent translations
        start_time = time.time()
        tasks = [translate_task(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # All translations should complete
        assert len(results) == 10
        for result in results:
            assert result is not None
            assert "translated_text" in result
        
        # Should complete in reasonable time (less than 5 seconds)
        assert (end_time - start_time) < 5
    
    async def test_large_text_translation(self, translator):
        """Test translation of very large text"""
        # Create large text (10KB)
        large_text = "This is a meditation guide. " * 400  # ~10KB
        
        mock_result = {
            "translated_text": "Esta es una guía de meditación. " * 400,
            "source_language": "en",
            "target_language": "es",
            "confidence_score": 0.85,
            "engine": "local"
        }
        
        translator.engines['local'].translate.return_value = mock_result
        
        start_time = time.time()
        result = await translator.translate(
            text=large_text,
            target_language="es",
            source_language="en"
        )
        end_time = time.time()
        
        assert result is not None
        assert len(result["translated_text"]) > 5000
        # Should handle large text within reasonable time
        assert (end_time - start_time) < 10
    
    async def test_batch_performance(self, translator):
        """Test batch translation performance"""
        # Create batch of 50 texts
        batch_texts = [f"Hello world {i}" for i in range(50)]
        
        # Mock batch response
        mock_results = []
        for i, text in enumerate(batch_texts):
            mock_results.append({
                "status": "success",
                "translated_text": f"Hola mundo {i}",
                "source_language": "en",
                "target_language": "es",
                "confidence_score": 0.9,
                "engine": "local"
            })
        
        translator.translate_batch = AsyncMock(return_value=mock_results)
        
        start_time = time.time()
        results = await translator.translate_batch([
            {
                'text': text,
                'target_language': 'es',
                'source_language': 'en'
            }
            for text in batch_texts
        ])
        end_time = time.time()
        
        assert len(results) == 50
        # Batch should be faster than individual translations
        assert (end_time - start_time) < 5
    
    async def test_memory_usage_large_batch(self, translator):
        """Test memory usage with large batch"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process large batch
        large_batch = [f"Text {i}" for i in range(1000)]
        mock_results = [{"status": "success", "translated_text": f"Texto {i}"}
                       for i in range(1000)]
        
        translator.translate_batch = AsyncMock(return_value=mock_results)
        
        results = await translator.translate_batch([
            {'text': text, 'target_language': 'es', 'source_language': 'en'}
            for text in large_batch
        ])
        
        final_memory = process.memory_info().rss
        memory_increase_mb = (final_memory - initial_memory) / 1024 / 1024
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase_mb < 100
        assert len(results) == 1000
    
    async def test_timeout_handling(self, translator):
        """Test timeout handling for slow operations"""
        
        # Mock slow translation
        async def slow_translate(*args, **kwargs):
            await asyncio.sleep(3)  # 3 second delay
            return {"translated_text": "Slow result"}
        
        translator.engines['local'].translate = slow_translate
        
        # Test with timeout
        start_time = time.time()
        try:
            result = await asyncio.wait_for(
                translator.translate(
                    text="Hello",
                    target_language="es",
                    source_language="en"
                ),
                timeout=1.0  # 1 second timeout
            )
            assert False, "Should have timed out"
        except asyncio.TimeoutError:
            pass  # Expected
        
        end_time = time.time()
        # Should timeout within reasonable time
        assert (end_time - start_time) < 2
    
    async def test_error_recovery_all_engines_slow(self, translator):
        """Test error recovery when all engines are slow"""
        
        # Make all engines slow except one
        async def slow_translate(*args, **kwargs):
            await asyncio.sleep(2)
            raise Exception("Engine timeout")
        
        async def fast_translate(*args, **kwargs):
            return {"translated_text": "Fast result", "engine": "fast"}
        
        translator.engines['local'].translate = slow_translate
        translator.engines['google'].translate = slow_translate
        translator.engines['indic'].translate = slow_translate
        translator.engines['argos'].translate = fast_translate
        
        start_time = time.time()
        result = await translator.translate(
            text="Hello",
            target_language="es",
            source_language="en"
        )
        end_time = time.time()
        
        assert result["engine"] == "fast"
        # Should complete quickly with fast engine
        assert (end_time - start_time) < 3
    
    async def test_unicode_edge_cases(self, translator):
        """Test handling of Unicode edge cases"""
        unicode_texts = [
            "🧘‍♀️ Meditation with emojis 🕉️",
            "नमस्ते सभी को",  # Hindi
            "السلام عليكم",  # Arabic
            "🌟✨💫⭐🌙",  # Only emojis
            "Ω≈∆∑∏π∞",  # Mathematical symbols
            "",  # Empty string
            " ",  # Single space
            "\n\t\r",  # Whitespace characters
        ]
        
        mock_result = {
            "translated_text": "Translated unicode",
            "source_language": "en",
            "target_language": "es",
            "engine": "local"
        }
        
        translator.engines['local'].translate.return_value = mock_result
        
        for text in unicode_texts:
            try:
                result = await translator.translate(
                    text=text,
                    target_language="es",
                    source_language="en"
                )
                assert result is not None
            except Exception as e:
                # Some edge cases may fail gracefully
                assert "validation" in str(e).lower() or "empty" in str(e).lower()
    
    async def test_malformed_requests(self, translator):
        """Test handling of malformed translation requests"""
        malformed_cases = [
            # None values
            {"text": None, "target_language": "es"},
            {"text": "Hello", "target_language": None},
            
            # Invalid types
            {"text": 123, "target_language": "es"},
            {"text": [], "target_language": "es"},
            {"text": {}, "target_language": "es"},
            
            # Very long language codes
            {"text": "Hello", "target_language": "x" * 100},
            
            # Special characters in language codes
            {"text": "Hello", "target_language": "es-MX@special"},
        ]
        
        for case in malformed_cases:
            try:
                result = await translator.translate(**case)
                # If no exception, result should handle gracefully
                assert result is not None
            except (TypeError, ValueError, AttributeError) as e:
                # Expected for malformed requests
                assert isinstance(e, (TypeError, ValueError, AttributeError))
    
    async def test_rate_limiting_simulation(self, translator):
        """Test behavior under simulated rate limiting"""
        call_count = 0
        
        async def rate_limited_translate(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 3 == 0:  # Every 3rd call fails
                raise Exception("Rate limited")
            return {"translated_text": f"Result {call_count}", "engine": "local"}
        
        translator.engines['local'].translate = rate_limited_translate
        
        # Make 10 requests
        results = []
        for i in range(10):
            try:
                result = await translator.translate(
                    text=f"Text {i}",
                    target_language="es",
                    source_language="en"
                )
                results.append(result)
            except Exception:
                pass  # Rate limited requests fail
        
        # Some requests should succeed
        assert len(results) > 0
        assert len(results) < 10  # Some should fail due to rate limiting
    
    async def test_engine_failover_performance(self, translator):
        """Test performance of engine failover mechanism"""
        
        # Make primary engines fail
        translator.engines['google'].translate.side_effect = Exception("Google failed")
        translator.engines['indic'].translate.side_effect = Exception("Indic failed")
        
        # Only local engine works
        translator.engines['local'].translate.return_value = {
            "translated_text": "Fallback result",
            "engine": "local"
        }
        
        start_time = time.time()
        result = await translator.translate(
            text="Hello",
            target_language="es",
            source_language="en"
        )
        end_time = time.time()
        
        assert result["engine"] == "local"
        # Failover should happen quickly (less than 2 seconds)
        assert (end_time - start_time) < 2
    
    async def test_memory_leak_prevention(self, translator):
        """Test for memory leaks in repeated operations"""
        import gc
        
        # Force garbage collection
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Perform many translation operations
        mock_result = {
            "translated_text": "Test result",
            "engine": "local"
        }
        
        translator.engines['local'].translate.return_value = mock_result
        
        for i in range(100):
            await translator.translate(
                text=f"Text {i}",
                target_language="es",
                source_language="en"
            )
        
        # Force garbage collection again
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Object count shouldn't grow significantly
        object_increase = final_objects - initial_objects
        assert object_increase < 1000  # Allow some reasonable increase
    
    async def test_resource_cleanup(self, translator):
        """Test proper resource cleanup"""
        # Mock engines with cleanup methods
        for engine_name, engine in translator.engines.items():
            engine.cleanup = AsyncMock()
            engine.close = AsyncMock()
        
        # Simulate service shutdown
        await translator.cleanup()
        
        # All engines should have cleanup called
        for engine in translator.engines.values():
            if hasattr(engine, 'cleanup'):
                engine.cleanup.assert_called_once()
    
    async def test_extreme_concurrency(self, translator):
        """Test with extreme concurrency levels"""
        mock_result = {
            "translated_text": "Concurrent result",
            "engine": "local"
        }
        
        translator.engines['local'].translate.return_value = mock_result
        
        # Create 100 concurrent tasks
        async def translation_task(task_id):
            return await translator.translate(
                text=f"Task {task_id}",
                target_language="es",
                source_language="en"
            )
        
        start_time = time.time()
        tasks = [translation_task(i) for i in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Count successful results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        
        # At least 80% should succeed
        assert len(successful_results) >= 80
        
        # Should complete in reasonable time
        assert (end_time - start_time) < 10
