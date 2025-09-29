# Phi3 Agent Service

## Description

The Phi3 Agent Service is a specialized AI agent service that provides high-performance text generation, translation, and natural language processing capabilities using Microsoft's Phi-3/Phi-4 models through Ollama. This service offers locally-hosted AI inference for privacy-sensitive applications, eliminating the need for external API calls while providing state-of-the-art language model capabilities for mental health conversations, content generation, and multilingual support.

This service solves the challenge of providing advanced AI capabilities while maintaining complete data privacy and control. By running Phi models locally through Ollama, it ensures that sensitive mental health conversations and user data never leave the MantraPath infrastructure, while still delivering cutting-edge AI performance for therapeutic conversations and content generation.

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
- Ollama installed and running
- GPU support recommended (NVIDIA CUDA) for optimal performance
- Phi-3 or Phi-4 models downloaded in Ollama
- Sufficient RAM (8GB+ recommended)

### Ollama Setup

1. **Install Ollama:**
   ```bash
   # Linux/macOS
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Or download from https://ollama.ai
   ```

2. **Download Phi-4 model:**
   ```bash
   ollama pull phi4
   # or for Phi-3
   ollama pull phi3
   ```

3. **Verify Ollama is running:**
   ```bash
   ollama list
   ```

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/phi3_agent
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

### Configuration

- Environment variables configuration:
  ```bash
  cp .env.example .env
  nano .env
  ```
- Key variables include `OLLAMA_URL`, model selection preferences, inference parameters, and performance optimization settings.

## Usage

The Phi3 Agent Service provides advanced AI capabilities through REST API endpoints.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8015 --reload
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d phi3_agent
  ```

- **Generate text:**
  ```bash
  curl -X POST "http://localhost:8015/generate" \
       -H "Content-Type: application/json" \
       -d '{"prompt":"Provide supportive advice for someone feeling anxious","max_tokens":500,"temperature":0.7}'
  ```

- **Translate text:**
  ```bash
  curl -X POST "http://localhost:8015/translate" \
       -H "Content-Type: application/json" \
       -d '{"text":"I am feeling better today","source_language":"en","target_language":"es"}'
  ```

- **Health check:**
  ```bash
  curl -X GET "http://localhost:8015/health"
  ```

- **Model status:**
  ```bash
  curl -X GET "http://localhost:8015/model/status"
  ```

- **API Documentation:**
  Interactive API documentation at `http://localhost:8015/docs`

## Features

- **Local AI Inference:** Complete privacy with locally-hosted Phi-3/Phi-4 models via Ollama
- **High-Performance Text Generation:** State-of-the-art language generation for therapeutic conversations
- **Multi-Language Translation:** Advanced translation capabilities for global mental health support
- **Therapeutic Content Generation:** Specialized prompts for mental health and wellness content
- **Conversation Continuity:** Context-aware conversations with memory of previous interactions
- **Configurable Parameters:** Customizable temperature, top-p, and max tokens for different use cases
- **Model Fallback:** Automatic fallback to available models if preferred model is unavailable
- **Performance Optimization:** Optimized inference with GPU acceleration when available
- **Privacy-First Architecture:** No external API calls, all processing happens locally
- **Real-Time Response:** Fast inference suitable for interactive conversations
- **Scalable Architecture:** Designed to handle multiple concurrent requests efficiently
- **Model Management:** Dynamic model loading and management through Ollama integration

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **AI Models:** Microsoft Phi-3/Phi-4 models via Ollama integration
- **ML Framework:** PyTorch 2.1.0, Transformers 4.36.0 (for model compatibility)
- **Acceleration:** Accelerate 0.24.1 for optimized inference
- **HTTP Client:** HTTPX 0.25.2 for Ollama API communication
- **Configuration:** Pydantic 2.5.0 for configuration management
- **Numerical Computing:** NumPy (<2.0.0) for efficient array operations
- **Server:** Uvicorn 0.24.0 for high-performance ASGI serving
- **Containerization:** Docker with GPU support

## Contributing

Contributions to enhance AI agent capabilities are highly valued:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhanced-ai-prompts`)
3. Focus on therapeutic conversation quality and AI safety
4. Add comprehensive tests for AI model outputs and safety
5. Ensure ethical AI practices and bias mitigation
6. Update therapeutic prompts and conversation flows
7. Submit a pull request with detailed AI performance evaluation

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"Ollama connection failed"**: Verify Ollama is running and accessible at the configured URL. Check firewall settings.
- **"Model not found"**: Ensure Phi-3 or Phi-4 models are downloaded in Ollama using `ollama pull phi4`.
- **"Slow inference"**: Enable GPU acceleration in Ollama and ensure adequate RAM allocation.
- **"AI responses not therapeutic"**: Review and customize prompts for mental health contexts.

## Future Implementation

- **Specialized Mental Health Models:** Fine-tuned Phi models specifically for therapeutic conversations
- **Multi-Modal Capabilities:** Integration of vision and audio capabilities with Phi models
- **Advanced Prompt Engineering:** Sophisticated prompt templates for various mental health scenarios
- **Model Quantization:** Optimized model versions for faster inference and lower resource usage
- **Conversation Memory:** Long-term conversation memory and context management
- **Clinical Integration:** AI outputs validated with clinical mental health professionals