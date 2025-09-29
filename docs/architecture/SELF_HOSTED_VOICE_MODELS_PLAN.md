# Self-Hosted Voice Models Implementation Plan
## MantraPath Voice Service - Open Source Alternative Models

### 🚀 **Executive Summary**

This document outlines the plan to implement fully self-hosted, open-source TTS and STT models for the MantraPath project. External API dependencies have been removed; local and open models are authoritative.

---

## 📊 **Current State Analysis**

### **Current Dependencies (API-based)**
- **STT**: Whisper-compatible local model (no external API)
- **TTS**: ElevenLabs API (quota limited, expensive)
- **Languages**: English, Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean, Arabic, Hindi, Russian

### **Current Limitations**
- ❌ API quota exhaustion
- ❌ High latency (network dependent)
- ❌ Cost scaling issues
- ❌ No offline capabilities
- ❌ Limited customization

---

## 🎯 **Self-Hosted Solutions**

### **1. Speech-to-Text (STT) Models**

#### **🥇 Primary: Whisper-Compatible (Local)**
```yaml
Model: whisper-large-v3
Size: ~3GB
Languages: 99+ languages (including all your supported ones)
Accuracy: Industry leading (>95% for English)
Latency: ~2-5 seconds (depending on hardware)
Hardware: GPU recommended (CUDA), CPU acceptable
Memory: 8GB RAM minimum, 16GB recommended
```

**Implementation Details:**
- **Models Available**: tiny, base, small, medium, large, large-v2, large-v3
- **Multilingual**: Native support for all your target languages
- **Formats**: WAV, MP3, FLAC, M4A, OGG, WEBM
- **Features**: Transcription, translation, timestamp alignment

#### **🥈 Alternative: SpeechRecognition + Vosk**
```yaml
Model: vosk-model-en-us-0.22, vosk-model-small-en-us-0.15
Size: 50MB (small) to 1.8GB (large)
Languages: 20+ languages available
Accuracy: ~85-90% (good for real-time)
Latency: <1 second (real-time capable)
Hardware: CPU only
Memory: 2-4GB RAM
```

#### **🥉 Backup: SpeechRecognition + PocketSphinx**
```yaml
Model: PocketSphinx acoustic models
Size: ~100MB per language
Languages: English, Spanish, French, German, Chinese
Accuracy: ~75-80% (basic but reliable)
Latency: <500ms (very fast)
Hardware: CPU only, low resource
Memory: 1-2GB RAM
```

### **2. Text-to-Speech (TTS) Models**

#### **🥇 Primary: Coqui TTS (XTTS-v2)**
```yaml
Model: tts_models/multilingual/multi-dataset/xtts_v2
Size: ~6GB
Languages: 17 languages (covers all your targets)
Quality: Near human-like, voice cloning capable
Latency: ~3-8 seconds
Hardware: GPU strongly recommended
Memory: 12GB RAM minimum
```

**Features:**
- **Voice Cloning**: Few-shot voice cloning from 10-30 seconds of audio
- **Multilingual**: Single model for all languages
- **Streaming**: Supports streaming synthesis
- **Emotions**: Natural emotional expression

#### **🥈 Alternative: Festival + MBROLA**
```yaml
Model: Festival diphone databases + MBROLA
Size: ~200MB per voice
Languages: 40+ languages available
Quality: Synthetic but clear
Latency: <2 seconds
Hardware: CPU only
Memory: 2-4GB RAM
```

#### **🥉 Backup: eSpeak-NG**
```yaml
Model: eSpeak-NG voices
Size: ~10MB total
Languages: 100+ languages
Quality: Robotic but intelligible
Latency: <500ms (very fast)
Hardware: CPU only, minimal resources
Memory: <1GB RAM
```

#### **🌟 Premium Alternative: Bark (Suno AI)**
```yaml
Model: Bark semantic/coarse/fine models
Size: ~8GB total
Languages: Multilingual (text-prompted)
Quality: Extremely natural, with non-speech sounds
Latency: ~10-30 seconds
Hardware: GPU required (8GB+ VRAM)
Memory: 16GB+ RAM
```

### **3. Voice Emotion Analysis**

#### **Primary: OpenSMILE + scikit-learn**
```yaml
Model: Custom trained emotion classifier
Size: ~100MB
Features: Joy, Sadness, Anger, Fear, Surprise, Neutral
Accuracy: ~80-85%
Latency: <1 second
Hardware: CPU only
```

