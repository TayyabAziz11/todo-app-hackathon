# Todo Frontend Helm Chart

Production-ready Helm chart for the Todo Frontend Next.js application with NodePort access for Minikube.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- Minikube (for local development)
- kubectl configured to communicate with your cluster
- Todo Backend service deployed and accessible

## Installation

### Standard Installation

Install the chart with default values:

```bash
helm install todo-frontend ./charts/todo-frontend --namespace todo-dev
```

### Minikube Development Installation

Install with development-specific resource limits and NodePort access:

```bash
helm install todo-frontend ./charts/todo-frontend \
  -f charts/todo-frontend/values.yaml \
  -f charts/todo-frontend/values-dev.yaml \
  --namespace todo-dev
```

### Custom Installation

Override specific values:

```bash
helm install todo-frontend ./charts/todo-frontend \
  --namespace todo-dev \
  --set replicaCount=2 \
  --set image.tag=v1.0.1 \
  --set service.nodePort=30081
```

### Installation from Custom Values File

Create your own values file:

```bash
helm install todo-frontend ./charts/todo-frontend \
  -f charts/todo-frontend/values.yaml \
  -f my-custom-values.yaml \
  --namespace todo-dev
```

## Accessing the Application

### Minikube NodePort Access

The frontend is exposed via NodePort for browser access on Minikube.

**Method 1: Using Minikube Service Command (Recommended)**

```bash
minikube service todo-frontend -n todo-dev
```

This automatically opens the application in your default browser.

**Method 2: Manual Access**

Get the Minikube IP and access the NodePort directly:

```bash
export MINIKUBE_IP=$(minikube ip)
echo "Access the frontend at: http://$MINIKUBE_IP:30080"
```

Then open your browser to: `http://<MINIKUBE_IP>:30080`

**Method 3: Port Forwarding (Alternative)**

```bash
kubectl port-forward -n todo-dev svc/todo-frontend 3000:3000
```

Then access: `http://localhost:3000`

## Upgrading

### Upgrade with New Image Version

```bash
helm upgrade todo-frontend ./charts/todo-frontend \
  --namespace todo-dev \
  --set image.tag=v1.0.1 \
  --reuse-values
```

### Upgrade with New Values File

```bash
helm upgrade todo-frontend ./charts/todo-frontend \
  -f charts/todo-frontend/values-dev.yaml \
  --namespace todo-dev
```

### Force Rollout (Restart Pods)

```bash
helm upgrade todo-frontend ./charts/todo-frontend \
  --namespace todo-dev \
  --set podAnnotations."kubectl\.kubernetes\.io/restartedAt"="$(date +%Y%m%d%H%M%S)" \
  --reuse-values
```

## Rollback

### View Release History

```bash
helm history todo-frontend --namespace todo-dev
```

### Rollback to Previous Version

```bash
helm rollback todo-frontend --namespace todo-dev
```

### Rollback to Specific Revision

```bash
helm rollback todo-frontend 2 --namespace todo-dev
```

## Uninstallation

Remove the chart and all associated resources:

```bash
helm uninstall todo-frontend --namespace todo-dev
```

## Verification

### Check Deployment Status

```bash
kubectl get deployments -n todo-dev
kubectl get pods -n todo-dev -l app.kubernetes.io/name=todo-frontend
kubectl get svc -n todo-dev -l app.kubernetes.io/name=todo-frontend
```

### View Helm Release Information

```bash
helm status todo-frontend --namespace todo-dev
helm get values todo-frontend --namespace todo-dev
helm get manifest todo-frontend --namespace todo-dev
```

### Check Application Logs

```bash
kubectl logs -n todo-dev -l app.kubernetes.io/name=todo-frontend -f
```

### Test Application Endpoint

Using port-forward:

```bash
kubectl port-forward -n todo-dev svc/todo-frontend 3000:3000
```

Then access: `http://localhost:3000`

Or using NodePort:

```bash
minikube service todo-frontend -n todo-dev --url
```

## Configuration

