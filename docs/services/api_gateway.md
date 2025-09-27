# API Gateway Service

## Description

The API Gateway Service serves as the single entry point and orchestration hub for the entire MantraPath platform. It provides intelligent request routing, load balancing, authentication, rate limiting, and service discovery for all 21+ microservices. This gateway is enhanced with voice-command routing, AI-powered context awareness, and cultural intelligence to provide a seamless, personalized experience across all platform interactions.

This service solves the complexity of managing multiple microservices by providing a unified interface that handles cross-cutting concerns like security, monitoring, caching, and service coordination. It enables the platform to scale horizontally while maintaining consistency and security across all service interactions.

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
- Redis (for caching and rate limiting)
- Access to all backend microservices
- SSL certificates (for production)

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/api_gateway
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

- Configuration is managed through environment variables and config files:
  ```bash
  cp .env.example .env
  nano .env
  ```
- Key configurations include service URLs, authentication settings, rate limiting rules, and SSL certificates.

## Usage

The API Gateway runs as the front-facing service that all client applications interact with.

- **Running the service locally:**
  ```bash
  uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d api_gateway
  ```

- **Health Check:**
  ```bash
  curl http://localhost:8000/health
  ```

- **Service Status:**
  ```bash
  curl http://localhost:8000/services/status
  ```

- **API Documentation:**
  Comprehensive API docs available at `http://localhost:8000/docs`

## Features

- **Intelligent Request Routing:** Routes requests to appropriate microservices based on path, headers, and context
- **Voice Command Routing:** Specialized routing for voice commands with natural language understanding
- **AI Context Awareness:** Maintains user context across services for personalized experiences
- **Cultural Intelligence:** Adapts responses based on user's cultural background and preferences
- **Load Balancing:** Multiple load balancing strategies including round-robin, weighted, and health-based
- **Rate Limiting:** Configurable rate limiting per user, IP, or service endpoint
- **Circuit Breaker Pattern:** Prevents cascading failures by monitoring service health
- **JWT Authentication:** Secure token-based authentication with role-based access control
- **WebSocket Support:** Real-time communication support for chat and notifications
- **Response Caching:** Intelligent caching to reduce latency and backend load
- **Performance Monitoring:** Built-in metrics and monitoring for all service interactions
- **Request/Response Transformation:** Modify requests and responses as they flow through the gateway

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **HTTP Client:** HTTPX for service-to-service communication
- **Security:** Python-JOSE, PyJWT, Passlib for authentication
- **Caching:** Redis with Hiredis for high-performance caching
- **Configuration:** Pydantic for configuration management
- **Logging:** Structlog for structured, searchable logs
- **Monitoring:** Prometheus metrics (optional)
- **WebSockets:** FastAPI native WebSocket support
- **Containerization:** Docker

## Contributing

Contributions to improve gateway functionality are welcomed:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhanced-routing`)
3. Implement changes with comprehensive tests
4. Ensure all existing functionality remains intact
5. Update configuration documentation
6. Submit a pull request with detailed explanation

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"Service not reachable through gateway"**: Verify service registration and health status. Check service discovery configuration.
- **"Authentication failures"**: Ensure JWT secret keys are properly configured and tokens are valid.
- **"High response times"**: Check circuit breaker status, enable caching, and verify backend service performance.
- **"Rate limiting too aggressive"**: Review rate limiting configuration and adjust limits based on usage patterns.

## Future Implementation

- **GraphQL Support:** Add GraphQL gateway functionality for more flexible API consumption
- **Advanced Analytics:** Enhanced request analytics and user behavior tracking
- **Auto-scaling Integration:** Automatic service scaling based on traffic patterns
- **Multi-region Support:** Geographic load balancing and edge gateway deployment
- **API Versioning:** Sophisticated API version management and migration support
- **Machine Learning Routing:** AI-powered request routing based on user behavior and service performance