---
name: dapr
description: |
  Comprehensive Dapr (Distributed Application Runtime) skill for building distributed microservices from hello-world to production systems. Use this skill when working with:
  (1) Microservices architecture and distributed systems
  (2) Service-to-service communication, state management, pub/sub messaging, bindings, actors, secrets, configuration, locks, workflows, or cryptography
  (3) Dapr building blocks, components, or APIs
  (4) Local development with Dapr or Kubernetes deployment
  (5) Production-grade Dapr configurations including HA, mTLS, observability
  (6) Any task involving "Dapr", "distributed apps", "service mesh", "sidecar pattern"
  (7) Multi-language microservices (Python, Go, JavaScript, Java, .NET)
  (8) Event-driven architectures, actor pattern, workflow orchestration
  (9) Cloud-native application development with pluggable components
---

# Dapr (Distributed Application Runtime)

Build resilient, portable distributed applications using Dapr's building blocks and sidecar architecture.

## Overview

Dapr is a portable, event-driven runtime that simplifies building microservices by providing:
- **Building Blocks**: APIs for common distributed patterns (state, pub/sub, service invocation, etc.)
- **Sidecar Architecture**: Runs alongside your app in a separate process/container
- **Language Agnostic**: SDKs for Python, Go, JavaScript, Java, .NET, and HTTP/gRPC APIs
- **Pluggable Components**: Swap infrastructure without code changes (Redis ↔ Kafka ↔ AWS)
- **Production Ready**: HA, mTLS, observability, and security built-in

## Core Workflow

1. **Initialize Environment**: Set up Dapr locally or on Kubernetes
2. **Choose Building Blocks**: Select which Dapr APIs your app needs
3. **Configure Components**: Define infrastructure connections (state stores, message brokers, etc.)
4. **Develop Application**: Use Dapr SDK or HTTP/gRPC APIs
5. **Deploy**: Run with `dapr run` locally or deploy to Kubernetes with annotations

## Quick Start

### Local Development

```bash
# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr (installs Docker containers: Redis, Zipkin, Placement)
dapr init

# Verify
dapr --version

# Run your app with Dapr sidecar
dapr run --app-id myapp --app-port 5000 -- python app.py
```

**Use the initialization script:**
```bash
.claude/skills/dapr/scripts/init_dapr_local.sh
```

### Kubernetes Deployment

```bash
# Development mode (includes Redis + Zipkin)
dapr init -k --dev

# Production mode (HA with 3 replicas)
dapr init -k --enable-ha=true

# Verify
dapr status -k
```

**Use the Kubernetes initialization script:**
```bash
# Development
.claude/skills/dapr/scripts/init_dapr_k8s.sh dev

# Production
.claude/skills/dapr/scripts/init_dapr_k8s.sh prod
```

## Building Blocks

Dapr provides 10+ building blocks. Always refer to `references/building-blocks.md` for complete API details.

### 1. Service-to-Service Invocation

Call other services using app IDs with built-in service discovery, tracing, and mTLS.

```python
from dapr.clients import DaprClient

with DaprClient() as client:
    resp = client.invoke_method(
        app_id='checkout-service',
        method_name='process-order',
        data='{"orderId": 123}',
        http_verb='POST'
    )
```

**When to use**: Synchronous microservice communication, API gateway patterns, request/response workflows.

### 2. State Management

Persist and retrieve key-value data with pluggable state stores (Redis, PostgreSQL, MongoDB, etc.).

```python
# Save state
client.save_state('statestore', 'order-123', json.dumps(order_data))

# Get state
state = client.get_state('statestore', 'order-123')

# Transaction (multi-key ACID operations)
client.execute_state_transaction('statestore', [
    {'operation': 'upsert', 'request': {'key': 'k1', 'value': 'v1'}},
    {'operation': 'delete', 'request': {'key': 'k2'}}
])
```

**Features**: ETags for optimistic concurrency, TTL, bulk operations, querying (filter/sort/paginate).

**When to use**: Session management, caching, shopping carts, user preferences.

### 3. Pub/Sub Messaging

Event-driven messaging with at-least-once delivery and pluggable brokers (Redis, Kafka, RabbitMQ, etc.).

