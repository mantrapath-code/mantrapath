# API Gateway V3 Enhanced - AI Context Guide

## Overview

The AI Context system in MantraPath API Gateway V3 Enhanced provides intelligent context injection and propagation across all microservices, enabling personalized, context-aware user experiences throughout the platform.

## AI Context Architecture

### Context Types

#### 1. User Context
```json
{
  "user_context": {
    "user_id": "user123",
    "profile": {
      "meditation_experience": "intermediate",
      "preferred_practices": ["mindfulness", "breathing"],
      "goals": ["stress_reduction", "better_sleep"],
      "schedule_preferences": {
        "preferred_time": "morning",
        "session_duration": 15,
        "frequency": "daily"
      }
    },
    "behavioral_patterns": {
      "session_completion_rate": 0.85,
      "preferred_content_types": ["guided", "nature_sounds"],
      "engagement_level": "high",
      "streak_days": 12
    },
    "emotional_state": {
      "current_mood": "stressed",
      "mood_trend": "improving",
      "stress_level": 6,
      "energy_level": 4
    }
  }
}
```

#### 2. Session Context
```json
{
  "session_context": {
    "session_id": "session456",
    "start_time": "2025-08-15T06:00:00Z",
    "platform": "mobile_app",
    "location": {
      "timezone": "Asia/Kolkata",
      "country": "IN",
      "region": "indian_subcontinent"
    },
    "conversation_history": [
      {
        "timestamp": "2025-08-15T06:01:00Z",
        "intent": "mood_tracking",
        "response": "successful",
        "sentiment": "positive"
      }
    ],
    "interaction_mode": "voice",
    "language": "hi"
  }
}
```

#### 3. AI Insights Context
```json
{
  "ai_insights": {
    "predictions": {
      "recommended_actions": [
        {
          "action": "breathing_exercise",
          "confidence": 0.92,
          "reasoning": "User shows stress indicators and benefits from breathing practices"
        },
        {
          "action": "guided_meditation",
          "confidence": 0.87,
          "reasoning": "Morning session aligns with user schedule preferences"
        }
      ],
      "mood_forecast": {
        "predicted_mood": "calm",
        "confidence": 0.78,
        "timeframe": "30_minutes"
      }
    },
    "personalization": {
      "adaptation_factors": [
        "cultural_background",
        "experience_level",
        "current_stress_state"
      ],
      "customization_score": 0.89
    },
    "content_recommendations": [
      {
        "content_id": "breathing_101_hindi",
        "relevance_score": 0.94,
        "reasoning": "Matches language, experience level, and current need"
      }
    ]
  }
}
```

#### 4. Cultural Context
```json
{
  "cultural_context": {
    "region": "indian_subcontinent",
    "language": "hi",
    "cultural_preferences": {
      "greeting_style": "namaste",
      "family_orientation": true,
      "spiritual_terminology": "traditional",
      "meditation_style": "vedic_tradition"
    },
    "adaptations": {
      "content_style": "respectful_traditional",
      "communication_tone": "warm_respectful",
      "practice_integration": ["yoga", "pranayama"],
      "festivals_awareness": ["diwali", "holi"],
      "seasonal_practices": true
    }
  }
}
```

## Context Injection Middleware

### Implementation

```python
class AIContextMiddleware:
    """Middleware for AI context injection"""
    
    async def __call__(self, request: Request, call_next):
        # Retrieve user context
        user_context = await self.get_user_context(request)
        
        # Generate AI insights
        ai_insights = await self.generate_ai_insights(user_context)
        
        # Inject context into request headers
        request.headers.update({
            "X-AI-Context": self.serialize_context(ai_insights),
            "X-User-Context": self.serialize_context(user_context)
        })
        
        response = await call_next(request)
        
        # Enhance response with AI insights
        enhanced_response = await self.enhance_response(response, ai_insights)
        
        return enhanced_response
```

### Context Retrieval Flow

