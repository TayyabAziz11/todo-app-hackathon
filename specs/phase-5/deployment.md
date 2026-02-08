# Phase V: Deployment Specification

**Feature Branch**: `005-name-phase5-cloud`
**Created**: 2026-02-06
**Status**: Draft

## Overview

This document specifies deployment procedures for Phase V across local development (Minikube) and cloud production (DigitalOcean Kubernetes) environments.

## Deployment Targets

| Environment | Platform | Purpose | Cost |
|------------|----------|---------|------|
| Local Dev | Minikube | Development, testing, debugging | $0 |
| Cloud Prod | DOKS | Production deployment, demo | ~$48-72/month |

## Prerequisites

### Local Development (Minikube)

```bash
# Required tools (Context7-verified versions)
minikube version  # v1.32.0+
kubectl version --client  # v1.28.0+
helm version  # v3.13.0+
dapr version  # v1.12.0+
docker version  # v24.0.0+

# Install if missing (see Context7-verified installation commands)
# minikube: https://minikube.sigs.k8s.io/docs/start/
# kubectl: https://kubernetes.io/docs/tasks/tools/
# helm: https://helm.sh/docs/intro/install/
# dapr: https://docs.dapr.io/getting-started/install-dapr-cli/
```

### Cloud Production (DOKS)

```bash
# Required tools
doctl version  # v1.104.0+ (Context7-verified)
kubectl version --client
helm version

# Authentication (Context7-verified command)
doctl auth init
doctl account get  # Verify authentication
```

## Infrastructure Setup

### Minikube Cluster

```bash
# Start Minikube with sufficient resources (Context7-verified)
minikube start \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --driver=docker \
  --kubernetes-version=v1.28.2

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

### DigitalOcean Kubernetes (DOKS)

**Using Budget-K8s Skill** (Context7-verified commands):

```bash
# Option 1: Using budget-k8s script
.claude/skills/budget-k8s/scripts/create-doks-cluster.sh \
  todo-app-cluster \
  nyc1 \
  s-2vcpu-4gb \
  3

# Option 2: Manual doctl command (Context7-verified)
doctl kubernetes cluster create todo-app-cluster \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 3 \
  --wait

# Save kubeconfig (Context7-verified)
doctl kubernetes cluster kubeconfig save todo-app-cluster

# Verify cluster
kubectl get nodes
```

**Cost Estimate**:
- 3 nodes × $24/month = $72/month
- Load Balancer: $12/month (if needed)
- **Total**: ~$84/month

## Application Deployment

### Step 1: Install Dapr Runtime

**Minikube**:
```bash
# Install Dapr (Context7-verified command)
dapr init --kubernetes --wait

# Verify Dapr installation
dapr status -k
kubectl get pods -n dapr-system
```

**DOKS (Production)**:
```bash
# Install Dapr with HA and mTLS (Context7-verified)
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=true \
  --set global.mtls.enabled=true \
  --set dapr_dashboard.enabled=true \
  --wait

# Verify installation
kubectl get pods -n dapr-system
kubectl get daprcomponents -n dapr-system
```

### Step 2: Deploy Infrastructure (Kafka, PostgreSQL)

**Minikube (Single-node, simplified)**:

```bash
# Create namespace
kubectl create namespace todo-app-dev

# Deploy PostgreSQL (single instance)
helm install postgresql bitnami/postgresql \
  --namespace todo-app-dev \
  --set auth.database=todoapp_db \
  --set auth.username=todoapp \
  --set auth.password=dev_password \
  --set primary.persistence.size=5Gi

# Deploy Kafka (KRaft mode, no Zookeeper)
helm install kafka bitnami/kafka \
  --namespace todo-app-dev \
  --set kraft.enabled=true \
  --set controller.replicaCount=1 \
  --set broker.replicaCount=1 \
  --set persistence.size=5Gi

# Wait for readiness
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql -n todo-app-dev --timeout=300s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka -n todo-app-dev --timeout=300s
```

**DOKS (Production with replication)**:

```bash
# Create namespace
kubectl create namespace todo-app-prod

# Deploy PostgreSQL (with replicas)
helm install postgresql bitnami/postgresql \
  --namespace todo-app-prod \
  --set auth.database=todoapp_db \
  --set auth.username=todoapp \
  --set auth.password=$(openssl rand -base64 32) \
  --set architecture=replication \
  --set replication.enabled=true \
  --set primary.persistence.size=20Gi \
  --set readReplicas.replicaCount=2

# Deploy Kafka (3 brokers, 2 replicas)
helm install kafka bitnami/kafka \
  --namespace todo-app-prod \
  --set kraft.enabled=true \
  --set controller.replicaCount=3 \
  --set broker.replicaCount=3 \
  --set replicaCount=3 \
  --set persistence.size=50Gi \
  --set persistence.storageClass=do-block-storage

