# Phase V.0 Infrastructure Topology

**Deployment Date**: 2026-02-06
**Kubernetes Version**: v1.35.0
**Environment**: Minikube (Local Development)

---

## Infrastructure Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Minikube Cluster                         │
│                     (4 CPU, 7.6GB RAM, 20GB Disk)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             NAMESPACE: dapr-system                        │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  • dapr-operator          (1/1 Running, v1.16.8)         │  │
│  │  • dapr-sentry            (1/1 Running, v1.16.8)         │  │
│  │  • dapr-sidecar-injector  (1/1 Running, v1.16.8)         │  │
│  │  • dapr-placement-server  (1/1 Running, v1.16.8)         │  │
│  │  • dapr-scheduler-server  (3/3 Running, v1.16.8)         │  │
│  │  • dapr-dashboard         (1/1 Running, v0.15.0)         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             NAMESPACE: todo-app-dev                       │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │  PostgreSQL (Bitnami)                               │ │  │
│  │  │  • postgresql-0 (1/1 Running, v18.1.0)              │ │  │
│  │  │  • Service: postgresql.todo-app-dev.svc:5432        │ │  │
│  │  │  • Database: todoapp_db                             │ │  │
│  │  │  • User: todoapp                                    │ │  │
│  │  │  • Storage: 5Gi PVC                                 │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │                                                            │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │  Apache Kafka (Strimzi)                             │ │  │
│  │  │  • Cluster: todo-kafka (KRaft mode, v4.0.1)         │ │  │
│  │  │  • Broker: todo-kafka-kafka-pool-0 (1/1 Running)    │ │  │
│  │  │  • Entity Operator: (2/2 Running)                   │ │  │
│  │  │    - Topic Operator                                 │ │  │
│  │  │    - User Operator                                  │ │  │
│  │  │  • Bootstrap: todo-kafka-kafka-bootstrap:9092       │ │  │
│  │  │  • Storage: 5Gi PVC                                 │ │  │
│  │  │  • Replication Factor: 1 (dev mode)                 │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │                                                            │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │  Strimzi Cluster Operator                           │ │  │
│  │  │  • strimzi-cluster-operator (1/1 Running)           │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │                                                            │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │  Kubernetes Secrets                                 │ │  │
│  │  │  • postgres-credentials (DB connection string)      │ │  │
│  │  │  • jwt-signing-key (JWT signing key)                │ │  │
│  │  │  • openai-api-key (OpenAI API key)                  │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             NAMESPACE: ingress-nginx                      │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  • ingress-nginx-controller (1/1 Running)                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             NAMESPACE: kube-system                        │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  • coredns (1/1 Running)                                 │  │
│  │  • metrics-server (1/1 Running)                          │  │
│  │  • kube-apiserver, kube-scheduler, etc.                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Minikube Configuration
- **Driver**: Docker
- **Kubernetes Version**: v1.35.0 (>= v1.28+ requirement ✅)
- **CPU**: 4 cores ✅
- **Memory**: 7802MB (~7.6GB, 5% below spec) ⚠️
- **Disk**: 20GB ✅
- **Addons**: ingress, metrics-server

### Dapr Runtime
- **Version**: 1.16.8
- **Control Plane Pods**: 6 (8 total including replicas)
- **Namespace**: dapr-system
- **Status**: All Healthy ✅

### PostgreSQL Database
- **Chart**: bitnami/postgresql v18.2.4
- **App Version**: 18.1.0
- **Deployment**: StatefulSet (1 replica)
- **Service**: postgresql.todo-app-dev.svc.cluster.local:5432
- **Database**: todoapp_db
- **User**: todoapp
- **Storage**: 5Gi Persistent Volume
- **Status**: Running, Ready ✅

### Apache Kafka
- **Operator**: Strimzi v1 (latest)
- **Kafka Version**: 4.0.1
- **Mode**: KRaft (no Zookeeper)
- **Deployment**: KafkaNodePool (1 broker)
- **Bootstrap Server**: todo-kafka-kafka-bootstrap.todo-app-dev.svc.cluster.local:9092
- **Listeners**:
  - Plain: port 9092 (internal, no TLS)
  - TLS: port 9093 (internal, TLS enabled)
- **Replication Factor**: 1 (development mode)
- **Storage**: 5Gi Persistent Volume
- **Entity Operators**: Topic Operator + User Operator (2/2 Running)
- **Status**: Ready ✅

### Kubernetes Secrets
| Secret Name | Purpose |
|-------------|---------|
| postgres-credentials | PostgreSQL connection string |
| jwt-signing-key | JWT token signing key |
| openai-api-key | OpenAI API credentials |

---

## Network Topology

```
External Access
       │
       ▼
┌─────────────────┐
│ Ingress-Nginx   │
│ Controller      │
└─────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│        todo-app-dev Namespace Services          │
├─────────────────────────────────────────────────┤
│                                                  │
│  PostgreSQL ◄──────┐                            │
│  :5432              │                            │
│                     │                            │
│  Kafka              │                            │
│  :9092 (plain)      ├─► (Future Microservices)  │
│  :9093 (tls)        │                            │
│                     │                            │
│  Secrets ◄──────────┘                            │
│                                                  │
└─────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────┐
│  Dapr Sidecars  │
│  (Future)       │
└─────────────────┘
```

---

## Phase V.0 Exit Criteria Status

✅ **All Exit Criteria Met**:

1. ✅ Minikube cluster running with kubectl access
2. ✅ Dapr runtime installed (6 control plane components healthy)
3. ✅ Kafka broker reachable (KRaft mode, Strimzi operator)
4. ✅ PostgreSQL deployed with successful test connection
5. ✅ Health check scripts validate all infrastructure
6. ✅ Namespace `todo-app-dev` active
7. ✅ All required secrets created (3/3)

---

## Known Considerations

⚠️ **Memory Allocation**: System allocated 7802MB (7.6GB) vs specified 8GB (5% below spec)
  - **Impact**: May experience memory pressure during peak operations
  - **Mitigation**: Monitor memory usage, scale down non-essential services if needed

✅ **Kafka Implementation Change**: Switched from Bitnami Kafka to Strimzi Kafka Operator
  - **Reason**: Bitnami images unavailable (subscription requirement)
  - **Alternative**: Strimzi is production-ready, Kubernetes-native, uses official Apache Kafka
  - **Compliance**: Meets all Phase V.0 requirements (KRaft mode, 1 broker, event streaming)

---

## Next Phase

**Phase V.1 - Event Backbone & Dapr Foundations**:
- Create 6 FastAPI microservices
- Configure Dapr State Store and Secrets components
- Deploy services with Dapr sidecars
- Implement smoke tests

**Ready for Human Approval Gate #1** 🛑
