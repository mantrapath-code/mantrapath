# MantraPath Cloud Kubernetes Deployment Strategy
## Comprehensive Infrastructure Planning for Production & Development

---

## 🎯 Executive Summary

MantraPath requires a sophisticated cloud-native Kubernetes deployment supporting **21 microservices** with AI/ML capabilities, voice processing, and real-time features. This document provides cloud-agnostic specifications optimized for cost-effectiveness while maintaining production reliability.

### Key Requirements
- **🤖 AI/ML Workloads**: GPU acceleration for NLP processing and chatbot intelligence
- **📊 Real-time Features**: WebSocket support and event streaming
- **🌍 Multi-language Support**: 25+ languages with cultural adaptations
- **🔄 Event-Driven Architecture**: NATS JetStream for service communication
- **📈 Auto-scaling**: Dynamic resource allocation based on demand
- **🔊 Voice Ready**: Infrastructure prepared for future voice integration

---

## 🏗️ Complete Infrastructure Architecture & Service Deployment

### **Detailed Service-to-Infrastructure Mapping**

```mermaid
graph TB
    subgraph "External Layer"
        CDN[CDN/CloudFlare<br/>Static Assets<br/>Global Distribution]
        LB[Load Balancer<br/>HTTPS/WSS Termination<br/>SSL Certificates]
    end
    
    subgraph "Frontend Infrastructure"
        subgraph "Frontend Node Pool"
            FE1[Frontend Node 1<br/>React App (Nginx)<br/>2 vCPU, 4GB RAM]
            FE2[Frontend Node 2<br/>React App (Nginx)<br/>2 vCPU, 4GB RAM]
        end
    end
    
    subgraph "Kubernetes Cluster - Backend Services"
        subgraph "GPU Node Pool (Tesla T4)"
            GPU1[GPU Node 1<br/>🤖 Models Service :8080<br/>🧠 Chatbot Intelligence<br/>4 vCPU, 16GB RAM, 1x T4]
            GPU2[GPU Node 2<br/>🧠 AI Context Store :8013<br/>🔄 AI Event Processor :8014<br/>4 vCPU, 16GB RAM, 1x T4]
        end
        
        subgraph "CPU Node Pool - Core Services"
            CPU1[CPU Node 1<br/>🌐 API Gateway :8000<br/>🔐 Auth Service :8001<br/>4 vCPU, 16GB RAM]
            CPU2[CPU Node 2<br/>👤 Profile Service :8002<br/>😊 Mood Service :8003<br/>🤖 Chatbot Service :8004<br/>4 vCPU, 16GB RAM]
            CPU3[CPU Node 3<br/>🌐 Translation Service :8005<br/>📝 Content Service :8005<br/>👥 Community Service :8006<br/>4 vCPU, 16GB RAM]
        end
        
        subgraph "CPU Node Pool - Processing Services"
            CPU4[CPU Node 4<br/>🔔 Notification Service :8007<br/>📁 Media Service :8009<br/>🎯 Action Orchestrator :8012<br/>4 vCPU, 16GB RAM]
            CPU5[CPU Node 5<br/>🔊 Voice Service :8011 (Disabled)<br/>🧠 Memory Service :8017<br/>🎯 Proactive Assistance :8018<br/>4 vCPU, 16GB RAM]
            CPU6[CPU Node 6<br/>📊 Deployment API :8019<br/>Load Balancer/Backup<br/>4 vCPU, 16GB RAM]
        end
        
        subgraph "Memory-Optimized Pool"
            MEM1[Memory Node 1<br/>Redis Primary :6379<br/>Session & Cache<br/>4 vCPU, 32GB RAM]
            MEM2[Memory Node 2<br/>Redis Agent :6380<br/>ML Model Cache<br/>4 vCPU, 32GB RAM]
            MEM3[Memory Node 3<br/>Redis Event :6381<br/>Event Streaming<br/>4 vCPU, 32GB RAM]
        end
        
        subgraph "Storage-Optimized Pool"
            STO1[Storage Node 1<br/>PostgreSQL Primary<br/>All Services DB<br/>4 vCPU, 16GB RAM, 500GB SSD]
            STO2[Storage Node 2<br/>NATS JetStream<br/>Event Bus<br/>2 vCPU, 8GB RAM, 100GB SSD]
            STO3[Storage Node 3<br/>Model Storage<br/>AI Models Cache<br/>2 vCPU, 8GB RAM, 1TB SSD]
        end
    end
    
    CDN --> LB
    LB --> FE1
    LB --> FE2
    LB --> CPU1
    
    FE1 --> CPU1
    FE2 --> CPU1
    
    CPU1 --> CPU2
    CPU1 --> CPU3
    CPU1 --> CPU4
    CPU1 --> CPU5
    CPU1 --> CPU6
    
    CPU2 --> GPU1
    CPU3 --> GPU2
    CPU4 --> MEM1
    CPU5 --> MEM2
    CPU6 --> MEM3
    
    GPU1 --> STO3
    GPU2 --> STO3
    CPU1 --> STO1
    CPU2 --> STO1
    CPU3 --> STO1
    CPU4 --> STO1
    CPU5 --> STO1
    CPU6 --> STO2
```

### **Complete Service Deployment Matrix**

