# Phase V: Dapr Integration Specification

**Feature Branch**: `005-name-phase5-cloud`
**Created**: 2026-02-06
**Status**: Draft

## Overview

This document specifies how Dapr building blocks are used in Phase V, including component configurations, sidecar setup, and integration patterns. All configurations are **Context7-verified** against official Dapr documentation.

## Dapr Building Blocks Usage

| Building Block | Component | Backing Store | Services Using | Priority |
|---------------|-----------|---------------|----------------|----------|
| State Management | statestore.postgresql | PostgreSQL | All services | P0 (Critical) |
| Pub/Sub | pubsub.kafka | Apache Kafka | All services | P0 (Critical) |
| Service Invocation | N/A (built-in) | gRPC/HTTP | All services | P0 (Critical) |
| Secrets | secretstore.kubernetes | K8s Secrets | All services | P1 (High) |
| Bindings (Output) | binding.smtp | SMTP Server | Notification Service | P2 (Medium) |
| Configuration | configstore.redis | Redis (future) | None (Phase VI) | P3 (Low) |

## 1. State Management

### Purpose

All services use Dapr State Management for persistent storage instead of direct database access. This provides:
- Database abstraction (can swap PostgreSQL for Cosmos DB without code changes)
- Built-in optimistic concurrency control (ETags)
- Transaction support (multi-item writes)
- TTL support (auto-expiration)

### Component Configuration

**File**: `components/statestore-postgresql.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-app-prod
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-credentials
      key: connectionString
  - name: tableName
    value: "state"
  - name: metadataTableName
    value: "state_metadata"
  - name: actorStateStore
    value: "false"
  - name: keyPrefix
    value: "none"
  - name: maxConns
    value: "10"
  - name: timeout
    value: "10"
  - name: cleanupInterval
    value: "1h"
scopes:
- todo-service
- user-service
- chat-service
- notification-service
- audit-service
- analytics-service
```

