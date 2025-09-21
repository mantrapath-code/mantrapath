"""
Shared authentication utilities
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
import os
import re
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    
    return True, ""

def generate_verification_token() -> str:
    """Generate a secure random verification token"""
    return secrets.token_urlsafe(32)

def send_verification_email(email: str, token: str, username: str) -> bool:
    """
    Send email verification link
    Returns True if email was sent successfully
    """
    try:
        # Email configuration from environment variables
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        from_email = os.getenv("FROM_EMAIL", smtp_username)
        app_url = os.getenv("APP_URL", "http://localhost:5173")
        
        # Get the API Gateway URL for verification
        api_gateway_url = os.getenv("VITE_API_GATEWAY_URL", os.getenv("API_GATEWAY_URL", "http://139.84.213.185:8000"))
        
        if not smtp_username or not smtp_password:
            # For development/testing - print verification link to console
            verification_url = f"{api_gateway_url}/api/auth/verify-email/{token}"
            print("\n" + "="*80)
            print("🔐 EMAIL VERIFICATION REQUIRED")
            print("="*80)
            print(f"User: {username} ({email})")
            print(f"Verification URL: {verification_url}")
            print(f"Verification Token: {token}")
            print("="*80)
            print("💡 SMTP not configured. In production, set these environment variables:")
            print("   SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL")
            print("="*80 + "\n")
            return False  # Return False to allow proper verification flow testing
        
        # Create verification URL - goes through API Gateway to auth service
        verification_url = f"{api_gateway_url}/api/auth/verify-email/{token}"
        
        # Create email content
        subject = "Welcome to MantraPath - Verify Your Email"
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
              <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #6366f1; margin: 0;">MantraPath</h1>
                <p style="color: #6b7280; margin: 5px 0;">Holistic Mental Wellness Platform</p>
              </div>
              
              <h2 style="color: #111827; margin-bottom: 20px;">Welcome, {username}!</h2>
              
              <p style="color: #374151; line-height: 1.6; margin-bottom: 25px;">
                Thank you for joining MantraPath! We're excited to support you on your mental wellness journey.
              </p>
              
              <p style="color: #374151; line-height: 1.6; margin-bottom: 25px;">
                To complete your registration and start using all features, please verify your email address by clicking the button below:
              </p>
              
              <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" 
                   style="background-color: #6366f1; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                  Verify Email Address
                </a>
              </div>
              
              <p style="color: #6b7280; font-size: 14px; line-height: 1.5; margin-top: 30px;">
                If the button doesn't work, you can copy and paste this link into your browser:<br>
                <a href="{verification_url}" style="color: #6366f1; word-break: break-all;">{verification_url}</a>
              </p>
              
              <p style="color: #6b7280; font-size: 14px; line-height: 1.5; margin-top: 20px;">
                This verification link will expire in 24 hours. If you didn't create an account with MantraPath, please ignore this email.
              </p>
              
              <div style="border-top: 1px solid #e5e7eb; margin-top: 30px; padding-top: 20px; text-align: center;">
                <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                  MantraPath - Supporting your mental wellness journey
                </p>
              </div>
            </div>
          </body>
        </html>
        """
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = email
        
        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print(f"✅ Verification email sent to {email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending verification email: {e}")
        # For development - still show the verification link in console using API Gateway
        api_gateway_url = os.getenv("VITE_API_GATEWAY_URL", os.getenv("API_GATEWAY_URL", "http://139.84.213.185:8000"))
        verification_url = f"{api_gateway_url}/api/auth/verify-email/{token}"
        print("\n" + "="*80)
        print("🔐 EMAIL VERIFICATION REQUIRED (Email send failed)")
        print("="*80)
        print(f"User: {username} ({email})")
        print(f"Verification URL: {verification_url}")
        print(f"Verification Token: {token}")
        print("="*80 + "\n")
        return False

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def get_password_hash(password: str) -> str:
    """Alias for hash_password"""
    return hash_password(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[Any, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[Any, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_service_token(service_name: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a service-to-service authentication token
    
    Args:
        service_name: Name of the service requesting the token
        expires_delta: Token expiration time
    
    Returns:
        JWT token for service authentication
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)  # Long-lived for services
    
    to_encode = {
        "sub": f"service:{service_name}",
        "service": service_name,
        "type": "service_token",
        "exp": expire,
        "iat": datetime.utcnow(),
        "is_service": True
    }
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_service_token(token: str) -> Optional[dict]:
    """
    Verify a service-to-service authentication token
    
    Args:
        token: JWT token to verify
    
    Returns:
        Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if it's a service token
        if payload.get("type") != "service_token" or not payload.get("is_service"):
            return None
            
        return payload
    except JWTError:
        return None

def verify_token(token: str, expected_type: Optional[str] = None) -> Optional[Dict[Any, Any]]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check token type if specified
        if expected_type and payload.get("type") != expected_type:
            return None
            
        return payload
    except JWTError:
        return None

def extract_user_id(token: str) -> Optional[str]:
    """Extract user ID from token"""
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None

# FastAPI dependency for getting current user
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"user_id": user_id, "email": payload.get("email")}

def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token, but don't raise error if token is invalid"""
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if payload is None:
            return None
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        return {"user_id": user_id, "email": payload.get("email")}
    except:
        return None

def verify_user_access(user_id: str, resource_user_id: str) -> bool:
    """Verify that a user has access to a resource"""
    return user_id == resource_user_id

def require_moderator(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Require moderator role (for now, just check if user is authenticated)"""
    # TODO: Implement actual role checking when roles are properly implemented
    user = get_current_user(credentials)
    return user

def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Require admin role (for now, just check if user is authenticated)"""
    # TODO: Implement actual role checking when roles are properly implemented
    user = get_current_user(credentials)
    return user