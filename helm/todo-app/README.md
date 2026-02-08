# Todo App Helm Chart

Production-ready Helm chart for deploying Todo App microservices with Dapr integration on Kubernetes.

## Overview

This Helm chart deploys a complete microservices architecture for the Todo application, including:

- **todo-service**: Core todo management service
- **user-service**: User authentication and management
- **chat-service**: AI-powered chat functionality
- **notification-service**: Push notifications and alerts
- **audit-service**: Audit logging and compliance
- **analytics-service**: Usage analytics and reporting

All services are deployed with:
- Dapr sidecar injection for service mesh capabilities
- Health checks (liveness and readiness probes)
- Resource limits optimized for Oracle Free Tier
- Security contexts (non-root users, capability dropping)
- Service discovery via ClusterIP services

## Prerequisites

1. **Kubernetes Cluster**: Minikube, Oracle OKE, or any Kubernetes 1.19+
2. **Helm**: Version 3.0+
3. **Dapr**: Installed and configured in cluster
4. **Namespace**: `todo-app-dev` created
5. **Docker Images**: All service images built and available

### Verify Prerequisites

```bash
# Check Kubernetes cluster
kubectl cluster-info

# Check Helm version
helm version

# Check Dapr installation
dapr status -k

# Create namespace if not exists
kubectl create namespace todo-app-dev

# Verify Dapr components
kubectl get components -n todo-app-dev
```

## Installation

### Standard Installation

```bash
# From project root
helm install todo-app ./helm/todo-app -n todo-app-dev
```

### Minikube Installation (Recommended for Development)

```bash
# Use Minikube-specific values
helm install todo-app ./helm/todo-app \
  -f helm/todo-app/values-minikube.yaml \
  -n todo-app-dev
```

### Dry Run (Test Before Installing)

```bash
helm install todo-app ./helm/todo-app \
  -f helm/todo-app/values-minikube.yaml \
  -n todo-app-dev \
  --dry-run --debug
```

## Configuration

### Default Values (`values.yaml`)

The chart comes with production-ready defaults:

```yaml
global:
  namespace: todo-app-dev
  imagePullPolicy: IfNotPresent
  replicaCount: 1

resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"

dapr:
  enabled: true
  logLevel: info
```

### Minikube Values (`values-minikube.yaml`)

Optimized for local development:

```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "50m"
  limits:
    memory: "128Mi"
    cpu: "100m"

dapr:
  logLevel: debug
```

### Custom Configuration

Create your own values file:

```bash
# Create custom values
cat > my-values.yaml <<EOF
global:
  replicaCount: 2

resources:
  limits:
    memory: "512Mi"
    cpu: "500m"

services:
  todoService:
    env:
      - name: CUSTOM_VAR
        value: "custom-value"
EOF

# Install with custom values
helm install todo-app ./helm/todo-app \
  -f helm/todo-app/values.yaml \
  -f my-values.yaml \
  -n todo-app-dev
```

## Upgrading

### Standard Upgrade

```bash
helm upgrade todo-app ./helm/todo-app -n todo-app-dev
```

### Upgrade with New Values

```bash
helm upgrade todo-app ./helm/todo-app \
  -f helm/todo-app/values-minikube.yaml \
  -n todo-app-dev
```

### Rollback

```bash
# List releases
helm history todo-app -n todo-app-dev

# Rollback to previous version
helm rollback todo-app -n todo-app-dev

# Rollback to specific revision
helm rollback todo-app 1 -n todo-app-dev
```

## Verification

### Check Deployment Status

```bash
# Check Helm release
helm status todo-app -n todo-app-dev

# Check pods
kubectl get pods -n todo-app-dev

# Check services
kubectl get svc -n todo-app-dev

# Check Dapr components
kubectl get components -n todo-app-dev
```

### Expected Output

```
NAME                                    READY   STATUS    RESTARTS   AGE
todo-service-xxx-yyy                    2/2     Running   0          2m
user-service-xxx-yyy                    2/2     Running   0          2m
chat-service-xxx-yyy                    2/2     Running   0          2m
notification-service-xxx-yyy            2/2     Running   0          2m
audit-service-xxx-yyy                   2/2     Running   0          2m
analytics-service-xxx-yyy               2/2     Running   0          2m
```

