# Notification Service

## Description

The Notification Service is the comprehensive communication hub of the MantraPath platform, managing push notifications, alerts, real-time messaging, and WebSocket-based communication. This service handles all forms of user notifications including mood reminders, achievement alerts, community updates, crisis interventions, and personalized wellness messages. It provides both asynchronous notification delivery and real-time communication channels for immediate user engagement.

This service solves the challenge of timely, relevant communication in mental health support by providing intelligent notification scheduling, real-time alerts, and multi-channel message delivery. It ensures users receive the right information at the right time through their preferred communication channels while respecting user preferences and avoiding notification fatigue.

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
- Redis (for message queuing and real-time operations)
- WebSocket support for real-time communications
- Access to external notification providers (optional)

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/notification_service
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
- Key variables include `DATABASE_URL`, `REDIS_URL`, notification provider settings, WebSocket configuration, and delivery preferences.

## Usage

The Notification Service provides comprehensive notification management through REST API endpoints and WebSocket connections.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8007 --reload
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d notification_service
  ```

- **Send notification:**
  ```bash
  curl -X POST "http://localhost:8007/notifications" \
       -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"recipient_id":"user123","title":"Mood Check-in","message":"How are you feeling today?","type":"mood_reminder"}'
  ```

- **Get user notifications:**
  ```bash
  curl -X GET "http://localhost:8007/notifications?limit=20" \
       -H "Authorization: Bearer <token>"
  ```

- **Mark notification as read:**
  ```bash
  curl -X PUT "http://localhost:8007/notifications/{notification_id}/read" \
       -H "Authorization: Bearer <token>"
  ```

- **WebSocket connection for real-time notifications:**
  ```javascript
  const ws = new WebSocket('ws://localhost:8007/ws/notifications');
  ws.onmessage = (event) => {
    const notification = JSON.parse(event.data);
    console.log('Real-time notification:', notification);
  };
  ```

- **API Documentation:**
  Interactive API documentation at `http://localhost:8007/docs`

## Features

- **Multi-Channel Notifications:** Push notifications, email, SMS, and in-app notifications
- **Real-Time WebSocket Communication:** Instant notification delivery through WebSocket connections
- **Smart Notification Scheduling:** Intelligent timing based on user behavior and preferences
- **Notification Queuing:** Redis-based queuing system for reliable message delivery
- **Connection Management:** Robust WebSocket connection management with automatic reconnection
- **Notification Preferences:** User-configurable notification settings and preferences
- **Priority Levels:** Different priority levels for various types of notifications
- **Delivery Status Tracking:** Comprehensive tracking of notification delivery status
- **Template Management:** Customizable notification templates for different message types
- **Batch Notifications:** Efficient batch processing for mass notification campaigns
- **Analytics and Reporting:** Detailed analytics on notification performance and engagement
- **Crisis Alert System:** Priority alert system for mental health crisis situations

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **Database:** PostgreSQL with SQLAlchemy 2.0.23 ORM
- **Real-time Communication:** WebSockets 12.0 for live notification delivery
- **Message Queuing:** Redis 5.0.1 for notification queuing and caching
- **Authentication:** JWT token validation through shared auth system
- **HTTP Client:** HTTPX 0.25.2 for external service integration
- **Templates:** Jinja2 3.1.2 for notification template rendering
- **Configuration:** Pydantic Settings 2.0.3 for configuration management
- **Logging:** Loguru 0.7.2, Structlog 23.2.0 for comprehensive logging
- **Monitoring:** Prometheus client 0.19.0 for metrics collection
- **File Operations:** Aiofiles 23.2.1 for asynchronous file handling
- **Database Migrations:** Alembic 1.12.1 for schema management
- **Containerization:** Docker

## Contributing

Contributions to enhance notification capabilities are highly valued:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhanced-notifications`)
3. Focus on user experience and notification effectiveness
4. Add comprehensive tests for notification delivery and WebSocket functionality
5. Ensure privacy and user preference compliance
6. Update notification templates and delivery logic
7. Submit a pull request with detailed notification performance analysis

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"WebSocket connections dropping frequently"**: Check network stability and implement proper reconnection logic in clients.
- **"Notifications not being delivered"**: Verify Redis connectivity and notification queue processing.
- **"High notification latency"**: Review notification scheduling logic and consider optimizing batch processing.
- **"Users receiving too many notifications"**: Review notification frequency limits and user preference settings.

## Future Implementation

- **AI-Powered Notification Optimization:** Machine learning for optimal notification timing and content
- **Advanced Personalization:** Dynamic notification content based on user mood and context
- **Multi-Platform Push Notifications:** Native mobile push notifications for iOS and Android
- **Smart Notification Batching:** Intelligent grouping of related notifications to reduce noise
- **Voice Notifications:** Integration with voice assistants for audio notification delivery
- **Predictive Notifications:** Proactive notifications based on predictive user need analysis