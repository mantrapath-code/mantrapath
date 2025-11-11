# MantraPath Models Service 🤖

## Overview

The **MantraPath Models Service** is a centralized AI model management and inference platform that serves as the backbone for all machine learning capabilities across the MantraPath wellness ecosystem. It provides unified access to Speech-to-Text (STT), Text-to-Speech (TTS), Natural Language Processing (NLP), and AI model management functionalities through a scalable REST API.

### Key Capabilities

- 🎤 **Speech-to-Text Processing** - Multi-engine STT with AI4Bharat IndicWav2Vec, Whisper, and Vosk
- 🔊 **Text-to-Speech Synthesis** - High-quality TTS with AI4Bharat Indic-TTS, Meta MMS-TTS, and lightweight alternatives
- 🧠 **Natural Language Processing** - Embeddings via TEI, translation, and text analysis with Phi-4
- 📦 **Dynamic Model Management** - Automated model downloading, caching, and lifecycle management
- 🌍 **Multi-Language Support** - Specialized Indian language models with international language fallbacks
- ⚡ **Performance Optimization** - GPU acceleration, model caching, and intelligent load balancing
- 🔄 **Service Integration** - Seamless integration with all MantraPath platform services

## Models Used and Their Purposes

### 1. Speech-to-Text (STT) Models

#### AI4Bharat IndicWav2Vec Models (Primary) 🎯
**Purpose**: High-quality speech recognition specifically optimized for Indian languages
**Architecture**: Wav2Vec2-based Connectionist Temporal Classification (CTC)
**Why Chosen**: Provides superior accuracy for Indian languages compared to generic multilingual models

**Supported Models**:
- `ai4bharat/indicwav2vec_v1_hindi` - Hindi speech recognition
- `ai4bharat/indicwav2vec_v1_bengali` - Bengali speech recognition  
- `ai4bharat/indicwav2vec_v1_gujarati` - Gujarati speech recognition
- `ai4bharat/indicwav2vec_v1_kannada` - Kannada speech recognition
- `ai4bharat/indicwav2vec_v1_malayalam` - Malayalam speech recognition
- `ai4bharat/indicwav2vec_v1_marathi` - Marathi speech recognition
- `ai4bharat/indicwav2vec_v1_odia` - Odia speech recognition
- `ai4bharat/indicwav2vec_v1_punjabi` - Punjabi speech recognition
- `ai4bharat/indicwav2vec_v1_tamil` - Tamil speech recognition
- `ai4bharat/indicwav2vec_v1_telugu` - Telugu speech recognition
- `ai4bharat/indicwav2vec_v1_urdu` - Urdu speech recognition
- `ai4bharat/indicwav2vec_v1_assamese` - Assamese speech recognition

#### OpenAI Whisper (Emergency Fallback) ⚠️
**Model**: `openai/whisper-small`
**Purpose**: Fallback speech recognition for unsupported languages or system failures
**Why Used**: Broad language support when IndicWav2Vec models are unavailable
**Status**: Disabled by default to ensure consistent quality, enabled via `ENABLE_WHISPER_FALLBACK=true`

#### Vosk (Lightweight Alternative) 🪶
**Purpose**: Resource-efficient speech recognition for minimal deployments
**Why Used**: Smaller memory footprint for constrained environments
**Use Case**: Basic STT functionality when full models are too resource-intensive

### 2. Text-to-Speech (TTS) Models

#### AI4Bharat Indic-TTS Models (Primary) 🗣️
**Purpose**: Natural, high-quality speech synthesis for Indian languages
**Why Chosen**: Specialized pronunciation and intonation patterns for authentic Indian language speech

**Supported Models**:
- `ai4bharat/indictts_v1_hi` - Hindi text-to-speech
- `ai4bharat/indictts_v1_bn` - Bengali text-to-speech
- `ai4bharat/indictts_v1_gu` - Gujarati text-to-speech
- `ai4bharat/indictts_v1_kn` - Kannada text-to-speech
- `ai4bharat/indictts_v1_ml` - Malayalam text-to-speech
- `ai4bharat/indictts_v1_mr` - Marathi text-to-speech
- `ai4bharat/indictts_v1_or` - Odia text-to-speech
- `ai4bharat/indictts_v1_pa` - Punjabi text-to-speech
- `ai4bharat/indictts_v1_ta` - Tamil text-to-speech
- `ai4bharat/indictts_v1_te` - Telugu text-to-speech
- `ai4bharat/indictts_v1_ur` - Urdu text-to-speech
- `ai4bharat/indictts_v1_as` - Assamese text-to-speech

#### Meta MMS-TTS (Universal Fallback) 🌐
**Purpose**: Multilingual text-to-speech using VITS architecture
**Why Used**: Comprehensive language coverage when Indic-TTS models are unavailable

**Language Mappings**:
- `facebook/mms-tts-hin` - Hindi
- `facebook/mms-tts-ben` - Bengali
- `facebook/mms-tts-tel` - Telugu
- `facebook/mms-tts-tam` - Tamil
- `facebook/mms-tts-mar` - Marathi
- `facebook/mms-tts-guj` - Gujarati
- `facebook/mms-tts-kan` - Kannada
- `facebook/mms-tts-mal` - Malayalam
- `facebook/mms-tts-ori` - Odia
- `facebook/mms-tts-pan` - Punjabi
- `facebook/mms-tts-asm` - Assamese
- `facebook/mms-tts-eng` - English

#### AI4Bharat Indic Parler-TTS (Advanced) 🎭
**Model**: `ai4bharat/indic-parler-tts`
**Purpose**: Advanced multilingual TTS with controllable voice characteristics
**Why Used**: Supports style control and multiple speaking characteristics for enhanced user experience

#### Lightweight TTS Options (Minimal Mode) 📱
- **pyttsx3**: System-level TTS for basic functionality
- **gTTS (Google Text-to-Speech)**: Cloud-based TTS for English
**Purpose**: Minimal resource footprint for constrained deployments

### 3. Natural Language Processing (NLP) Models

#### Text Embeddings Inference (TEI) 🔍
**Default Model**: `google/embeddinggemma-300m`
**Purpose**: Generate semantic text embeddings for similarity search and NLP tasks
**Why Used**: High-quality embeddings for content understanding, semantic search, and downstream NLP applications
**Integration**: External TEI server provides scalable embedding generation

#### TinyLlama (Current - Text Generation) 💬
**Model**: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
**Purpose**: Lightweight text generation for chatbot responses and content creation
**Parameters**: 1.1B
**Context Window**: 2048 tokens
**Why Chosen**:
- Extremely lightweight (~1.1GB in FP16) for resource-constrained deployments
- Fast inference on CPU (24-30s) and GPU (2-5s)
- Good chat capabilities for basic conversational AI
- Direct HuggingFace integration (no external dependencies)
- Low memory footprint enables co-deployment with other models

**Current Status**: ✅ **In Production** - Serving chatbot and text generation requests

**Performance**:
- CPU: 24-30s per request (acceptable for background processing)
- GPU (CUDA): 2-5s per request (recommended for real-time chat)
- Memory: ~1.1GB (FP16) / ~2.2GB (FP32)

#### Microsoft Phi-4 (Recommended Upgrade - Advanced NLP) 🧠
**Model**: `microsoft/Phi-4-mini-instruct` (Primary) / `microsoft/Phi-4-mini-flash-reasoning` (Advanced)
**Purpose**: Advanced multilingual text generation, reasoning, translation, and instruction-following
**Parameters**: 3.8B (3.4x larger than TinyLlama)
**Context Window**: 64K tokens (32x larger than TinyLlama)
**Supported Languages**: 25+ languages including all major Indian languages

**Why Upgrade to Phi-4**:
- **Significantly better quality** over TinyLlama for complex tasks
- **64K context window** vs 2K context (32x improvement)
- **Superior reasoning capabilities** for mathematical and logical tasks
- **Advanced multilingual performance** including Indian languages
- **Better instruction-following** for complex NLP tasks
- **Improved translation quality** between Indian languages and English
- **10x better throughput** for long-context generation compared to Phi-3
- **State-of-art small model performance** with excellent efficiency

**Upgrade Path**:
```python
# CURRENT (Production)
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # 1.1B params, 2K context
memory_requirement = "~1.1GB (FP16)"
inference_time_gpu = "2-5s"

# RECOMMENDED UPGRADE (Better Quality)
model_name = "microsoft/Phi-4-mini-instruct"  # 3.8B params, 64K context
memory_requirement = "~7.6GB (FP16)"
inference_time_gpu = "3-8s"  # Slightly slower but much better quality

# FOR ADVANCED REASONING
model_name = "microsoft/Phi-4-mini-flash-reasoning"  # Advanced reasoning capabilities
```

**Trade-offs**:
- **TinyLlama**: Lower memory (1.1GB), faster (2-5s GPU), good for basic chat
- **Phi-4**: Higher memory (7.6GB), slightly slower (3-8s GPU), excellent for complex reasoning and multilingual tasks

**Recommendation**: Deploy Phi-4 on GPU-enabled production infrastructure for superior quality, keep TinyLlama as lightweight fallback

### 4. Legacy/Compatibility Models

#### Facebook Wav2Vec2 (Legacy STT) 🏛️
**Purpose**: Backward compatibility for existing integrations
**Status**: Superseded by IndicWav2Vec but maintained for compatibility

**Legacy Models**:
- `facebook/wav2vec2-large-xlsr-53-hindi`
- `facebook/wav2vec2-large-xlsr-53-bengali`
- `facebook/wav2vec2-large-xlsr-53-telugu`
- `facebook/wav2vec2-large-xlsr-53-tamil`

## Model Selection Strategy 🎯

### 1. **Indian Languages Priority**
- **STT**: AI4Bharat IndicWav2Vec models (primary) → Meta MMS (fallback)
- **TTS**: AI4Bharat Indic-TTS (primary) → Meta MMS-TTS (fallback)
- **Rationale**: Models trained specifically for Indian languages provide superior accuracy and naturalness