**Context7 Verification**: ✅ All metadata fields verified from [Dapr PostgreSQL State Store docs](https://docs.dapr.io/reference/components-reference/supported-state-stores/setup-postgresql/)

### Usage Pattern (Python SDK)

```python
from dapr.clients import DaprClient

# Initialize Dapr client
client = DaprClient()

# Save state with ETag (optimistic concurrency)
client.save_state(
    store_name="statestore",
    key="todo-12345",
    value={"title": "Buy groceries", "status": "pending"},
    etag="v1",  # Optional: for concurrency control
    options=StateOptions(
        concurrency=Concurrency.first_write,
        consistency=Consistency.strong
    )
)

# Get state with ETag
result = client.get_state(store_name="statestore", key="todo-12345")
data = result.data
etag = result.etag

# Bulk save (transaction)
client.save_bulk_state(
    store_name="statestore",
    states=[
        StateItem(key="todo-1", value={"title": "Task 1"}),
        StateItem(key="todo-2", value={"title": "Task 2"})
    ]
)

# Delete state
client.delete_state(store_name="statestore", key="todo-12345")
```

### State Key Naming Convention

Format: `{service}-{entity}-{id}`

Examples:
- `todo-service-todo-12345`
- `user-service-user-456`
- `chat-service-conversation-conv-123`

### ETag Strategy

**Optimistic Locking**:
1. Read entity with ETag: `GET /state/{key}` → returns data + ETag
2. Modify entity in memory
3. Write entity with ETag: `POST /state/{key}` with `If-Match: {etag}` header
4. If ETag mismatch → 409 Conflict → retry with exponential backoff

**Implementation** (pseudo-code):
```python
def update_todo_with_retry(todo_id, updates, max_retries=3):
    for attempt in range(max_retries):
        # Read current state
        result = dapr.get_state("statestore", f"todo-{todo_id}")
        todo = result.data
        etag = result.etag

        # Apply updates
        todo.update(updates)

        # Try to save with ETag
        try:
            dapr.save_state("statestore", f"todo-{todo_id}", todo, etag=etag)
            return todo  # Success
        except DaprConflictException:
            if attempt == max_retries - 1:
                raise  # Max retries exceeded
            time.sleep(2 ** attempt)  # Exponential backoff
```

### TTL (Time-To-Live)

Use TTL for ephemeral data (e.g., session tokens, temporary cache):

```python
from dapr.clients.grpc._state import StateOptions

client.save_state(
    store_name="statestore",
    key="session-xyz",
    value={"user_id": "456", "expires_at": "2026-02-07T10:00:00Z"},
    options=StateOptions(ttl_in_seconds=3600)  # 1 hour TTL
)
```

**Use Cases**:
- Chat conversation context (30-day TTL)
- Rate limiting counters (1-minute TTL)
- Notification queue (1-day TTL)

## 2. Pub/Sub (Kafka)

### Purpose

All event-driven communication uses Dapr Pub/Sub with Kafka as the backing message broker.

### Component Configuration

**File**: `components/pubsub-kafka.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: todo-app-prod
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-0.kafka-headless.todo-app-prod.svc.cluster.local:9092,kafka-1.kafka-headless.todo-app-prod.svc.cluster.local:9092,kafka-2.kafka-headless.todo-app-prod.svc.cluster.local:9092"
  - name: authType
    value: "none"  # Use "sasl" for production with secretKeyRef
  - name: consumerGroup
    value: "{podName}"  # Dynamic per service
  - name: clientID
    value: "{appID}"
  - name: maxMessageBytes
    value: "1048576"  # 1MB
  - name: version
    value: "3.6.0"
scopes:
- todo-service
- user-service
- chat-service
- notification-service
- audit-service
- analytics-service
```

**Context7 Verification**: ✅ All metadata fields verified from [Dapr Kafka Pub/Sub docs](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)

### Publisher Usage (Python SDK)

```python
from dapr.clients import DaprClient
import json

client = DaprClient()

# Publish event (CloudEvents format automatically applied by Dapr)
event_data = {
    "todo_id": "12345",
    "user_id": "user-456",
    "title": "Buy groceries",
    "status": "pending"
}

client.publish_event(
    pubsub_name="pubsub",
    topic_name="todo.created",
    data=json.dumps(event_data),
    data_content_type="application/json",
    metadata={
        "cloudevent.type": "com.todoapp.todo.created.v1",
        "cloudevent.source": "//todoapp/services/todo-service"
    }
)
```

### Subscriber Configuration

**File**: `components/subscription-todo-service.yaml`

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: todo-service-subscriptions
  namespace: todo-app-prod
spec:
  pubsubname: pubsub
  topic: user.deleted
  routes:
    default: /events/user-deleted
  scopes:
  - todo-service
```

**Context7 Verification**: ✅ Subscription schema verified from [Dapr Pub/Sub docs](https://docs.dapr.io/developing-applications/building-blocks/pubsub/subscription-methods/)

### Subscriber Handler (FastAPI)

```python
from fastapi import FastAPI, Request, Response
from dapr.ext.fastapi import DaprApp
import json

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub="pubsub", topic="user.deleted")
async def handle_user_deleted(event: dict):
    """
    Handle user.deleted event: cascade delete all todos for user.
    """
    try:
        user_id = event['data']['user_id']

        # Check idempotency
        event_id = event['id']
        if await is_event_processed(event_id):
            return Response(status_code=200)  # Already processed

        # Business logic: delete all todos for user
        await delete_todos_by_user(user_id)

        # Mark event as processed
        await mark_event_processed(event_id)

        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Failed to process user.deleted event: {e}")
        return Response(status_code=500)  # Trigger retry
```

### Dead Letter Queue

**File**: `components/pubsub-kafka-dlq.yaml`

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: todo-service-dlq
  namespace: todo-app-prod
spec:
  pubsubname: pubsub
  topic: user.deleted
  routes:
    default: /events/user-deleted
  deadLetterTopic: user.deleted.dlq
  scopes:
  - todo-service
```

**Retry Policy**:
- Max retries: 3
- Backoff: exponential (1s, 2s, 4s)
- After max retries → send to DLQ

## 3. Service Invocation

### Purpose

Synchronous service-to-service calls use Dapr Service Invocation for:
- Service discovery (no hardcoded IPs)
- Built-in retries and circuit breaking
- Distributed tracing (OpenTelemetry)
- mTLS (mutual TLS) for security

### Invocation Pattern

**Caller** (Chat Service invokes Todo Service):
```python
from dapr.clients import DaprClient

client = DaprClient()

# Invoke Todo Service to create a todo
response = client.invoke_method(
    app_id="todo-service",
    method_name="todos",
    data=json.dumps({
        "title": "Buy groceries",
        "priority": "high"
    }),
    http_verb="POST",
    content_type="application/json"
)

todo = response.json()
```