| Service | Port | Node Pool | Resource Allocation | Replicas | Storage | 
|---------|------|-----------|-------------------|----------|---------|
| **Frontend Services** |
| React Frontend | 80/443 | Frontend Pool | 2 vCPU, 4GB RAM | 3 | 10GB |
| **GPU-Intensive Services** |
| 🤖 Models Service | 8080 | GPU Pool | 4 vCPU, 16GB RAM, 1 GPU | 2 | 50GB (NLP Models) |
| 🔊 Voice Service | 8011 | CPU Pool | 1 vCPU, 2GB RAM | 1 (Disabled) | 5GB |
| 🧠 AI Context Store | 8013 | GPU Pool | 2 vCPU, 8GB RAM, 0.5 GPU | 2 | 50GB |
| 🔄 AI Event Processor | 8014 | GPU Pool | 2 vCPU, 8GB RAM, 0.5 GPU | 2 | 20GB |
| **Core Application Services** |
| 🌐 API Gateway | 8000 | CPU Pool | 2 vCPU, 4GB RAM | 3 | 5GB |
| 🔐 Auth Service | 8001 | CPU Pool | 1 vCPU, 2GB RAM | 3 | 5GB |
| 👤 Profile Service | 8002 | CPU Pool | 1 vCPU, 2GB RAM | 2 | 5GB |
| 😊 Mood Service | 8003 | CPU Pool | 1 vCPU, 2GB RAM | 2 | 10GB |
| 🤖 Chatbot Service | 8004 | CPU Pool | 2 vCPU, 4GB RAM | 2 | 10GB |
| 🌐 Translation Service | 8005 | CPU Pool | 1 vCPU, 2GB RAM | 2 | 5GB |
| 📝 Content Service | 8005 | CPU Pool | 1 vCPU, 2GB RAM | 2 | 20GB |
| 👥 Community Service | 8006 | CPU Pool | 1 vCPU, 2GB RAM | 2 | 15GB |
| 🔔 Notification Service | 8007 | CPU Pool | 1 vCPU, 2GB RAM | 2 | 5GB |
| 📁 Media Service | 9009 | CPU Pool | 2 vCPU, 4GB RAM | 2 | 100GB |
| **Processing Services** |
| 🎯 Action Orchestrator | 8012 | CPU Pool | 1 vCPU, 2GB RAM | 2 | 5GB |
| 🎵 Voice Event Processor | 8015 | CPU Pool | 1 vCPU, 2GB RAM | 2 | 10GB |
| 🧠 Memory Service | 8017 | CPU Pool | 1 vCPU, 2GB RAM | 2 | 10GB |
| 🎯 Proactive Assistance | 8018 | CPU Pool | 1 vCPU, 2GB RAM | 2 | 5GB |
| 📊 Deployment API | 8019 | CPU Pool | 1 vCPU, 2GB RAM | 1 | 5GB |
| **Infrastructure Services** |
| PostgreSQL | 5432 | Storage Pool | 4 vCPU, 16GB RAM | 1 | 500GB SSD |
| Redis Primary | 6379 | Memory Pool | 2 vCPU, 8GB RAM | 1 | 20GB |
| Redis Agent | 6380 | Memory Pool | 2 vCPU, 8GB RAM | 1 | 20GB |
| Redis Event | 6381 | Memory Pool | 2 vCPU, 8GB RAM | 1 | 20GB |
| NATS JetStream | 4222 | Storage Pool | 2 vCPU, 4GB RAM | 1 | 100GB |

### **Detailed Node Pool Specifications**

#### **Frontend Node Pool**
```yaml
nodePool:
  name: "frontend-pool"
  purpose: "React Frontend Applications"
  nodeCount: { min: 2, max: 5, initial: 3 }
  machineType: "n1-standard-2 / m5.large / Standard_D2s_v3"
  specs:
    cpu: "2 vCPUs"
    memory: "8 GB"
    storage: "50GB SSD"
  services:
    - name: "React Frontend"
      replicas: 3
      resources: "2 vCPU, 4GB RAM each"
      storage: "10GB per replica"
  estimatedCost: "$140/month"
```

#### **GPU Node Pool (AI/ML Services)**
```yaml
nodePool:
  name: "gpu-pool"
  purpose: "AI/ML Processing & NLP Intelligence"
  nodeCount: { min: 2, max: 4, initial: 2 }
  machineType: "g4dn.xlarge / n1-standard-4+T4 / NC4as_T4_v3"
  specs:
    cpu: "4 vCPUs"
    memory: "16 GB"
    gpu: "1x NVIDIA Tesla T4"
    storage: "100GB SSD"
  services:
    - name: "Models Service"
      replicas: 2
      resources: "4 vCPU, 16GB RAM, 1 GPU each"
      models: "Phi-4 (7.5GB), Embedding Models (1GB)"
    - name: "AI Context Store"
      replicas: 2
      resources: "2 vCPU, 8GB RAM, 0.5 GPU each"
    - name: "AI Event Processor"
      replicas: 2
      resources: "2 vCPU, 8GB RAM, 0.5 GPU each"
  estimatedCost: "$380/month"  # Reduced from 2 nodes to 1 node
```

#### **CPU Node Pool (Application Services)**
```yaml
nodePool:
  name: "cpu-pool"
  purpose: "Core Application Services"
  nodeCount: { min: 4, max: 8, initial: 6 }
  machineType: "n1-standard-4 / m5.xlarge / Standard_D4s_v3"
  specs:
    cpu: "4 vCPUs"
    memory: "16 GB"
    storage: "50GB SSD"
  serviceDistribution:
    node1:
      - "API Gateway (3 replicas): 6 vCPU, 12GB RAM"
      - "Auth Service (3 replicas): 3 vCPU, 6GB RAM"
    node2:
      - "Profile Service (2 replicas): 2 vCPU, 4GB RAM"
      - "Mood Service (2 replicas): 2 vCPU, 4GB RAM"
      - "Chatbot Service (2 replicas): 4 vCPU, 8GB RAM"
    node3:
      - "Translation Service (2 replicas): 2 vCPU, 4GB RAM"
      - "Content Service (2 replicas): 2 vCPU, 4GB RAM"
      - "Community Service (2 replicas): 2 vCPU, 4GB RAM"
    node4:
      - "Notification Service (2 replicas): 2 vCPU, 4GB RAM"
      - "Media Service (2 replicas): 4 vCPU, 8GB RAM"
      - "Action Orchestrator (2 replicas): 2 vCPU, 4GB RAM"
    node5:
      - "Voice Service (1 replica - DISABLED): 1 vCPU, 2GB RAM"
      - "Memory Service (2 replicas): 2 vCPU, 4GB RAM"
      - "Proactive Assistance (2 replicas): 2 vCPU, 4GB RAM"
    node6:
      - "Deployment API (1 replica): 1 vCPU, 2GB RAM"
      - "Reserve Capacity: 3 vCPU, 14GB RAM"
  estimatedCost: "$690/month"
```

#### **Memory Node Pool (Caching Layer)**
```yaml
nodePool:
  name: "memory-pool"
  purpose: "Redis Cluster & Caching"
  nodeCount: { min: 3, max: 5, initial: 3 }
  machineType: "n1-highmem-4 / r5.xlarge / Standard_E4s_v3"
  specs:
    cpu: "4 vCPUs"
    memory: "32 GB"
    storage: "50GB SSD"
  services:
    - name: "Redis Primary"
      replicas: 1
      resources: "2 vCPU, 8GB RAM"
      purpose: "Session management, API Gateway cache"
    - name: "Redis Agent"
      replicas: 1
      resources: "2 vCPU, 8GB RAM"
      purpose: "ML model cache, AI context storage"
    - name: "Redis Event"
      replicas: 1
      resources: "2 vCPU, 8GB RAM"
      purpose: "Event streaming, WebSocket connections"
  estimatedCost: "$546/month"
```

