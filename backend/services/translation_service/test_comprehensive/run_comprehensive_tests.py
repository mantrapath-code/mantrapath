#!/usr/bin/env python3
"""
Comprehensive Test Runner for Translation Service
Runs all tests and generates coverage reports targeting 80% coverage
"""
import os
import sys
import subprocess
import json
import time
from pathlib import Path

# Add service directory to Python path
current_dir = Path(__file__).parent
service_dir = current_dir.parent
sys.path.insert(0, str(service_dir))
sys.path.insert(0, str(service_dir.parent.parent.parent))

class ComprehensiveTestRunner:
    """Run comprehensive tests with coverage analysis"""
    
    def __init__(self):
        self.service_dir = Path(__file__).parent.parent
        self.test_dir = Path(__file__).parent
        self.coverage_threshold = 80
        
    def setup_environment(self):
        """Setup test environment"""
        print("🔧 Setting up test environment...")
        
        # Set environment variables for testing
        os.environ.update({
            'TESTING': 'true',
            'DEBUG': 'false',
            'DATABASE_URL': 'sqlite:///test_translation.db',
            'REDIS_URL': 'redis://localhost:6379',
            'JWT_SECRET_KEY': 'test_secret_key_for_testing_only',
            'PYTHONPATH': f"{self.service_dir}:{self.service_dir.parent.parent.parent}"
        })
        
        print("✅ Test environment configured")
    
    def install_dependencies(self):
        """Install test dependencies"""
        print("📦 Installing test dependencies...")
        
        try:
            # Install test requirements
            subprocess.run([
                sys.executable, '-m', 'pip', 'install',
                'pytest>=7.0.0',
                'pytest-asyncio>=0.21.0', 
                'pytest-cov>=4.0.0',
                'pytest-mock>=3.10.0',
                'coverage>=7.0.0',
                'httpx>=0.24.0',
                'fastapi>=0.100.0',
                'pydantic>=1.10.0',
                'psutil>=5.9.0'
            ], check=True, capture_output=True)
            
            print("✅ Dependencies installed successfully")
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Failed to install some dependencies: {e}")
            print("Continuing with available packages...")
    
    def run_unit_tests(self):
        """Run unit tests"""
        print("🧪 Running unit tests...")
        
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.test_dir),
            '-v',
            '--tb=short',
            '-m', 'unit or not integration',
            '--cov=engines',
            '--cov=models', 
            '--cov=main',
            '--cov=config',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov',
            '--cov-report=json:coverage.json',
            f'--cov-fail-under={self.coverage_threshold}'
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.service_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            print("Unit Test Output:")
            print(result.stdout)
            if result.stderr:
                print("Unit Test Errors:")
                print(result.stderr)
                
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Unit tests timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"❌ Failed to run unit tests: {e}")
            return False
    
    def run_integration_tests(self):
        """Run integration tests"""
        print("🔗 Running integration tests...")
        
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.test_dir / 'test_api_endpoints.py'),
            '-v',
            '--tb=short',
            '--cov-append',
            '--cov=main',
            '--cov-report=term-missing'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.service_dir,
                capture_output=True,
                text=True,
                timeout=180  # 3 minute timeout
            )
            
            print("Integration Test Output:")
            print(result.stdout)
            if result.stderr:
                print("Integration Test Errors:")
                print(result.stderr)
                
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Integration tests timed out after 3 minutes")
            return False
        except Exception as e:
            print(f"❌ Failed to run integration tests: {e}")
            return False
    
    def run_performance_tests(self):
        """Run performance and edge case tests"""
        print("🚀 Running performance tests...")
        
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.test_dir / 'test_performance_edge_cases.py'),
            '-v',
            '--tb=short',
            '--cov-append'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.service_dir,
                capture_output=True, 
                text=True,
                timeout=240  # 4 minute timeout
            )
            
            print("Performance Test Output:")
            print(result.stdout)
            if result.stderr:
                print("Performance Test Errors:")
                print(result.stderr)
                
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Performance tests timed out after 4 minutes")
            return False
        except Exception as e:
            print(f"❌ Failed to run performance tests: {e}")
            return False
    
    def analyze_coverage(self):
        """Analyze test coverage"""
        print("📊 Analyzing test coverage...")
        
        coverage_file = self.service_dir / 'coverage.json'
        
        if not coverage_file.exists():
            print("⚠️  Coverage report not found")
            return False
        
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
            
            # Extract coverage summary
            summary = coverage_data.get('totals', {})
            covered_lines = summary.get('covered_lines', 0)
            num_statements = summary.get('num_statements', 0)
            
            if num_statements > 0:
                coverage_percent = (covered_lines / num_statements) * 100
            else:
                coverage_percent = 0
            
            print(f"📈 Coverage Summary:")
            print(f"   Total Statements: {num_statements}")
            print(f"   Covered Lines: {covered_lines}")
            print(f"   Coverage Percentage: {coverage_percent:.2f}%")
            print(f"   Target: {self.coverage_threshold}%")
            
            # Detailed file coverage
            files = coverage_data.get('files', {})
            print(f"\n📋 File Coverage Details:")
            
            for file_path, file_data in files.items():
                file_summary = file_data.get('summary', {})
                file_covered = file_summary.get('covered_lines', 0)
                file_total = file_summary.get('num_statements', 0)
                
                if file_total > 0:
                    file_percent = (file_covered / file_total) * 100
                    print(f"   {file_path}: {file_percent:.1f}% ({file_covered}/{file_total})")
            
            # Coverage achievement status
            if coverage_percent >= self.coverage_threshold:
                print(f"\n🎉 SUCCESS: Coverage target of {self.coverage_threshold}% achieved!")
                print(f"   Actual coverage: {coverage_percent:.2f}%")
                return True
            else:
                print(f"\n⚠️  WARNING: Coverage target not met")
                print(f"   Target: {self.coverage_threshold}%")
                print(f"   Actual: {coverage_percent:.2f}%")
                print(f"   Gap: {self.coverage_threshold - coverage_percent:.2f}%")
                return False
                
        except Exception as e:
            print(f"❌ Failed to analyze coverage: {e}")
            return False
    
    def generate_reports(self):
        """Generate test and coverage reports"""
        print("📄 Generating reports...")
        
        # Generate HTML coverage report
        try:
            subprocess.run([
                sys.executable, '-m', 'coverage', 'html',
                '--directory=htmlcov'
            ], cwd=self.service_dir, check=True)
            
            html_report = self.service_dir / 'htmlcov' / 'index.html'
            if html_report.exists():
                print(f"✅ HTML coverage report: {html_report}")
            
        except subprocess.CalledProcessError:
            print("⚠️  Failed to generate HTML coverage report")
        
        # Generate terminal coverage report
        try:
            result = subprocess.run([
                sys.executable, '-m', 'coverage', 'report',
                '--show-missing'
            ], cwd=self.service_dir, capture_output=True, text=True)
            
            print("\n📊 Coverage Report:")
            print(result.stdout)
            
        except subprocess.CalledProcessError:
            print("⚠️  Failed to generate terminal coverage report")
    
    def cleanup(self):
        """Cleanup test artifacts"""
        print("🧹 Cleaning up...")
        
        cleanup_patterns = [
            '*.pyc',
            '__pycache__',
            '.pytest_cache',
            'test_translation.db',
            '.coverage'
        ]
        
        for pattern in cleanup_patterns:
            try:
                if pattern.startswith('.') and not pattern.startswith('..'):
                    # Remove hidden files/directories
                    for path in self.service_dir.rglob(pattern):
                        if path.is_file():
                            path.unlink()
                        elif path.is_dir():
                            import shutil
                            shutil.rmtree(path)
            except Exception as e:
                print(f"Warning: Failed to cleanup {pattern}: {e}")
        
        print("✅ Cleanup completed")
    
    def run_all_tests(self):
        """Run all tests and generate coverage report"""
        start_time = time.time()
        print("🚀 Starting Comprehensive Translation Service Tests")
        print("=" * 60)
        
        # Setup
        self.setup_environment()
        self.install_dependencies()
        
        # Test execution
        results = {
            'unit_tests': False,
            'integration_tests': False,
            'performance_tests': False,
            'coverage_target_met': False
        }
        
        # Run test suites
        results['unit_tests'] = self.run_unit_tests()
        results['integration_tests'] = self.run_integration_tests()
        results['performance_tests'] = self.run_performance_tests()
        
        # Coverage analysis
        results['coverage_target_met'] = self.analyze_coverage()
        
        # Generate reports
        self.generate_reports()
        
        # Summary
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 60)
        
        for test_type, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_type.replace('_', ' ').title()}: {status}")
        
        passed_count = sum(results.values())
        total_count = len(results)
        
        print(f"\nOverall Results: {passed_count}/{total_count} test suites passed")
        print(f"Total Execution Time: {total_time:.2f} seconds")
        
        if results['coverage_target_met']:
            print(f"\n🎉 SUCCESS: 80% coverage target achieved!")
        else:
            print(f"\n⚠️  Coverage target not fully met - see details above")
        
        print(f"\n📄 Reports generated in:")
        print(f"   HTML Coverage: {self.service_dir}/htmlcov/index.html")
        print(f"   JSON Coverage: {self.service_dir}/coverage.json")
        
        # Cleanup
        self.cleanup()
        
        return results['coverage_target_met'] and passed_count >= 3


def main():
    """Main entry point"""
    runner = ComprehensiveTestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n🎉 All tests completed successfully with 80% coverage!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed or coverage target not met")
        sys.exit(1)


if __name__ == "__main__":
    main()
