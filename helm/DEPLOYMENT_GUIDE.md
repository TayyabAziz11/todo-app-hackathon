# Helm Chart Deployment Guide - Phase V.1

Quick reference guide for deploying Todo App microservices using Helm.

## Quick Start (Minikube)

```bash
# 1. Ensure prerequisites
kubectl cluster-info
dapr status -k
helm version

# 2. Create namespace
kubectl create namespace todo-app-dev

# 3. Deploy using automated script
./scripts/deploy-helm-chart.sh

# OR deploy manually
helm install todo-app ./helm/todo-app \
  -f helm/todo-app/values-minikube.yaml \
  -n todo-app-dev
```

## Chart Location

```
/mnt/e/Certified Cloud Native Generative and Agentic AI Engineer/Q4 part 2/Q4 part 2/Hackathon-2/Todo-app/helm/todo-app/
```

## Services Deployed

| Service | Image | Port | Dapr App ID |
|---------|-------|------|-------------|
| todo-service | todo-service:dev | 8000 | todo-service |
| user-service | user-service:dev | 8000 | user-service |
| chat-service | chat-service:dev | 8000 | chat-service |
| notification-service | notification-service:dev | 8000 | notification-service |
| audit-service | audit-service:dev | 8000 | audit-service |
| analytics-service | analytics-service:dev | 8000 | analytics-service |

## Resource Specifications

### Default (Production)
- Memory: 128Mi request / 256Mi limit
- CPU: 100m request / 200m limit
- Replicas: 1

### Minikube (Development)
- Memory: 64Mi request / 128Mi limit
- CPU: 50m request / 100m limit
- Replicas: 1

## Essential Commands

### Deployment

```bash
# Install (first time)
helm install todo-app ./helm/todo-app \
  -f helm/todo-app/values-minikube.yaml \
  -n todo-app-dev

# Upgrade (updates)
helm upgrade todo-app ./helm/todo-app \
  -f helm/todo-app/values-minikube.yaml \
  -n todo-app-dev

# Dry run (test before deploy)
helm install todo-app ./helm/todo-app \
  -f helm/todo-app/values-minikube.yaml \
  -n todo-app-dev \
  --dry-run --debug
```

### Validation

```bash
# Check Helm release
helm status todo-app -n todo-app-dev
helm list -n todo-app-dev

# Check pods (should show 2/2 READY - app + daprd)
kubectl get pods -n todo-app-dev

# Check services
kubectl get svc -n todo-app-dev

# Check Dapr components
kubectl get components -n todo-app-dev
```

### Monitoring

```bash
# Watch pods
kubectl get pods -n todo-app-dev -w

# Pod logs (application)
kubectl logs -n todo-app-dev -l app.kubernetes.io/name=todo-service -c todo-service

# Pod logs (Dapr sidecar)
kubectl logs -n todo-app-dev -l app.kubernetes.io/name=todo-service -c daprd

# Events
kubectl get events -n todo-app-dev --sort-by='.lastTimestamp'
```

### Access Services

```bash
# Port-forward individual services
kubectl port-forward -n todo-app-dev svc/todo-service 8000:8000
kubectl port-forward -n todo-app-dev svc/user-service 8001:8000
kubectl port-forward -n todo-app-dev svc/chat-service 8002:8000

# Test health
curl http://localhost:8000/health/ready
curl http://localhost:8000/health/live
```

### Maintenance

```bash
# Rollback to previous version
helm rollback todo-app -n todo-app-dev

# Rollback to specific revision
helm history todo-app -n todo-app-dev
helm rollback todo-app 1 -n todo-app-dev

# Uninstall
helm uninstall todo-app -n todo-app-dev
```

## Dapr Annotations

Each pod includes these Dapr annotations:

```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "<service-name>"
  dapr.io/app-port: "8000"
  dapr.io/log-level: "info"  # "debug" in Minikube values
  dapr.io/enable-api-logging: "true"
```

## Health Probes

All services include:

**Readiness Probe:**
- Path: `/health/ready`
- Initial Delay: 10s (5s for Minikube)
- Period: 10s (5s for Minikube)

**Liveness Probe:**
- Path: `/health/live`
- Initial Delay: 30s (15s for Minikube)
- Period: 15s (10s for Minikube)

## Customization

### Override Values

Create custom values file:

```yaml
# my-custom-values.yaml
global:
  replicaCount: 2

resources:
  limits:
    memory: "512Mi"
    cpu: "500m"

services:
  todoService:
    env:
      - name: LOG_LEVEL
        value: "DEBUG"
```

Deploy with custom values:

