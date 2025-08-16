#!/usr/bin/env python3
"""
Test runner script for models_service
Runs comprehensive test suite with coverage reporting
"""

import sys
import subprocess
import os
from pathlib import Path

def run_tests():
    """Run the complete test suite"""
    print("🧪 Running Models Service Test Suite")
    print("=" * 50)
    
    # Set PYTHONPATH to include the service directory
    service_dir = Path(__file__).parent
    env = os.environ.copy()
    env['PYTHONPATH'] = str(service_dir)
    
    # Base pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=.",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml",
        "--cov-fail-under=80",
        "-v",
        "--tb=short"
    ]
    
    # Add additional options based on arguments
    if len(sys.argv) > 1:
        if "--fast" in sys.argv:
            cmd.extend(["-x", "--disable-warnings"])
        if "--verbose" in sys.argv:
            cmd.append("-vv")
        if "--debug" in sys.argv:
            cmd.extend(["--pdb", "--pdbcls=IPython.terminal.debugger:Pdb"])
        if "--unit" in sys.argv:
            cmd.extend(["-m", "unit"])
        if "--integration" in sys.argv:
            cmd.extend(["-m", "integration"])
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, env=env, cwd=service_dir)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            print("📊 Coverage report generated in htmlcov/index.html")
        else:
            print(f"\n❌ Tests failed with exit code {result.returncode}")
        
        return result.returncode
    
    except KeyboardInterrupt:
        print("\n⚠️ Test run interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test run failed: {e}")
        return 1

def run_specific_test():
    """Run a specific test file or test function"""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py <test_file_or_function>")
        return 1
    
    test_target = sys.argv[1]
    
    # Set PYTHONPATH
    service_dir = Path(__file__).parent
    env = os.environ.copy()
    env['PYTHONPATH'] = str(service_dir)
    
    cmd = [
        sys.executable, "-m", "pytest",
        test_target,
        "--cov=.",
        "--cov-report=term-missing",
        "-v"
    ]
    
    try:
        result = subprocess.run(cmd, env=env, cwd=service_dir)
        return result.returncode
    except Exception as e:
        print(f"Failed to run test: {e}")
        return 1

def show_coverage():
    """Show coverage report"""
    service_dir = Path(__file__).parent
    coverage_file = service_dir / "htmlcov" / "index.html"
    
    if coverage_file.exists():
        print(f"📊 Opening coverage report: {coverage_file}")
        if sys.platform.startswith('darwin'):  # macOS
            subprocess.run(["open", str(coverage_file)])
        elif sys.platform.startswith('linux'):  # Linux
            subprocess.run(["xdg-open", str(coverage_file)])
        elif sys.platform.startswith('win'):  # Windows
            subprocess.run(["start", str(coverage_file)], shell=True)
        else:
            print(f"Please open {coverage_file} in your browser")
    else:
        print("❌ Coverage report not found. Run tests first.")

def main():
    """Main test runner"""
    if len(sys.argv) > 1 and sys.argv[1] == "--coverage":
        show_coverage()
        return 0
    
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        return run_specific_test()
    
    return run_tests()

if __name__ == "__main__":
    sys.exit(main())
