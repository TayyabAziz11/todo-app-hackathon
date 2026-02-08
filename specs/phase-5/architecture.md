# Phase V: Architecture Specification

**Feature Branch**: `005-name-phase5-cloud`
**Created**: 2026-02-06
**Status**: Draft

## Overview

Phase V transforms the Todo AI Chatbot into a cloud-native, event-driven microservices application with full Dapr integration, Apache Kafka for event streaming, and multi-environment deployment capabilities (Minikube + Cloud).

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway                              │
│                    (Dapr Ingress / Envoy)                       │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│ Todo Service │ │ User Service│ │Chat Service│
│  (FastAPI)   │ │  (FastAPI)  │ │  (FastAPI) │
└──────┬───────┘ └──────┬──────┘ └──────┬─────┘
       │                │               │
       │  ┌─────────────┴───────────────┤
       │  │          Dapr Sidecar        │
       │  │  ┌──────────────────────┐   │
       │  │  │  State Management    │   │
       │  │  │  Pub/Sub             │   │
       │  │  │  Service Invocation  │   │
       │  │  │  Secrets             │   │
       │  │  │  Bindings            │   │
       │  │  └──────────────────────┘   │
       │  └──────────────┬───────────────┘
       │                 │
┌──────▼─────────────────▼──────────────────────┐
│         Apache Kafka (Event Bus)              │
│  Topics: todo.created, todo.updated,          │
│          todo.deleted, user.events            │
└───────────────────┬───────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼────────┐ ┌───▼────────┐ ┌───▼────────┐
│ Notification│ │  Audit     │ │  Analytics │
│  Service    │ │  Service   │ │  Service   │
│  (FastAPI)  │ │ (FastAPI)  │ │ (FastAPI)  │
└─────────────┘ └────────────┘ └────────────┘

