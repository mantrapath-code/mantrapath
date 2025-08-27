# Authentication Service

## Overview

The Authentication Service is the security backbone of MantraPath, handling user registration, login, email verification, JWT token management, and user session control. It provides secure authentication mechanisms with email verification, password strength validation, and automatic cleanup of unverified accounts.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   Auth Service   │───▶│   Database      │
│   (Login/Reg)   │    │   (Port 8001)    │    │   (PostgreSQL)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Email Service  │
                       │   (SMTP/Gmail)   │
                       └──────────────────┘
```

## Key Features

### 🔐 **User Authentication**
- **Secure Registration**: Email/username uniqueness validation
- **Password Security**: Bcrypt hashing with strength validation
- **Multi-Login Support**: Login with email or username
- **JWT Tokens**: Access tokens (30min) + Refresh tokens (7 days)
- **Session Management**: Secure token creation and validation

### 📧 **Email Verification System**
- **Verification Tokens**: Secure 32-character URL-safe tokens
- **HTML Email Templates**: Professional verification emails
- **Token Expiration**: 24-hour verification window
- **Resend Capability**: Users can request new verification emails
- **Development Mode**: Console output when SMTP not configured

### 🧹 **Account Management**
- **Automatic Cleanup**: Removes unverified accounts after 5 minutes
- **Duplicate Prevention**: Handles registration conflicts intelligently
- **Account Recovery**: Verification resend functionality
- **User Profiles**: Automatic profile creation on registration

### 🛡️ **Security Features**
- **Password Validation**: 8+ chars, uppercase, lowercase, numbers, special chars
- **Rate Limiting**: Prevents rapid re-registration attempts
- **Token Security**: Separate access/refresh token validation
- **Privacy Protection**: Unique 5-character user identifiers

## Database Schema

### **Users Table**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    role VARCHAR(20) DEFAULT 'user',
    verification_token VARCHAR(255),
    verification_token_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### **User Profiles Table**
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

## API Endpoints

### **User Registration**
```http
POST /register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response**:
```json
{
  "message": "Registration successful! Please check your email to verify your account.",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "verification_required": true
}
```

**Password Requirements**:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter  
- At least one number
- At least one special character

### **User Login**
```http
POST /login
Content-Type: application/json

{
  "email_or_username": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### **Email Verification**
```http
POST /verify-email
Content-Type: application/json

{
  "token": "verification_token_from_email"
}
```

**Response**:
```json
{
  "message": "Email verified successfully! You can now log in."
}
```

### **Resend Verification**
```http
POST /resend-verification
Content-Type: application/json

{
  "email": "user@example.com"
}
```

### **Token Refresh**
```http
POST /refresh-token
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### **Get Current User**
```http
GET /me
Authorization: Bearer {access_token}
```

**Response**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": true,
  "role": "user",
  "display_name": "ABCD1",
  "initials": "AB"
}
```

### **Logout**
```http
POST /logout
Authorization: Bearer {access_token}
```

### **Development Login** (Development Only)
```http
POST /dev/login
```
Creates/logs in a test user without email verification.

### **Health Check**
```http
GET /health
```

## Core Functions

### **Registration Process**

#### `register(user_data: UserRegister)`
**Process**:
1. **Password Validation**: Checks strength requirements
2. **Duplicate Check**: Verifies email/username uniqueness
3. **Conflict Resolution**: Handles unverified account conflicts
4. **User Creation**: Creates user with hashed password
5. **Profile Creation**: Automatically creates user profile
6. **Verification Setup**: Generates token and sends email
7. **Response**: Returns registration status and requirements

**Conflict Handling**:
- **Verified User**: Returns error (cannot re-register)
- **Recent Unverified**: Rate limits (5-minute window)
- **Old Unverified**: Removes old account, allows re-registration

### **Authentication Process**

#### `login(user_data: UserLogin)`
**Process**:
1. **User Lookup**: Finds user by email or username
2. **Password Verification**: Bcrypt password validation
3. **Account Status**: Checks active and verified status
4. **Session Update**: Updates last_login timestamp
5. **Token Generation**: Creates access and refresh tokens
6. **Response**: Returns JWT tokens

### **Email Verification System**

#### `send_verification_email(email, token, username)`
**Features**:
- **HTML Templates**: Professional email design
- **Secure Links**: Verification URL with token
- **Fallback Mode**: Console output when SMTP unavailable
- **Error Handling**: Graceful failure with console fallback

**Email Template**:
```html
<div style="max-width: 600px; margin: 0 auto; background-color: white;">
  <h1 style="color: #6366f1;">MantraPath</h1>
  <h2>Welcome, {username}!</h2>
  <p>Please verify your email address:</p>
  <a href="{verification_url}" style="background-color: #6366f1;">
    Verify Email Address
  </a>
