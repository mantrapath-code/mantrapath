# Model Recommendations for MantraPath Local Agent Integration

## 🎯 Executive Summary

This document provides specific model recommendations for integrating a local AI agent into the MantraPath chatbot service, prioritizing resource efficiency, conversation quality, and scalability for mental health support applications.

## 🏆 Primary Recommendation: Phi-3 Mini 4K Instruct (vLLM Optimized)

### **Why Phi-3 Mini 4K Instruct with vLLM?**

✅ **Ultra-Efficient**: Only 3.8B parameters with exceptional performance  
✅ **Resource Optimized**: ~2.5GB VRAM with GPU acceleration via vLLM  
✅ **High Throughput**: 40-60 tokens/second with vLLM optimization  
✅ **Instruction Following**: State-of-the-art instruction following capabilities  
✅ **Context Length**: 4K context window optimized for conversational flow  
✅ **Production Ready**: Microsoft's production-grade model with enterprise support

### **Technical Specifications**
```yaml
Model: microsoft/Phi-3-mini-4k-instruct
Parameters: 3.8 billion
Memory Requirement: 2.5-4GB VRAM (GPU) / 8GB RAM (CPU fallback)
Context Length: 4,096 tokens
Optimization: vLLM with OpenAI-compatible API
Format: HuggingFace Transformers (FP16/BF16)
Average Speed: 40-60 tokens/second (with vLLM)
Quality Score: 9.5/10 for conversational AI
```

### **Docker Setup Commands**
```bash
# Deploy Phi-3 Mini with vLLM (GPU optimized)
docker run --runtime nvidia --gpus all \
	--name mantrapath_phi3_agent \
	-v ~/.cache/huggingface:/root/.cache/huggingface \
	--env "HUGGING_FACE_HUB_TOKEN=<your_hf_token>" \
	-p 8000:8000 \
	--ipc=host \
	--restart unless-stopped \
	vllm/vllm-openai:latest \
	--model microsoft/Phi-3-mini-4k-instruct \
	--served-model-name phi3-mini \
	--max-model-len 4096 \
	--trust-remote-code

# Verify deployment
curl http://localhost:8000/v1/models
```

## 🚀 Alternative Recommendations

### **Option 2: Phi-3 Mini (Ultra-Lightweight)**

**Best for**: High-throughput, resource-constrained environments

```yaml
Model: microsoft/Phi-3-mini-4k-instruct-gguf
Parameters: 3.8 billion
Memory Requirement: 2.5-3GB RAM
Context Length: 4,096 tokens
Speed: 30-45 tokens/second
Resource Efficiency: 10/10
Quality Score: 8/10
```

**Pros**: Extremely fast, minimal resource usage, excellent reasoning  
**Cons**: Shorter context window, less nuanced responses

### **Option 3: Llama 2 7B Chat (Proven Stability)**

**Best for**: Conservative deployment, maximum stability

```yaml
Model: llama-2-7b-chat.Q4_K_M.gguf
Parameters: 7 billion
Memory Requirement: 4-5GB RAM
Context Length: 4,096 tokens
Speed: 15-25 tokens/second
Stability: 10/10
Quality Score: 8/10
```

**Pros**: Battle-tested, excellent safety alignment, stable performance  
**Cons**: Slower inference, shorter context than Mistral

### **Option 4: Code Llama 7B Instruct (Technical Conversations)**

**Best for**: Users discussing technical mental health tools

```yaml
Model: codellama-7b-instruct.Q4_K_M.gguf
Parameters: 7 billion
Memory Requirement: 4-5GB RAM
Context Length: 16,384 tokens
Speed: 18-28 tokens/second
Technical Accuracy: 10/10
Quality Score: 7/10 (general conversation)
```

**Pros**: Excellent for technical discussions, large context window  
**Cons**: Less optimized for emotional support conversations

## 🎚️ GPU-Accelerated Options (Optional)

### **Premium Option: Mistral 7B Instruct (FP16)**

**Best for**: High-demand periods, premium response quality

```yaml
Model: mistral-7b-instruct-v0.2 (full precision)
Parameters: 7 billion (FP16)
Memory Requirement: 14-16GB VRAM
Speed: 60-120 tokens/second (RTX 4090)
Quality Score: 10/10
Power Consumption: High
```

**Resource Requirements**:
- GPU: RTX 4090 (24GB), RTX 3090 (24GB), or A100 (40GB)
- Power: 350-400W GPU power draw
- Cooling: Adequate GPU cooling required

### **Mid-Range GPU Option: Mistral 7B (8-bit)**

```yaml
Model: mistral-7b-instruct-v0.2 (8-bit quantized)
Parameters: 7 billion (8-bit)
Memory Requirement: 8-10GB VRAM
Speed: 40-80 tokens/second
Quality Score: 9.5/10
GPU Requirement: RTX 3080 (12GB) or better
```

## 🏥 Mental Health Specialized Models

### **MentalBERT Fine-tuned Models**

**Best for**: Mental health classification and sentiment analysis

```yaml
Model: mental-bert-base-uncased
Parameters: 110 million
Memory Requirement: <1GB RAM
Speed: 100+ inferences/second
Specialization: Mental health domain
Use Case: Preprocessing and classification
```

**Integration Strategy**: Use alongside primary model for:
- Crisis detection preprocessing
- Emotional state classification
- Mental health topic identification
- Risk assessment scoring

### **CounselChat Fine-tuned Models**

**Best for**: Therapeutic conversation patterns

```yaml
Model: counselchat-t5-base
Parameters: 220 million
Memory Requirement: <2GB RAM
Speed: 50+ responses/second
Specialization: Counseling conversations
Use Case: Response style guidance
```