### 2. **English/International Languages**
- **STT**: Whisper (when enabled) or universal models
- **TTS**: Meta MMS models for broad language coverage
- **NLP**: Phi-4 for advanced multilingual processing (upgrade from Phi-3 required)

### 3. **Fallback Hierarchy**
1. Specialized Indian language models (AI4Bharat)
2. Universal multilingual models (Meta MMS)
3. Lightweight alternatives (Vosk, pyttsx3, gTTS)
4. Emergency fallbacks (Whisper when enabled)

### 4. **Deployment Modes**

#### Enhanced Voice Stack Mode (`VOICE_STACK_MODE=enhanced`)
- **Purpose**: Maximum quality for production voice applications
- **Behavior**: Preloads Indian language models for immediate availability
- **Use Case**: Production deployments prioritizing voice quality

#### Minimal Mode (`MODELS_SERVICE_MODE=minimal`)
- **Purpose**: Resource conservation
- **Behavior**: On-demand model loading, lightweight alternatives
- **Use Case**: Development environments or resource-constrained deployments

#### Standard Mode (Default)
- **Purpose**: Balanced performance and resource usage
- **Behavior**: Intelligent caching with fallback strategies
- **Use Case**: General production deployments

## � **Production Deployment Guide**

### GPU Configuration for Optimal Performance

#### Current Performance Benchmarks

**TinyLlama-1.1B-Chat-v1.0**:
| Hardware | Inference Time | Memory Usage | Use Case |
|----------|---------------|--------------|----------|
| CPU (Intel Xeon) | 24-30s | ~2.2GB (FP32) | Background processing, async tasks |
| GPU (CUDA, FP16) | 2-5s | ~1.1GB | Real-time chat, interactive responses |
| GPU (Pipeline) | 1.5-4s | ~1.1GB | Batch processing, high throughput |

**Phi-4-mini-instruct** (Recommended Upgrade):
| Hardware | Inference Time | Memory Usage | Use Case |
|----------|---------------|--------------|----------|
| CPU (Intel Xeon) | 90-120s | ~7.6GB (FP32) | Not recommended |
| GPU (CUDA, FP16) | 3-8s | ~3.8GB | Production chat, complex reasoning |
| GPU (Pipeline) | 2-6s | ~3.8GB | Batch operations, multi-turn conversations |

#### GPU Deployment (Docker Compose)

**1. Enable GPU in docker-compose.yml**:
```yaml
models_service:
  deploy:
    resources:
      limits:
        memory: 8G
      reservations:
        memory: 4G
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  environment:
    - USE_GPU=true
    - TORCH_DEVICE=cuda  # or 'auto' for automatic detection
    - MAX_GPU_MEMORY=0.8  # Use 80% of available GPU memory
```

**2. GPU Prerequisites**:
```bash
# Install NVIDIA Docker Runtime
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

**3. Deploy with GPU**:
```bash
# Start services with GPU support
docker-compose up -d models_service

# Verify GPU is being used
docker exec models_service python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Check model health
curl http://localhost:8081/api/v1/nlp/health
```

#### Response Caching for Production

**Current Implementation**: In-memory caching (suitable for single-instance deployments)

**Production Recommendation**: Redis-based distributed caching

**Benefits**:
- Shared cache across multiple service instances
- Persistent cache across restarts
- TTL-based expiration for stale responses
- Significantly reduced response times for common queries

**Implementation Steps**:

1. **Add Redis dependency** (already available in stack):
```python
# In text_generation_routes.py, replace in-memory cache with Redis:
import redis.asyncio as redis

redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/4"),
    encoding="utf-8",
    decode_responses=True
)
```

2. **Update caching logic**:
```python
# Cache lookup
cache_key = f"textgen:{_get_cache_key(request)}"
cached = await redis_client.get(cache_key)
if cached:
    return TextGenerationResponse(**json.loads(cached))

# Cache storage (with 1-hour TTL)
await redis_client.setex(
    cache_key,
    3600,  # 1 hour TTL
    json.dumps(response_data)
)
```

3. **Environment configuration**:
```yaml
environment:
  - REDIS_URL=redis://redis:6379/4
  - TEXT_GEN_CACHE_TTL=3600  # 1 hour
  - TEXT_GEN_CACHE_ENABLED=true
```

#### Model Upgrade Strategy: TinyLlama → Phi-4

**When to Upgrade**:
- ✅ Need better response quality for complex questions
- ✅ Require advanced reasoning capabilities
- ✅ Working with longer context (>2K tokens)
- ✅ Need better multilingual performance
- ✅ GPU infrastructure is available

**Upgrade Steps**:

1. **Update model name** in `text_generation_routes.py`:
```python
# Change from:
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# To:
model_name = "microsoft/Phi-4-mini-instruct"
```

2. **Adjust memory limits** in docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      memory: 12G  # Increased for Phi-4
    reservations:
      memory: 8G
```

3. **Update environment variables**:
```yaml
environment:
  - USE_GPU=true  # Strongly recommended for Phi-4
  - MAX_GPU_MEMORY=0.8
```

4. **Test and validate**:
```bash
# Check health
curl http://localhost:8081/api/v1/nlp/health

# Test generation
curl -X POST http://localhost:8081/api/v1/nlp/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing", "max_tokens": 200}'
```

#### Performance Optimization Checklist

**For Real-Time Chat (High Priority)**:
- [x] Enable GPU acceleration (`USE_GPU=true`)
- [x] Use FP16 precision (automatic with GPU)
- [x] Enable pipeline mode (`use_pipeline=true`)
- [ ] Implement Redis caching
- [ ] Consider Phi-4 upgrade for better quality

**For Background Processing (Lower Priority)**:
- [x] Current CPU performance acceptable (24-30s)
- [x] Enable response caching
- [ ] Batch requests when possible
- [ ] Use pipeline mode for multiple requests

**Infrastructure Recommendations**:
- **Minimum**: 4GB RAM, 2 vCPU (CPU-only, TinyLlama)
- **Recommended**: 8GB RAM, 4 vCPU, NVIDIA GPU with 4GB+ VRAM (TinyLlama)
- **Optimal**: 16GB RAM, 8 vCPU, NVIDIA GPU with 8GB+ VRAM (Phi-4)

## �🚨 **Critical Architecture Issues & Recommendations**

### **Issue 1: Outdated Phi-3 Usage**
**Problem**: Currently using `microsoft/Phi-3-mini-4k-instruct` when Phi-4 offers significant improvements:
- **64K context** vs 4K context (16x improvement)
- **10x better throughput** for long sequences
- **Superior reasoning capabilities** for mathematical and logical tasks
- **Better multilingual performance**

**Recommendation**: 
```python
# CURRENT (Deprecated)
self.model_name = "microsoft/Phi-3-mini-4k-instruct"

# RECOMMENDED (Upgrade Required)
self.model_name = "microsoft/Phi-4-mini-instruct"  # General use
# OR
self.model_name = "microsoft/Phi-4-mini-flash-reasoning"  # Advanced reasoning
```

### **Issue 2: Duplicate Service Architecture**
**Problem**: Two services handling similar NLP tasks:
- `models_service` (Port 8080) - Has `phi3_engine.py` using Phi-3
# phi3_agent service removed - Phi-4 functionality integrated into models_service

**Current Architecture Problems**:
```
models_service:8080 ──► phi3_engine.py ──► Phi-3 (Direct HuggingFace)
                    │
                    └──► ollama_integration.py ──► phi3:mini (Ollama)

# phi3_agent:8016 removed - now: models_service:8081 ──► Phi-4 (Direct Transformers)
```

**Recommended Solution**:
1. **✅ COMPLETED: Consolidated to Models Service**: Removed separate `phi3_agent` service
2. **Upgrade to Phi-4**: Update `phi3_engine.py` to use Phi-4 models
3. **Dual Integration**: Support both direct HuggingFace and Ollama backends

### **Issue 3: Inconsistent Model References**
**Problem**: Code contains mixed references:
- `emotion_routes.py` mentions "Phi-4" but uses `ollama_client.analyze_emotion_via_phi4()` (not implemented)
- `text_generation_routes.py` defaults to `model: Optional[str] = "phi4"`
- `translation_routes.py` uses `engine: str = "phi3"`

**Fix Required**: Update all references to use consistent Phi-4 models

### **Recommended Migration Plan**

#### **Phase 1: Immediate Updates (Week 1)**
1. **Update Model References**:
   ```python
   # models/phi3_engine.py → models/phi4_engine.py
   self.model_name = "microsoft/Phi-4-mini-instruct"
   ```

2. **Fix API Routes**:
   ```python
   # Update all default model references
   model: Optional[str] = "phi4-mini-instruct"
   ```

#### **Phase 2: Service Consolidation (Week 2)**
1. **Merge Phi3_Agent functionality** into Models Service
2. **Remove duplicate service** to reduce complexity
3. **Update service discovery** and routing

#### **Phase 3: Performance Optimization (Week 3)**
1. **Implement Phi-4 Flash Reasoning** for advanced tasks
2. **Add context window optimization** (64K vs 4K)
3. **Performance benchmarking** and comparison

## Quality Assurance Strategy 🔒

### Model Quality Hierarchy
1. **Tier 1**: AI4Bharat specialized models (highest quality for Indian languages)
2. **Tier 2**: Meta MMS universal models (consistent quality across languages)  
3. **Tier 3**: Microsoft Phi-4 models (advanced reasoning and multilingual NLP)
4. **Tier 4**: Legacy/lightweight models (basic functionality)

### Strict Model Enforcement
- **Default Behavior**: Only high-quality models are used
- **Fallback Prevention**: Whisper fallback disabled by default to prevent quality degradation
- **Language Validation**: Unsupported languages return explicit errors rather than silent fallbacks
- **Version Control**: Automatic deprecation warnings for outdated models (Phi-3)

