#!/usr/bin/env python3
"""
Test SMTP configuration for MantraPath
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_smtp_connection():
    """Test SMTP connection and email sending"""
    try:
        # Load environment variables
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        from_email = os.getenv("FROM_EMAIL", smtp_username)
        
        print("🔧 SMTP Configuration Test")
        print("=" * 50)
        print(f"SMTP Server: {smtp_server}")
        print(f"SMTP Port: {smtp_port}")
        print(f"SMTP Username: {smtp_username}")
        print(f"From Email: {from_email}")
        print(f"Password Length: {len(smtp_password)} characters")
        print("=" * 50)
        
        if not smtp_username or not smtp_password:
            print("❌ SMTP credentials not configured!")
            print("Please set SMTP_USERNAME and SMTP_PASSWORD environment variables")
            return False
        
        # Test connection
        print("🔗 Testing SMTP connection...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("✅ Connected to SMTP server")
            
            print("🔐 Starting TLS...")
            server.starttls()
            print("✅ TLS started successfully")
            
            print("🔑 Authenticating...")
            server.login(smtp_username, smtp_password)
            print("✅ Authentication successful")
            
            # Send a test email
            test_email = "ssharma8132@outlook.com"  # Replace with your test email
            
            msg = MIMEMultipart()
            msg['Subject'] = "MantraPath SMTP Test"
            msg['From'] = from_email
            msg['To'] = test_email
            
            body = """
            <html>
              <body>
                <h2>MantraPath SMTP Test</h2>
                <p>This is a test email to verify SMTP configuration.</p>
                <p>If you receive this email, SMTP is working correctly!</p>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            print(f"📧 Sending test email to {test_email}...")
            server.send_message(msg)
            print("✅ Test email sent successfully!")
            
        print("\n🎉 SMTP configuration is working correctly!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication Error: {e}")
        print("💡 Check your Gmail App Password or enable 2FA + App Passwords")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ SMTP Connection Error: {e}")
        print("💡 Check your SMTP server and port settings")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded environment variables from .env")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment variables")
    
    test_smtp_connection()
