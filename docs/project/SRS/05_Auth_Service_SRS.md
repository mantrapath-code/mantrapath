# Software Requirements Specification (SRS)
## Authentication Service

**Version:** 1.0.0  
**Date:** December 2024  
**Project:** MantraPath - Mental Health and Wellness Platform

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements for the Authentication Service, a critical security component of the MantraPath platform that handles user registration, authentication, authorization, and account management. The service provides secure JWT-based authentication with email verification, password management, and automated account cleanup capabilities.

### 1.2 Scope
The Authentication Service encompasses:
- User registration with email verification and password strength validation
- Multi-factor authentication with JWT token management
- Account lifecycle management with automated cleanup of unverified accounts
- Session management with access and refresh token handling
- Security features including rate limiting and brute force protection
- Development utilities for testing and debugging

### 1.3 Definitions and Acronyms
- **JWT**: JSON Web Token for stateless authentication
- **Access Token**: Short-lived token for API access authentication
- **Refresh Token**: Long-lived token for obtaining new access tokens
- **Email Verification**: Process to confirm user email ownership
- **Password Hashing**: Secure password storage using bcrypt algorithm
- **Account Cleanup**: Automated removal of unverified expired accounts

### 1.4 References
- MantraPath Security Architecture Documentation
- OAuth 2.0 and JWT Standards (RFC 7519, RFC 6749)
- OWASP Authentication Guidelines
- GDPR Data Protection Requirements

### 1.5 Document Overview
This SRS details functional requirements, non-functional requirements, system interfaces, and implementation constraints for the Authentication Service within the MantraPath ecosystem.

---

## 2. Overall Description

### 2.1 Product Perspective
The Authentication Service operates as the security gateway in MantraPath's microservices architecture. It:
- Serves as the primary authentication provider for all platform services
- Integrates with the user database for account management
- Provides JWT tokens consumed by all other microservices
- Manages user profiles in coordination with Profile Service
- Supports frontend applications with secure authentication flows

### 2.2 Product Functions
**Core Functions:**
- **User Registration**: Secure account creation with email verification and password strength validation
- **Authentication**: Multi-method login supporting email/username with secure password verification
- **Token Management**: JWT access and refresh token generation, validation, and renewal
- **Email Verification**: Automated email verification system with configurable bypass for development
- **Account Management**: User profile retrieval, password management, and account status control
- **Security Monitoring**: Automated cleanup of unverified accounts and security event logging

**Authentication Methods:**
- **Email/Password**: Traditional email and password authentication
- **Username/Password**: Alternative username-based authentication
- **JWT Token**: Stateless token-based session management
- **Refresh Token**: Secure token renewal mechanism

**Security Features:**
- **Password Strength Validation**: Configurable password complexity requirements
- **Email Verification**: Mandatory email confirmation with 24-hour token expiration
- **Account Lockout**: Protection against brute force attacks
- **Automated Cleanup**: Removal of unverified accounts after 5 minutes
- **Development Mode**: Configurable security bypasses for testing environments

### 2.3 User Classes and Characteristics
**Primary Users:**
- End Users: Platform users requiring secure authentication
- Frontend Applications: Web and mobile clients consuming authentication APIs
- Backend Services: Microservices validating user authentication
- System Administrators: Managing user accounts and security policies

**User Characteristics:**
- Varying technical proficiency levels requiring intuitive authentication flows
- Security-conscious users expecting robust protection of personal data
- International users requiring compliance with regional privacy regulations
- Developers needing flexible authentication for testing and development

### 2.4 Operating Environment
**Deployment Environment:**
- Containerized deployment using Docker
- Kubernetes orchestration for high availability
- Port 8001 for HTTP API access
- PostgreSQL database for user data persistence
- SMTP server integration for email verification

**Dependencies:**
- Python 3.11+ runtime environment
- FastAPI web framework
- PostgreSQL database with SQLAlchemy ORM
- Redis for session caching (optional)
- SMTP server for email delivery

### 2.5 Design and Implementation Constraints
**Technical Constraints:**
- Authentication response time <200ms for 95% of requests
- Support for 1,000+ concurrent authentication requests
- JWT token validation <50ms across all services
- Email verification delivery within 30 seconds

**Regulatory Constraints:**
- GDPR compliance for European user data protection
- HIPAA compliance for health-related user information
- SOC 2 Type II compliance for security controls
- Data retention policies with automated cleanup

### 2.6 Assumptions and Dependencies
**Assumptions:**
- SMTP server maintains reliable email delivery
- Database maintains 99.9% availability for user data
- Frontend applications handle token storage securely
- Network connectivity supports real-time authentication

**Dependencies:**
- PostgreSQL database for user account storage
- SMTP server for email verification delivery
- Shared authentication library for JWT operations
- All platform services for token validation integration

---

## 3. System Features

### 3.1 User Registration and Verification
**Description:** Secure user account creation with comprehensive validation and email verification.