### Performance Monitoring
- Model usage statistics tracking
- Quality metrics collection
- Automatic model health checks
- Resource utilization monitoring
- **Context window utilization** tracking for Phi-4

## Technical Specifications 📋

### Model Sizes and Requirements

#### STT Models (AI4Bharat IndicWav2Vec)
- **Model Size**: ~1.2GB per language model
- **Memory Requirements**: 2-4GB RAM per loaded model
- **Processing**: 16kHz mono audio input required
- **Architecture**: Wav2Vec2 with CTC head
- **Languages**: 12 Indian languages supported

#### TTS Models 
**AI4Bharat Indic-TTS**:
- **Model Size**: ~500MB - 1GB per language
- **Memory Requirements**: 1-2GB RAM per loaded model
- **Output**: 22kHz/44kHz audio synthesis
- **Architecture**: Neural vocoder-based synthesis

**Meta MMS-TTS**:
- **Model Size**: ~400-800MB per language
- **Memory Requirements**: 1-1.5GB RAM per loaded model
- **Output**: 16kHz audio synthesis
- **Architecture**: VITS (Variational Inference Text-to-Speech)

#### NLP Models
**Microsoft Phi-4**:
- **Model Size**: ~7.5GB (64K context, mini variant)
- **Memory Requirements**: 8-16GB RAM (CPU) / 8GB VRAM (GPU)
- **Context Window**: 65,536 tokens (16x larger than Phi-3)
- **Parameters**: ~3.8 billion
- **Performance**: 10x better throughput for long sequences
- **Architecture**: Hybrid decoder with state space models

**Embedding Gemma-300M**:
- **Model Size**: ~600MB
- **Memory Requirements**: 1-2GB RAM
- **Embedding Dimension**: 768
- **Max Sequence Length**: 512 tokens

### Hardware Recommendations

#### Minimum Requirements
- **CPU**: 4 cores, 2.5GHz
- **RAM**: 8GB
- **Storage**: 50GB for basic model set
- **Network**: 1Gbps for model downloading

#### Recommended (Production)
- **CPU**: 8+ cores, 3.0GHz (Intel Xeon/AMD EPYC)
- **RAM**: 32GB+
- **GPU**: NVIDIA GPU with 8GB+ VRAM (optional but recommended)
- **Storage**: 200GB+ SSD for model caching
- **Network**: 10Gbps for rapid model deployment

#### Optimal (High-Load Production)
- **CPU**: 16+ cores, 3.5GHz
- **RAM**: 64GB+
- **GPU**: NVIDIA A100/V100 or equivalent (40GB+ VRAM)
- **Storage**: 500GB+ NVMe SSD
- **Network**: 25Gbps+ for model synchronization

### Performance Characteristics

#### Latency Benchmarks (Typical)
- **STT (IndicWav2Vec)**: 0.5-2.0x real-time processing
- **TTS (Indic-TTS)**: 0.3-1.0x real-time synthesis
- **TTS (MMS)**: 0.2-0.8x real-time synthesis
- **Embeddings (TEI)**: 10-50ms per request
- **Phi-4 Generation**: 15-40 tokens/second (CPU), 80-150 tokens/second (GPU)
- **Phi-4 Long Context**: Up to 10x faster for sequences >2K tokens

#### Throughput Capacity
- **Concurrent STT Streams**: 5-20 (depending on hardware)
- **Concurrent TTS Requests**: 10-30 (depending on model)
- **Embedding Requests/sec**: 100-500 (with TEI)
- **NLP Generation Requests**: 5-15 concurrent (GPU recommended)

## Configuration Options ⚙️

### Environment Variables

#### Core Service Configuration
```bash
# Service mode
MODELS_SERVICE_MODE=minimal|standard|enhanced
VOICE_STACK_MODE=enhanced  # Preload voice models

# Model selection
MODELS_PRELOAD_LIST=hi,bn,te,ta  # Comma-separated language codes
MODELS_PRELOAD_BACKGROUND=true   # Preload models in background
MODELS_SERVICE_SKIP_DEFAULTS=false  # Skip default model loading

# Emergency fallbacks
ENABLE_WHISPER_FALLBACK=false  # Enable Whisper fallback (not recommended)
```

#### External Service Integration
```bash
# TEI Embeddings Server
TEI_BASE_URL=http://ext-embeddings-inference:80
TEI_MODEL_ID=google/embeddinggemma-300m
TEI_TIMEOUT_SECONDS=15

# Ollama Integration (Optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini
OLLAMA_TIMEOUT_SECONDS=30
```

#### Hardware Optimization
```bash
# GPU Configuration
CUDA_VISIBLE_DEVICES=0,1  # GPU selection
TORCH_DEVICE=auto|cpu|cuda

# Memory Management
MAX_GPU_MEMORY=0.8  # Use 80% of GPU memory
MODEL_CACHE_SIZE=5  # Number of models to keep in memory
MAX_CONCURRENT_REQUESTS=10
```

### Language Configuration

#### Supported Language Codes
```python
# Indian Languages (Primary Support)
INDIAN_LANGUAGES = {
    "hi": "Hindi",      "bn": "Bengali",    "te": "Telugu",
    "ta": "Tamil",      "mr": "Marathi",    "gu": "Gujarati", 
    "kn": "Kannada",    "ml": "Malayalam",  "pa": "Punjabi",
    "or": "Odia",       "as": "Assamese",   "ur": "Urdu"
}

# International Languages (Fallback Support)
INTERNATIONAL_LANGUAGES = {
    "en": "English",    "es": "Spanish",    "fr": "French",
    "de": "German",     "zh": "Chinese",    "ja": "Japanese",
    "ko": "Korean",     "ru": "Russian",    "ar": "Arabic"
}
```

## Service Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Platform Services                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Voice     │  │  Chatbot    │  │    Translation          │ │
│  │  Service    │  │  Service    │  │     Service             │ │
│  │ (Port 8011) │  │ (Port 8004) │  │   (Port 8005)          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Media     │  │   ML        │  │    Community            │ │
│  │  Service    │  │  Service    │  │     Service             │ │
│  │ (Port 8021) │  │ (Port 8008) │  │   (Port 8006)          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ Model Requests
┌─────────────────────────────────────────────────────────────────┐
│                Models Service (Port 8080)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │    STT      │  │    TTS      │  │       NLP               │ │
│  │   Engine    │  │   Engine    │  │     Engine              │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Model     │  │ Embeddings  │  │    Phi-3 AI             │ │
│  │  Manager    │  │Integration  │  │     Engine              │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI Model Repository                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │AI4Bharat    │  │AI4Bharat    │  │   Google Embedding      │ │
│  │IndicWav2Vec │  │ Indic-TTS   │  │    Gemma-300M          │ │
│  │(STT Models) │  │(TTS Models) │  │   (via TEI)            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Meta      │  │  Microsoft  │  │      Whisper            │ │
│  │  MMS-TTS    │  │   Phi-3     │  │   (Emergency            │ │
│  │  (Fallback) │  │  (4K-Mini)  │  │    Fallback)           │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
models_service/
├── main.py                           # FastAPI application entry point (254 lines)
├── requirements.txt                  # Python dependencies (47 lines)
├── Dockerfile                        # Container configuration (Port 8080)
├── start_simple.sh                   # Simple startup script
├── embeddings_integration.py         # TEI embeddings client integration
├── ollama_integration.py             # Ollama model integration
├── __init__.py                       # Package initialization
├── api/                             # API endpoint modules
│   ├── __init__.py
│   ├── routes.py                    # Core STT/TTS/NLP API routes (390 lines)
│   ├── translation_routes.py        # Translation service endpoints
│   ├── text_generation_routes.py    # Text generation via Ollama
│   └── emotion_routes.py            # Emotion analysis endpoints
├── models/                          # AI model engines
│   ├── __init__.py
│   ├── model_manager.py             # Central model management (462 lines)
│   ├── stt_engine.py                # Speech-to-Text engine (454 lines)
│   ├── tts_engine.py                # Text-to-Speech engine (506 lines)
│   ├── nlp_engine.py                # NLP processing engine (103 lines)
│   └── phi3_engine.py               # Phi-3 AI model integration
├── config/                          # Configuration management
│   ├── __init__.py
│   └── settings.py                  # Service configuration (344 lines)
├── utils/                           # Utility modules
│   ├── __init__.py
│   └── logger.py                    # Structured logging configuration
├── tests/                           # Test suites
│   ├── __init__.py
│   ├── conftest.py                  # Test configuration
│   ├── test_main.py                 # Main application tests
│   ├── test_model_manager.py        # Model manager tests
│   ├── test_stt_engine.py           # STT engine tests
│   ├── test_tts_engine.py           # TTS engine tests
│   ├── test_nlp_engine.py           # NLP engine tests
│   ├── test_api_routes.py           # API endpoint tests
│   ├── test_config.py               # Configuration tests
│   └── test_utils.py                # Utility tests
└── logs/                           # Application logs
    └── (runtime log files)
