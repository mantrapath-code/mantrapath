#!/usr/bin/env python3
"""
MantraPath Authentication Enhancement Setup Script

This script sets up the enhanced authentication system with:
- Email verification
- Strong password requirements  
- Login with email or username
- Non-unique usernames
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     MantraPath Authentication Enhancement                     ║
║                                                                              ║
║  🔐 Enhanced Security Features:                                              ║
║  • Email verification for new registrations                                 ║
║  • Strong password requirements (8+ chars, mixed case, numbers, symbols)    ║
║  • Login with email OR username                                             ║
║  • Non-unique usernames (email remains unique)                              ║
║  • Improved error messages and user experience                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

def check_requirements():
    """Check if required dependencies are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python packages
    required_packages = [
        'fastapi', 'sqlalchemy', 'pydantic', 'passlib', 
        'python-jose', 'pyjwt', 'redis', 'uvicorn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Installing missing packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages)
    else:
        print("✅ All required packages are installed")

def setup_environment():
    """Setup environment configuration"""
    print("🔧 Setting up environment configuration...")
    
    env_file = Path("backend/.env")
    env_example = Path("backend/.env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📋 Creating .env file from .env.example...")
        shutil.copy(env_example, env_file)
        print("⚠️  Please update backend/.env with your SMTP credentials for email verification")
    else:
        print("✅ Environment file already exists")

def run_migration():
    """Run database migration"""
    print("🗄️  Running database migration...")
    
    migration_script = Path("backend/scripts/migrate_auth_enhancement.py")
    if migration_script.exists():
        try:
            result = subprocess.run([sys.executable, str(migration_script)], 
                                  capture_output=True, text=True, cwd="backend")
            if result.returncode == 0:
                print("✅ Database migration completed successfully")
            else:
                print(f"❌ Migration failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Migration error: {e}")
    else:
        print("⚠️  Migration script not found")

def display_configuration_help():
    """Display configuration instructions"""
    print("""
📧 EMAIL CONFIGURATION REQUIRED:

To enable email verification, update your backend/.env file with:

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@mantrapath.com
APP_URL=http://localhost:3000

For Gmail:
1. Enable 2-factor authentication
2. Generate an "App Password" for MantraPath
3. Use the app password in SMTP_PASSWORD

For other providers:
- Outlook: smtp-mail.outlook.com:587
- Yahoo: smtp.mail.yahoo.com:587
- Custom SMTP: Use your provider's settings

⚠️  Without email configuration, users will be created as verified (development mode).
    """)

def display_feature_overview():
    """Display the new features"""
    print("""
🎯 NEW AUTHENTICATION FEATURES:

📧 Email Verification:
   • New users receive verification emails
   • Must verify before first login
   • Resend verification option available

🔒 Strong Password Requirements:
   • Minimum 8 characters
   • At least 1 uppercase letter
   • At least 1 lowercase letter  
   • At least 1 number
   • At least 1 special character
   • Real-time strength indicator

👤 Flexible Login:
   • Login with email OR username
   • Usernames no longer need to be unique
   • Email remains unique for account recovery

🎨 Enhanced UI/UX:
   • Password strength indicator
   • Email verification modal
   • Better error messages
   • Verification status tracking

🛡️  Security Improvements:
   • JWT token type validation
   • Verification token expiration
   • Rate limiting support ready
   • Audit trail preparation
    """)

def main():
    os.chdir(Path(__file__).parent.parent)  # Change to project root
    
    print_banner()
    
    print("🚀 Starting MantraPath Authentication Enhancement Setup...\n")
    
    check_requirements()
    setup_environment()
    run_migration()
    
    print("\n" + "="*80)
    print("🎉 SETUP COMPLETE!")
    print("="*80)
    
    display_configuration_help()
    display_feature_overview()
    
    print("""
🚀 NEXT STEPS:

1. Configure email settings in backend/.env
2. Start backend services: ./backend/start-dev.sh
3. Start frontend: cd frontend && npm run dev  
4. Test registration with a real email address
5. Check email for verification link

📚 For more information, see:
   • docs/AUTHENTICATION_TEST_REPORT.md
   • backend/SETUP.md
   • README.md

Happy coding! 🎊
    """)

if __name__ == "__main__":
    main()
