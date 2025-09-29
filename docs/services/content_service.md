# Content Service

## Description

The Content Service is the educational and inspirational content hub of the MantraPath platform, managing articles, videos, exercises, affirmations, and personalized recommendations. This service curates and delivers mental health resources, wellness content, and therapeutic materials tailored to individual user needs and preferences. It serves as the knowledge base that empowers users with educational content, daily affirmations, and evidence-based wellness practices.

This service solves the challenge of content discovery and personalization in mental health education. By analyzing user behavior, mood patterns, and preferences, it delivers relevant, timely content that supports users' wellness journeys. It transforms a vast library of mental health resources into a personalized, accessible learning experience.

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
- Redis (for caching and recommendations)
- Access to shared authentication system

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/content_service
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
- Key variables include `DATABASE_URL`, `REDIS_URL`, content storage settings, and recommendation algorithm parameters.

## Usage

The Content Service provides comprehensive content management and delivery through REST API endpoints.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8005 --reload
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d content_service
  ```

- **Get personalized recommendations:**
  ```bash
  curl -X GET "http://localhost:8005/content/recommendations" \
       -H "Authorization: Bearer <token>"
  ```

- **Create new content:**
  ```bash
  curl -X POST "http://localhost:8005/content" \
       -H "Authorization: Bearer <token>" \
       -H "Content-Type: application/json" \
       -d '{"title":"Mindfulness Guide","content":"...","content_type":"article","category":"mindfulness"}'
  ```

- **Get daily affirmations:**
  ```bash
  curl -X GET "http://localhost:8005/affirmations/daily" \
       -H "Authorization: Bearer <token>"
  ```

- **API Documentation:**
  Interactive API documentation at `http://localhost:8005/docs`

## Features

- **Multi-Format Content Management:** Support for articles, videos, audio, and interactive exercises
- **Personalized Recommendations:** AI-driven content suggestions based on user behavior and mood
- **Daily Affirmations:** Curated, mood-aware affirmations delivered at optimal times
- **Content Categorization:** Organized content by mental health topics, difficulty levels, and formats
- **User Engagement Tracking:** Views, likes, bookmarks, and completion tracking
- **Search and Discovery:** Advanced search with filters for content type, category, and difficulty
- **Content Curation:** Editorial workflow for content review and approval
- **Mood-Aware Delivery:** Content suggestions adapted to current user mood and context
- **Progress Tracking:** Monitor user engagement with educational content
- **Collaborative Filtering:** Recommendation engine based on similar user preferences
- **Content Analytics:** Detailed insights into content performance and user engagement
- **Accessibility Features:** Support for different learning styles and accessibility needs

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **Database:** PostgreSQL with SQLAlchemy 2.0.23 ORM
- **Caching:** Redis 5.0.1 for recommendation caching and performance optimization
- **Authentication:** JWT token validation through shared auth system
- **HTTP Client:** HTTPX 0.25.2 for external content integration
- **Event System:** Enhanced Event Bus V3 for content interaction events
- **Logging:** Loguru for content access and performance logging
- **File Handling:** Aiofiles for media content management
- **Templates:** Jinja2 for content rendering and email templates
- **Database Migrations:** Alembic 1.12.1 for schema management
- **Containerization:** Docker

## Contributing

Contributions to enhance content delivery and personalization are welcomed:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improved-recommendations`)
3. Implement content-focused improvements
4. Add comprehensive tests for recommendation algorithms
5. Ensure content accessibility and inclusivity
6. Update content guidelines and curation workflows
7. Submit a pull request with detailed content impact analysis

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"Recommendations not personalized"**: Check user interaction data and ensure recommendation algorithms have sufficient data
- **"Content not loading"**: Verify database connectivity and content storage configuration
- **"Search not working"**: Review search index configuration and ensure database indexes are properly created
- **"Affirmations not displaying"**: Check affirmation delivery logic and user mood context integration

## Future Implementation

- **AI Content Generation:** Automatic creation of personalized affirmations and exercises
- **Interactive Content:** Gamified wellness exercises and interactive learning modules
- **Video Analytics:** Advanced video engagement tracking and adaptive streaming
- **Collaborative Content:** User-generated content with community review and rating
- **Multi-language Support:** Automatic content translation and localization
- **Offline Content:** Content synchronization for offline access and learning