1. **Request Analysis**
   - Extract user ID from authentication
   - Analyze request intent and parameters
   - Determine context requirements

2. **Context Assembly**
   - Fetch user profile and preferences
   - Retrieve session history
   - Generate AI predictions
   - Apply cultural adaptations

3. **Context Injection**
   - Serialize context to headers
   - Maintain context hierarchy
   - Handle context versioning

4. **Service Propagation**
   - Forward context to target services
   - Ensure context consistency
   - Track context usage

## AI Context Manager Service

### Core Functions

```python
class AIContextManager:
    """Manages AI context generation and caching"""
    
    async def get_context(
        self, 
        user_context: Optional[Dict],
        request_context: Optional[Dict] = None
    ) -> AIContext:
        """Get comprehensive AI context"""
        
        # Check cache first
        cache_key = self.generate_cache_key(user_context, request_context)
        cached_context = await self.cache.get(cache_key)
        
        if cached_context and not self.is_context_stale(cached_context):
            return cached_context
        
        # Generate fresh context
        context = await self.generate_context(user_context, request_context)
        
        # Cache the context
        await self.cache.set(cache_key, context, ttl=self.context_ttl)
        
        return context
    
    async def generate_context(
        self, 
        user_context: Dict,
        request_context: Dict
    ) -> AIContext:
        """Generate AI context using ML services"""
        
        # Analyze user patterns
        behavioral_insights = await self.analyze_user_behavior(user_context)
        
        # Generate predictions
        predictions = await self.generate_predictions(user_context, behavioral_insights)
        
        # Create recommendations
        recommendations = await self.create_recommendations(
            user_context, 
            predictions, 
            request_context
        )
        
        return AIContext(
            user_insights=behavioral_insights,
            predictions=predictions,
            recommendations=recommendations,
            confidence_score=self.calculate_confidence(predictions),
            generation_timestamp=time.time()
        )
```

### Context Caching Strategy

```python
class ContextCache:
    """Intelligent caching for AI context"""
    
    def __init__(self):
        self.cache_layers = {
            "user_profile": {"ttl": 3600, "size": 10000},  # 1 hour
            "session_context": {"ttl": 1800, "size": 50000},  # 30 minutes
            "ai_insights": {"ttl": 300, "size": 100000},  # 5 minutes
            "predictions": {"ttl": 600, "size": 20000}  # 10 minutes
        }
    
    async def get_layered_context(self, user_id: str) -> Dict:
        """Get context from multiple cache layers"""
        context = {}
        
        # Layer 1: User profile (long-term)
        profile = await self.get_cached("user_profile", user_id)
        if profile:
            context.update(profile)
        
        # Layer 2: Session context (medium-term)
        session = await self.get_cached("session_context", user_id)
        if session:
            context.update(session)
        
        # Layer 3: AI insights (short-term)
        insights = await self.get_cached("ai_insights", user_id)
        if insights:
            context.update(insights)
        
        return context
```

## Context Propagation

### Header-Based Propagation

```python
def propagate_context_headers(request: Request, ai_context: AIContext) -> Dict[str, str]:
    """Create headers for context propagation"""
    
    headers = {
        "X-AI-Context-Version": "v3.0",
        "X-AI-Context-Timestamp": str(ai_context.generation_timestamp),
        "X-AI-Context-Confidence": str(ai_context.confidence_score),
        "X-AI-Context-User-ID": ai_context.user_id,
    }
    
    # Compress and encode context data
    context_data = {
        "insights": ai_context.user_insights,
        "predictions": ai_context.predictions[:5],  # Top 5 predictions
        "recommendations": ai_context.recommendations[:3]  # Top 3 recommendations
    }
    
    compressed_context = compress_and_encode(context_data)
    headers["X-AI-Context-Data"] = compressed_context
    
    return headers
```

### Service-Specific Context Filtering