#### **Storage Node Pool (Persistent Data)**
```yaml
nodePool:
  name: "storage-pool"
  purpose: "Database & Persistent Storage"
  nodeCount: { min: 3, max: 4, initial: 3 }
  machineType: "n1-standard-4 / m5.xlarge / Standard_D4s_v3"
  specs:
    cpu: "4 vCPUs"
    memory: "16 GB"
    storage: "500GB+ SSD"
  services:
    - name: "PostgreSQL"
      replicas: 1
      resources: "4 vCPU, 16GB RAM"
      storage: "500GB SSD (primary) + 500GB (backup)"
    - name: "NATS JetStream"
      replicas: 1
      resources: "2 vCPU, 4GB RAM"
      storage: "100GB SSD"
    - name: "Model Storage"
      replicas: 1
      resources: "2 vCPU, 8GB RAM"
      storage: "1TB SSD (AI models cache)"
  estimatedCost: "$420/month"
```

### **Complete Resource Allocation Summary**

#### **Total Infrastructure Requirements**

| Component | Nodes | Total vCPUs | Total RAM | Total Storage | Total GPUs | Monthly Cost |
|-----------|-------|-------------|-----------|---------------|------------|--------------|
| **Frontend Pool** | 3 | 6 vCPUs | 24 GB | 150 GB | 0 | $140 |
| **GPU Pool** | 1 | 4 vCPUs | 16 GB | 100 GB | 1 Tesla T4 | $380 |
| **CPU Pool** | 6 | 24 vCPUs | 96 GB | 300 GB | 0 | $690 |
| **Memory Pool** | 3 | 12 vCPUs | 96 GB | 150 GB | 0 | $546 |
| **Storage Pool** | 3 | 10 vCPUs | 28 GB | 2100 GB | 0 | $420 |
| **Load Balancer** | - | - | - | - | - | $50 |
| **Monitoring** | - | - | - | - | - | $50 |
| **TOTAL PRODUCTION** | **16 nodes** | **56 vCPUs** | **260 GB** | **2800 GB** | **1 GPU** | **$2,276/month** |

#### **Development Environment (Reduced)**

| Component | Nodes | Total vCPUs | Total RAM | Total Storage | Total GPUs | Monthly Cost |
|-----------|-------|-------------|-----------|---------------|------------|--------------|
| **Frontend Pool** | 1 | 2 vCPUs | 8 GB | 50 GB | 0 | $47 |
| **GPU Pool** | 1 | 4 vCPUs | 16 GB | 100 GB | 1 Tesla T4 | $380 |
| **CPU Pool** | 2 | 8 vCPUs | 32 GB | 100 GB | 0 | $230 |
| **Memory Pool** | 1 | 4 vCPUs | 32 GB | 50 GB | 0 | $182 |
| **Storage Pool** | 1 | 4 vCPUs | 16 GB | 200 GB | 0 | $140 |
| **TOTAL DEVELOPMENT** | **5 nodes** | **22 vCPUs** | **104 GB** | **500 GB** | **1 GPU** | **$979/month** |

---

## 📊 Resource Requirements Analysis

### 🤖 AI/ML Service Resource Requirements

#### **Models Service (Port 8080) - GPU Required**
**AI Models Hosted:**
- **Microsoft Phi-4**: 7.5GB model size, 8-16GB VRAM needed
- **Google Embedding Gemma**: 600MB model
- **Text Processing Models**: Various NLP models for content analysis
- **Cultural Intelligence Models**: Multi-language understanding
- **Future Voice Models**: Reserved space for voice integration

**Resource Specifications:**
```yaml
resources:
  requests:
    memory: "8Gi"  # Reduced without voice models
    cpu: "2"
    nvidia.com/gpu: "1"
  limits:
    memory: "16Gi"
    cpu: "4"
    nvidia.com/gpu: "1"

# GPU Requirements
nodeSelector:
  accelerator: nvidia-tesla-t4  # Or equivalent
tolerations:
  - key: nvidia.com/gpu
    operator: Equal
    value: "true"
    effect: NoSchedule
```

#### **Voice Service (Port 8011) - DISABLED**
**Status:**
- Service disabled for fresh voice integration planning
- Placeholder deployment with minimal resources
- Ready for future voice capabilities implementation

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "0.5"
  limits:
    memory: "2Gi"
    cpu: "1"
# Note: GPU requirements removed - will be added in future voice integration
```

#### **AI Context Store & AI Event Processor - GPU Optional**
```yaml
resources:
  requests:
    memory: "4Gi"
    cpu: "2"
  limits:
    memory: "8Gi"
    cpu: "4"
```

### 💾 Database & Storage Services

#### **PostgreSQL Database**
```yaml
resources:
  requests:
    memory: "8Gi"
    cpu: "2"
    storage: "200Gi"  # SSD recommended
  limits:
    memory: "16Gi"
    cpu: "4"

# Storage Class for persistent volumes
storageClassName: "ssd-retain"
```

#### **Redis Cluster (3 instances)**
```yaml
# Per Redis instance
resources:
  requests:
    memory: "4Gi"
    cpu: "1"
  limits:
    memory: "8Gi"
    cpu: "2"
```

#### **NATS JetStream**
```yaml
resources:
  requests:
    memory: "2Gi"
    cpu: "1"
    storage: "50Gi"
  limits:
    memory: "4Gi"
    cpu: "2"
```

### 🌐 Application Services

#### **API Gateway (Port 8000)**
```yaml
resources:
  requests:
    memory: "2Gi"
    cpu: "1"
  limits:
    memory: "4Gi"
    cpu: "2"

# Auto-scaling configuration
replicas: 3
maxReplicas: 10
targetCPUUtilizationPercentage: 70
```

#### **Core Services (Auth, Profile, Mood, etc.)**
```yaml
# Standard service template
resources:
  requests:
    memory: "1Gi"
    cpu: "0.5"
  limits:
    memory: "2Gi"
    cpu: "1"

