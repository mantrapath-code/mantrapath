#!/usr/bin/env python3
"""
Test script to verify whisper installation and provide diagnostics
"""

import sys
import platform
import subprocess

def test_whisper_import():
    """Test whisper import and provide diagnostics"""
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.machine()}")
    print("-" * 50)
    
    # Test basic import
    try:
        import whisper
        print("✅ Successfully imported whisper")
        
        # Test load_model function
        if hasattr(whisper, 'load_model'):
            print("✅ whisper.load_model is available")
        else:
            print("❌ whisper.load_model is not available")
            return False
            
        # Test model loading (small model for quick test)
        try:
            print("🔄 Testing model loading (this may take a moment)...")
            model = whisper.load_model("tiny")
            print("✅ Successfully loaded tiny model")
            print(f"Model device: {model.device}")
            return True
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import whisper: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_dependencies():
    """Test key dependencies"""
    dependencies = ['torch', 'numpy', 'tqdm', 'tiktoken']
    
    print("\n" + "=" * 50)
    print("Testing dependencies:")
    print("=" * 50)
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} (missing)")
        except Exception as e:
            print(f"⚠️  {dep} (error: {e})")

def check_triton():
    """Check triton availability"""
    print("\n" + "=" * 50)
    print("Checking triton (CUDA dependency):")
    print("=" * 50)
    
    try:
        import triton
        print("✅ triton is available")
        return True
    except ImportError:
        print("❌ triton is not available (expected on ARM64)")
        return False
    except Exception as e:
        print(f"⚠️  triton error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 MantraPath Models Service - Whisper Installation Test")
    print("=" * 60)
    
    test_dependencies()
    check_triton()
    
    print("\n" + "=" * 50)
    print("Testing whisper:")
    print("=" * 50)
    
    success = test_whisper_import()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Whisper is working correctly.")
    else:
        print("❌ Tests failed. Check the errors above.")
        sys.exit(1)
