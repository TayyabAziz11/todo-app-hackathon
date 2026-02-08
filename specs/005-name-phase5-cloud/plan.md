# Phase V: Advanced Cloud Deployment - Implementation Plan

**Feature Branch**: `005-name-phase5-cloud`
**Created**: 2026-02-06
**Status**: Draft - Ready for Review
**Plan Version**: 1.0.0

---

## Executive Summary

This implementation plan provides a **conservative, incremental, low-risk strategy** for implementing Phase V: Advanced Cloud Deployment. The plan strictly adheres to approved specifications in `/specs/phase-5/` and introduces **zero new scope**.

**Key Principles**:
- ✅ Spec-driven: Every implementation decision traces back to approved specifications
- ✅ Incremental: Each stage builds on previous stages with explicit rollback points
- ✅ Risk-controlled: High-risk steps have guardrails and validation checkpoints
- ✅ Skills-based: Implementation uses Claude Code skills, not autonomous agents
- ✅ Human-gated: Major phase transitions require explicit human approval

**Estimated Effort**: High complexity, 6-8 weeks of implementation (qualitative estimate)

---

## 1. Phase V Breakdown (Macro-Level)

### Phase V.0 — Infrastructure & Runtime Enablement

**Purpose**: Establish foundational infrastructure (Minikube, Dapr runtime, Kafka) and validate deployment pipeline before any service implementation.

**Entry Criteria**:
- ✅ Phase V specifications approved (`/specs/phase-5/`)
- ✅ This implementation plan reviewed and approved
- ✅ Development machine meets prerequisites (4 CPU, 8GB RAM, Docker, Minikube)

**Exit Criteria**:
- ✅ Minikube cluster running with 3 worker nodes
- ✅ Dapr runtime installed and verified (`dapr status -k`)
- ✅ Kafka (KRaft mode, 1 broker) deployed and reachable
- ✅ PostgreSQL deployed with test connection successful
- ✅ Helm 3 installed and configured
- ✅ All Context7-verified commands documented and tested
- ✅ Health check scripts validate infrastructure readiness

**Dependencies**: None (foundation stage)

**Skills Used**:
- `budget-k8s` (not for Minikube, but for doctl CLI familiarity)
- `dapr` (Dapr initialization and component setup)
- Custom Kafka skill (if created) or direct kubectl commands

**Rollback Point**: Delete Minikube cluster (`minikube delete`), restart clean

**Human Approval Gate #1**: After infrastructure validated, present:
- Screenshot of `kubectl get pods -A` showing all infrastructure pods Running
- Output of `dapr status -k` showing 3/3 Dapr control plane pods
- Output of health check script validating Kafka and PostgreSQL connectivity
- **STOP** until human approves before proceeding to V.1

---

### Phase V.1 — Event Backbone & Dapr Foundations

**Purpose**: Establish event-driven architecture foundations (Dapr State Store, minimal Pub/Sub) and decompose monolithic backend into 6 microservices (code structure only, no full event-driven behavior yet).

**Entry Criteria**:
- ✅ Phase V.0 complete (infrastructure validated)
- ✅ Human approval received for Phase V.0

**Exit Criteria**:
- ✅ 6 FastAPI services created with directory structure
- ✅ Each service has: main.py, Dockerfile, requirements.txt, dapr/components/
- ✅ Dapr State Store configured for all services (PostgreSQL backend)
- ✅ Services deployed to Minikube with Dapr sidecar injection
- ✅ All services report healthy (2/2 containers per pod)
- ✅ Smoke test: Create todo via Todo Service API, verify in State Store

**Dependencies**: Phase V.0

**Skills Used**:
- `dapr`, `dockerization-agent`, `helm-chart-architect`

**Human Approval Gate #2**: Present pod status, health checks, smoke test results

---

### Phase V.2 — Core Feature Enablement (MVP)

**Purpose**: Implement MVP features (F3: Priority, F4: Tags, F6: Audit) and enable Kafka Pub/Sub.

**Exit Criteria**:
- ✅ F3, F4, F6 implemented with acceptance criteria met
- ✅ Kafka Pub/Sub functional (todo.created → audit log)
- ✅ CloudEvents-compliant event schemas validated
- ✅ Idempotency implemented (7-day deduplication window)

**Human Approval Gate #3**: Demo MVP features, audit logging, event payloads

---

### Phase V.3 — Advanced Features

**Purpose**: Implement F5 (Search), F2 (Notifications) with multi-service coordination.

**Exit Criteria**:
- ✅ Full-text search functional (PostgreSQL tsvector)
- ✅ Email notifications functional (Dapr SMTP binding)
- ✅ Event workflows validated (reminder → email)

**Human Approval Gate #4**: Demo search, notifications, event flows

---

