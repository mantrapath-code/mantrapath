# Translation Service

## Description

The Translation Service is the multilingual communication hub of the MantraPath platform, providing real-time text translation with a special focus on Indian regional languages. This service enables global accessibility of mental health resources by translating content, conversations, and interface elements across multiple languages. It features intelligent language detection, cultural context preservation, and domain-specific translation optimized for mental health terminology.

This service solves the critical challenge of language barriers in mental health support, making the platform accessible to users regardless of their preferred language. By providing accurate, culturally-sensitive translations with special expertise in Indian languages, it ensures that mental health resources and support are truly inclusive and globally accessible.

## Table of Contents

- [Installation / Setup](#installation--setup)
- [Usage](#usage)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)
- [License](#license)
- [Contact / Author Info](#contact--author-info)
- [FAQ / Troubleshooting](#faq--troubleshooting)
- [Future Implementation](#future-implementation)

## Installation / Setup

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Access to translation engines (Phi-3, Google Translate, etc.)
- Redis (for translation caching)
- Models Service for AI-powered translation

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/translation_service
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download language models:**
   ```bash
   python -c "import nltk; nltk.download('punkt')"
   ```

### Configuration

- Environment variables configuration:
  ```bash
  cp .env.example .env
  nano .env
  ```
- Key variables include translation engine API keys, Models Service URL, caching configuration, and Indian language preferences.

## Usage

The Translation Service provides comprehensive translation capabilities through REST API endpoints.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8005 --reload
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d translation_service
  ```

- **Translate text:**
  ```bash
  curl -X POST "http://localhost:8005/translate" \
       -H "Content-Type: application/json" \
       -d '{"text":"I am feeling anxious today","source_language":"en","target_language":"hi","domain":"mental_health"}'
  ```

- **Detect language:**
  ```bash
  curl -X POST "http://localhost:8005/detect-language" \
       -H "Content-Type: application/json" \
       -d '{"text":"मैं आज चिंतित महसूस कर रहा हूँ"}'
  ```

- **Get supported languages:**
  ```bash
  curl -X GET "http://localhost:8005/languages"
  ```

- **Batch translation:**
  ```bash
  curl -X POST "http://localhost:8005/translate/batch" \
       -H "Content-Type: application/json" \
       -d '{"texts":["Hello","How are you?"],"target_language":"hi"}'
  ```

- **API Documentation:**
  Interactive API documentation at `http://localhost:8005/docs`

## Features

- **Multi-Engine Translation:** Intelligent coordination between Phi-3, Google Translate, and other engines
- **Indian Language Focus:** Specialized support for Hindi, Tamil, Telugu, Bengali, Marathi, and other Indian languages
- **Automatic Language Detection:** Smart detection of source language with confidence scoring
- **Domain-Specific Translation:** Optimized translations for mental health terminology and context
- **Cultural Context Preservation:** Maintains cultural nuances and context in translations
- **Translation Caching:** High-performance caching to reduce latency and API costs
- **Confidence Scoring:** Quality assessment of translations with confidence metrics
- **Batch Processing:** Efficient batch translation for large content volumes
- **Real-Time Translation:** Low-latency translation suitable for live conversations
- **Quality Assurance:** Multiple engine validation and quality checking
- **Fallback Mechanisms:** Robust fallback strategies for engine failures
- **Performance Monitoring:** Comprehensive translation quality and performance metrics

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **Translation Engines:** Phi-3 Enhanced Coordinator, Google Translate API, LibreTranslate
- **Language Detection:** Advanced language detection algorithms
- **Caching:** Redis for translation result caching
- **HTTP Client:** HTTPX for external service integration
- **Configuration:** Environment-based configuration management
- **Logging:** Comprehensive logging with structured formats
- **Testing:** Pytest with translation accuracy testing
- **Containerization:** Docker with multi-stage builds

## Contributing

Contributions to enhance translation capabilities are highly valued:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-language-support`)
3. Focus on translation accuracy and cultural sensitivity
4. Add comprehensive tests for new languages and domains
5. Ensure proper handling of mental health terminology
6. Update language models and translation engines
7. Submit a pull request with detailed translation quality analysis

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"Translation quality poor for Indian languages"**: Verify Indian language models are properly loaded and consider using domain-specific translation engines.
- **"Language detection failing"**: Check text length and character encoding. Ensure sufficient text for accurate detection.
- **"High translation latency"**: Enable caching and consider batch processing for multiple translations.
- **"Cultural context lost in translation"**: Review cultural context preservation settings and use domain-specific translation modes.

## Future Implementation

- **Neural Machine Translation:** Advanced neural networks for higher quality translations
- **Real-Time Voice Translation:** Live voice translation integration with Voice Service
- **Contextual Translation:** AI-powered contextual understanding for more accurate translations
- **Translation Memory:** Advanced translation memory for consistent terminology
- **Professional Review:** Integration with human translators for critical content validation
- **Dialect Support:** Support for regional dialects and variations within languages