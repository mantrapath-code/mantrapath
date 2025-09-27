# Proactive Assistance Engine Service

## Description

The Proactive Assistance Engine is the intelligent orchestration hub that coordinates existing AI capabilities into a cohesive, proactive mental health support system. This service analyzes user patterns, predicts needs, and delivers timely, contextually relevant, and culturally sensitive assistance before users explicitly request help. It integrates with all other MantraPath services to provide seamless, anticipatory support that enhances the user's mental wellness journey.

This service solves the challenge of making mental health support truly proactive rather than reactive. By analyzing user behavior patterns, mood trends, and contextual factors, it anticipates when users might need support and automatically triggers appropriate interventions, notifications, or content recommendations, creating a more supportive and responsive mental health platform.

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
- Redis (for real-time coordination)
- NATS messaging system
- Access to all MantraPath services for orchestration
- Models Service for AI inference

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/proactive_assistance_engine
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
- Key variables include `DATABASE_URL`, `REDIS_URL`, `NATS_URL`, service URLs for orchestration, and AI model configuration settings.

## Usage

The Proactive Assistance Engine operates primarily as a background orchestration service with API endpoints for monitoring and control.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8018 --reload
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d proactive_assistance_engine
  ```

- **Check assistance status:**
  ```bash
  curl -X GET "http://localhost:8018/health" \
       -H "Authorization: Bearer <token>"
  ```

- **Get user assistance evaluation:**
  ```bash
  curl -X GET "http://localhost:8018/assistance/evaluate/{user_id}" \
       -H "Authorization: Bearer <token>"
  ```

- **Trigger proactive assistance:**
  ```bash
  curl -X POST "http://localhost:8018/assistance/trigger" \
       -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"user_id":"user123","context":"mood_decline","priority":"high"}'
  ```

- **Voice-enabled assistance:**
  ```bash
  curl -X POST "http://localhost:8018/assistance/voice" \
       -H "Authorization: Bearer <token>" \
       -F "audio=@user_voice.wav" \
       -F "context=check_in"
  ```

- **API Documentation:**
  Interactive API documentation at `http://localhost:8018/docs`

## Features

- **Intelligent Orchestration:** Coordinates all existing AI capabilities into cohesive proactive assistance
- **Predictive Assistance:** Anticipates user needs based on behavior patterns and mood trends
- **Contextual Relevance:** Delivers assistance that is contextually appropriate and timely
- **Cultural Sensitivity:** Culturally-aware assistance that respects individual backgrounds and preferences
- **Multi-Service Integration:** Seamlessly integrates with Models Service for voice and multilingual support
- **Real-Time Coordination:** Real-time coordination through NATS messaging for immediate response
- **Assistance Evaluation:** Comprehensive evaluation of user assistance needs and effectiveness
- **Background Processing:** Continuous monitoring and analysis without user intervention
- **Priority Management:** Intelligent prioritization of assistance based on urgency and user state
- **Voice Integration:** Voice-enabled assistance through Models Service integration
- **Performance Monitoring:** Comprehensive monitoring with Prometheus metrics
- **Health Checks:** Kubernetes-ready health checks for production deployment

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **Database:** PostgreSQL with SQLAlchemy 2.0.23 ORM
- **Messaging:** NATS-py 2.6.0 for real-time service coordination
- **Caching:** Redis 5.0.1 for coordination state and performance optimization
- **HTTP Client:** HTTPX 0.25.2 for service integration
- **Authentication:** PyJWT 2.8.0, Python-JOSE with cryptography
- **Monitoring:** Prometheus client 0.19.0, Structlog 23.2.0
- **Resilience:** Tenacity 8.2.3 for retry logic and fault tolerance
- **Configuration:** PyYAML 6.0.1 for configuration management
- **Testing:** Pytest with asyncio, coverage, and mocking support
- **MQTT Integration:** Asyncio-MQTT 0.16.1 for IoT device coordination
- **Database Migrations:** Alembic 1.12.1 for schema management
- **Containerization:** Docker with Kubernetes support

## Contributing

Contributions to enhance proactive assistance capabilities are highly valued:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhanced-prediction`)
3. Focus on predictive accuracy and user experience
4. Add comprehensive tests for assistance orchestration logic
5. Ensure ethical AI practices and user consent
6. Update assistance algorithms and coordination workflows
7. Submit a pull request with detailed assistance effectiveness analysis

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"Assistance not being triggered"**: Verify service integrations and check event processing logs. Ensure all dependent services are running.
- **"Prediction accuracy low"**: Review user behavior patterns and adjust prediction algorithms. Ensure sufficient historical data.
- **"Cultural sensitivity issues"**: Review cultural context processing and update cultural intelligence models.
- **"High resource usage"**: Optimize orchestration logic and implement more efficient caching strategies.

## Future Implementation

- **Advanced Predictive Models:** Deep learning models for more accurate user need prediction
- **Personalized Assistance Profiles:** Individual assistance profiles that learn and adapt over time
- **Crisis Intervention Automation:** Automated crisis detection and intervention coordination
- **Multi-Modal Assistance:** Integration of visual, audio, and haptic assistance modalities
- **Collaborative Assistance:** Coordination with human therapists and support staff
- **IoT Integration:** Integration with wearable devices and smart home systems for comprehensive assistance