```bash
helm install todo-app ./helm/todo-app \
  -f helm/todo-app/values.yaml \
  -f my-custom-values.yaml \
  -n todo-app-dev
```

### Disable Specific Services

```yaml
# In values file
services:
  analyticsService:
    enabled: false
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod details
kubectl describe pod <pod-name> -n todo-app-dev

# Check events
kubectl get events -n todo-app-dev --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -c <container-name> -n todo-app-dev
```

### Image Pull Errors

```bash
# For Minikube, use Minikube's Docker daemon
eval $(minikube docker-env)

# Verify images
docker images | grep -E "(todo|user|chat|notification|audit|analytics)-service"

# Rebuild if needed
cd services/<service-name>
docker build -t <service-name>:dev .
```

### Dapr Sidecar Issues

```bash
# Check Dapr installation
dapr status -k

# Check Dapr components
kubectl get components -n todo-app-dev

# Verify Dapr sidecar injected
kubectl get pod <pod-name> -n todo-app-dev -o yaml | grep dapr
```

### Resource Constraints

```bash
# Check node resources
kubectl top nodes

# Check pod resources
kubectl top pods -n todo-app-dev

# If insufficient, reduce in values file
resources:
  limits:
    memory: "128Mi"
    cpu: "100m"
```

## Pre-Deployment Checklist

- [ ] Kubernetes cluster accessible (`kubectl cluster-info`)
- [ ] Dapr installed in cluster (`dapr status -k`)
- [ ] Helm 3+ installed (`helm version`)
- [ ] Namespace created (`kubectl create namespace todo-app-dev`)
- [ ] Docker images built (all 6 services with `:dev` tag)
- [ ] Dapr components deployed (statestore, secretstore)
- [ ] Chart validated (`helm lint ./helm/todo-app`)

## Post-Deployment Validation

- [ ] All pods running with 2/2 containers (`kubectl get pods -n todo-app-dev`)
- [ ] All services created (`kubectl get svc -n todo-app-dev`)
- [ ] Dapr sidecars injected (check pod details)
- [ ] Health endpoints responding (port-forward and curl)
- [ ] No error events (`kubectl get events -n todo-app-dev`)

## File Structure

```
helm/todo-app/
├── Chart.yaml                    # Chart metadata
├── values.yaml                   # Default values (production)
├── values-minikube.yaml          # Minikube-specific values
├── README.md                     # Full documentation
├── .helmignore                   # Files to ignore
└── templates/
    ├── _helpers.tpl              # Template helpers
    ├── NOTES.txt                 # Post-install instructions
    ├── *-deployment.yaml         # 6 deployment templates
    └── *-service.yaml            # 6 service templates
```

## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Pods pending | Check resource limits, node capacity |
| ImagePullBackOff | Verify images exist in Minikube registry |
| CrashLoopBackOff | Check application logs, health endpoints |
| Dapr sidecar missing | Verify Dapr installed, namespace labeled |
| Service not accessible | Check service type (ClusterIP), port-forward |

## Next Steps After Deployment

1. Verify all services are healthy
2. Test inter-service communication via Dapr
3. Check Dapr state store integration
4. Test service mesh features
5. Monitor resource usage
6. Set up ingress for external access (if needed)

## Support Resources

- Chart README: `/mnt/e/.../helm/todo-app/README.md`
- Helm Docs: https://helm.sh/docs/
- Dapr Docs: https://docs.dapr.io/
- Kubernetes Docs: https://kubernetes.io/docs/

## Quick Test Script

```bash
#!/bin/bash
# Test all services
NAMESPACE="todo-app-dev"
SERVICES=("todo-service" "user-service" "chat-service" "notification-service" "audit-service" "analytics-service")

for service in "${SERVICES[@]}"; do
    echo "Testing $service..."
    kubectl port-forward -n $NAMESPACE svc/$service 8000:8000 &
    PID=$!
    sleep 2
    curl -s http://localhost:8000/health/ready
    kill $PID
    echo ""
done
```

## Production Considerations

When deploying to production (Oracle OKE):

1. Create `values-production.yaml` with:
   - Increased resource limits
   - Production log levels (info/warn)
   - Appropriate replica counts
   - Persistent storage if needed

2. Use secrets management:
   - External secret store
   - Dapr secret store component
   - Kubernetes secrets

3. Configure ingress:
   - NGINX Ingress Controller
   - SSL/TLS certificates
   - Domain routing

4. Set up monitoring:
   - Prometheus/Grafana
   - Dapr dashboard
   - Centralized logging

5. Implement CI/CD:
   - ArgoCD for GitOps
   - Automated deployments
   - Rollback strategies
