# Dapr Kafka Integration

> **Source**: Dapr Official Documentation (docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)

## Table of Contents
- [Component Configuration](#component-configuration)
- [Metadata Fields Reference](#metadata-fields-reference)
- [Authentication Methods](#authentication-methods)
- [Consumer Group Behavior](#consumer-group-behavior)
- [Topic Subscription](#topic-subscription)
- [Error Handling and Retries](#error-handling-and-retries)
- [Delivery Semantics](#delivery-semantics)
- [Environment-Specific Configuration](#environment-specific-configuration)

## Component Configuration

Dapr abstracts Kafka access via the `pubsub.kafka` component. All Kafka interaction happens through Dapr APIs.

**Basic component YAML**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka-kafka-bootstrap.kafka:9092"
    - name: consumerGroup
      value: "{appId}"
    - name: authType
      value: "none"
```

**Kubernetes deployment pattern**:
```yaml
# Component in same namespace as Kafka
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default  # Or your app namespace
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka-kafka-bootstrap.kafka:9092"  # Strimzi default service name
    - name: consumerGroup
      value: "{appId}"  # Templated - becomes app-id at runtime
    - name: clientID
      value: "{appId}"
    - name: version
      value: "3.6.0"  # Match your Kafka cluster version
```

## Metadata Fields Reference

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `brokers` | **Yes** | - | Comma-separated list of Kafka brokers (host:port) |
| `consumerGroup` | No | `{appId}` | Consumer group name; supports `{namespace}`, `{podName}` templates |
| `consumerID` | No | Random UUID | Consumer identifier within the group |
| `clientID` | No | `{consumerID}` | Client identifier for Kafka connection |
| `authType` | **Yes** | - | Authentication: `none`, `password`, `mtls`, `oidc`, `awsiam` |
| `version` | No | `2.0.0` | Kafka cluster version (e.g., `3.6.0`) |
| `consumeRetryEnabled` | No | `true` | Enable retry on consume failures |
| `consumeRetryInterval` | No | `100ms` | Interval between consume retries |
| `heartbeatInterval` | No | `3s` | Consumer heartbeat interval (max 1/3 of sessionTimeout) |
| `sessionTimeout` | No | `10s` | Timeout to detect consumer failures |
| `maxMessageBytes` | No | `1024` | Maximum message size in bytes |
| `initialOffset` | No | `newest` | Where new consumers start: `newest` or `oldest` |
| `escapeHeaders` | No | `false` | Escape special characters in headers |
| `caCert` | Conditional | - | CA certificate for TLS (required for mTLS) |
| `clientCert` | Conditional | - | Client certificate for mTLS |
| `clientKey` | Conditional | - | Client private key for mTLS |
| `saslUsername` | Conditional | - | Username for SASL/PLAIN or SASL/SCRAM |
| `saslPassword` | Conditional | - | Password (use secretKeyRef in production) |

**Template variables**:
- `{appId}`: Replaced with Dapr application ID
- `{namespace}`: Replaced with Kubernetes namespace
- `{podName}`: Replaced with pod name

## Authentication Methods

### 1. No Authentication (Development)
```yaml
metadata:
  - name: authType
    value: "none"
```

### 2. SASL/PLAIN with Password (Common for Cloud)
```yaml
metadata:
  - name: authType
    value: "password"
  - name: saslUsername
    value: "kafka-user"
  - name: saslPassword
    secretKeyRef:
      name: kafka-secrets
      key: password
```

**Kubernetes Secret**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: kafka-secrets
  namespace: default
type: Opaque
stringData:
  password: "your-password-here"
```

### 3. mTLS (Production Strimzi)
```yaml
metadata:
  - name: authType
    value: "mtls"
  - name: caCert
    secretKeyRef:
      name: kafka-cluster-ca-cert
      key: ca.crt
  - name: clientCert
    secretKeyRef:
      name: kafka-user-cert
      key: user.crt
  - name: clientKey
    secretKeyRef:
      name: kafka-user-cert
      key: user.key
```

**Strimzi auto-generates** these secrets when you create a `KafkaUser` resource.

## Consumer Group Behavior

**Consumer group naming**:
- Dapr uses `consumerGroup` metadata to organize consumers
- Default: `{appId}` (each app gets its own group)
- Custom: Specify a fixed group name for shared consumption

**Load balancing within a group**:
```
Topic: task-events (3 partitions)
Consumer Group: recurring-task-service
Replicas: 3 pods

Dapr assigns:
Pod 1 → Partition 0
Pod 2 → Partition 1
Pod 3 → Partition 2
```

**Multiple consumer groups (broadcast pattern)**:
```yaml
# Recurring task service
---
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  metadata:
    - name: consumerGroup
      value: "recurring-task-service"

# Audit service (receives same events)
---
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  metadata:
    - name: consumerGroup
      value: "audit-service"
```

Each service receives **all** events independently.

## Topic Subscription

**Application subscription** (in app code or declarative YAML):

**Declarative subscription YAML**:
```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-sub
  namespace: default
spec:
  pubsubname: kafka-pubsub
  topic: task-events
  routes:
    default: /task-events
  scopes:
    - recurring-task-service
```

**Application receives POST** to `/task-events` with:
```json
{
  "id": "event-uuid",
  "source": "todo-backend",
  "type": "task.completed",
  "data": {
    "task_id": "task-456",
    "user_id": "user-123"
  },
  "datacontenttype": "application/json",
  "pubsubname": "kafka-pubsub",
  "topic": "task-events"
}
```

**Application responds**:
```json
{
  "status": "SUCCESS"  // or "RETRY" or "DROP"
}
```

## Error Handling and Retries

**Consume retry configuration**:
```yaml
metadata:
  - name: consumeRetryEnabled
    value: "true"
  - name: consumeRetryInterval
    value: "100ms"  # Retry every 100ms on transient errors
```

**Application-level retry**:
- App returns `{"status": "RETRY"}` → Dapr redelivers message
- App returns `{"status": "DROP"}` → Message is skipped (offset committed)
- App returns `{"status": "SUCCESS"}` → Message processed (offset committed)

**Session timeout and heartbeats**:
```yaml
metadata:
  - name: sessionTimeout
    value: "30s"  # Consumer marked dead after 30s without heartbeat
  - name: heartbeatInterval
    value: "10s"  # Must be < sessionTimeout / 3
```

**Rebalancing on failure**:
- If consumer pod crashes, Kafka rebalances partitions to other consumers
- New consumer starts from **last committed offset** (no message loss if using manual commit)

## Delivery Semantics

**At-least-once delivery** (Dapr default):
- Dapr commits offset **after app returns SUCCESS**
- If app crashes before responding, message is redelivered
- Application must be **idempotent**

**Idempotency pattern**:
```python
# Store processed event IDs to detect duplicates
processed_events = set()

@app.post("/task-events")
async def handle_event(event: CloudEvent):
    event_id = event.id

    if event_id in processed_events:
        return {"status": "SUCCESS"}  # Already processed

    # Process event
    process_task_event(event.data)

    # Store event ID
    processed_events.add(event_id)

    return {"status": "SUCCESS"}
```

**Production pattern**: Use database/cache to track processed event IDs across pod restarts.

## Environment-Specific Configuration

**Local development (Minikube + Strimzi)**:
```yaml
metadata:
  - name: brokers
    value: "kafka-kafka-bootstrap.kafka:9092"
  - name: authType
    value: "none"
```

**Production (Managed Kafka with SASL)**:
```yaml
metadata:
  - name: brokers
    value: "kafka-broker-1.cloud.redpanda.com:9092"
  - name: authType
    value: "password"
  - name: saslUsername
    value: "prod-user"
  - name: saslPassword
    secretKeyRef:
      name: kafka-prod-secrets
      key: password
  - name: version
    value: "3.6.0"
```

**Multi-environment templating**:
```yaml
# Use Kustomize overlays or Helm values
metadata:
  - name: brokers
    value: {{ .Values.kafka.brokers }}
  - name: authType
    value: {{ .Values.kafka.authType }}
```

## Best Practices for Event-Driven Systems

1. **Consumer group per service**: Each microservice should have its own consumer group
2. **Idempotent processing**: Always handle duplicate messages gracefully
3. **Manual offset commit**: Commit only after successful processing
4. **Topic per domain**: Separate topics for different business domains (task-events, user-events)
5. **Event versioning**: Include schema version in event headers
6. **Monitoring**: Track consumer lag via Dapr metrics

**Dapr simplifies**:
- No direct Kafka client libraries needed
- Automatic offset management
- Retry policies without custom code
- Environment portability (swap Kafka for RabbitMQ with config change)