replicas: 2
maxReplicas: 5
```

---

## 🏷️ Node Pool Configuration

### **GPU Node Pool** (For AI/ML Workloads)
```yaml
nodePool:
  name: "gpu-pool"
  machineType: 
    # Cloud-agnostic equivalents
    # AWS: p3.xlarge, p3.2xlarge
    # GCP: n1-highmem-4 + Tesla T4
    # Azure: Standard_NC6s_v3
  nodeCount:
    min: 1
    max: 4
    initial: 2
  
  specs:
    cpu: "4-8 vCPUs"
    memory: "16-32 GB"
    gpu: "1x NVIDIA Tesla T4 or equivalent"
    storage: "100GB SSD"
  
  labels:
    workload-type: "gpu-intensive"
    node-type: "gpu"
  
  taints:
    - key: "nvidia.com/gpu"
      value: "true"
      effect: "NoSchedule"
```

### **CPU Node Pool** (For Application Services)
```yaml
nodePool:
  name: "cpu-pool"
  machineType:
    # Cloud-agnostic equivalents
    # AWS: m5.large, m5.xlarge
    # GCP: n1-standard-4
    # Azure: Standard_D4s_v3
  nodeCount:
    min: 3
    max: 10
    initial: 4
  
  specs:
    cpu: "4 vCPUs"
    memory: "16 GB"
    storage: "50GB SSD"
  
  labels:
    workload-type: "general"
    node-type: "cpu"
```

### **Memory-Optimized Node Pool** (For Caching)
```yaml
nodePool:
  name: "memory-pool"
  machineType:
    # Cloud-agnostic equivalents
    # AWS: r5.xlarge
    # GCP: n1-highmem-4
    # Azure: Standard_E4s_v3
  nodeCount:
    min: 1
    max: 3
    initial: 2
  
  specs:
    cpu: "4 vCPUs"
    memory: "32 GB"
    storage: "50GB SSD"
  
  labels:
    workload-type: "memory-intensive"
    node-type: "memory"
```

### **Service-Specific Resource Planning**

#### **Frontend Application Deployment**
```yaml
# Frontend React Application
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mantrapath-frontend
  namespace: mantrapath-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mantrapath-frontend
  template:
    metadata:
      labels:
        app: mantrapath-frontend
    spec:
      nodeSelector:
        node-type: frontend
      containers:
      - name: frontend
        image: mantrapath/frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        env:
        - name: REACT_APP_API_URL
          value: "https://api.mantrapath.com"
        - name: REACT_APP_WEBSOCKET_URL
          value: "wss://api.mantrapath.com"
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/conf.d
      volumes:
      - name: nginx-config
        configMap:
          name: frontend-nginx-config
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  selector:
    app: mantrapath-frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

#### **Complete Service Deployment Templates**

##### **API Gateway (Entry Point)**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: mantrapath-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    spec:
      nodeSelector:
        node-type: cpu
      containers:
      - name: api-gateway
        image: mantrapath/api-gateway:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: url
        - name: REDIS_URL
          value: "redis://redis-primary:6379"
        - name: NATS_URL
          value: "nats://nats:4222"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 5
```

##### **Models Service (GPU Required)**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: models-service
  namespace: mantrapath-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: models-service
  template:
    spec:
      nodeSelector:
        accelerator: nvidia-tesla-t4
      tolerations:
      - key: nvidia.com/gpu
        operator: Equal
        value: "true"
        effect: NoSchedule
      containers:
      - name: models-service
        image: mantrapath/models-service:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
          limits:
            memory: "32Gi"
            cpu: "8"
            nvidia.com/gpu: "1"
        env:
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        - name: TRANSFORMERS_CACHE
          value: "/models/cache"
        - name: MODELS_SERVICE_MODE
          value: "nlp_only"  # NLP only mode
        - name: VOICE_MODELS_DISABLED
          value: "true"
        volumeMounts:
        - name: model-cache
          mountPath: /models
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 120
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 10
      volumes:
      - name: model-cache
        persistentVolumeClaim:
          claimName: models-cache-pvc
```

##### **Voice Service (DISABLED - Future Integration)**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: voice-service
  namespace: mantrapath-prod
  annotations:
    deployment.kubernetes.io/status: "disabled"
    description: "Disabled for fresh voice integration - placeholder deployment"
spec:
  replicas: 0  # Disabled - set to 0
  selector:
    matchLabels:
      app: voice-service
  template:
    spec:
      nodeSelector:
        node-type: cpu  # Moved to CPU pool
      containers:
      - name: voice-service-placeholder
        image: mantrapath/voice-service:disabled
        ports:
        - containerPort: 8011
        resources:
          requests:
            memory: "1Gi"  # Minimal resources
            cpu: "0.5"
          limits:
            memory: "2Gi"
            cpu: "1"
        env:
        - name: SERVICE_STATUS
          value: "DISABLED_FOR_REDESIGN"
        - name: PLACEHOLDER_MODE
          value: "true"
        livenessProbe:
          httpGet:
            path: /health
            port: 8011
          initialDelaySeconds: 30
          periodSeconds: 30
```

##### **Standard Service Template (CPU-based)**
```yaml
# Template for CPU-based services (Auth, Profile, Mood, etc.)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${SERVICE_NAME}
  namespace: mantrapath-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ${SERVICE_NAME}
  template:
    spec:
      nodeSelector:
        node-type: cpu
      containers:
      - name: ${SERVICE_NAME}
        image: mantrapath/${SERVICE_NAME}:latest
        ports:
        - containerPort: ${SERVICE_PORT}
        resources:
          requests:
            memory: "1Gi"
            cpu: "0.5"
          limits:
            memory: "2Gi"
            cpu: "1"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: url
        - name: REDIS_URL
          value: "redis://redis-primary:6379"
        livenessProbe:
          httpGet:
            path: /health
            port: ${SERVICE_PORT}
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: ${SERVICE_PORT}
          initialDelaySeconds: 15
          periodSeconds: 5

# Apply this template for:
# - auth-service (port 8001)
# - profile-service (port 8002)
# - mood-service (port 8003)
# - chatbot-service (port 8004)
# - translation-service (port 8005)
# - content-service (port 8005)
# - community-service (port 8006)
# - notification-service (port 8007)
# - media-service (port 8009)
# - voice-service (port 8011) - DISABLED
# - action-orchestrator (port 8012)
# - ai-context-store (port 8013)
# - ai-event-processor (port 8014)
# - memory-service (port 8017)
# - proactive-assistance (port 8018)
# - deployment-api (port 8019)
```

---

## 🔧 Kubernetes Deployment Configurations

### **Namespace Structure**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mantrapath-prod
  labels:
    environment: production
---
apiVersion: v1
kind: Namespace
metadata:
  name: mantrapath-dev
  labels:
    environment: development
```

