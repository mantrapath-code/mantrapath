# Models Service

## Description

The Models Service is the centralized artificial intelligence model management and inference hub of the MantraPath platform. This service manages, serves, and provides inference capabilities for Speech-to-Text (STT), Text-to-Speech (TTS), Natural Language Processing (NLP), and other AI models used across the platform. It acts as the single source of truth for all AI model operations, ensuring consistent, optimized, and scalable AI capabilities throughout the MantraPath ecosystem.

This service solves the challenge of AI model management in a distributed microservices architecture. By centralizing model loading, inference, and management, it eliminates redundant model deployments, provides consistent AI capabilities across services, and enables efficient resource utilization while maintaining high performance and reliability.

## Table of Contents

- [Installation / Setup](#installation--setup)
- [Usage](#usage)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)
- [License](#license)
- [Contact / Author Info](#contact--author-info)
- [FAQ / Troubleshooting](#faq--troubleshooting)
- [Future Implementation](#future-implementation)

## Installation / Setup

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- GPU support recommended (NVIDIA CUDA) for optimal performance
- Sufficient storage for AI models (10-50GB depending on models)
- High-performance CPU for inference operations
- Redis (for model caching and job queuing)

### System Dependencies

```bash
# Audio processing libraries
sudo apt-get update
sudo apt-get install -y ffmpeg libsndfile1 portaudio19-dev

# For TTS engine
sudo apt-get install -y espeak espeak-data libespeak-dev
```

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/models_service
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download initial models:**
   ```bash
   ./start_simple.sh
   ```

### Configuration

- Environment variables configuration:
  ```bash
  cp .env.example .env
  nano .env
  ```
- Key variables include `MODELS_DIR`, `MODELS_SERVICE_MODE`, `MODELS_PRELOAD_LIST`, GPU configuration, and inference optimization settings.

## Usage

The Models Service provides AI model inference capabilities through REST API endpoints.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8080 --reload
  ```

- **Running in minimal mode:**
  ```bash
  MODELS_SERVICE_MODE=minimal python main.py
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d models_service
  ```

- **Speech-to-Text inference:**
  ```bash
  curl -X POST "http://localhost:8080/api/v1/stt/transcribe" \
       -F "audio=@audio_file.wav" \
       -F "model=whisper-base"
  ```

- **Text-to-Speech synthesis:**
  ```bash
  curl -X POST "http://localhost:8080/api/v1/tts/synthesize" \
       -H "Content-Type: application/json" \
       -d '{"text":"Hello world","voice":"en-us","model":"coqui-tts"}'
  ```

- **NLP inference:**
  ```bash
  curl -X POST "http://localhost:8080/api/v1/nlp/analyze" \
       -H "Content-Type: application/json" \
       -d '{"text":"I am feeling great today","task":"emotion_detection"}'
  ```

- **Model status:**
  ```bash
  curl -X GET "http://localhost:8080/api/v1/models/status"
  ```

- **API Documentation:**
  Interactive API documentation at `http://localhost:8080/docs`

## Features

- **Multi-Model Support:** STT (Whisper, Vosk), TTS (Coqui TTS, gTTS, pyttsx3), NLP (Transformers-based models)
- **Dynamic Model Loading:** On-demand model loading and unloading for efficient resource management
- **GPU Acceleration:** Automatic GPU detection and utilization for faster inference
- **Model Caching:** Intelligent model caching and memory management
- **Batch Processing:** Efficient batch inference for high-throughput scenarios
- **Model Management:** Download, update, and version management of AI models
- **Translation Services:** Multi-language text translation capabilities
- **Text Generation:** Advanced text generation using state-of-the-art language models
- **Audio Processing:** Comprehensive audio preprocessing and postprocessing
- **Performance Monitoring:** Real-time inference performance and resource monitoring
- **Minimal Mode:** Lightweight mode for development and resource-constrained environments
- **Background Processing:** Asynchronous model operations for non-blocking performance

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **AI/ML Frameworks:** PyTorch (optional), Transformers, OpenAI Whisper
- **Audio Processing:** Librosa 0.10.1, SoundFile 0.12.1, PyDub 0.25.1
- **Speech Recognition:** OpenAI Whisper 20231117, Vosk 0.3.45
- **Text-to-Speech:** Coqui TTS 0.22.0, gTTS 2.4.0, pyttsx3 2.90
- **Configuration:** Pydantic Settings 2.1.0
- **Caching:** Redis 5.0.1 for model and inference caching
- **Monitoring:** Prometheus client, Structlog for comprehensive logging
- **Database:** SQLAlchemy 2.0.23 for model metadata
- **File Operations:** Aiofiles for asynchronous file handling
- **System Monitoring:** PSUtil 5.9.8 for resource monitoring
- **Containerization:** Docker

## Contributing

Contributions to enhance AI model capabilities are highly valued:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-ai-model`)
3. Focus on model performance, accuracy, and resource efficiency
4. Add comprehensive tests for new models and inference paths
5. Ensure proper GPU utilization and memory management
6. Update model documentation and performance benchmarks
7. Submit a pull request with detailed model evaluation metrics

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"Model loading fails with GPU errors"**: Verify CUDA installation and GPU compatibility. Check GPU memory availability.
- **"STT transcription quality poor"**: Ensure audio quality is sufficient and try different Whisper model sizes.
- **"TTS synthesis slow"**: Consider using lighter TTS models or enabling GPU acceleration for Coqui TTS.
- **"Out of memory errors"**: Reduce batch sizes, enable model unloading, or use minimal mode for development.

## Future Implementation

- **Model Fine-tuning:** Custom model training and fine-tuning capabilities for domain-specific tasks
- **Distributed Inference:** Multi-node model serving for high-throughput scenarios
- **Model Quantization:** Model optimization techniques for faster inference and reduced memory usage
- **Real-time Streaming:** Real-time audio streaming for live STT and TTS applications
- **Advanced NLP Models:** Integration of latest language models and specialized mental health NLP models
- **Edge Deployment:** Lightweight models optimized for edge computing and mobile deployment