#### **Alternative: speechbrain/emotion-recognition**
```yaml
Model: Pre-trained emotion recognition
Size: ~500MB
Languages: English primarily
Accuracy: ~90%
Latency: ~2 seconds
Hardware: GPU recommended
```

---

## 🏗️ **Implementation Architecture**

### **Model Priority System**
```python
STT_ENGINES = [
    {
        "name": "whisper_local",
        "priority": 1,
        "type": "local",
        "model": "whisper-large-v3",
        "fallback": "whisper_api"
    },
    {
        "name": "vosk",
        "priority": 2,
        "type": "local",
        "model": "vosk-model-en-us-0.22",
        "fallback": "whisper_local"
    },
    {
        "name": "whisper_api",
        "priority": 3,
        "type": "api",
        "fallback": None
    }
]

TTS_ENGINES = [
    {
        "name": "coqui_xtts",
        "priority": 1,
        "type": "local",
        "model": "xtts_v2",
        "fallback": "festival"
    },
    {
        "name": "festival",
        "priority": 2,
        "type": "local",
        "model": "festival_voices",
        "fallback": "elevenlabs_api"
    },
    {
        "name": "elevenlabs_api",
        "priority": 3,
        "type": "api",
        "fallback": "espeak"
    },
    {
        "name": "espeak",
        "priority": 4,
        "type": "local",
        "model": "espeak_voices",
        "fallback": None
    }
]
```

### **Resource Management**
```python
# GPU Memory Management
GPU_MEMORY_ALLOCATION = {
    "whisper_large": "4GB",
    "coqui_xtts": "6GB",
    "emotion_analysis": "2GB",
    "buffer": "2GB"
}

# CPU Fallback Models
CPU_MODELS = {
    "stt": ["vosk", "pocketsphinx"],
    "tts": ["festival", "espeak"],
    "emotion": ["opensmile"]
}
```

---

## 📦 **Required Dependencies**

### **Core ML Libraries**
```python
# requirements_local.txt
torch>=2.0.0
torchaudio>=2.0.0
transformers>=4.25.0
datasets>=2.6.0
librosa>=0.10.0
soundfile>=0.12.0
numpy>=1.24.0
scipy>=1.10.0

# Whisper Local
# Removed external OpenAI package pin; using faster-whisper / whisper.cpp variants
faster-whisper>=0.9.0  # Faster inference

# Coqui TTS
coqui-tts>=0.15.0

# Vosk
vosk>=0.3.45

# Festival TTS
festival  # System package
espeak-ng  # System package

# Emotion Analysis
speechbrain>=0.5.14
opensmile>=2.5.0
scikit-learn>=1.3.0

# Audio Processing
pydub>=0.25.1
webrtcvad>=2.0.10
```

### **System Dependencies**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y \
    festival \
    espeak espeak-data \
    libespeak-ng-dev \
    festival-dev \
    speech-tools \
    festvox-kallpc16k \
    ffmpeg \
    sox \
    libsox-fmt-all

# macOS
brew install festival espeak sox ffmpeg

# CUDA (for GPU acceleration)
# Follow official NVIDIA CUDA installation guide
```

---

## 🛠️ **Implementation Steps**

### **Phase 1: Local Whisper Integration (Week 1)**
1. **Install Dependencies**
   ```bash
    pip install faster-whisper torch torchaudio
   ```

2. **Create Local Whisper Engine**
   ```python
   # File: engines/whisper_local_engine.py
   import whisper
   from faster_whisper import WhisperModel
   
   class LocalWhisperEngine(BaseSTTEngine):
       def __init__(self):
           self.model = WhisperModel("large-v3", device="cuda")
   ```

3. **Download Models**
   ```bash
   python -c "import whisper; whisper.load_model('large-v3')"
   ```

### **Phase 2: Coqui TTS Integration (Week 2)**
1. **Install Coqui TTS**
   ```bash
   pip install coqui-tts
   ```

2. **Create Coqui Engine**
   ```python
   # File: engines/coqui_tts_engine.py
   from TTS.api import TTS
   
   class CoquiTTSEngine(BaseTTSEngine):
       def __init__(self):
           self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
   ```

### **Phase 3: Fallback Models (Week 3)**
1. **Vosk Integration**
   ```bash
   pip install vosk
   wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
   ```

2. **Festival Integration**
   ```python
   # System integration with festival
   subprocess.run(["festival", "--tts"], input=text, text=True)
   ```

### **Phase 4: Optimization & Monitoring (Week 4)**
1. **Model Caching**
2. **Performance Monitoring**
3. **Auto-fallback Logic**
4. **Resource Management**

---

## 💾 **Storage Requirements**

### **Model Storage**
```
/data/models/
├── whisper/
│   ├── large-v3.pt (3GB)
│   ├── medium.pt (1.5GB)
│   └── base.pt (290MB)
├── coqui/
│   ├── xtts_v2/ (6GB)
│   └── vocoder/ (1GB)
├── vosk/
│   ├── en-us-0.22/ (1.8GB)
│   ├── es-0.42/ (1.2GB)
│   └── fr-0.39/ (1.5GB)
└── emotion/
    ├── opensmile_models/ (100MB)
    └── speechbrain/ (500MB)