### **GPU-Enabled Models Service Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: models-service
  namespace: mantrapath-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: models-service
  template:
    metadata:
      labels:
        app: models-service
    spec:
      nodeSelector:
        accelerator: nvidia-tesla-t4
      tolerations:
        - key: nvidia.com/gpu
          operator: Equal
          value: "true"
          effect: NoSchedule
      containers:
      - name: models-service
        image: mantrapath/models-service:latest
        ports:
        - containerPort: 8080
        env:
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        - name: TRANSFORMERS_CACHE
          value: "/models/cache"
        - name: HF_HOME
          value: "/models/hf"
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
          limits:
            memory: "32Gi"
            cpu: "8"
            nvidia.com/gpu: "1"
        volumeMounts:
        - name: model-cache
          mountPath: /models
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: model-cache
        persistentVolumeClaim:
          claimName: models-cache-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: models-cache-pvc
  namespace: mantrapath-prod
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: ssd-retain
  resources:
    requests:
      storage: 100Gi
```

### **Voice Service with GPU Sharing**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: voice-service
  namespace: mantrapath-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: voice-service
  template:
    metadata:
      labels:
        app: voice-service
    spec:
      nodeSelector:
        accelerator: nvidia-tesla-t4
      tolerations:
        - key: nvidia.com/gpu
          operator: Equal
          value: "true"
          effect: NoSchedule
      containers:
      - name: voice-service
        image: mantrapath/voice-service:latest
        ports:
        - containerPort: 8011
        env:
        - name: MODELS_SERVICE_URL
          value: "http://models-service:8080"
        - name: REDIS_URL
          value: "redis://redis-cluster:6379"
        resources:
          requests:
            memory: "8Gi"
            cpu: "2"
            nvidia.com/gpu: "0.5"
          limits:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: "0.5"
        livenessProbe:
          httpGet:
            path: /health
            port: 8011
          initialDelaySeconds: 30
          periodSeconds: 15
```

### **PostgreSQL with High Availability**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: mantrapath-prod
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      nodeSelector:
        node-type: cpu
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: mantrapath
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        resources:
          requests:
            memory: "8Gi"
            cpu: "2"
            storage: "200Gi"
          limits:
            memory: "16Gi"
            cpu: "4"
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - mantrapath
          initialDelaySeconds: 30
          periodSeconds: 10
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: ssd-retain
      resources:
        requests:
          storage: 200Gi
```

### **Redis Cluster Configuration**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
  namespace: mantrapath-prod
spec:
  serviceName: redis-cluster
  replicas: 3
  selector:
    matchLabels:
      app: redis-cluster
  template:
    metadata:
      labels:
        app: redis-cluster
    spec:
      nodeSelector:
        node-type: memory
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        - containerPort: 16379
        command:
        - redis-server
        args:
        - /etc/redis/redis.conf
        - --cluster-enabled
        - "yes"
        - --cluster-config-file
        - nodes.conf
        - --cluster-node-timeout
        - "5000"
        - --appendonly
        - "yes"
        resources:
          requests:
            memory: "4Gi"
            cpu: "1"
          limits:
            memory: "8Gi"
            cpu: "2"
        volumeMounts:
        - name: redis-storage
          mountPath: /data
        - name: redis-config
          mountPath: /etc/redis
      volumes:
      - name: redis-config
        configMap:
          name: redis-config
  volumeClaimTemplates:
  - metadata:
      name: redis-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: ssd-retain
      resources:
        requests:
          storage: 20Gi
```

---

## 🌍 Cloud-Agnostic Resource Mapping

### **GPU Instance Equivalents**

| Cloud Provider | Instance Type | GPU | vCPUs | Memory | Storage | Cost/Hour (Est.) |
|---------------|---------------|-----|-------|---------|---------|------------------|
| **AWS** | p3.xlarge | 1x V100 | 4 | 61 GB | 25 GB | $3.06 |
| **AWS** | g4dn.xlarge | 1x T4 | 4 | 16 GB | 125 GB | $0.526 |
| **GCP** | n1-standard-4 + T4 | 1x T4 | 4 | 15 GB | 100 GB | $0.50 |
| **Azure** | Standard_NC6s_v3 | 1x V100 | 6 | 112 GB | 736 GB | $3.06 |
| **Azure** | Standard_NC4as_T4_v3 | 1x T4 | 4 | 28 GB | 180 GB | $0.526 |

**Recommended for Production**: Tesla T4 instances for cost-effectiveness

### **CPU Instance Equivalents**

| Cloud Provider | Instance Type | vCPUs | Memory | Storage | Cost/Hour (Est.) |
|---------------|---------------|-------|---------|---------|------------------|
| **AWS** | m5.xlarge | 4 | 16 GB | EBS | $0.192 |
| **GCP** | n1-standard-4 | 4 | 15 GB | 100 GB | $0.189 |
| **Azure** | Standard_D4s_v3 | 4 | 16 GB | 32 GB | $0.192 |

### **Memory-Optimized Equivalents**

| Cloud Provider | Instance Type | vCPUs | Memory | Storage | Cost/Hour (Est.) |
|---------------|---------------|-------|---------|---------|------------------|
| **AWS** | r5.xlarge | 4 | 32 GB | EBS | $0.252 |
| **GCP** | n1-highmem-4 | 4 | 26 GB | 100 GB | $0.237 |
| **Azure** | Standard_E4s_v3 | 4 | 32 GB | 64 GB | $0.252 |

---

## 💰 Cost Optimization Strategy

### **Development Environment**
```yaml
# Reduced resource allocation for dev
resources:
  models-service:
    replicas: 1
    gpu: 0.5  # Shared GPU
    memory: "8Gi"
  
  other-services:
    replicas: 1
    memory: "512Mi"
  
  database:
    storage: "50Gi"
    memory: "4Gi"

# Estimated Monthly Cost: $800-1200
```

### **Production Environment**
```yaml
# Full resource allocation
resources:
  models-service:
    replicas: 2
    gpu: 1
    memory: "16Gi"
  
  critical-services:
    replicas: 3
    memory: "2Gi"
  
  database:
    storage: "200Gi"
    memory: "8Gi"

# Estimated Monthly Cost: $2500-3500
```

### **Auto-scaling Configuration**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 🔒 Security & Networking

