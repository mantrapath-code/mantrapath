#!/usr/bin/env python3
"""
Debug JWT token validation across services
"""
import os
import jwt
from datetime import datetime, timedelta

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Get the JWT secret from environment
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
ALGORITHM = "HS256"

print("=== JWT Debug Information ===")
print(f"JWT_SECRET_KEY (first 20 chars): {JWT_SECRET[:20]}...")
print(f"Algorithm: {ALGORITHM}")
print()

# Test token from the login response
test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMGE4MjExZi1hNWRjLTQ2MjktOTA2MS0yMmE3MjgxMTJhYWIiLCJlbWFpbCI6InNoYXJtYXNhY2hpbjgxMzJAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJleHAiOjE3NTQxNDIzOTAsInR5cGUiOiJhY2Nlc3MifQ.nA4h-MgPMw5vND3CKMqKY8eSlnhMPMlqnjJFQYO2PoM"

print("=== Testing Token Validation ===")
try:
    # Decode without verification first to see payload
    payload_unverified = jwt.decode(test_token, options={"verify_signature": False})
    print("Unverified payload:", payload_unverified)
    print()
    
    # Check expiration
    exp_timestamp = payload_unverified.get('exp', 0)
    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    current_time = datetime.now()
    
    print(f"Token expires at: {exp_datetime}")
    print(f"Current time: {current_time}")
    print(f"Token expired: {current_time > exp_datetime}")
    print()
    
    # Now try to verify with secret
    payload_verified = jwt.decode(test_token, JWT_SECRET, algorithms=[ALGORITHM])
    print("✅ Token verification successful!")
    print("Verified payload:", payload_verified)
    
except jwt.ExpiredSignatureError:
    print("❌ Token has expired")
except jwt.InvalidTokenError as e:
    print(f"❌ Token validation failed: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print()
print("=== Creating New Token for Testing ===")
try:
    # Create a new token for testing
    new_payload = {
        "sub": "10a8211f-a5dc-4629-9061-22a728112aab",
        "email": "sharmasachin8132@gmail.com",
        "role": "user",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "type": "access"
    }
    
    new_token = jwt.encode(new_payload, JWT_SECRET, algorithm=ALGORITHM)
    print(f"New token created: {new_token[:50]}...")
    
    # Verify the new token
    verified_payload = jwt.decode(new_token, JWT_SECRET, algorithms=[ALGORITHM])
    print("✅ New token verified successfully!")
    print("New token payload:", verified_payload)
    
except Exception as e:
    print(f"❌ Error creating/verifying new token: {e}")
