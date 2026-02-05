# Todo Backend Helm Chart

Production-ready Helm chart for the Todo Backend FastAPI application with PostgreSQL database and OpenAI integration.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- Minikube (for local development)
- kubectl configured to communicate with your cluster

### Kubernetes Secret

Before deploying the backend, create the required Kubernetes Secret in the `todo-dev` namespace:

```bash
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL='your-postgresql-connection-string' \
  --from-literal=SECRET_KEY='your-jwt-secret-key-min-32-chars' \
  --from-literal=OPENAI_API_KEY='your-openai-api-key' \
  --namespace todo-dev
```

**Required Secret Keys:**
- `DATABASE_URL`: PostgreSQL connection string (e.g., Neon Serverless PostgreSQL)
- `SECRET_KEY`: JWT secret key (minimum 32 characters)
- `OPENAI_API_KEY`: OpenAI API key for Phase 3 chatbot functionality

**Verify Secret Creation:**
```bash
kubectl get secret todo-backend-secrets -n todo-dev
```

## Installation

### Standard Installation

Install the chart with default values:

```bash
helm install todo-backend ./charts/todo-backend --namespace todo-dev
```

### Minikube Development Installation

Install with development-specific resource limits:

```bash
helm install todo-backend ./charts/todo-backend \
  -f charts/todo-backend/values.yaml \
  -f charts/todo-backend/values-dev.yaml \
  --namespace todo-dev
```

### Custom Installation

Override specific values:

```bash
helm install todo-backend ./charts/todo-backend \
  --namespace todo-dev \
  --set replicaCount=2 \
  --set image.tag=v1.0.1 \
  --set resources.requests.memory=512Mi
```

### Installation from Custom Values File

Create your own values file:

```bash
helm install todo-backend ./charts/todo-backend \
  -f charts/todo-backend/values.yaml \
  -f my-custom-values.yaml \
  --namespace todo-dev
```

## Upgrading

### Upgrade with New Image Version

```bash
helm upgrade todo-backend ./charts/todo-backend \
  --namespace todo-dev \
  --set image.tag=v1.0.1 \
  --reuse-values
```

### Upgrade with New Values File

```bash
helm upgrade todo-backend ./charts/todo-backend \
  -f charts/todo-backend/values-dev.yaml \
  --namespace todo-dev
```

### Force Rollout (Restart Pods)

```bash
helm upgrade todo-backend ./charts/todo-backend \
  --namespace todo-dev \
  --set podAnnotations."kubectl\.kubernetes\.io/restartedAt"="$(date +%Y%m%d%H%M%S)" \
  --reuse-values
```

## Rollback

### View Release History

```bash
helm history todo-backend --namespace todo-dev
```

### Rollback to Previous Version

```bash
helm rollback todo-backend --namespace todo-dev
```

### Rollback to Specific Revision

```bash
helm rollback todo-backend 2 --namespace todo-dev
```

## Uninstallation

Remove the chart and all associated resources:

```bash
helm uninstall todo-backend --namespace todo-dev
```

**Note:** This does NOT delete the Secret `todo-backend-secrets`. To remove it:

```bash
kubectl delete secret todo-backend-secrets --namespace todo-dev
```

## Verification

### Check Deployment Status

```bash
kubectl get deployments -n todo-dev
kubectl get pods -n todo-dev -l app.kubernetes.io/name=todo-backend
kubectl get svc -n todo-dev -l app.kubernetes.io/name=todo-backend
```

### View Helm Release Information

```bash
helm status todo-backend --namespace todo-dev
helm get values todo-backend --namespace todo-dev
helm get manifest todo-backend --namespace todo-dev
```

### Check Application Logs

```bash
kubectl logs -n todo-dev -l app.kubernetes.io/name=todo-backend -f
```

### Test Health Endpoint

Port-forward to the service:

```bash
kubectl port-forward -n todo-dev svc/todo-backend 8000:8000
```

Then access the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

## Configuration

### Key Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `todo-backend` |
| `image.tag` | Image tag | `v1.0.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `resources.requests.memory` | Memory request | `256Mi` (prod), `128Mi` (dev) |
| `resources.requests.cpu` | CPU request | `250m` (prod), `100m` (dev) |
| `resources.limits.memory` | Memory limit | `512Mi` (prod), `256Mi` (dev) |
| `resources.limits.cpu` | CPU limit | `500m` (prod), `250m` (dev) |
| `autoscaling.enabled` | Enable HPA | `false` |
| `livenessProbe.enabled` | Enable liveness probe | `true` |
| `readinessProbe.enabled` | Enable readiness probe | `true` |
| `namespace` | Deployment namespace | `todo-dev` |
| `existingSecret` | Name of existing secret | `todo-backend-secrets` |

### Environment Variables

The chart configures the following environment variables:

**From ConfigMap:**
- `FRONTEND_URL`: URL of the frontend service (default: `http://todo-frontend:3000`)

**From Secret:**
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `OPENAI_API_KEY`: OpenAI API key

## Resource Management

### Production Resources
- Requests: 250m CPU, 256Mi memory
- Limits: 500m CPU, 512Mi memory

### Development (Minikube) Resources
- Requests: 100m CPU, 128Mi memory
- Limits: 250m CPU, 256Mi memory

## Health Checks

### Liveness Probe
- Path: `/health`
- Initial Delay: 30s (prod), 15s (dev)
- Period: 10s
- Timeout: 5s
- Failure Threshold: 3

### Readiness Probe
- Path: `/health`
- Initial Delay: 15s (prod), 10s (dev)
- Period: 5s
- Timeout: 3s
- Failure Threshold: 3

## Autoscaling

Horizontal Pod Autoscaling is disabled by default. To enable:

```bash
helm upgrade todo-backend ./charts/todo-backend \
  --namespace todo-dev \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=5 \
  --set autoscaling.targetCPUUtilizationPercentage=80 \
  --reuse-values
```

## Deployment Strategy

The chart uses a RollingUpdate strategy:
- Max Surge: 1
- Max Unavailable: 0

This ensures zero-downtime deployments.

## Troubleshooting

### Pods Not Starting

Check pod status:
```bash
kubectl get pods -n todo-dev -l app.kubernetes.io/name=todo-backend
kubectl describe pod <pod-name> -n todo-dev
```

Common issues:
- Missing secret: Verify `todo-backend-secrets` exists
- Image pull errors: Check image name and pull policy
- Resource constraints: Verify node has sufficient resources

### Health Check Failures

Check logs for health endpoint errors:
```bash
kubectl logs -n todo-dev -l app.kubernetes.io/name=todo-backend
```

### Service Connection Issues

Verify service endpoints:
```bash
kubectl get endpoints -n todo-dev todo-backend
```

Test from another pod:
```bash
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n todo-dev -- \
  curl http://todo-backend:8000/health
```

## Values Files

- `values.yaml`: Production-ready defaults
- `values-dev.yaml`: Minikube development overrides

## Chart Information

- **Chart Version**: 1.0.0
- **App Version**: v1.0.0
- **API Version**: v2
- **Type**: application

## Support

For issues and questions:
1. Check application logs: `kubectl logs -n todo-dev -l app.kubernetes.io/name=todo-backend`
2. Verify secret configuration: `kubectl describe secret todo-backend-secrets -n todo-dev`
3. Review Helm release notes: `helm status todo-backend -n todo-dev`
