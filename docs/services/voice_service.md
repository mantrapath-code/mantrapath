# Voice Service

## Description

The Voice Service is the comprehensive voice processing hub of the MantraPath platform, providing clean, efficient speech-to-text (STT) and text-to-speech (TTS) capabilities through integration with the Models Service. This service enables voice-driven interactions throughout the platform, including voice journaling, spoken mood entries, voice-guided meditations, and conversational AI interactions. It serves as the primary interface for all voice-related functionality while maintaining optimal performance and reliability.

This service solves the challenge of providing consistent, high-quality voice processing across all platform interactions. By integrating seamlessly with the Models Service, it ensures that voice capabilities are available wherever needed while maintaining clean separation of concerns and optimal resource utilization.

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
- Access to Models Service for STT/TTS processing
- Audio processing capabilities
- WebSocket support for real-time voice streaming

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/voice_service
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

### Configuration

- Environment variables configuration:
  ```bash
  cp .env.example .env
  nano .env
  ```
- Key variables include `MODELS_SERVICE_URL`, audio processing settings, and voice quality parameters.

## Usage

The Voice Service provides clean voice processing capabilities through REST API endpoints with Models Service integration.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8011 --reload
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d voice_service
  ```

- **Speech to Text:**
  ```bash
  curl -X POST "http://localhost:8011/api/v1/voice/stt" \
       -F "audio=@recording.wav" \
       -F "language=en" \
       -F "model_preference=whisper-base"
  ```

- **Text to Speech:**
  ```bash
  curl -X POST "http://localhost:8011/api/v1/voice/tts" \
       -H "Content-Type: application/json" \
       -d '{"text":"Welcome to MantraPath. How are you feeling today?","language":"en","voice":"neutral"}'
  ```

- **Voice conversation:**
  ```bash
  curl -X POST "http://localhost:8011/api/v1/voice/conversation" \
       -F "audio=@question.wav" \
       -F "language=auto" \
       -F "context={\"mood\":\"calm\"}"
  ```

- **Models Service status:**
  ```bash
  curl -X GET "http://localhost:8011/api/v1/models/status"
  ```

- **API Documentation:**
  Comprehensive API documentation at `http://localhost:8011/docs`

## Features

- **Clean Models Service Integration:** Seamless integration with Models Service for all AI processing
- **High-Quality Speech Recognition:** Advanced STT with support for multiple languages and accents
- **Natural Text-to-Speech:** High-quality TTS with various voice options and emotional tones
- **Automatic Language Detection:** Smart detection of spoken language for multilingual support
- **Voice Quality Optimization:** Audio preprocessing and postprocessing for optimal quality
- **Streaming Support:** Real-time voice streaming capabilities for live interactions
- **Multiple Audio Formats:** Support for various audio formats (WAV, MP3, OGG, etc.)
- **Conversation Context:** Context-aware voice processing for natural conversations
- **Performance Optimization:** Efficient audio processing with minimal latency
- **Error Handling:** Robust error handling with graceful degradation
- **Health Monitoring:** Comprehensive health checks and service status monitoring
- **Clean Architecture:** Well-structured, maintainable codebase with clear separation of concerns

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **Models Integration:** Custom Models Service client for AI processing
- **Audio Processing:** Built-in audio handling and format conversion
- **HTTP Server:** Uvicorn for high-performance ASGI serving
- **File Handling:** Advanced file upload and processing capabilities
- **Configuration:** Environment-based configuration management
- **Logging:** Structured logging with configurable levels
- **Error Handling:** Comprehensive exception handling and user feedback
- **API Documentation:** Automatic OpenAPI documentation generation
- **Containerization:** Docker with optimized voice processing environment

## Contributing

Contributions to enhance voice processing capabilities are highly valued:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhanced-voice-quality`)
3. Focus on voice quality, performance, and user experience
4. Add comprehensive tests for voice processing functionality
5. Ensure proper integration with Models Service
6. Update voice processing workflows and documentation
7. Submit a pull request with detailed voice quality analysis

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"Models Service connection failed"**: Verify Models Service is running and accessible at the configured URL.
- **"Poor speech recognition quality"**: Check audio quality, format, and ensure proper microphone setup.
- **"TTS audio quality issues"**: Verify TTS model selection and audio output settings.
- **"High processing latency"**: Check Models Service performance and network connectivity.

## Future Implementation

- **Voice Biometrics:** Speaker identification and verification capabilities
- **Emotional Voice Synthesis:** TTS with emotional expression and personality
- **Real-Time Voice Effects:** Live voice processing with filters and effects
- **Advanced Conversation AI:** Context-aware conversational voice interactions
- **Voice Analytics:** Detailed voice pattern analysis and insights
- **Multi-Modal Integration:** Combined voice, text, and visual processing capabilities