### **Network Policies**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mantrapath-network-policy
  namespace: mantrapath-prod
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: mantrapath-prod
    ports:
    - protocol: TCP
      port: 8000-8020
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: mantrapath-prod
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS outbound
    - protocol: TCP
      port: 5432  # PostgreSQL
    - protocol: TCP
      port: 6379  # Redis
```

### **Service Mesh (Optional - Istio)**
```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: mantrapath-istio
spec:
  components:
    pilot:
      k8s:
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
  values:
    global:
      meshID: mantrapath-mesh
      network: mantrapath-network
```

---

## 📊 Monitoring & Observability

### **Prometheus Configuration**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'mantrapath-services'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - mantrapath-prod
          - mantrapath-dev
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
    - job_name: 'gpu-metrics'
      static_configs:
      - targets: ['nvidia-gpu-exporter:9445']
```

### **Grafana Dashboard for AI/ML Metrics**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-gpu-dashboard
data:
  gpu-dashboard.json: |
    {
      "dashboard": {
        "title": "MantraPath GPU & AI Metrics",
        "panels": [
          {
            "title": "GPU Utilization",
            "targets": [
              {
                "expr": "nvidia_gpu_utilization_gpu"
              }
            ]
          },
          {
            "title": "Model Inference Latency",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, rate(model_inference_duration_seconds_bucket[5m]))"
              }
            ]
          },
          {
            "title": "Voice Processing Queue",
            "targets": [
              {
                "expr": "voice_processing_queue_size"
              }
            ]
          }
        ]
      }
    }
```

---

## 🚀 Deployment Pipeline

### **CI/CD Pipeline (GitHub Actions Example)**
```yaml
name: Deploy MantraPath
on:
  push:
    branches: [main, develop]
  
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Cloud CLI
      run: |
        # Cloud-agnostic: Install kubectl and helm
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        chmod +x kubectl && sudo mv kubectl /usr/local/bin/
        
        curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/namespaces.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/configmaps.yaml
        kubectl apply -f k8s/services/
        kubectl apply -f k8s/deployments/
        
        # Wait for rollout
        kubectl rollout status deployment/api-gateway -n mantrapath-prod
        kubectl rollout status deployment/models-service -n mantrapath-prod
    
    - name: Run Health Checks
      run: |
        kubectl run healthcheck --rm -i --restart=Never --image=curlimages/curl -- \
          curl -f http://api-gateway.mantrapath-prod:8000/health
```

### **Complete Helm Chart Structure**
```
helm-charts/mantrapath/
├── Chart.yaml
├── values.yaml                 # Default values
├── values-dev.yaml             # Development environment
├── values-prod.yaml            # Production environment
├── values-gpu.yaml             # GPU-specific configurations
└── templates/
    ├── _helpers.tpl            # Template helpers
    ├── namespace.yaml          # Namespaces
    ├── secrets.yaml            # All secrets
    ├── configmaps.yaml         # Configuration maps
    ├── rbac.yaml              # RBAC policies
    ├── network-policies.yaml   # Network security
    │
    ├── frontend/               # Frontend deployments
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   ├── ingress.yaml
    │   └── configmap.yaml
    │
    ├── infrastructure/         # Infrastructure services
    │   ├── postgres.yaml
    │   ├── redis-primary.yaml
    │   ├── redis-agent.yaml
    │   ├── redis-event.yaml
    │   ├── nats.yaml
    │   └── storage-classes.yaml
    │
    ├── gpu-services/           # GPU-intensive services
    │   ├── models-service.yaml
    │   ├── ai-context-store.yaml
    │   └── ai-event-processor.yaml
    │
    ├── core-services/          # Core application services
    │   ├── api-gateway.yaml
    │   ├── auth-service.yaml
    │   ├── profile-service.yaml
    │   ├── mood-service.yaml
    │   ├── chatbot-service.yaml
    │   ├── translation-service.yaml
    │   ├── content-service.yaml
    │   ├── community-service.yaml
    │   └── notification-service.yaml
    │
    ├── processing-services/    # Processing and utility services
    │   ├── media-service.yaml
    │   ├── action-orchestrator.yaml
    │   ├── voice-service-disabled.yaml  # Placeholder for future integration
    │   ├── memory-service.yaml
    │   ├── proactive-assistance.yaml
    │   └── deployment-api.yaml
    │
    ├── monitoring/             # Monitoring stack
    │   ├── prometheus.yaml
    │   ├── grafana.yaml
    │   ├── gpu-exporter.yaml
    │   └── dashboards/
    │       ├── gpu-dashboard.yaml
    │       ├── service-dashboard.yaml
    │       └── infrastructure-dashboard.yaml
    │
    └── autoscaling/            # Auto-scaling configurations
        ├── hpa-api-gateway.yaml
        ├── hpa-models-service.yaml
        ├── hpa-voice-service.yaml
        ├── cluster-autoscaler.yaml
        └── vertical-pod-autoscaler.yaml
```

### **Complete Values Configuration**

#### **values-prod.yaml (Production Environment)**
```yaml
# Global settings
global:
  environment: production
  registry: "mantrapath"
  imageTag: "latest"
  pullPolicy: "Always"
  
# Node pool configurations
nodePools:
  frontend:
    enabled: true
    nodeCount: 3
    machineType: "n1-standard-2"
  gpu:
    enabled: true
    nodeCount: 2
    machineType: "g4dn.xlarge"
    gpu: "nvidia-tesla-t4"
  cpu:
    enabled: true
    nodeCount: 6
    machineType: "n1-standard-4"
  memory:
    enabled: true
    nodeCount: 3
    machineType: "n1-highmem-4"
  storage:
    enabled: true
    nodeCount: 3
    machineType: "n1-standard-4"

# Frontend configuration
frontend:
  replicas: 3
  resources:
    requests:
      memory: "2Gi"
      cpu: "1"
    limits:
      memory: "4Gi"
      cpu: "2"
  ingress:
    enabled: true
    host: "app.mantrapath.com"
    tls: true

# GPU Services
gpuServices:
  modelsService:
    replicas: 2
    resources:
      requests:
        memory: "8Gi"  # Reduced without voice models
        cpu: "2"
        "nvidia.com/gpu": "1"
      limits:
        memory: "16Gi"
        cpu: "4"
        "nvidia.com/gpu": "1"
    storage:
      size: "50Gi"  # Reduced storage for NLP-only models
      class: "ssd-retain"
  
  # Voice service moved to disabled services
  voiceService:
    enabled: false  # Completely disabled
    replicas: 0
    note: "Disabled for fresh voice integration design"

