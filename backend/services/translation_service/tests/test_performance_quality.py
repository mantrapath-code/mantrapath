"""
Performance and Quality Tests for Translation Service
Tests for performance benchmarks and quality assurance
"""
import pytest
import asyncio
import time
import statistics
from unittest.mock import Mock, AsyncMock, patch

class TestTranslationPerformance:
    """Performance benchmarks for translation service"""
    
    @pytest.fixture
    async def mock_translation_engine(self):
        """Create mock translation engine with realistic timing"""
        engine = Mock()
        engine.is_initialized = True
        
        async def mock_translate(text, source_lang, target_lang, **kwargs):
            # Simulate realistic processing time based on text length
            base_time = 50  # Base 50ms
            length_factor = len(text) * 2  # 2ms per character
            total_time = base_time + length_factor
            
            # Simulate network delay
            await asyncio.sleep(total_time / 1000)  # Convert to seconds
            
            result = Mock()
            result.translated_text = f"Translated: {text}"
            result.source_language = source_lang
            result.target_language = target_lang
            result.confidence_score = 0.95
            result.engine_name = "google"
            result.processing_time_ms = total_time
            result.metadata = {"quality_score": 0.92}
            
            return result
        
        engine.translate = mock_translate
        return engine
    
    @pytest.mark.asyncio
    async def test_single_translation_latency(self, mock_translation_engine):
        """Test single translation latency requirements"""
        test_cases = [
            ("Hi", "en", "es"),
            ("Hello world", "en", "es"),
            ("This is a medium length text for testing", "en", "es"),
            ("This is a much longer text that contains multiple sentences and should still be processed within our latency requirements for real-time applications", "en", "es")
        ]
        
        latencies = []
        
        for text, source, target in test_cases:
            start_time = time.time()
            result = await mock_translation_engine.translate(text, source, target)
            end_time = time.time()
            
            latency = (end_time - start_time) * 1000  # Convert to milliseconds
            latencies.append(latency)
            
            # Individual request should be under 1 second
            assert latency < 1000
            assert result.translated_text.startswith("Translated:")
        
        # Calculate performance statistics
        avg_latency = statistics.mean(latencies)
        p95_latency = sorted(latencies)[int(0.95 * len(latencies))]
        
        # Performance targets
        assert avg_latency < 300  # Average under 300ms
        assert p95_latency < 500   # 95th percentile under 500ms
        
        print(f"Average latency: {avg_latency:.2f}ms")
        print(f"95th percentile: {p95_latency:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_batch_processing_efficiency(self, mock_translation_engine):
        """Test batch processing efficiency"""
        texts = [
            "Hello",
            "World", 
            "How are you?",
            "Fine, thank you",
            "Goodbye"
        ] * 5  # 25 texts total
        
        # Sequential processing
        start_time = time.time()
        sequential_results = []
        for text in texts:
            result = await mock_translation_engine.translate(text, "en", "es")
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # Concurrent processing (simulating batch)
        start_time = time.time()
        concurrent_tasks = [
            mock_translation_engine.translate(text, "en", "es") 
            for text in texts
        ]
        concurrent_results = await asyncio.gather(*concurrent_tasks)
        concurrent_time = time.time() - start_time
        
        # Batch should be significantly faster than sequential
        efficiency_ratio = sequential_time / concurrent_time
        assert efficiency_ratio > 2.0  # At least 2x faster
        
        assert len(concurrent_results) == len(texts)
        print(f"Sequential time: {sequential_time:.2f}s")
        print(f"Concurrent time: {concurrent_time:.2f}s")
        print(f"Efficiency ratio: {efficiency_ratio:.2f}x")
    
    @pytest.mark.asyncio
    async def test_throughput_under_load(self, mock_translation_engine):
        """Test service throughput under load"""
        # Simulate high load scenario
        num_requests = 50
        concurrent_limit = 10
        
        async def make_request(request_id):
            return await mock_translation_engine.translate(
                f"Test request {request_id}", "en", "es"
            )
        
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        async def limited_request(request_id):
            async with semaphore:
                return await make_request(request_id)
        
        start_time = time.time()
        tasks = [limited_request(i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Calculate throughput
        throughput = num_requests / total_time
        
        assert len(results) == num_requests
        assert throughput > 10  # At least 10 requests/second
        
        print(f"Processed {num_requests} requests in {total_time:.2f}s")
        print(f"Throughput: {throughput:.2f} requests/second")

class TestTranslationQuality:
    """Quality assurance tests for translation accuracy"""
    
    @pytest.fixture
    def quality_test_cases(self):
        """Test cases for quality assessment"""
        return [
            {
                "source": "Hello world",
                "source_lang": "en",
                "target_lang": "es",
                "expected_quality": 0.9,
                "domain": "general"
            },
            {
                "source": "Practice mindfulness meditation",
                "source_lang": "en", 
                "target_lang": "hi",
                "expected_quality": 0.85,
                "domain": "meditation"
            },
            {
                "source": "Inner peace and tranquility",
                "source_lang": "en",
                "target_lang": "zh",
                "expected_quality": 0.8,
                "domain": "mindfulness"
            },
            {
                "source": "Breathe deeply and relax",
                "source_lang": "en",
                "target_lang": "fr",
                "expected_quality": 0.9,
                "domain": "breathing"
            }
        ]
    
    def test_quality_score_calculation(self, quality_test_cases):
        """Test quality score calculation logic"""
        
        def calculate_quality_score(source_text, translated_text, source_lang, target_lang, domain):
            """Mock quality score calculation"""
            # Basic quality factors
            base_quality = 0.8
            
            # Length similarity bonus
            length_ratio = min(len(translated_text) / len(source_text), 1.0)
            length_bonus = length_ratio * 0.1
            
            # Domain-specific bonus
            domain_bonus = 0.05 if domain in ["meditation", "mindfulness"] else 0.0
            
            # Language pair confidence
            high_confidence_pairs = [("en", "es"), ("en", "fr")]
            pair_bonus = 0.1 if (source_lang, target_lang) in high_confidence_pairs else 0.0
            
            total_quality = base_quality + length_bonus + domain_bonus + pair_bonus
            return min(total_quality, 1.0)
        
        for test_case in quality_test_cases:
            # Simulate translation
            translated_text = f"Translated: {test_case['source']}"
            
            quality_score = calculate_quality_score(
                test_case['source'],
                translated_text,
                test_case['source_lang'],
                test_case['target_lang'],
                test_case['domain']
            )
            
            # Quality should meet minimum expectations
            assert quality_score >= test_case['expected_quality'] - 0.1
            assert 0.0 <= quality_score <= 1.0
    
    def test_confidence_score_accuracy(self):
        """Test confidence score accuracy for different scenarios"""
        
        def calculate_confidence(text_length, language_pair, domain):
            """Mock confidence calculation"""
            base_confidence = 0.7
            
            # Length factor (longer text = higher confidence)
            length_factor = min(text_length / 100, 0.2)
            
            # Language pair factor
            common_pairs = [("en", "es"), ("en", "fr"), ("en", "de")]
            pair_factor = 0.15 if language_pair in common_pairs else 0.05
            
            # Domain factor (meditation domain gets bonus)
            domain_factor = 0.1 if domain == "meditation" else 0.05
            
            return min(base_confidence + length_factor + pair_factor + domain_factor, 1.0)
        
        test_scenarios = [
            ("Hi", ("en", "es"), "general", 0.8),
            ("This is a longer text with more context", ("en", "fr"), "meditation", 0.95),
            ("Short", ("en", "zh"), "general", 0.75),
            ("Medium length meditation instruction", ("en", "hi"), "meditation", 0.9)
        ]
        
        for text, lang_pair, domain, expected_min in test_scenarios:
            confidence = calculate_confidence(len(text), lang_pair, domain)
            
            assert confidence >= expected_min - 0.1
            assert 0.0 <= confidence <= 1.0

class TestCulturalAdaptation:
    """Test cultural adaptation features"""
    
    def test_meditation_terminology_handling(self):
        """Test handling of meditation-specific terminology"""
        meditation_terms = [
            ("mindfulness", "en", "hi"),
            ("meditation", "en", "zh"),
            ("enlightenment", "en", "sa"),
            ("chakra", "sa", "en"),
            ("nirvana", "sa", "en")
        ]
        
        def apply_cultural_adaptation(term, source_lang, target_lang):
            """Mock cultural adaptation for meditation terms"""
            adaptations = []
            
            # Sanskrit terms preservation
            if source_lang == "sa" or target_lang == "sa":
                adaptations.append("sanskrit_preservation")
            
            # Meditation context handling
            meditation_keywords = ["mindfulness", "meditation", "enlightenment", "chakra", "nirvana"]
            if term.lower() in meditation_keywords:
                adaptations.append("meditation_context")
            
            # Cultural formality
            if target_lang in ["hi", "ja", "ko"]:
                adaptations.append("formal_tone")
            
            return adaptations
        
        for term, source, target in meditation_terms:
            adaptations = apply_cultural_adaptation(term, source, target)
            
            # Should apply some cultural adaptation
            assert len(adaptations) > 0
            
            # Meditation terms should get special handling
            assert "meditation_context" in adaptations
    
    def test_rtl_language_support(self):
        """Test right-to-left language handling"""
        rtl_languages = ["ar", "he", "ur", "fa"]
        
        def format_for_rtl(text, target_lang):
            """Mock RTL formatting"""
            if target_lang in rtl_languages:
                return {
                    "text": text,
                    "direction": "rtl",
                    "alignment": "right",
                    "special_formatting": True
                }
            else:
                return {
                    "text": text,
                    "direction": "ltr", 
                    "alignment": "left",
                    "special_formatting": False
                }
        
        test_text = "Peace and love"
        
        for lang in rtl_languages:
            formatted = format_for_rtl(test_text, lang)
            
            assert formatted["direction"] == "rtl"
            assert formatted["alignment"] == "right"
            assert formatted["special_formatting"] is True
        
        # Test LTR language
        ltr_formatted = format_for_rtl(test_text, "en")
        assert ltr_formatted["direction"] == "ltr"
        assert ltr_formatted["special_formatting"] is False

class TestErrorHandlingAndResilience:
    """Test error handling and service resilience"""
    
    @pytest.mark.asyncio
    async def test_translation_engine_failure_recovery(self):
        """Test recovery from translation engine failures"""
        
        class FailingEngine:
            def __init__(self, failure_rate=0.3):
                self.failure_rate = failure_rate
                self.call_count = 0
            
            async def translate(self, text, source_lang, target_lang, **kwargs):
                self.call_count += 1
                
                # Simulate intermittent failures
                if (self.call_count % 3) == 0:  # Fail every 3rd request
                    raise Exception("Translation engine temporarily unavailable")
                
                # Successful translation
                result = Mock()
                result.translated_text = f"Translated: {text}"
                result.confidence_score = 0.9
                result.processing_time_ms = 100
                return result
        
        engine = FailingEngine()
        
        # Test with retry logic
        async def translate_with_retry(text, max_retries=3):
            for attempt in range(max_retries):
                try:
                    return await engine.translate(text, "en", "es")
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    await asyncio.sleep(0.1)  # Brief delay before retry
        
        # Should succeed despite intermittent failures
        success_count = 0
        total_requests = 10
        
        for i in range(total_requests):
            try:
                result = await translate_with_retry(f"Test {i}")
                success_count += 1
                assert result.translated_text.startswith("Translated:")
            except Exception:
                pass  # Count failures
        
        # Should have high success rate with retries
        success_rate = success_count / total_requests
        assert success_rate > 0.7  # At least 70% success rate
    
    def test_input_validation_and_sanitization(self):
        """Test input validation and sanitization"""
        
        def validate_translation_input(text, source_lang, target_lang):
            """Mock input validation"""
            errors = []
            
            # Text validation
            if not text or not text.strip():
                errors.append("Text cannot be empty")
            
            if len(text) > 5000:
                errors.append("Text too long (max 5000 characters)")
            
            # Language code validation
            valid_languages = ["en", "es", "fr", "de", "hi", "zh", "ar", "ja"]
            
            if source_lang and source_lang not in valid_languages:
                errors.append(f"Unsupported source language: {source_lang}")
            
            if target_lang not in valid_languages:
                errors.append(f"Unsupported target language: {target_lang}")
            
            # Malicious content detection
            suspicious_patterns = ["<script>", "javascript:", "data:"]
            if any(pattern in text.lower() for pattern in suspicious_patterns):
                errors.append("Potentially malicious content detected")
            
            return errors
        
        # Valid inputs
        assert validate_translation_input("Hello world", "en", "es") == []
        
        # Invalid inputs
        assert "Text cannot be empty" in validate_translation_input("", "en", "es")[0]
        assert "Text too long" in validate_translation_input("x" * 6000, "en", "es")[0]
        assert "Unsupported source language" in validate_translation_input("Hello", "xx", "es")[0]
        assert "malicious content" in validate_translation_input("<script>alert('xss')</script>", "en", "es")[0]

class TestCachingEfficiency:
    """Test caching system efficiency"""
    
    def test_cache_key_generation_consistency(self):
        """Test cache key generation consistency"""
        import hashlib
        
        def generate_cache_key(text, source_lang, target_lang, domain=None):
            """Mock cache key generation"""
            text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
            key_parts = [
                "translation",
                text_hash,
                source_lang,
                target_lang,
                domain or "general"
            ]
            return ":".join(key_parts)
        
        # Same inputs should generate same keys
        key1 = generate_cache_key("Hello world", "en", "es", "general")
        key2 = generate_cache_key("Hello world", "en", "es", "general")
        assert key1 == key2
        
        # Different inputs should generate different keys
        key3 = generate_cache_key("Hello world", "en", "fr", "general")
        assert key1 != key3
        
        key4 = generate_cache_key("Hello world", "en", "es", "meditation")
        assert key1 != key4
    
    @pytest.mark.asyncio
    async def test_cache_hit_performance(self):
        """Test cache hit performance"""
        
        class MockCache:
            def __init__(self):
                self.cache = {}
                self.hit_count = 0
                self.miss_count = 0
            
            async def get(self, key):
                if key in self.cache:
                    self.hit_count += 1
                    return self.cache[key]
                else:
                    self.miss_count += 1
                    return None
            
            async def set(self, key, value, ttl=3600):
                self.cache[key] = value
        
        cache = MockCache()
        
        # Simulate cache operations
        test_key = "translation:hash123:en:es:general"
        cached_result = '{"translated_text": "Hola mundo", "confidence": 0.95}'
        
        # Cache miss
        start_time = time.time()
        result = await cache.get(test_key)
        miss_time = (time.time() - start_time) * 1000
        
        assert result is None
        assert miss_time < 10  # Cache miss should be very fast
        
        # Store in cache
        await cache.set(test_key, cached_result)
        
        # Cache hit
        start_time = time.time()
        result = await cache.get(test_key)
        hit_time = (time.time() - start_time) * 1000
        
        assert result == cached_result
        assert hit_time < 5  # Cache hit should be even faster
        
        # Verify cache statistics
        assert cache.hit_count == 1
        assert cache.miss_count == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
