---
name: apache-kafka
description: Build event-driven architectures with Apache Kafka on Kubernetes using Dapr Pub/Sub. Use when designing or implementing event-driven microservices, domain event publishing/consuming, Kafka cluster deployment with Strimzi, topic configuration, consumer groups, idempotent processing, or integrating Kafka with Dapr for production-ready event-driven systems on Kubernetes. Covers hello-world to production-grade deployments.
---

# Apache Kafka Event-Driven Architecture

Build production-ready event-driven microservices with Apache Kafka on Kubernetes.

## Core Workflow

**Event-driven architecture workflow**:
1. **Design domain events** → Define business events and topics
2. **Deploy Kafka cluster** → Use Strimzi on Kubernetes
3. **Create topics** → Define partitioning and retention
4. **Configure Dapr** → Set up Pub/Sub components
5. **Implement producers** → Publish events from services
6. **Implement consumers** → Subscribe and process events idempotently
7. **Monitor and scale** → Track consumer lag, tune performance

## Quick Reference

**Kafka cluster deployment** (Strimzi):
```bash
scripts/deploy_strimzi_kafka.sh [namespace] [cluster-name] [replicas]
# Example: scripts/deploy_strimzi_kafka.sh kafka kafka-cluster 1
```

**Create event topics**:
```bash
scripts/create_topics.sh [namespace] [cluster-name]
# Creates: task-events, task-reminders, task-audit, task-updates
```

**Dapr component configuration**:
- Copy `assets/dapr-kafka-component.yaml` and customize
- Apply: `kubectl apply -f dapr-kafka-component.yaml`

**Producer code** (publish events):
- See `assets/producer-example.py` for CloudEvents-compliant publishing

**Consumer code** (subscribe to events):
- See `assets/consumer-example.py` for idempotent event processing

## When to Use This Skill

Trigger this skill when working on:

**Event-Driven Design**:
- Designing domain events for microservices
- Defining event schemas and versioning strategy
- Choosing between event-driven vs request-response patterns

**Kafka Infrastructure**:
- Deploying Kafka clusters on Kubernetes with Strimzi
- Configuring topics, partitions, and replication
- Setting up authentication and authorization

**Dapr Integration**:
- Configuring Dapr Pub/Sub components for Kafka
- Subscribing services to topics declaratively
- Managing consumer groups and partition assignment

**Event Processing**:
- Publishing events from backend services
- Implementing idempotent consumers
- Handling event ordering and partitioning
- Retry strategies and dead letter queues

**Production Concerns**:
- Scaling Kafka brokers and consumers
- Monitoring consumer lag and throughput
- Ensuring at-least-once delivery semantics
- Schema evolution and backward compatibility

## Reference Documentation

Consult these references as needed:

### kafka-core-concepts.md
**Read when**: Learning Kafka fundamentals or designing event architecture.

**Contains**:
- Events, topics, partitions, offsets
- Producers and consumers
- Consumer groups and partition assignment
- Replication and durability guarantees
- Brokers and KRaft mode

### dapr-kafka-integration.md
**Read when**: Configuring Dapr components or implementing publishers/subscribers.

**Contains**:
- Dapr component YAML specification
- Metadata fields reference (brokers, consumerGroup, auth, retries)
- Authentication methods (none, SASL, mTLS)
- Topic subscription patterns
- Delivery semantics and offset management

### strimzi-kubernetes.md
**Read when**: Deploying or managing Kafka clusters on Kubernetes.

**Contains**:
- Strimzi operator architecture
- Installation methods (YAML, Helm, OLM)
- Kafka cluster CRD configuration
- Topic and user management with CRDs
- Production best practices (resources, storage, replication)

### event-driven-patterns.md
**Read when**: Implementing event-driven services or designing event schemas.

**Contains**:
- Event design principles (CloudEvents, naming conventions)
- Domain event patterns (lifecycle events, event sourcing, real-time sync)
- Idempotency strategies (deduplication, database constraints)
- Schema evolution approaches
- Error handling patterns (retry, DLQ, circuit breaker)
- Observability (metrics, tracing, logging)

## Deployment Patterns

### Local Development (Minikube)

**1. Deploy single-broker Kafka**:
```bash
scripts/deploy_strimzi_kafka.sh kafka kafka-cluster 1
```

**2. Create topics**:
```bash
scripts/create_topics.sh kafka kafka-cluster
```

**3. Configure Dapr (no auth)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka-cluster-kafka-bootstrap.kafka:9092"
    - name: consumerGroup
      value: "{appId}"
    - name: authType
      value: "none"
```

### Production (Kubernetes)

**1. Deploy 3-broker cluster with persistence**:
```bash
scripts/deploy_strimzi_kafka.sh kafka kafka-cluster 3
```

**2. Create KafkaUser with mTLS**:
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaUser
metadata:
  name: recurring-task-service
  namespace: kafka
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  authentication:
    type: tls
  authorization:
    type: simple
    acls:
      - resource:
          type: topic
          name: task-events
        operations: [Read, Write, Describe]
      - resource:
          type: group
          name: recurring-task-service
        operations: [Read]
```

