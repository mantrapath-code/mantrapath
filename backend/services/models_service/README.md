# MantraPath Models Service

## 🎯 Overview

The MantraPath Models Service is a self-hosted, open-source solution for Text-to-Speech (TTS) and Speech-to-Text (STT) capabilities, specifically designed to support Indian regional languages while avoiding dependency on external APIs like OpenAI.

## ✨ Features

### 🎤 Speech-to-Text (STT)
- **OpenAI Whisper** - Multi-language support including Hindi, Bengali, Telugu, Tamil
- **Vosk** - Offline STT with dedicated models for Indian languages  
- **Wav2Vec2** - Facebook's transformer-based STT models
- **Language Support**: Hindi, Bengali, Telugu, Tamil, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, Assamese

### 🔊 Text-to-Speech (TTS)
- **Google TTS (gTTS)** - High-quality online synthesis
- **Coqui TTS** - Advanced neural TTS with voice cloning
- **Festival & eSpeak** - Lightweight offline TTS engines
- **Voice Cloning** - Custom voice synthesis capabilities

### 🧠 Natural Language Processing
- **Sentiment Analysis** - Text emotion detection
- **Language Translation** - Multi-language translation
- **Text Embeddings** - Semantic text representations

### 🏗️ Architecture
- **FastAPI** - Modern, high-performance API framework
- **Docker** - Containerized deployment
- **Redis** - Caching and job queues
- **Async Processing** - Non-blocking operations
- **Health Monitoring** - Service status and diagnostics

## 🚀 Quick Start

### Prerequisites

- **Docker** (version 20.0+)
- **Docker Compose** (version 2.0+)
- **10GB+ disk space** (for model storage)
- **4GB+ RAM** (recommended)

### Installation

1. **Clone and navigate**:
   ```bash
   cd backend/services/models_service
   ```

2. **Run setup script**:
   ```bash
   ./setup.sh
   ```

3. **Verify installation**:
   ```bash
   curl -s http://localhost:8085/health | python3 -m json.tool
   ```

### Manual Setup (Alternative)

```bash
# Build and start services
docker-compose build
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f models-service
```

## 📡 API Endpoints

### Core Services

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/docs` | GET | Interactive API documentation |
| `/models/available` | GET | List all available models |
| `/models/loaded` | GET | List currently loaded models |

### Speech-to-Text (STT)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/stt/transcribe` | POST | Transcribe audio to text |
| `/api/v1/stt/languages` | GET | Supported STT languages |

### Text-to-Speech (TTS)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/tts/synthesize` | POST | Convert text to speech |
| `/api/v1/tts/clone-voice` | POST | Clone voice from sample |
| `/api/v1/tts/languages` | GET | Supported TTS languages |
| `/api/v1/tts/voices/{language}` | GET | Available voices for language |

### Model Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/models/download` | POST | Download model |
| `/api/v1/models/download/{name}/progress` | GET | Download progress |
| `/api/v1/models/{name}` | DELETE | Remove model |

## 💾 Model Management

### Downloading Models

```bash
# Download Whisper tiny model (39MB)
curl -X POST "http://localhost:8085/api/v1/models/download" \
     -H "Content-Type: application/json" \
     -d '{"model_name": "whisper_tiny"}'

# Download Hindi Vosk model (45MB) 
curl -X POST "http://localhost:8085/api/v1/models/download" \
     -H "Content-Type: application/json" \
     -d '{"model_name": "vosk_hi_small"}'
```

### Available Models

#### STT Models
- **whisper_tiny** (39MB) - Fast, multi-language
- **whisper_small** (244MB) - Better quality
- **whisper_medium** (769MB) - High quality
- **vosk_hi_small** (45MB) - Hindi, CPU-optimized
- **wav2vec2_hi** (1.2GB) - Hindi, transformer-based