```python
def filter_context_for_service(context: AIContext, service_name: str) -> AIContext:
    """Filter context based on service requirements"""
    
    service_filters = {
        "mood_service": ["emotional_state", "mood_predictions", "stress_insights"],
        "content_service": ["preferences", "recommendations", "behavioral_patterns"],
        "chatbot_service": ["conversation_history", "personality_insights", "context_awareness"],
        "community_service": ["social_preferences", "engagement_patterns", "cultural_context"]
    }
    
    relevant_fields = service_filters.get(service_name, [])
    
    filtered_context = AIContext()
    for field in relevant_fields:
        if hasattr(context, field):
            setattr(filtered_context, field, getattr(context, field))
    
    return filtered_context
```

## Machine Learning Integration

### ML Service Communication

```python
class MLServiceIntegrator:
    """Integrates with ML service for AI insights"""
    
    def __init__(self, ml_service_url: str):
        self.ml_service_url = ml_service_url
        self.client = httpx.AsyncClient()
    
    async def get_user_insights(self, user_data: Dict) -> Dict:
        """Get AI insights from ML service"""
        
        response = await self.client.post(
            f"{self.ml_service_url}/insights/user",
            json={
                "user_id": user_data["user_id"],
                "profile": user_data["profile"],
                "behavioral_data": user_data["behavioral_patterns"],
                "context_type": "comprehensive"
            }
        )
        
        return response.json()
    
    async def generate_predictions(self, context: Dict) -> List[Dict]:
        """Generate predictions using ML models"""
        
        response = await self.client.post(
            f"{self.ml_service_url}/predictions/generate",
            json={
                "context": context,
                "prediction_types": [
                    "mood_forecast",
                    "engagement_prediction",
                    "content_preference",
                    "optimal_timing"
                ],
                "time_horizon": "1_hour"
            }
        )
        
        return response.json()["predictions"]
    
    async def get_recommendations(self, user_context: Dict, predictions: List[Dict]) -> List[Dict]:
        """Get personalized recommendations"""
        
        response = await self.client.post(
            f"{self.ml_service_url}/recommendations/generate",
            json={
                "user_context": user_context,
                "predictions": predictions,
                "recommendation_types": [
                    "content",
                    "practice",
                    "timing",
                    "social"
                ],
                "max_recommendations": 5
            }
        )
        
        return response.json()["recommendations"]
```

### Real-time Model Updates

```python
class ModelUpdateManager:
    """Manages real-time ML model updates"""
    
    async def update_user_model(self, user_id: str, interaction_data: Dict):
        """Update user-specific model with new interaction data"""
        
        await self.client.post(
            f"{self.ml_service_url}/models/user/{user_id}/update",
            json={
                "interaction_data": interaction_data,
                "timestamp": time.time(),
                "update_type": "incremental"
            }
        )
    
    async def batch_model_updates(self, updates: List[Dict]):
        """Batch update multiple user models"""
        
        await self.client.post(
            f"{self.ml_service_url}/models/batch_update",
            json={
                "updates": updates,
                "batch_id": str(uuid.uuid4()),
                "timestamp": time.time()
            }
        )
```

## Performance Optimization

### Context Generation Performance

```python
class ContextPerformanceOptimizer:
    """Optimizes AI context generation performance"""
    
    def __init__(self):
        self.generation_cache = {}
        self.precompute_queue = asyncio.Queue()
        self.background_tasks = set()
    
    async def precompute_contexts(self):
        """Precompute contexts for active users"""
        
        while True:
            try:
                user_id = await self.precompute_queue.get()
                
                # Generate context in background
                context = await self.generate_context_background(user_id)
                
                # Cache precomputed context
                await self.cache_precomputed_context(user_id, context)
                
            except Exception as e:
                logger.exception("Context precomputation failed", user_id=user_id, error=str(e))
    
    async def schedule_precomputation(self, user_id: str):
        """Schedule context precomputation for user"""
        
        if not self.precompute_queue.full():
            await self.precompute_queue.put(user_id)
```

### Context Compression