┌─────────────────────────────────────────────┐
│         PostgreSQL Cluster                  │
│  - Todo DB (via Dapr State Store)           │
│  - User DB (via Dapr State Store)           │
│  - Audit DB (via Dapr State Store)          │
└─────────────────────────────────────────────┘
```

### Microservices Architecture

**Service Decomposition Principles:**
1. Each service owns its data (Database per Service pattern)
2. Services communicate via events (Kafka) for async operations
3. Services communicate via Dapr Service Invocation for sync operations
4. All external communication goes through API Gateway
5. Each service is independently deployable and scalable

**Core Services:**

1. **Todo Service**
   - Responsibilities: CRUD operations for todos, priority management, tags, search
   - State: Todo entities with metadata (created_at, updated_at, completed_at)
   - Events Published: todo.created, todo.updated, todo.completed, todo.deleted
   - Events Consumed: user.deleted (for cascade deletion)

2. **User Service**
   - Responsibilities: User authentication, profile management, preferences
   - State: User profiles, authentication tokens, preferences
   - Events Published: user.created, user.updated, user.deleted
   - Events Consumed: None (root aggregate)

3. **Chat Service**
   - Responsibilities: AI chatbot interactions, conversation management, MCP tool orchestration
   - State: Conversation history, user context
   - Events Published: chat.message.sent, chat.action.completed
   - Events Consumed: todo.* (to update chat context)

4. **Notification Service**
   - Responsibilities: Send reminders, alerts, digests via email/push
   - State: Notification queue, delivery status
   - Events Published: notification.sent, notification.failed
   - Events Consumed: todo.reminder.due, todo.completed, user.settings.updated

5. **Audit Service**
   - Responsibilities: Immutable audit log for compliance and debugging
   - State: Event sourcing log (all domain events)
   - Events Published: None (sink service)
   - Events Consumed: *.* (all events)

6. **Analytics Service**
   - Responsibilities: User behavior analytics, usage patterns, performance metrics
   - State: Aggregated metrics, time-series data
   - Events Published: analytics.report.generated
   - Events Consumed: todo.*, user.*, chat.*

### Event-Driven Architecture with Apache Kafka

**Event Bus Topology:**

```
Kafka Cluster (3 brokers)
├── todo.created (partitions: 3, replication: 2)
├── todo.updated (partitions: 3, replication: 2)
├── todo.completed (partitions: 3, replication: 2)
├── todo.deleted (partitions: 3, replication: 2)
├── todo.reminder.due (partitions: 3, replication: 2)
├── user.created (partitions: 1, replication: 2)
├── user.updated (partitions: 1, replication: 2)
├── user.deleted (partitions: 1, replication: 2)
├── chat.message.sent (partitions: 3, replication: 2)
└── notification.* (partitions: 2, replication: 2)
```

**Event Schema Standards:**
- CloudEvents specification compliance
- JSON Schema validation at producer and consumer
- Backward compatibility guaranteed via schema registry
- Event versioning: v1, v2, etc. (embedded in event type)

**Event Ordering Guarantees:**
- Todo events partitioned by `todo_id` (per-todo ordering)
- User events partitioned by `user_id` (per-user ordering)
- Global ordering NOT guaranteed (by design for scalability)

**Idempotency Strategy:**
- All event consumers implement idempotency using `event_id` deduplication
- Each service maintains processed event IDs (windowed, 7-day retention)
- Exactly-once semantics via Kafka transactions + consumer offset management

### Dapr Integration Architecture

**Dapr Building Blocks Used:**

1. **State Management**
   - Component: `statestore.postgresql`
   - Backing Store: PostgreSQL with optimistic concurrency control
   - Features: TTL, transactions, bulk operations
   - Usage: All persistent entity storage

2. **Pub/Sub**
   - Component: `pubsub.kafka`
   - Backing Broker: Apache Kafka
   - Features: Topic routing, dead letter queues, message TTL
   - Usage: All event publishing and subscription

3. **Service Invocation**
   - Protocol: gRPC (service-to-service), HTTP (API Gateway)
   - Features: Service discovery, retries, circuit breaking, observability
   - Usage: Synchronous inter-service calls

4. **Secrets Management**
   - Component: `secretstore.kubernetes` (Minikube), `secretstore.aws` (Cloud)
   - Features: Secret rotation, versioning, access control
   - Usage: Database credentials, API keys, encryption keys

5. **Bindings (Input/Output)**
   - Input Bindings: Kafka consumer binding (alternative to Pub/Sub)
   - Output Bindings: Email (SMTP), SMS (Twilio), Slack webhooks
   - Usage: External system integrations

6. **Actors** (Future Phase)
   - Not implemented in Phase V (reserved for Phase VI)
   - Planned Usage: Stateful recurring task scheduling

**Dapr Component Configuration Pattern:**

Each service has a dedicated `components/` directory with YAML configurations:
```
components/
├── statestore-todo.yaml
├── pubsub-kafka.yaml
├── secretstore-k8s.yaml
├── binding-email.yaml
└── subscription-todo.yaml
```

**Dapr Sidecar Injection:**
- Kubernetes: Automatic injection via annotations
- Local Development: Manual sidecar start via `dapr run`

### Deployment Architecture

**Multi-Environment Strategy:**

1. **Local Development (Minikube)**
   - Single-node Kubernetes cluster
   - Local Kafka (KRaft mode, no Zookeeper)
   - Local PostgreSQL (single instance)
   - Dapr in self-hosted mode
   - Port-forwarding for API access

2. **Cloud Production (DigitalOcean Kubernetes)**
   - Multi-node DOKS cluster (3+ nodes)
   - Managed Kafka (Confluent Cloud or self-hosted on K8s)
   - Managed PostgreSQL (DigitalOcean Managed Database)
   - Dapr in Kubernetes mode with mTLS
   - Load Balancer + Ingress Controller

**Kubernetes Resource Topology:**

```
Namespace: todo-app-prod
├── Deployments
│   ├── todo-service (replicas: 3, Dapr sidecar)
│   ├── user-service (replicas: 2, Dapr sidecar)
│   ├── chat-service (replicas: 3, Dapr sidecar)
│   ├── notification-service (replicas: 2, Dapr sidecar)
│   ├── audit-service (replicas: 1, Dapr sidecar)
│   └── analytics-service (replicas: 1, Dapr sidecar)
├── Services (ClusterIP)
│   ├── todo-service-svc
│   ├── user-service-svc
│   └── ... (one per deployment)
├── ConfigMaps
│   ├── app-config
│   ├── dapr-config
│   └── kafka-config
├── Secrets
│   ├── postgres-credentials
│   ├── kafka-credentials
│   └── jwt-signing-key
├── Ingress
│   └── api-gateway-ingress (routes to services via Dapr)
├── StatefulSets
│   ├── kafka (3 replicas) [if self-hosted]
│   └── postgresql (1 primary + 2 replicas) [if self-hosted]
└── PersistentVolumeClaims
    ├── kafka-data-0, kafka-data-1, kafka-data-2
    └── postgres-data
