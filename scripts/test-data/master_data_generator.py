#!/usr/bin/env python3
"""
Master Test Data Generation Script
Orchestrates all test data generation across services with proper authentication
"""

import sys
import os
import subprocess
from datetime import datetime

# Add parent directory to path for auth_helper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth_helper import get_authenticated_session

class MasterDataGenerator:
    def __init__(self):
        self.scripts_base = "/Users/sachin/Documents/GitHub/mantrapath/scripts/test-data"
        self.services = {
            "mood": {
                "name": "Mood Service",
                "script": f"{self.scripts_base}/mood-service/generate_mood_data.py",
                "description": "Generate realistic mood entries with patterns and streaks"
            },
            "journal": {
                "name": "Journal Service", 
                "script": f"{self.scripts_base}/journal-service/generate_journal_data.py",
                "description": "Create mood-correlated journal entries with themes"
            },
            "community": {
                "name": "Community Service",
                "script": f"{self.scripts_base}/community-service/generate_community_data.py", 
                "description": "Generate community posts, comments, and interactions"
            },
            "ml": {
                "name": "ML Service Tester",
                "script": f"{self.scripts_base}/ml-service/test_ml_insights.py",
                "description": "Test ML endpoints and validate insights data flow"
            }
        }
    
    def check_prerequisites(self):
        """Check if all services are running and auth works"""
        print("🔍 Checking prerequisites...")
        
        try:
            # Test authentication
            auth = get_authenticated_session("primary")
            print("✅ Authentication: Working")
            
            # Test API connectivity
            response = auth.make_request("GET", "/health")
            if response.status_code == 200:
                print("✅ API Gateway: Accessible")
            else:
                print(f"⚠️ API Gateway: Status {response.status_code}")
            
            # Test individual services
            services_to_test = [
                ("/me", "Auth Service"),
                ("/health", "Mood Service"),
                ("/health", "Content Service"),
                ("/health", "Community Service"),
                ("/ml/health", "ML Service")
            ]
            
            for endpoint, service_name in services_to_test:
                try:
                    response = auth.make_request("GET", endpoint)
                    if response.status_code == 200:
                        print(f"✅ {service_name}: Available")
                    else:
                        print(f"⚠️ {service_name}: Status {response.status_code}")
                except Exception as e:
                    print(f"❌ {service_name}: Error - {str(e)[:50]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Prerequisites check failed: {e}")
            return False
    
    def run_service_script(self, service_key: str, auto_choice: str = None):
        """Run a specific service's test data script"""
        if service_key not in self.services:
            print(f"❌ Unknown service: {service_key}")
            return False
        
        service = self.services[service_key]
        script_path = service["script"]
        
        if not os.path.exists(script_path):
            print(f"❌ Script not found: {script_path}")
            return False
        
        print(f"\n🚀 Running {service['name']} data generation...")
        print(f"📝 {service['description']}")
        
        try:
            # Make script executable
            os.chmod(script_path, 0o755)
            
            # Run the script
            if auto_choice:
                # Run with automated input
                process = subprocess.Popen(
                    ["python3", script_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=os.path.dirname(script_path)
                )
                stdout, stderr = process.communicate(input=auto_choice + "\n")
                
                print(stdout)
                if stderr:
                    print(f"⚠️ Errors: {stderr}")
                
                return process.returncode == 0
            else:
                # Run interactively
                result = subprocess.run(
                    ["python3", script_path],
                    cwd=os.path.dirname(script_path)
                )
                return result.returncode == 0
                
        except Exception as e:
            print(f"❌ Error running {service['name']} script: {e}")
            return False
    
    def generate_comprehensive_dataset(self):
        """Generate a comprehensive dataset across all services"""
        print("\n🎯 Generating Comprehensive Test Dataset...")
        print("=" * 60)
        
        # Define the automated choices for comprehensive generation
        auto_choices = {
            "mood": "6",      # All patterns (comprehensive)
            "journal": "5",   # Comprehensive journal data
            "community": "5", # Comprehensive community data
            "ml": "5"         # Full validation suite
        }
        
        results = {}
        
        for service_key, choice in auto_choices.items():
            print(f"\n📊 Generating {self.services[service_key]['name']} data...")
            success = self.run_service_script(service_key, choice)
            results[service_key] = success
            
            if success:
                print(f"✅ {self.services[service_key]['name']}: Completed successfully")
            else:
                print(f"❌ {self.services[service_key]['name']}: Failed")
        
        # Summary
        successful = sum(results.values())
        total = len(results)
        
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE DATASET GENERATION SUMMARY")
        print("=" * 60)
        
        for service_key, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{self.services[service_key]['name']}: {status}")
        
        print(f"\nOverall: {successful}/{total} services completed successfully")
        
        if successful == total:
            print("🎉 All test data generated successfully!")
            print("\n💡 Next steps:")
            print(f"   • Visit {os.getenv('PROTOCOL', 'http')}://{os.getenv('DOMAIN', 'localhost')}:{os.getenv('FRONTEND_PORT', '5173')} to see the insights")
            print("   • Check 'Best Moments' section for real data")
            print("   • Look for populated mood streaks and energy peaks")
        else:
            print("⚠️ Some services failed. Check logs above for details.")
    
    def interactive_menu(self):
        """Show interactive menu for selective data generation"""
        while True:
            print("\n" + "=" * 60)
            print("🎛️  MANTRAPATH TEST DATA GENERATOR")
            print("=" * 60)
            print("0. Check prerequisites")
            print("1. Generate mood service data")
            print("2. Generate journal service data") 
            print("3. Generate community service data")
            print("4. Test ML service and insights")
            print("5. Generate comprehensive dataset (ALL)")
            print("6. Exit")
            print("=" * 60)
            
            choice = input("Enter your choice (0-6): ").strip()
            
            if choice == "0":
                self.check_prerequisites()
            elif choice == "1":
                self.run_service_script("mood")
            elif choice == "2":
                self.run_service_script("journal")
            elif choice == "3":
                self.run_service_script("community")
            elif choice == "4":
                self.run_service_script("ml")
            elif choice == "5":
                self.generate_comprehensive_dataset()
            elif choice == "6":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")

def main():
    """Main function"""
    print("🚀 MantraPath Test Data Generation Suite")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    generator = MasterDataGenerator()
    
    # Check if we should run in automated mode
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        print("\n🤖 Running in automated mode...")
        if generator.check_prerequisites():
            generator.generate_comprehensive_dataset()
        else:
            print("❌ Prerequisites check failed. Cannot proceed.")
    else:
        # Interactive mode
        if generator.check_prerequisites():
            generator.interactive_menu()
        else:
            print("❌ Prerequisites check failed.")
            print("💡 Make sure Docker Compose services are running:")
            print("   cd /path/to/mantrapath/backend && docker-compose up -d")

if __name__ == "__main__":
    main()
