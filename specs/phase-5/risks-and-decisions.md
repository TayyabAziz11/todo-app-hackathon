# Phase V: Risks and Architectural Decisions

**Feature Branch**: `005-name-phase5-cloud`
**Created**: 2026-02-06
**Status**: Draft

## Overview

This document catalogs all architectural decisions requiring ADRs and comprehensive risk analysis for Phase V implementation.

## Architectural Decision Records (ADRs) Required

### ADR-001: Event-Driven Architecture with Apache Kafka

**Decision**: Use Apache Kafka as the primary event bus for async communication between microservices.

**Context**:
- Need reliable event streaming for 6 microservices
- Require event replay capability for debugging and recovery
- Must support high throughput (1000+ events/second)
- Need persistent event log for audit trail

**Alternatives Considered**:
1. **RabbitMQ**: Mature AMQP broker, simpler than Kafka
   - ❌ No native event replay (messages deleted after consumption)
   - ❌ Lower throughput than Kafka
   - ✅ Easier to operate
   - ✅ Better for low-latency messaging

2. **AWS SQS/SNS**: Managed cloud service
   - ❌ Vendor lock-in (cannot run locally or on DOKS)
   - ❌ Higher cost at scale
   - ✅ Zero operational overhead
   - ✅ Excellent reliability

3. **NATS JetStream**: Cloud-native messaging
   - ❌ Smaller ecosystem than Kafka
   - ❌ Less Dapr maturity
   - ✅ Very fast, lightweight
   - ✅ Built-in persistence

**Decision Rationale**:
- Kafka selected for **event replay** capability (critical for debugging)
- **Dapr Pub/Sub** has first-class Kafka support (Context7-verified)
- **Local development** parity (Kafka runs in Minikube)
- **Industry standard** for event-driven microservices

**Tradeoffs Accepted**:
- ❌ **Operational complexity**: Kafka requires careful tuning (partitions, replication, retention)
- ❌ **Learning curve**: Developers must understand Kafka semantics (offsets, consumer groups)
- ✅ **Mitigation**: Use managed Kafka (Confluent Cloud) or simplified KRaft mode (no Zookeeper)

**Consequences**:
- All services must implement idempotent event handlers
- Events must follow CloudEvents specification
- Dead letter queue required for failed events
- Monitoring Kafka lag becomes critical operational metric

---

### ADR-002: Microservices Decomposition (6 Services)

**Decision**: Decompose application into 6 microservices: Todo, User, Chat, Notification, Audit, Analytics.

**Context**:
- Current Phase IV has 3 components: backend (FastAPI), frontend (Next.js), database (PostgreSQL)
- Phase V requires event-driven architecture and independent scaling
- Need clear bounded contexts for domain-driven design

**Alternatives Considered**:
1. **Monolith** (single FastAPI app):
   - ✅ Simpler deployment, no network overhead
   - ❌ Cannot scale components independently
   - ❌ Tight coupling, harder to maintain

2. **3 Services** (Todo+User+Chat, Notification+Audit+Analytics):
   - ✅ Less operational complexity than 6 services
   - ❌ Blurs bounded contexts
   - ❌ Still requires service mesh

3. **12+ Services** (fine-grained, e.g., separate TagService, RecurrenceService):
   - ❌ Over-engineered for current scale
   - ❌ Network chattiness
   - ❌ Coordination overhead

**Decision Rationale**:
- **6 services** strike balance between granularity and manageability
- Each service has clear **single responsibility**:
  - Todo: Task management
  - User: Identity and preferences
  - Chat: AI interactions
  - Notification: Reminders and alerts
  - Audit: Compliance logging
  - Analytics: Insights and metrics
- Each service can scale independently (e.g., Chat service scales more than Audit)

**Tradeoffs Accepted**:
- ❌ **Network latency**: Cross-service calls add 5-20ms per hop
- ❌ **Distributed transactions**: Eventual consistency required (Saga pattern)
- ✅ **Mitigation**: Use Dapr Service Invocation (built-in retries, tracing)

