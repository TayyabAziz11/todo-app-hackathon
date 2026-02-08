# Strimzi Kafka on Kubernetes

> **Source**: Strimzi Official Documentation (strimzi.io/docs/operators/latest/)

## Table of Contents
- [Strimzi Architecture](#strimzi-architecture)
- [Installation Methods](#installation-methods)
- [Custom Resource Definitions](#custom-resource-definitions)
- [Kafka Cluster Configuration](#kafka-cluster-configuration)
- [Topic Management](#topic-management)
- [User Management](#user-management)
- [Node Pools](#node-pools)
- [Production Best Practices](#production-best-practices)

## Strimzi Architecture

Strimzi extends Kubernetes with **operators** that automate Apache Kafka management.

**Core components**:

1. **Cluster Operator**
   - Manages Kafka clusters and supporting components
   - Deploys resources based on CRDs
   - Automates upgrades, scaling, and broker management
   - **Required**: Must be deployed first

2. **Topic Operator**
   - Manages Kafka topics via `KafkaTopic` CRDs
   - Enables declarative topic management
   - Part of Entity Operator

3. **User Operator**
   - Manages Kafka users via `KafkaUser` CRDs
   - Handles authentication and authorization
   - Generates certificates and secrets
   - Part of Entity Operator

4. **Entity Operator**
   - Runs Topic and User Operators together
   - Deployed automatically with Kafka cluster

**Infrastructure-as-Code workflow**:
- Define Kafka resources in YAML
- Version control configurations
- Automated deployment pipelines
- GitOps-friendly

## Installation Methods

### Method 1: Manual YAML (Recommended for Learning)

```bash
# 1. Create namespace
kubectl create namespace kafka

# 2. Install Cluster Operator
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# 3. Wait for operator to be ready
kubectl wait deployment/strimzi-cluster-operator --for=condition=Available --timeout=300s -n kafka
```

### Method 2: Helm Chart (Recommended for Production)

```bash
# Add Strimzi Helm repo
helm repo add strimzi https://strimzi.io/charts/
helm repo update

# Install with custom values
helm install kafka-operator strimzi/strimzi-kafka-operator \
  --namespace kafka \
  --create-namespace \
  --set watchNamespaces="{default,kafka}"
```

### Method 3: OperatorHub (OpenShift/OLM)

```bash
# Install via Operator Lifecycle Manager
kubectl create -f - <<EOF
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: strimzi-kafka-operator
  namespace: openshift-operators
spec:
  channel: stable
  name: strimzi-kafka-operator
  source: operatorhubio-catalog
  sourceNamespace: olm
EOF
```

**Verification**:
```bash
kubectl get pods -n kafka
# Expected: strimzi-cluster-operator-xxx Running
```

## Custom Resource Definitions

Strimzi provides CRDs for declarative Kafka management.

**Available CRDs**:
- `Kafka` - Kafka cluster configuration
- `KafkaTopic` - Topic specifications
- `KafkaUser` - User authentication and ACLs
- `KafkaNodePool` - Node pool definitions (broker/controller roles)
- `KafkaConnect` - Kafka Connect clusters
- `KafkaMirrorMaker2` - Cross-cluster replication
- `KafkaBridge` - HTTP Bridge for REST API access

**Check installed CRDs**:
```bash
kubectl get crd | grep kafka
```

## Kafka Cluster Configuration

**Minimal development cluster**:
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: kafka-cluster
  namespace: kafka
spec:
  kafka:
    version: 3.9.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
    storage:
      type: ephemeral
  entityOperator:
    topicOperator: {}
    userOperator: {}
```

**Production-grade cluster** (3 brokers, 3 replicas, persistent storage):
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: kafka-cluster
  namespace: kafka
spec:
  kafka:
    version: 3.9.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
        authentication:
          type: tls
    config:
      # Production durability settings
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
      # Performance tuning
      num.network.threads: 8
      num.io.threads: 8
      socket.send.buffer.bytes: 102400
      socket.receive.buffer.bytes: 102400
      socket.request.max.bytes: 104857600
      # Log retention
      log.retention.hours: 168  # 7 days
      log.segment.bytes: 1073741824  # 1 GB
    storage:
      type: persistent-claim
      size: 100Gi
      class: fast-ssd  # Use appropriate storage class
      deleteClaim: false
    resources:
      requests:
        memory: 4Gi
        cpu: "2"
      limits:
        memory: 8Gi
        cpu: "4"
  zookeeper:  # Only for Kafka < 4.0
    replicas: 3
    storage:
      type: persistent-claim
      size: 10Gi
      deleteClaim: false
  entityOperator:
    topicOperator:
      resources:
        requests:
          memory: 512Mi
          cpu: "0.2"
        limits:
          memory: 512Mi
          cpu: "0.5"
    userOperator:
      resources:
        requests:
          memory: 512Mi
          cpu: "0.2"
        limits:
          memory: 512Mi
          cpu: "0.5"
```

**Apply and monitor**:
```bash
kubectl apply -f kafka-cluster.yaml -n kafka

# Watch cluster creation
kubectl get kafka -n kafka -w

# Check broker pods
kubectl get pods -n kafka -l strimzi.io/name=kafka-cluster-kafka
```

**Service endpoints**:
```
# Internal access (from within Kubernetes)
kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092  # Plain
kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9093  # TLS

# Shorthand (from same namespace)
kafka-cluster-kafka-bootstrap:9092
```

## Topic Management

**Declarative topic creation**:
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 604800000  # 7 days in milliseconds
    segment.bytes: 1073741824  # 1 GB
    compression.type: producer  # Use producer's compression
    min.insync.replicas: 2
    cleanup.policy: delete
```

**Event-driven topic examples**:
```yaml
---
# Task lifecycle events
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 6  # Higher for more parallelism
  replicas: 3
  config:
    retention.ms: 604800000  # 7 days
    min.insync.replicas: 2

---
# Reminder notifications (higher retention)
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 2592000000  # 30 days
    min.insync.replicas: 2

---
# Audit log (long retention, compaction)
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-audit
  namespace: kafka
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 31536000000  # 365 days
    cleanup.policy: compact  # Keep latest per key
    min.insync.replicas: 2
```

**List topics**:
```bash
kubectl get kafkatopics -n kafka
```

## User Management

**Create user with TLS authentication**:
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
      # Producer permissions for task-events topic
      - resource:
          type: topic
          name: task-events
          patternType: literal
        operations:
          - Write
          - Describe
        host: "*"
      # Consumer permissions
      - resource:
          type: topic
          name: task-events
          patternType: literal
        operations:
          - Read
          - Describe
        host: "*"
      # Consumer group permissions
      - resource:
          type: group
          name: recurring-task-service
          patternType: literal
        operations:
          - Read
        host: "*"
```

**Strimzi auto-generates**:
- TLS certificates
- Kubernetes Secret: `recurring-task-service` containing:
  - `ca.crt` - Cluster CA certificate
  - `user.crt` - User certificate
  - `user.key` - User private key

**Use in Dapr component**:
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

## Node Pools

**Node pools** (Kafka 3.3+) enable separate broker and controller roles for better scalability.

**Broker pool**:
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaNodePool
metadata:
  name: broker-pool
  namespace: kafka
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  replicas: 3
  roles:
    - broker
  storage:
    type: persistent-claim
    size: 100Gi
  resources:
    requests:
      memory: 4Gi
      cpu: "2"
```

**Controller pool**:
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaNodePool
metadata:
  name: controller-pool
  namespace: kafka
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  replicas: 3
  roles:
    - controller
  storage:
    type: persistent-claim
    size: 10Gi
  resources:
    requests:
      memory: 2Gi
      cpu: "1"
```

**Benefits**:
- Scale brokers and controllers independently
- Optimize resources per role
- Simplified KRaft mode setup

## Production Best Practices

**Resource sizing**:
```yaml
# Minimum production setup
kafka.replicas: 3
kafka.storage.size: 100Gi
kafka.resources.requests.memory: 4Gi
kafka.resources.requests.cpu: 2

# High-throughput setup
kafka.replicas: 5+
kafka.storage.size: 500Gi+
kafka.resources.requests.memory: 16Gi
kafka.resources.requests.cpu: 4
```

**Durability settings**:
```yaml
config:
  default.replication.factor: 3
  min.insync.replicas: 2
  offsets.topic.replication.factor: 3
  transaction.state.log.replication.factor: 3
```

**Monitoring**:
```yaml
# Enable Prometheus metrics
kafka:
  metricsConfig:
    type: jmxPrometheusExporter
    valueFrom:
      configMapKeyRef:
        name: kafka-metrics
        key: kafka-metrics-config.yml
```

**Rack awareness** (multi-zone deployment):
```yaml
kafka:
  rack:
    topologyKey: topology.kubernetes.io/zone
```

**Storage class**:
- Use **fast SSDs** (NVMe preferred)
- Enable `deleteClaim: false` to prevent data loss on cluster deletion
- Consider **local persistent volumes** for maximum performance

**Network policies**:
```yaml
# Restrict access to Kafka brokers
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: kafka-access
  namespace: kafka
spec:
  podSelector:
    matchLabels:
      strimzi.io/name: kafka-cluster-kafka
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: default  # Only allow default namespace
      ports:
        - port: 9092
```

**Backup strategy**:
- Use **MirrorMaker 2** for cross-cluster replication
- Snapshot persistent volumes regularly
- Test disaster recovery procedures
