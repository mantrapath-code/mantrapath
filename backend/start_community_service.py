#!/usr/bin/env python3
"""
Simple script to start the community service
"""
import sys
import os
import subprocess

def main():
    # Ensure we're in the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Activate virtual environment
    venv_path = os.path.join(backend_dir, 'venv311', 'bin', 'activate')
    if os.path.exists(venv_path):
        print("🔧 Using Python 3.11 virtual environment...")
        # Run with activated venv
        python_path = os.path.join(backend_dir, 'venv311', 'bin', 'python')
    else:
        print("🔧 Using system Python...")
        python_path = 'python3.11'
    
    print("🚀 Starting Community Service...")
    
    try:
        # Start community service
        cmd = [python_path, '-m', 'services.community_service.main']
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start community service: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Community service stopped")
        return 0

if __name__ == "__main__":
    sys.exit(main())