**Consequences**:
- Each service owns its database (database-per-service pattern)
- Cross-service queries require event-driven views or API composition
- Deployment complexity increases (Helm charts, K8s manifests)

---

### ADR-003: Database-per-Service Pattern

**Decision**: Each service has its own PostgreSQL database (logical separation within same PostgreSQL cluster).

**Context**:
- Microservices must be independently deployable
- Avoid tight coupling through shared database
- Enable service-level data ownership

**Alternatives Considered**:
1. **Shared Database** (all services write to same schema):
   - ✅ Simple joins, no distributed queries
   - ❌ Tight coupling (schema changes affect all services)
   - ❌ Violates microservices principles

2. **Polyglot Persistence** (PostgreSQL for Todo, MongoDB for Chat, etc.):
   - ✅ Optimal DB per use case
   - ❌ Operational complexity (multiple DB clusters)
   - ❌ Learning curve for developers

3. **Shared PostgreSQL, Separate Databases**:
   - ✅ Single PostgreSQL cluster, lower cost
   - ✅ Logical isolation (DB permissions)
   - ✅ Easier backups (single cluster)
   - ❌ Still shares infrastructure (but acceptable tradeoff)

**Decision Rationale**:
- **Separate databases** (todo_db, user_db, chat_db, etc.) within single PostgreSQL cluster
- Dapr State Store provides abstraction (can swap to DynamoDB later)
- Balance between isolation and operational simplicity

**Tradeoffs Accepted**:
- ❌ **No joins**: Cross-service queries require API calls or event-driven views
- ❌ **Data duplication**: User name may be stored in multiple services
- ✅ **Mitigation**: Use events to propagate changes (eventual consistency)

**Consequences**:
- Each service manages its own migrations (Alembic per service)
- Backup strategy must cover all databases
- Monitoring per-database metrics (query performance, connections)

---

### ADR-004: Dapr as Service Mesh Alternative

**Decision**: Use Dapr for service-to-service communication instead of full service mesh (Istio/Linkerd).

**Context**:
- Need service discovery, retries, circuit breaking, observability
- Traditional service meshes (Istio) have steep learning curve and resource overhead

**Alternatives Considered**:
1. **Istio**: Full-featured service mesh
   - ✅ Mature, production-proven
   - ❌ High resource overhead (sidecar per pod)
   - ❌ Complex configuration (VirtualServices, DestinationRules)
   - ❌ Overkill for 6 services

2. **Linkerd**: Lightweight service mesh
   - ✅ Simpler than Istio, lower resource usage
   - ❌ Still adds operational complexity
   - ❌ Less Dapr-compatible than direct approach

3. **No Mesh**: Direct HTTP/gRPC calls
   - ✅ Simplest approach
   - ❌ Manual retries, no observability
   - ❌ No mTLS without additional work

**Decision Rationale**:
- **Dapr provides 80% of service mesh benefits** at 20% complexity
- Built-in: service discovery, retries, circuit breaking, mTLS, tracing
- **Polyglot support**: Works with any language (not just Envoy-compatible)
- **Portable**: Same APIs work on Kubernetes, VMs, edge devices

**Tradeoffs Accepted**:
- ❌ **Less traffic control**: No advanced routing (canary, A/B testing) compared to Istio
- ❌ **Dapr dependency**: Vendor lock-in (but open-source, CNCF sandbox project)
- ✅ **Mitigation**: Use Dapr resiliency policies for retries/timeouts

**Consequences**:
- All services must integrate Dapr SDK
- Sidecar pattern: each pod has 2 containers (app + daprd)
- Dapr components (state, pub/sub, secrets) must be configured

---

### ADR-005: Multi-Environment Strategy (Minikube + DOKS)

**Decision**: Support both local Minikube and cloud DOKS for development and production.