# Core Services
coreServices:
  apiGateway:
    replicas: 3
    resources:
      requests:
        memory: "2Gi"
        cpu: "1"
      limits:
        memory: "4Gi"
        cpu: "2"
    autoscaling:
      enabled: true
      minReplicas: 3
      maxReplicas: 10
      targetCPU: 70
      targetMemory: 80
  
  authService:
    replicas: 3
    resources:
      requests:
        memory: "1Gi"
        cpu: "0.5"
      limits:
        memory: "2Gi"
        cpu: "1"
  
  # Template for other services
  standardService:
    replicas: 2
    resources:
      requests:
        memory: "1Gi"
        cpu: "0.5"
      limits:
        memory: "2Gi"
        cpu: "1"

# Infrastructure Services
infrastructure:
  postgres:
    replicas: 1
    resources:
      requests:
        memory: "8Gi"
        cpu: "2"
      limits:
        memory: "16Gi"
        cpu: "4"
    storage:
      size: "500Gi"
      class: "ssd-retain"
    backup:
      enabled: true
      schedule: "0 2 * * *"
  
  redis:
    primary:
      resources:
        requests:
          memory: "4Gi"
          cpu: "1"
        limits:
          memory: "8Gi"
          cpu: "2"
    agent:
      resources:
        requests:
          memory: "4Gi"
          cpu: "1"
        limits:
          memory: "8Gi"
          cpu: "2"
    event:
      resources:
        requests:
          memory: "4Gi"
          cpu: "1"
        limits:
          memory: "8Gi"
          cpu: "2"
  
  nats:
    resources:
      requests:
        memory: "2Gi"
        cpu: "1"
      limits:
        memory: "4Gi"
        cpu: "2"
    storage:
      size: "100Gi"
      class: "ssd-retain"

# Monitoring
monitoring:
  enabled: true
  prometheus:
    retention: "30d"
    storage: "100Gi"
  grafana:
    adminPassword: "mantrapath-admin"
  alerting:
    enabled: true
    slack:
      webhook: "{{ .Values.monitoring.slack.webhook }}"

# Security
security:
  networkPolicies:
    enabled: true
  podSecurityPolicies:
    enabled: true
  rbac:
    enabled: true

# Cost optimization
costOptimization:
  spotInstances:
    enabled: false  # Enable for dev environment
  resourceLimits:
    enforced: true
  autoScaling:
    enabled: true
```

#### **values-dev.yaml (Development Environment)**
```yaml
# Override production values for development
global:
  environment: development
  imageTag: "dev"

# Reduced node pools for dev
nodePools:
  frontend:
    nodeCount: 1
  gpu:
    nodeCount: 1
  cpu:
    nodeCount: 2
  memory:
    nodeCount: 1
  storage:
    nodeCount: 1

# Reduced replicas for all services
frontend:
  replicas: 1

gpuServices:
  modelsService:
    replicas: 1
    resources:
      requests:
        memory: "4Gi"  # Further reduced for dev
        cpu: "1"
        "nvidia.com/gpu": "0.5"
  voiceService:
    enabled: false  # Disabled in dev as well
    replicas: 0

coreServices:
  apiGateway:
    replicas: 1
    autoscaling:
      enabled: false
  authService:
    replicas: 1
  standardService:
    replicas: 1

infrastructure:
  postgres:
    storage:
      size: "100Gi"
  redis:
    primary:
      resources:
        requests:
          memory: "2Gi"
          cpu: "0.5"

# Enable cost optimization for dev
costOptimization:
  spotInstances:
    enabled: true
  resourceLimits:
    enforced: false
```

---

## 📋 Pre-Deployment Checklist

### **Infrastructure Requirements**
- [ ] Kubernetes cluster (1.25+) with GPU node pools
- [ ] GPU drivers and NVIDIA device plugin installed
- [ ] Persistent storage classes configured (SSD recommended)
- [ ] Load balancer controller installed
- [ ] DNS and certificate management configured
- [ ] Monitoring stack (Prometheus/Grafana) deployed

### **Security Configuration**
- [ ] RBAC policies configured
- [ ] Network policies applied
- [ ] Secrets management configured
- [ ] Image scanning enabled
- [ ] Pod security policies/admission controllers

### **AI/ML Setup**
- [ ] GPU quota allocated
- [ ] Model storage persistent volumes created
- [ ] Hugging Face token configured (if needed)
- [ ] Model caching strategy implemented
- [ ] GPU sharing configuration validated

### **Testing & Validation**
- [ ] End-to-end health checks passing
- [ ] Voice processing pipeline tested
- [ ] AI model inference validated
- [ ] WebSocket connections working
- [ ] Database connectivity verified
- [ ] Auto-scaling behavior tested

---

## 🔄 Environment-Specific Configurations

### **Development Environment Values**
```yaml
# values-dev.yaml
global:
  environment: development
  replicas: 1
  
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"

gpu:
  enabled: false  # Use CPU-only models for dev

database:
  size: "50Gi"
  
monitoring:
  enabled: false
```

### **Production Environment Values**
```yaml
# values-prod.yaml
global:
  environment: production
  replicas: 3
  
resources:
  requests:
    memory: "2Gi"
    cpu: "1"
  limits:
    memory: "4Gi"
    cpu: "2"

gpu:
  enabled: true
  type: "nvidia-tesla-t4"

database:
  size: "200Gi"
  backup:
    enabled: true
    schedule: "0 2 * * *"

monitoring:
  enabled: true
  alerting: true
```

---

## 📈 Scalability & Performance Tuning

### **GPU Resource Sharing**
```yaml
# Enable GPU sharing for multiple workloads
apiVersion: v1
kind: ConfigMap
metadata:
  name: gpu-sharing-config
data:
  config.yaml: |
    gpu_sharing:
      enabled: true
      memory_limit: "8Gi"  # Per pod GPU memory limit
      compute_limit: "0.5"  # 50% GPU compute per pod
```

### **Model Caching Strategy**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: shared-model-cache
spec:
  accessModes:
    - ReadWriteMany  # Shared across pods
  storageClassName: nfs-client
  resources:
    requests:
      storage: 500Gi
```

### **Database Connection Pooling**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config
data:
  postgresql.conf: |
    max_connections = 200
    shared_buffers = 4GB
    effective_cache_size = 12GB
    work_mem = 64MB
    maintenance_work_mem = 1GB