```python
# Publish
client.publish_event('pubsub', 'orders', json.dumps({'orderId': 123}))

# Subscribe (Flask)
@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    return jsonify([{'pubsubname': 'pubsub', 'topic': 'orders', 'route': '/orders'}])

@app.route('/orders', methods=['POST'])
def handle_order():
    event = from_http(request.headers, request.get_data())
    # Process event
    return jsonify({'success': True}), 200
```

**When to use**: Decoupled services, event-driven architecture, async processing, webhooks.

### 4. Bindings

Trigger code from external events (input) or invoke external systems (output).

```python
# Output binding (send to Kafka, S3, Twilio, etc.)
client.invoke_binding('kafka-binding', 'create', data, metadata={'topic': 'events'})

# Input binding (receive events via HTTP endpoint)
@app.route('/cron-job', methods=['POST'])
def scheduled_task():
    # Triggered by cron binding
    return {}, 200
```

**When to use**: Scheduled jobs (cron), external integrations (Kafka, queues), file uploads (S3, Azure Storage).

### 5. Actors

Virtual actors with turn-based concurrency for stateful operations.

**When to use**: User sessions, device twins, shopping carts, game entities, workflow orchestration.

See `references/building-blocks.md` for implementation examples.

### 6-10. Additional Building Blocks

- **Secrets Management**: Retrieve secrets from Vault, Kubernetes, AWS Secrets Manager
- **Configuration**: Dynamic configuration with change notifications
- **Distributed Lock**: Coordinate access to shared resources
- **Workflows**: Long-running orchestrations spanning multiple services
- **Cryptography**: Encrypt/decrypt data without exposing keys

**Reference**: See `references/building-blocks.md` for all APIs and examples.

## Components

Components are pluggable infrastructure implementations. Use the component generator script for common patterns.

### Generate Component YAML

```bash
# Redis state store
python .claude/skills/dapr/scripts/create_component.py state.redis mystatestore \
  --redis-host redis:6379 \
  --enable-tls \
  --scopes myapp,otherapp \
  --output components/statestore.yaml

# Kafka pub/sub
python .claude/skills/dapr/scripts/create_component.py pubsub.redis mypubsub \
  --redis-host redis-master:6379 \
  --namespace production

# Kafka binding
python .claude/skills/dapr/scripts/create_component.py bindings.kafka kafka-events \
  --brokers kafka-broker:9092 \
  --topics events,orders \
  --consumer-group myapp-group
```

### Component Structure

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    secretKeyRef:
      name: redis-secret
      key: password
  scopes:
  - app1  # Restrict to specific apps
```

**Reference**: See `references/components.md` for comprehensive component configurations including:
- State stores (Redis, PostgreSQL, MongoDB, Cassandra, CosmosDB, DynamoDB)
- Pub/sub brokers (Redis, Kafka, RabbitMQ, Azure Service Bus, AWS SNS/SQS)
- Bindings (Kafka, Cron, HTTP, AWS S3, Azure Storage)
- Secret stores (Kubernetes, Vault, AWS Secrets Manager, Azure Key Vault)
- Configuration stores (Redis, PostgreSQL)
- Lock stores (Redis)

## SDK Usage

Dapr provides SDKs for multiple languages. Always use SDK when possible for type safety and convenience.

### Installation

```bash
# Python
pip install dapr dapr-ext-grpc

# Go
go get github.com/dapr/go-sdk

# JavaScript/TypeScript
npm install @dapr/dapr

# Java
# Add to pom.xml: io.dapr:dapr-sdk:1.11.0

# .NET
dotnet add package Dapr.Client
```

### Language-Specific Examples

**Reference**: See `references/sdk-examples.md` for complete examples in:
- Python (Flask, FastAPI)
- Go (HTTP server, gRPC)
- JavaScript/TypeScript (Express, Node.js)
- Java (Spring Boot)
- .NET (ASP.NET Core)

## Hello World Template

A complete example demonstrating multiple building blocks.

**Location**: `assets/hello-world/python/`

```bash
# Copy template
cp -r .claude/skills/dapr/assets/hello-world/python ./my-dapr-service
cd my-dapr-service

# Install dependencies
pip install -r requirements.txt

# Run with Dapr
dapr run --app-id hello-python --app-port 5000 -- python app.py
```

**Template includes**: Service invocation, state management, pub/sub, service-to-service calls.

## Deployment Patterns

### Local Development

```bash
# Single app
dapr run --app-id myapp --app-port 5000 -- python app.py

