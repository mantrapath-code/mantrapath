# Auth Service

## Description

The Auth Service is the security cornerstone of the MantraPath platform, handling all aspects of user authentication, authorization, and identity management. This service provides secure user registration, login, token management, and role-based access control across all microservices. It implements modern security best practices including JWT tokens, password hashing, email verification, and account management features.

This service solves the critical challenge of maintaining secure, scalable authentication across a distributed microservices architecture. By centralizing authentication logic, it ensures consistent security policies, simplifies user management, and provides a single source of truth for user identity and permissions throughout the platform.

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
- Redis (for session caching)
- SMTP server (for email verification)

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/auth_service
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
- Critical variables include `JWT_SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `SMTP_SERVER`, and `SKIP_EMAIL_VERIFICATION` for development.

## Usage

The Auth Service provides REST API endpoints for all authentication operations.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8001 --reload
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d auth_service
  ```

- **User Registration:**
  ```bash
  curl -X POST "http://localhost:8001/register" \
       -H "Content-Type: application/json" \
       -d '{"email":"user@example.com","username":"testuser","password":"SecurePass123!","first_name":"John","last_name":"Doe"}'
  ```

- **User Login:**
  ```bash
  curl -X POST "http://localhost:8001/login" \
       -H "Content-Type: application/json" \
       -d '{"email_or_username":"user@example.com","password":"SecurePass123!"}'
  ```

- **API Documentation:**
  Interactive API docs at `http://localhost:8001/docs`

## Features

- **Secure User Registration:** Email validation, password strength requirements, and unique identifier generation
- **Flexible Login:** Support for login with either email or username
- **JWT Token Management:** Access and refresh token generation with configurable expiration
- **Email Verification:** Secure email verification process with token-based confirmation
- **Password Security:** BCrypt hashing with salt, password strength validation
- **User Profile Management:** Integration with user profiles and display names
- **Role-Based Access Control:** User roles and permissions management
- **Account Cleanup:** Automatic cleanup of unverified accounts
- **Session Management:** Redis-based session caching for performance
- **Security Headers:** CORS configuration and security middleware
- **Development Mode:** Configurable email verification skipping for local development

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **Database:** PostgreSQL with SQLAlchemy 2.0.23 ORM
- **Caching:** Redis with Hiredis for session management
- **Security:** Python-JOSE with cryptography, PyJWT, Passlib with BCrypt
- **Validation:** Pydantic with email validation
- **Database Migrations:** Alembic 1.13.0
- **HTTP Server:** Uvicorn with standard extras
- **Containerization:** Docker

## Contributing

Security-focused contributions are essential for this critical service:

1. Fork the repository
2. Create a security-focused branch (`git checkout -b security/enhanced-auth`)
3. Implement security improvements with thorough testing
4. Ensure all authentication flows work correctly
5. Add comprehensive security tests
6. Update security documentation
7. Submit a pull request with security review

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"JWT token expired" errors**: Check token expiration settings and implement proper token refresh logic in clients
- **"Email verification not working"**: Verify SMTP configuration and check if `SKIP_EMAIL_VERIFICATION` is set appropriately
- **"Password too weak" errors**: Review password strength requirements in the validation function
- **"Database connection failed"**: Ensure PostgreSQL is running and `DATABASE_URL` is correct

## Future Implementation

- **Multi-Factor Authentication (MFA):** SMS and authenticator app support for enhanced security
- **OAuth2 Integration:** Google, Apple, and other social login providers
- **Advanced Session Management:** Device tracking and concurrent session limits
- **Passwordless Authentication:** Magic link and biometric authentication options
- **Advanced Security Monitoring:** Suspicious activity detection and automatic account protection
- **API Key Management:** Service-to-service authentication with API keys