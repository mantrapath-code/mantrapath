# Quick Reference: Text Generation Service

## Model Information

**Current Model**: TinyLlama-1.1B-Chat-v1.0  
**Size**: 1.1B parameters (~1.1GB in FP16)  
**Context**: 2048 tokens  
**Recommended Upgrade**: Phi-4-mini-instruct (3.8B params, 64K context)

## Performance at a Glance

| Deployment | Response Time | Memory | Use Case |
|-----------|---------------|---------|----------|
| CPU Only | 24-30s | 2.2GB | Background tasks ✅ Current |
| GPU (Basic) | 2-5s | 1.1GB | Real-time chat 🎯 Recommended |
| GPU + Pipeline | 1.5-4s | 1.1GB | High throughput 🚀 Optimal |

## Quick Start

### Test the Service
```bash
# Health check
curl http://localhost:8081/api/v1/nlp/health

# Generate text
curl -X POST http://localhost:8081/api/v1/nlp/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?", "max_tokens": 100}'
```

### Enable GPU (Production)

1. **Edit docker-compose.yml**:
```yaml
models_service:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  environment:
    - USE_GPU=true
    - TORCH_DEVICE=cuda
```

2. **Restart service**:
```bash
docker-compose up -d models_service
```

### Enable Response Caching (Production)

Already enabled by default with in-memory cache.

For Redis (recommended):
```yaml
environment:
  - REDIS_URL=redis://redis:6379/4
  - TEXT_GEN_CACHE_TTL=3600
```

## API Endpoints

### Generate Text
```bash
POST /api/v1/nlp/generate
{
  "prompt": "Your prompt here",
  "max_tokens": 256,
  "temperature": 0.7,
  "use_cache": true,      # Enable caching
  "use_pipeline": false   # Enable for 20-30% speedup
}
```

### Check Health
```bash
GET /api/v1/nlp/health
# Returns: model info, device, GPU status, performance metrics
```

### Cache Management
```bash
# Get cache statistics
GET /api/v1/nlp/cache_stats

# Clear all caches
POST /api/v1/nlp/clear_cache
```

## Upgrade to Phi-4

For better quality responses:

1. Update `text_generation_routes.py` line 103:
```python
model_name = "microsoft/Phi-4-mini-instruct"
```

2. Increase memory in docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      memory: 12G
```

3. Restart service

**Note**: Requires GPU for acceptable performance (3-8s vs 90-120s on CPU)

## Environment Variables

```bash
# Text Generation Settings
ENABLE_TEXT_GENERATION=true
TEXT_GEN_USE_PIPELINE=false      # Enable for speedup
TEXT_GEN_CACHE_ENABLED=true      # Enable caching
TEXT_GEN_CACHE_TTL=3600          # Cache TTL in seconds

# Hardware Settings
USE_GPU=false                     # Enable for 10x speedup
TORCH_DEVICE=cpu                  # 'cuda' or 'auto' for GPU
MAX_GPU_MEMORY=0.8               # GPU memory limit (80%)

# Redis Cache (Optional)
REDIS_URL=redis://localhost:6379/4
```

## Troubleshooting

### Slow Response Times
- ✅ **Current**: 24-30s on CPU is normal
- 🎯 **Solution**: Enable GPU for 2-5s responses
- 🚀 **Optimize**: Use pipeline mode for additional speedup

### Out of Memory
- **CPU**: Increase Docker memory limit to 4GB+
- **GPU**: Reduce `MAX_GPU_MEMORY` or use smaller model
- **Solution**: Current TinyLlama is optimized for low memory

### Cache Not Working
- Check Redis connection: `curl http://localhost:8081/api/v1/nlp/cache_stats`
- Falls back to in-memory automatically
- Verify `use_cache: true` in requests

### GPU Not Detected
```bash
# Verify GPU access in container
docker exec models_service python -c "import torch; print(torch.cuda.is_available())"

# Check NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## Performance Tuning

### For Real-Time Chat
```python
{
  "max_tokens": 256,        # Limit response length
  "temperature": 0.7,       # Balanced creativity
  "use_cache": true,        # Cache common queries
  "use_pipeline": true      # Enable for speedup
}
```

### For Complex Reasoning
```python
{
  "max_tokens": 512,        # Allow detailed responses
  "temperature": 0.3,       # More deterministic
  "use_cache": false,       # Fresh responses
  "system_prompt": "You are an expert..."
}
```

## Monitoring

Key metrics to track:
- Response time (target: <5s with GPU)
- Cache hit rate (target: >40%)
- GPU utilization (target: 60-80%)
- Memory usage (should be stable)

```bash
# Monitor cache effectiveness
watch -n 5 'curl -s http://localhost:8081/api/v1/nlp/cache_stats'

# Monitor GPU usage
watch -n 1 nvidia-smi
```

## Resources

- Full Documentation: `backend/services/models_service/README.md`
- Production Guide: `PRODUCTION_READINESS_UPDATES.md`
- Docker Compose: `backend/docker-compose.yml`
- Source Code: `backend/services/models_service/api/text_generation_routes.py`
