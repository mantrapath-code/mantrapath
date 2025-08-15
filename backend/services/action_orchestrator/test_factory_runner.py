#!/usr/bin/env python3
"""
Standalone test runner for orchestrator factory to avoid Pydantic import conflicts
"""
import sys
import os
import subprocess

def run_factory_tests():
    """Run orchestrator factory tests in isolation"""
    print("🧪 Running Orchestrator Factory Tests...")
    
    # Run tests with fresh Python process to avoid Pydantic conflicts
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/test_orchestrator_factory.py::TestOrchestratorFactory", 
        "--cov=src.services.orchestrator_factory",
        "--cov-report=term-missing",
        "--tb=short",
        "-v"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        print(f"Exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Tests passed successfully!")
        else:
            print("❌ Tests failed or had errors")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_factory_tests()
    sys.exit(0 if success else 1)
