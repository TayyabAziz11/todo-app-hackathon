# Dapr Building Blocks Reference

This document provides detailed information about all Dapr building blocks, their APIs, and usage patterns.

## Table of Contents

1. [Service-to-Service Invocation](#service-to-service-invocation)
2. [State Management](#state-management)
3. [Pub/Sub Messaging](#pubsub-messaging)
4. [Bindings](#bindings)
5. [Actors](#actors)
6. [Secrets Management](#secrets-management)
7. [Configuration](#configuration)
8. [Distributed Lock](#distributed-lock)
9. [Workflows](#workflows)
10. [Cryptography](#cryptography)

---

## Service-to-Service Invocation

**Purpose:** Enable secure, reliable service-to-service communication with service discovery, distributed tracing, and error handling.

**HTTP API:**
```
GET/POST http://localhost:3500/v1.0/invoke/<app-id>/method/<method-name>
```

**Use Cases:**
- Microservice communication
- API gateway patterns
- Request/response workflows

**Features:**
- Automatic service discovery
- Built-in distributed tracing
- mTLS encryption
- Automatic retries
- Circuit breaking

**Example (Python):**
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

**Example (Go):**
```go
client, _ := dapr.NewClient()
resp, err := client.InvokeMethod(ctx, "checkout-service", "process-order", "post")
```

---

## State Management

**Purpose:** Persist and retrieve application state with pluggable state stores.

**HTTP API:**
```
POST   http://localhost:3500/v1.0/state/<store-name>
GET    http://localhost:3500/v1.0/state/<store-name>/<key>
DELETE http://localhost:3500/v1.0/state/<store-name>/<key>
POST   http://localhost:3500/v1.0/state/<store-name>/bulk
POST   http://localhost:3500/v1.0/state/<store-name>/transaction
POST   http://localhost:3500/v1.0/state/<store-name>/query
```

**Features:**
- ETags for optimistic concurrency
- Bulk operations
- Transactions (multi-key ACID)
- State query (filter, sort, paginate)
- TTL support
- State encryption

**Supported State Stores:**
- Redis, PostgreSQL, MySQL, MongoDB, Cassandra, CosmosDB, DynamoDB, etc.

**Example (JavaScript):**
```javascript
const client = new DaprClient();

// Save state
await client.state.save('statestore', [
    { key: 'order-1', value: { orderId: 1, status: 'pending' } }
]);

// Get state
const order = await client.state.get('statestore', 'order-1');

// Transaction
await client.state.transaction('statestore', [
    { operation: 'upsert', request: { key: 'key1', value: 'val1' } },
    { operation: 'delete', request: { key: 'key2' } }
]);

// Query (if state store supports querying)
const results = await client.state.query('statestore', {
    filter: { EQ: { 'status': 'pending' } },
    sort: [{ key: 'orderId', order: 'DESC' }],
    page: { limit: 10 }
});
```

**ETag Concurrency Example:**
```python
# Get with ETag
item = client.get_state('statestore', 'key1')
etag = item.etag

# Save with ETag (fails if modified)
client.save_state('statestore', 'key1', 'new-value', etag=etag)
```

---

## Pub/Sub Messaging

**Purpose:** Implement event-driven architectures with at-least-once delivery guarantees.

**HTTP API:**
```
POST http://localhost:3500/v1.0/publish/<pubsub-name>/<topic>
```

**Subscription Endpoint (App implements):**
```
GET  /dapr/subscribe     # Returns subscription list
POST /<route>            # Receives messages
```

**Features:**
- At-least-once delivery
- Message TTL
- Dead letter queues
- CloudEvents format
- Bulk publish
- Message routing

**Supported Brokers:**
- Redis, Kafka, RabbitMQ, Azure Service Bus, AWS SNS/SQS, GCP Pub/Sub, etc.

**Publisher Example (Python):**
```python
client.publish_event(
    pubsub_name='orderpubsub',
    topic_name='orders',
    data=json.dumps({'orderId': 123}),
    data_content_type='application/json'
)
```

**Subscriber Example (Flask):**
```python
@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    return jsonify([{
        'pubsubname': 'orderpubsub',
        'topic': 'orders',
        'route': 'orders'
    }])

@app.route('/orders', methods=['POST'])
def orders_handler():
    event = from_http(request.headers, request.get_data())
    print(f"Received: {event.data}")
    return json.dumps({'success': True}), 200
```

**Message Routing:**
```python
# Subscription with routing rules
{
    'pubsubname': 'pubsub',
    'topic': 'orders',
    'route': 'orders',
    'metadata': {
        'rawPayload': 'true'
    },
    'routes': {
        'rules': [
            {'match': 'event.type == "premium"', 'path': '/premium-orders'},
            {'match': 'event.type == "standard"', 'path': '/orders'}
        ],
        'default': '/orders'
    }
}
```

---

## Bindings

**Purpose:** Trigger code execution from external events or invoke external systems.

**Types:**
- **Input Bindings:** External events trigger your app (e.g., Kafka message arrives)
- **Output Bindings:** Your app invokes external systems (e.g., send SMS via Twilio)

**HTTP API (Output):**
```
POST http://localhost:3500/v1.0/bindings/<binding-name>
```

**Input Binding Endpoint (App implements):**
```
POST /<binding-name>
```

**Supported Bindings:**
- Kafka, RabbitMQ, Cron, HTTP, AWS S3, Azure Storage, GCP Storage, MQTT, Twitter, etc.

**Output Binding Example (Go):**
```go
req := &dapr.InvokeBindingRequest{
    Name:      "kafka-binding",
    Operation: "create",
    Data:      []byte(`{"message":"Hello"}`),
    Metadata:  map[string]string{"topic": "orders"},
}
client.InvokeOutputBinding(ctx, req)
```

**Input Binding Example (Python):**
```python
@app.route('/kafka-binding', methods=['POST'])
def kafka_handler():
    data = request.json
    print(f"Received from Kafka: {data}")
    return {}, 200
```

**Cron Binding (Scheduled Jobs):**
Component YAML:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: cron-job
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "@every 1m"  # Or "0 */5 * * *" for cron format
```

---

## Actors

**Purpose:** Virtual actors pattern for stateful, concurrent operations with turn-based access guarantees.

**Features:**
- Turn-based concurrency (one method at a time)
- State management
- Timers and reminders
- Automatic activation/deactivation
- Location transparency

**HTTP API:**
```
POST   http://localhost:3500/v1.0/actors/<actor-type>/<actor-id>/method/<method>
GET    http://localhost:3500/v1.0/actors/<actor-type>/<actor-id>/state/<key>
POST   http://localhost:3500/v1.0/actors/<actor-type>/<actor-id>/state
DELETE http://localhost:3500/v1.0/actors/<actor-type>/<actor-id>/reminders/<name>
```

**Use Cases:**
- User sessions
- Device twins
- Shopping carts
- Game entities
- Workflow orchestration

**Example (Python):**
```python
from dapr.actor import Actor, ActorMethod, ActorId

class CounterActor(Actor):
    async def _on_activate(self):
        self.count = await self._state_manager.try_get_state('count') or 0

    @ActorMethod(name="increment")
    async def increment(self):
        self.count += 1
        await self._state_manager.set_state('count', self.count)
        return self.count

# Invoke actor
proxy = ActorProxy.create('CounterActor', ActorId('counter-1'), CounterActorInterface)
result = await proxy.increment()
```

**Reminders vs Timers:**
- **Reminders:** Persist across deactivations, guaranteed delivery
- **Timers:** Not persisted, stopped on deactivation

---

## Secrets Management

**Purpose:** Securely access secrets from secret stores without hardcoding credentials.

**HTTP API:**
```
GET http://localhost:3500/v1.0/secrets/<secret-store>/<secret-name>
GET http://localhost:3500/v1.0/secrets/<secret-store>/bulk
```

**Supported Secret Stores:**
- Kubernetes Secrets, HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager, etc.

**Example (Python):**
```python
secrets = client.get_secret(
    store_name='vault',
    secret_name='db-credentials'
)
username = secrets['username']
password = secrets['password']
```

**Component Reference in Metadata:**
```yaml
spec:
  metadata:
  - name: connectionString
    secretKeyRef:
      name: redis-secret
      key: password
```

---

## Configuration

**Purpose:** Retrieve application configuration from configuration stores with change notifications.

**HTTP API:**
```
GET http://localhost:3500/v1.0/configuration/<store-name>
GET http://localhost:3500/v1.0/configuration/<store-name>/<key>
GET http://localhost:3500/v1.0/configuration/<store-name>/subscribe
```

**Supported Stores:**
- Redis, PostgreSQL, Azure App Configuration, etc.

**Example (Go):**
```go
// Get configuration
items, err := client.GetConfigurationItems(ctx, "configstore", []string{"key1", "key2"})

// Subscribe to changes
subscriptionID, err := client.SubscribeConfigurationItems(ctx, "configstore",
    []string{"key1"}, func(ctx context.Context, items []*ConfigurationItem) error {
        fmt.Printf("Config changed: %v\n", items)
        return nil
    })
```

---

## Distributed Lock

**Purpose:** Coordinate access to shared resources across distributed applications.

**HTTP API:**
```
POST   http://localhost:3500/v1.0-alpha1/lock/<store-name>
POST   http://localhost:3500/v1.0-alpha1/unlock/<store-name>
```

**Features:**
- Lock expiry (TTL)
- Owner identification
- Prevent race conditions

**Example (Go):**
```go
// Acquire lock
resp, err := client.TryLockAlpha1(ctx, "lockstore", &dapr.LockRequest{
    LockOwner:       "client-123",
    ResourceID:      "order-456",
    ExpiryInSeconds: 60,
})

if resp.Success {
    // Critical section
    defer client.UnlockAlpha1(ctx, "lockstore", &dapr.UnlockRequest{
        LockOwner:  "client-123",
        ResourceID: "order-456",
    })
}
```

---

## Workflows

**Purpose:** Orchestrate long-running, stateful processes across multiple services.

**HTTP API:**
```
POST   http://localhost:3500/v1.0-beta1/workflows/<workflow-name>/start
GET    http://localhost:3500/v1.0-beta1/workflows/<instance-id>
POST   http://localhost:3500/v1.0-beta1/workflows/<instance-id>/terminate
POST   http://localhost:3500/v1.0-beta1/workflows/<instance-id>/pause
POST   http://localhost:3500/v1.0-beta1/workflows/<instance-id>/resume
```

**Features:**
- Durable execution
- Automatic state persistence
- Error handling and retries
- Human-in-the-loop patterns
- Parallel execution

**Example (Python):**
```python
from dapr.ext.workflow import WorkflowRuntime, WorkflowContext

def order_workflow(ctx: WorkflowContext, order):
    # Step 1: Reserve inventory
    inventory_result = yield ctx.call_activity('reserve_inventory', order)

    # Step 2: Process payment
    payment_result = yield ctx.call_activity('process_payment', order)

    # Step 3: Ship order
    if payment_result.success:
        yield ctx.call_activity('ship_order', order)

    return {'status': 'completed'}

# Start workflow
client.start_workflow(
    workflow_component='dapr',
    workflow_name='order_workflow',
    input={'orderId': 123}
)
```

---

## Cryptography

**Purpose:** Encrypt/decrypt data without exposing cryptographic keys to applications.

**HTTP API:**
```
POST http://localhost:3500/v1.0-alpha1/crypto/<vault-name>/encrypt
POST http://localhost:3500/v1.0-alpha1/crypto/<vault-name>/decrypt
```

**Features:**
- Key rotation support
- Algorithm flexibility
- Streaming encryption

**Example (JavaScript):**
```javascript
// Encrypt
const encrypted = await client.crypto.encrypt({
    componentName: 'vault',
    keyName: 'my-key',
    plainText: Buffer.from('sensitive data'),
    algorithm: 'RSA-OAEP-256'
});

// Decrypt
const decrypted = await client.crypto.decrypt({
    componentName: 'vault',
    keyName: 'my-key',
    cipherText: encrypted
});
```

---

## Common Patterns

### Error Handling
All building blocks return errors consistently. Always check error codes and implement retry logic where appropriate.

### Metadata
Most APIs support metadata for additional configuration:
```python
client.save_state('statestore', 'key', 'value', metadata={'ttlInSeconds': '3600'})
```

### Resiliency
Configure retries, timeouts, and circuit breakers in resiliency policies:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Resiliency
metadata:
  name: myresiliency
spec:
  policies:
    retries:
      DefaultRetryPolicy:
        policy: constant
        duration: 5s
        maxRetries: 3
```