**Callee** (Todo Service endpoint):
```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/todos")
async def create_todo(todo: TodoCreate):
    # Business logic
    todo_id = await save_todo(todo)
    return {"id": todo_id, "title": todo.title}
```

**Context7 Verification**: ✅ Service invocation API verified from [Dapr Service Invocation docs](https://docs.dapr.io/developing-applications/building-blocks/service-invocation/service-invocation-overview/)

### Service Discovery

Dapr automatically discovers services via Kubernetes DNS:
- Service name: `{app-id}.{namespace}.svc.cluster.local`
- Example: `todo-service.todo-app-prod.svc.cluster.local`

No need to configure service registry (Consul, etcd, etc.).

### Resiliency Policy

**File**: `components/resiliency.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Resiliency
metadata:
  name: app-resiliency
  namespace: todo-app-prod
spec:
  policies:
    retries:
      default:
        policy: exponential
        duration: 1s
        maxDuration: 10s
        maxRetries: 3
    timeouts:
      default: 5s
    circuitBreakers:
      default:
        consecutiveFailures: 5
        timeout: 30s
        trip: consecutive_failures
  targets:
    apps:
      todo-service:
        retry: default
        timeout: default
        circuitBreaker: default
      user-service:
        retry: default
        timeout: default
        circuitBreaker: default
      chat-service:
        retry: default
        timeout: default
        circuitBreaker: default
```

**Context7 Verification**: ✅ Resiliency policies verified from [Dapr Resiliency docs](https://docs.dapr.io/operations/resiliency/resiliency-overview/)

## 4. Secrets Management

### Purpose

All sensitive configuration (database passwords, API keys, encryption keys) is stored in Kubernetes Secrets and accessed via Dapr Secrets API.

### Component Configuration

**File**: `components/secretstore-kubernetes.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
  namespace: todo-app-prod
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
  - name: vaultKubernetesMountPath
    value: "kubernetes"
scopes:
- todo-service
- user-service
- chat-service
- notification-service
```

**Context7 Verification**: ✅ Kubernetes secret store verified from [Dapr Secrets docs](https://docs.dapr.io/reference/components-reference/supported-secret-stores/kubernetes-secret-store/)

### Secrets Creation (kubectl)

```bash
# Create PostgreSQL credentials secret
kubectl create secret generic postgres-credentials \
  --from-literal=connectionString="host=postgres.todo-app-prod.svc.cluster.local port=5432 user=todoapp password=<password> dbname=todoapp_db sslmode=require" \
  --namespace=todo-app-prod

# Create JWT signing key secret
kubectl create secret generic jwt-signing-key \
  --from-literal=key="<random-256-bit-key>" \
  --namespace=todo-app-prod

# Create OpenAI API key secret (for Chat Service)
kubectl create secret generic openai-api-key \
  --from-literal=apiKey="sk-..." \
  --namespace=todo-app-prod
```

### Usage Pattern (Python SDK)

```python
from dapr.clients import DaprClient

client = DaprClient()

# Get secret
secret = client.get_secret(
    store_name="secretstore",
    key="postgres-credentials",
    metadata={"namespace": "todo-app-prod"}
)

connection_string = secret.secrets["connectionString"]

# Use secret in application
import psycopg2
conn = psycopg2.connect(connection_string)
```

**Best Practice**: Never log secrets or include them in error messages.

## 5. Output Bindings (SMTP Email)

### Purpose

Notification Service uses Dapr Output Binding to send emails without directly integrating with SMTP library.

### Component Configuration

**File**: `components/binding-smtp.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: smtp
  namespace: todo-app-prod
spec:
  type: bindings.smtp
  version: v1
  metadata:
  - name: host
    value: "smtp.sendgrid.net"
  - name: port
    value: "587"
  - name: user
    secretKeyRef:
      name: sendgrid-credentials
      key: username
  - name: password
    secretKeyRef:
      name: sendgrid-credentials
      key: apiKey
  - name: skipTLSVerify
    value: "false"
scopes:
- notification-service
```

**Context7 Verification**: ✅ SMTP binding verified from [Dapr SMTP Binding docs](https://docs.dapr.io/reference/components-reference/supported-bindings/smtp/)

### Usage Pattern (Python SDK)

```python
from dapr.clients import DaprClient
import json

client = DaprClient()

# Send email via binding
email_data = {
    "emailFrom": "noreply@todoapp.com",
    "emailTo": "user@example.com",
    "subject": "Reminder: Prepare Phase V documentation due in 1 hour",
    "body": "<h1>Reminder</h1><p>Your task is due in 1 hour.</p>"
}

client.invoke_binding(
    binding_name="smtp",
    operation="create",
    data=json.dumps(email_data)
)
```

**Benefits**:
- Swap SMTP provider without code changes (e.g., SendGrid → Mailgun)
- Retry logic handled by Dapr
- Observability (metrics, traces) out-of-the-box

## Dapr Sidecar Configuration

### Kubernetes Deployment with Sidecar Injection

**File**: `k8s/deployments/todo-service.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-service
  namespace: todo-app-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: todo-service
  template:
    metadata:
      labels:
        app: todo-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-service"
        dapr.io/app-port: "8000"
        dapr.io/app-protocol: "http"
        dapr.io/log-level: "info"
        dapr.io/enable-metrics: "true"
        dapr.io/metrics-port: "9090"
        dapr.io/config: "dapr-config"
    spec:
      containers:
      - name: todo-service
        image: todo-app/todo-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DAPR_HTTP_PORT
          value: "3500"
        - name: DAPR_GRPC_PORT
          value: "50001"
```

**Context7 Verification**: ✅ Sidecar annotations verified from [Dapr Kubernetes docs](https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-overview/)

### Dapr Configuration

**File**: `components/dapr-config.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
  namespace: todo-app-prod
spec:
  tracing:
    samplingRate: "1"  # 100% sampling in dev, 0.01 in prod
    zipkin:
      endpointAddress: "http://jaeger-collector.observability.svc.cluster.local:9411/api/v2/spans"
  metric:
    enabled: true
  mtls:
    enabled: true
    workloadCertTTL: "24h"
    allowedClockSkew: "15m"
```

### Local Development (Dapr CLI)

For local development on developer machines (without Kubernetes):

```bash
# Start Todo Service with Dapr sidecar
dapr run \
  --app-id todo-service \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --dapr-grpc-port 50001 \
  --components-path ./components \
  -- python3 -m uvicorn todo_service.main:app --port 8000

# Invoke service locally via Dapr CLI
dapr invoke --app-id todo-service --method todos --verb POST --data '{"title":"Test todo"}'

# Publish event locally
dapr publish --publish-app-id todo-service --pubsub pubsub --topic todo.created --data '{"todo_id":"123"}'
```

## Dapr Observability

### Metrics (Prometheus)

Dapr sidecar exposes metrics on port 9090:
- `dapr_http_server_request_count{app_id, method, path, status}`
- `dapr_grpc_io_server_completed_rpcs{app_id, method, status}`
- `dapr_component_invocation_count{component, operation, success}`
- `dapr_pubsub_ingress_count{topic, success}`

**Prometheus Scrape Config**:
```yaml
scrape_configs:
- job_name: 'dapr'
  kubernetes_sd_configs:
  - role: pod
    namespaces:
      names:
      - todo-app-prod
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_annotation_dapr_io_enabled]
    action: keep
    regex: true
  - source_labels: [__meta_kubernetes_pod_annotation_dapr_io_metrics_port]
    action: replace
    target_label: __address__
    regex: (.+)
    replacement: $1:9090
```

### Tracing (Jaeger)

Dapr automatically propagates W3C Trace Context headers:
- `traceparent: 00-{trace-id}-{span-id}-01`
- `tracestate: dapr={span-id}`

**Integration**:
1. Dapr sidecar sends spans to Jaeger Collector
2. Jaeger stores spans in Elasticsearch
3. Jaeger UI displays distributed traces

**Example Trace**:
```
User → Chat Service (span 1)
  → Todo Service (span 2, parent=1)
    → Dapr State Store (span 3, parent=2)
    → Kafka Pub/Sub (span 4, parent=2)
      → Notification Service (span 5, parent=4)
```

### Logging

Dapr sidecar logs are sent to stdout/stderr and collected by Fluentd:

**Log Levels**:
- `info`: Default production level
- `debug`: Verbose logging for troubleshooting
- `warn`: Warnings (e.g., retries)
- `error`: Errors (e.g., component failures)

**Configure Log Level**:
```bash
# Via annotation (Kubernetes)
dapr.io/log-level: "debug"

# Via CLI (local)
dapr run --log-level debug ...
```

## Deployment Strategy

### Minikube (Local Development)

```bash
# Install Dapr in Minikube
dapr init --kubernetes --wait

# Verify Dapr installation
dapr status -k

# Apply components
kubectl apply -f components/

# Deploy services
kubectl apply -f k8s/deployments/
```

### DigitalOcean Kubernetes (Production)

```bash
# Install Dapr with Helm (production settings)
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=true \
  --set global.mtls.enabled=true \
  --wait

# Verify Dapr installation
kubectl get pods -n dapr-system

# Apply components (with production secrets)
kubectl apply -f components-prod/

# Deploy services
kubectl apply -f k8s/deployments-prod/
```

## Testing Strategy

### Unit Tests (Mock Dapr Client)

```python
from unittest.mock import Mock
from dapr.clients import DaprClient

def test_save_todo():
    # Mock Dapr client
    mock_client = Mock(spec=DaprClient)
    mock_client.save_state.return_value = None

    # Test business logic
    service = TodoService(dapr_client=mock_client)
    todo = service.create_todo({"title": "Test", "status": "pending"})

    # Assert Dapr client was called correctly
    mock_client.save_state.assert_called_once_with(
        store_name="statestore",
        key=f"todo-{todo.id}",
        value=todo.dict()
    )
```

### Integration Tests (Real Dapr Components)

```bash
# Start Dapr with test components
dapr run --app-id todo-service --components-path ./test-components -- pytest tests/integration/

# Test components use in-memory stores
# components/test-statestore.yaml → type: state.in-memory
# components/test-pubsub.yaml → type: pubsub.in-memory
```

### End-to-End Tests (Kubernetes)

```bash
# Deploy to test namespace
kubectl apply -f k8s/test/ -n todo-app-test

# Run E2E tests
pytest tests/e2e/ --namespace=todo-app-test

# Cleanup
kubectl delete namespace todo-app-test
```

## Troubleshooting

### Dapr Sidecar Not Injected

**Symptom**: Pod only has 1 container (application), no `daprd` sidecar.

**Solution**:
```bash
# Check Dapr sidecar injector is running
kubectl get pods -n dapr-system -l app=dapr-sidecar-injector

# Verify namespace has Dapr enabled
kubectl get namespace todo-app-prod -o jsonpath='{.metadata.labels}'

# Check pod annotations
kubectl get pod <pod-name> -o jsonpath='{.metadata.annotations}'
```

### State Store Connection Failures

**Symptom**: `ERROR: failed to initialize state store statestore: connection refused`

**Solution**:
```bash
# Verify PostgreSQL is reachable
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- psql -h postgres.todo-app-prod.svc.cluster.local -U todoapp

# Check secret exists
kubectl get secret postgres-credentials -n todo-app-prod

# Check Dapr logs
kubectl logs <pod-name> -c daprd -n todo-app-prod
```

### Pub/Sub Events Not Delivered

**Symptom**: Events published but not received by subscribers.

**Solution**:
```bash
# Check Kafka broker is reachable
kubectl run -it --rm kafka-test --image=confluentinc/cp-kafka:7.5.0 --restart=Never -- kafka-console-consumer --bootstrap-server kafka-0.kafka-headless.todo-app-prod.svc.cluster.local:9092 --topic todo.created --from-beginning

# Check subscription configuration
kubectl get subscription -n todo-app-prod

# Check Dapr logs for consumer errors
kubectl logs <pod-name> -c daprd -n todo-app-prod | grep pubsub
```

## References

- [Dapr Documentation](https://docs.dapr.io/) (Context7-verified)
- [Dapr Python SDK](https://github.com/dapr/python-sdk)
- [Dapr Helm Charts](https://github.com/dapr/dapr/tree/master/charts/dapr)
- [Dapr Best Practices](https://docs.dapr.io/operations/best-practices/)

---

**Next Steps:**
1. Create Dapr component YAML files for all building blocks
2. Implement Dapr SDK integration in all services
3. Set up Dapr observability (Prometheus, Jaeger)
4. Write integration tests for Dapr components