Total: ~15-20GB
```

### **Cache Storage**
```
/data/cache/
├── whisper_cache/ (2GB)
├── tts_cache/ (5GB)
└── temp_audio/ (1GB)

Total: ~8GB
```

---

## ⚡ **Performance Benchmarks**

### **Expected Latencies (Local)**
| Model | Task | GPU | CPU | Quality |
|-------|------|-----|-----|---------|
| Whisper Large-v3 | STT | 2-4s | 10-20s | 95%+ |
| Whisper Medium | STT | 1-2s | 5-10s | 90%+ |
| Coqui XTTS-v2 | TTS | 3-6s | 15-30s | 90%+ |
| Festival | TTS | N/A | 1-2s | 70% |
| Vosk | STT | N/A | <1s | 85% |

### **Hardware Recommendations**

#### **Minimum Requirements**
- **CPU**: 8 cores, 3.0GHz+
- **RAM**: 16GB
- **Storage**: 50GB SSD
- **GPU**: None (CPU-only fallback)

#### **Recommended Requirements**
- **CPU**: 12+ cores, 3.5GHz+
- **RAM**: 32GB
- **Storage**: 100GB NVMe SSD
- **GPU**: NVIDIA RTX 3080/4070 (12GB+ VRAM)

#### **Optimal Requirements**
- **CPU**: 16+ cores, 4.0GHz+
- **RAM**: 64GB
- **Storage**: 200GB NVMe SSD
- **GPU**: NVIDIA RTX 4080/4090 (16GB+ VRAM)

---

## 🔄 **Fallback Strategy**

### **Multi-Tier Fallback System**
```python
class VoiceEngineManager:
    def __init__(self):
        self.fallback_chain = {
            "stt": [
                ("whisper_local_gpu", "gpu"),
                ("whisper_local_cpu", "cpu"),
                ("vosk", "cpu"),
                ("whisper_api", "api"),
                ("google_api", "api")
            ],
            "tts": [
                ("coqui_gpu", "gpu"),
                ("coqui_cpu", "cpu"),
                ("festival", "cpu"),
                ("elevenlabs_api", "api"),
                ("espeak", "cpu")
            ]
        }
    
    async def process_with_fallback(self, task_type, *args, **kwargs):
        for engine_name, engine_type in self.fallback_chain[task_type]:
            try:
                engine = self.get_engine(engine_name)
                if engine.is_available():
                    return await engine.process(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Engine {engine_name} failed: {e}")
                continue
        
        raise AllEnginesFailedError("All engines failed")
```

---

## 🚦 **Deployment Strategy**

### **Development Environment**
```yaml
# docker-compose.voice-dev.yml
version: '3.8'
services:
  voice-service-local:
    build: 
      context: ./voice_service
      dockerfile: Dockerfile.local
    environment:
      - VOICE_ENGINE_MODE=local
      - WHISPER_MODEL=medium
      - COQUI_MODEL=xtts_v2
      - ENABLE_GPU=true
    volumes:
      - ./data/models:/app/models
      - ./data/cache:/app/cache
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### **Production Environment**
```yaml
# kubernetes/voice-service-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: voice-service-local
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: voice-service
        image: mantrapath/voice-service:local
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: 1
          limits:
            memory: "32Gi"
            cpu: "8"
            nvidia.com/gpu: 1
        volumeMounts:
        - name: models-storage
          mountPath: /app/models
        - name: cache-storage
          mountPath: /app/cache
```

---

## 📊 **Cost Analysis**

### **Current API Costs (Monthly)**
Costs tied to external APIs eliminated by local deployment; operational cost is compute only.
- **ElevenLabs TTS**: $0.18/1000 characters → ~$540/month (3M characters)
- **Total Monthly**: ~$720

### **Self-Hosted Costs (One-time + Monthly)**
- **Hardware (RTX 4080)**: $1,200 (one-time)
- **Storage (1TB SSD)**: $100 (one-time)
- **Monthly Power**: ~$50
- **Total First Year**: $1,900
- **ROI**: Break-even in 3 months

### **Cost Benefits**
- ✅ **60-80% cost reduction** after initial setup
- ✅ **No quota limitations**
- ✅ **Predictable costs**
- ✅ **Better privacy and security**

---

## 🔐 **Security & Privacy Benefits**

### **Data Privacy**
- ✅ Audio never leaves your infrastructure
- ✅ No third-party API calls for sensitive content
- ✅ GDPR/HIPAA compliance ready
- ✅ Full audit trail control

### **Security**
- ✅ No external API key management
- ✅ Reduced attack surface
- ✅ Air-gapped deployment possible
- ✅ Custom security policies

---

## 📈 **Scalability Plan**

### **Horizontal Scaling**
```python
# Load balancer configuration
VOICE_SERVICE_INSTANCES = [
    {
        "gpu": "rtx_4080",
        "capacity": "high",
        "models": ["whisper_large", "coqui_xtts"]
    },
    {
        "gpu": "rtx_3080", 
        "capacity": "medium",
        "models": ["whisper_medium", "festival"]
    },
    {
        "gpu": None,
        "capacity": "low", 
        "models": ["vosk", "espeak"]
    }
]
```

### **Auto-scaling Rules**
- **Scale up**: >80% GPU utilization for 5 minutes
- **Scale down**: <30% GPU utilization for 15 minutes
- **Max instances**: 5
- **Min instances**: 2

---

## 🎯 **Success Metrics**

### **Performance KPIs**
- **Latency**: <5 seconds for STT, <8 seconds for TTS
- **Accuracy**: >90% for STT, >85% naturalness for TTS
- **Availability**: >99.5% uptime
- **Cost**: <$200/month operational costs

### **Quality KPIs**
- **Word Error Rate (WER)**: <10% for primary languages
- **Mean Opinion Score (MOS)**: >4.0 for TTS quality
- **User Satisfaction**: >90% positive feedback

---

## 🛣️ **Roadmap**

### **Phase 1: Foundation (Weeks 1-4)**
- ✅ Local Whisper implementation
- ✅ Coqui TTS integration
- ✅ Basic fallback system
- ✅ Performance monitoring

### **Phase 2: Enhancement (Weeks 5-8)**
- ✅ Voice cloning capabilities
- ✅ Emotion analysis integration
- ✅ Multi-language optimization
- ✅ Caching system

### **Phase 3: Scale (Weeks 9-12)**
- ✅ Kubernetes deployment
- ✅ Auto-scaling implementation
- ✅ Advanced monitoring
- ✅ Performance optimization

### **Phase 4: Innovation (Weeks 13-16)**
- ✅ Custom model fine-tuning
- ✅ Real-time streaming
- ✅ Advanced voice features
- ✅ ML pipeline automation

---

## 📝 **Next Steps**

### **Immediate Actions (This Week)**
1. **Hardware Assessment**: Evaluate current GPU capabilities
2. **Model Download**: Start downloading Whisper and Coqui models
3. **Environment Setup**: Prepare development environment
4. **Proof of Concept**: Implement basic local Whisper

### **Week 1 Deliverables**
1. Local Whisper engine integrated
2. Basic TTS fallback (Festival/eSpeak)
3. Performance baseline established
4. Documentation updated

### **Decision Points**
- **GPU Budget**: Determine hardware investment level
- **Model Selection**: Choose optimal model sizes for your use case
- **Deployment Strategy**: Docker vs Kubernetes vs bare metal
- **Monitoring Tools**: Select observability stack

---

## 🔧 **Technical Implementation Files**

The following files need to be created/modified:

1. **`engines/whisper_local_engine.py`** - Local Whisper implementation
2. **`engines/coqui_tts_engine.py`** - Coqui TTS implementation  
3. **`engines/vosk_engine.py`** - Vosk STT implementation
4. **`engines/festival_tts_engine.py`** - Festival TTS implementation
5. **`services/model_manager.py`** - Model lifecycle management
6. **`config/local_models_config.yaml`** - Model configuration
7. **`docker/Dockerfile.local`** - Local model container
8. **`scripts/download_models.py`** - Model download automation
9. **`monitoring/model_metrics.py`** - Performance monitoring
10. **`requirements_local.txt`** - Local model dependencies

---

This plan enables full independence from external API quotas while improving performance and reducing recurring costs. The self-hosted approach gives complete control over the voice processing pipeline with enterprise-grade reliability.

Would you like me to start implementing any specific part of this plan?
