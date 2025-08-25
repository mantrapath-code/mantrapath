"""
Debug script to test imports
"""
import sys
sys.path.append('/app')
sys.path.append('/app/shared')

print("1. Testing basic shared import...")
try:
    import shared
    print("✓ shared module imported successfully")
except Exception as e:
    print(f"✗ Failed to import shared: {e}")
    exit(1)

print("2. Testing shared.models import...")
try:
    import shared.models
    print("✓ shared.models imported successfully")
except Exception as e:
    print(f"✗ Failed to import shared.models: {e}")
    exit(1)

print("3. Testing specific UserProfile import...")
try:
    from shared.models import UserProfile
    print("✓ UserProfile imported successfully")
    print(f"UserProfile: {UserProfile}")
except Exception as e:
    print(f"✗ Failed to import UserProfile: {e}")
    exit(1)

print("4. Testing specific User import...")
try:
    from shared.models import User
    print("✓ User imported successfully")
    print(f"User: {User}")
except Exception as e:
    print(f"✗ Failed to import User: {e}")
    exit(1)

print("5. Testing specific Base import...")
try:
    from shared.models import Base
    print("✓ Base imported successfully")
    print(f"Base: {Base}")
except Exception as e:
    print(f"✗ Failed to import Base: {e}")
    exit(1)

print("All imports successful!")
