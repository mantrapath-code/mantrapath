#!/usr/bin/env python3
"""
Voice Latency Collector for MantraPath V3
Monitors voice processing performance metrics including STT, TTS, and routing latency
"""

import time
import logging
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import statistics
from prometheus_client import Counter, Histogram, Gauge, Summary
import redis.asyncio as redis
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VoiceLatencyMetrics:
    """Voice processing latency metrics"""
    stt_processing_time: float = 0.0
    tts_generation_time: float = 0.0
    voice_command_routing_time: float = 0.0
    voice_session_establishment_time: float = 0.0
    total_processing_time: float = 0.0
    confidence_score: Optional[float] = None
    language: str = "unknown"
    engine: str = "unknown"
    success: bool = True
    error_type: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class VoiceLatencyCollector:
    """Collects and tracks voice processing latency metrics"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.metrics_buffer: List[VoiceLatencyMetrics] = []
        self.buffer_size = 100
        self.flush_interval = 30  # seconds
        
        # Prometheus metrics
        self._setup_prometheus_metrics()
        
        # Performance thresholds
        self.thresholds = {
            "stt_processing": 2.0,      # 2 seconds
            "tts_generation": 1.0,      # 1 second
            "command_routing": 0.05,    # 50ms
            "session_establishment": 0.1,  # 100ms
            "total_processing": 3.0     # 3 seconds
        }
        
        # Start background tasks
        self.running = True
        asyncio.create_task(self._background_flush())
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for voice latency monitoring"""
        
        # Voice processing duration histograms
        self.stt_processing_duration = Histogram(
            'voice_stt_processing_duration_seconds',
            'STT processing duration in seconds',
            ['language', 'engine', 'status']
        )
        
        self.tts_generation_duration = Histogram(
            'voice_tts_generation_duration_seconds',
            'TTS generation duration in seconds',
            ['language', 'engine', 'status']
        )
        
        self.voice_routing_duration = Histogram(
            'voice_command_routing_duration_seconds',
            'Voice command routing duration in seconds',
            ['language', 'intent', 'status']
        )
        
        self.session_establishment_duration = Histogram(
            'voice_session_establishment_duration_seconds',
            'Voice session establishment duration in seconds',
            ['language', 'status']
        )
        
        self.total_processing_duration = Histogram(
            'voice_total_processing_duration_seconds',
            'Total voice processing duration in seconds',
            ['language', 'engine', 'status']
        )
        
        # Voice processing counters
        self.voice_processing_requests = Counter(
            'voice_processing_requests_total',
            'Total voice processing requests',
            ['language', 'engine', 'status', 'error_type']
        )
        
        self.voice_sessions_active = Gauge(
            'voice_sessions_active',
            'Number of active voice sessions',
            ['language']
        )
        
        # Voice quality metrics
        self.voice_confidence_score = Summary(
            'voice_confidence_score',
            'Voice recognition confidence score',
            ['language', 'engine']
        )
        
        # Voice engine availability
        self.voice_engine_availability = Gauge(
            'voice_engine_availability',
            'Voice engine availability status',
            ['engine', 'language']
        )
        
        # Voice error rates
        self.voice_error_rate = Counter(
            'voice_error_rate_total',
            'Voice processing error rate',
            ['error_type', 'language', 'engine']
        )
    
    async def connect_redis(self):
        """Connect to Redis for metrics storage"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("✅ Connected to Redis for voice metrics storage")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def track_stt_processing(self, language: str, engine: str, duration: float, 
                           confidence: Optional[float] = None, success: bool = True,
                           error_type: Optional[str] = None):
        """Track STT processing performance"""
        try:
            # Record Prometheus metrics
            status = "success" if success else "failure"
            self.stt_processing_duration.labels(
                language=language,
                engine=engine,
                status=status
            ).observe(duration)
            
            # Record confidence score if available
            if confidence is not None:
                self.voice_confidence_score.labels(
                    language=language,
                    engine=engine
                ).observe(confidence)
            
            # Record request count
            self.voice_processing_requests.labels(
                language=language,
                engine=engine,
                status=status,
                error_type=error_type or "none"
            ).inc()
            
            # Record error if applicable
            if not success and error_type:
                self.voice_error_rate.labels(
                    error_type=error_type,
                    language=language,
                    engine=engine
                ).inc()
            
            # Check performance thresholds
            if duration > self.thresholds["stt_processing"]:
                logger.warning(f"⚠️ STT processing exceeded threshold: {duration}s > {self.thresholds['stt_processing']}s "
                             f"(Language: {language}, Engine: {engine})")
            
            # Store detailed metrics
            metrics = VoiceLatencyMetrics(
                stt_processing_time=duration,
                language=language,
                engine=engine,
                success=success,
                error_type=error_type,
                confidence_score=confidence
            )
            
            self._add_to_buffer(metrics)
            
        except Exception as e:
            logger.error(f"❌ Error tracking STT processing: {e}")
    
    def track_tts_generation(self, language: str, engine: str, duration: float,
                            text_length: int, success: bool = True,
                            error_type: Optional[str] = None):
        """Track TTS generation performance"""
        try:
            # Record Prometheus metrics
            status = "success" if success else "failure"
            self.tts_generation_duration.labels(
                language=language,
                engine=engine,
                status=status
            ).observe(duration)
            
            # Record request count
            self.voice_processing_requests.labels(
                language=language,
                engine=engine,
                status=status,
                error_type=error_type or "none"
            ).inc()
            
            # Record error if applicable
            if not success and error_type:
                self.voice_error_rate.labels(
                    error_type=error_type,
                    language=language,
                    engine=engine
                ).inc()
            
            # Check performance thresholds
            if duration > self.thresholds["tts_generation"]:
                logger.warning(f"⚠️ TTS generation exceeded threshold: {duration}s > {self.thresholds['tts_generation']}s "
                             f"(Language: {language}, Engine: {engine}, Text length: {text_length})")
            
            # Store detailed metrics
            metrics = VoiceLatencyMetrics(
                tts_generation_time=duration,
                language=language,
                engine=engine,
                success=success,
                error_type=error_type
            )
            
            self._add_to_buffer(metrics)
            
        except Exception as e:
            logger.error(f"❌ Error tracking TTS generation: {e}")
    
    def track_voice_routing(self, language: str, intent: str, duration: float,
                           success: bool = True, error_type: Optional[str] = None):
        """Track voice command routing performance"""
        try:
            # Record Prometheus metrics
            status = "success" if success else "failure"
            self.voice_routing_duration.labels(
                language=language,
                intent=intent,
                status=status
            ).observe(duration)
            
            # Record request count
            self.voice_processing_requests.labels(
                language=language,
                engine="routing",
                status=status,
                error_type=error_type or "none"
            ).inc()
            
            # Record error if applicable
            if not success and error_type:
                self.voice_error_rate.labels(
                    error_type=error_type,
                    language=language,
                    engine="routing"
                ).inc()
            
            # Check performance thresholds
            if duration > self.thresholds["command_routing"]:
                logger.warning(f"⚠️ Voice routing exceeded threshold: {duration}s > {self.thresholds['command_routing']}s "
                             f"(Language: {language}, Intent: {intent})")
            
            # Store detailed metrics
            metrics = VoiceLatencyMetrics(
                voice_command_routing_time=duration,
                language=language,
                success=success,
                error_type=error_type
            )
            
            self._add_to_buffer(metrics)
            
        except Exception as e:
            logger.error(f"❌ Error tracking voice routing: {e}")
    
    def track_session_establishment(self, language: str, duration: float,
                                  success: bool = True, error_type: Optional[str] = None):
        """Track voice session establishment performance"""
        try:
            # Record Prometheus metrics
            status = "success" if success else "failure"
            self.session_establishment_duration.labels(
                language=language,
                status=status
            ).observe(duration)
            
            # Update active sessions count
            if success:
                self.voice_sessions_active.labels(language=language).inc()
            else:
                self.voice_sessions_active.labels(language=language).dec()
            
            # Record request count
            self.voice_processing_requests.labels(
                language=language,
                engine="session",
                status=status,
                error_type=error_type or "none"
            ).inc()
            
            # Record error if applicable
            if not success and error_type:
                self.voice_error_rate.labels(
                    error_type=error_type,
                    language=language,
                    engine="session"
                ).inc()
            
            # Check performance thresholds
            if duration > self.thresholds["session_establishment"]:
                logger.warning(f"⚠️ Session establishment exceeded threshold: {duration}s > {self.thresholds['session_establishment']}s "
                             f"(Language: {language})")
            
            # Store detailed metrics
            metrics = VoiceLatencyMetrics(
                voice_session_establishment_time=duration,
                language=language,
                success=success,
                error_type=error_type
            )
            
            self._add_to_buffer(metrics)
            
        except Exception as e:
            logger.error(f"❌ Error tracking session establishment: {e}")
    
    def track_complete_voice_processing(self, language: str, engine: str,
                                      stt_time: float, tts_time: float,
                                      routing_time: float, session_time: float,
                                      total_time: float, success: bool = True,
                                      error_type: Optional[str] = None):
        """Track complete voice processing workflow"""
        try:
            # Calculate total processing time
            calculated_total = stt_time + tts_time + routing_time + session_time
            
            # Record total processing duration
            status = "success" if success else "failure"
            self.total_processing_duration.labels(
                language=language,
                engine=engine,
                status=status
            ).observe(total_time)
            
            # Check performance thresholds
            if total_time > self.thresholds["total_processing"]:
                logger.warning(f"⚠️ Total processing exceeded threshold: {total_time}s > {self.thresholds['total_processing']}s "
                             f"(Language: {language}, Engine: {engine})")
            
            # Store comprehensive metrics
            metrics = VoiceLatencyMetrics(
                stt_processing_time=stt_time,
                tts_generation_time=tts_time,
                voice_command_routing_time=routing_time,
                voice_session_establishment_time=session_time,
                total_processing_time=total_time,
                language=language,
                engine=engine,
                success=success,
                error_type=error_type
            )
            
            self._add_to_buffer(metrics)
            
        except Exception as e:
            logger.error(f"❌ Error tracking complete voice processing: {e}")
    
    def _add_to_buffer(self, metrics: VoiceLatencyMetrics):
        """Add metrics to buffer for batch processing"""
        self.metrics_buffer.append(metrics)
        
        # Flush buffer if it's full
        if len(self.metrics_buffer) >= self.buffer_size:
            asyncio.create_task(self._flush_metrics())
    
    async def _flush_metrics(self):
        """Flush metrics buffer to Redis"""
        if not self.metrics_buffer or not self.redis_client:
            return
        
        try:
            # Convert metrics to JSON-serializable format
            metrics_data = []
            for metric in self.metrics_buffer:
                metric_dict = {
                    "stt_processing_time": metric.stt_processing_time,
                    "tts_generation_time": metric.tts_generation_time,
                    "voice_command_routing_time": metric.voice_command_routing_time,
                    "voice_session_establishment_time": metric.voice_session_establishment_time,
                    "total_processing_time": metric.total_processing_time,
                    "confidence_score": metric.confidence_score,
                    "language": metric.language,
                    "engine": metric.engine,
                    "success": metric.success,
                    "error_type": metric.error_type,
                    "timestamp": metric.timestamp.isoformat()
                }
                metrics_data.append(metric_dict)
            
            # Store in Redis with timestamp key
            timestamp = datetime.now(timezone.utc).isoformat()
            key = f"voice_metrics:{timestamp}"
            
            await self.redis_client.setex(
                key,
                3600,  # 1 hour TTL
                json.dumps(metrics_data)
            )
            
            # Clear buffer
            self.metrics_buffer.clear()
            
            logger.debug(f"✅ Flushed {len(metrics_data)} voice metrics to Redis")
            
        except Exception as e:
            logger.error(f"❌ Error flushing voice metrics: {e}")
    
    async def _background_flush(self):
        """Background task to flush metrics periodically"""
        while self.running:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_metrics()
            except Exception as e:
                logger.error(f"❌ Error in background flush: {e}")
    
    async def get_performance_summary(self, language: Optional[str] = None,
                                    time_window: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """Get voice performance summary for the specified time window"""
        try:
            if not self.redis_client:
                return {"error": "Redis not connected"}
            
            # Get metrics from Redis
            metrics = await self._get_metrics_from_redis(time_window)
            
            if not metrics:
                return {"message": "No metrics available for the specified time window"}
            
            # Filter by language if specified
            if language:
                metrics = [m for m in metrics if m.get("language") == language]
            
            # Calculate summary statistics
            summary = self._calculate_summary_statistics(metrics)
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting performance summary: {e}")
            return {"error": str(e)}
    
    async def _get_metrics_from_redis(self, time_window: timedelta) -> List[Dict[str, Any]]:
        """Retrieve metrics from Redis for the specified time window"""
        try:
            # Get all voice metrics keys
            pattern = "voice_metrics:*"
            keys = await self.redis_client.keys(pattern)
            
            if not keys:
                return []
            
            # Filter keys by time window
            cutoff_time = datetime.now(timezone.utc) - time_window
            valid_keys = []
            
            for key in keys:
                try:
                    # Extract timestamp from key
                    timestamp_str = key.decode().split(":")[1]
                    key_time = datetime.fromisoformat(timestamp_str)
                    
                    if key_time >= cutoff_time:
                        valid_keys.append(key)
                except Exception:
                    continue
            
            # Retrieve metrics data
            all_metrics = []
            for key in valid_keys:
                try:
                    data = await self.redis_client.get(key)
                    if data:
                        metrics_batch = json.loads(data)
                        all_metrics.extend(metrics_batch)
                except Exception:
                    continue
            
            return all_metrics
            
        except Exception as e:
            logger.error(f"❌ Error retrieving metrics from Redis: {e}")
            return []
    
    def _calculate_summary_statistics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics from metrics data"""
        if not metrics:
            return {}
        
        # Extract numeric values
        stt_times = [m.get("stt_processing_time", 0) for m in metrics if m.get("stt_processing_time")]
        tts_times = [m.get("tts_generation_time", 0) for m in metrics if m.get("tts_generation_time")]
        routing_times = [m.get("voice_command_routing_time", 0) for m in metrics if m.get("voice_command_routing_time")]
        session_times = [m.get("voice_session_establishment_time", 0) for m in metrics if m.get("voice_session_establishment_time")]
        total_times = [m.get("total_processing_time", 0) for m in metrics if m.get("total_processing_time")]
        confidence_scores = [m.get("confidence_score", 0) for m in metrics if m.get("confidence_score")]
        
        # Calculate statistics
        def safe_stats(values):
            if not values:
                return {"count": 0, "mean": 0, "median": 0, "p95": 0, "p99": 0, "min": 0, "max": 0}
            
            sorted_values = sorted(values)
            return {
                "count": len(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "p95": sorted_values[int(len(sorted_values) * 0.95)] if len(sorted_values) > 0 else 0,
                "p99": sorted_values[int(len(sorted_values) * 0.99)] if len(sorted_values) > 0 else 0,
                "min": min(values),
                "max": max(values)
            }
        
        # Calculate success rates
        total_requests = len(metrics)
        successful_requests = len([m for m in metrics if m.get("success", False)])
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Language distribution
        language_distribution = {}
        for metric in metrics:
            lang = metric.get("language", "unknown")
            language_distribution[lang] = language_distribution.get(lang, 0) + 1
        
        # Engine distribution
        engine_distribution = {}
        for metric in metrics:
            engine = metric.get("engine", "unknown")
            engine_distribution[engine] = engine_distribution.get(engine, 0) + 1
        
        # Error distribution
        error_distribution = {}
        for metric in metrics:
            error_type = metric.get("error_type", "none")
            error_distribution[error_type] = error_distribution.get(error_type, 0) + 1
        
        return {
            "summary": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "success_rate_percentage": round(success_rate, 2),
                "time_window_hours": time_window.total_seconds() / 3600
            },
            "performance_metrics": {
                "stt_processing": safe_stats(stt_times),
                "tts_generation": safe_stats(tts_times),
                "voice_routing": safe_stats(routing_times),
                "session_establishment": safe_stats(session_times),
                "total_processing": safe_stats(total_times)
            },
            "quality_metrics": {
                "confidence_scores": safe_stats(confidence_scores)
            },
            "distribution": {
                "languages": language_distribution,
                "engines": engine_distribution,
                "errors": error_distribution
            },
            "thresholds": self.thresholds,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def update_engine_availability(self, engine: str, language: str, available: bool):
        """Update voice engine availability status"""
        try:
            status = 1 if available else 0
            self.voice_engine_availability.labels(
                engine=engine,
                language=language
            ).set(status)
            
            if not available:
                logger.warning(f"⚠️ Voice engine {engine} for {language} is unavailable")
            else:
                logger.info(f"✅ Voice engine {engine} for {language} is available")
                
        except Exception as e:
            logger.error(f"❌ Error updating engine availability: {e}")
    
    async def shutdown(self):
        """Shutdown the collector gracefully"""
        self.running = False
        await self._flush_metrics()
        
        if self.redis_client:
            await self.redis_client.close()

# Example usage and testing
async def main():
    """Example usage of VoiceLatencyCollector"""
    collector = VoiceLatencyCollector()
    await collector.connect_redis()
    
    # Simulate voice processing metrics
    collector.track_stt_processing("en", "whisper", 1.5, confidence=0.95)
    collector.track_tts_generation("en", "elevenlabs", 0.8, text_length=100)
    collector.track_voice_routing("en", "log_mood", 0.03)
    collector.track_session_establishment("en", 0.05)
    
    # Track complete workflow
    collector.track_complete_voice_processing(
        language="en",
        engine="whisper",
        stt_time=1.5,
        tts_time=0.8,
        routing_time=0.03,
        session_time=0.05,
        total_time=2.38
    )
    
    # Update engine availability
    collector.update_engine_availability("whisper", "en", True)
    collector.update_engine_availability("elevenlabs", "en", True)
    
    # Wait for metrics to be processed
    await asyncio.sleep(5)
    
    # Get performance summary
    summary = await collector.get_performance_summary()
    print("Voice Performance Summary:")
    print(json.dumps(summary, indent=2))
    
    # Shutdown
    await collector.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
