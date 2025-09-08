# Model Centralization Plan for MantraPath Backend

## Current State Analysis

### Services with Duplicate Model Dependencies:
1. **ai_event_processor**: emotion analysis models (transformers)
2. **translation_service**: IndicTrans2 models (transformers)  
3. **models_service**: Phi-3 via transformers (duplicate with phi3_agent)
4. **phi3_agent**: Uses Ollama for Phi-4 ✅ (correctly centralized)
5. **ml_service**: Full ML stack (scikit-learn, tensorflow)

### Issues Identified:
- Multiple services downloading same transformers models
- phi3_agent uses Ollama but models_service downloads Phi-3 separately
- Memory inefficiency with multiple PyTorch instances
- Inconsistent model serving approaches

## Centralization Strategy

### Phase 1: Consolidate Text Generation Models

**Problem**: Both `phi3_agent` and `models_service` serve text generation
**Solution**: Make models_service use Ollama as backend

#### 1.1 Update Models Service to Use Ollama
```python
# services/models_service/models/ollama_client.py
class OllamaClient:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        
    async def generate_text(self, prompt: str, model: str = "phi4"):
        # Use Ollama API instead of loading transformers
        
    async def translate_text(self, text: str, source: str, target: str):
        # Use phi4 for translation via Ollama
```

#### 1.2 Remove Duplicate Phi-3 Dependencies
- Remove transformers dependencies from models_service
- Keep phi3_agent as Ollama interface
- Route all text generation through Ollama

### Phase 2: Centralize NLP Models

**Problem**: ai_event_processor loads emotion models locally
**Solution**: Move emotion analysis to models_service

#### 2.1 Add Emotion Analysis to Models Service
```python
# services/models_service/api/emotion_routes.py
@router.post("/emotion/analyze")
async def analyze_emotion(request: EmotionRequest):
    # Centralized emotion analysis
    # Use Ollama for complex emotion analysis
    # Keep lightweight sentiment for fallback
```

#### 2.2 Update AI Event Processor
```python
# services/ai_event_processor/core/emotion_analyzer.py
class EmotionAnalyzer:
    def __init__(self):
        # Remove local transformers models
        # Use only models_service_client
        self.use_models_service = True  # Always true
```

### Phase 3: Centralize Translation Models

**Problem**: translation_service loads IndicTrans2 locally
**Solution**: Move to models_service or use Ollama

#### 3.1 Option A: Use Ollama for Translation
```python
# Add to models_service
async def translate_via_ollama(text, source_lang, target_lang):
    prompt = f"Translate from {source_lang} to {target_lang}: {text}"
    return await ollama_client.generate(prompt, model="phi4")
```

#### 3.2 Option B: Keep IndicTrans2 in Models Service
- Move IndicTrans2 models from translation_service to models_service
- translation_service becomes pure API layer
- Centralize all transformer-based translation

### Phase 4: Optimize ML Service

**Problem**: ml_service has complete ML stack for analytics
**Solution**: Keep separate but optimize

#### 4.1 ML Service Specialization
- Keep for: time series, analytics, recommendations
- Remove: text processing models (delegate to models_service)
- Optimize: use lighter sklearn models, lazy loading

## Implementation Plan

### Step 1: Update Docker Compose
```yaml
# docker-compose.yml changes
models-service:
  environment:
    - OLLAMA_BASE_URL=http://host.docker.internal:11434
    - USE_OLLAMA_FOR_TEXT_GENERATION=true
    - USE_OLLAMA_FOR_TRANSLATION=true
  extra_hosts:
    - "host.docker.internal:host-gateway"
```

### Step 2: Update Models Service
1. Add Ollama client integration
2. Remove local Phi-3 model loading
3. Add emotion analysis endpoints
4. Optimize memory usage

### Step 3: Update Client Services
1. Remove local transformers from ai_event_processor
2. Remove local IndicTrans2 from translation_service  
3. Update all clients to use models_service exclusively

### Step 4: Performance Optimization
1. Implement model caching in models_service
2. Add request batching for efficiency
3. Optimize Ollama model switching
4. Monitor memory usage across services

## Expected Benefits

### Memory Reduction
- Remove ~2-3GB duplicate model memory
- Single PyTorch instance in models_service
- Ollama handles model memory efficiently

### Performance Improvement
- Faster startup times (no model downloads)
- Better GPU utilization (if available)
- Consistent model serving latency

### Maintenance Benefits
- Single point for model updates
- Centralized model configuration
- Easier monitoring and debugging

## Risk Mitigation

### Fallback Strategy
- Keep minimal local models for critical services
- Graceful degradation when models_service unavailable
- Health checks and circuit breakers

### Monitoring
- Add model service health endpoints
- Monitor response times and error rates
- Track memory usage across services

## Migration Timeline

### Week 1: Models Service Ollama Integration
- Implement Ollama client in models_service
- Test text generation via Ollama
- Update health checks

### Week 2: AI Event Processor Migration
- Remove local transformers
- Test emotion analysis via models_service
- Performance testing

### Week 3: Translation Service Migration  
- Move IndicTrans2 to models_service OR implement Ollama translation
- Update translation workflows
- End-to-end testing

### Week 4: Optimization & Monitoring
- Performance tuning
- Add comprehensive monitoring
- Documentation updates

## Validation Criteria

### Performance Targets
- Response time < 500ms for text generation
- Response time < 200ms for emotion analysis
- Memory usage reduction > 40%
- Zero downtime during migration

### Quality Metrics
- Translation quality maintained (BLEU scores)
- Emotion analysis accuracy preserved
- All existing API contracts maintained