**Functional Requirements:**
- FR-3.1.1: System shall validate email format and uniqueness before registration
- FR-3.1.2: System shall enforce password strength requirements with configurable complexity rules
- FR-3.1.3: System shall generate secure verification tokens with 24-hour expiration
- FR-3.1.4: System shall send verification emails with secure links for account activation
- FR-3.1.5: System shall support development mode with configurable email verification bypass

**Registration Process:**
1. **Input Validation**: Email format, username uniqueness, password strength verification
2. **Account Creation**: Secure password hashing using bcrypt with salt
3. **Verification Token Generation**: Cryptographically secure token with expiration
4. **Email Delivery**: SMTP-based verification email with embedded activation link
5. **Account Activation**: Token validation and account status update

**Input:** UserRegister object with email, username, password, first_name, last_name
**Output:** RegistrationResponse with user_id, verification status, and optional tokens

### 3.2 Authentication and Login
**Description:** Multi-method user authentication with secure session management.

**Functional Requirements:**
- FR-3.2.1: System shall support authentication via email or username
- FR-3.2.2: System shall verify passwords using secure bcrypt comparison
- FR-3.2.3: System shall validate account status (active, verified) before login
- FR-3.2.4: System shall generate JWT access tokens with user claims
- FR-3.2.5: System shall create refresh tokens for secure token renewal

**Authentication Flow:**
1. **Credential Validation**: Email/username lookup and password verification
2. **Account Status Check**: Verification status and account activation validation
3. **Token Generation**: JWT access token with user claims and refresh token
4. **Session Tracking**: Last login timestamp update and audit logging
5. **Response Delivery**: Secure token pair delivery to client

**Input:** UserLogin object with email_or_username and password
**Output:** Token object with access_token, refresh_token, and token_type

### 3.3 Token Management and Renewal
**Description:** Comprehensive JWT token lifecycle management with secure renewal capabilities.

**Functional Requirements:**
- FR-3.3.1: System shall generate JWT access tokens with configurable expiration (default 15 minutes)
- FR-3.3.2: System shall create refresh tokens with extended expiration (default 7 days)
- FR-3.3.3: System shall validate token signatures and expiration dates
- FR-3.3.4: System shall support secure token renewal using valid refresh tokens
- FR-3.3.5: System shall invalidate tokens on logout and security events

**Token Structure:**
- **Access Token Claims**: sub (user_id), email, role, exp, iat
- **Refresh Token Claims**: sub (user_id), exp, iat, token_type
- **Security Features**: HMAC SHA-256 signature, configurable expiration
- **Validation**: Signature verification, expiration check, user status validation

### 3.4 Account Management and Security
**Description:** Comprehensive account lifecycle management with automated security features.

**Functional Requirements:**
- FR-3.4.1: System shall provide user profile retrieval with authentication
- FR-3.4.2: System shall support password reset with secure token generation
- FR-3.4.3: System shall automatically cleanup unverified accounts after 5 minutes
- FR-3.4.4: System shall maintain audit logs for all authentication events
- FR-3.4.5: System shall support account deactivation and reactivation

**Automated Cleanup Process:**
- **Scheduled Execution**: Every 5 minutes background cleanup task
- **Account Identification**: Unverified accounts older than 5 minutes
- **Cascade Deletion**: Removal of related data (profiles, journal entries, mood data)
- **Audit Logging**: Cleanup activity logging for compliance
- **Error Handling**: Graceful handling of deletion failures with retry logic

### 3.5 Development and Testing Support
**Description:** Development utilities and testing support features for efficient development workflows.

**Functional Requirements:**
- FR-3.5.1: System shall provide development login endpoint with test user creation
- FR-3.5.2: System shall support configurable email verification bypass
- FR-3.5.3: System shall provide health check endpoints for monitoring
- FR-3.5.4: System shall support environment-specific configuration
- FR-3.5.5: System shall provide comprehensive error handling and logging

---

## 4. External Interface Requirements

### 4.1 User Interfaces
**Client Applications:**
- Web-based registration and login forms
- Mobile application authentication screens
- Password reset and email verification interfaces
- Administrative user management dashboards

### 4.2 API Interfaces

**Authentication Endpoints:**
```
POST /register
- Input: UserRegister (email, username, password, first_name, last_name)
- Output: RegistrationResponse with verification requirements

POST /login
- Input: UserLogin (email_or_username, password)
- Output: Token (access_token, refresh_token, token_type)

POST /refresh-token
- Input: Refresh token
- Output: New token pair

GET /me
- Input: JWT access token
- Output: UserResponse with profile information

POST /logout
- Input: JWT access token
- Output: Logout confirmation
```

**Email Verification Endpoints:**
```
POST /verify-email
- Input: VerificationRequest (token)
- Output: Verification confirmation

GET /verify-email/{token}
- Input: Verification token in URL
- Output: Redirect to frontend with status

POST /resend-verification
- Input: Email address
- Output: Resend confirmation
```

**Development Endpoints:**
```
POST /dev/login
- Input: None (creates/authenticates test user)
- Output: Token for development testing

GET /health
- Output: Service health status
```

### 4.3 Hardware Interfaces
**Compute Resources:**
- CPU: Multi-core processor for concurrent authentication requests
- Memory: Minimum 512MB RAM for token generation and validation
- Storage: SSD storage for user data and audit logs

