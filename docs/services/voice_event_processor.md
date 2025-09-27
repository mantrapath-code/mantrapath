# Voice Event Processor Service

## Description

The Voice Event Processor Service is the real-time voice analytics and event processing engine of the MantraPath platform. This service handles live voice stream processing, voice activity detection, emotion recognition from voice patterns, and real-time event broadcasting. It processes continuous audio streams to detect speech events, emotional states, and behavioral patterns, providing immediate insights that enhance the conversational AI experience and enable proactive mental health support.

This service solves the challenge of understanding emotional and behavioral context from voice interactions in real-time. By analyzing voice patterns, detecting emotional states, and processing speech events as they occur, it enables the platform to provide more empathetic, contextually-aware responses and proactive interventions based on vocal cues and emotional indicators.

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
- Audio processing capabilities (microphone access for testing)
- WebSocket support for real-time streaming
- GPU support recommended for emotion recognition models

### System Dependencies

```bash
# Audio processing libraries
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio

# For advanced audio processing
sudo apt-get install -y ffmpeg libsndfile1
```

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/voice_event_processor
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
- Key variables include audio processing settings, emotion recognition model configuration, and WebSocket parameters.

## Usage

The Voice Event Processor provides real-time voice analysis through WebSocket connections and REST API endpoints.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8016 --reload
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d voice_event_processor
  ```

- **WebSocket connection for real-time processing:**
  ```javascript
  const ws = new WebSocket('ws://localhost:8016/ws/voice-stream/user123');
  
  // Send audio data
  ws.send(audioBuffer);
  
  // Receive voice events
  ws.onmessage = (event) => {
    const voiceEvent = JSON.parse(event.data);
    console.log('Voice event:', voiceEvent);
  };
  ```

- **Configure voice stream:**
  ```bash
  curl -X POST "http://localhost:8016/configure-stream" \
       -H "Content-Type: application/json" \
       -d '{"sample_rate":16000,"chunk_size":1024,"vad_sensitivity":0.7,"emotion_analysis":true}'
  ```

- **Get processing status:**
  ```bash
  curl -X GET "http://localhost:8016/status"
  ```

- **API Documentation:**
  Interactive API documentation at `http://localhost:8016/docs`

## Features

- **Real-Time Voice Streaming:** WebSocket-based continuous audio stream processing
- **Voice Activity Detection (VAD):** Intelligent detection of speech vs. silence with configurable sensitivity
- **Emotion Recognition:** Advanced emotion analysis from voice patterns and prosodic features
- **Event Broadcasting:** Real-time broadcasting of voice events to connected clients
- **Connection Management:** Robust WebSocket connection management with automatic reconnection support
- **Multi-Client Support:** Concurrent processing of multiple voice streams
- **Configurable Processing:** Customizable audio processing parameters per client
- **Low Latency Processing:** Optimized for real-time applications with minimal delay
- **Audio Quality Analysis:** Analysis of audio quality and noise levels
- **Stream Health Monitoring:** Continuous monitoring of stream quality and processing performance
- **Event Filtering:** Intelligent filtering and aggregation of voice events
- **Scalable Architecture:** Designed to handle multiple concurrent voice streams efficiently

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **Real-Time Communication:** WebSockets for live audio streaming
- **Audio Processing:** PyAudio, LibROSA, SoundFile for audio analysis
- **Voice Activity Detection:** Custom VAD algorithms with machine learning
- **Emotion Recognition:** Deep learning models for emotion analysis from voice
- **Connection Management:** Advanced WebSocket connection management
- **Event System:** Real-time event broadcasting and filtering
- **Configuration:** Pydantic for stream configuration management
- **Logging:** Structured logging for voice processing events
- **Monitoring:** Performance monitoring for real-time processing metrics
- **Containerization:** Docker with audio processing support

## Contributing

Contributions to enhance voice processing capabilities are highly valued:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhanced-emotion-detection`)
3. Focus on real-time performance and accuracy
4. Add comprehensive tests for voice processing algorithms
5. Ensure low latency and high throughput
6. Update audio processing models and algorithms
7. Submit a pull request with detailed performance analysis

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"WebSocket connections dropping frequently"**: Check network stability and audio buffer sizes. Ensure proper WebSocket keepalive configuration.
- **"Voice activity detection not accurate"**: Adjust VAD sensitivity parameters based on audio environment and user voice characteristics.
- **"High processing latency"**: Optimize audio chunk sizes and processing algorithms. Consider GPU acceleration for emotion recognition.
- **"Emotion recognition inaccurate"**: Verify audio quality and ensure sufficient audio samples for accurate emotion analysis.

## Future Implementation

- **Advanced Emotion Models:** Deep learning models with improved emotion recognition accuracy
- **Speaker Identification:** Voice biometric identification for personalized processing
- **Multi-Language Voice Analysis:** Language-specific voice processing and emotion recognition
- **Real-Time Stress Detection:** Advanced stress and mental state detection from voice patterns
- **Voice Coaching:** Real-time feedback for voice-based therapeutic exercises
- **Integration with Wearables:** Correlation with physiological data from wearable devices