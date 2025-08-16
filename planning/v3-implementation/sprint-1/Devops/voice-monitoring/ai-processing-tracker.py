#!/usr/bin/env python3
"""
AI Processing Tracker for MantraPath V3
Monitors AI processing performance including inference times, cultural context processing, and ML service metrics
"""

import time
import logging
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import statistics
from prometheus_client import Counter, Histogram, Gauge, Summary
import redis.asyncio as redis
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIProcessingMetrics:
    """AI processing performance metrics"""
    inference_time: float = 0.0
    context_injection_time: float = 0.0
    cultural_context_processing_time: float = 0.0
    emotion_analysis_time: float = 0.0
    intent_classification_time: float = 0.0
    model_name: str = "unknown"
    model_version: str = "unknown"
    input_size: int = 0
    output_size: int = 0
    success: bool = True
    error_type: Optional[str] = None
    confidence_score: Optional[float] = None
    language: str = "unknown"
    cultural_context: str = "unknown"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class AIProcessingTracker:
    """Tracks AI processing performance and cultural intelligence metrics"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.metrics_buffer: List[AIProcessingMetrics] = []
        self.buffer_size = 100
        self.flush_interval = 30  # seconds
        
        # Prometheus metrics
        self._setup_prometheus_metrics()
        
        # Performance thresholds
        self.thresholds = {
            "inference_time": 0.5,           # 500ms
            "context_injection": 0.02,       # 20ms
            "cultural_processing": 0.1,      # 100ms
            "emotion_analysis": 0.5,         # 500ms
            "intent_classification": 0.2,    # 200ms
            "total_processing": 1.0          # 1 second
        }
        
        # Start background tasks
        self.running = True
        asyncio.create_task(self._background_flush())
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for AI processing monitoring"""
        
        # AI inference duration histograms
        self.ai_inference_duration = Histogram(
            'ai_inference_duration_seconds',
            'AI model inference duration in seconds',
            ['model_name', 'model_version', 'language', 'status']
        )
        
        self.context_injection_duration = Histogram(
            'ai_context_injection_duration_seconds',
            'AI context injection duration in seconds',
            ['context_type', 'language', 'status']
        )
        
        self.cultural_context_duration = Histogram(
            'ai_cultural_context_duration_seconds',
            'Cultural context processing duration in seconds',
            ['cultural_context', 'language', 'status']
        )
        
        self.emotion_analysis_duration = Histogram(
            'ai_emotion_analysis_duration_seconds',
            'Emotion analysis processing duration in seconds',
            ['language', 'status']
        )
        
        self.intent_classification_duration = Histogram(
            'ai_intent_classification_duration_seconds',
            'Intent classification duration in seconds',
            ['language', 'intent_type', 'status']
        )
        
        # AI processing counters
        self.ai_processing_requests = Counter(
            'ai_processing_requests_total',
            'Total AI processing requests',
            ['model_name', 'language', 'status', 'error_type']
        )
        
        self.cultural_adaptations = Counter(
            'ai_cultural_adaptations_total',
            'Total cultural adaptations applied',
            ['cultural_context', 'language', 'adaptation_type']
        )
        
        # AI model performance metrics
        self.ai_model_accuracy = Summary(
            'ai_model_accuracy',
            'AI model accuracy scores',
            ['model_name', 'model_version', 'language']
        )
        
        self.ai_model_confidence = Summary(
            'ai_model_confidence',
            'AI model confidence scores',
            ['model_name', 'model_version', 'language']
        )
        
        # AI service health metrics
        self.ai_service_health = Gauge(
            'ai_service_health',
            'AI service health status',
            ['service_name', 'model_name']
        )
        
        self.ai_model_availability = Gauge(
            'ai_model_availability',
            'AI model availability status',
            ['model_name', 'language']
        )
        
        # AI resource utilization
        self.ai_gpu_utilization = Gauge(
            'ai_gpu_utilization_percentage',
            'AI GPU utilization percentage',
            ['model_name', 'device_id']
        )
        
        self.ai_memory_utilization = Gauge(
            'ai_memory_utilization_percentage',
            'AI memory utilization percentage',
            ['model_name']
        )
        
        self.ai_cpu_utilization = Gauge(
            'ai_cpu_utilization_percentage',
            'AI CPU utilization percentage',
            ['model_name']
        )
    
    async def connect_redis(self):
        """Connect to Redis for metrics storage"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("✅ Connected to Redis for AI metrics storage")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def track_ai_inference(self, model_name: str, model_version: str, language: str,
                          duration: float, input_size: int, output_size: int,
                          confidence: Optional[float] = None, success: bool = True,
                          error_type: Optional[str] = None):
        """Track AI model inference performance"""
        try:
            # Record Prometheus metrics
            status = "success" if success else "failure"
            self.ai_inference_duration.labels(
                model_name=model_name,
                model_version=model_version,
                language=language,
                status=status
            ).observe(duration)
            
            # Record request count
            self.ai_processing_requests.labels(
                model_name=model_name,
                language=language,
                status=status,
                error_type=error_type or "none"
            ).inc()
            
            # Record confidence score if available
            if confidence is not None:
                self.ai_model_confidence.labels(
                    model_name=model_name,
                    model_version=model_version,
                    language=language
                ).observe(confidence)
            
            # Check performance thresholds
            if duration > self.thresholds["inference_time"]:
                logger.warning(f"⚠️ AI inference exceeded threshold: {duration}s > {self.thresholds['inference_time']}s "
                             f"(Model: {model_name}, Language: {language})")
            
            # Store detailed metrics
            metrics = AIProcessingMetrics(
                inference_time=duration,
                model_name=model_name,
                model_version=model_version,
                input_size=input_size,
                output_size=output_size,
                language=language,
                success=success,
                error_type=error_type,
                confidence_score=confidence
            )
            
            self._add_to_buffer(metrics)
            
        except Exception as e:
            logger.error(f"❌ Error tracking AI inference: {e}")
    
    def track_context_injection(self, context_type: str, language: str, duration: float,
                               context_size: int, success: bool = True,
                               error_type: Optional[str] = None):
        """Track AI context injection performance"""
        try:
            # Record Prometheus metrics
            status = "success" if success else "failure"
            self.context_injection_duration.labels(
                context_type=context_type,
                language=language,
                status=status
            ).observe(duration)
            
            # Record request count
            self.ai_processing_requests.labels(
                model_name="context_injection",
                language=language,
                status=status,
                error_type=error_type or "none"
            ).inc()
            
            # Check performance thresholds
            if duration > self.thresholds["context_injection"]:
                logger.warning(f"⚠️ Context injection exceeded threshold: {duration}s > {self.thresholds['context_injection']}s "
                             f"(Type: {context_type}, Language: {language})")
            
            # Store detailed metrics
            metrics = AIProcessingMetrics(
                context_injection_time=duration,
                language=language,
                success=success,
                error_type=error_type
            )
            
            self._add_to_buffer(metrics)
            
        except Exception as e:
            logger.error(f"❌ Error tracking context injection: {e}")
    
    def track_cultural_context_processing(self, cultural_context: str, language: str,
                                        duration: float, adaptation_type: str,
                                        success: bool = True, error_type: Optional[str] = None):
        """Track cultural context processing performance"""
        try:
            # Record Prometheus metrics
            status = "success" if success else "failure"
            self.cultural_context_duration.labels(
                cultural_context=cultural_context,
                language=language,
                status=status
            ).observe(duration)
            
            # Record cultural adaptations
            if success:
                self.cultural_adaptations.labels(
                    cultural_context=cultural_context,
                    language=language,
                    adaptation_type=adaptation_type
                ).inc()
            
            # Record request count
            self.ai_processing_requests.labels(
                model_name="cultural_processing",
                language=language,
                status=status,
                error_type=error_type or "none"
            ).inc()
            
            # Check performance thresholds
            if duration > self.thresholds["cultural_processing"]:
                logger.warning(f"⚠️ Cultural processing exceeded threshold: {duration}s > {self.thresholds['cultural_processing']}s "
                             f"(Context: {cultural_context}, Language: {language})")
            
            # Store detailed metrics
            metrics = AIProcessingMetrics(
                cultural_context_processing_time=duration,
                language=language,
                cultural_context=cultural_context,
                success=success,
                error_type=error_type
            )
            
            self._add_to_buffer(metrics)
            
        except Exception as e:
            logger.error(f"❌ Error tracking cultural context processing: {e}")
    
    def track_emotion_analysis(self, language: str, duration: float,
                              emotion_detected: str, confidence: Optional[float] = None,
                              success: bool = True, error_type: Optional[str] = None):
        """Track emotion analysis performance"""
        try:
            # Record Prometheus metrics
            status = "success" if success else "failure"
            self.emotion_analysis_duration.labels(
                language=language,
                status=status
            ).observe(duration)
            
            # Record request count
            self.ai_processing_requests.labels(
                model_name="emotion_analysis",
                language=language,
                status=status,
                error_type=error_type or "none"
            ).inc()
            
            # Record confidence score if available
            if confidence is not None:
                self.ai_model_confidence.labels(
                    model_name="emotion_analysis",
                    model_version="latest",
                    language=language
                ).observe(confidence)
            
            # Check performance thresholds
            if duration > self.thresholds["emotion_analysis"]:
                logger.warning(f"⚠️ Emotion analysis exceeded threshold: {duration}s > {self.thresholds['emotion_analysis']}s "
                             f"(Language: {language}, Emotion: {emotion_detected})")
            
            # Store detailed metrics
            metrics = AIProcessingMetrics(
                emotion_analysis_time=duration,
                language=language,
                success=success,
                error_type=error_type,
                confidence_score=confidence
            )
            
            self._add_to_buffer(metrics)
            
        except Exception as e:
            logger.error(f"❌ Error tracking emotion analysis: {e}")
    
    def track_intent_classification(self, language: str, intent_type: str, duration: float,
                                  confidence: Optional[float] = None, success: bool = True,
                                  error_type: Optional[str] = None):
        """Track intent classification performance"""
        try:
            # Record Prometheus metrics
            status = "success" if success else "failure"
            self.intent_classification_duration.labels(
                language=language,
                intent_type=intent_type,
                status=status
            ).observe(duration)
            
            # Record request count
            self.ai_processing_requests.labels(
                model_name="intent_classification",
                language=language,
                status=status,
                error_type=error_type or "none"
            ).inc()
            
            # Record confidence score if available
            if confidence is not None:
                self.ai_model_confidence.labels(
                    model_name="intent_classification",
                    model_version="latest",
                    language=language
                ).observe(confidence)
            
            # Check performance thresholds
            if duration > self.thresholds["intent_classification"]:
                logger.warning(f"⚠️ Intent classification exceeded threshold: {duration}s > {self.thresholds['intent_classification']}s "
                             f"(Language: {language}, Intent: {intent_type})")
            
            # Store detailed metrics
            metrics = AIProcessingMetrics(
                intent_classification_time=duration,
                language=language,
                success=success,
                error_type=error_type,
                confidence_score=confidence
            )
            
            self._add_to_buffer(metrics)
            
        except Exception as e:
            logger.error(f"❌ Error tracking intent classification: {e}")
    
    def track_complete_ai_processing(self, model_name: str, model_version: str,
                                   language: str, cultural_context: str,
                                   inference_time: float, context_injection_time: float,
                                   cultural_processing_time: float, emotion_analysis_time: float,
                                   intent_classification_time: float, total_time: float,
                                   success: bool = True, error_type: Optional[str] = None):
        """Track complete AI processing workflow"""
        try:
            # Calculate total processing time
            calculated_total = (inference_time + context_injection_time + cultural_processing_time +
                              emotion_analysis_time + intent_classification_time)
            
            # Check performance thresholds
            if total_time > self.thresholds["total_processing"]:
                logger.warning(f"⚠️ Total AI processing exceeded threshold: {total_time}s > {self.thresholds['total_processing']}s "
                             f"(Model: {model_name}, Language: {language})")
            
            # Store comprehensive metrics
            metrics = AIProcessingMetrics(
                inference_time=inference_time,
                context_injection_time=context_injection_time,
                cultural_context_processing_time=cultural_processing_time,
                emotion_analysis_time=emotion_analysis_time,
                intent_classification_time=intent_classification_time,
                model_name=model_name,
                model_version=model_version,
                language=language,
                cultural_context=cultural_context,
                success=success,
                error_type=error_type
            )
            
            self._add_to_buffer(metrics)
            
        except Exception as e:
            logger.error(f"❌ Error tracking complete AI processing: {e}")
    
    def update_model_accuracy(self, model_name: str, model_version: str, language: str,
                             accuracy_score: float):
        """Update AI model accuracy metrics"""
        try:
            self.ai_model_accuracy.labels(
                model_name=model_name,
                model_version=model_version,
                language=language
            ).observe(accuracy_score)
            
            logger.debug(f"✅ Updated accuracy for {model_name} v{model_version} ({language}): {accuracy_score}")
            
        except Exception as e:
            logger.error(f"❌ Error updating model accuracy: {e}")
    
    def update_service_health(self, service_name: str, model_name: str, healthy: bool):
        """Update AI service health status"""
        try:
            status = 1 if healthy else 0
            self.ai_service_health.labels(
                service_name=service_name,
                model_name=model_name
            ).set(status)
            
            if not healthy:
                logger.warning(f"⚠️ AI service {service_name} for model {model_name} is unhealthy")
            else:
                logger.debug(f"✅ AI service {service_name} for model {model_name} is healthy")
                
        except Exception as e:
            logger.error(f"❌ Error updating service health: {e}")
    
    def update_model_availability(self, model_name: str, language: str, available: bool):
        """Update AI model availability status"""
        try:
            status = 1 if available else 0
            self.ai_model_availability.labels(
                model_name=model_name,
                language=language
            ).set(status)
            
            if not available:
                logger.warning(f"⚠️ AI model {model_name} for {language} is unavailable")
            else:
                logger.debug(f"✅ AI model {model_name} for {language} is available")
                
        except Exception as e:
            logger.error(f"❌ Error updating model availability: {e}")
    
    def update_resource_utilization(self, model_name: str, gpu_util: Optional[float] = None,
                                   memory_util: Optional[float] = None, cpu_util: Optional[float] = None,
                                   device_id: str = "default"):
        """Update AI resource utilization metrics"""
        try:
            if gpu_util is not None:
                self.ai_gpu_utilization.labels(
                    model_name=model_name,
                    device_id=device_id
                ).set(gpu_util)
            
            if memory_util is not None:
                self.ai_memory_utilization.labels(
                    model_name=model_name
                ).set(memory_util)
            
            if cpu_util is not None:
                self.ai_cpu_utilization.labels(
                    model_name=model_name
                ).set(cpu_util)
                
        except Exception as e:
            logger.error(f"❌ Error updating resource utilization: {e}")
    
    def _add_to_buffer(self, metrics: AIProcessingMetrics):
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
                    "inference_time": metric.inference_time,
                    "context_injection_time": metric.context_injection_time,
                    "cultural_context_processing_time": metric.cultural_context_processing_time,
                    "emotion_analysis_time": metric.emotion_analysis_time,
                    "intent_classification_time": metric.intent_classification_time,
                    "model_name": metric.model_name,
                    "model_version": metric.model_version,
                    "input_size": metric.input_size,
                    "output_size": metric.output_size,
                    "language": metric.language,
                    "cultural_context": metric.cultural_context,
                    "success": metric.success,
                    "error_type": metric.error_type,
                    "confidence_score": metric.confidence_score,
                    "timestamp": metric.timestamp.isoformat()
                }
                metrics_data.append(metric_dict)
            
            # Store in Redis with timestamp key
            timestamp = datetime.now(timezone.utc).isoformat()
            key = f"ai_metrics:{timestamp}"
            
            await self.redis_client.setex(
                key,
                3600,  # 1 hour TTL
                json.dumps(metrics_data)
            )
            
            # Clear buffer
            self.metrics_buffer.clear()
            
            logger.debug(f"✅ Flushed {len(metrics_data)} AI metrics to Redis")
            
        except Exception as e:
            logger.error(f"❌ Error flushing AI metrics: {e}")
    
    async def _background_flush(self):
        """Background task to flush metrics periodically"""
        while self.running:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_metrics()
            except Exception as e:
                logger.error(f"❌ Error in background flush: {e}")
    
    async def get_performance_summary(self, model_name: Optional[str] = None,
                                    language: Optional[str] = None,
                                    time_window: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """Get AI processing performance summary for the specified time window"""
        try:
            if not self.redis_client:
                return {"error": "Redis not connected"}
            
            # Get metrics from Redis
            metrics = await self._get_metrics_from_redis(time_window)
            
            if not metrics:
                return {"message": "No metrics available for the specified time window"}
            
            # Filter by model and language if specified
            if model_name:
                metrics = [m for m in metrics if m.get("model_name") == model_name]
            
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
            # Get all AI metrics keys
            pattern = "ai_metrics:*"
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
        inference_times = [m.get("inference_time", 0) for m in metrics if m.get("inference_time")]
        context_injection_times = [m.get("context_injection_time", 0) for m in metrics if m.get("context_injection_time")]
        cultural_processing_times = [m.get("cultural_context_processing_time", 0) for m in metrics if m.get("cultural_context_processing_time")]
        emotion_analysis_times = [m.get("emotion_analysis_time", 0) for m in metrics if m.get("emotion_analysis_time")]
        intent_classification_times = [m.get("intent_classification_time", 0) for m in metrics if m.get("intent_classification_time")]
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
        
        # Model distribution
        model_distribution = {}
        for metric in metrics:
            model = metric.get("model_name", "unknown")
            model_distribution[model] = model_distribution.get(model, 0) + 1
        
        # Language distribution
        language_distribution = {}
        for metric in metrics:
            lang = metric.get("language", "unknown")
            language_distribution[lang] = language_distribution.get(lang, 0) + 1
        
        # Cultural context distribution
        cultural_context_distribution = {}
        for metric in metrics:
            context = metric.get("cultural_context", "unknown")
            cultural_context_distribution[context] = cultural_context_distribution.get(context, 0) + 1
        
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
                "inference": safe_stats(inference_times),
                "context_injection": safe_stats(context_injection_times),
                "cultural_processing": safe_stats(cultural_processing_times),
                "emotion_analysis": safe_stats(emotion_analysis_times),
                "intent_classification": safe_stats(intent_classification_times)
            },
            "quality_metrics": {
                "confidence_scores": safe_stats(confidence_scores)
            },
            "distribution": {
                "models": model_distribution,
                "languages": language_distribution,
                "cultural_contexts": cultural_context_distribution,
                "errors": error_distribution
            },
            "thresholds": self.thresholds,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def shutdown(self):
        """Shutdown the tracker gracefully"""
        self.running = False
        await self._flush_metrics()
        
        if self.redis_client:
            await self.redis_client.close()

# Example usage and testing
async def main():
    """Example usage of AIProcessingTracker"""
    tracker = AIProcessingTracker()
    await tracker.connect_redis()
    
    # Simulate AI processing metrics
    tracker.track_ai_inference("gpt-4", "1.0", "en", 0.3, 100, 50, confidence=0.95)
    tracker.track_context_injection("user_profile", "en", 0.015, 200)
    tracker.track_cultural_context_processing("indian", "hi", 0.08, "greeting_style")
    tracker.track_emotion_analysis("en", 0.4, "joy", confidence=0.88)
    tracker.track_intent_classification("en", "log_mood", 0.15, confidence=0.92)
    
    # Track complete workflow
    tracker.track_complete_ai_processing(
        model_name="gpt-4",
        model_version="1.0",
        language="en",
        cultural_context="indian",
        inference_time=0.3,
        context_injection_time=0.015,
        cultural_processing_time=0.08,
        emotion_analysis_time=0.4,
        intent_classification_time=0.15,
        total_time=0.945
    )
    
    # Update model metrics
    tracker.update_model_accuracy("gpt-4", "1.0", "en", 0.94)
    tracker.update_service_health("ml_service", "gpt-4", True)
    tracker.update_model_availability("gpt-4", "en", True)
    tracker.update_resource_utilization("gpt-4", gpu_util=45.2, memory_util=67.8, cpu_util=23.1)
    
    # Wait for metrics to be processed
    await asyncio.sleep(5)
    
    # Get performance summary
    summary = await tracker.get_performance_summary()
    print("AI Processing Performance Summary:")
    print(json.dumps(summary, indent=2))
    
    # Shutdown
    await tracker.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
