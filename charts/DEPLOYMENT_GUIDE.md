# Todo App Kubernetes Deployment Guide

## Overview

This guide explains the normalized, production-grade Helm chart configuration for the Todo application with clear separation between deployment scenarios.

## Configuration Structure

### Backend Configuration Files

```
charts/todo-backend/
├── values.yaml          # Base configuration (production defaults)
├── values-dev.yaml      # In-cluster development (Minikube with service DNS)
└── values-local.yaml    # Local port-forward testing (localhost URLs)
```

### Frontend Configuration Files

```
charts/todo-frontend/
├── values.yaml          # Base configuration (localhost URLs baked in image)
├── values-dev.yaml      # Development resource limits
└── values-local.yaml    # Local port-forward testing (explicit localhost config)
```

## Deployment Scenarios

### Scenario 1: Local Port-Forward Testing (Recommended for Development)

**Use Case:** Testing the application from your local browser using kubectl port-forward

**Backend Configuration:**
- FRONTEND_URL: `http://localhost:3000`
- CORS_ORIGINS: `http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000`

**Frontend Configuration:**
- NEXT_PUBLIC_API_BASE_URL: `http://localhost:8000` (baked into image v1.0.2)
- NEXT_PUBLIC_CHAT_API_URL: `http://localhost:8000` (baked into image v1.0.2)

**Deployment:**

```bash
# Deploy backend
helm upgrade --install todo-backend charts/todo-backend \
  -f charts/todo-backend/values.yaml \
  -f charts/todo-backend/values-local.yaml \
  -n todo-dev

# Deploy frontend
helm upgrade --install todo-frontend charts/todo-frontend \
  -f charts/todo-frontend/values.yaml \
  -f charts/todo-frontend/values-local.yaml \
  -n todo-dev
```

**Access:**

```bash
# Terminal 1: Forward backend
kubectl port-forward -n todo-dev svc/todo-backend 8000:8000

# Terminal 2: Forward frontend
kubectl port-forward -n todo-dev svc/todo-frontend 3000:3000

# Browser: Open http://localhost:3000
```

### Scenario 2: In-Cluster Development (Minikube NodePort)

**Use Case:** Testing with Minikube's NodePort for external browser access

**Backend Configuration:**
- FRONTEND_URL: `http://todo-frontend:3000` (Kubernetes service DNS)
- CORS_ORIGINS: `http://todo-frontend:3000`

**Frontend Configuration:**
- Service Type: NodePort
- NodePort: 30080

**Deployment:**

```bash
# Deploy backend
helm upgrade --install todo-backend charts/todo-backend \
  -f charts/todo-backend/values.yaml \
  -f charts/todo-backend/values-dev.yaml \
  -n todo-dev

# Deploy frontend
helm upgrade --install todo-frontend charts/todo-frontend \
  -f charts/todo-frontend/values.yaml \
  -f charts/todo-frontend/values-dev.yaml \
  -n todo-dev
```

**Access:**

```bash
# Get Minikube IP and access via NodePort
minikube service todo-frontend -n todo-dev

# Or manually:
export MINIKUBE_IP=$(minikube ip)
echo "Access the frontend at: http://$MINIKUBE_IP:30080"
```

**Note:** In this scenario, the frontend image still has `localhost:8000` baked in. For true in-cluster communication, you would need to rebuild the frontend image with `http://todo-backend:8000` and use a different image tag.

## Configuration Details

### Backend ConfigMap (Non-Sensitive)

```yaml
configMap:
  FRONTEND_URL: "http://localhost:3000"      # CORS trusted origin
  CORS_ORIGINS: "http://localhost:3000,..."  # Allowed CORS origins
```

### Backend Secrets (Sensitive)

The backend requires a Kubernetes Secret named `todo-backend-secrets` with the following keys:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-backend-secrets
  namespace: todo-dev
type: Opaque
stringData:
  DATABASE_URL: "postgresql+psycopg://user:pass@host:5432/dbname"
  SECRET_KEY: "your-secret-key-here"
  OPENAI_API_KEY: "your-openai-api-key-here"
```

**Create the secret:**

```bash
kubectl create secret generic todo-backend-secrets \
  --namespace=todo-dev \
  --from-literal=DATABASE_URL='postgresql+psycopg://user:pass@host:5432/dbname' \
  --from-literal=SECRET_KEY='your-secret-key-here' \
  --from-literal=OPENAI_API_KEY='sk-...'
```

### Frontend ConfigMap (Build-Time Variables)

```yaml
configMap:
  NEXT_PUBLIC_API_BASE_URL: "http://localhost:8000"
  NEXT_PUBLIC_CHAT_API_URL: "http://localhost:8000"
  NEXT_PUBLIC_OPENAI_DOMAIN_KEY: "placeholder"
