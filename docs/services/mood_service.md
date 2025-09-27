# Mood Service

## Description

The Mood Service is the emotional intelligence core of the MantraPath platform, providing AI-powered emotion detection, mood tracking, and emotional analytics. This service uses advanced machine learning models, including the GoEmotions AI model, to analyze user emotions from text, voice, and behavioral data. It maintains comprehensive mood histories, provides real-time emotion analysis, and integrates with other services to enable emotion-aware experiences throughout the platform.

This service solves the critical challenge of understanding and tracking emotional states in mental health applications. By providing accurate, real-time emotion detection and comprehensive mood analytics, it enables personalized mental health support, mood-aware content delivery, and proactive intervention capabilities based on emotional patterns and trends.

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
- PostgreSQL database
- Redis (for caching and real-time operations)
- GPU support recommended for ML model inference
- Access to Memory Service for context integration

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/mood_service
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

4. **Download AI models:**
   ```bash
   python -c "from transformers import pipeline; pipeline('text-classification', model='j-hartmann/emotion-english-distilroberta-base')"
   ```

### Configuration

- Environment variables configuration:
  ```bash
  cp .env.example .env
  nano .env
  ```
- Key variables include `DATABASE_URL`, `REDIS_URL`, emotion detection model settings, and Memory Service integration configuration.

## Usage

The Mood Service provides comprehensive emotion analysis and mood tracking through REST API endpoints.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8003 --reload
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d mood_service
  ```

- **Analyze emotion from text:**
  ```bash
  curl -X POST "http://localhost:8003/api/v1/mood/analyze" \
       -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"text":"I am feeling really anxious about tomorrow","context":"journal_entry"}'
  ```

- **Record mood entry:**
  ```bash
  curl -X POST "http://localhost:8003/api/v1/mood/entries" \
       -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"mood":"anxious","intensity":7,"notes":"Work stress","activities":["work","meeting"]}'
  ```

- **Get mood history:**
  ```bash
  curl -X GET "http://localhost:8003/api/v1/mood/history?days=30" \
       -H "Authorization: Bearer <token>"
  ```

- **Get mood insights:**
  ```bash
  curl -X GET "http://localhost:8003/api/v1/mood/insights" \
       -H "Authorization: Bearer <token>"
  ```

- **API Documentation:**
  Interactive API documentation at `http://localhost:8003/docs`

## Features

- **AI-Powered Emotion Detection:** Advanced emotion analysis using GoEmotions and other state-of-the-art models
- **Multi-Modal Analysis:** Emotion detection from text, voice patterns, and behavioral data
- **Mood Tracking:** Comprehensive mood logging with intensity, activities, and contextual information
- **Real-Time Analytics:** Instant emotion analysis and mood pattern recognition
- **Memory Service Integration:** Seamless integration with Memory Service for enhanced context awareness
- **Mood Pattern Analysis:** Long-term trend analysis and pattern recognition in emotional states
- **Contextual Awareness:** Context-sensitive emotion analysis based on user activities and history
- **Mood Insights:** AI-generated insights about emotional patterns, triggers, and trends
- **Crisis Detection:** Early warning system for concerning emotional patterns
- **Personalized Analytics:** Customized mood analytics based on individual user patterns
- **Privacy-Preserving:** Secure emotion analysis with user privacy protection
- **Cross-Service Integration:** Mood data available to other services for emotion-aware features

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **Database:** PostgreSQL with SQLAlchemy 2.0.23 ORM
- **AI/ML:** Transformers 4.35.2, PyTorch 2.1.1, NumPy (<2.0.0), SciPy
- **NLP Models:** GoEmotions, DistilRoBERTa-based emotion detection models
- **Tokenization:** Tokenizers 0.15.0 for efficient text processing
- **Caching:** Redis 5.0.1 for mood data caching and real-time operations
- **Authentication:** JWT token validation through shared auth system
- **HTTP Client:** HTTPX 0.25.2 for service integration
- **Configuration:** Pydantic Settings 2.0.3 for configuration management
- **Security:** Python-JOSE with cryptography, Passlib with BCrypt
- **Containerization:** Docker

## Contributing

Contributions to enhance emotion analysis and mood tracking are highly valued:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/advanced-emotion-analysis`)
3. Focus on emotion detection accuracy and user experience
4. Add comprehensive tests for emotion analysis algorithms
5. Ensure privacy and ethical considerations in emotion processing
6. Update emotion models and validation metrics
7. Submit a pull request with detailed emotion analysis performance evaluation

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"Emotion detection inaccurate"**: Verify model loading and check text preprocessing. Consider using different emotion models for specific contexts.
- **"Mood insights not generating"**: Ensure sufficient mood history data and check Memory Service integration.
- **"Performance slow with large text"**: Optimize text chunking and consider batch processing for large content analysis.
- **"Memory service integration failing"**: Verify Memory Service connectivity and authentication configuration.

## Future Implementation

- **Advanced Emotion Models:** Integration of multimodal emotion detection including voice tone and facial expressions
- **Personalized Emotion Models:** User-specific emotion detection models trained on individual patterns
- **Real-time Emotion Streaming:** Live emotion monitoring from continuous text and voice input
- **Clinical Integration:** Emotion analysis validated with clinical mental health assessments
- **Cultural Emotion Models:** Culturally-aware emotion detection considering cultural expression differences
- **Predictive Mood Modeling:** Predictive models for anticipating mood changes and emotional needs