</div>
```

### **Automatic Cleanup System**

#### `cleanup_unverified_accounts()`
**Process**:
1. **Cutoff Calculation**: 5 minutes ago timestamp
2. **Account Discovery**: Finds expired unverified accounts
3. **Cascade Deletion**: Removes related data (mood entries, journal entries, chat sessions)
4. **Profile Cleanup**: Removes associated user profiles
5. **User Removal**: Deletes user account
6. **Logging**: Reports cleanup activity

**Cleanup Schedule**: Runs every 5 minutes via background thread

## Security Implementation

### **Password Security**
```python
# Password hashing with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def validate_password_strength(password: str) -> tuple[bool, str]:
    # 8+ characters, uppercase, lowercase, numbers, special chars
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    # ... additional validations
```

### **JWT Token Management**
```python
# Token configuration
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

# Token creation
def create_access_token(data: Dict[Any, Any]) -> str:
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### **Verification Token Security**
```python
def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)  # 32-character URL-safe token
```

## Configuration

### **Environment Variables**
```bash
# Database
DATABASE_URL=postgresql://mantrapath:password@postgres:5432/mantrapath

# JWT Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@mantrapath.com

# Application
APP_URL=http://localhost:5174
SKIP_EMAIL_VERIFICATION=false  # Set to true for development
ENVIRONMENT=development  # Enables /dev/login endpoint
```

### **Email Setup**
For Gmail SMTP:
1. Enable 2-factor authentication
2. Generate app-specific password
3. Use app password in SMTP_PASSWORD

## Dependencies

### **Core Dependencies** (`requirements.txt`)
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
PyJWT==2.8.0
```

### **Security Libraries**
- **passlib**: Password hashing with bcrypt
- **python-jose**: JWT token handling with cryptography
- **PyJWT**: JWT encoding/decoding
- **secrets**: Secure token generation

## Docker Configuration

### **Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y curl

# Install dependencies
COPY services/auth_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules and service code
COPY shared /app/shared
COPY services/auth_service /app/

ENV PYTHONPATH=/app
EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## Error Handling

### **Registration Errors**
- **400 Bad Request**: Password too weak, email/username taken
- **429 Too Many Requests**: Recent registration attempt (rate limiting)
- **500 Internal Server Error**: Database or email service issues

### **Login Errors**
- **401 Unauthorized**: Invalid credentials, unverified email, inactive account

### **Verification Errors**
- **400 Bad Request**: Invalid token, expired token, already verified

## User Display System

### **Privacy-First Identifiers**
```python
def get_user_display_name(user) -> str:
    """Returns unique 5-character identifier (e.g., 'ABCD1')"""
    return generate_unique_user_display(str(user.id))

def format_user_for_api(user) -> dict:
    """Formats user data with unique identifier for API responses"""
    return {
        'id': str(user.id),
        'display_name': get_user_display_name(user),  # 'ABCD1'
        'initials': get_user_initials(user),          # 'AB'
        # ... other fields
    }
```

## Background Tasks

### **Startup Tasks**
```python
@app.on_event("startup")
async def startup_event():
    """Starts background cleanup task"""
    cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
    cleanup_thread.start()
```

### **Periodic Cleanup**
- **Frequency**: Every 5 minutes
- **Target**: Unverified accounts older than 5 minutes
- **Process**: Cascade deletion of related data
- **Logging**: Reports cleanup activity

## Development Features

### **Development Login**
```python
@app.post("/dev/login")
async def dev_login():
    """Creates/logs in test user without email verification"""
    # Only available in development environment
    # Creates testuser@mantrapath.com with password TestPassword123!