```

**IMPORTANT:** These are **build-time** environment variables for Next.js. They are baked into the JavaScript bundle during `docker build` and **cannot be changed at runtime**.

To change these values:
1. Rebuild the Docker image with new values:
   ```bash
   docker build \
     --build-arg NEXT_PUBLIC_API_BASE_URL=http://new-url:8000 \
     --build-arg NEXT_PUBLIC_CHAT_API_URL=http://new-url:8000 \
     -t todo-frontend:v1.0.3 \
     ./frontend
   ```
2. Update the image tag in `values.yaml`
3. Upgrade the Helm release

## Verification

### Check Pod Status

```bash
kubectl get pods -n todo-dev
```

Expected output:
```
NAME                             READY   STATUS    RESTARTS   AGE
todo-backend-xxx-yyy             1/1     Running   0          1m
todo-frontend-xxx-yyy            1/1     Running   0          1m
```

### Verify Environment Variables

**Backend:**
```bash
kubectl exec -n todo-dev deployment/todo-backend -- env | grep -E "FRONTEND_URL|CORS_ORIGINS"
```

Expected:
```
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000
```

**Frontend:**
```bash
kubectl exec -n todo-dev deployment/todo-frontend -- env | grep "NEXT_PUBLIC"
```

Expected:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_CHAT_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=placeholder
```

### Test Health Endpoints

**Backend:**
```bash
kubectl exec -n todo-dev deployment/todo-backend -- curl -s http://localhost:8000/health
```

Expected: `{"status":"ok","version":"3.0.0"}`

**Frontend Logs:**
```bash
kubectl logs -n todo-dev deployment/todo-frontend --tail=20
```

Expected: `✓ Ready in X.Xs`

## Troubleshooting

### CORS Errors in Browser

**Symptom:** Browser console shows CORS errors when accessing backend APIs

**Solution:** Ensure `CORS_ORIGINS` in backend ConfigMap includes the URL your browser uses to access the frontend.

For port-forward: `http://localhost:3000`
For NodePort: `http://<minikube-ip>:30080`

### Frontend Can't Connect to Backend

**Symptom:** API calls fail, network errors in browser console

**Cause:** Frontend NEXT_PUBLIC_API_BASE_URL doesn't match how you're accessing the backend

**Solution:**
- If using port-forward to backend on 8000 → URLs should be `http://localhost:8000`
- If using NodePort → Rebuild frontend image with Minikube IP

### Pods in CrashLoopBackOff

**Backend:**
Check secret exists:
```bash
kubectl get secret todo-backend-secrets -n todo-dev
```

Check logs:
```bash
kubectl logs -n todo-dev deployment/todo-backend
```

**Frontend:**
Check logs:
```bash
kubectl logs -n todo-dev deployment/todo-frontend
```

### Configuration Not Taking Effect

**Issue:** Changed ConfigMap values but pods still have old values

**Solution:** Restart the deployment:
```bash
kubectl rollout restart deployment/todo-backend -n todo-dev
kubectl rollout restart deployment/todo-frontend -n todo-dev
```

## Best Practices

1. **Never commit secrets to version control** - Always use Kubernetes Secrets or external secret managers

2. **Use values layering** - Combine base values.yaml with environment-specific overrides:
   ```bash
   helm upgrade --install myapp charts/myapp \
     -f charts/myapp/values.yaml \
     -f charts/myapp/values-dev.yaml
   ```

3. **Frontend build-time variables** - Remember that NEXT_PUBLIC_* vars require image rebuild to change

4. **CORS configuration** - Always include all URLs from which browsers will access your app

5. **Port-forward for development** - Easier and more reliable than NodePort for local testing

6. **Verify before production** - Always check environment variables in running pods match your expectations

## Files Reference

### Modified Files (Phase IV Refactoring)

- `charts/todo-backend/values.yaml` - Added CORS_ORIGINS to ConfigMap
- `charts/todo-backend/values-dev.yaml` - Updated for in-cluster service DNS
- `charts/todo-backend/values-local.yaml` - **NEW** - Port-forward configuration
- `charts/todo-backend/templates/configmap.yaml` - Added CORS_ORIGINS field
- `charts/todo-backend/templates/deployment.yaml` - Added CORS_ORIGINS env injection
- `charts/todo-frontend/values-local.yaml` - **NEW** - Port-forward configuration with build-time notes

### Current Image Versions

- Backend: `todo-backend:v1.0.0`
- Frontend: `todo-frontend:v1.0.2` (built with localhost:8000 URLs)

## Summary

This setup provides a clean, production-grade Kubernetes deployment configuration with:

✅ Clear separation between deployment scenarios (port-forward vs in-cluster)
✅ Proper ConfigMap usage for non-sensitive configuration
✅ Proper Secret usage for sensitive data (DATABASE_URL, SECRET_KEY, OPENAI_API_KEY)
✅ No hardcoded values in templates
✅ Comprehensive documentation for Next.js build-time vs runtime behavior
✅ CORS configuration that works for both scenarios
✅ Easy-to-use values file layering for environment-specific overrides

**Current deployment status:** Port-forward testing configuration (values-local.yaml) applied and verified working.
