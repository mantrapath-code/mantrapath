# Chatbot Service

## Description

The Chatbot Service is the conversational AI heart of the MantraPath platform, providing intelligent, context-aware mental health support through natural language interactions. This service integrates voice processing, multi-language support, mood awareness, and cultural intelligence to deliver personalized therapeutic conversations. It serves as the primary interface for users seeking immediate mental health guidance, emotional support, and platform navigation assistance.

This service solves the challenge of providing accessible, 24/7 mental health support that understands user context and emotional state. By integrating with all other platform services, it creates a comprehensive conversational experience that can access user mood data, journal entries, community interactions, and provide intelligent, culturally-sensitive responses tailored to individual needs.

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
- Access to Models Service for AI inference
- Voice Service integration
- Redis (optional, for conversation caching)

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/chatbot_service
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
- Key variables include `MODELS_SERVICE_URL`, `VOICE_SERVICE_URL`, `DATABASE_URL`, and conversation memory settings.

## Usage

The Chatbot Service provides both text and voice conversation capabilities through REST API endpoints.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8004 --reload
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d chatbot_service
  ```

- **Start a conversation:**
  ```bash
  curl -X POST "http://localhost:8004/chat/start" \
       -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"user_message":"I'm feeling anxious today"}'
  ```

- **Voice conversation:**
  ```bash
  curl -X POST "http://localhost:8004/voice/chat" \
       -H "Authorization: Bearer <token>" \
       -F "audio=@voice_message.wav"
  ```

- **API Documentation:**
  Interactive Swagger UI at `http://localhost:8004/docs`

## Features

- **Multi-Language Voice Support:** Voice input/output with automatic language detection
- **Context-Aware Conversations:** Integration with mood, journal, and community data for personalized responses
- **Cultural Intelligence:** Culturally-sensitive responses adapted to user background
- **Mood-Aware Responses:** Real-time mood analysis integration for appropriate conversation tone
- **Conversation Memory:** Persistent conversation history and context retention
- **Service Integration:** Seamless integration with all MantraPath services for comprehensive support
- **Action Orchestration:** Ability to trigger actions across services through conversation
- **Real-Time Voice Processing:** Live voice conversation capabilities with streaming responses
- **Sentiment Analysis:** Continuous emotional state monitoring during conversations
- **Crisis Detection:** Automatic identification of crisis situations with appropriate escalation
- **Therapeutic Techniques:** Integration of CBT, mindfulness, and other therapeutic approaches
- **Progress Tracking:** Conversation-based progress monitoring and insights

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **Database:** PostgreSQL with SQLAlchemy 2.0.23 ORM
- **AI Integration:** Models Service client for natural language processing
- **Voice Processing:** Voice Service integration for speech-to-text/text-to-speech
- **HTTP Client:** HTTPX 0.25.2 for service communication
- **Authentication:** JWT token validation through shared auth module
- **Logging:** Loguru for structured conversation logging
- **File Handling:** Aiofiles for voice file processing
- **Templates:** Jinja2 for response templating
- **Database Migrations:** Alembic for schema management
- **Containerization:** Docker

## Contributing

Contributions to enhance conversational AI capabilities are highly valued:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhanced-therapy-techniques`)
3. Implement improvements with focus on therapeutic effectiveness
4. Add comprehensive conversation flow tests
5. Ensure cultural sensitivity and accessibility
6. Update conversation templates and responses
7. Submit a pull request with detailed conversation examples

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"Chatbot responses are generic"**: Ensure user context services are running and accessible. Check mood and profile service integration.
- **"Voice processing not working"**: Verify Voice Service connectivity and audio file format compatibility.
- **"Cultural responses inappropriate"**: Review cultural intelligence configuration and user profile cultural settings.
- **"Conversation memory lost"**: Check database connectivity and conversation session persistence.

## Future Implementation

- **Advanced Therapeutic Protocols:** Implementation of structured therapy sessions (CBT, DBT, EMDR)
- **Multimodal Conversations:** Integration of images, documents, and other media in conversations
- **Group Therapy Facilitation:** AI-moderated group conversation capabilities
- **Specialized AI Models:** Fine-tuned models for specific mental health conditions
- **Real-time Emotion Recognition:** Advanced emotional state detection through voice and text analysis
- **Personalized Therapy Plans:** AI-generated, therapist-reviewed treatment recommendations