**Context**:
- Developers need local environment for fast iteration
- Production requires cloud deployment for demos and testing
- Cost constraint: cannot run cloud 24/7 during development

**Alternatives Considered**:
1. **Cloud-only** (always deploy to DOKS):
   - ✅ Production parity (no "works on my machine")
   - ❌ Expensive ($72/month minimum)
   - ❌ Slow feedback loop (5-10 min deployments)

2. **Docker Compose** for local, Kubernetes for prod:
   - ✅ Fast local development
   - ❌ Dev/prod parity broken (Dapr works differently)
   - ❌ Two deployment configurations to maintain

3. **Minikube for dev, DOKS for prod** (chosen):
   - ✅ Kubernetes parity (same manifests)
   - ✅ Dapr works identically
   - ✅ Cost-effective (only pay for prod)
   - ❌ Minikube requires resources (4 CPU, 8GB RAM)

**Decision Rationale**:
- **Minikube** provides 95% production parity at $0 cost
- Helm values files differentiate environments (`values-minikube.yaml` vs `values-prod.yaml`)
- Developers can test full stack locally before pushing

**Tradeoffs Accepted**:
- ❌ **Resource requirements**: Developers need capable machines
- ❌ **Configuration drift**: Must keep Minikube and DOKS configs in sync
- ✅ **Mitigation**: Use Helm templates, single source of truth

**Consequences**:
- CI/CD pipeline must support both environments
- Documentation must cover both deployment procedures
- Testing strategy: unit tests locally, E2E tests in DOKS

---

## Risk Analysis

### Risk Matrix

| Risk | Probability | Impact | Severity | Mitigation Priority |
|------|-------------|--------|----------|---------------------|
| Kafka operational complexity | High | High | **Critical** | P0 |
| Distributed tracing overhead | Medium | Medium | **High** | P1 |
| Cost overrun (cloud infra) | High | High | **Critical** | P0 |
| Learning curve (Dapr+Kafka+K8s) | High | High | **Critical** | P0 |
| Database migration failures | Medium | High | **High** | P1 |
| Event schema evolution breaking changes | Medium | Medium | **Medium** | P2 |
| Network latency in microservices | Low | Medium | **Low** | P3 |

---

### Risk 1: Kafka Operational Complexity (Critical)

**Description**: Apache Kafka is notoriously difficult to operate, requiring expertise in partitions, replication, consumer groups, and offset management. Misconfiguration can lead to data loss or processing delays.

**Probability**: High (80%)
- Team has limited Kafka experience
- Kafka tuning is complex (100+ configuration parameters)

**Impact**: High
- Events not processed → features broken (reminders, notifications)
- Kafka downtime → system partially unavailable
- Debugging Kafka issues time-consuming

**Mitigation Strategies**:

1. **Use Managed Kafka** (Priority: P0)
   - **Option A**: Confluent Cloud (fully managed)
     - Cost: ~$100/month for small cluster
     - Benefit: Zero operational overhead, auto-scaling, monitoring
   - **Option B**: DigitalOcean Managed Kafka (when available)
   - **Fallback**: Self-hosted Kafka in KRaft mode (no Zookeeper, simpler)

2. **Start Simple** (Priority: P0)
   - **Minikube**: Single Kafka broker, single partition per topic
   - **DOKS**: 3 brokers, 3 partitions, replication factor 2 (minimum HA)
   - **Production**: Increase only when bottlenecks identified

3. **Dapr Abstraction** (Priority: P1)
   - Use Dapr Pub/Sub API (hides Kafka complexity)
   - Can swap Kafka for RabbitMQ without code changes (escape hatch)

4. **Extensive Monitoring** (Priority: P1)
   - Alert on consumer lag > 10,000 messages
   - Dashboard: producer throughput, consumer offset, broker health
   - Runbooks for common issues (broker down, rebalancing)