# Wait for readiness
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql -n todo-app-prod --timeout=600s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka -n todo-app-prod --timeout=600s
```

### Step 3: Configure Secrets

**Minikube**:
```bash
# PostgreSQL connection string
kubectl create secret generic postgres-credentials \
  --from-literal=connectionString="host=postgresql.todo-app-dev.svc.cluster.local port=5432 user=todoapp password=dev_password dbname=todoapp_db sslmode=disable" \
  --namespace=todo-app-dev

# JWT signing key
kubectl create secret generic jwt-signing-key \
  --from-literal=key="dev-signing-key-$(openssl rand -hex 32)" \
  --namespace=todo-app-dev

# OpenAI API key (for Chat Service)
kubectl create secret generic openai-api-key \
  --from-literal=apiKey="${OPENAI_API_KEY}" \
  --namespace=todo-app-dev
```

**DOKS (Production)**:
```bash
# Use strong passwords in production
POSTGRES_PASSWORD=$(openssl rand -base64 32)
JWT_KEY=$(openssl rand -base64 64)

kubectl create secret generic postgres-credentials \
  --from-literal=connectionString="host=postgresql-primary.todo-app-prod.svc.cluster.local port=5432 user=todoapp password=${POSTGRES_PASSWORD} dbname=todoapp_db sslmode=require" \
  --namespace=todo-app-prod

kubectl create secret generic jwt-signing-key \
  --from-literal=key="${JWT_KEY}" \
  --namespace=todo-app-prod

kubectl create secret generic openai-api-key \
  --from-literal=apiKey="${OPENAI_API_KEY}" \
  --namespace=todo-app-prod
```

### Step 4: Deploy Dapr Components

```bash
# Apply Dapr components (state store, pub/sub, secrets)
kubectl apply -f k8s/dapr/components/ -n todo-app-dev  # or todo-app-prod

# Verify components
kubectl get daprcomponents -n todo-app-dev
```

**Expected Output**:
```
NAME          AGE
pubsub        10s
secretstore   10s
statestore    10s
```

### Step 5: Deploy Application Services

**Using Helm Chart**:

```bash
# Minikube deployment
helm install todo-app ./helm/todo-app \
  --namespace todo-app-dev \
  --values ./helm/todo-app/values-minikube.yaml \
  --wait

# DOKS deployment
helm install todo-app ./helm/todo-app \
  --namespace todo-app-prod \
  --values ./helm/todo-app/values-prod.yaml \
  --wait
```

**Or manually with kubectl**:

```bash
# Deploy all services
kubectl apply -f k8s/deployments/ -n todo-app-dev

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod --all -n todo-app-dev --timeout=600s

# Check deployment status
kubectl get pods -n todo-app-dev
```

**Expected Pods**:
```
NAME                                   READY   STATUS    RESTARTS
todo-service-7d4b6c8f9-abcde          2/2     Running   0
user-service-5f9c7b6d8-fghij          2/2     Running   0
chat-service-8c6d9e7f2-klmno          2/2     Running   0
notification-service-6b8a5d4c3-pqrst  2/2     Running   0
audit-service-9d7e6f5a4-uvwxy         2/2     Running   0
analytics-service-4c5b6a7d8-zabcd     2/2     Running   0
```

Note: Each pod has 2 containers (application + Dapr sidecar).

### Step 6: Configure Ingress

**Minikube**:
```bash
# Apply Ingress resource
kubectl apply -f k8s/ingress-minikube.yaml -n todo-app-dev

# Get Minikube IP
minikube ip

# Access application
curl http://$(minikube ip)/api/v1/health
```

**DOKS (with LoadBalancer)**:
```bash
# Apply Ingress resource (creates DigitalOcean Load Balancer)
kubectl apply -f k8s/ingress-prod.yaml -n todo-app-prod

# Wait for external IP
kubectl get ingress -n todo-app-prod --watch

# Access application
curl http://<EXTERNAL-IP>/api/v1/health
```

## Deployment Verification

### Health Check Script

```bash
#!/bin/bash
# verify-deployment.sh

NAMESPACE=${1:-todo-app-dev}

echo "🔍 Verifying deployment in namespace: $NAMESPACE"

# Check all pods are running
echo "Checking pods..."
kubectl get pods -n $NAMESPACE

# Check Dapr components
echo "Checking Dapr components..."
kubectl get daprcomponents -n $NAMESPACE

# Health checks for each service
SERVICES=("todo-service" "user-service" "chat-service" "notification-service" "audit-service" "analytics-service")

for service in "${SERVICES[@]}"; do
  echo "Checking $service health..."
  POD=$(kubectl get pod -l app=$service -n $NAMESPACE -o jsonpath='{.items[0].metadata.name}')
  kubectl exec -n $NAMESPACE $POD -c $service -- curl -s http://localhost:8000/health/ready || echo "❌ $service not ready"
done

