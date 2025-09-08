"""
Simple test execution script for Voice Service
Run specific test scenarios quickly
"""
import os
import sys
import subprocess
from pathlib import Path

def run_basic_tests():
    """Run basic unit tests"""
    print("🧪 Running Basic Unit Tests...")
    voice_service_dir = Path(__file__).parent.parent
    
    # Run pytest with basic options
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/unit/",
        "-v",
        "--tb=short",
        "--disable-warnings"
    ]
    
    result = subprocess.run(cmd, cwd=voice_service_dir)
    return result.returncode == 0

def run_indian_language_tests():
    """Run tests specific to Indian languages"""
    print("🇮🇳 Running Indian Language Tests...")
    voice_service_dir = Path(__file__).parent.parent
    
    # Run specific test patterns
    test_patterns = [
        "test_detect_hindi",
        "test_detect_bengali", 
        "test_detect_tamil",
        "test_all_indian_languages",
        "test_code_switching"
    ]
    
    for pattern in test_patterns:
        print(f"  Testing: {pattern}")
        cmd = [
            sys.executable, "-m", "pytest",
            "-k", pattern,
            "-v",
            "--tb=line"
        ]
        
        result = subprocess.run(cmd, cwd=voice_service_dir)
        if result.returncode != 0:
            print(f"  ❌ Failed: {pattern}")
            return False
        else:
            print(f"  ✅ Passed: {pattern}")
    
    return True

def run_integration_tests():
    """Run integration tests (requires running service)"""
    print("🔗 Running Integration Tests...")
    voice_service_dir = Path(__file__).parent.parent
    
    # Check if service is running
    try:
        import requests
        response = requests.get("http://localhost:8010/health", timeout=5)
        if response.status_code != 200:
            print("❌ Voice service not running on localhost:8010")
            return False
    except Exception:
        print("❌ Voice service not accessible")
        return False
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/integration/",
        "-v",
        "--tb=short"
    ]
    
    result = subprocess.run(cmd, cwd=voice_service_dir)
    return result.returncode == 0

def check_dependencies():
    """Check if all test dependencies are installed"""
    required_packages = [
        "pytest",
        "pytest-asyncio", 
        "aiohttp",
        "requests"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing test dependencies: {', '.join(missing_packages)}")
        print("Install with: pip install pytest pytest-asyncio aiohttp requests")
        return False
    
    return True

def main():
    """Main test function"""
    if not check_dependencies():
        return 1
    
    # Get test type from command line
    test_type = sys.argv[1] if len(sys.argv) > 1 else "basic"
    
    if test_type == "basic":
        success = run_basic_tests()
    elif test_type == "indian":
        success = run_indian_language_tests()
    elif test_type == "integration":
        success = run_integration_tests()
    elif test_type == "all":
        success = (
            run_basic_tests() and
            run_indian_language_tests() and
            run_integration_tests()
        )
    else:
        print("Usage: python test_runner.py [basic|indian|integration|all]")
        return 1
    
    if success:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