### 4.4 Software Interfaces

**Database Interfaces:**
- PostgreSQL: User account storage with SQLAlchemy ORM
- User table: Core user account information
- UserProfile table: Extended user profile data
- Cascade relationships: Proper foreign key constraints

**Email Service Interfaces:**
- SMTP Server: Email verification delivery
- Email Templates: HTML/text verification emails
- Delivery Tracking: Email send status monitoring

**Security Interfaces:**
- JWT Library: Token generation and validation
- Bcrypt: Password hashing and verification
- Cryptographic Functions: Secure token generation

**Service Integration:**
- Shared Authentication Library: Common JWT utilities
- All Platform Services: Token validation integration
- API Gateway: Authentication middleware integration

### 4.5 Communication Protocols
- HTTP/HTTPS for REST API communication
- SMTP for email delivery
- JSON for data serialization
- JWT for stateless authentication tokens

---

## 5. Non-Functional Requirements

### 5.1 Performance
- **Authentication Response Time:** 95% of login requests completed within 200ms
- **Token Validation:** <50ms token validation across all services
- **Concurrent Users:** Support 1,000+ simultaneous authentication requests
- **Email Delivery:** Verification emails delivered within 30 seconds

### 5.2 Security
- **Password Security:** Bcrypt hashing with configurable salt rounds (minimum 12)
- **Token Security:** HMAC SHA-256 signed JWT tokens with secure key management
- **Account Protection:** Automated cleanup of unverified accounts
- **Data Encryption:** TLS 1.3 for all external communications
- **Audit Logging:** Complete audit trail for all authentication events

### 5.3 Reliability
- **Availability:** 99.9% uptime for authentication services
- **Data Consistency:** ACID compliance for user account operations
- **Error Recovery:** Graceful handling of database and email service failures
- **Backup and Recovery:** Automated user data backup with point-in-time recovery

### 5.4 Scalability
- **Horizontal Scaling:** Auto-scaling based on authentication load
- **Database Scaling:** Read replicas for improved query performance
- **Token Validation:** Stateless JWT design for distributed validation
- **Session Management:** Stateless authentication supporting microservices architecture

### 5.5 Compliance
- **GDPR Compliance:** Right to erasure, data portability, consent management
- **HIPAA Compliance:** Secure handling of health-related user data
- **SOC 2 Compliance:** Security controls and audit requirements
- **Password Policies:** Configurable complexity requirements

---

## 6. Glossary and Appendix

### 6.1 Glossary
- **Access Token**: Short-lived JWT token for API authentication
- **Account Cleanup**: Automated removal of unverified expired user accounts
- **Bcrypt**: Secure password hashing algorithm with built-in salt
- **Email Verification**: Process to confirm user email address ownership
- **JWT**: JSON Web Token for stateless authentication
- **Refresh Token**: Long-lived token for renewing access tokens

### 6.2 Appendix A: Configuration Parameters
```yaml
# Authentication Configuration
JWT_SECRET_KEY: "your-super-secret-jwt-key"
ACCESS_TOKEN_EXPIRE_MINUTES: 15
REFRESH_TOKEN_EXPIRE_DAYS: 7

# Email Configuration
SMTP_SERVER: "smtp.gmail.com"
SMTP_PORT: 587
SMTP_USERNAME: "your-email@domain.com"
SMTP_PASSWORD: "your-app-password"

# Security Configuration
BCRYPT_ROUNDS: 12
PASSWORD_MIN_LENGTH: 8
REQUIRE_EMAIL_VERIFICATION: true
SKIP_EMAIL_VERIFICATION: false  # Development only

# Cleanup Configuration
CLEANUP_INTERVAL_MINUTES: 5
UNVERIFIED_ACCOUNT_TTL_MINUTES: 5
```

### 6.2 Appendix B: Password Strength Requirements
**Default Password Policy:**
- Minimum 8 characters length
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)
- At least one special character (!@#$%^&*)
- No common passwords from breach databases
- No personal information (name, email) in password

### 6.3 Appendix C: JWT Token Structure
**Access Token Claims:**
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "role": "user",
  "exp": 1640995200,
  "iat": 1640994300,
  "type": "access"
}
```

**Refresh Token Claims:**
```json
{
  "sub": "user-uuid",
  "exp": 1641600000,
  "iat": 1640994300,
  "type": "refresh"
}
```

### 6.4 Appendix D: Database Schema
**Users Table:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    role VARCHAR(50) DEFAULT 'user',
    verification_token VARCHAR(255),
    verification_token_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

**UserProfiles Table:**
```sql
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6.5 Appendix E: Error Codes and Messages
**Authentication Error Codes:**
- `AUTH_001`: Invalid credentials
- `AUTH_002`: Account not verified
- `AUTH_003`: Account deactivated
- `AUTH_004`: Token expired
- `AUTH_005`: Invalid token signature
- `AUTH_006`: Password too weak
- `AUTH_007`: Email already registered
- `AUTH_008`: Username already taken



