# Models Service Testing Suite

Interactive testing tools for the MantraPath Models Service. Test STT, TTS, and NLP capabilities with different models and languages.

## 📁 Files

### `simple_tester.py` - **RECOMMENDED** 
- **No external dependencies** (just requests)
- Interactive menu-driven testing
- Tests all TTS models with sample texts
- NLP capabilities testing
- Focus on Indian languages
- **Easy to run and debug**

### `interactive_tester.py` - Advanced Features
- Full interactive testing with audio recording
- Requires PyAudio for microphone input
- More comprehensive but needs setup

## 🚀 Quick Start

### 1. Make sure Models Service is running
```bash
# Check if running
curl http://localhost:8085/health
```

### 2. Run the simple tester (Recommended)
```bash
cd /Users/sachin/Desktop/mantrapath/backend/models_service_testing
python3 simple_tester.py
```

## 🧪 Testing Options

### Simple Tester Menu:
1. **📊 Service Status & Capabilities** - Check what's available
2. **🔊 Test TTS for All Languages** - Generate audio for all supported languages
3. **🇮🇳 Test Indian Languages Focus** - Focus on Hindi, Bengali, Telugu, Tamil, etc.
4. **🧠 Test NLP Capabilities** - Test sentiment analysis and translation
5. **🎯 Test Specific TTS Model** - Test individual models
6. **🚀 Run Comprehensive Test** - Full test suite
7. **🚪 Exit**

## 📊 What Gets Tested

### TTS (Text-to-Speech)
- **Languages**: 21+ languages including all Indian languages
- **Models**: 
  - Coqui TTS (coqui_xtts_v2, coqui_hi, coqui_bn)
  - eSpeak (espeak_en, espeak_hi, etc.)
  - Festival (festival_en, festival_hi)
- **Output**: WAV files saved in `test_outputs/` directory

### STT (Speech-to-Text) 
- **Languages**: 17+ languages
- **Models**:
  - Whisper (whisper_medium)
  - Vosk (vosk_hi, vosk_mr, etc.)
  - Wav2Vec2 (wav2vec2_en, wav2vec2_hi, etc.)

### NLP (Natural Language Processing)
- **Sentiment Analysis**: Positive/Negative/Neutral detection
- **Translation**: Multi-language translation
- **Text Embeddings**: Semantic representations

## 🇮🇳 Indian Languages Support

The testing suite includes sample texts for:
- **Hindi (hi)**: नमस्ते, मैं मंत्रपथ हूं। यह एक टेस्ट है।
- **Bengali (bn)**: হ্যালো, আমি মন্ত্রপথ। এটি একটি পরীক্ষা।
- **Telugu (te)**: హలో, నేను మంత్రపథ్. ఇది ఒక పరీక్ష.
- **Tamil (ta)**: வணக்கம், நான் மந்திரபாதை. இது ஒரு சோதனை.
- **Marathi (mr)**: नमस्कार, मी मंत्रपथ आहे. ही एक चाचणी आहे.
- **Gujarati (gu)**: નમસ્તે, હું મંત્રપથ છું. આ એક પરીક્ષણ છે.
- **Kannada (kn)**: ನಮಸ್ತೆ, ನಾನು ಮಂತ್ರಪಥ್. ಇದು ಒಂದು ಪರೀಕ್ಷೆ.
- **Malayalam (ml)**: ഹലോ, ഞാൻ മന്ত്രപഥ്. ഇത് ഒരു പരീക്ഷണമാണ്.
- **Punjabi (pa)**: ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਮੈਂ ਮੰਤ੍ਰਪਥ ਹਾਂ। ਇਹ ਇੱਕ ਟੈਸਟ ਹੈ।

## 📁 Output Files

All generated audio files are saved in `test_outputs/` with naming pattern:
- `tts_{language}_{model}_{timestamp}.wav`

Example:
- `tts_hi_espeak_hi_20250831_143022.wav`
- `tts_en_coqui_xtts_v2_20250831_143025.wav`

## 🎵 Playing Audio

Generated WAV files can be played with:
- **macOS**: `afplay filename.wav`
- **Linux**: `aplay filename.wav`  
- **Windows**: Double-click the file
- **Any platform**: VLC, Media Player, etc.

## 🔧 Advanced Setup (for interactive_tester.py)

If you want to use the full interactive tester with audio recording:

```bash
# Install PyAudio (may need system dependencies)
pip install pyaudio

# On macOS you might need:
brew install portaudio
pip install pyaudio

# On Ubuntu/Debian:
sudo apt-get install python3-pyaudio

# Then run:
python3 interactive_tester.py
```

## 🎯 Use Cases

### Testing Before Voice Service Development
1. **Run comprehensive test** to understand all capabilities
2. **Test Indian languages** to see quality and performance
3. **Compare different models** for the same language
4. **Measure response times** and audio quality

### Quality Assessment
1. **Listen to TTS outputs** for different models
2. **Test sentiment analysis** accuracy
3. **Verify translation** quality
4. **Check language detection** accuracy

### Performance Benchmarking
1. **Model loading times**
2. **Synthesis speed**
3. **Memory usage** per model
4. **Concurrent request** handling

## 📋 Troubleshooting

### Models Service Not Running
```bash
# Check if it's running
curl http://localhost:8085/health

# If not, start it (from backend directory)
docker-compose up models-service
```

### No Audio Output
- Check `test_outputs/` directory for WAV files
- Try different TTS models (some may fail)
- Verify Models Service logs for errors

### Permission Issues
```bash
# Make scripts executable
chmod +x simple_tester.py
chmod +x interactive_tester.py
```

## 🚀 Next Steps

After testing, you'll have a good understanding of:
1. **Which models work best** for each language
2. **Performance characteristics** of different engines
3. **Quality differences** between models
4. **Response times** and reliability

This information will be crucial for designing the Voice Service architecture!

## 📊 Expected Results

### Working Models (Based on Testing):
- ✅ **eSpeak**: Fast, reliable for all languages
- ✅ **Coqui TTS**: Higher quality, slower
- ✅ **Festival**: Good for English and Hindi
- ✅ **Sentiment Analysis**: High accuracy
- ✅ **Translation**: Good quality with confidence scores

Use this data to make informed decisions about which models to use in the Voice Service!
