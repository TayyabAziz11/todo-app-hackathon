# Dapr Deployment Patterns and Production Best Practices

This guide covers deployment patterns for Dapr from local development through production-grade Kubernetes deployments.

## Table of Contents

1. [Local Development (Self-Hosted)](#local-development-self-hosted)
2. [Kubernetes Deployment](#kubernetes-deployment)
3. [Production Configuration](#production-configuration)
4. [High Availability](#high-availability)
5. [Security Hardening](#security-hardening)
6. [Observability](#observability)
7. [Resource Management](#resource-management)
8. [Best Practices](#best-practices)

---

## Local Development (Self-Hosted)

### Installation

```bash
# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr runtime
dapr init

# Verify installation
dapr --version
```

**What gets installed:**
- Dapr runtime binaries
- Redis container (state + pub/sub)
- Zipkin container (tracing)
- Placement service (actors)
- Default components in `~/.dapr/components/`

### Running Applications

**Basic:**
```bash
dapr run --app-id myapp --app-port 5000 -- python app.py
```

**With custom components:**
```bash
dapr run \
  --app-id myapp \
  --app-port 5000 \
  --components-path ./components \
  --config ./config.yaml \
  -- python app.py
```

**Multi-App (Run multiple services):**
```bash
# Terminal 1
dapr run --app-id service-a --app-port 5000 -- python service_a.py

# Terminal 2
dapr run --app-id service-b --app-port 5001 -- python service_b.py
```

**Using dapr.yaml (Multi-app file):**
```yaml
# dapr.yaml
version: 1
common:
  resourcesPath: ./components
apps:
  - appID: frontend
    appDirPath: ./frontend/
    appPort: 3000
    command: ["npm", "start"]
  - appID: backend
    appDirPath: ./backend/
    appPort: 5000
    command: ["python", "app.py"]
```

Run all apps:
```bash
dapr run -f dapr.yaml
```

### Dapr Dashboard

```bash
dapr dashboard
# Opens http://localhost:8080
```

---

## Kubernetes Deployment

### Installation Options

#### Option 1: Dapr CLI

**Development:**
```bash
dapr init -k --dev
```
Installs: Dapr control plane + Redis + Zipkin

**Production:**
```bash
dapr init -k --enable-ha=true
```
Installs: Dapr control plane with 3 replicas (HA mode)

#### Option 2: Helm (Recommended for Production)

```bash
# Add Dapr repo
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install (basic)
helm install dapr dapr/dapr \
  --version=1.15 \
  --namespace dapr-system \
  --create-namespace \
  --wait

# Install (production with HA + mTLS)
helm install dapr dapr/dapr \
  --version=1.15 \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=true \
  --set global.mtls.enabled=true \
  --set global.logAsJson=true \
  --set dapr_dashboard.enabled=true \
  --wait
```

### Verify Installation

```bash
dapr status -k
```

Expected output:
```
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE
dapr-sentry            dapr-system  True     Running  3         1.15.0   1m
dapr-operator          dapr-system  True     Running  3         1.15.0   1m
dapr-placement-server  dapr-system  True     Running  3         1.15.0   1m
dapr-sidecar-injector  dapr-system  True     Running  3         1.15.0   1m
```

### Deploying Applications

**Deployment with Dapr Annotations:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
      annotations:
        # Enable Dapr sidecar
        dapr.io/enabled: "true"

        # App configuration
        dapr.io/app-id: "myapp"
        dapr.io/app-port: "5000"
        dapr.io/app-protocol: "http"  # or "grpc"

        # Dapr configuration
        dapr.io/config: "appconfig"
        dapr.io/log-level: "info"
        dapr.io/enable-metrics: "true"
        dapr.io/metrics-port: "9090"

        # Resource limits (sidecar)
        dapr.io/sidecar-cpu-limit: "300m"
        dapr.io/sidecar-memory-limit: "512Mi"
        dapr.io/sidecar-cpu-request: "100m"
        dapr.io/sidecar-memory-request: "250Mi"

        # Security
        dapr.io/enable-api-logging: "true"

    spec:
      containers:
      - name: myapp
        image: myapp:1.0.0
        ports:
        - containerPort: 5000
        env:
        - name: DAPR_HTTP_PORT
          value: "3500"
        - name: DAPR_GRPC_PORT
          value: "50001"
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

**Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
```

### Component Deployment

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: production  # Namespace-scoped
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis-master.default.svc.cluster.local:6379
  - name: redisPassword
    secretKeyRef:
      name: redis-secret
      key: password
  - name: enableTLS
    value: "true"
```

Apply components:
```bash
kubectl apply -f components/ -n production
```

---

## Production Configuration

### Dapr Configuration Resource

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: appconfig
  namespace: production
spec:
  # Tracing
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: http://zipkin.observability:9411/api/v2/spans

  # Metrics
  metric:
    enabled: true

  # mTLS
  mtls:
    enabled: true
    workloadCertTTL: "24h"
    allowedClockSkew: "15m"

  # Access Control
  accessControl:
    defaultAction: deny
    trustDomain: "production"
    policies:
    - appId: frontend
      defaultAction: allow
      trustDomain: "production"
      operations:
      - name: /orders
        httpVerb: ['POST', 'GET']
        action: allow

  # API
  api:
    allowed:
    - name: state
      version: v1
      protocol: http
    - name: pubsub
      version: v1
      protocol: http

  # Secrets
  secrets:
    scopes:
    - storeName: kubernetes-secrets
      defaultAccess: allow
      allowedSecrets: ["redis-password", "db-connection"]
```

---

## High Availability

### Control Plane HA

**Helm Installation:**
```bash
helm install dapr dapr/dapr \
  --namespace dapr-system \
  --set global.ha.enabled=true \
  --set global.ha.replicaCount=3 \
  --set global.ha.disruption.minimumAvailable=2
```

**Components:**
- **dapr-operator**: 3 replicas (leader election)
- **dapr-placement**: 3 replicas (actor placement)
- **dapr-sentry**: 3 replicas (certificate authority)
- **dapr-sidecar-injector**: 3 replicas

### Application HA

```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0

  # Pod Disruption Budget
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: myapp
```

### Component HA (Redis Example)

```yaml
# Redis Sentinel for HA
spec:
  metadata:
  - name: redisHost
    value: redis-sentinel.default.svc.cluster.local:26379
  - name: redisPassword
    secretKeyRef:
      name: redis-secret
      key: password
  - name: sentinelMasterName
    value: mymaster
  - name: failover
    value: "true"
  - name: sentinelUsername
    value: ""
  - name: sentinelPassword
    secretKeyRef:
      name: redis-secret
      key: password
```

---

## Security Hardening

### 1. Enable mTLS (Mutual TLS)

**Automatic Certificate Rotation:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: appconfig
spec:
  mtls:
    enabled: true
    workloadCertTTL: "24h"
    allowedClockSkew: "15m"
```

All service-to-service communication is encrypted.

### 2. API Token Authentication

```bash
# Generate token
TOKEN=$(openssl rand -base64 32)

# Store as secret
kubectl create secret generic dapr-api-token \
  --from-literal=token=$TOKEN \
  -n production
```

**App annotation:**
```yaml
annotations:
  dapr.io/api-token-secret: "dapr-api-token"
```

### 3. Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: dapr-sidecar-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          dapr.io/enabled: "true"
    ports:
    - protocol: TCP
      port: 5000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: dapr-system
  - to:
    - podSelector:
        matchLabels:
          dapr.io/enabled: "true"
```

### 4. Secret Scope Restrictions

```yaml
spec:
  secrets:
    scopes:
    - storeName: kubernetes-secrets
      defaultAccess: deny
      allowedSecrets: ["db-password"]
      deniedSecrets: ["admin-token"]
```

### 5. Component Scopes

```yaml
spec:
  scopes:
  - payment-service
  - checkout-service
  # Only these apps can access this component
```

---

## Observability

### Metrics (Prometheus)

**Install Prometheus Operator:**
```bash
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml
```

**ServiceMonitor for Dapr:**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: dapr
  namespace: dapr-system
spec:
  selector:
    matchLabels:
      app: dapr-operator
  endpoints:
  - port: metrics
    interval: 15s
```

**Application Metrics:**
```yaml
annotations:
  dapr.io/enable-metrics: "true"
  dapr.io/metrics-port: "9090"
  prometheus.io/scrape: "true"
  prometheus.io/port: "9090"
  prometheus.io/path: "/metrics"
```

### Logging (Fluentd/Fluent Bit)

**JSON Logging:**
```bash
helm upgrade dapr dapr/dapr \
  --set global.logAsJson=true
```

**Log Levels:**
```yaml
annotations:
  dapr.io/log-level: "info"  # debug, info, warn, error
```

### Tracing (Jaeger/Zipkin)

**Jaeger Setup:**
```bash
kubectl create deployment jaeger --image=jaegertracing/all-in-one:latest
kubectl expose deployment jaeger --port=9411 --target-port=9411
```

**Configuration:**
```yaml
spec:
  tracing:
    samplingRate: "1"  # 100% sampling (reduce in prod)
    zipkin:
      endpointAddress: http://jaeger.observability:9411/api/v2/spans
```

**OTEL Collector (Recommended for Production):**
```yaml
spec:
  tracing:
    samplingRate: "0.1"  # 10% sampling
    otel:
      endpointAddress: otel-collector.observability:4318
      isSecure: true
      protocol: http
```

---

## Resource Management

### Sidecar Resource Limits

```yaml
annotations:
  # CPU
  dapr.io/sidecar-cpu-limit: "300m"
  dapr.io/sidecar-cpu-request: "100m"

  # Memory
  dapr.io/sidecar-memory-limit: "512Mi"
  dapr.io/sidecar-memory-request: "250Mi"
```

### Control Plane Resources (Helm)

```yaml
# values.yaml
dapr_operator:
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi

dapr_placement:
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi

dapr_sentry:
  resources:
    requests:
      cpu: 50m
      memory: 64Mi
    limits:
      cpu: 100m
      memory: 128Mi

dapr_sidecar_injector:
  resources:
    requests:
      cpu: 50m
      memory: 64Mi
    limits:
      cpu: 100m
      memory: 128Mi
```

Install with custom values:
```bash
helm install dapr dapr/dapr -f values.yaml
```

---

## Best Practices

### 1. Environment Separation

- **Dev**: Local Dapr init or K8s with `--dev` flag
- **Staging**: Kubernetes with basic HA (2 replicas)
- **Production**: Kubernetes with full HA (3 replicas) + mTLS

### 2. Component Organization

```
components/
├── base/
│   ├── statestore.yaml
│   └── pubsub.yaml
├── dev/
│   └── kustomization.yaml (patches for dev)
├── staging/
│   └── kustomization.yaml
└── production/
    └── kustomization.yaml (production secrets, HA configs)
```

### 3. Version Pinning

```yaml
# Pin Dapr version in deployment
annotations:
  dapr.io/sidecar-image: "daprio/daprd:1.15.0"
```

### 4. Graceful Shutdown

```yaml
# App must handle SIGTERM
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 15"]
```

Dapr sidecar waits 5 seconds before shutdown.

### 5. Health Checks

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 3500
  initialDelaySeconds: 5
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /healthz
    port: 3500
  initialDelaySeconds: 5
  periodSeconds: 5
```

### 6. Resource Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: production
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
```

### 7. Regular Updates

```bash
# Check for updates
helm search repo dapr/dapr --versions

# Upgrade
helm upgrade dapr dapr/dapr \
  --version=1.15.1 \
  --namespace dapr-system \
  --reuse-values
```

### 8. Monitoring Alerts

**Example Prometheus Alert:**
```yaml
groups:
- name: dapr
  rules:
  - alert: DaprSidecarDown
    expr: up{job="dapr-sidecar"} == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Dapr sidecar is down"
```

---

## Troubleshooting

### View Sidecar Logs

```bash
kubectl logs <pod-name> -c daprd
```

### Check Control Plane

```bash
dapr status -k
kubectl get pods -n dapr-system
```

### Debug Mode

```yaml
annotations:
  dapr.io/log-level: "debug"
  dapr.io/enable-debug: "true"
```

### Common Issues

1. **Sidecar not injecting**: Check namespace label `dapr.io/enabled=true`
2. **mTLS errors**: Verify cert expiry, clock sync
3. **Component not found**: Check component namespace and scopes
4. **High latency**: Review resource limits, enable metrics