```

## API Endpoints

### Health & Status Monitoring

#### GET `/health`
**Basic Health Check**
```json
Response:
{
  "status": "healthy",
  "timestamp": "2025-09-27T14:30:00Z",
  "service": "models_service",
  "version": "1.0.0"
}
```

#### GET `/status`
**Detailed Service Status**
```json
Response:
{
  "service": "models_service",
  "timestamp": "2025-09-27T14:30:00Z",
  "status": "running",
  "hardware": {
    "cpu_count": 8,
    "memory_gb": 32.0,
    "gpu_available": true,
    "gpu_count": 1,
    "gpu_memory_gb": [24.0]
  },
  "models": {
    "stt_loaded": 3,
    "tts_loaded": 2,
    "nlp_loaded": 1
  },
  "supported_languages": {
    "stt": ["en", "hi", "bn", "te", "ta", "mr", "es", "fr", "de"],
    "tts": ["en", "hi", "bn", "te", "ta", "mr", "es", "fr", "de", "zh", "ja"]
  }
}
```

### Model Management

#### GET `/models/available`
**List All Available Models**
```json
Response:
{
  "stt_models": [
    {
      "name": "whisper_medium",
      "type": "stt",
      "languages": ["multilingual"],
      "quality": "high",
      "size": "769MB",
      "device": ["cpu", "cuda"]
    },
    {
      "name": "vosk_en_us",
      "type": "stt", 
      "languages": ["en"],
      "quality": "good",
      "size": "50MB",
      "device": ["cpu"]
    }
  ],
  "tts_models": [
    {
      "name": "coqui_xtts_v2",
      "type": "tts",
      "languages": ["multilingual"],
      "quality": "high",
      "size": "2.3GB",
      "device": ["cpu", "cuda"]
    }
  ],
  "nlp_models": [
    {
      "name": "sentence_transformers",
      "type": "embeddings",
      "languages": ["multilingual"],
      "quality": "high",
      "size": "438MB",
      "device": ["cpu", "cuda"]
    }
  ]
}
```

#### GET `/models/loaded`
**List Currently Loaded Models**
```json
Response:
{
  "stt": ["whisper_medium", "vosk_en_us", "vosk_hi"],
  "tts": ["coqui_xtts_v2", "espeak_en"],
  "nlp": ["sentence_transformers", "tei_embeddings"]
}
```

### Speech-to-Text (STT) Endpoints

#### POST `/api/v1/stt/transcribe`
**Transcribe Audio to Text**
```json
Request:
Content-Type: multipart/form-data
audio: (audio file - WAV, MP3, FLAC, M4A)
language: "auto" | "en" | "hi" | "bn" | etc.
model_preference: "whisper_medium" (optional)

Response:
{
  "success": true,
  "text": "Hello, how are you feeling today?",
  "language_detected": "en",
  "confidence": 0.94,
  "model_used": "whisper_medium",
  "processing_time_ms": 1250
}
```

#### GET `/api/v1/stt/languages`
**Get Supported STT Languages**
```json
Response:
{
  "supported_languages": {
    "en": {
      "name": "English",
      "models": ["whisper_medium", "vosk_en_us", "wav2vec2_en"],
      "quality_levels": ["high", "medium", "fast"]
    },
    "hi": {
      "name": "हिंदी (Hindi)",
      "models": ["whisper_medium", "vosk_hi", "wav2vec2_hi"],
      "quality_levels": ["high", "medium", "fast"]
    },
    "bn": {
      "name": "বাংলা (Bengali)",
      "models": ["whisper_medium", "wav2vec2_bn"],
      "quality_levels": ["high", "medium"]
    }
  }
}
```

### Text-to-Speech (TTS) Endpoints

#### POST `/api/v1/tts/synthesize`
**Synthesize Speech from Text**
```json
Request:
{
  "text": "Welcome to MantraPath wellness platform",
  "language": "en",
  "voice": "default",
  "model_preference": "coqui_xtts_v2"
}

Response:
{
  "success": true,
  "audio_url": "/api/v1/tts/audio/session_123_audio.wav",
  "duration": 3.2,
  "sample_rate": 22050,
  "model_used": "coqui_xtts_v2",
  "processing_time_ms": 2100
}
```

#### GET `/api/v1/tts/languages`
**Get Supported TTS Languages**
```json
Response:
{
  "supported_languages": {
    "en": {
      "name": "English",
      "voices": ["default", "male", "female"],
      "models": ["coqui_xtts_v2", "espeak_en", "festival_en"],
      "quality_levels": ["high", "medium", "fast"]
    },
    "hi": {
      "name": "हिंदी (Hindi)",
      "voices": ["default", "male", "female"],
      "models": ["coqui_xtts_v2", "coqui_hi", "espeak_hi"],
      "quality_levels": ["high", "medium", "fast"]
    }
  }
}
```

#### GET `/api/v1/tts/voices/{language}`
**Get Available Voices for Language**
```json
Response:
{
  "language": "en",
  "voices": [
    {
      "id": "default",
      "name": "Default English",
      "gender": "neutral",
      "model": "coqui_xtts_v2",
      "quality": "high"
    },
    {
      "id": "male_formal",
      "name": "Formal Male",
      "gender": "male", 
      "model": "coqui_xtts_v2",
      "quality": "high"
    }
  ]
}
```

### Natural Language Processing (NLP) Endpoints

#### POST `/api/v1/nlp/embeddings`
**Generate Text Embeddings**
```json
Request:
{
  "texts": [
    "I am feeling peaceful after meditation",
    "Today was a challenging day at work"
  ],
  "model": "sentence_transformers"
}

Response:
{
  "success": true,
  "embeddings": [
    [0.1234, -0.5678, 0.9012, ...],  // 384-dimensional vector
    [0.2345, -0.6789, 0.8901, ...]
  ],
  "model_used": "sentence_transformers",
  "dimensions": 384,
  "processing_time_ms": 156
}
```

#### POST `/api/v1/nlp/similarity`
**Calculate Text Similarity**
```json
Request:
{
  "text1": "I feel happy and energetic",
  "text2": "I am joyful and full of energy",
  "model": "sentence_transformers"
}

Response:
{
  "success": true,
  "similarity_score": 0.87,
  "model_used": "sentence_transformers",
  "processing_time_ms": 89
}
```

### Translation Endpoints

#### POST `/api/v1/translation/translate`
**Translate Text Between Languages**
```json
Request:
{
  "text": "I am feeling better today",
  "source_lang": "en",
  "target_lang": "hi",
  "model_preference": "nllb_200"
}

Response:
{
  "success": true,
  "translated_text": "मुझे आज बेहतर महसूस हो रहा है",
  "source_lang": "en",
  "target_lang": "hi",
  "confidence": 0.91,
  "model_used": "nllb_200",
  "processing_time_ms": 234
}
```

#### POST `/api/v1/translation/detect-language`
**Detect Language of Text**
```json
Request:
{
  "text": "मैं खुश हूं"
}

Response:
{
  "success": true,
  "detected_language": "hi",
  "confidence": 0.98,
  "language_name": "Hindi",
  "supported_by_translation": true
}
```

### Text Generation Endpoints (TinyLlama)

#### Current Implementation: TinyLlama-1.1B-Chat-v1.0 🚀

**Model**: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
**Purpose**: Lightweight, efficient text generation for chatbot responses and content generation
**Architecture**: 1.1B parameter transformer model optimized for chat interactions

**Performance Characteristics**:
- **CPU Inference**: 24-30 seconds per request (acceptable for background processing)
- **GPU Inference**: 2-5 seconds per request (recommended for real-time chat)
- **Memory**: ~2.2GB (FP32) or ~1.1GB (FP16 with GPU)
- **Context Length**: 2048 tokens

**Features**:
- ✅ Direct HuggingFace Transformers integration (no external services)
- ✅ GPU acceleration support (CUDA)
- ✅ Response caching for common queries (in-memory)
- ✅ Pipeline mode for faster real-time inference
- ✅ Chat template support for conversational AI
- ✅ Low memory footprint for resource-constrained deployments

**Production Recommendations**:
- 🎯 **GPU Deployment**: Use CUDA-enabled infrastructure for <5s response times
- 🎯 **Response Caching**: Enable Redis caching for frequently asked questions
- 🎯 **Model Upgrade Path**: Consider Phi-4 for improved quality (3.8B parameters, better reasoning)
- 🎯 **Pipeline Mode**: Use `use_pipeline=true` for 20-30% speedup in batch scenarios

#### POST `/api/v1/nlp/generate`
**Generate Text Using TinyLlama**
```json
Request:
{
  "prompt": "Write a short meditation guide for beginners",
  "message": "Optional: alternative to prompt for chat-style input",
  "model": "tinyllama",
  "max_tokens": 256,
  "temperature": 0.7,
  "system_prompt": "You are a helpful meditation guide",
  "use_cache": true,
  "use_pipeline": false
}

Response:
{
  "generated_text": "Here's a simple meditation guide for beginners:\n\n1. Find a quiet, comfortable space...",
  "response": "Here's a simple meditation guide for beginners...",
  "model_used": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
  "tokens_generated": 156,
  "processing_time_ms": 4200,
  "success": true,
  "confidence": 0.85
}
```

**Request Parameters**:
- `prompt` (required): Main text prompt for generation
- `message` (optional): Alternative to prompt for chat-style interactions
- `max_tokens` (default: 256): Maximum tokens to generate
- `temperature` (default: 0.7): Sampling temperature (0.0-1.0)
- `model` (default: "tinyllama"): Model identifier
- `system_prompt` (optional): System-level instructions for the model
- `use_cache` (default: true): Enable response caching
- `use_pipeline` (default: false): Use pipeline for faster inference

#### GET `/api/v1/nlp/health`
**Check Text Generation Service Health**
```json
Response:
{
  "model_available": true,
  "model_name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
  "status": "healthy",
  "device": "cuda:0",
  "dtype": "torch.float16",
  "gpu_available": true,
  "pipeline_available": true,
  "cache_enabled": true,
  "test_inference_ms": 145.32,
  "production_notes": {
    "current_performance": "24-30s CPU, 2-5s GPU",
    "recommended_upgrade": "Phi-4 for better quality",
    "caching": "In-memory (Redis recommended for production)"
  }
}
```

#### POST `/api/v1/nlp/clear_cache`
**Clear Response Cache**
```json
Response:
{
  "success": true,
  "cleared_entries": 42,
  "message": "Response cache cleared successfully"
}
```

### Legacy Text Generation Endpoints (Ollama Integration - Deprecated)

**Note**: The following Ollama-based endpoints are maintained for backward compatibility but are deprecated in favor of the direct TinyLlama integration above.

#### POST `/api/v1/nlp/generate` (Legacy)
**Generate Text Using AI Models via Ollama**
```json
Request:
{
  "prompt": "Write a short meditation guide for beginners",
  "model": "phi3:mini",
  "max_tokens": 200,
  "temperature": 0.7
}

