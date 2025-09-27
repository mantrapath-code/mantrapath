# Memory Service

## Description

The Memory Service is the intelligent data aggregation and behavioral analysis engine of the MantraPath platform. This service processes user interactions, tracks behavioral patterns, and maintains contextual memory across all platform activities. It creates comprehensive user behavior profiles that enable personalized experiences, predictive insights, and intelligent recommendations throughout the mental health journey.

This service solves the challenge of understanding user behavior patterns across distributed interactions. By maintaining intelligent memory of user activities, preferences, and behavioral changes over time, it enables the platform to provide increasingly personalized and effective mental health support that adapts to individual user needs and progress.

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
- Redis (for high-performance caching and real-time operations)
- Access to NATS messaging system
- Scientific computing libraries

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/memory_service
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

4. **Download required language models:**
   ```bash
   python -c "import nltk; nltk.download('vader_lexicon')"
   ```

### Configuration

- Environment variables configuration:
  ```bash
  cp .env.example .env
  nano .env
  ```
- Key variables include `DATABASE_URL`, `REDIS_URL`, `NATS_URL`, cultural intelligence settings, and pattern analysis parameters.

## Usage

The Memory Service operates primarily as a background service processing events and providing behavioral insights.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8017 --reload
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d memory_service
  ```

- **Get memory statistics:**
  ```bash
  curl -X GET "http://localhost:8017/memory/stats" \
       -H "Authorization: Bearer <token>"
  ```

- **Get user behavioral insights:**
  ```bash
  curl -X GET "http://localhost:8017/memory/insights/{user_id}" \
       -H "Authorization: Bearer <token>"
  ```

- **Process user interaction:**
  ```bash
  curl -X POST "http://localhost:8017/memory/interactions" \
       -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"user_id":"user123","interaction_type":"mood_entry","data":{"mood":"happy"}}'
  ```

- **API Documentation:**
  Interactive API documentation at `http://localhost:8017/docs`

## Features

- **Real-time Interaction Processing:** Processes user interactions as they happen across all platform services
- **Behavioral Pattern Analysis:** Advanced pattern recognition to identify user behavior trends and changes
- **Cultural Context Integration:** Culturally-aware memory processing that respects individual cultural backgrounds
- **Event-driven Memory Updates:** Automatic memory updates based on events from across the platform
- **Statistical Tracking:** Comprehensive statistics on interactions, patterns, insights, and sessions
- **Memory Aggregation:** Intelligent aggregation of user data for efficient retrieval and analysis
- **Temporal Analysis:** Time-based analysis of user behavior changes and trends
- **Cross-service Memory:** Unified memory across all MantraPath services and interactions
- **Privacy-preserving Analytics:** Advanced analytics while maintaining user privacy and data protection
- **Scalable Architecture:** High-performance architecture capable of handling large-scale user interactions
- **Cultural Intelligence:** Language detection and culturally-sensitive behavior analysis
- **Memory Optimization:** Efficient memory storage and retrieval with intelligent caching strategies

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **Database:** PostgreSQL with SQLAlchemy 2.0.25 ORM, AsyncPG 0.29.0
- **Caching:** Redis 5.0.1 for high-performance memory operations
- **Scientific Computing:** NumPy 1.25.2, Pandas 2.1.4, Scikit-learn 1.3.2
- **Messaging:** NATS-py 2.6.0 for event-driven architecture
- **Cultural Intelligence:** LangDetect 1.0.9, Polyglot 16.07.04
- **Authentication:** JWT token validation through shared auth system
- **Logging:** Structlog 23.2.0 for comprehensive operation logging
- **Monitoring:** Sentry SDK 1.38.0 for error tracking
- **Database Migrations:** Alembic 1.13.1 for schema management
- **File Operations:** Aiofiles 23.2.1 for asynchronous file handling
- **Testing:** Pytest with asyncio support and Factory Boy for test data
- **Containerization:** Docker

## Contributing

Contributions to enhance memory and behavioral analysis capabilities are highly valued:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/advanced-pattern-analysis`)
3. Focus on behavioral analysis and privacy-preserving techniques
4. Add comprehensive tests for memory processing logic
5. Ensure cultural sensitivity and ethical data handling
6. Update behavioral analysis algorithms and documentation
7. Submit a pull request with detailed behavioral analysis insights

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"Memory statistics not updating"**: Verify event bus connectivity and ensure interaction processing pipeline is active
- **"Pattern analysis slow"**: Check scientific computing library configuration and consider optimizing data aggregation intervals
- **"Cultural context not recognized"**: Review language detection settings and ensure polyglot language models are properly installed
- **"Memory insights inconsistent"**: Verify data consistency across services and check temporal analysis parameters

## Future Implementation

- **Advanced ML Models:** Deep learning models for complex behavioral pattern recognition
- **Predictive Memory:** Predictive modeling to anticipate user needs and behaviors
- **Real-time Personalization:** Instant personalization based on real-time behavioral analysis
- **Federated Learning:** Privacy-preserving distributed learning across user data
- **Advanced Cultural Models:** Enhanced cultural intelligence with regional and personal cultural modeling
- **Memory Consolidation:** Advanced memory consolidation algorithms for long-term user understanding