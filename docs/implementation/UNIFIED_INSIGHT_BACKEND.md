# Unified Insights Backend Implementation (E2)

## Overview
Server-side aggregation endpoint that replaces client-side parallel API calls in `unifiedInsightService.ts`. Provides caching, structured logging, and extensible architecture for future insight sources.

## Architecture

### Components
- **Aggregator** (`unified_insights_aggregator.py`): Core logic for data collection and response building
- **Cache** (`unified_insights_cache.py`): In-memory TTL cache (120s) with future Redis support
- **Endpoint** (`/api/v1/insights/unified`): FastAPI endpoint with feature flag gating
- **Feature Flags** (`shared/feature_flags.py`): Environment-driven configuration

### Data Flow
```
Frontend → GET /api/v1/insights/unified → Aggregator → Cache Check → DB Queries → Response
```

## Current Implementation (MVP)

### Data Sources
- ✅ **Mood Statistics**: Average, variability, best day, energy peak, streak calculation
- 🔄 **ML Insights**: Placeholder (future integration)
- 🔄 **Correlations**: Placeholder (future integration)  
- 🔄 **Community Metrics**: Placeholder (future integration)

### Response Contract
```json
{
  "dashboard": {
    "weeklySummary": { "currentWeekScore": 68, "trend": "stable", "daysTracked": 8, "achievements": [] },
    "currentStatus": { "moodScore": 68, "energyLevel": 0, "stressLevel": 0, "lastUpdated": "..." },
    "topHighlights": { "bestDay": "Friday", "energyPeak": "14:00", "dominantMood": "good", "moodStreak": 3 }
  },
  "detailedAnalysis": { "patterns": {...}, "correlations": {...}, "predictions": {...} },
  "recommendedActions": [],
  "progressTracking": { "goals": [], "trends": {...}, "comparisons": {...}, "successPatterns": [] },
  "metadata": {
    "lastUpdated": "2025-08-13T...",
    "dataQuality": 45,
    "confidenceScore": 0.4,
    "insightCount": 0,
    "sourceDistribution": { "personalized": 0, "patterns": 0, "weather": 0, "ml": 0, "community": 0 },
    "cache": "hit|miss"
  }
}
```

## Configuration

### Environment Variables
```bash
# Enable server-side unified insights
USE_SERVER_UNIFIED_INSIGHTS=true

# Future: Redis caching
REDIS_URL=redis://localhost:6379
```

### Feature Flag Usage
```python
from shared.feature_flags import feature_enabled

if feature_enabled('USE_SERVER_UNIFIED_INSIGHTS'):
    # Endpoint is available
```

## Logging & Observability

### Structured Events
```json
{
  "event": "unified_insights_cache",
  "status": "hit|miss", 
  "user_id": "...",
  "latency_ms": 123,
  "subcall_count": 2,
  "data_quality": 45,
  "confidence_score": 0.4
}
```

### Metrics
- Cache hit ratio
- Response latency (P95 target: <300ms warm, <600ms cold)
- Data quality distribution
- Subcall count (optimization target)

## Caching Strategy

### Cache Key Format
```
unified:{user_id}:v1
```

### TTL & Invalidation
- **Default TTL**: 120 seconds
- **Invalidation**: Force refresh flag, future event triggers
- **Storage**: In-memory (production: Redis)

### Performance Characteristics
- **Cache Hit**: ~5-15ms response time
- **Cache Miss**: ~50-200ms (depending on data volume)
- **Memory Usage**: ~2KB per cached entry

## Testing

### Unit Tests
```bash
cd backend/services/ml_service
python -m pytest tests/test_unified_insights_aggregator.py -v
```

### Integration Testing
```bash
# Start ML service first
cd backend/services/ml_service
USE_SERVER_UNIFIED_INSIGHTS=true python main.py

# Run endpoint tests
./scripts/test_unified_insights.sh
```

### Test Coverage
- ✅ Empty data handling
- ✅ Mood aggregation accuracy
- ✅ Cache hit/miss behavior
- ✅ Data quality scoring
- ✅ Response contract validation
- ✅ Mood streak calculation

## Frontend Integration

### Client Adaptation (Future)
```typescript
// In unifiedInsightService.ts
async getComprehensiveInsights(useCache = true): Promise<ComprehensiveInsights> {
  try {
    // Try server endpoint first
    const response = await apiService.request('/api/v1/insights/unified')
    return response // Server contract matches frontend expectations
  } catch (error) {
    if (error.status === 404) {
      // Fallback to client-side aggregation
      return this.getComprehensiveInsightsLegacy(useCache)
    }
    throw error
  }
}
```

## Future Enhancements (E3-E6)

### Data Source Expansion
- **E3**: Achievement calculations, community engagement metrics
- **E4**: Real-time delta updates via WebSocket
- **E5**: Language detection, translation stubs, sentiment per language  
- **E6**: Redis caching, query optimization, leaderboard materialization

### Performance Improvements
- Selective eager loading for complex queries
- Background pre-computation for heavy calculations
- Circuit breaker for external service calls
- Response compression for large datasets

### Observability Expansion
- Prometheus metrics endpoint
- Correlation ID tracing
- Error rate monitoring per data source
- Performance regression detection

## Migration Strategy

### Rollout Plan
1. **Phase 1**: Feature flag enabled for internal testing
2. **Phase 2**: A/B test 10% of users (compare performance)
3. **Phase 3**: Gradual rollout based on cache hit ratios
4. **Phase 4**: Remove client-side aggregation fallback

### Risk Mitigation
- Feature flag allows instant rollback
- Client fallback maintains functionality
- Extensive logging for debugging
- Cache warming during low-traffic periods

## API Documentation

### Endpoint: `GET /api/v1/insights/unified`

#### Headers
- `Authorization: Bearer <token>` (required)
- `X-Insight-Version: v1` (optional, for future versioning)

#### Query Parameters
- `force_refresh: boolean` (optional, default: false)

#### Response Codes
- `200`: Success
- `401`: Unauthorized  
- `404`: Feature disabled (USE_SERVER_UNIFIED_INSIGHTS=false)
- `500`: Server error

#### Rate Limiting
- Current: None
- Future (E7): 60 requests/minute per user

---

**Implementation Date**: August 13, 2025  
**Next Review**: After E3 achievement integration  
**Status**: ✅ MVP Complete, Ready for Testing
