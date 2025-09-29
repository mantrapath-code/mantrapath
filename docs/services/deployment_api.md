# Deployment API Service

## Description

The Deployment API Service serves as a controlled, secure gateway specifically designed for frontend engineers to access deployment-related information and system status. This service provides a curated API layer that exposes essential deployment metrics, model training status, service health information, and system monitoring data without compromising backend security. It acts as a safe interface between the frontend development team and the complex backend infrastructure.

This service solves the problem of providing frontend engineers with necessary deployment and system information while maintaining strict security boundaries. It eliminates the need for frontend teams to have direct access to production systems, instead offering a controlled, rate-limited, and audited interface for accessing deployment status, API documentation, and system health metrics.

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
- Access to backend services for health monitoring
- JWT authentication system
- Rate limiting infrastructure

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/deployment_api
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

4. **Set up service configuration:**
   ```bash
   ./start.sh
   ```

### Configuration

- Environment variables configuration:
  ```bash
  cp .env.example .env
  nano .env
  ```
- Key variables include frontend engineer authentication settings, rate limiting configuration, and service URLs for health monitoring.

## Usage

The Deployment API provides secure, rate-limited access to deployment and system information.

- **Running the service locally:**
  ```bash
  python src/main.py
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d deployment_api
  ```

- **Check system health:**
  ```bash
  curl -X GET "http://localhost:8020/api/v1/health/system" \
       -H "Authorization: Bearer <frontend_engineer_token>"
  ```

- **Get model training status:**
  ```bash
  curl -X GET "http://localhost:8020/api/v1/models/training-status" \
       -H "Authorization: Bearer <frontend_engineer_token>"
  ```

- **API Documentation:**
  Secure API documentation at `http://localhost:8020/docs` (requires authentication)

## Features

- **Frontend Engineer Authentication:** Specialized authentication system for frontend development team
- **System Health Monitoring:** Real-time health status of all backend services
- **Model Training Status:** Current status and progress of AI model training processes
- **API Documentation Service:** Dynamic, up-to-date API documentation for frontend integration
- **Usage Tracking:** Comprehensive tracking of frontend API usage and patterns
- **Rate Limiting:** Configurable rate limiting to prevent abuse and ensure system stability
- **Audit Logging:** Complete audit trail of all frontend engineer API access
- **Permission Management:** Granular permissions for different levels of frontend access
- **Deployment Status:** Real-time deployment status and version information
- **Service Discovery:** Dynamic discovery and monitoring of available backend services
- **Error Reporting:** Detailed error reporting and troubleshooting information
- **Performance Metrics:** API performance and response time metrics

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **Authentication:** PyJWT 2.8.0, Python-JOSE with cryptography
- **HTTP Client:** HTTPX 0.25.2 for service health checks
- **Configuration:** Pydantic Settings 2.0.3 for configuration management
- **Logging:** Structlog 23.2.0, Loguru 0.7.2 for comprehensive logging
- **Async Support:** Native asyncio support for concurrent operations
- **Security:** Trusted host middleware, CORS configuration
- **Testing:** Pytest with asyncio and coverage support
- **Code Quality:** Black, isort, flake8, mypy for code quality
- **Containerization:** Docker

## Contributing

Contributions to improve deployment API functionality are welcomed:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhanced-monitoring`)
3. Focus on security and frontend developer experience
4. Add comprehensive tests for new API endpoints
5. Ensure proper authentication and authorization
6. Update API documentation
7. Submit a pull request with detailed security review

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"Authentication failed for frontend engineer"**: Verify JWT token format and ensure proper frontend engineer permissions are configured
- **"Rate limiting too restrictive"**: Review rate limiting configuration and adjust based on legitimate frontend development needs
- **"Health checks failing"**: Ensure all backend services are accessible and health check endpoints are properly configured
- **"API documentation not updating"**: Verify service discovery is working and API documentation service has access to current schemas

## Future Implementation

- **Real-time Dashboard:** Live dashboard for deployment status and system metrics
- **Automated Deployment Triggers:** Controlled deployment triggers for frontend engineers
- **Enhanced Analytics:** Advanced usage analytics and performance insights
- **Integration Testing Support:** API endpoints for integration testing coordination
- **Deployment History:** Comprehensive deployment history and rollback information
- **Alert Integration:** Integration with alerting systems for proactive issue notification