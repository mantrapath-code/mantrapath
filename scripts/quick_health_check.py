#!/usr/bin/env python3
"""
MantraPath Quick Health Monitor
Simple script to monitor service health and key functionality
"""

import requests
import json
from datetime import datetime
import sys

def health_check():
    """Quick health check of all MantraPath services"""
    services = {
        "API Gateway": "http://localhost:8000/health",
        "Auth Service": "http://localhost:8001/health", 
        "Profile Service": "http://localhost:8002/health",
        "Mood Service": "http://localhost:8003/health",
        "Chatbot Service": "http://localhost:8004/health",
        "Content Service": "http://localhost:8005/health",
        "Community Service": "http://localhost:8006/health",
        "Notification Service": "http://localhost:8007/health",
        "ML Service": "http://localhost:8008/health",
        "Media Service": "http://localhost:8009/health",
    }
    
    print(f"🔍 MantraPath Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    healthy = 0
    total = len(services)
    
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f"✅ {service:20} | Healthy")
                healthy += 1
            else:
                print(f"❌ {service:20} | Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {service:20} | Error: Connection failed")
    
    print("=" * 60)
    health_percentage = (healthy / total) * 100
    print(f"📊 Overall Health: {healthy}/{total} services ({health_percentage:.1f}%)")
    
    if health_percentage >= 90:
        print("🟢 System Status: EXCELLENT")
    elif health_percentage >= 75:
        print("🟡 System Status: GOOD")
    elif health_percentage >= 50:
        print("🟠 System Status: DEGRADED")
    else:
        print("🔴 System Status: CRITICAL")
    
    return health_percentage

def quick_login_test():
    """Test login functionality"""
    print("\n🔐 Testing Authentication...")
    
    try:
        response = requests.post(
            "http://localhost:8001/login",
            json={
                "email_or_username": "ssharma8132@gmail.com",
                "password": "Dev@#123"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Authentication: Working")
            return True
        else:
            print("❌ Authentication: Failed")
            return False
    except Exception as e:
        print("❌ Authentication: Error")
        return False

if __name__ == "__main__":
    health_percentage = health_check()
    auth_working = quick_login_test()
    
    print(f"\n📋 Quick Summary:")
    print(f"   Services Health: {health_percentage:.1f}%")
    print(f"   Authentication: {'✅ Working' if auth_working else '❌ Failed'}")
    
    # Exit with error code if system is not healthy
    if health_percentage < 80 or not auth_working:
        sys.exit(1)
    else:
        sys.exit(0)
