# MantraPath Production Port Mapping

## 🎯 Centralized Port Configuration
All service ports are defined in `values-prod.yaml` under `global.ports` to prevent conflicts and ensure consistency.

## 📊 Port Allocation Strategy

### Infrastructure Services
| Service | Port | Range | Description |
|---------|------|-------|-------------|
| PostgreSQL | 5432 | Standard | Database |
| Redis | 6379 | Standard | Cache |
| NATS | 4222 | Standard | Message Queue |
| Frontend | 3000 | Standard | React App |
| Gateway | 8080 | Standard | Nginx Gateway |

### Core API Services (80xx range)
| Service | Port | Function |
|---------|------|----------|
| API Gateway | 8000 | Main API Gateway |
| Models Service | 8001 | AI/ML Model Inference |
| Translation Service | 8002 | Language Translation |
| Translation gRPC | 9002 | gRPC for Translation |

### Authentication & User Services (81xx range)
| Service | Port | Function |
|---------|------|----------|
| Auth Service | 8100 | Authentication & Authorization |
| Profile Service | 8101 | User Profile Management |
| Mood Service | 8102 | Mood Tracking & Analysis |

### AI & ML Services (82xx range)
| Service | Port | Function |
|---------|------|----------|
| Chatbot Service | 8200 | Conversational AI |
| ML Service | 8201 | Machine Learning Pipeline |
| AI Context Store | 8202 | Context Management |
| AI Event Processor | 8203 | Event Processing |
| Memory Service | 8204 | Context & Memory Store |
| Proactive Assistance | 8205 | Proactive AI |

### Content & Media Services (83xx range)
| Service | Port | Function |
|---------|------|----------|
| Content Service | 8300 | Content Management |
| Media Service | 8301 | Media File Handling |
| Community Service | 8302 | Community Features |
| Notification Service | 8303 | Push Notifications |

### Voice & Audio Services (84xx range)
| Service | Port | Function |
|---------|------|----------|
| Voice Service | 8400 | Voice Processing |
| Voice Event Processor | 8401 | Voice Events |

### Orchestration & Workflow Services (85xx range)
| Service | Port | Function |
|---------|------|----------|
| Action Orchestrator | 8500 | Workflow Management |

## 🔧 Production Configuration

### Resource Allocation
- **High-Performance Services**: Models (8001), ML (8201), Voice (8400)
  - CPU: 1-4 cores, Memory: 2-8GB
- **Standard Services**: Auth (8100), Profile (8101), Content (8300)
  - CPU: 200m-1 core, Memory: 256Mi-1GB
- **AI Services**: Chatbot (8200), AI Context (8202), Memory (8204)
  - CPU: 300m-2 cores, Memory: 512Mi-4GB

### Autoscaling Configuration
- **API Gateway (8000)**: 3-15 replicas
- **Chatbot Service (8200)**: 3-12 replicas
- **Models Service (8001)**: 2-10 replicas
- **Translation Service (8002)**: 2-8 replicas

### Pod Disruption Budgets
- **Critical Services**: Minimum 2 replicas available
- **Standard Services**: Maximum 1 unavailable
- **Infrastructure**: Always available (PostgreSQL, Redis, NATS)

## 🌐 External Access

### Production URLs
- **Frontend**: https://mantrapath.com
- **API Gateway**: https://api.mantrapath.com
- **Health Checks**: https://api.mantrapath.com/health

### NodePort Access (if needed)
- **Gateway**: NodePort 30880 → 8080
- **API**: NodePort 30800 → 8000

## 🔒 Security Configuration

### TLS/SSL
- **Cert Manager**: Automatic Let's Encrypt certificates
- **Ingress**: nginx with SSL termination
- **Internal**: Service-to-service communication encrypted

### Secrets Management
- **Database**: Secure PostgreSQL credentials
- **JWT**: 256-bit secure keys
- **Redis**: Authentication enabled
- **External APIs**: OpenAI, SMTP credentials

## 📝 Deployment Commands

### Production Deployment
```bash
# Deploy to production
./deployment/helm-deploy.sh --environment prod

# Deploy with custom values
helm upgrade --install mantrapath-prod . \
  --namespace mantrapath-prod \
  --values values-prod.yaml \
  --set global.env=prod

# Scale specific service
kubectl scale deployment mantrapath-prod-chatbot-service --replicas=5 -n mantrapath-prod

# Check service status
kubectl get pods -n mantrapath-prod | grep chatbot-service
```

### Port Testing
```bash
# Test API Gateway
curl https://api.mantrapath.com/health

# Test specific service via port-forward
kubectl port-forward svc/mantrapath-prod-chatbot-service 8200:8200 -n mantrapath-prod
curl http://localhost:8200/health

# Test database connection
kubectl exec -it mantrapath-prod-postgres-0 -n mantrapath-prod -- psql -U mantrapath_prod -d mantrapath_prod
```

## 🚨 Important Notes

1. **Port Conflicts**: All ports are carefully allocated to prevent conflicts
2. **Single Source of Truth**: All ports defined in `values-prod.yaml` under `global.ports`
3. **Easy Updates**: Change port in one place, affects all references
4. **Production Ready**: Resource limits, autoscaling, and PDBs configured
5. **Monitoring**: Prometheus and Grafana integration ready
6. **Security**: TLS, secrets, and network policies configured

## 📊 Quick Reference

```yaml
# To change any service port, edit values-prod.yaml:
global:
  ports:
    authService: 8100      # Change here
    chatbotService: 8200   # Change here
    # etc...
```

This ensures all templates, services, and configurations automatically use the updated ports!

