"""
Migration wrapper for backward compatibility
This file imports from the new unified authentication system
while maintaining compatibility with existing imports
"""

# Import all functions from the unified auth system
from auth_unified import *

# Additional legacy functions that may still be needed
import os
import secrets
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Email configuration for verification
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

def validate_password_strength(password: str) -> bool:
    """Validate password meets minimum requirements"""
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return has_upper and has_lower and has_digit and has_special

def generate_verification_token() -> str:
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

def send_verification_email(email: str, token: str, user_name: str = None) -> bool:
    """Send verification email to user"""
    try:
        if not SMTP_EMAIL or not SMTP_PASSWORD:
            logger.warning("SMTP configuration not found, skipping email verification")
            return False
        
        # Create verification URL
        verification_url = f"{FRONTEND_URL}/auth/verify-email?token={token}"
        
        # Create email content
        subject = "Verify your MantraPath account"
        
        html_body = f"""
        <html>
        <body>
            <h2>Welcome to MantraPath!</h2>
            <p>Hi {user_name or 'there'},</p>
            <p>Thank you for registering with MantraPath. Please click the link below to verify your email address:</p>
            <p><a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
            <p>Or copy and paste this link into your browser:</p>
            <p>{verification_url}</p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create an account, please ignore this email.</p>
            <p>Best regards,<br>The MantraPath Team</p>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to MantraPath!
        
        Hi {user_name or 'there'},
        
        Thank you for registering with MantraPath. Please visit the following link to verify your email address:
        
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        The MantraPath Team
        """
        
        # Create message
        msg = MimeMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_EMAIL
        msg['To'] = email
        
        # Add both text and HTML parts
        msg.attach(MimeText(text_body, 'plain'))
        msg.attach(MimeText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Verification email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {e}")
        return False

# Maintain backward compatibility aliases
get_password_hash = hash_password