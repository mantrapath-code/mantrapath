"""
Test runner script for Action Orchestrator Service
Provides easy commands for running different test suites
"""
import subprocess
import sys
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    print(f"Return code: {result.returncode}")
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Test runner for Action Orchestrator Service")
    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "all", "coverage", "quick"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--file", "-f",
        help="Run specific test file"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = "python -m pytest"
    if args.verbose:
        base_cmd += " -v"
    
    success = True
    
    if args.test_type == "unit":
        cmd = f"{base_cmd} tests/unit/"
        success = run_command(cmd, "Unit Tests")
    
    elif args.test_type == "integration":
        cmd = f"{base_cmd} tests/integration/"
        success = run_command(cmd, "Integration Tests")
    
    elif args.test_type == "all":
        # Run all tests
        cmd = f"{base_cmd} tests/"
        success = run_command(cmd, "All Tests")
    
    elif args.test_type == "coverage":
        # Run tests with coverage
        cmd = f"{base_cmd} tests/ --cov=src --cov-report=term-missing --cov-report=html"
        success = run_command(cmd, "Tests with Coverage")
        
        if success:
            print("\n" + "="*60)
            print("Coverage report generated in htmlcov/index.html")
            print("="*60)
    
    elif args.test_type == "quick":
        # Run quick unit tests only
        cmd = f"{base_cmd} tests/unit/ -x"  # Stop on first failure
        success = run_command(cmd, "Quick Unit Tests")
    
    if args.file:
        # Run specific test file
        cmd = f"{base_cmd} {args.file}"
        success = run_command(cmd, f"Test File: {args.file}")
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
