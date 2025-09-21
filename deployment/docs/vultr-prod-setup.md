# MantraPath Production Setup - Vultr Kubernetes

This document outlines the production deployment setup for MantraPath on Vultr Kubernetes cluster.

## Vultr Kubernetes Configuration

### Prerequisites
- Vultr Kubernetes cluster provisioned
- kubectl configured with cluster credentials
- Helm 3.x installed
- Access to Vultr Container Registry

### Production Environment Specifications

#### Cluster Requirements
- **Node Pool:** Minimum 3 worker nodes
- **Instance Type:** vc2-4c-8gb or higher
- **Storage:** High-performance block storage
- **Networking:** Load balancer for ingress

#### Resource Allocation
- **API Gateway:** 2 replicas, 2GB RAM, 1 CPU
- **Frontend:** 2 replicas, 1GB RAM, 0.5 CPU
- **Translation Service:** 2 replicas, 4GB RAM, 2 CPU
- **Models Service:** 2 replicas, 8GB RAM, 4 CPU
- **Database:** PostgreSQL with persistent storage (50GB)
- **Cache:** Redis with persistent storage (10GB)

## Production Configuration Files

### 1. Production Values Override
File: `values-vultr-prod.yaml`

```yaml
global:
  env: prod
  registry: "blr.vultrcr.com/mantrapath"
  namespace: mantrapath-prod
  
  # Production secrets (manage externally)
  secrets:
    postgres:
      database: "mantrapath_prod"
      user: "mantrapath_prod"
      password: "${POSTGRES_PASSWORD}"  # From external secret
    jwt:
      secretKey: "${JWT_SECRET_KEY}"    # From external secret
    external:
      openaiApiKey: "${OPENAI_API_KEY}" # From external secret

# High availability configuration
apiGateway:
  replicaCount: 3
  resources:
    requests:
      cpu: "500m"
      memory: "1Gi"
    limits:
      cpu: "2000m"
      memory: "4Gi"
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10

frontend:
  replicaCount: 2
  resources:
    requests:
      cpu: "200m"
      memory: "512Mi"
    limits:
      cpu: "1000m"
      memory: "2Gi"

# Database with persistence
postgres:
  enabled: true
  storage:
    size: 50Gi
    storageClass: "vultr-block-storage-hdd"
  resources:
    requests:
      cpu: "1000m"
      memory: "2Gi"
    limits:
      cpu: "4000m"
      memory: "8Gi"

# Redis with persistence
redis:
  enabled: true
  storage:
    size: 10Gi
    storageClass: "vultr-block-storage-hdd"
  resources:
    requests:
      cpu: "500m"
      memory: "1Gi"
    limits:
      cpu: "2000m"
      memory: "4Gi"

# Enable all production services
translationService:
  enabled: true
  replicaCount: 2
modelsService:
  enabled: true
  replicaCount: 2
authService:
  enabled: true
  replicaCount: 2
# ... (all other services)

# Production ingress with SSL
ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: mantrapath.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: mantrapath-tls
      hosts:
        - mantrapath.com

# Production monitoring
monitoring:
  enabled: true
  prometheus:
    enabled: true
  grafana:
    enabled: true
  alerts:
    enabled: true
```

### 2. Production Deployment Script
File: `scripts/deploy-vultr-prod.sh`

```bash
#!/bin/bash
set -euo pipefail

# Vultr Kubernetes Production Deployment
CLUSTER_NAME="mantrapath-prod"
NAMESPACE="mantrapath-prod"
REGISTRY="blr.vultrcr.com/mantrapath"

# Validate environment
if [[ -z "${KUBECONFIG:-}" ]]; then
    echo "Error: KUBECONFIG not set for Vultr cluster"
    exit 1
fi

# Verify cluster access
echo "Verifying Vultr cluster access..."
kubectl cluster-info

# Create namespace
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Create registry secret
kubectl create secret docker-registry mantrapath-prod-registry \
    --docker-server=blr.vultrcr.com \
    --docker-username=e9b950f6-81b8-4433-bb62-844d3f44b6bb \
    --docker-password=D5w5WAevjZQhcUrEQPcuuA6qgCTXzTfLHtYJ \
    --namespace=$NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

# Deploy with Helm
helm upgrade --install mantrapath-prod ./deployment/helm/mantrapath \
    --namespace $NAMESPACE \
    --values ./deployment/helm/mantrapath/values-vultr-prod.yaml \
    --set global.registry=$REGISTRY \
    --timeout 20m \
    --wait \
    --atomic

echo "Production deployment completed!"
```

## Security Considerations

### 1. External Secret Management
- Use Vultr's secret management or external-secrets operator
- Never store production secrets in values files
- Rotate secrets regularly

### 2. Network Security
- Configure network policies
- Use private node pools
- Enable cluster firewall rules

### 3. SSL/TLS Configuration
- Install cert-manager for automatic SSL certificates
- Use Let's Encrypt for domain validation
- Configure HSTS headers

## Monitoring and Observability

### 1. Prometheus Stack
```yaml
# Install kube-prometheus-stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --create-namespace
```

### 2. Logging
- Use Vultr's managed logging service
- Configure log aggregation with Fluentd/Fluent Bit
- Set up log retention policies

### 3. Alerts
- Configure alerts for high resource usage
- Set up notifications for pod failures
- Monitor application-specific metrics

## Backup and Disaster Recovery

### 1. Database Backups
- Schedule automated PostgreSQL backups
- Store backups in Vultr Object Storage
- Test restore procedures regularly

### 2. Application Backups
- Backup Kubernetes manifests and configurations
- Use Velero for cluster-wide backups
- Document recovery procedures

## Scaling Configuration

### 1. Horizontal Pod Autoscaling
```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

### 2. Cluster Autoscaling
- Configure Vultr cluster autoscaler
- Set minimum and maximum node counts
- Define scaling policies

## Cost Optimization

### 1. Resource Limits
- Set appropriate CPU and memory limits
- Use resource quotas per namespace
- Monitor resource utilization

### 2. Storage Optimization
- Use appropriate storage classes
- Implement data lifecycle policies
- Monitor storage usage and costs

## Deployment Pipeline

### 1. CI/CD Integration
- GitHub Actions with Vultr credentials
- Automated testing before production deployment
- Blue-green deployment strategy

### 2. Environment Promotion
```bash
# Promote from staging to production
./scripts/promote-to-production.sh \
    --from-tag=staging-v1.2.3 \
    --to-env=production
```

## Troubleshooting

### Common Issues
1. **Pod scheduling failures:** Check node resources and taints
2. **Image pull errors:** Verify registry credentials
3. **Ingress issues:** Check load balancer configuration
4. **Persistent volume issues:** Verify storage class availability

### Monitoring Commands
```bash
# Check cluster health
kubectl get nodes
kubectl get pods --all-namespaces

# Check specific deployment
kubectl get pods -n mantrapath-prod
kubectl logs -f deployment/mantrapath-prod-api-gateway -n mantrapath-prod

# Check ingress
kubectl get ingress -n mantrapath-prod
kubectl describe ingress mantrapath-prod-ingress -n mantrapath-prod
```

