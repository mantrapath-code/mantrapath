#!/usr/bin/env python3
"""
Authentication Helper for Test Data Scripts
Provides centralized authentication for all test data generation scripts
"""

import requests
import json
import os
from typing import Optional, Dict, Any

class AuthHelper:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.current_token = None
        self.current_user = None
        
        # Test user credentials - UPDATE THESE WITH YOUR ACTUAL CREDENTIALS
        self.test_users = {
            "primary": {
                "email": "ssharma8132@gmail.com",      # UPDATE: Replace with your actual email
                "password": "Dev@#123",   # UPDATE: Replace with your actual password
                "username": "sachin",  # Add username
                "first_name": "Sachin",
                "last_name": "Sharma"
            },
            "secondary": {
                "email": "test.user@example.com",
                "password": "test123456",
                "username": "test_user",
                "first_name": "Test",
                "last_name": "User"
            }
        }
    
    def login(self, user_type: str = "primary") -> Optional[Dict[str, Any]]:
        """Login with test user credentials"""
        if user_type not in self.test_users:
            raise ValueError(f"Unknown user type: {user_type}")
        
        user_creds = self.test_users[user_type]
        
        try:
            # Login request
            response = self.session.post(
                f"{self.base_url}/login",
                json={
                    "email_or_username": user_creds["email"],
                    "password": user_creds["password"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                self.current_token = auth_data.get("access_token")
                
                # Update session headers first
                self.session.headers.update({
                    "Authorization": f"Bearer {self.current_token}",
                    "Content-Type": "application/json"
                })
                
                # Get user data from /me endpoint
                try:
                    me_response = self.session.get(f"{self.base_url}/me")
                    if me_response.status_code == 200:
                        self.current_user = me_response.json()
                    else:
                        print(f"⚠️ Could not fetch user data from /me: {me_response.status_code}")
                        self.current_user = {"id": "unknown"}
                except Exception as e:
                    print(f"⚠️ Error fetching user data: {e}")
                    self.current_user = {"id": "unknown"}
                
                print(f"✅ Successfully logged in as {user_creds['email']}")
                return auth_data
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return None
    
    def register_if_needed(self, user_type: str = "primary") -> bool:
        """Register user if they don't exist"""
        if user_type not in self.test_users:
            raise ValueError(f"Unknown user type: {user_type}")
        
        user_creds = self.test_users[user_type]
        
        try:
            # Try to register
            response = self.session.post(
                f"{self.base_url}/register",
                json={
                    "email": user_creds["email"],
                    "password": user_creds["password"],
                    "username": user_creds["username"],
                    "first_name": user_creds["first_name"],
                    "last_name": user_creds["last_name"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ User {user_creds['email']} registered successfully")
                return True
            elif response.status_code == 400 and "already exists" in response.text.lower():
                print(f"ℹ️ User {user_creds['email']} already exists")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get authenticated headers for API requests"""
        if not self.current_token:
            raise ValueError("No active session. Please login first.")
        
        return {
            "Authorization": f"Bearer {self.current_token}",
            "Content-Type": "application/json"
        }
    
    def get_user_id(self) -> str:
        """Get current user ID"""
        if not self.current_user:
            raise ValueError("No active session. Please login first.")
        
        return self.current_user.get("id") or self.current_user.get("user_id")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated API request"""
        if not self.current_token:
            raise ValueError("No active session. Please login first.")
        
        url = f"{self.base_url}{endpoint}"
        return self.session.request(method, url, **kwargs)
    
    def setup_user(self, user_type: str = "primary") -> bool:
        """Setup user (register if needed, then login)"""
        self.register_if_needed(user_type)
        return self.login(user_type) is not None

# Convenience function for quick setup
def get_authenticated_session(user_type: str = "primary") -> AuthHelper:
    """Get an authenticated session for test scripts"""
    auth = AuthHelper()
    if auth.setup_user(user_type):
        return auth
    else:
        raise Exception(f"Failed to setup authenticated session for {user_type}")

if __name__ == "__main__":
    # Test the auth helper
    print("Testing authentication helper...")
    auth = get_authenticated_session()
    print(f"User ID: {auth.get_user_id()}")
    print("Authentication helper working correctly!")