#### TTS Models  
- **gtts** - Google TTS (online)
- **coqui_xtts_v2** (6GB) - Advanced voice cloning
- **espeak_hi** (10MB) - Basic Hindi TTS
- **festival_hi** (50MB) - Hindi Festival TTS

## 🔧 Usage Examples

### Speech-to-Text

```bash
# Transcribe audio file
curl -X POST "http://localhost:8085/api/v1/stt/transcribe" \
     -F "audio=@audio.wav" \
     -F "language=hi" \
     -F "model=whisper_tiny"
```

### Text-to-Speech

```bash
# Synthesize Hindi text
curl -X POST "http://localhost:8085/api/v1/tts/synthesize" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "नमस्ते, यह एक परीक्षण है",
       "language": "hi",
       "model": "gtts"
     }' \
     --output output.wav
```

### Model Information

```bash
# List available models
curl -s http://localhost:8085/models/available | python3 -m json.tool

# Check supported languages
curl -s http://localhost:8085/api/v1/stt/languages | python3 -m json.tool
```

## 🌍 Language Support

### Indian Languages
- **Hindi (hi)** - Complete STT/TTS support
- **Bengali (bn)** - STT via Wav2Vec2, TTS via Coqui
- **Telugu (te)** - STT via Wav2Vec2, TTS via eSpeak
- **Tamil (ta)** - STT via Wav2Vec2, TTS via eSpeak  
- **Marathi (mr)** - STT via Vosk, TTS via eSpeak
- **Gujarati (gu)** - STT via Vosk, TTS via eSpeak
- **Kannada (kn)** - STT via Vosk, TTS via eSpeak
- **Malayalam (ml)** - STT via Vosk, TTS via eSpeak
- **Punjabi (pa)** - STT via Vosk, TTS via eSpeak
- **Odia (or)** - STT via Vosk, TTS via eSpeak
- **Assamese (as)** - STT via Vosk, TTS via eSpeak

### International Languages
- **English (en)** - Full support all engines
- **Spanish (es)** - Whisper STT, multiple TTS
- **French (fr)** - Whisper STT, multiple TTS
- **German (de)** - Whisper STT, multiple TTS

## 🐳 Docker Configuration

### Services

1. **models-service** (Port 8085)
   - FastAPI application
   - Model management and inference
   - Health monitoring

2. **redis** (Port 6385)  
   - Caching layer
   - Job queues
   - Session storage

3. **model-downloader** (On-demand)
   - Automated model downloads
   - Progress tracking
   - Cleanup tasks

### Volumes

- `./models:/app/models` - Model storage
- `./cache:/app/cache` - Cache data
- `./logs:/app/logs` - Service logs

## 🔧 Configuration

### Environment Variables

```env
# Service Configuration
SERVICE_PORT=8080
DEBUG=false
USE_GPU=true
MAX_CONCURRENT_REQUESTS=10

# Model Defaults
DEFAULT_STT_MODEL=whisper_medium
DEFAULT_TTS_MODEL=gtts
WHISPER_MODEL_SIZE=medium

# API Fallbacks
ENABLE_API_FALLBACK=true
OPENAI_API_KEY=your_key_here
GOOGLE_CLOUD_API_KEY=your_key_here
```

### Docker Compose Customization

```yaml
# To change ports
services:
  models-service:
    ports:
      - "8086:8080"  # Change from 8085 to 8086
  
  redis:
    ports:
      - "6386:6379"  # Change from 6385 to 6386
```

## 🛠️ Management Commands

### Service Control

```bash
# Start services
docker-compose up -d

# Stop services  
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f models-service

# Check status
docker-compose ps
```

### Model Management

```bash
# List downloaded models
ls -la models/

# Clear cache
rm -rf cache/*

# Check disk usage
du -sh models/ cache/
```

### Health Monitoring

```bash
# Service health
curl -s http://localhost:8085/health

# Container health
docker-compose ps

# Resource usage
docker stats
```

## 🚨 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using port 8085
lsof -i :8085