**Contingency Plan**:
If Kafka proves too complex, **fallback to Dapr in-memory Pub/Sub** for Minikube and **RabbitMQ** for DOKS (Dapr supports both without code changes).

---

### Risk 2: Distributed Tracing Overhead (High)

**Description**: Distributed tracing (Dapr + OpenTelemetry + Jaeger) adds latency and resource overhead. Misconfigured sampling can generate excessive data or miss critical traces.

**Probability**: Medium (50%)
- Tracing works in development but causes issues at scale

**Impact**: Medium
- Increased response time (5-10ms per hop)
- Jaeger storage costs (Elasticsearch)
- Developer confusion (too many spans)

**Mitigation Strategies**:

1. **Adaptive Sampling** (Priority: P0)
   - **Development**: 100% sampling (debug everything)
   - **Production**: 1% sampling (reduce overhead)
   - **Errors**: Always sample failed requests (override sampling)

2. **Jaeger Storage Optimization** (Priority: P1)
   - Use Elasticsearch with short retention (7 days hot, 30 days cold)
   - OR use Jaeger in-memory backend for development only

3. **Performance Budget** (Priority: P1)
   - Target: <5ms tracing overhead (measure with load tests)
   - If exceeded, reduce sampling or disable tracing for health checks

**Contingency Plan**:
If tracing overhead unacceptable, **disable distributed tracing** and rely on **structured logging with correlation IDs** (manual trace reconstruction).

---

### Risk 3: Cost Overrun (Critical)

**Description**: Cloud infrastructure costs (DOKS cluster, Load Balancer, managed databases) can exceed budget, especially during extended development.

**Probability**: High (70%)
- Forgetting to tear down clusters after use
- Over-provisioning resources

**Impact**: High
- Burn through $200 DigitalOcean credit quickly
- Project becomes financially unsustainable

**Mitigation Strategies**:

