# Namespace Assets

This folder contains base namespaces and shared, pre-created secrets.

## Vultr Container Registry Secret

We pre-provision a dockerconfig secret named `vultr-cr-credentials` for both namespaces so workloads can pull images from `blr.vultrcr.com/mantrapath`.

Apply:

```bash
kubectl apply -f deployment/helm/namespaces/dev.yaml
kubectl apply -f deployment/helm/namespaces/prod.yaml
kubectl apply -f deployment/helm/namespaces/registry-secrets.yaml
```

Verify:

```bash
kubectl get secret vultr-cr-credentials -n mantrapath-dev -o yaml | head -n 20
kubectl get secret vultr-cr-credentials -n mantrapath-prod -o yaml | head -n 20
```

Pods reference this secret via `global.imagePullSecrets` in Helm values.