# With custom components
dapr run --app-id myapp --app-port 5000 \
  --components-path ./components \
  --config ./config.yaml \
  -- python app.py

# Multi-app (using dapr.yaml)
dapr run -f dapr.yaml
```

### Kubernetes Deployment

Add Dapr annotations to your deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "myapp"
        dapr.io/app-port: "5000"
        dapr.io/config: "appconfig"
        dapr.io/log-level: "info"
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        ports:
        - containerPort: 5000
```

**Reference**: See `references/deployment.md` for:
- Production-grade configurations
- High availability setup (HA with 3 replicas)
- Security hardening (mTLS, API tokens, network policies)
- Observability (Prometheus metrics, Jaeger tracing, logging)
- Resource management (CPU/memory limits)
- Best practices and troubleshooting

## Production Considerations

### High Availability

```bash
# Kubernetes with HA (3 replicas for control plane)
helm install dapr dapr/dapr \
  --namespace dapr-system \
  --set global.ha.enabled=true \
  --set global.mtls.enabled=true
```

### Security (mTLS)

Enable automatic mutual TLS for all service-to-service communication:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: appconfig
spec:
  mtls:
    enabled: true
    workloadCertTTL: "24h"
```

### Observability

**Metrics**: Prometheus (enabled by default on port 9090)
**Tracing**: Zipkin, Jaeger, OTEL Collector
**Logging**: JSON format with configurable levels

```yaml
annotations:
  dapr.io/enable-metrics: "true"
  dapr.io/metrics-port: "9090"
  dapr.io/log-level: "info"
```

### Resource Limits

```yaml
annotations:
  dapr.io/sidecar-cpu-limit: "300m"
  dapr.io/sidecar-memory-limit: "512Mi"
  dapr.io/sidecar-cpu-request: "100m"
  dapr.io/sidecar-memory-request: "250Mi"
```

**Reference**: See `references/deployment.md` for complete production deployment guide.

## Common Patterns

### Multi-Environment Configuration

Structure components for different environments:

```
components/
├── base/
│   ├── statestore.yaml
│   └── pubsub.yaml
├── dev/
│   └── kustomization.yaml
├── staging/
│   └── kustomization.yaml
└── production/
    └── kustomization.yaml (with secrets, HA configs)
```

### Service Mesh Integration

Dapr complements service meshes:
- **Dapr**: Application-level patterns (state, pub/sub, actors)
- **Service Mesh**: Network-level concerns (traffic routing, retries)

Can run together or independently.

### Migration Strategy

1. **Start Small**: Add Dapr to one service, use service invocation
2. **Incremental Adoption**: Add state management, then pub/sub
3. **Component Swapping**: Start with Redis, migrate to production stores without code changes
4. **Production Hardening**: Enable HA, mTLS, observability

## Reference Files

- **`references/building-blocks.md`**: Complete API reference for all 10+ building blocks with examples
- **`references/components.md`**: Component configuration patterns for all supported implementations
- **`references/deployment.md`**: Production deployment guide (local, K8s, HA, security, observability)
- **`references/sdk-examples.md`**: Multi-language SDK examples (Python, Go, JS, Java, .NET)

## Scripts

- **`scripts/init_dapr_local.sh`**: Initialize Dapr for local development
- **`scripts/init_dapr_k8s.sh <mode>`**: Initialize Dapr on Kubernetes (dev/prod)
- **`scripts/create_component.py`**: Generate component YAML files from templates

## Assets

- **`assets/hello-world/python/`**: Complete Python hello-world service template

## Troubleshooting

**Sidecar not injecting**: Check namespace has `dapr.io/enabled=true` label
**Component not found**: Verify component namespace matches pod namespace
**mTLS errors**: Check certificate expiry with `dapr mtls export -o ./certs`
**High latency**: Review sidecar resource limits, enable metrics to identify bottlenecks

**Dashboard**: `dapr dashboard` (local) or `dapr dashboard -k` (Kubernetes)

**Logs**: `kubectl logs <pod> -c daprd` (sidecar logs)

## Additional Resources

- Official Docs: https://docs.dapr.io
- GitHub: https://github.com/dapr/dapr
- Discord: https://discord.gg/dapr
- Quickstarts: https://github.com/dapr/quickstarts
