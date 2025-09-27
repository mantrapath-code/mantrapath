# AI Event Processor Service

## Description

The AI Event Processor Service is a sophisticated real-time AI processing pipeline that forms the intelligence backbone of the MantraPath platform. This service processes events from across all microservices, applying advanced machine learning models to understand user emotions, predict intervention needs, and provide cultural intelligence. It transforms raw user interactions into actionable insights that drive personalized mental health support.

This service solves the critical challenge of making sense of complex user behavioral data in real-time. By processing events through multiple AI models simultaneously, it enables proactive mental health interventions, culturally-sensitive responses, and personalized user experiences that adapt to individual needs and cultural contexts.

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
- GPU support recommended for ML models (NVIDIA CUDA)
- Redis (for caching and job queues)
- Access to Models Service for AI model inference

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/ai_event_processor
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

4. **Download required ML models:**
   ```bash
   python -c "import nltk; nltk.download('vader_lexicon')"
   python -m spacy download en_core_web_sm
   ```

### Configuration

- Environment variables are managed in a `.env` file:
  ```bash
  cp .env.example .env
  nano .env
  ```
- Key variables include `AI_EVENT_PROCESSOR_PORT`, `REDIS_URL`, `MODELS_SERVICE_URL`, and AI model configuration settings.

## Usage

The AI Event Processor runs as a background service, processing events in real-time and providing AI insights through REST API endpoints.

- **Running the service locally:**
  ```bash
  python main.py
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d ai_event_processor
  ```

- **Health Check:**
  ```bash
  curl http://localhost:8014/health
  ```

- **API Documentation:**
  Interactive Swagger UI available at `http://localhost:8014/docs`

## Features

- **Real-time Emotion Analysis:** Processes text, voice, and behavioral data to detect emotional states using advanced NLP models
- **Predictive Intervention Engine:** Uses machine learning to predict when users might need mental health support
- **Cultural Intelligence Processing:** Adapts responses and recommendations based on cultural context and preferences
- **Multi-modal AI Processing:** Handles text, voice, and behavioral event data through specialized processors
- **Structured Logging:** Comprehensive logging with structured JSON format for observability
- **Health Monitoring:** Built-in health checks for all AI components
- **Event-driven Architecture:** Processes events asynchronously for high throughput and low latency
- **Model Integration:** Seamless integration with the Models Service for AI inference

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **AI/ML:** PyTorch 2.1.1, Transformers 4.36.2, Scikit-learn 1.3.2
- **NLP:** NLTK 3.8.1, spaCy 3.7.2
- **Cultural Intelligence:** LangDetect, Polyglot
- **Data Processing:** NumPy, Pandas
- **Caching:** Redis 5.0.1
- **Monitoring:** Prometheus, Structlog
- **Testing:** Pytest, Pytest-asyncio
- **Containerization:** Docker

## Contributing

We welcome contributions to enhance the AI capabilities! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-ai-model`)
3. Ensure all AI models are properly tested
4. Add comprehensive tests for new functionality
5. Update documentation for new AI features
6. Submit a pull request with detailed description

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"AI models not loading"**: Ensure you have sufficient memory and GPU resources. Check that model files are properly downloaded.
- **"High processing latency"**: Verify GPU availability and consider scaling horizontally. Check Redis connectivity for caching.
- **"Emotion analysis accuracy issues"**: Ensure input text is properly preprocessed and models are updated to latest versions.

## Future Implementation

- **Advanced Multimodal Models:** Integration of vision-language models for processing images and videos
- **Real-time Model Training:** Continuous learning from user feedback to improve prediction accuracy
- **Explainable AI:** Adding model interpretability features to explain AI decisions to users and clinicians
- **Edge Computing:** Deploying lightweight models for client-side processing to reduce latency
- **Federated Learning:** Privacy-preserving model training across distributed user data