### Key Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `todo-frontend` |
| `image.tag` | Image tag | `v1.0.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `NodePort` |
| `service.port` | Service port | `3000` |
| `service.nodePort` | NodePort for external access | `30080` |
| `resources.requests.memory` | Memory request | `128Mi` (prod), `64Mi` (dev) |
| `resources.requests.cpu` | CPU request | `100m` (prod), `50m` (dev) |
| `resources.limits.memory` | Memory limit | `256Mi` (prod), `128Mi` (dev) |
| `resources.limits.cpu` | CPU limit | `250m` (prod), `150m` (dev) |
| `autoscaling.enabled` | Enable HPA | `false` |
| `livenessProbe.enabled` | Enable liveness probe | `true` |
| `readinessProbe.enabled` | Enable readiness probe | `true` |
| `namespace` | Deployment namespace | `todo-dev` |

### Environment Variables (Build-Time)

The chart configures the following build-time environment variables:

**From ConfigMap:**
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: `http://todo-backend:8000`)
- `NEXT_PUBLIC_CHAT_API_URL`: Backend Chat API URL (default: `http://todo-backend:8000/api`)
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`: OpenAI domain key placeholder (default: `placeholder`)

**Important Note:** These are Next.js build-time variables prefixed with `NEXT_PUBLIC_`. They are baked into the Docker image during the build process and cannot be changed at runtime. To update these values:

1. Rebuild the Docker image with new environment variables
2. Update the image tag in values.yaml
3. Upgrade the Helm release with the new image

## Resource Management

### Production Resources
- Requests: 100m CPU, 128Mi memory
- Limits: 250m CPU, 256Mi memory

### Development (Minikube) Resources
- Requests: 50m CPU, 64Mi memory
- Limits: 150m CPU, 128Mi memory

## Health Checks

### Liveness Probe
- Path: `/`
- Initial Delay: 30s (prod), 15s (dev)
- Period: 10s
- Timeout: 5s
- Failure Threshold: 3

### Readiness Probe
- Path: `/`
- Initial Delay: 15s (prod), 10s (dev)
- Period: 5s
- Timeout: 3s
- Failure Threshold: 3

## Deployment Strategy

The chart uses a RollingUpdate strategy:
- Max Surge: 1
- Max Unavailable: 0

This ensures zero-downtime deployments.

## Backend Communication

The frontend communicates with the backend service using Kubernetes DNS:

- **Backend Service Name**: `todo-backend`
- **Backend Namespace**: `todo-dev`
- **Backend Port**: `8000`
- **API URL**: `http://todo-backend:8000`
- **Chat API URL**: `http://todo-backend:8000/api`

Ensure the backend service is deployed before deploying the frontend.

## NodePort Configuration

### Default NodePort
- **Port**: 30080

### Custom NodePort

To use a different NodePort (must be in range 30000-32767):

```bash
helm upgrade todo-frontend ./charts/todo-frontend \
  --namespace todo-dev \
  --set service.nodePort=30081 \
  --reuse-values
```

### NodePort Limitations

- NodePort range is typically 30000-32767
- Only one service can use a specific NodePort
- Not recommended for production (use Ingress or LoadBalancer instead)

## Troubleshooting

### Pods Not Starting

Check pod status:
```bash
kubectl get pods -n todo-dev -l app.kubernetes.io/name=todo-frontend
kubectl describe pod <pod-name> -n todo-dev
```

Common issues:
- Image pull errors: Check image name and pull policy
- Resource constraints: Verify node has sufficient resources
- Backend not available: Ensure todo-backend service is running

### Health Check Failures

Check logs for startup errors:
```bash
kubectl logs -n todo-dev -l app.kubernetes.io/name=todo-frontend
```

### Cannot Access via NodePort

1. Verify Minikube is running:
   ```bash
   minikube status
   ```

2. Check service NodePort:
   ```bash
   kubectl get svc todo-frontend -n todo-dev
   ```

3. Get Minikube IP:
   ```bash
   minikube ip
   ```

4. Verify NodePort is open:
   ```bash
   minikube service list -n todo-dev
   ```

5. Test with curl:
   ```bash
   curl http://$(minikube ip):30080
   ```

### Backend Connection Issues

If the frontend cannot connect to the backend:

1. Verify backend service is running:
   ```bash
   kubectl get svc todo-backend -n todo-dev
   ```

2. Test backend connectivity from a debug pod:
   ```bash
   kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n todo-dev -- \
     curl http://todo-backend:8000/health
   ```

3. Check backend logs:
   ```bash
   kubectl logs -n todo-dev -l app.kubernetes.io/name=todo-backend
   ```

### Build-Time Environment Variables

Remember that `NEXT_PUBLIC_*` variables are build-time only. If you need to change these:

1. Update the Dockerfile or build command with new environment variables
2. Rebuild the Docker image:
   ```bash
   docker build -t todo-frontend:v1.0.1 \
     --build-arg NEXT_PUBLIC_API_URL=http://new-backend:8000 \
     -f frontend/Dockerfile frontend/
   ```
3. Update the image tag in values.yaml
4. Upgrade the Helm release

## Values Files

- `values.yaml`: Production-ready defaults with NodePort service
- `values-dev.yaml`: Minikube development overrides with reduced resources

## Chart Information

- **Chart Version**: 1.0.0
- **App Version**: v1.0.0
- **API Version**: v2
- **Type**: application

## Support

For issues and questions:
1. Check application logs: `kubectl logs -n todo-dev -l app.kubernetes.io/name=todo-frontend`
2. Verify backend connectivity: Test from a debug pod
3. Review Helm release notes: `helm status todo-frontend -n todo-dev`
4. Check Minikube service: `minikube service list -n todo-dev`
