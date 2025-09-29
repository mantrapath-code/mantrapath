# Profile Service

## Description

The Profile Service is the comprehensive user identity and preference management hub of the MantraPath platform. This service handles all aspects of user profiles, personal preferences, settings management, and customization options. It maintains detailed user information including biographical data, privacy settings, notification preferences, theme selections, timezone configurations, and language preferences, enabling personalized experiences across all platform interactions.

This service solves the challenge of maintaining consistent, personalized user experiences across a distributed microservices architecture. By centralizing user profile data and preferences, it ensures that all services can access current user settings to deliver customized experiences while maintaining user privacy and control over their personal information.

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
- Redis (for profile caching)
- Access to shared authentication system
- WebSocket support for real-time updates

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/profile_service
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
- Key variables include `DATABASE_URL`, `REDIS_URL`, profile storage settings, privacy configuration, and notification preferences.

## Usage

The Profile Service provides comprehensive user profile management through REST API endpoints.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8002 --reload
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d profile_service
  ```

- **Get user profile:**
  ```bash
  curl -X GET "http://localhost:8002/profile" \
       -H "Authorization: Bearer <token>"
  ```

- **Update profile:**
  ```bash
  curl -X PUT "http://localhost:8002/profile" \
       -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"bio":"Mental health advocate","timezone":"America/New_York","theme_preference":"dark"}'
  ```

- **Update notification preferences:**
  ```bash
  curl -X PUT "http://localhost:8002/preferences/notifications" \
       -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"email_notifications":true,"mood_reminders":true,"weekly_reports":false}'
  ```

- **Set privacy preferences:**
  ```bash
  curl -X PUT "http://localhost:8002/preferences/privacy" \
       -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"privacy_level":"private"}'
  ```

- **Search profiles (if permitted):**
  ```bash
  curl -X GET "http://localhost:8002/profiles/search?query=depression+support" \
       -H "Authorization: Bearer <token>"
  ```

- **API Documentation:**
  Interactive API documentation at `http://localhost:8002/docs`

## Features

- **Comprehensive Profile Management:** Complete user profile including bio, avatar, timezone, and personal information
- **Advanced Preference System:** Detailed preferences for notifications, themes, privacy, and user experience
- **Privacy Controls:** Granular privacy settings with multiple privacy levels (public, friends, private)
- **Notification Preferences:** Customizable notification settings for all platform communications
- **Theme Management:** User interface customization with light, dark, and auto theme options
- **Language Preferences:** Multi-language support with user-specific language settings
- **Timezone Management:** Accurate timezone handling for personalized scheduling
- **Profile Caching:** Redis-based caching for high-performance profile access
- **Real-time Updates:** WebSocket support for real-time profile synchronization
- **Search Functionality:** Privacy-respecting profile search with configurable visibility
- **Access Control:** Comprehensive access control with user verification
- **Data Validation:** Robust data validation and sanitization for profile information

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **Database:** PostgreSQL with SQLAlchemy 2.0.23 ORM
- **Caching:** Redis 5.0.1 for high-performance profile caching
- **Real-time Updates:** WebSockets 12.0 for live profile synchronization
- **Authentication:** JWT token validation through shared auth system
- **HTTP Client:** HTTPX 0.25.2 for service integration
- **Templates:** Jinja2 3.1.2 for profile data rendering
- **Configuration:** Pydantic Settings 2.0.3 for configuration management
- **Logging:** Loguru 0.7.2, Structlog 23.2.0 for comprehensive logging
- **Monitoring:** Prometheus client 0.19.0 for metrics collection
- **File Operations:** Aiofiles 23.2.1 for avatar and file handling
- **Database Migrations:** Alembic 1.12.1 for schema management
- **Security:** Python-JOSE with cryptography, Passlib with BCrypt
- **Containerization:** Docker

## Contributing

Contributions to enhance profile management capabilities are highly valued:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhanced-preferences`)
3. Focus on user experience and privacy protection
4. Add comprehensive tests for profile operations and privacy controls
5. Ensure GDPR compliance and data protection
6. Update preference schemas and validation logic
7. Submit a pull request with detailed privacy impact analysis

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"Profile changes not syncing"**: Check Redis connectivity and WebSocket connections. Verify cache invalidation logic.
- **"Privacy settings not being respected"**: Review access control implementation and ensure proper permission checks.
- **"Theme preferences not applying"**: Verify theme preference storage and client-side theme application logic.
- **"Timezone issues with scheduling"**: Check timezone validation and conversion logic in dependent services.

## Future Implementation

- **Advanced Personalization:** AI-driven profile customization based on user behavior and preferences
- **Social Features:** Enhanced social profile features with friend connections and shared interests
- **Profile Analytics:** Insights into profile usage patterns and preference effectiveness
- **Multi-Device Synchronization:** Seamless profile synchronization across multiple devices
- **Profile Backup and Export:** Comprehensive data export and backup functionality for user data portability
- **Advanced Privacy Controls:** Granular privacy controls with dynamic permission management