echo "✅ Verification complete"
```

### Smoke Tests

```bash
# Create a test todo via API
kubectl run -it --rm curl --image=curlimages/curl --restart=Never -n todo-app-dev -- \
  curl -X POST http://todo-service:8000/api/v1/todos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -d '{"title":"Test todo","priority":"high"}'

# Expected: 201 Created with todo JSON

# Check Kafka topic has event
kubectl exec -it kafka-0 -n todo-app-dev -- \
  kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic todo.created \
  --from-beginning \
  --max-messages 1

# Expected: CloudEvents JSON for todo.created
```

## Rollback Procedures

### Helm Rollback

```bash
# List releases
helm list -n todo-app-prod

# Get release history
helm history todo-app -n todo-app-prod

# Rollback to previous version
helm rollback todo-app 1 -n todo-app-prod --wait

# Verify rollback
kubectl get pods -n todo-app-prod --watch
```

### Manual Rollback

```bash
# Rollback deployment to previous revision
kubectl rollout undo deployment/todo-service -n todo-app-prod

# Check rollout status
kubectl rollout status deployment/todo-service -n todo-app-prod
```

## Monitoring Setup

### Prometheus & Grafana

```bash
# Install Prometheus stack (Helm)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace observability \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --wait

# Port-forward Grafana
kubectl port-forward -n observability svc/prometheus-grafana 3000:80

# Access Grafana at http://localhost:3000
# Default credentials: admin/prom-operator
```

### Jaeger (Distributed Tracing)

```bash
# Install Jaeger Operator
kubectl create namespace observability
kubectl apply -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.51.0/jaeger-operator.yaml -n observability

# Deploy Jaeger instance
kubectl apply -f k8s/observability/jaeger.yaml -n observability

# Port-forward Jaeger UI
kubectl port-forward -n observability svc/jaeger-query 16686:16686

# Access Jaeger at http://localhost:16686
```

## CI/CD Pipeline (GitHub Actions)

**File**: `.github/workflows/deploy.yml`

```yaml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Build Docker images
      run: |
        docker build -t todo-app/todo-service:${{ github.sha }} services/todo-service
        docker build -t todo-app/user-service:${{ github.sha }} services/user-service
        # ... (build all services)

    - name: Push to Registry
      run: |
        echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
        docker push todo-app/todo-service:${{ github.sha }}
        # ... (push all images)

    - name: Deploy to DOKS
      uses: digitalocean/action-doctl@v2
      with:
        token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
    - run: |
        doctl kubernetes cluster kubeconfig save todo-app-cluster
        helm upgrade todo-app ./helm/todo-app \
          --namespace todo-app-prod \
          --set todoService.image.tag=${{ github.sha }} \
          --wait
```

## Teardown Procedures

### Minikube Cleanup

```bash
# Delete application
helm uninstall todo-app -n todo-app-dev
kubectl delete namespace todo-app-dev

# Delete Minikube cluster
minikube delete
```

### DOKS Cleanup (Stop Charges)

**Using Budget-K8s Skill**:

```bash
# Delete DOKS cluster (Context7-verified)
.claude/skills/budget-k8s/scripts/delete-doks-cluster.sh todo-app-cluster

# Or manual deletion
doctl kubernetes cluster delete todo-app-cluster --force
doctl kubernetes cluster kubeconfig remove todo-app-cluster

# Verify deletion
doctl kubernetes cluster list
```

**Cost Impact**: Charges stop immediately upon cluster deletion.

## Troubleshooting

### Pod CrashLoopBackOff

```bash
# Check pod logs
kubectl logs <pod-name> -c <container-name> -n todo-app-dev

# Describe pod for events
kubectl describe pod <pod-name> -n todo-app-dev

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd -n todo-app-dev
```

### Database Connection Errors

```bash
# Test PostgreSQL connectivity from pod
kubectl run -it --rm psql --image=postgres:15 --restart=Never -n todo-app-dev -- \
  psql -h postgresql.todo-app-dev.svc.cluster.local -U todoapp -d todoapp_db

# Check secret
kubectl get secret postgres-credentials -n todo-app-dev -o jsonpath='{.data.connectionString}' | base64 -d
```

### Kafka Not Receiving Events

```bash
# Check Kafka broker status
kubectl exec -it kafka-0 -n todo-app-dev -- kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# List topics
kubectl exec -it kafka-0 -n todo-app-dev -- kafka-topics.sh --list --bootstrap-server localhost:9092

# Consume from topic
kubectl exec -it kafka-0 -n todo-app-dev -- kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic todo.created --from-beginning
```

## References

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/) (Context7-verified)
- [DigitalOcean Kubernetes](https://docs.digitalocean.com/products/kubernetes/) (Context7-verified)
- [Dapr on Kubernetes](https://docs.dapr.io/operations/hosting/kubernetes/) (Context7-verified)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)

---

**Next Steps:**
1. Create Helm chart with values files for each environment
2. Write deployment verification scripts
3. Set up CI/CD pipeline with GitHub Actions
4. Document runbooks for common operational tasks