1. **Cost Monitoring** (Priority: P0)
   - Set up DigitalOcean billing alerts: $50, $100, $150
   - Daily cost review (https://cloud.digitalocean.com/account/billing)
   - Track spending in project log

2. **Auto-Shutdown Policies** (Priority: P0)
   - **Rule**: Tear down DOKS cluster every night (automate with cron)
   - **Budget-K8s skill**: Use teardown script after demos
   - **Cost**: 8-hour workday = $2.40/day (vs $72/month if left running)

3. **Resource Right-Sizing** (Priority: P1)
   - Start with **s-2vcpu-4gb** nodes (not s-4vcpu-8gb)
   - Use 2 nodes (not 3) for dev/test environments
   - Scale up only when performance issues identified

4. **Minikube First** (Priority: P0)
   - Do 80% of development on Minikube (free)
   - Deploy to DOKS only for:
     - Demos to stakeholders
     - Performance testing
     - Production-like integration tests

**Contingency Plan**:
If budget exhausted, **pause Phase V cloud deployment** and complete remaining work on Minikube only. Document cloud deployment procedures without executing.

---

### Risk 4: Learning Curve (Critical)

**Description**: Phase V introduces 3 new technologies simultaneously (Dapr, Kafka, Kubernetes), creating steep learning curve that delays implementation.

**Probability**: High (80%)
- Team has limited experience with all three
- Documentation spread across multiple sources

**Impact**: High
- Timeline slips 2-4 weeks
- Developer frustration, burnout
- Suboptimal implementations (technical debt)

**Mitigation Strategies**:

1. **Incremental Learning** (Priority: P0)
   - **Week 1**: Dapr only (State Management, Service Invocation)
   - **Week 2**: Add Kafka (Pub/Sub)
   - **Week 3**: Add Kubernetes (Minikube)
   - **Week 4**: Add DOKS (cloud deployment)

2. **Context7 Verification** (Priority: P0)
   - Verify ALL commands/configurations against official docs via Context7
   - Never guess—always query Context7 for authoritative answers

3. **Skills as Training Modules** (Priority: P1)
   - **Budget-K8s skill**: Learn doctl and DOKS
   - **Dapr skill**: Learn building blocks and components
   - **Apache Kafka skill** (create if needed): Learn Kafka fundamentals

4. **Pair Programming** (Priority: P1)
   - Rotate knowledge: Person A learns Dapr, teaches Person B
   - Code reviews catch misunderstandings early

**Contingency Plan**:
If learning curve too steep, **simplify architecture**:
- Reduce to 3 services (combine microservices)
- Use synchronous REST (skip Kafka)
- Use Docker Compose (skip Kubernetes)

---

### Risk 5: Database Migration Failures (High)

**Description**: Backward-incompatible schema changes during microservices migration cause data corruption or service downtime.

**Probability**: Medium (40%)
- Schema changes are tricky with zero-downtime deployments

**Impact**: High
- Data loss or corruption
- Rollback required (downtime)

**Mitigation Strategies**:

1. **Expand-Contract Pattern** (Priority: P0)
   - **Phase 1 (Expand)**: Add new columns/tables alongside old schema
   - **Phase 2 (Migrate)**: Dual-write to old and new schema
   - **Phase 3 (Contract)**: Remove old schema once all services migrated

2. **Database Backups** (Priority: P0)
   - **Before every migration**: Take full PostgreSQL backup
   - **Retention**: 7-day retention policy
   - **Test restores**: Weekly restore drills

3. **Blue-Green Deployment** (Priority: P1)
   - Run old and new services simultaneously
   - Switch traffic only after validation
   - Rollback = switch back to blue environment

4. **Migration Testing** (Priority: P1)
   - Test migrations on Minikube with production-like data
   - Run migrations in staging DOKS before production

**Contingency Plan**:
If migration fails, **restore from backup** and **rollback deployment**. Accept downtime (acceptable for development project).

---

## Open Questions for ADRs

These questions require clarification before finalizing ADRs:

1. **Event Schema Evolution** (ADR-006 candidate):
   - How to handle breaking changes in event schemas?
   - Use schema registry (Confluent Schema Registry, Apicurio)?
   - **Decision needed by**: Week 2 (before implementing events)

2. **Multi-Tenancy** (ADR-007 candidate):
   - Is Phase V single-tenant or multi-tenant?
   - **Current assumption**: Single-tenant (one user per deployment)
   - **Decision needed by**: Week 1 (affects database design)

3. **API Gateway** (ADR-008 candidate):
   - Use dedicated API Gateway (Kong, Ambassador, AWS API Gateway)?
   - OR rely on Kubernetes Ingress + Dapr?
   - **Current assumption**: Kubernetes Ingress is sufficient
   - **Decision needed by**: Week 3 (before DOKS deployment)

4. **Secrets Rotation** (ADR-009 candidate):
   - How often to rotate PostgreSQL passwords, JWT keys?
   - Manual or automated rotation?
   - **Decision needed by**: Week 4 (before production deployment)

---

## Success Criteria for Risk Mitigation

Phase V risks are considered **acceptable** if:

1. ✅ Kafka consumer lag < 10,000 messages (p95)
2. ✅ Distributed tracing overhead < 5ms per request (p95)
3. ✅ Cloud infrastructure cost < $150/month
4. ✅ All developers complete Dapr+Kafka+K8s training within 2 weeks
5. ✅ Zero database migration failures (validated in staging)
6. ✅ Event schema changes backward-compatible (validated with schema registry)
7. ✅ Rollback procedures tested and documented

---

## References

- [Architectural Decision Records (ADR)](https://adr.github.io/)
- [Risk Management in Software Projects](https://www.pmi.org/learning/library/risk-management-software-projects-5706)
- [Microservices Patterns by Chris Richardson](https://microservices.io/patterns/)

---

**Next Steps:**
1. Create formal ADR documents for ADR-001 through ADR-005
2. Document risk mitigation progress weekly
3. Review open questions with stakeholders
4. Update risk register after each sprint