Note: Each pod has 2 containers (app + daprd sidecar)

### Test Service Health

```bash
# Port-forward to todo-service
kubectl port-forward -n todo-app-dev svc/todo-service 8000:8000 &

# Test health endpoints
curl http://localhost:8000/health/ready
curl http://localhost:8000/health/live

# Stop port-forward
killall kubectl
```

## Troubleshooting

### Pods Not Starting

```bash
# Check events
kubectl get events -n todo-app-dev --sort-by='.lastTimestamp'

# Describe pod
kubectl describe pod <pod-name> -n todo-app-dev

# Check logs (application)
kubectl logs <pod-name> -c todo-service -n todo-app-dev

# Check logs (Dapr sidecar)
kubectl logs <pod-name> -c daprd -n todo-app-dev
```

### Image Pull Errors

```bash
# Verify images exist locally (Minikube)
eval $(minikube docker-env)
docker images | grep -E "(todo|user|chat|notification|audit|analytics)-service"

# If images missing, rebuild
# (Navigate to each service and build)
cd services/todo-service
docker build -t todo-service:dev .
```

### Dapr Sidecar Not Injected

```bash
# Check Dapr installation
dapr status -k

# Verify Dapr running in dapr-system namespace
kubectl get pods -n dapr-system

# Check pod annotations
kubectl get pod <pod-name> -n todo-app-dev -o yaml | grep dapr
```

### Resource Constraints

```bash
# Check node resources
kubectl top nodes

# Check pod resources
kubectl top pods -n todo-app-dev

# If resources insufficient, reduce limits in values file
```

## Uninstallation

```bash
# Uninstall release
helm uninstall todo-app -n todo-app-dev

# Verify removal
helm list -n todo-app-dev
kubectl get pods -n todo-app-dev
```

## Advanced Usage

### Disable Specific Services

```yaml
# In custom values file
services:
  analyticsService:
    enabled: false
```

### Custom Resource Limits per Service

```yaml
# Not directly supported; requires template modification
# Or use multiple releases for different services
```

### Environment-Specific Deployments

```bash
# Development
helm install todo-app-dev ./helm/todo-app \
  -f helm/todo-app/values-minikube.yaml \
  -n todo-app-dev

# Staging (create values-staging.yaml)
helm install todo-app-staging ./helm/todo-app \
  -f helm/todo-app/values-staging.yaml \
  -n todo-app-staging

# Production (create values-production.yaml)
helm install todo-app-prod ./helm/todo-app \
  -f helm/todo-app/values-production.yaml \
  -n todo-app-prod
```

## Chart Structure

```
helm/todo-app/
├── Chart.yaml                              # Chart metadata
├── values.yaml                             # Default values
├── values-minikube.yaml                    # Minikube overrides
├── .helmignore                             # Files to ignore
├── README.md                               # This file
└── templates/
    ├── _helpers.tpl                        # Template helpers
    ├── NOTES.txt                           # Post-install notes
    ├── todo-service-deployment.yaml        # Todo service deployment
    ├── todo-service-service.yaml           # Todo service
    ├── user-service-deployment.yaml        # User service deployment
    ├── user-service-service.yaml           # User service
    ├── chat-service-deployment.yaml        # Chat service deployment
    ├── chat-service-service.yaml           # Chat service
    ├── notification-service-deployment.yaml # Notification deployment
    ├── notification-service-service.yaml   # Notification service
    ├── audit-service-deployment.yaml       # Audit service deployment
    ├── audit-service-service.yaml          # Audit service
    ├── analytics-service-deployment.yaml   # Analytics deployment
    └── analytics-service-service.yaml      # Analytics service
```

## Best Practices

1. **Always use values files** for environment-specific configuration
2. **Test with `--dry-run`** before deploying to production
3. **Monitor resource usage** and adjust limits accordingly
4. **Use semantic versioning** for chart versions
5. **Keep secrets external** - use Kubernetes secrets or external secret stores
6. **Document custom values** in comments for team reference
7. **Version control values files** for different environments

## Support

For issues and questions:
- Check the [troubleshooting section](#troubleshooting)
- Review Kubernetes events and logs
- Consult Dapr documentation for sidecar issues
- Check project documentation

## License

Part of Todo App project - see main repository for license information.