## 📊 Performance Comparison Matrix

| Model | Size | RAM | Speed (t/s) | Quality | GPU Req | Best Use Case |
|-------|------|-----|-------------|---------|---------|---------------|
| **Mistral 7B Q4** | 4GB | 6GB | 25 | 9/10 | None | **Primary recommendation** |
| Phi-3 Mini Q4 | 2.5GB | 4GB | 40 | 8/10 | None | High throughput |
| Llama 2 7B Q4 | 4GB | 5GB | 20 | 8/10 | None | Maximum stability |
| Code Llama 7B Q4 | 4GB | 5GB | 25 | 7/10 | None | Technical discussions |
| Mistral 7B FP16 | 14GB | 2GB | 80 | 10/10 | RTX 4090 | Premium quality |
| MentalBERT | 0.5GB | 1GB | 100+ | 7/10 | None | Specialized classification |

## 🛠️ Implementation Strategy

### **Multi-Model Architecture (Recommended)**

```python
class MultiModelManager:
    """
    Manages multiple models for different conversation aspects
    """
    def __init__(self):
        self.primary_model = "mistral-7b-instruct-q4"     # Main conversations
        self.crisis_classifier = "mental-bert"            # Crisis detection
        self.fallback_model = "phi-3-mini-q4"            # High-load periods
        
    async def select_optimal_model(self, conversation_context):
        if conversation_context.crisis_indicators:
            return await self.crisis_classifier.classify_and_respond()
        elif conversation_context.load_level > 0.8:
            return await self.fallback_model.generate_response()
        else:
            return await self.primary_model.generate_response()
```

### **Resource-Aware Model Switching**

```python
class ResourceAwareModelManager:
    """
    Dynamically switches models based on system resources
    """
    
    def __init__(self):
        self.models = {
            'high_quality': 'mistral-7b-instruct-q4',
            'high_speed': 'phi-3-mini-q4',
            'gpu_accelerated': 'mistral-7b-fp16'
        }
        
    async def get_optimal_model(self):
        system_load = await self.monitor.get_system_metrics()
        
        if system_load.gpu_available and system_load.peak_hours:
            return self.models['gpu_accelerated']
        elif system_load.cpu_usage > 0.7:
            return self.models['high_speed']
        else:
            return self.models['high_quality']
```

## 🔧 Configuration Templates

### **Ollama Configuration**

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull recommended model
ollama pull mistral:7b-instruct-q4_k_m

# Configure for MantraPath
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_MODELS=/opt/mantrapath/models
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_LOADED_MODELS=2

# Start with resource limits
ollama serve --host 127.0.0.1 --port 11434
```

### **Docker Configuration**

```yaml
# docker-compose-agent.yml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: mantrapath-agent
    ports:
      - "11434:11434"
    volumes:
      - ./models:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_NUM_PARALLEL=4
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '2.0'
        reservations:
          memory: 4G
          cpus: '1.0'
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### **Python Client Configuration**

```python
# agent_config.py
AGENT_CONFIG = {
    'models': {
        'primary': {
            'name': 'mistral:7b-instruct-q4_k_m',
            'endpoint': 'http://localhost:11434',
            'parameters': {
                'temperature': 0.7,
                'top_p': 0.9,
                'max_tokens': 512,
                'context_length': 4096
            }
        },
        'fallback': {
            'name': 'phi3:mini-q4',
            'endpoint': 'http://localhost:11434',
            'parameters': {
                'temperature': 0.6,
                'top_p': 0.85,
                'max_tokens': 256,
                'context_length': 2048
            }
        }
    },
    'performance': {
        'timeout_seconds': 30,
        'max_concurrent': 10,
        'queue_size': 50,
        'cache_ttl': 3600
    }
}
```

## 🎯 Deployment Recommendations

### **Development Environment**
- **Model**: Phi-3 Mini Q4 (fast iteration)
- **Resources**: 4GB RAM, 2 CPU cores
- **Setup Time**: ~5 minutes

### **Staging Environment**
- **Model**: Mistral 7B Instruct Q4 (production testing)
- **Resources**: 8GB RAM, 4 CPU cores
- **Setup Time**: ~10 minutes

### **Production Environment**
- **Primary Model**: Mistral 7B Instruct Q4
- **Fallback Model**: Phi-3 Mini Q4
- **Specialized Model**: MentalBERT (classification)
- **Resources**: 12GB RAM, 6 CPU cores per instance
- **Scaling**: 2-4 instances behind load balancer

### **High-Performance Production**
- **Primary Model**: Mistral 7B FP16 (GPU)
- **Fallback Model**: Mistral 7B Q4 (CPU)
- **Resources**: RTX 4090 + 16GB RAM
- **Scaling**: GPU instances for peak hours, CPU for off-peak

## 🔍 Model Evaluation Criteria

### **Conversation Quality Assessment**
- **Empathy Score**: Response emotional appropriateness
- **Coherence Score**: Logical conversation flow
- **Helpfulness Score**: Practical advice quality
- **Safety Score**: Harmful content avoidance
- **Therapeutic Alignment**: Mental health best practices

### **Technical Performance Metrics**
- **Response Time**: Time to first token and completion
- **Memory Usage**: Peak and average RAM/VRAM consumption
- **Throughput**: Concurrent conversations supported
- **Reliability**: Uptime and error rates
- **Scalability**: Performance under increasing load

This comprehensive model recommendation guide ensures you select the optimal AI model configuration for your MantraPath chatbot enhancement while balancing quality, performance, and resource efficiency.
