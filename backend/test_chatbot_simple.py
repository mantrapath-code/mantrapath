#!/usr/bin/env python3
"""
Simple test script for chatbot service
"""
import requests
import json

def test_chatbot():
    """Test the chatbot service"""
    
    # Test health endpoint first
    print("Testing health endpoint...")
    health_response = requests.get("http://localhost:8004/health")
    print(f"Health Status: {health_response.status_code}")
    print(f"Health Response: {health_response.text}")
    
    # Get authentication token
    print("\nGetting authentication token...")
    auth_payload = {
        "email_or_username": "sa@gmail.com",
        "password": "Dev@#123"
    }
    
    auth_response = requests.post(
        "http://localhost:8000/auth/login",
        json=auth_payload
    )
    
    if auth_response.status_code == 200:
        token_data = auth_response.json()
        print(f"Token response: {token_data}")
        
        # Handle different response formats
        if isinstance(token_data, dict) and "body" in token_data:
            if isinstance(token_data["body"], str):
                import json
                body_data = json.loads(token_data["body"])
                access_token = body_data["access_token"]
            else:
                access_token = token_data["body"]["access_token"]
        elif isinstance(token_data, dict) and "access_token" in token_data:
            access_token = token_data["access_token"]
        else:
            print(f"Unexpected token format: {token_data}")
            return
            
        print(f"Token acquired successfully")
        
        # Test chatbot intelligent endpoint
        print("\nTesting chatbot intelligent endpoint...")
        chat_payload = {
            "message": "Hello, how are you today?",
            "language": "auto"
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            chat_response = requests.post(
                "http://localhost:8004/chat/intelligent",
                json=chat_payload,
                headers=headers,
                timeout=30
            )
            
            print(f"Chat Response Status: {chat_response.status_code}")
            print(f"Chat Response: {chat_response.text}")
            
        except Exception as e:
            print(f"Error making chat request: {e}")
            
        # Test Hindi message
        print("\nTesting Hindi language detection...")
        hindi_payload = {
            "message": "मैं आज बहुत खुश हूं",
            "language": "auto"
        }
        
        try:
            hindi_response = requests.post(
                "http://localhost:8004/chat/intelligent",
                json=hindi_payload,
                headers=headers,
                timeout=30
            )
            
            print(f"Hindi Response Status: {hindi_response.status_code}")
            print(f"Hindi Response: {hindi_response.text}")
            
        except Exception as e:
            print(f"Error making Hindi request: {e}")
    else:
        print(f"Authentication failed: {auth_response.status_code}")
        print(f"Auth Response: {auth_response.text}")

if __name__ == "__main__":
    test_chatbot()