```python
def compress_context(context: Dict) -> str:
    """Compress context for efficient transmission"""
    
    import gzip
    import base64
    import json
    
    # Serialize to JSON
    json_data = json.dumps(context, separators=(',', ':'))
    
    # Compress with gzip
    compressed = gzip.compress(json_data.encode('utf-8'))
    
    # Encode as base64
    encoded = base64.b64encode(compressed).decode('ascii')
    
    return encoded

def decompress_context(compressed_context: str) -> Dict:
    """Decompress context data"""
    
    import gzip
    import base64
    import json
    
    # Decode from base64
    compressed = base64.b64decode(compressed_context.encode('ascii'))
    
    # Decompress with gzip
    json_data = gzip.decompress(compressed).decode('utf-8')
    
    # Parse JSON
    context = json.loads(json_data)
    
    return context
```

## Monitoring and Analytics

### Context Usage Metrics

```python
class ContextMetricsCollector:
    """Collects metrics on AI context usage"""
    
    def __init__(self):
        self.metrics = {
            "context_generations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_generation_time": 0.0,
            "prediction_accuracy": 0.0,
            "recommendation_relevance": 0.0
        }
    
    async def record_context_generation(self, generation_time: float, cache_hit: bool):
        """Record context generation metrics"""
        
        self.metrics["context_generations"] += 1
        
        if cache_hit:
            self.metrics["cache_hits"] += 1
        else:
            self.metrics["cache_misses"] += 1
        
        # Update average generation time
        alpha = 0.1  # Exponential moving average factor
        self.metrics["avg_generation_time"] = (
            alpha * generation_time + 
            (1 - alpha) * self.metrics["avg_generation_time"]
        )
    
    async def record_prediction_feedback(self, prediction_id: str, accuracy: float):
        """Record prediction accuracy feedback"""
        
        # Update prediction accuracy using exponential moving average
        alpha = 0.1
        self.metrics["prediction_accuracy"] = (
            alpha * accuracy + 
            (1 - alpha) * self.metrics["prediction_accuracy"]
        )
```

### Health Monitoring

```python
async def health_check_ai_context() -> Dict[str, Any]:
    """Health check for AI context system"""
    
    try:
        # Test context generation
        test_context = await generate_test_context()
        generation_successful = test_context is not None
        
        # Test ML service connectivity
        ml_service_healthy = await check_ml_service_health()
        
        # Check cache performance
        cache_performance = await check_cache_performance()
        
        # Overall health assessment
        healthy = (
            generation_successful and
            ml_service_healthy and
            cache_performance["hit_rate"] > 0.8
        )
        
        return {
            "status": "healthy" if healthy else "degraded",
            "context_generation": "ok" if generation_successful else "error",
            "ml_service": "ok" if ml_service_healthy else "error",
            "cache_performance": cache_performance,
            "metrics": context_metrics_collector.get_metrics(),
            "timestamp": time.time()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }
```

## Configuration

### AI Context Configuration

```yaml
# config/ai_context_config.yaml
ai_context:
  enabled: true
  cache_ttl: 300  # 5 minutes
  max_cache_size: 10000
  generation_timeout: 2000  # 2 seconds
  
ml_service:
  url: "http://ml-service:8006"
  timeout: 5000
  retry_attempts: 3
  
context_types:
  user_profile:
    cache_ttl: 3600
    required_fields: ["user_id", "preferences"]
    
  predictions:
    cache_ttl: 600
    max_predictions: 5
    confidence_threshold: 0.7
    
  recommendations:
    cache_ttl: 300
    max_recommendations: 3
    relevance_threshold: 0.8

compression:
  enabled: true
  algorithm: "gzip"
  min_size: 1024  # Only compress if larger than 1KB

monitoring:
  metrics_collection: true
  performance_tracking: true
  prediction_feedback: true
```

This comprehensive guide covers all aspects of the AI Context system in the MantraPath API Gateway V3 Enhanced, providing the foundation for intelligent, personalized user experiences across the platform.