```

**Helm Chart Structure:**
```
helm/todo-app/
├── Chart.yaml
├── values.yaml
├── values-minikube.yaml
├── values-prod.yaml
├── templates/
│   ├── services/
│   │   ├── todo-service.yaml
│   │   ├── user-service.yaml
│   │   └── ... (one per service)
│   ├── dapr/
│   │   ├── components.yaml
│   │   └── configuration.yaml
│   ├── kafka/
│   │   ├── statefulset.yaml (optional)
│   │   └── service.yaml
│   └── ingress.yaml
└── README.md
```

### Data Architecture

**Database-per-Service Pattern:**

1. **Todo Database** (owned by Todo Service)
   - Tables: todos, tags, todo_tags (many-to-many)
   - Indexes: user_id, status, priority, due_date, tags
   - Retention: Soft delete with 90-day hard delete policy

2. **User Database** (owned by User Service)
   - Tables: users, user_preferences, sessions
   - Indexes: email (unique), created_at
   - Retention: GDPR-compliant (user data deletion on request)

3. **Chat Database** (owned by Chat Service)
   - Tables: conversations, messages
   - Indexes: user_id, conversation_id, created_at
   - Retention: 30-day conversation history

4. **Audit Database** (owned by Audit Service)
   - Tables: events (event sourcing log)
   - Indexes: entity_id, event_type, timestamp
   - Retention: 7-year retention for compliance

5. **Analytics Database** (owned by Analytics Service)
   - Tables: user_metrics, todo_metrics, time_series
   - Indexes: metric_name, timestamp
   - Retention: 1-year hot storage, 5-year cold storage

**Consistency Model:**
- **Strong Consistency**: Within service boundaries (PostgreSQL ACID transactions)
- **Eventual Consistency**: Across service boundaries (event-driven propagation)
- **Conflict Resolution**: Last-write-wins with version vectors (Dapr ETag support)

**Data Migration Strategy:**
- Each service owns its database migrations (Alembic for FastAPI)
- Backward-compatible schema changes (expand-contract pattern)
- Zero-downtime deployments via blue-green or rolling updates

### Security Architecture

**Authentication & Authorization:**
- OAuth2 + JWT tokens (Better Auth frontend → User Service)
- Service-to-service: Dapr mTLS (mutual TLS via Dapr sidecar)
- API Gateway: JWT validation before routing

**Secrets Management:**
- Kubernetes Secrets (encrypted at rest)
- Dapr Secrets API (abstraction layer)
- Secret rotation: 90-day policy (automated via external-secrets operator)

**Network Security:**
- Network Policies: Deny-all by default, explicit allow rules
- Service Mesh (Future): Istio or Linkerd for zero-trust networking
- Egress Control: Only whitelisted external domains

**Data Security:**
- Encryption at Rest: PostgreSQL transparent data encryption
- Encryption in Transit: TLS 1.3 for all HTTP traffic, mTLS for Dapr
- PII Handling: Hashed user emails, encrypted sensitive fields

### Observability Architecture

**Logging:**
- Structured JSON logs (logrus/structlog)
- Centralized logging: Fluentd → Elasticsearch → Kibana (EFK stack)
- Log Levels: DEBUG (local), INFO (prod), ERROR (alerts)

**Metrics:**
- Prometheus scraping (Dapr metrics + custom application metrics)
- Grafana dashboards: Service health, latency, throughput, error rates
- Alerting: Prometheus Alertmanager → Slack/PagerDuty

**Tracing:**
- Distributed tracing: Dapr + OpenTelemetry → Jaeger
- Trace context propagation: W3C Trace Context standard
- Sampling: 1% in production, 100% in development

**Health Checks:**
- Kubernetes Liveness Probes: `/health/live` (process alive)
- Kubernetes Readiness Probes: `/health/ready` (dependencies healthy)
- Startup Probes: `/health/startup` (initialization complete)

### Resilience Patterns

**Circuit Breaking:**
- Dapr Resiliency Policies: Circuit breaker on service invocation
- Thresholds: 50% error rate, 10-second window, 30-second cooldown

**Retries:**
- Exponential backoff: 1s, 2s, 4s, 8s (max 4 retries)
- Idempotency: All APIs and event handlers are idempotent

**Timeouts:**
- Service Invocation: 5-second timeout (configurable per service)
- Database Queries: 10-second timeout
- Kafka Consumer: 30-second max.poll.interval

**Rate Limiting:**
- API Gateway: 100 requests/minute per user (sliding window)
- Service-level: 1000 requests/minute per service (token bucket)

**Bulkheading:**
- Separate thread pools for sync vs. async operations
- Separate Kafka consumer groups per service

**Graceful Degradation:**
- Chat Service: Fallback to synchronous todo operations if Kafka is down
- Notification Service: Store-and-forward pattern (retry queue)

## Technology Stack (Context7-Verified)

**Core Runtime:**
- Python 3.11+ (FastAPI services)
- Dapr 1.12+ (sidecar runtime)
- Apache Kafka 3.6+ (event streaming)

**Infrastructure:**
- Kubernetes 1.28+ (orchestration)
- PostgreSQL 15+ (state storage)
- Helm 3.13+ (package management)

**Development Tools:**
- Minikube (local Kubernetes)
- kubectl (cluster management)
- dapr CLI (local development)
- kafkacat/kcat (Kafka debugging)

**Deployment Targets:**
- Local: Minikube on developer machine
- Cloud: DigitalOcean Kubernetes (DOKS)

## Non-Functional Requirements

**Performance:**
- API Latency: p95 < 200ms, p99 < 500ms
- Event Processing: < 1-second end-to-end latency
- Throughput: 1000 requests/second per service

**Scalability:**
- Horizontal scaling: All services must be stateless (state in Dapr)
- Kafka partitions: Scale to 10 partitions per topic
- Database: Read replicas for analytics queries

**Availability:**
- Target: 99.9% uptime (8.76 hours downtime/year)
- Zero-downtime deployments: Rolling updates with readiness probes
- Multi-AZ deployment (cloud production)

**Disaster Recovery:**
- RPO (Recovery Point Objective): 1 hour (hourly database backups)
- RTO (Recovery Time Objective): 4 hours (restore from backup)
- Kafka retention: 7 days (replay events if needed)

## Architecture Decision Records (ADRs)

The following architectural decisions require ADRs:

1. **ADR-001: Event-Driven Architecture with Kafka**
   - Decision: Use Apache Kafka for event streaming
   - Alternatives: RabbitMQ, AWS SQS, NATS
   - Rationale: High throughput, persistence, replay capability, Dapr Pub/Sub support

2. **ADR-002: Microservices Decomposition**
   - Decision: 6 microservices (Todo, User, Chat, Notification, Audit, Analytics)
   - Alternatives: Monolith, 3 services (Todo+User+Chat), 12 services (finer-grained)
   - Rationale: Balance between complexity and maintainability, clear bounded contexts

3. **ADR-003: Database-per-Service Pattern**
   - Decision: Separate PostgreSQL database per service
   - Alternatives: Shared database, NoSQL (MongoDB, Cassandra)
   - Rationale: Service autonomy, independent scaling, Dapr State Store compatibility

4. **ADR-004: Dapr as Service Mesh**
   - Decision: Use Dapr for service-to-service communication
   - Alternatives: Istio, Linkerd, raw gRPC/HTTP
   - Rationale: Polyglot support, built-in observability, simplified deployment

5. **ADR-005: Multi-Environment Deployment (Minikube + Cloud)**
   - Decision: Support both local Minikube and cloud DOKS
   - Alternatives: Cloud-only, Docker Compose for local
   - Rationale: Developer experience, production parity, cost-effective learning

## Out of Scope

The following are explicitly OUT OF SCOPE for Phase V:

1. **Multi-tenancy**: Single-tenant application (one user per deployment)
2. **GraphQL API**: REST-only (GraphQL deferred to Phase VI)
3. **Real-time WebSockets**: Polling-based updates (WebSockets in Phase VI)
4. **Advanced ML Features**: No recommendation engine (Phase VI+)
5. **Mobile Apps**: Web-only (React frontend from Phase II)
6. **Multi-region Deployment**: Single-region deployment only

## Risk Analysis

**Top Risks:**

1. **Kafka Operational Complexity** (High)
   - Mitigation: Use managed Kafka (Confluent Cloud) or simplified self-hosted (KRaft mode)
   - Fallback: Dapr Pub/Sub with in-memory provider for local development

2. **Distributed Tracing Overhead** (Medium)
   - Mitigation: 1% sampling in production, disable in dev if performance issues
   - Fallback: Structured logging with correlation IDs

3. **Database Migration Coordination** (Medium)
   - Mitigation: Backward-compatible schema changes, feature flags for gradual rollout
   - Fallback: Blue-green deployments with rollback capability

4. **Cost Overrun (Cloud Infrastructure)** (High)
   - Mitigation: Use DigitalOcean $200 credit, monitor spending daily, auto-shutdown policies
   - Fallback: Minikube-only development, delay cloud deployment

5. **Learning Curve (Dapr + Kafka + K8s)** (High)
   - Mitigation: Incremental learning (Dapr first, Kafka second, K8s last), extensive documentation
   - Fallback: Simplify to 3 services, synchronous communication, Docker Compose

## References

- [Dapr Documentation](https://docs.dapr.io/) (Context7-verified)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/) (Context7-verified)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/) (Context7-verified)
- [Microservices Patterns by Chris Richardson](https://microservices.io/patterns/) (Industry standard)
- [CloudEvents Specification](https://cloudevents.io/) (Event schema standard)

---

**Next Steps:**
1. Review this architecture with stakeholders
2. Document detailed event schemas in `events.md`
3. Define Dapr component configurations in `dapr.md`
4. Create service API specifications in `services.md`
5. Plan deployment procedures in `deployment.md`