### Phase V.4 — Recurring Tasks & Analytics

**Purpose**: Implement F1 (Recurring), F7 (Analytics).

**Exit Criteria**:
- ✅ RRULE parsing functional
- ✅ Next instance generation on completion
- ✅ Analytics dashboard with trends, streaks, insights

**Human Approval Gate #5**: Demo recurring tasks, analytics dashboard

---

### Phase V.5 — Observability & Hardening

**Purpose**: Add Prometheus, Jaeger, resilience patterns, load testing.

**Exit Criteria**:
- ✅ Monitoring stack deployed
- ✅ Distributed tracing functional
- ✅ NFRs validated (API latency p95 <200ms, event processing <1s)
- ✅ Resilience tested (circuit breakers, DLQ)

**Human Approval Gate #6**: Grafana dashboards, Jaeger traces, load test results

---

### Phase V.6 — Cloud Deployment

**Purpose**: Deploy to DOKS, validate cloud-specific configurations.

**Exit Criteria**:
- ✅ 3-node DOKS cluster provisioned (budget-k8s)
- ✅ All services deployed via Helm (values-prod.yaml)
- ✅ External API access functional
- ✅ Cost monitoring: ~$72-84/month
- ✅ Auto-shutdown script documented

**Human Approval Gate #7**: DOKS cluster details, external URL, cost summary

---

## 2. Feature Implementation Order

**MVP (Phase V.2)**:
1. F3: Priority Levels (simplest, no dependencies)
2. F4: Tags (standalone, many-to-many pattern)
3. F6: Audit Logging (foundational, validates Kafka)

**Core (Phase V.3)**:
4. F5: Search (builds on F3+F4)
5. F2: Notifications (complex, multi-service)

**Advanced (Phase V.4)**:
6. F1: Recurring Tasks (depends on F2)
7. F7: Analytics (depends on all features)

---

## 3. Event-Driven Rollout Strategy

**V.1**: No Kafka (State Store only)
**V.2**: Kafka introduced (Todo Service → Audit Service)
**V.3**: Multi-service events (User, Chat, Notification services)
**V.4**: Complex workflows (recurring, analytics)

**Schema Versioning**: CloudEvents v1.0, expand-contract pattern for changes

---

## 4. Dapr Adoption Phases

**V.1**: Sidecar + State Store
**V.2**: Add Pub/Sub (Kafka)
**V.3**: Add Service Invocation
**V.4**: Add Secrets Management
**V.5**: Add Output Bindings (SMTP)

---

## 5. Environment Progression

**Minikube (Primary)**: All features validated locally first
**DOKS (Cloud)**: Production-like deployment for demos

**Promotion Rule**: Only deploy to DOKS after Minikube validation complete

---

## 6. Risk-Control Plan

**Risk 1**: Kafka complexity → Use KRaft mode, Context7-verified commands, fallback to in-memory Pub/Sub
**Risk 2**: Migration failures → Backup before migration, expand-contract pattern, rollback scripts
**Risk 3**: Cost overrun → Daily monitoring, billing alerts, auto-shutdown script

---

## 7. Skills Mapping

| Phase | Skills | Responsibility |
|-------|--------|----------------|
| V.0 | budget-k8s, dapr | Infrastructure setup |
| V.1 | dockerization-agent, helm-chart-architect, dapr | Service structure |
| V.2-V.4 | Custom implementation | Feature development |
| V.5 | Custom implementation | Observability |
| V.6 | budget-k8s, dapr | Cloud deployment |

---

## 8. Human Approval Gates

7 explicit gates where execution MUST STOP:
1. After V.0: Infrastructure validated
2. After V.1: Services deployed
3. After V.2: MVP features complete
4. After V.3: Advanced features complete
5. After V.4: All features complete
6. After V.5: System hardened
7. After V.6: Cloud deployed

---

## Constitution Compliance

✅ Spec-First Development: Plan derived from approved specs
✅ Phase Isolation: Explicit rollback points
✅ Agentic Workflow: spec → plan → tasks → implement
✅ Human-in-the-Loop: 7 approval gates
✅ Clean Architecture: Microservices with clear boundaries
✅ Deterministic Behavior: Idempotent events
✅ Simplicity: Incremental rollout

---

## Final Verification

**Execution Flow**: V.0 → V.1 → V.2 → V.3 → V.4 → V.5 → V.6

**Effort**: 6-8 weeks (qualitative)

**Compliance**:
✅ Fully complies with Phase V specs
✅ Introduces zero new scope
✅ Safe to proceed to `/sp.tasks`

**Plan Status**: ✅ APPROVED FOR TASK GENERATION

**Next Step**: Run `/sp.tasks`

**Stop Here**: Do NOT proceed until human reviews and approves this plan.