```

---

## 📊 Cost Analysis Summary

### **Monthly Infrastructure Costs (Estimated)**

#### **Development Environment**
- **GPU Nodes**: 1x Tesla T4 × 24/7 = ~$380/month
- **CPU Nodes**: 2x Standard-4 × 24/7 = ~$276/month  
- **Storage**: 100GB SSD = ~$20/month
- **Load Balancer**: ~$25/month
- **Total Dev Cost**: ~$700/month

#### **Production Environment**
- **GPU Nodes**: 2x Tesla T4 × 24/7 = ~$760/month
- **CPU Nodes**: 4x Standard-4 × 24/7 = ~$552/month
- **Memory Nodes**: 2x High-Memory-4 × 24/7 = ~$364/month
- **Storage**: 500GB SSD + Backups = ~$100/month
- **Load Balancer + CDN**: ~$50/month
- **Monitoring**: ~$50/month
- **Total Prod Cost**: ~$1,876/month

#### **Cost Optimization Opportunities**
- **Spot/Preemptible Instances**: 60-70% cost reduction for non-critical workloads
- **Reserved Instances**: 20-40% discount for committed usage
- **Auto-scaling**: Reduce costs during low-traffic periods
- **Model Optimization**: Smaller models reduce GPU requirements

---

## 🔊 Voice Integration Status & Future Planning

### **Current Voice Service Status: DISABLED**

#### **What Was Removed:**
- **STT (Speech-to-Text) Models**: All IndicWav2Vec and Whisper models
- **TTS (Text-to-Speech) Models**: All Indic-TTS and MMS-TTS models  
- **Voice Processing Pipeline**: Real-time audio processing capabilities
- **GPU Requirements**: Voice-specific GPU allocation (0.5 GPU saved per node)
- **Storage Requirements**: 50GB+ voice model storage removed
- **Voice Event Processor**: Disabled voice analytics and processing

#### **Infrastructure Impact:**
```yaml
# Cost Savings from Voice Removal
resourceSavings:
  gpu: "1x Tesla T4 GPU (50% GPU utilization freed)"
  memory: "16GB RAM freed from voice processing"
  storage: "120GB storage freed from voice models"
  compute: "4 vCPUs freed from voice workloads"
  monthlyCost: "$380/month saved"

# Updated Resource Allocation
currentAllocation:
  gpuNodes: "1 node (down from 2)"
  totalGPUs: "1 Tesla T4 (down from 2)"
  voiceService: "Placeholder deployment with 0 replicas"
  modelsService: "NLP-only mode, voice models disabled"
```

#### **Service Architecture Changes:**
- **Voice Service (Port 8011)**: Moved to CPU pool with 0 replicas (disabled)
- **Models Service**: Switched to `nlp_only` mode, voice models removed
- **GPU Pool**: Reduced from 2 nodes to 1 node
- **Voice Event Processor**: Disabled, ready for future reactivation

#### **Future Voice Integration Readiness:**
```yaml
# Infrastructure Reserved for Voice
voiceIntegrationPlan:
  serviceEndpoint: "Port 8011 reserved"
  deploymentTemplate: "Ready for voice service activation"
  gpuResources: "Can scale GPU pool back to 2 nodes"
  storageSpace: "120GB reserved for voice models"
  networkRouting: "API Gateway voice routes maintained"
  
# Quick Reactivation Strategy
reactivationSteps:
  1: "Enable voice models in Models Service configuration"
  2: "Scale GPU node pool from 1 to 2 nodes" 
  3: "Deploy voice service with replicas: 2"
  4: "Mount voice model storage volumes"
  5: "Enable voice event processing pipeline"
  estimatedReactivationTime: "15-30 minutes"
```

#### **Benefits of Clean Removal:**
✅ **Cost Optimization**: $380/month savings in production  
✅ **Resource Efficiency**: 50% GPU utilization freed for other AI tasks  
✅ **Clean Architecture**: No orphaned voice dependencies  
✅ **Future Flexibility**: Easy to reintegrate with new voice stack  
✅ **Development Focus**: Team can focus on core platform features  
✅ **Infrastructure Ready**: All voice infrastructure patterns preserved  

#### **Maintained Voice Readiness:**
- **API Endpoints**: Voice endpoints preserved but return "disabled" status
- **Network Routing**: API Gateway voice routing rules maintained
- **Database Schema**: Voice-related tables and fields preserved
- **Event Channels**: Voice event channels ready for reactivation
- **Security Policies**: Voice service security configurations maintained
- **Monitoring**: Voice service monitoring dashboards prepared

### **Recommendation for Future Voice Integration:**

When ready to reintegrate voice capabilities:

1. **Assessment Phase** (1 week):
   - Evaluate new voice technologies and providers
   - Design modern STT/TTS architecture
   - Plan integration with existing services

2. **Development Phase** (2-3 weeks):
   - Implement new voice processing pipeline
   - Integrate with Models Service
   - Test with reduced resource requirements

3. **Deployment Phase** (1 week):
   - Scale GPU resources back up
   - Deploy voice services with new architecture
   - Enable voice event processing
   - Complete end-to-end testing

**Total Reintegration Timeline**: 4-5 weeks with modern voice stack

---

## 🎯 Conclusion & Next Steps

### **Immediate Actions (Week 1)**
1. **Set up Kubernetes cluster** with GPU node pools
2. **Configure basic services** (PostgreSQL, Redis, NATS)
3. **Deploy core services** (API Gateway, Auth, Profile)
4. **Test basic functionality** end-to-end

### **Phase 2 (Week 2-3)**
1. **Deploy AI/ML services** with GPU acceleration
2. **Configure voice processing pipeline**
3. **Set up monitoring and alerting**
4. **Performance testing and optimization**

### **Phase 3 (Week 4)**
1. **Production hardening** and security review
2. **Disaster recovery setup**
3. **Load testing and capacity planning**
4. **Documentation and runbooks**

### **Key Success Metrics**
- ✅ **AI Model Inference**: <2s response time for voice/text processing
- ✅ **System Availability**: 99.9% uptime target
- ✅ **Auto-scaling**: Handles 10x traffic spikes gracefully
- ✅ **Cost Efficiency**: Stays within $2000/month budget for production

This comprehensive deployment strategy provides a solid foundation for running MantraPath in production while maintaining cost-effectiveness and scalability for future growth.