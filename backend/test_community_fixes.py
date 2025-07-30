#!/usr/bin/env python3
"""
Test script to verify community service likes and comments persistence fixes
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
COMMUNITY_URL = "http://localhost:8006"

def test_user_auth() -> Dict[str, Any]:
    """Test user authentication and get token"""
    print("Testing authentication...")
    
    # Try to register a test user
    register_data = {
        "email": "test@example.com", 
        "username": "testuser",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        if response.status_code in [200, 201]:
            print("✅ User registered successfully")
        elif response.status_code == 400:
            print("ℹ️  User already exists, proceeding with login")
        else:
            print(f"❌ Registration failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    # Login with JSON data
    login_data = {"email": "test@example.com", "password": "testpass123"}
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful")
            return {"Authorization": f"Bearer {token_data.get('access_token')}"}
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return {}
    except Exception as e:
        print(f"❌ Login error: {e}")
        return {}

def test_forums(headers: Dict[str, str]) -> str:
    """Test forum functionality and return a forum ID"""
    print("\nTesting forums...")
    
    try:
        response = requests.get(f"{COMMUNITY_URL}/forums", headers=headers)
        if response.status_code == 200:
            forums = response.json()
            print(f"✅ Retrieved {len(forums)} forums")
            if forums:
                forum_id = forums[0]["id"]
                print(f"ℹ️  Using forum: {forums[0]['name']} (ID: {forum_id})")
                return forum_id
            else:
                print("❌ No forums found")
                return ""
        else:
            print(f"❌ Failed to get forums: {response.status_code}")
            return ""
    except Exception as e:
        print(f"❌ Forums error: {e}")
        return ""

def test_forum_membership(forum_id: str, headers: Dict[str, str]) -> bool:
    """Test joining a forum"""
    print(f"\nTesting forum membership...")
    
    try:
        # Try to join the forum
        response = requests.post(f"{COMMUNITY_URL}/forums/{forum_id}/join", headers=headers)
        if response.status_code in [200, 400]:  # 400 if already joined
            print("✅ Forum join/membership working")
            return True
        else:
            print(f"❌ Failed to join forum: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Forum membership error: {e}")
        return False

def test_thread_creation(forum_id: str, headers: Dict[str, str]) -> str:
    """Test creating a thread and return thread ID"""
    print(f"\nTesting thread creation...")
    
    thread_data = {
        "forum_id": forum_id,
        "title": "Test Thread for Persistence",
        "content": "This is a test thread to verify likes and comments persist properly after our fixes."
    }
    
    try:
        response = requests.post(f"{COMMUNITY_URL}/forums/thread", json=thread_data, headers=headers)
        if response.status_code in [200, 201]:
            thread = response.json()
            thread_id = thread["id"]
            print(f"✅ Thread created successfully (ID: {thread_id})")
            return thread_id
        else:
            print(f"❌ Failed to create thread: {response.status_code}")
            print(f"Response: {response.text}")
            return ""
    except Exception as e:
        print(f"❌ Thread creation error: {e}")
        return ""

def test_likes_persistence(thread_id: str, headers: Dict[str, str]) -> bool:
    """Test that likes persist properly"""
    print(f"\nTesting likes persistence...")
    
    like_data = {
        "content_type": "thread",
        "content_id": thread_id
    }
    
    try:
        # Like the thread
        response = requests.post(f"{COMMUNITY_URL}/forums/like", json=like_data, headers=headers)
        if response.status_code == 200:
            like_result = response.json()
            print(f"✅ Like added: {like_result['message']}")
            print(f"ℹ️  Like count: {like_result['like_count']}")
            
            # Check like status
            response = requests.get(f"{COMMUNITY_URL}/forums/like/thread/{thread_id}", headers=headers)
            if response.status_code == 200:
                status = response.json()
                if status["liked"] and status["like_count"] > 0:
                    print("✅ Like persisted correctly!")
                    return True
                else:
                    print("❌ Like not persisted correctly")
                    return False
            else:
                print(f"❌ Failed to check like status: {response.status_code}")
                return False
        else:
            print(f"❌ Failed to like thread: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Likes persistence error: {e}")
        return False

def test_comments_persistence(thread_id: str, headers: Dict[str, str]) -> bool:
    """Test that comments persist properly"""
    print(f"\nTesting comments persistence...")
    
    reply_data = {
        "content": "This is a test reply to verify comments persistence after our fixes."
    }
    
    try:
        # Add a reply
        response = requests.post(f"{COMMUNITY_URL}/forums/thread/{thread_id}/reply", json=reply_data, headers=headers)
        if response.status_code in [200, 201]:
            reply = response.json()
            print(f"✅ Reply added successfully (ID: {reply['id']})")
            
            # Get thread replies
            response = requests.get(f"{COMMUNITY_URL}/forums/thread/{thread_id}/replies", headers=headers)
            if response.status_code == 200:
                replies = response.json()
                if len(replies) > 0:
                    print(f"✅ Found {len(replies)} replies - comments persisted correctly!")
                    return True
                else:
                    print("❌ No replies found - comments not persisted")
                    return False
            else:
                print(f"❌ Failed to get replies: {response.status_code}")
                return False
        else:
            print(f"❌ Failed to add reply: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Comments persistence error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Community Service Persistence Fixes")
    print("=" * 50)
    
    # Test authentication
    headers = test_user_auth()
    if not headers:
        print("❌ Authentication failed - cannot continue tests")
        return
    
    # Test forums
    forum_id = test_forums(headers)
    if not forum_id:
        print("❌ No forums available - cannot continue tests")
        return
    
    # Test forum membership
    if not test_forum_membership(forum_id, headers):
        print("❌ Forum membership failed - cannot continue tests")
        return
    
    # Test thread creation
    thread_id = test_thread_creation(forum_id, headers)
    if not thread_id:
        print("❌ Thread creation failed - cannot continue tests")
        return
    
    # Test persistence
    likes_ok = test_likes_persistence(thread_id, headers)
    comments_ok = test_comments_persistence(thread_id, headers)
    
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary:")
    print(f"✅ Likes Persistence: {'PASS' if likes_ok else 'FAIL'}")
    print(f"✅ Comments Persistence: {'PASS' if comments_ok else 'FAIL'}")
    
    if likes_ok and comments_ok:
        print("\n🎉 All persistence tests PASSED! The fixes are working correctly.")
    else:
        print("\n⚠️  Some tests FAILED. The persistence issues may still exist.")

if __name__ == "__main__":
    main()