**3. Configure Dapr with mTLS**:
```yaml
metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap.kafka:9093"
  - name: authType
    value: "mtls"
  - name: caCert
    secretKeyRef:
      name: recurring-task-service
      key: ca.crt
  - name: clientCert
    secretKeyRef:
      name: recurring-task-service
      key: user.crt
  - name: clientKey
    secretKeyRef:
      name: recurring-task-service
      key: user.key
```

## Event Design Guidelines

**Topic naming convention**:
```
<domain>-<entity>-<purpose>

Examples:
task-events       # All task lifecycle events
task-reminders    # Reminder notifications
task-audit        # Immutable audit trail
user-events       # User-related events
```

**Event type naming** (CloudEvents):
```
<reverse-dns>.<entity>.<action>

Examples:
com.todoapp.task.created
com.todoapp.task.completed
com.todoapp.task.updated
com.todoapp.task.deleted
```

**Partition key selection**:
- Use `user_id` for user-scoped events (guarantees ordering per user)
- Use `task_id` for task-scoped events
- Use `null` for broadcast events (no ordering needed)

**Replication settings**:
```yaml
# Development (1 broker)
replicas: 1
min.insync.replicas: 1

# Production (3+ brokers)
replicas: 3
min.insync.replicas: 2  # Tolerates 1 broker failure
```

## Idempotency Checklist

Ensure consumers are idempotent (safe to process events multiple times):

- [ ] **Event ID deduplication**: Track processed event IDs in Redis/database
- [ ] **Database constraints**: Use unique constraints to prevent duplicate writes
- [ ] **Idempotent operations**: Design state changes to be naturally idempotent
- [ ] **Manual offset commit**: Commit only after successful processing
- [ ] **Retry strategy**: Return `RETRY` status for transient errors

**Example deduplication** (Python):
```python
import redis

redis_client = redis.Redis(host='redis', port=6379)

@app.route('/task-events', methods=['POST'])
def handle_event():
    event = from_http(request.headers, request.get_data())
    event_id = event['id']

    # Check if already processed
    if redis_client.exists(f"processed:{event_id}"):
        return jsonify({'status': 'SUCCESS'})

    # Process event
    process_task_event(event.data)

    # Mark as processed (24h TTL)
    redis_client.setex(f"processed:{event_id}", 86400, "1")

    return jsonify({'status': 'SUCCESS'})
```

## Monitoring

**Key metrics to track**:
- **Consumer lag**: Number of unprocessed events
- **Processing latency**: Time from publish to consume
- **Error rate**: Failed events / total events
- **Throughput**: Events processed per second

**Check consumer lag**:
```bash
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-consumer-groups.sh \
    --bootstrap-server localhost:9092 \
    --describe \
    --group recurring-task-service
```

**Dapr metrics** (Prometheus format):
- `dapr_component_pubsub_ingress_count` - Events received
- `dapr_component_pubsub_ingress_latencies_ms` - Processing latency
- `dapr_runtime_pubsub_errors_total` - Error count

## Common Commands

**List Kafka clusters**:
```bash
kubectl get kafka -n kafka
```

**List topics**:
```bash
kubectl get kafkatopics -n kafka
```

**List users**:
```bash
kubectl get kafkausers -n kafka
```

**Describe cluster**:
```bash
kubectl describe kafka kafka-cluster -n kafka
```

**Check broker pods**:
```bash
kubectl get pods -n kafka -l strimzi.io/name=kafka-cluster-kafka
```

**View broker logs**:
```bash
kubectl logs -f kafka-cluster-kafka-0 -n kafka
```

**Connect to broker (debug)**:
```bash
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- /bin/bash
```

## Troubleshooting

**Consumer not receiving messages**:
1. Check Dapr subscription is applied: `kubectl get subscriptions`
2. Verify topic exists: `kubectl get kafkatopics -n kafka`
3. Check consumer group: `kafka-consumer-groups.sh --describe`
4. Review Dapr sidecar logs: `kubectl logs <pod> -c daprd`

**Events not publishing**:
1. Verify Dapr component is applied: `kubectl get components`
2. Check broker connectivity from producer pod
3. Review application logs for Dapr client errors
4. Verify topic has appropriate partitions and replication

**Performance issues**:
1. Increase partition count for higher parallelism
2. Scale consumer replicas to match partition count
3. Tune Kafka broker resources (CPU, memory, disk I/O)
4. Enable producer batching and compression

**Data loss concerns**:
1. Set `acks=all` in producer configuration
2. Ensure `min.insync.replicas >= 2`
3. Use manual offset commits in consumers
4. Implement idempotent processing to handle retries

## Architecture Decision Points

When designing event-driven systems:

**Topic granularity**:
- **Single topic per domain**: Easier management, sequential ordering
- **Topic per event type**: Finer-grained access control, independent scaling

**Partitioning strategy**:
- **By user ID**: Guarantees ordering per user
- **By entity ID**: Guarantees ordering per entity
- **Round-robin (no key)**: Maximum throughput, no ordering

**Consumer group strategy**:
- **One group per service**: Load balancing within service
- **Multiple groups**: Broadcast same events to multiple services

**Retention policy**:
- **Time-based**: `retention.ms` (e.g., 7 days)
- **Size-based**: `retention.bytes` (e.g., 1 GB per partition)
- **Compaction**: `cleanup.policy=compact` (event sourcing, audit logs)

Consult reference documentation for detailed patterns and configurations.
