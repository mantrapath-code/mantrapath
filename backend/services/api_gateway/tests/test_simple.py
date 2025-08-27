"""
Simple integration test to verify the gateway starts correctly
"""
import subprocess
import sys
import time
import requests
from pathlib import Path

def test_gateway_startup():
    """Test that the gateway starts without errors"""
    gateway_dir = Path(__file__).parent.parent
    src_dir = gateway_dir / "src"
    
    print(f"Testing gateway startup from: {gateway_dir}")
    print(f"Source directory: {src_dir}")
    
    # Start the gateway in background
    try:
        # Check if we can import the main module
        sys.path.insert(0, str(src_dir))
        
        from main import app
        print("✅ Successfully imported main application")
        
        # Test that FastAPI app is created
        assert app is not None
        print("✅ FastAPI app instance created")
        
        # Test that the app has the expected endpoints
        routes = [route.path for route in app.routes]
        expected_routes = ['/health', '/health/detailed', '/health/ready', '/health/live', '/metrics']
        
        for expected_route in expected_routes:
            assert any(expected_route in route for route in routes), f"Route {expected_route} not found"
        
        print("✅ All expected routes are registered")
        
        print("🎉 Gateway startup test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Gateway startup test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_gateway_startup()
    sys.exit(0 if success else 1)
