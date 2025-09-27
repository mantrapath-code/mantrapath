# Community Service

## Description

The Community Service is the social backbone of the MantraPath platform, fostering peer support, shared wellness journeys, and meaningful connections between users. This service manages community forums, group challenges, events, and social interactions that are essential for mental health recovery and maintenance. It creates safe spaces for users to share experiences, participate in wellness challenges, and build supportive relationships with others on similar journeys.

This service solves the isolation problem common in mental health struggles by providing structured, moderated community interactions. It enables users to find peer support, participate in group activities, share achievements, and learn from others' experiences while maintaining privacy and safety through comprehensive moderation features.

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
- Redis (for caching and real-time features)
- Access to shared authentication and event systems

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/community_service
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

4. **Run database migrations:**
   ```bash
   python migrate_database.py
   ```

### Configuration

- Environment variables configuration:
  ```bash
  cp .env.example .env
  nano .env
  ```
- Key variables include `DATABASE_URL`, `REDIS_URL`, moderation settings, and event bus configuration.

## Usage

The Community Service provides comprehensive social features through REST API endpoints.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8006 --reload
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d community_service
  ```

- **Join a forum:**
  ```bash
  curl -X POST "http://localhost:8006/forums/{forum_id}/join" \
       -H "Authorization: Bearer <token>"
  ```

- **Create a discussion thread:**
  ```bash
  curl -X POST "http://localhost:8006/forums/{forum_id}/threads" \
       -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"title":"Weekly Check-in","content":"How is everyone doing this week?"}'
  ```

- **API Documentation:**
  Interactive API documentation at `http://localhost:8006/docs`

## Features

- **Community Forums:** Organized discussion spaces by topic, condition, or interest
- **Discussion Threads:** Threaded conversations with replies and reactions
- **Wellness Challenges:** Group challenges for habits, goals, and mutual support
- **Community Events:** Virtual and local events for community building
- **Peer Support:** Private messaging and support group functionality
- **Achievement Sharing:** Celebrate milestones and progress with the community
- **Moderation Tools:** Comprehensive content moderation and safety features
- **Privacy Controls:** Granular privacy settings for different types of content
- **Real-time Interactions:** Live chat and real-time forum updates
- **Psychology-based Features:** Evidence-based community psychology principles
- **Cultural Sensitivity:** Culturally-aware community guidelines and moderation
- **Crisis Support:** Community-driven crisis identification and support protocols

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **Database:** PostgreSQL with SQLAlchemy 2.0.23 ORM
- **Caching:** Redis 5.0.1 for real-time features and caching
- **Real-time Communication:** WebSockets 12.0 for live interactions
- **Authentication:** JWT token validation through shared auth system
- **Event System:** Enhanced Event Bus V3 for cross-service communication
- **HTTP Client:** HTTPX 0.25.2 for service communication
- **Logging:** Loguru and Structlog for comprehensive logging
- **Monitoring:** Prometheus client for metrics
- **Database Migrations:** Alembic 1.12.1
- **File Handling:** Aiofiles for community content management
- **Containerization:** Docker

## Contributing

Contributions to enhance community features are highly valued:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhanced-moderation`)
3. Implement community-focused improvements
4. Add comprehensive tests for social interactions
5. Ensure privacy and safety features work correctly
6. Update community guidelines and documentation
7. Submit a pull request with detailed community impact analysis

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"Forums not loading"**: Check database connectivity and ensure community tables are properly created
- **"Real-time features not working"**: Verify WebSocket configuration and Redis connectivity
- **"Moderation not functioning"**: Review moderation settings and ensure proper authentication for moderator roles
- **"Challenge progress not updating"**: Check event bus connectivity and challenge progress calculation logic

## Future Implementation

- **AI-Powered Moderation:** Advanced content filtering and automatic community safety measures
- **Peer Matching:** Algorithm-based matching of users with similar interests or challenges
- **Group Therapy Integration:** Structured group therapy sessions within the community platform
- **Mentorship Programs:** Formal peer mentorship matching and management
- **Community Analytics:** Detailed insights into community health and engagement patterns
- **Mobile-First Features:** Enhanced mobile community experience with push notifications