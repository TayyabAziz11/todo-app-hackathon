# Dapr Components Configuration Reference

Components are Dapr's pluggable resources that provide building block implementations. This reference covers configuration patterns for common component types.

## Table of Contents

1. [Component Structure](#component-structure)
2. [State Stores](#state-stores)
3. [Pub/Sub Brokers](#pubsub-brokers)
4. [Bindings](#bindings)
5. [Secret Stores](#secret-stores)
6. [Configuration Stores](#configuration-stores)
7. [Lock Stores](#lock-stores)
8. [Component Scopes](#component-scopes)
9. [Secret References](#secret-references)

---

## Component Structure

All Dapr components follow this YAML structure:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: <component-name>
  namespace: <namespace>  # Kubernetes only
spec:
  type: <component-type>.<implementation>
  version: v1
  metadata:
  - name: <key>
    value: <value>
  # Optional: Restrict to specific apps
  scopes:
  - app1
  - app2
```

**Key Fields:**
- `metadata.name`: Unique identifier for the component
- `spec.type`: Component category and implementation (e.g., `state.redis`)
- `spec.version`: API version (typically `v1`)
- `spec.metadata`: Component-specific configuration
- `scopes`: Apps allowed to use this component (optional)

---

## State Stores

### Redis State Store

**Local Development:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
  - name: actorStateStore
    value: "true"  # Enable for actor state
```

**Production (Kubernetes with TLS):**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: production
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
  - name: failover
    value: "true"
  - name: sentinelMasterName
    value: mymaster
```

### PostgreSQL State Store

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: postgres-state
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "host=localhost user=postgres password=pass database=dapr port=5432 sslmode=disable"
  - name: tableName
    value: state
  - name: metadataTableName
    value: metadata
  - name: cleanupIntervalInSeconds
    value: "3600"
```

**With Connection Pooling:**
```yaml
  metadata:
  - name: connectionString
    value: "host=localhost user=postgres password=pass database=dapr port=5432 pool_max_conns=10"
  - name: timeout
    value: "30"
  - name: maxConIdleTime
    value: "0"
```

### MongoDB State Store

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: mongodb-state
spec:
  type: state.mongodb
  version: v1
  metadata:
  - name: host
    value: mongodb://localhost:27017
  - name: username
    value: admin
  - name: password
    secretKeyRef:
      name: mongo-secret
      key: password
  - name: databaseName
    value: daprDb
  - name: collectionName
    value: daprCollection
  - name: writeConcern
    value: majority
  - name: readConcern
    value: majority
```

### Cassandra State Store

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: cassandra-state
spec:
  type: state.cassandra
  version: v1
  metadata:
  - name: hosts
    value: cassandra.cassandra.svc.cluster.local
  - name: port
    value: "9042"
  - name: username
    value: cassandra
  - name: password
    secretKeyRef:
      name: cassandra-secret
      key: password
  - name: keyspace
    value: dapr
  - name: table
    value: state
  - name: consistency
    value: Quorum
  - name: replicationFactor
    value: "3"
```

---

## Pub/Sub Brokers

### Redis Pub/Sub

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
  - name: consumerID
    value: "{appID}"  # Uses app ID as consumer
  - name: enableTLS
    value: "false"
  - name: processingTimeout
    value: "60s"
  - name: redeliverInterval
    value: "30s"
  - name: maxLenApprox
    value: "10000"
```

### Kafka Pub/Sub

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
    value: localhost:9092
  - name: consumerGroup
    value: group1
  - name: clientID
    value: dapr-client
  - name: authType
    value: password
  - name: saslUsername
    secretKeyRef:
      name: kafka-secret
      key: username
  - name: saslPassword
    secretKeyRef:
      name: kafka-secret
      key: password
  - name: maxMessageBytes
    value: "1048576"
  - name: consumeRetryInterval
    value: "200ms"
```

**With SASL/TLS:**
```yaml
  metadata:
  - name: authType
    value: certificate
  - name: caCert
    value: |
      -----BEGIN CERTIFICATE-----
      ...
      -----END CERTIFICATE-----
  - name: clientCert
    secretKeyRef:
      name: kafka-tls
      key: client-cert
  - name: clientKey
    secretKeyRef:
      name: kafka-tls
      key: client-key
```

### RabbitMQ Pub/Sub

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: rabbitmq-pubsub
spec:
  type: pubsub.rabbitmq
  version: v1
  metadata:
  - name: host
    value: amqp://localhost:5672
  - name: username
    value: guest
  - name: password
    secretKeyRef:
      name: rabbitmq-secret
      key: password
  - name: durable
    value: "true"
  - name: deletedWhenUnused
    value: "false"
  - name: autoAck
    value: "false"
  - name: deliveryMode
    value: "2"  # Persistent
  - name: requeueInFailure
    value: "true"
  - name: prefetchCount
    value: "10"
  - name: reconnectWait
    value: "3s"
  - name: concurrencyMode
    value: parallel
```

---

## Bindings

### Kafka Binding (Input/Output)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-binding
spec:
  type: bindings.kafka
  version: v1
  metadata:
  - name: brokers
    value: localhost:9092
  - name: topics
    value: topic1,topic2
  - name: consumerGroup
    value: group1
  - name: publishTopic
    value: output-topic
  - name: authType
    value: none
  - name: direction
    value: input,output  # or just "input" or "output"
```

### Cron Binding (Scheduled Jobs)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: daily-cleanup
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "0 2 * * *"  # 2 AM daily
  - name: direction
    value: input
```

**Schedule Formats:**
- Cron: `"0 */5 * * *"` (every 5 minutes)
- Interval: `"@every 1h30m"` (every 1.5 hours)
- Named: `"@daily"`, `"@hourly"`, `"@weekly"`

### HTTP Binding

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: http-binding
spec:
  type: bindings.http
  version: v1
  metadata:
  - name: url
    value: https://api.example.com/webhook
  - name: method
    value: POST
  - name: direction
    value: output
```

### AWS S3 Binding

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: s3-binding
spec:
  type: bindings.aws.s3
  version: v1
  metadata:
  - name: bucket
    value: my-bucket
  - name: region
    value: us-east-1
  - name: accessKey
    secretKeyRef:
      name: aws-secret
      key: access-key
  - name: secretKey
    secretKeyRef:
      name: aws-secret
      key: secret-key
  - name: direction
    value: input,output
```

---

## Secret Stores

### Kubernetes Secrets

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

### HashiCorp Vault

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: vault
spec:
  type: secretstores.hashicorp.vault
  version: v1
  metadata:
  - name: vaultAddr
    value: https://vault.example.com:8200
  - name: vaultToken
    value: root
  - name: vaultTokenMountPath
    value: /vault/token
  - name: vaultKVPrefix
    value: dapr
  - name: vaultKVUsePrefix
    value: "true"
  - name: skipVerify
    value: "false"
  - name: tlsServerName
    value: vault.example.com
  - name: caCert
    value: |
      -----BEGIN CERTIFICATE-----
      ...
      -----END CERTIFICATE-----
```

### AWS Secrets Manager

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: aws-secrets
spec:
  type: secretstores.aws.secretmanager
  version: v1
  metadata:
  - name: region
    value: us-east-1
  - name: accessKey
    value: AWS_ACCESS_KEY
  - name: secretKey
    value: AWS_SECRET_KEY
```

---

## Configuration Stores

### Redis Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: configstore
spec:
  type: configuration.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
  - name: enableTLS
    value: "false"
```

### PostgreSQL Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: postgres-config
spec:
  type: configuration.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "host=localhost user=postgres password=pass database=config"
  - name: table
    value: configuration
  - name: maxIdleConns
    value: "10"
  - name: connMaxLifetime
    value: "0"
```

---

## Lock Stores

### Redis Lock

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: lockstore
spec:
  type: lock.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
  - name: enableTLS
    value: "false"
```

---

## Component Scopes

Limit component access to specific applications:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: sensitive-statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  scopes:
  - payment-service
  - billing-service
  # Only these apps can use this component
```

---

## Secret References

Reference Kubernetes secrets in component metadata:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis-master:6379
  - name: redisPassword
    secretKeyRef:
      name: redis-secret  # Kubernetes Secret name
      key: password       # Key within the secret
auth:
  secretStore: kubernetes-secrets  # Optional: specify secret store
```

**Create the Kubernetes Secret:**
```bash
kubectl create secret generic redis-secret --from-literal=password='MyRedisPassword'
```

---

## Environment-Specific Configurations

### Development (Local)

Use simple, unsecured configurations:
```yaml
spec:
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
```

### Staging

Add basic security:
```yaml
spec:
  metadata:
  - name: redisHost
    value: redis-staging.svc.cluster.local:6379
  - name: redisPassword
    secretKeyRef:
      name: redis-staging-secret
      key: password
```

### Production

Full security with TLS, secrets, and HA:
```yaml
spec:
  metadata:
  - name: redisHost
    value: redis-prod-master.svc.cluster.local:6379
  - name: redisPassword
    secretKeyRef:
      name: redis-prod-secret
      key: password
  - name: enableTLS
    value: "true"
  - name: failover
    value: "true"
  - name: sentinelMasterName
    value: mymaster
  scopes:
  - critical-service
```

---

## Template Variables

Use placeholders in component metadata:

```yaml
metadata:
- name: clientID
  value: "{appID}"  # Replaced with app's ID
- name: namespace
  value: "{namespace}"  # Replaced with pod's namespace
- name: podName
  value: "{podName}"  # Replaced with pod name
- name: uuid
  value: "{uuid}"  # Replaced with unique UUID
```

**Example:**
```yaml
- name: consumerID
  value: "{appID}-{namespace}"  # Results in: "myapp-production"
```
