# 🔧 Development Tools

This directory contains various tools and utilities for development and testing.

## 📁 Directory Structure

### 🧪 Testing Tools (`testing/`)
- **Test audio files for voice functionality**
- **Voice STT (Speech-to-Text) testing scripts**

**Files:**
- `test_audio.txt` - Text content for audio testing
- `test_audio.wav` - Audio file for voice feature testing
- `test_voice_stt.sh` - Voice STT testing script

## 🎯 Usage

### Voice Testing
```bash
# Run voice STT tests
./tools/testing/test_voice_stt.sh

# Use test audio files
# test_audio.wav - For audio processing tests
# test_audio.txt - For text comparison and validation
```

## 📝 Notes

- Audio files are provided for testing voice features
- STT testing requires appropriate audio codecs
- Ensure microphone permissions are set for local testing