Response:
{
  "success": true,
  "generated_text": "Here's a simple meditation guide for beginners:\n\n1. Find a quiet, comfortable space...",
  "model_used": "phi3:mini",
  "tokens_used": 156,
  "processing_time_ms": 3400
}
```

#### POST `/api/v1/nlp/chat`
**Interactive Chat with AI Models**
```json
Request:
{
  "message": "How can I manage stress better?",
  "conversation_id": "conv_123",
  "model": "phi3:mini",
  "context": {
    "user_mood": "stressed",
    "previous_conversations": 3
  }
}

Response:
{
  "success": true,
  "response": "Here are some effective stress management techniques...",
  "conversation_id": "conv_123", 
  "model_used": "phi3:mini",
  "processing_time_ms": 2100
}
```

## Port Configuration

### Service Port Details
- **Primary Port**: **8080** (Configurable via MODELS_SERVICE_PORT)
- **Health Check Port**: Same as primary (8080)
- **Internal Communication**: Port 8080 for container-to-container communication
- **External Access**: Via API Gateway (Port 8000) with routing to `/models/*`

### Environment Configuration
```bash
# Service Configuration
MODELS_SERVICE_PORT=8080
MODELS_SERVICE_MODE=normal  # normal|minimal
DEBUG=false

# Model Configuration
DEFAULT_STT_MODEL=whisper_medium
DEFAULT_TTS_MODEL=coqui_xtts_v2
DEFAULT_NLP_MODEL=sentence_transformers

# Hardware Configuration
USE_GPU=true
MAX_GPU_MEMORY=0.8
TORCH_DEVICE=auto  # auto|cpu|cuda
MAX_CONCURRENT_REQUESTS=10

# Model Loading Strategy
MODELS_PRELOAD_LIST=whisper_medium,coqui_xtts_v2
MODELS_PRELOAD_BACKGROUND=true
MODELS_SERVICE_SKIP_DEFAULTS=false

# External Services
ENABLE_OLLAMA_ROUTES=false
OLLAMA_BASE_URL=http://ollama:11434
TEI_ENDPOINT=http://tei:3000

# Performance Settings
MODEL_CACHE_SIZE=5
REQUEST_TIMEOUT=300
CACHE_SIZE_LIMIT=10737418240  # 10GB

# Paths
MODELS_DIR=/app/models
CACHE_DIR=/app/cache
LOGS_DIR=/app/logs
```

## Request Flow

### STT Processing Flow
```mermaid
sequenceDiagram
    participant Client as Client Service
    participant API as Models Service API
    participant Engine as STT Engine
    participant Manager as Model Manager
    participant Models as Model Repository

    Client->>API: POST /api/v1/stt/transcribe
    API->>API: Validate audio format & language
    
    API->>Engine: Process transcription request
    Engine->>Engine: Select optimal model for language
    
    alt Model Not Loaded
        Engine->>Manager: Load model (whisper_medium)
        Manager->>Models: Retrieve model from cache/disk
        Models-->>Manager: Model loaded
        Manager-->>Engine: Model ready
    end
    
    Engine->>Engine: Preprocess audio (normalize, resample)
    Engine->>Engine: Run inference on audio
    Engine->>Engine: Post-process results
    
    Engine-->>API: Transcription results
    API-->>Client: JSON response with text & metadata
```

### TTS Processing Flow
```mermaid
sequenceDiagram
    participant Client as Client Service
    participant API as Models Service API
    participant Engine as TTS Engine
    participant Manager as Model Manager
    participant Storage as Audio Storage

    Client->>API: POST /api/v1/tts/synthesize
    API->>API: Validate text & language parameters
    
    API->>Engine: Process synthesis request
    Engine->>Engine: Select optimal model & voice
    
    alt Model Not Loaded
        Engine->>Manager: Load model (coqui_xtts_v2)
        Manager-->>Engine: Model ready
    end
    
    Engine->>Engine: Text preprocessing (phonemization)
    Engine->>Engine: Generate audio waveform
    Engine->>Engine: Post-process audio (normalization)
    
    Engine->>Storage: Save audio file
    Storage-->>Engine: Audio URL
    
    Engine-->>API: Synthesis results
    API-->>Client: JSON response with audio URL
```

### Dynamic Model Loading Flow
```mermaid
sequenceDiagram
    participant Request as API Request
    participant Manager as Model Manager
    participant Cache as Model Cache
    participant Download as Model Downloader
    participant Registry as Model Registry

    Request->>Manager: Request model "whisper_large"
    Manager->>Cache: Check if model loaded
    
    alt Model Already Loaded
        Cache-->>Manager: Model instance
    else Model Available Locally
        Manager->>Cache: Load from disk
        Cache-->>Manager: Model loaded
    else Model Not Available
        Manager->>Registry: Check model availability
        Registry-->>Manager: Model metadata
        Manager->>Download: Download model
        Download->>Download: Fetch model files
        Download-->>Manager: Download complete
        Manager->>Cache: Load new model
        Cache-->>Manager: Model ready
    end
    
    Manager-->>Request: Model ready for use
```

## Service Communication

### Internal Service Dependencies

#### Model Repository Integration
```python
# Model Storage and Caching Strategy
Model Storage:
├── Local Disk Cache (MODELS_DIR)
│   ├── whisper_medium/        # 769MB - Multilingual STT
│   ├── coqui_xtts_v2/        # 2.3GB - High-quality TTS
│   ├── vosk_en_us/           # 50MB - Fast English STT
│   └── sentence_transformers/ # 438MB - Text embeddings
├── Memory Cache (Active Models)
│   ├── Recently used models kept in RAM/VRAM
│   ├── LRU eviction policy when cache full
│   └── Configurable cache size limits
└── Remote Model Registry
    ├── Hugging Face Hub integration
    ├── Custom model repository support
    └── Automatic model discovery and metadata
```

#### External Service Integration
```python
# External AI Service Integration
TEI (Text Embeddings Inference):
├── Endpoint: http://tei:3000
├── Purpose: High-performance embeddings generation
├── Models: sentence-transformers variants
└── Load balancing: Round-robin with health checks

Ollama Integration:
├── Endpoint: http://ollama:11434
├── Purpose: Local LLM inference (Phi-3, Llama)
├── Models: phi3:mini, phi3:medium, llama2
└── Context: Conversational AI and text generation

Model Downloads:
├── Hugging Face Hub (huggingface.co)
├── Whisper models (openai/whisper)
├── Coqui TTS models (coqui-ai/TTS)
└── Custom model repositories via HTTP/HTTPS
```

### Cross-Service Communication

#### API Gateway Integration (Port 8000)
```python
# Route Registration in API Gateway
Routes:
├── /models/* → models-service:8080/*
├── Health checks via /health endpoint
├── Model status via /status endpoint
└── Authentication bypass for internal services

# Service Discovery
Configuration:
├── DNS-based service discovery (models-service)
├── Health-based routing decisions
├── Circuit breaker for failure handling
└── Request timeout management (300s default)
```

#### Voice Service Integration (Port 8011)
```python
# Voice Processing Pipeline
Voice Service Communication:
├── STT Processing: POST /api/v1/stt/transcribe
│   ├── Audio format: WAV, MP3, FLAC
│   ├── Languages: en, hi, bn, te, ta, mr
│   └── Real-time processing support
├── TTS Processing: POST /api/v1/tts/synthesize
│   ├── Text input with language detection
│   ├── Voice selection and customization
│   └── Streaming audio response support
└── Language Detection: POST /api/v1/translation/detect-language
    ├── Automatic language identification
    ├── Confidence scoring
    └── Fallback language handling
```

#### Chatbot Service Integration (Port 8004)
```python
# NLP Processing Pipeline
Chatbot Service Communication:
├── Text Generation: POST /api/v1/nlp/generate
│   ├── Conversational AI with Phi-3
│   ├── Context-aware responses
│   └── Mood-based response adaptation
├── Embeddings: POST /api/v1/nlp/embeddings
│   ├── Semantic similarity calculations
│   ├── Context retrieval for conversations
│   └── User intent classification
├── Translation: POST /api/v1/translation/translate
│   ├── Multi-language conversation support
│   ├── Real-time translation
│   └── Cultural context preservation
└── Emotion Analysis: POST /api/v1/emotion/analyze
    ├── Sentiment analysis of user input
    ├── Emotional state detection
    └── Crisis intervention triggers
```

#### Translation Service Integration (Port 8005)
```python
# Translation Pipeline
Translation Service Communication:
├── Text Translation: POST /api/v1/translation/translate
│   ├── NLLB-200 multilingual model
│   ├── Indian language specialization
│   └── Context-aware translation
├── Language Detection: POST /api/v1/translation/detect-language
│   ├── Automatic source language identification
│   ├── Script detection (Devanagari, Latin, etc.)
│   └── Confidence scoring
└── Batch Processing: POST /api/v1/translation/batch
    ├── Large text processing
    ├── Document translation
    └── Asynchronous processing support
```

## High-Level Architecture

### System Design Principles

#### 1. **Centralized Model Management**
```python
Architecture Pattern:
├── Single Source of Truth → All AI models centrally managed
├── Lazy Loading → Models loaded on-demand to optimize memory
├── Intelligent Caching → LRU eviction with configurable limits
├── Hot Swapping → Dynamic model updates without service restart
└── Resource Optimization → GPU/CPU load balancing
```

#### 2. **Multi-Engine Support**
```python
Engine Architecture:
├── STT Engines → Whisper, Vosk, Wav2Vec2, SpeechRecognition
├── TTS Engines → Coqui TTS, eSpeak, Festival, gTTS
├── NLP Engines → Transformers, TEI, Ollama, OpenAI
├── Translation Engines → NLLB, mBART, Google Translate
└── Custom Engines → Plugin architecture for proprietary models
```

#### 3. **Language-First Design**
```python
Language Support:
├── Indian Languages → Hindi, Bengali, Telugu, Tamil, Marathi, etc.
├── International Languages → English, Spanish, French, German, etc.
├── Script Support → Devanagari, Latin, Arabic, Chinese, etc.
├── Cultural Context → Language-specific processing adaptations
└── Accessibility → Voice interfaces for diverse user base
```

### Low-Level Design

#### Model Manager Core Architecture
```python
class ModelManager:
    """Central model lifecycle management with intelligent caching"""
    
    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.available_models: Dict[str, Dict] = {}
        self.loaded_models: Dict[str, Any] = {}
        self.download_progress: Dict[str, Dict] = {}
        self.cache_size_limit = 10 * 1024**3  # 10GB
        self.model_usage_stats: Dict[str, Dict] = {}
    
    async def get_model(self, model_name: str, **kwargs) -> Any:
        """Get model with automatic loading and caching"""
        # 1. Check if model already loaded
        if model_name in self.loaded_models:
            await self._update_usage_stats(model_name)
            return self.loaded_models[model_name]
        
        # 2. Check if model available locally
        if not self.is_model_available(model_name):
            await self.download_model(model_name)
        
        # 3. Load model into memory
        model = await self._load_model_from_disk(model_name, **kwargs)
        
        # 4. Manage cache size
        await self._manage_cache_size()
        
        # 5. Store in loaded models
        self.loaded_models[model_name] = model
        await self._update_usage_stats(model_name)
        
        return model
    
    async def download_model(self, model_name: str) -> bool:
        """Download model with progress tracking"""
        if model_name in self.downloading:
            return await self._wait_for_download(model_name)
        
        self.downloading.add(model_name)
        
        try:
            config = self.model_configs.get(model_name)
            if not config:
                raise ValueError(f"Unknown model: {model_name}")
            
            # Download from appropriate source
            if config.get("source") == "huggingface":
                success = await self._download_from_huggingface(model_name, config)
            elif config.get("source") == "custom":
                success = await self._download_from_url(model_name, config)
            else:
                success = await self._download_from_registry(model_name, config)
            
            if success:
                await self._validate_downloaded_model(model_name)
            
            return success
            
        finally:
            self.downloading.discard(model_name)
```

#### STT Engine Architecture
```python
class STTEngine:
    """Multi-engine speech-to-text processing"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.loaded_models: Dict[str, Any] = {}
        
        # Engine-specific handlers
        self.engine_handlers = {
            "whisper": self._handle_whisper,
            "vosk": self._handle_vosk,
            "wav2vec2": self._handle_wav2vec2,
            "speech_recognition": self._handle_speech_recognition
        }
    
    async def transcribe(self, audio_data: bytes, language: str = "auto", 
                        model_preference: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe audio with automatic model selection"""
        
        # 1. Preprocess audio
        processed_audio = await self._preprocess_audio(audio_data)
        
        # 2. Select optimal model
        model_name = await self._select_optimal_model(language, model_preference)
        
        # 3. Load model if needed
        model = await self.model_manager.get_model(model_name)
        
        # 4. Determine engine type
        engine_type = self._get_engine_type(model_name)
        handler = self.engine_handlers[engine_type]
        
        # 5. Run inference
        result = await handler(model, processed_audio, language)
        
        # 6. Post-process results
        return await self._postprocess_results(result, model_name)
    
    async def _select_optimal_model(self, language: str, 
                                  preference: Optional[str] = None) -> str:
        """Select best model based on language, quality, and availability"""
        if preference and self._is_model_suitable(preference, language):
            return preference
        
        # Get available models for language
        suitable_models = self.supported_languages.get(language, [])
        
        if not suitable_models:
            # Fallback to multilingual models
            suitable_models = ["whisper_medium", "whisper_base"]
        
        # Prioritize by quality and availability
        for model_name in suitable_models:
            if self.model_manager.is_model_available(model_name):
                return model_name
        
        # Return best available model
        return suitable_models[0] if suitable_models else "whisper_base"
```

#### TTS Engine Architecture
```python
class TTSEngine:
    """Multi-engine text-to-speech synthesis"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.loaded_models: Dict[str, Any] = {}
        
        # Voice configuration per language
        self.voice_configs = {
            "en": {"default": "neutral", "male": "formal", "female": "gentle"},
            "hi": {"default": "neutral", "male": "traditional", "female": "modern"},
            "bn": {"default": "neutral", "male": "classic", "female": "contemporary"}
        }
    
    async def synthesize(self, text: str, language: str = "en", 
                        voice: Optional[str] = None,
                        model_preference: Optional[str] = None) -> Dict[str, Any]:
        """Synthesize speech with voice customization"""
        
        # 1. Text preprocessing
        processed_text = await self._preprocess_text(text, language)
        
        # 2. Select model and voice
        model_name = await self._select_optimal_model(language, model_preference)
        voice_config = await self._select_voice(language, voice)
        
        # 3. Load model
        model = await self.model_manager.get_model(model_name)
        
        # 4. Generate audio
        audio_data = await self._generate_audio(
            model, processed_text, language, voice_config
        )
        
        # 5. Post-process and save
        return await self._save_audio_file(audio_data, model_name)
    
    async def _generate_audio(self, model: Any, text: str, 
                            language: str, voice_config: Dict) -> bytes:
        """Generate audio using appropriate TTS engine"""
        engine_type = self._get_engine_type(model)
        
        if engine_type == "coqui":
            return await self._coqui_synthesis(model, text, language, voice_config)
        elif engine_type == "espeak":
            return await self._espeak_synthesis(model, text, language, voice_config)
        elif engine_type == "festival":
            return await self._festival_synthesis(model, text, language, voice_config)
        else:
            raise ValueError(f"Unsupported TTS engine: {engine_type}")
```

## Design Documentation

### Model Configuration Schema

#### Core Model Registry
```yaml
# Model Configuration Format
model_configs:
  whisper_medium:
    type: "stt"
    engine: "whisper"
    source: "huggingface"
    repository: "openai/whisper-medium"
    languages: ["multilingual"]
    quality: "high"
    size_mb: 769
    device: ["cpu", "cuda"]
    requirements:
      python: ">=3.8"
      torch: ">=1.13.0"
    performance:
      cpu_inference_time: 2.5  # seconds per minute of audio
      gpu_inference_time: 0.8
      memory_usage_mb: 2048
  
  coqui_xtts_v2:
    type: "tts"
    engine: "coqui"
    source: "huggingface"
    repository: "coqui/XTTS-v2"
    languages: ["multilingual"]
    quality: "high" 
    size_mb: 2304
    device: ["cpu", "cuda"]
    voices:
      - id: "default"
        name: "Default Neutral"
        gender: "neutral"
      - id: "male_formal"
        name: "Formal Male"
        gender: "male"
```

#### Indian Language Configuration
```yaml
# Indian Languages Support Matrix
indian_languages:
  hi:  # Hindi
    name: "हिंदी"
    script: "Devanagari"
    iso_639_1: "hi"
    iso_639_3: "hin"
    stt_models:
      - "whisper_medium"      # High quality, slower
      - "vosk_hi"            # Medium quality, faster
      - "wav2vec2_hi"        # Good quality, local
    tts_models:
      - "coqui_xtts_v2"      # High quality, multilingual
      - "coqui_hi"           # Hindi-specific model
      - "espeak_hi"          # Fast, lightweight
    quality_rankings:
      stt: ["whisper_medium", "wav2vec2_hi", "vosk_hi"]
      tts: ["coqui_xtts_v2", "coqui_hi", "espeak_hi"]
  
  bn:  # Bengali
    name: "বাংলা"
    script: "Bengali"
    iso_639_1: "bn"
    iso_639_3: "ben"
    stt_models:
      - "whisper_medium"
      - "wav2vec2_bn"
    tts_models:
      - "coqui_xtts_v2"
      - "coqui_bn"
      - "espeak_bn"
```

### Performance Optimization Strategy

#### Memory Management
```python
# Memory Usage Optimization
Memory_Strategy:
├── Model Quantization → 8-bit/16-bit model loading for efficiency
├── Lazy Loading → Models loaded only when requested
├── LRU Eviction → Least recently used models removed first
├── GPU Memory Pools → Efficient VRAM allocation and cleanup
└── Batch Processing → Multiple requests processed together

# Cache Management
Cache_Levels:
├── L1: In-Memory Model Cache (loaded models)
├── L2: Disk Cache (downloaded models)
├── L3: Network Cache (model registry metadata)
└── Session Cache (temporary audio files)
```

#### Inference Optimization
```python
# Performance Optimizations
Inference_Optimizations:
├── Model Compilation → TorchScript/ONNX for faster inference
├── Batch Inference → Process multiple inputs simultaneously
├── Async Processing → Non-blocking API responses
├── GPU Acceleration → CUDA/ROCm/Metal support
├── Mixed Precision → FP16/BF16 for faster processing
└── Model Distillation → Smaller models for edge deployment
```

### Security & Privacy Design

#### Data Protection
```python
Privacy_Measures:
├── Data Encryption → All audio/text data encrypted in transit
├── Temporary Storage → Audio files automatically deleted after processing
├── No Data Logging → Model inputs not logged in production
├── Memory Cleanup → Sensitive data cleared from memory after use
└── Access Control → API authentication and rate limiting

# GDPR Compliance
GDPR_Features:
├── Data Minimization → Only process necessary data
├── Right to Deletion → Automatic cleanup of temporary files
├── Data Portability → Standard formats for all outputs
├── Privacy by Design → Default privacy-friendly settings
└── Consent Management → Clear data processing agreements
```

#### Model Security
```python
Security_Layers:
├── Model Validation → Cryptographic verification of downloaded models
├── Sandboxed Execution → Isolated model runtime environments
├── Resource Limits → CPU/memory/GPU usage constraints
├── Input Validation → Comprehensive sanitization of all inputs
└── Audit Logging → Complete access and usage logging
```

## Incomplete Implementations & TODOs

### Current Limitations

#### 1. **Advanced Model Features Missing**
```python
# TODO: Advanced Model Capabilities
class AdvancedModelFeatures:
    # Currently basic model loading and inference
    # Needed: Advanced model optimization and deployment features
    
    async def model_quantization(self, model_name: str, precision: str):
        """Model quantization for efficiency - NOT YET IMPLEMENTED"""
        # TODO: 8-bit and 16-bit model quantization
        # TODO: Dynamic quantization based on hardware
        # TODO: Calibration dataset for post-training quantization
        raise NotImplementedError("Model quantization not implemented")
    
    async def model_compilation(self, model_name: str, target_device: str):
        """Model compilation optimization - NOT YET IMPLEMENTED"""
        # TODO: TorchScript compilation for faster inference
        # TODO: ONNX conversion for cross-platform deployment
        # TODO: TensorRT optimization for NVIDIA GPUs
        # TODO: OpenVINO optimization for Intel hardware
        raise NotImplementedError("Model compilation not implemented")
    
    async def distributed_inference(self, model_name: str, input_data: Any):
        """Distributed model inference - NOT YET IMPLEMENTED"""
        # TODO: Multi-GPU inference support
        # TODO: Model parallelism for large models
        # TODO: Pipeline parallelism for sequential processing
        raise NotImplementedError("Distributed inference not implemented")
```

#### 2. **Real-time Processing Gaps**
```python
# TODO: Real-time Audio Processing
class RealTimeProcessing:
    # Current: Batch audio processing only
    # Missing: Streaming and real-time capabilities
    
    async def streaming_stt(self, audio_stream: AsyncIterator[bytes]):
        """Real-time streaming STT - NOT YET IMPLEMENTED"""
        # TODO: WebSocket-based streaming audio input
        # TODO: Incremental transcription with confidence scores
        # TODO: Voice activity detection (VAD)
        # TODO: Real-time language detection
        pass
    
    async def streaming_tts(self, text_stream: AsyncIterator[str]):
        """Real-time streaming TTS - NOT YET IMPLEMENTED"""
        # TODO: Real-time audio synthesis streaming
        # TODO: Low-latency voice synthesis
        # TODO: Adaptive audio quality based on bandwidth
        # TODO: Voice cloning and customization
        pass
    
    async def real_time_translation(self, audio_stream: AsyncIterator[bytes]):
        """Real-time speech translation - NOT YET IMPLEMENTED"""
        # TODO: Live speech-to-speech translation
        # TODO: Simultaneous interpretation capabilities
        # TODO: Multi-speaker handling
        pass
```

#### 3. **Advanced NLP Features**
```python
# TODO: Comprehensive NLP Pipeline
class AdvancedNLPFeatures:
    """Advanced natural language processing - PARTIALLY IMPLEMENTED"""
    
    async def emotion_analysis(self, text: str, context: Dict):
        """Emotion and sentiment analysis - BASIC IMPLEMENTATION"""
        # TODO: Multi-dimensional emotion analysis
        # TODO: Cultural context in emotion detection
        # TODO: Temporal emotion tracking
        # TODO: Voice-based emotion recognition
        pass
    
    async def intent_classification(self, text: str, domain: str):
        """Intent classification and entity extraction - NOT YET IMPLEMENTED"""
        # TODO: Domain-specific intent recognition
        # TODO: Named entity recognition (NER)
        # TODO: Slot filling for structured data
        # TODO: Context-aware intent understanding
        pass
    
    async def conversation_ai(self, message: str, context: Dict):
        """Advanced conversational AI - BASIC IMPLEMENTATION"""
        # TODO: Multi-turn conversation management
        # TODO: Personality-based response generation
        # TODO: Emotional intelligence in responses
        # TODO: Memory and context retention
        pass
```

#### 4. **Missing API Endpoints**
```python
# TODO: Advanced Model Management
@app.post("/api/v1/models/optimize")
async def optimize_model():
    """Model optimization and quantization - NOT YET IMPLEMENTED"""
    pass

@app.post("/api/v1/models/fine-tune")
async def fine_tune_model():
    """Model fine-tuning capabilities - NOT YET IMPLEMENTED"""
    pass

# TODO: Batch Processing Endpoints
@app.post("/api/v1/stt/batch")
async def batch_transcribe():
    """Batch audio transcription - NOT YET IMPLEMENTED"""
    pass

@app.post("/api/v1/tts/batch")
async def batch_synthesize():
    """Batch text synthesis - NOT YET IMPLEMENTED"""
    pass

# TODO: Advanced Audio Processing
@app.post("/api/v1/audio/enhance")
async def enhance_audio():
    """Audio enhancement and noise reduction - NOT YET IMPLEMENTED"""
    pass

@app.post("/api/v1/audio/speaker-diarization")
async def speaker_diarization():
    """Speaker separation and identification - NOT YET IMPLEMENTED"""
    pass

# TODO: Model Analytics
@app.get("/api/v1/analytics/model-performance")
async def get_model_analytics():
    """Model performance analytics - NOT YET IMPLEMENTED"""
    pass

@app.get("/api/v1/analytics/usage-statistics")
async def get_usage_statistics():
    """Service usage statistics - NOT YET IMPLEMENTED"""
    pass
```

#### 5. **Performance Monitoring Gaps**
```python
# TODO: Comprehensive Monitoring
class PerformanceMonitoring:
    """Advanced performance monitoring - NOT YET IMPLEMENTED"""
    
    async def model_performance_tracking(self):
        # TODO: Real-time inference latency monitoring
        # TODO: Model accuracy tracking over time
        # TODO: Resource utilization per model
        # TODO: Cost analysis per inference
        pass
    
    async def predictive_scaling(self):
        # TODO: Auto-scaling based on load patterns
        # TODO: Model preloading based on usage prediction
        # TODO: Dynamic resource allocation
        # TODO: Load balancing across model instances
        pass
```

#### 6. **Voice Quality Enhancement**
```python
# TODO: Advanced Audio Processing
class AudioProcessing:
    """Audio enhancement and quality improvement - NOT YET IMPLEMENTED"""
    
    async def noise_reduction(self, audio_data: bytes):
        """Noise reduction and audio enhancement - NOT YET IMPLEMENTED"""
        # TODO: Spectral noise reduction
        # TODO: Echo cancellation
        # TODO: Audio normalization
        # TODO: Dynamic range compression
        pass
    
    async def voice_conversion(self, audio_data: bytes, target_voice: str):
        """Voice conversion and cloning - NOT YET IMPLEMENTED"""
        # TODO: Real-time voice conversion
        # TODO: Custom voice training
        # TODO: Emotional voice synthesis
        # TODO: Age/gender voice transformation
        pass
```

### Technical Debt

#### 1. **Testing Infrastructure**
```python
# Current: Basic unit tests exist
# Missing:
├── Comprehensive integration tests with real models
├── Performance benchmarking tests
├── Load testing for concurrent requests
├── Audio quality regression tests
└── Cross-language consistency tests

# TODO: Test Coverage Improvement
Target Coverage:
├── Unit Tests: 95%+ coverage for all engines
├── Integration Tests: All API endpoints tested
├── Performance Tests: Latency and throughput validation
└── Audio Quality Tests: Automated quality assessment
```

#### 2. **Error Handling & Resilience**
```python
# TODO: Comprehensive Error Handling
Error_Handling_Gaps:
├── Graceful model loading failures
├── Audio format compatibility issues
├── Out-of-memory handling for large models
├── Network failure recovery during downloads
└── Partial model corruption detection and recovery
```

#### 3. **Configuration Management**
```python
# TODO: Advanced Configuration
Configuration_Needs:
├── Dynamic configuration updates without restart
├── A/B testing for different models
├── Feature flags for experimental features
├── Environment-specific model configurations
└── User-specific model preferences
```

## Future Development Plans

### Phase 1 - Real-time Processing (Q4 2025)

#### 1.1 **Streaming Audio Support**
- [ ] **WebSocket Streaming** - Real-time audio input/output via WebSockets
- [ ] **Voice Activity Detection** - Automatic speech/silence detection
- [ ] **Incremental STT** - Progressive transcription with live updates
- [ ] **Low-latency TTS** - Sub-second audio generation for real-time responses
- [ ] **Adaptive Quality** - Dynamic quality adjustment based on network conditions

#### 1.2 **Real-time Translation**
```python
Real_Time_Features:
├── Speech-to-speech translation with <3s latency
├── Simultaneous interpretation capabilities
├── Multi-speaker conversation handling
├── Real-time language detection and switching
└── Cultural context preservation in translation
```

#### 1.3 **Performance Optimization**
```python
Performance_Improvements:
├── Model quantization for 50% faster inference
├── GPU memory optimization for concurrent processing
├── Batch inference for improved throughput
├── Model compilation with TorchScript/ONNX
└── Edge deployment for local processing
```

### Phase 2 - Advanced AI Features (Q1 2026)

#### 2.1 **Emotion-Aware Processing**
- [ ] **Emotional STT** - Emotion detection from speech patterns
- [ ] **Emotional TTS** - Voice synthesis with emotional expression
- [ ] **Sentiment Analysis** - Real-time sentiment tracking in conversations
- [ ] **Mood-based Responses** - AI responses adapted to user emotional state
- [ ] **Cultural Emotion Recognition** - Culture-specific emotion interpretation

#### 2.2 **Advanced Conversational AI**
```python
Conversational_Features:
├── Multi-turn conversation memory and context
├── Personality-based AI assistants
├── Domain-specific knowledge integration
├── Proactive conversation engagement
└── Therapeutic conversation capabilities
```

#### 2.3 **Voice Personalization**
```python
Voice_Personalization:
├── Custom voice training from user samples
├── Voice cloning with minimal data
├── Emotional voice modulation
├── Age and accent adaptation
└── Accessibility-focused voice options
```

### Phase 3 - Enterprise Platform (Q2 2026)

#### 3.1 **Model Management Platform**
- [ ] **Model Registry** - Centralized model versioning and deployment
- [ ] **A/B Testing** - Model performance comparison and rollout
- [ ] **Custom Models** - Support for user-trained models
- [ ] **Model Marketplace** - Community model sharing and discovery
- [ ] **Automated Optimization** - Self-tuning model performance

#### 3.2 **Analytics & Monitoring**
```python
Analytics_Platform:
├── Real-time inference monitoring and alerting
├── Model accuracy tracking and degradation detection
├── Usage analytics and cost optimization
├── Performance benchmarking across models
└── Quality assurance automation
```

#### 3.3 **Integration Ecosystem**
```python
Integration_Features:
├── Webhook system for external model integrations
├── Plugin architecture for custom processing pipelines
├── Third-party model provider integrations
├── Multi-cloud deployment support
└── Edge computing distribution
```

### Phase 4 - Research & Innovation (Q3-Q4 2026)

#### 4.1 **Cutting-edge AI Research**
- [ ] **Multimodal AI** - Text, speech, and visual processing integration
- [ ] **Few-shot Learning** - Rapid adaptation to new voices and languages
- [ ] **Neural Architecture Search** - Automated model design optimization
- [ ] **Continual Learning** - Models that improve through usage
- [ ] **Federated Learning** - Privacy-preserving collaborative model training

#### 4.2 **Innovation Features**
```python
Innovation_Research:
├── Quantum-enhanced audio processing algorithms
├── Brain-computer interface integration
├── Augmented reality voice interaction
├── Emotional AI for mental health applications
└── Cross-modal learning (audio-visual-text)
```

### **Immediate Action Plan: Phi-3 to Phi-4 Migration** 🚀

#### **Week 1: Critical Fixes**
```bash
# 1. Update model engine
mv models/phi3_engine.py models/phi4_engine.py

# 2. Update model name in phi4_engine.py
- self.model_name = "microsoft/Phi-3-mini-4k-instruct"
+ self.model_name = "microsoft/Phi-4-mini-instruct"

# 3. Fix API route defaults
- model: Optional[str] = "phi3:mini"
+ model: Optional[str] = "phi4-mini-instruct"

# 4. Update imports
- from models.phi3_engine import Phi3Engine
+ from models.phi4_engine import Phi4Engine
```

#### **Week 2: Service Architecture Decision**
**Option A: Consolidate Services (Recommended)**
```bash
# Remove separate phi3_agent service
rm -rf backend/services/phi3_agent/

# Integrate functionality into models_service
# Update docker-compose to remove phi3_agent:8016
```

**Option B: Keep Separate but Specialized**
```bash
# models_service:8080 → STT/TTS/Basic NLP
# phi3_agent:8016 → Advanced reasoning/conversation
# Update service responsibilities documentation
```

#### **Week 3: Performance Validation**
```python
# Benchmark comparison
Phi-3 Performance:
├── Context: 4K tokens
├── Speed: 50-100 tokens/sec (GPU)
└── Memory: 8GB VRAM

Phi-4 Expected Performance:
├── Context: 64K tokens (16x improvement)
├── Speed: 80-150 tokens/sec (GPU) 
└── Memory: 8GB VRAM (similar)
```

### Development Roadmap Timeline

```
2025 Q4: Phi-4 Migration & Real-time Processing
├── Week 1-2: CRITICAL - Phi-3 to Phi-4 migration
├── Week 3-4: Service architecture consolidation  
├── Week 5-8: WebSocket streaming implementation
├── Week 9-12: Voice activity detection and incremental STT
└── Week 13-16: Real-time translation pipeline

2026 Q1: Advanced AI Features (Phi-4 Powered)
├── Month 1: Phi-4 Flash Reasoning integration
├── Month 2: 64K context window optimization
└── Month 3: Advanced conversational AI capabilities

2026 Q2: Enterprise Platform Development
├── Month 1: Model management platform
├── Month 2: Analytics and monitoring system
└── Month 3: Integration ecosystem development

2026 Q3-Q4: Research & Innovation Phase
├── Q3: Cutting-edge AI research implementation
└── Q4: Innovation features and future-proofing
```

## Development & Testing

### Local Development Setup

#### Prerequisites
```bash
# System requirements
Python 3.11+
PyTorch 1.13+
CUDA 11.8+ (optional, for GPU acceleration)
FFmpeg (for audio processing)
Docker & Docker Compose (optional)

# Hardware recommendations
CPU: 8+ cores for concurrent processing
RAM: 16GB+ (32GB recommended for large models)
GPU: 8GB+ VRAM (optional, for acceleration)
Storage: 50GB+ SSD for model cache
```

#### Quick Start
```bash
# 1. Clone and navigate to service
cd /home/sachin/mantrapath/backend/services/models_service

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export MODELS_SERVICE_PORT=8080
export MODELS_DIR=./models
export USE_GPU=true
export DEBUG=true

# 5. Start service in minimal mode (fast startup)
export MODELS_SERVICE_MODE=minimal
python main.py

# 6. Or start with preloaded models
export MODELS_PRELOAD_LIST=whisper_medium,espeak_en
python main.py
```

#### Docker Development
```bash
# Build and run with Docker
docker build -t mantrapath/models-service .
docker run -d \
  --name models-service \
  -p 8080:8080 \
  --gpus all \
  -e MODELS_SERVICE_MODE=minimal \
  -e USE_GPU=true \
  -v $(pwd)/models:/app/models \
  mantrapath/models-service
```

### Testing Strategy

#### Unit Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Test specific components
python -m pytest tests/test_stt_engine.py -v
python -m pytest tests/test_tts_engine.py -v
python -m pytest tests/test_model_manager.py -v
python -m pytest tests/test_nlp_engine.py -v

# Coverage reporting
python -m pytest tests/ --cov=. --cov-report=html
```

#### Integration Testing
```bash
# API endpoint testing
python -m pytest tests/test_api_routes.py -v

# Model loading testing
python -m pytest tests/test_model_integration.py -v

# Cross-engine compatibility testing
python -m pytest tests/test_engine_compatibility.py -v
```

#### Performance Testing
```bash
# Load testing with multiple concurrent requests
python tests/performance/test_concurrent_requests.py

# Audio quality testing
python tests/quality/test_audio_quality.py

# Model inference benchmarking
python tests/benchmarks/test_model_performance.py
```

### Production Deployment

#### Container Deployment
```dockerfile
# Production-optimized Dockerfile
FROM python:3.11-slim
WORKDIR /app

# System dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg sox libsndfile1 espeak-ng festival \
    build-essential gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Python dependencies with caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Create non-root user
RUN groupadd -r modelsuser && useradd -r -g modelsuser modelsuser
RUN chown -R modelsuser:modelsuser /app
USER modelsuser

# Expose port and health check
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s \
    CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["python", "main.py"]
```

#### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: models-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: models-service
  template:
    metadata:
      labels:
        app: models-service
    spec:
      containers:
      - name: models-service
        image: mantrapath/models-service:latest
        ports:
        - containerPort: 8080
        env:
        - name: MODELS_SERVICE_MODE
          value: "minimal"
        - name: USE_GPU
          value: "true"
        - name: MODELS_PRELOAD_LIST
          value: "whisper_medium,espeak_en,espeak_hi"
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "16Gi"
            cpu: "8"
            nvidia.com/gpu: 1
        volumeMounts:
        - name: models-cache
          mountPath: /app/models
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 120
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /status
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 10
      volumes:
      - name: models-cache
        persistentVolumeClaim:
          claimName: models-cache-pvc
```

## Monitoring & Observability

### Health Monitoring
```python
# Service health endpoints provide comprehensive status
Health_Checks:
├── /health → Basic health status for load balancers
├── /status → Detailed status including hardware and models
├── /models/loaded → Currently loaded models status
└── /models/available → Available models inventory

# Key metrics to monitor
Critical_Metrics:
├── Model loading success rate (percentage)
├── STT processing latency (seconds per minute of audio)
├── TTS synthesis quality (MOS scores)
├── GPU utilization and memory usage (percentage)
├── Concurrent request handling (requests/second)
├── Model cache hit ratio (percentage)
└── Download success rate for new models (percentage)
```

### Logging Strategy
```python
# Structured logging format for production
{
    "timestamp": "2025-09-27T14:30:00Z",
    "level": "INFO",
    "service": "models_service",
    "component": "stt_engine",
    "model_name": "whisper_medium",
    "operation": "transcribe",
    "audio_duration": 45.2,
    "processing_time_ms": 1150.7,
    "language_detected": "en",
    "confidence": 0.94,
    "gpu_memory_used": 2048,
    "correlation_id": "req_abc123"
}
```

### Performance Metrics
```python
# Business metrics for monitoring
Business_KPIs:
├── STT accuracy rate > 95% for supported languages
├── TTS naturalness score > 4.0/5.0 (MOS)
├── Average processing latency < 2x real-time
├── Model availability uptime > 99.9%
├── GPU utilization efficiency > 80%
└── User satisfaction with voice quality > 90%
```

## Contributing

### Development Guidelines
1. **Code Quality**: Follow PEP 8 style guidelines and comprehensive type hints
2. **Testing**: Write unit tests for all new model integrations
3. **Documentation**: Update API documentation for all endpoint changes
4. **Performance**: Consider memory usage implications of new models
5. **Accessibility**: Ensure voice interfaces work for diverse user needs

### Key Areas for Contribution
- **Model Integration** - Adding support for new STT/TTS/NLP models
- **Language Support** - Expanding language coverage, especially Indian languages
- **Performance Optimization** - Model quantization, caching, and GPU acceleration
- **Real-time Processing** - Streaming audio and low-latency inference
- **Quality Enhancement** - Audio processing, noise reduction, and voice cloning
- **Testing Infrastructure** - Comprehensive test coverage and benchmarking

---

**Service Status**: ✅ Active Development  
**Port**: 8080 (Configurable)  
**Version**: 1.0.0  
**Last Updated**: September 2025  
**Maintainer**: MantraPath Development Team  
**License**: MIT License