```

### **Email Verification Skip**
```bash
# Skip email verification in development
SKIP_EMAIL_VERIFICATION=true
```

### **Console Email Output**
When SMTP is not configured, verification emails are printed to console:
```
================================================================================
🔐 EMAIL VERIFICATION REQUIRED
================================================================================
User: John Doe (user@example.com)
Verification URL: http://localhost:5174/verify-email?token=abc123...
Verification Token: abc123...
================================================================================
```

## Monitoring & Logging

### **Request Logging**
- User registration attempts
- Login successes/failures
- Email verification events
- Account cleanup activities

### **Health Monitoring**
```bash
# Service health
curl http://localhost:8001/health

# Response
{"status": "healthy", "service": "auth-service"}
```

## Security Best Practices

### **Implemented Security**
- ✅ **Password Hashing**: Bcrypt with salt
- ✅ **JWT Security**: Separate access/refresh tokens
- ✅ **Email Verification**: Required for account activation
- ✅ **Rate Limiting**: Registration attempt throttling
- ✅ **Input Validation**: Pydantic models with validation
- ✅ **SQL Injection Prevention**: SQLAlchemy ORM
- ✅ **Token Expiration**: Time-limited verification tokens

### **Production Recommendations**
- [ ] **HTTPS Only**: Force SSL/TLS in production
- [ ] **Strong JWT Secret**: Use cryptographically secure secret key
- [ ] **Rate Limiting**: Implement comprehensive rate limiting
- [ ] **Account Lockout**: Lock accounts after failed login attempts
- [ ] **Audit Logging**: Log all authentication events
- [ ] **Password History**: Prevent password reuse
- [ ] **2FA Support**: Two-factor authentication option

## Testing

### **Manual Testing**
```bash
# Register new user
curl -X POST http://localhost:8001/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login
curl -X POST http://localhost:8001/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_username": "test@example.com",
    "password": "TestPass123!"
  }'

# Get user info
curl -X GET http://localhost:8001/me \
  -H "Authorization: Bearer {access_token}"
```

### **Development Testing**
```bash
# Quick development login
curl -X POST http://localhost:8001/dev/login

# Returns tokens for testuser@mantrapath.com
```

## Troubleshooting

### **Common Issues**

**Email Verification Not Working**:
- Check SMTP configuration in environment variables
- Verify Gmail app password if using Gmail
- Check console output for verification URLs in development

**Registration Conflicts**:
- Wait 5 minutes for automatic cleanup of unverified accounts
- Check for existing verified accounts with same email/username

**Token Issues**:
- Verify JWT_SECRET_KEY is consistent across restarts
- Check token expiration times
- Ensure proper Authorization header format: `Bearer {token}`

**Database Connection**:
- Verify DATABASE_URL format and credentials
- Check PostgreSQL service availability
- Ensure database tables are created

### **Debug Commands**
```bash
# Check service health
curl http://localhost:8001/health

# Test database connection
docker-compose exec postgres psql -U mantrapath -d mantrapath -c "\dt"

# View service logs
docker-compose logs -f auth-service

# Check email configuration
docker-compose exec auth-service env | grep SMTP
```

## Future Enhancements

### **Planned Features**
- [ ] **OAuth Integration**: Google, GitHub, Apple login
- [ ] **Two-Factor Authentication**: TOTP/SMS support
- [ ] **Password Reset**: Secure password recovery flow
- [ ] **Account Lockout**: Brute force protection
- [ ] **Session Management**: Active session tracking
- [ ] **Audit Logging**: Comprehensive security event logging
- [ ] **Role-Based Access**: Enhanced permission system
- [ ] **Account Deletion**: GDPR-compliant account removal

### **Performance Optimizations**
- [ ] **Redis Sessions**: Distributed session storage
- [ ] **Token Blacklisting**: Revoked token tracking
- [ ] **Connection Pooling**: Database connection optimization
- [ ] **Async Email**: Background email sending
- [ ] **Caching**: User data caching for frequent lookups