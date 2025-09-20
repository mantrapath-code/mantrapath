# MantraPath Helm Deployment

This folder contains an umbrella Helm chart for deploying all services into Kubernetes with an NGINX gateway on port 8080. Two primary environments are supported: dev and prod. Developers can optionally deploy isolated namespaces (e.g., `dev-jane`).

## Structure
- `mantrapath/`: Umbrella chart
  - `charts/`: Subcharts for gateway, api-gateway, frontend, translation-service, models-service, redis, postgres, nats
- `namespaces/`: K8s namespace manifests

## Prerequisites
- Kubernetes cluster running on the server
- kubectl and helm configured
- Container images pushed and accessible by the cluster nodes

## Namespaces
- Dev: `mantrapath-dev`
- Prod: `mantrapath-prod`

To create them manually:

```bash
kubectl apply -f deployment/helm/namespaces/dev.yaml
kubectl apply -f deployment/helm/namespaces/prod.yaml
```

## Deploy to Dev
```bash
helm upgrade --install mantrapath-dev deployment/helm/mantrapath \
  -n mantrapath-dev -f deployment/helm/mantrapath/values.yaml \
  -f deployment/helm/mantrapath/values-dev.yaml

Optional checks before install:

```bash
helm lint deployment/helm/mantrapath
helm template mantrapath-dev deployment/helm/mantrapath -n mantrapath-dev \
  -f deployment/helm/mantrapath/values.yaml -f deployment/helm/mantrapath/values-dev.yaml | head -n 60
```

Access in dev (kind example):
- Gateway (NodePort): http://localhost:30880
- API Gateway service (ClusterIP): `http://mantrapath-dev-api-gateway:8000` inside the cluster
```

## Deploy to Prod
```bash
helm upgrade --install mantrapath-prod deployment/helm/mantrapath \
  -n mantrapath-prod -f deployment/helm/mantrapath/values.yaml \
  -f deployment/helm/mantrapath/values-prod.yaml
```

## Developer Namespaces
To create an isolated namespace for a developer (e.g., `dev-alex`):
```bash
kubectl create ns dev-alex
helm upgrade --install mantrapath-dev-alex deployment/helm/mantrapath -n dev-alex \
  -f deployment/helm/mantrapath/values.yaml -f deployment/helm/mantrapath/values-dev.yaml
```

## Gateway Routing
The NGINX gateway listens on NodePort 30880 mapped to port 8080 inside the Pod. Default routes:
- `/api/` -> `api-gateway:8000`
- `/frontend/` -> `frontend:3000`

Update routes in `charts/gateway-nginx/values.yaml` or override via `-f` files.

## Promotion Flow
1. Push to main triggers GitHub Actions to deploy to `mantrapath-dev`.
2. After verification, promote to prod by running the prod helm upgrade as above or by a separate workflow.

## Zero-impact Maintenance
Each service is independently deployable (subcharts). Update one without impacting others; routing continues via the gateway.

## Deprecating Docker Compose for Dev
Development now targets Kubernetes via Helm. Docker Compose files remain for reference and migration but are not required for dev bring-up. Use:

```bash
kubectl apply -f deployment/helm/namespaces/dev.yaml
helm upgrade --install mantrapath-dev deployment/helm/mantrapath -n mantrapath-dev \
  -f deployment/helm/mantrapath/values.yaml -f deployment/helm/mantrapath/values-dev.yaml
```