# Use different port in docker-compose.yml
ports:
  - "8086:8080"
```

#### Model Download Issues
```bash
# Check download progress
curl -s http://localhost:8085/api/v1/models/download/whisper_tiny/progress

# Check available space
df -h .

# Clear failed downloads
rm -rf models/partial_downloads/
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Reduce concurrent requests
# Edit docker-compose.yml environment:
MAX_CONCURRENT_REQUESTS=5

# Use smaller models
# whisper_tiny instead of whisper_large
```

#### Service Not Starting
```bash
# Check detailed logs
docker-compose logs models-service

# Rebuild images
docker-compose build --no-cache

# Check Python environment
docker-compose exec models-service python --version
```

### Debug Mode

```bash
# Enable debug logging
docker-compose up -d --env DEBUG=true

# Access container shell
docker-compose exec models-service bash

# Test Python imports
docker-compose exec models-service python -c "import whisper; print('OK')"
```

## 🔗 Integration

### With Main Backend

```python
import requests

# STT Example
def transcribe_audio(audio_file, language="hi"):
    files = {"audio": open(audio_file, "rb")}
    data = {"language": language, "model": "whisper_tiny"}
    response = requests.post(
        "http://localhost:8085/api/v1/stt/transcribe",
        files=files, 
        data=data
    )
    return response.json()

# TTS Example  
def synthesize_text(text, language="hi"):
    data = {
        "text": text,
        "language": language,
        "model": "gtts"
    }
    response = requests.post(
        "http://localhost:8085/api/v1/tts/synthesize",
        json=data
    )
    return response.content  # Audio bytes
```

### With Frontend

```javascript
// STT Example
async function transcribeAudio(audioBlob, language = 'hi') {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    formData.append('language', language);
    formData.append('model', 'whisper_tiny');
    
    const response = await fetch('/api/v1/stt/transcribe', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}

// TTS Example
async function synthesizeText(text, language = 'hi') {
    const response = await fetch('/api/v1/tts/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: text,
            language: language,
            model: 'gtts'
        })
    });
    
    return await response.blob(); // Audio blob
}
```

## 📊 Performance

### Benchmarks

| Model | Language | Size | CPU Time | GPU Time | Quality |
|-------|----------|------|----------|----------|---------|
| whisper_tiny | hi | 39MB | ~2s | ~0.5s | Good |
| whisper_small | hi | 244MB | ~5s | ~1s | Better |
| vosk_hi_small | hi | 45MB | ~1s | N/A | Fast |
| gtts | hi | Online | ~3s | N/A | High |

### Optimization Tips

1. **Use appropriate model sizes** for your needs
2. **Enable GPU acceleration** when available  
3. **Cache frequently used models** in memory
4. **Use Redis** for response caching
5. **Monitor resource usage** and adjust limits

## 🔒 Security

### Access Control
- API rate limiting via Redis
- Input validation and sanitization
- File upload restrictions
- Container isolation

### Best Practices
- Run containers as non-root user
- Use secure network configurations
- Regular security updates
- Monitor for unusual activity

## 📈 Monitoring

### Metrics Available
- Request count and latency
- Model load times
- Memory and CPU usage
- Error rates by endpoint
- Cache hit rates

### Health Checks
- Service availability
- Model status
- Redis connectivity
- Disk space monitoring

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd backend/services/models_service

# Install dependencies  
pip install -r requirements.txt

# Run in development mode
uvicorn main:app --reload --port 8080
```

### Adding New Models

1. Update `config/settings.py` with model configuration
2. Implement model loader in `services/`
3. Add API endpoints in `routes/`
4. Update documentation and tests

## 📄 License

This project is part of MantraPath and follows the main project license.

## 🆘 Support

For issues and support:
1. Check this documentation
2. Review Docker logs: `docker-compose logs`
3. Check GitHub issues
4. Contact development team

---

**MantraPath Models Service** - Empowering voice technology in Indian languages 🇮🇳
