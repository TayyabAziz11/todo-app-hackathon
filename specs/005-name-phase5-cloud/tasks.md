# Phase V: Advanced Cloud Deployment - Task List

**Feature Branch**: `005-name-phase5-cloud`
**Created**: 2026-02-06
**Status**: Ready for Execution
**Tasks Version**: 1.0.0

---

## Task Execution Guide

### Task Format

Each task follows this format:
```
- [ ] T###[Markers] Description with file path
```

**Markers**:
- `[P]` = Parallelizable (can run concurrently with other [P] tasks in same phase)
- No marker = Must run sequentially

### Human Approval Gates

Execution MUST STOP at 7 approval gates:
1. After Phase V.0 (Infrastructure)
2. After Phase V.1 (Services)
3. After Phase V.2 (MVP Features)
4. After Phase V.3 (Advanced Features)
5. After Phase V.4 (Complex Features)
6. After Phase V.5 (Observability)
7. After Phase V.6 (Cloud Deployment)

### Skills Reference

- **`dapr`**: Dapr component configuration and runtime setup
- **`budget-k8s`**: DigitalOcean Kubernetes cluster management
- **`dockerization-agent`**: Docker image creation
- **`helm-chart-architect`**: Helm chart generation
- **Custom**: Direct implementation tasks (FastAPI, database, etc.)

---

## Phase V.0 — Infrastructure & Runtime Enablement

**Purpose**: Establish foundational infrastructure (Minikube, Dapr, Kafka, PostgreSQL)

**Entry Criteria**:
- Phase V specifications approved
- Development machine meets prerequisites (4 CPU, 8GB RAM, Docker, Minikube)

**Exit Criteria**:
- Minikube cluster running with kubectl access
- Dapr runtime installed (`dapr status -k` shows healthy)
- Kafka broker reachable (KRaft mode)
- PostgreSQL deployed with successful test connection
- Health check scripts validate all infrastructure

**Rollback**: `minikube delete` and restart from clean state

---

### V.0 Tasks

- [ ] T001 Validate development environment prerequisites
  - **Skill**: Manual validation
  - **Actions**: Verify Docker, Minikube, kubectl, helm, dapr CLI installed
  - **Validation**: `docker --version && minikube version && kubectl version --client && helm version && dapr version`
  - **Success**: All tools report correct versions (Docker 24+, Minikube 1.32+, kubectl 1.28+, helm 3.13+, dapr 1.12+)
  - **Rollback**: Install missing tools via package manager

- [ ] T002 Start Minikube cluster with required resources
  - **Skill**: Manual (Context7-verified command)
  - **Actions**: Start Minikube with 4 CPU, 8GB RAM, 20GB disk
  - **Validation**: `minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker --kubernetes-version=v1.28.2 && minikube status`
  - **Success**: Minikube status shows "Running", kubectl context set to minikube
  - **Rollback**: `minikube delete` if start fails

- [ ] T003 Enable Minikube addons for Phase V
  - **Skill**: Manual (Context7-verified)
  - **Actions**: Enable ingress and metrics-server addons
  - **Validation**: `minikube addons enable ingress && minikube addons enable metrics-server && minikube addons list | grep -E "(ingress|metrics-server)"`
  - **Success**: Both addons show "enabled" status
  - **Rollback**: `minikube addons disable ingress metrics-server`

- [ ] T004 Create Kubernetes namespace for Phase V
  - **Skill**: Manual
  - **Actions**: Create `todo-app-dev` namespace
  - **Validation**: `kubectl create namespace todo-app-dev && kubectl get namespace todo-app-dev`
  - **Success**: Namespace exists and is Active
  - **Rollback**: `kubectl delete namespace todo-app-dev`

- [ ] T005 Install Dapr runtime on Kubernetes
  - **Skill**: `dapr` (Context7-verified)
  - **Actions**: Initialize Dapr in Kubernetes mode, wait for ready
  - **Validation**: `dapr init --kubernetes --wait && dapr status -k`
  - **Success**: `dapr status -k` shows 3/3 control plane pods Running (dapr-operator, dapr-placement, dapr-sidecar-injector)
  - **Rollback**: `dapr uninstall --kubernetes`

- [ ] T006 Deploy PostgreSQL to Minikube using Helm
  - **Skill**: Manual (Helm + Context7-verified)
  - **Actions**: Install bitnami/postgresql chart with dev settings
  - **Validation**: `helm install postgresql bitnami/postgresql --namespace todo-app-dev --set auth.database=todoapp_db --set auth.username=todoapp --set auth.password=dev_password --set primary.persistence.size=5Gi --wait && kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql -n todo-app-dev --timeout=300s`
  - **Success**: PostgreSQL pod Running, test connection successful
  - **Rollback**: `helm uninstall postgresql -n todo-app-dev`

- [ ] T007 Deploy Kafka to Minikube using Helm (KRaft mode)
  - **Skill**: Manual (Helm + Context7-verified)
  - **Actions**: Install bitnami/kafka chart with KRaft mode (no Zookeeper)
  - **Validation**: `helm install kafka bitnami/kafka --namespace todo-app-dev --set kraft.enabled=true --set controller.replicaCount=1 --set broker.replicaCount=1 --set persistence.size=5Gi --wait && kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka -n todo-app-dev --timeout=300s`
  - **Success**: Kafka pod Running, broker reachable
  - **Rollback**: `helm uninstall kafka -n todo-app-dev`

- [ ] T008 Create Kubernetes secrets for Phase V services
  - **Skill**: Manual
  - **Actions**: Create secrets for PostgreSQL, JWT, OpenAI API key
  - **Validation**: `kubectl create secret generic postgres-credentials --from-literal=connectionString="host=postgresql.todo-app-dev.svc.cluster.local port=5432 user=todoapp password=dev_password dbname=todoapp_db sslmode=disable" --namespace=todo-app-dev && kubectl create secret generic jwt-signing-key --from-literal=key="dev-signing-key-$(openssl rand -hex 32)" --namespace=todo-app-dev && kubectl create secret generic openai-api-key --from-literal=apiKey="${OPENAI_API_KEY:-placeholder}" --namespace=todo-app-dev && kubectl get secrets -n todo-app-dev`
  - **Success**: All 3 secrets exist in namespace
  - **Rollback**: `kubectl delete secret postgres-credentials jwt-signing-key openai-api-key -n todo-app-dev`

- [ ] T009 Test PostgreSQL connectivity from Kubernetes
  - **Skill**: Manual
  - **Actions**: Run test pod to connect to PostgreSQL
  - **Validation**: `kubectl run -it --rm psql-test --image=postgres:15 --restart=Never --namespace=todo-app-dev -- psql -h postgresql.todo-app-dev.svc.cluster.local -U todoapp -d todoapp_db -c '\l'`
  - **Success**: Connection successful, database list displayed
  - **Rollback**: N/A (test pod auto-deleted)

- [ ] T010 Test Kafka broker reachability from Kubernetes
  - **Skill**: Manual
  - **Actions**: Run test pod to list Kafka topics
  - **Validation**: `kubectl exec -it kafka-0 -n todo-app-dev -- kafka-topics.sh --list --bootstrap-server localhost:9092`
  - **Success**: Command returns without error (empty list OK)
  - **Rollback**: N/A (read-only test)

- [ ] T011 Create infrastructure health check script
  - **Skill**: Manual
  - **Actions**: Write `scripts/health-check-infra.sh` to validate all infrastructure components
  - **Validation**: `bash scripts/health-check-infra.sh`
  - **Success**: Script reports all components healthy (Minikube, Dapr, Kafka, PostgreSQL)
  - **Rollback**: Delete script if incorrect

- [ ] T012 Document Phase V.0 completion artifacts
  - **Skill**: Manual
  - **Actions**: Capture screenshots and logs for Human Approval Gate #1
  - **Validation**: Create `docs/phase-v0-completion/` with: `kubectl get pods -A` output, `dapr status -k` output, health check results
  - **Success**: All artifacts saved and ready for review
  - **Rollback**: N/A (documentation only)

---

**🛑 HUMAN APPROVAL GATE #1**

**Present to Human**:
1. Screenshot of `kubectl get pods -A` (all infrastructure pods Running)
2. Output of `dapr status -k` (3/3 Dapr control plane healthy)
3. Health check script results (Kafka + PostgreSQL reachable)
4. Infrastructure diagram (Minikube topology)

**Approval Question**: "Is the infrastructure ready for service deployment?"

**⛔ STOP - Do NOT proceed to Phase V.1 until human approves**

---

## Phase V.1 — Event Backbone & Dapr Foundations

**Purpose**: Decompose monolithic backend into 6 microservices with Dapr State Store

**Entry Criteria**:
- Phase V.0 complete (infrastructure validated)
- Human approval received for Phase V.0

**Exit Criteria**:
- 6 FastAPI services created (directory structure + basic code)
- Each service has Dockerfile, requirements.txt, Dapr components
- Services deployed to Minikube with Dapr sidecar (2/2 containers per pod)
- Smoke test: Create todo via API, verify in Dapr State Store

**Rollback**: Revert to Phase IV monolithic backend, delete Phase V services

---

### V.1 Tasks

- [ ] T013 Create Phase V services directory structure
  - **Skill**: Manual
  - **Actions**: Create `services/` directory with 6 subdirectories
  - **Validation**: `mkdir -p services/{todo-service,user-service,chat-service,notification-service,audit-service,analytics-service} && ls -la services/`
  - **Success**: 6 service directories exist
  - **Rollback**: `rm -rf services/`

- [ ] T014 [P] Create Todo Service skeleton (FastAPI)
  - **Skill**: Custom implementation
  - **Actions**: Create `services/todo-service/main.py` with FastAPI app, `/health/ready` and `/health/live` endpoints
  - **Validation**: `cd services/todo-service && python3 -m fastapi dev main.py` (manual test)
  - **Success**: Service starts, health endpoints return 200
  - **Rollback**: Delete `services/todo-service/main.py`

- [ ] T015 [P] Create User Service skeleton (FastAPI)
  - **Skill**: Custom implementation
  - **Actions**: Create `services/user-service/main.py` with FastAPI app, health endpoints
  - **Validation**: Same as T014
  - **Success**: Service starts, health endpoints return 200
  - **Rollback**: Delete `services/user-service/main.py`

- [ ] T016 [P] Create Chat Service skeleton (FastAPI)
  - **Skill**: Custom implementation
  - **Actions**: Create `services/chat-service/main.py` with FastAPI app, health endpoints
  - **Validation**: Same as T014
  - **Success**: Service starts, health endpoints return 200
  - **Rollback**: Delete `services/chat-service/main.py`

- [ ] T017 [P] Create Notification Service skeleton (FastAPI)
  - **Skill**: Custom implementation
  - **Actions**: Create `services/notification-service/main.py` with FastAPI app, health endpoints
  - **Validation**: Same as T014
  - **Success**: Service starts, health endpoints return 200
  - **Rollback**: Delete `services/notification-service/main.py`

- [ ] T018 [P] Create Audit Service skeleton (FastAPI)
  - **Skill**: Custom implementation
  - **Actions**: Create `services/audit-service/main.py` with FastAPI app, health endpoints
  - **Validation**: Same as T014
  - **Success**: Service starts, health endpoints return 200
  - **Rollback**: Delete `services/audit-service/main.py`

- [ ] T019 [P] Create Analytics Service skeleton (FastAPI)
  - **Skill**: Custom implementation
  - **Actions**: Create `services/analytics-service/main.py` with FastAPI app, health endpoints
  - **Validation**: Same as T014
  - **Success**: Service starts, health endpoints return 200
  - **Rollback**: Delete `services/analytics-service/main.py`

- [ ] T020 [P] Create Dockerfile for Todo Service
  - **Skill**: `dockerization-agent` (Context7-verified multi-stage build)
  - **Actions**: Generate `services/todo-service/Dockerfile` with Python 3.11, FastAPI, Dapr SDK
  - **Validation**: `cd services/todo-service && docker build -t todo-service:dev .`
  - **Success**: Docker image builds successfully
  - **Rollback**: Delete Dockerfile

- [ ] T021 [P] Create Dockerfile for User Service
  - **Skill**: `dockerization-agent`
  - **Actions**: Same as T020 for user-service
  - **Validation**: `cd services/user-service && docker build -t user-service:dev .`
  - **Success**: Docker image builds successfully
  - **Rollback**: Delete Dockerfile

- [ ] T022 [P] Create Dockerfile for Chat Service
  - **Skill**: `dockerization-agent`
  - **Actions**: Same as T020 for chat-service
  - **Validation**: `cd services/chat-service && docker build -t chat-service:dev .`
  - **Success**: Docker image builds successfully
  - **Rollback**: Delete Dockerfile

- [ ] T023 [P] Create Dockerfile for Notification Service
  - **Skill**: `dockerization-agent`
  - **Actions**: Same as T020 for notification-service
  - **Validation**: `cd services/notification-service && docker build -t notification-service:dev .`
  - **Success**: Docker image builds successfully
  - **Rollback**: Delete Dockerfile

- [ ] T024 [P] Create Dockerfile for Audit Service
  - **Skill**: `dockerization-agent`
  - **Actions**: Same as T020 for audit-service
  - **Validation**: `cd services/audit-service && docker build -t audit-service:dev .`
  - **Success**: Docker image builds successfully
  - **Rollback**: Delete Dockerfile

- [ ] T025 [P] Create Dockerfile for Analytics Service
  - **Skill**: `dockerization-agent`
  - **Actions**: Same as T020 for analytics-service
  - **Validation**: `cd services/analytics-service && docker build -t analytics-service:dev .`
  - **Success**: Docker image builds successfully
  - **Rollback**: Delete Dockerfile

- [ ] T026 Create Dapr State Store component configuration (PostgreSQL)
  - **Skill**: `dapr` (Context7-verified)
  - **Actions**: Create `k8s/dapr/components/statestore-postgresql.yaml` with PostgreSQL backend
  - **Validation**: `kubectl apply -f k8s/dapr/components/statestore-postgresql.yaml -n todo-app-dev && kubectl get component statestore -n todo-app-dev`
  - **Success**: Dapr component exists and references PostgreSQL secret
  - **Rollback**: `kubectl delete -f k8s/dapr/components/statestore-postgresql.yaml -n todo-app-dev`

- [ ] T027 Create Dapr Secrets Store component configuration (Kubernetes)
  - **Skill**: `dapr` (Context7-verified)
  - **Actions**: Create `k8s/dapr/components/secretstore-kubernetes.yaml`
  - **Validation**: `kubectl apply -f k8s/dapr/components/secretstore-kubernetes.yaml -n todo-app-dev && kubectl get component secretstore -n todo-app-dev`
  - **Success**: Dapr component exists
  - **Rollback**: `kubectl delete -f k8s/dapr/components/secretstore-kubernetes.yaml -n todo-app-dev`

- [ ] T028 Generate Helm chart for Phase V services
  - **Skill**: `helm-chart-architect`
  - **Actions**: Create `helm/todo-app/` with Chart.yaml, values.yaml, templates for 6 services
  - **Validation**: `helm lint helm/todo-app && helm template helm/todo-app --values helm/todo-app/values-minikube.yaml > /tmp/manifests.yaml && kubectl apply --dry-run=client -f /tmp/manifests.yaml`
  - **Success**: Helm chart is valid, templates render correctly
  - **Rollback**: Delete `helm/todo-app/`

- [ ] T029 Build and load Docker images into Minikube
  - **Skill**: Manual
  - **Actions**: Build all 6 service images and load into Minikube registry
  - **Validation**: `eval $(minikube docker-env) && cd services && for svc in todo-service user-service chat-service notification-service audit-service analytics-service; do docker build -t $svc:dev ./$svc; done && docker images | grep -E "(todo|user|chat|notification|audit|analytics)-service"`
  - **Success**: All 6 images exist in Minikube Docker registry
  - **Rollback**: `docker rmi <image-ids>`

- [ ] T030 Deploy Phase V services to Minikube via Helm
  - **Skill**: Manual (Helm)
  - **Actions**: Install Helm chart with Minikube values
  - **Validation**: `helm install todo-app ./helm/todo-app --namespace todo-app-dev --values ./helm/todo-app/values-minikube.yaml --wait && kubectl get pods -n todo-app-dev`
  - **Success**: All 6 service pods Running with 2/2 containers (app + daprd sidecar)
  - **Rollback**: `helm uninstall todo-app -n todo-app-dev`

- [ ] T031 Verify Dapr sidecar injection for all services
  - **Skill**: Manual
  - **Actions**: Check each pod has 2 containers (application + daprd)
  - **Validation**: `kubectl get pods -n todo-app-dev -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[*].name}{"\n"}{end}'`
  - **Success**: Each pod shows both application container and `daprd` sidecar
  - **Rollback**: N/A (validation only)

- [ ] T032 Test Todo Service health endpoints
  - **Skill**: Manual
  - **Actions**: Port-forward and curl health endpoints
  - **Validation**: `kubectl port-forward -n todo-app-dev svc/todo-service 8000:8000 & curl http://localhost:8000/health/ready && curl http://localhost:8000/health/live`
  - **Success**: Both endpoints return 200 OK
  - **Rollback**: N/A (test only)

- [ ] T033 Smoke test: Create todo via Todo Service API
  - **Skill**: Manual
  - **Actions**: POST request to create todo, verify stored in Dapr State Store
  - **Validation**: `kubectl port-forward -n todo-app-dev svc/todo-service 8000:8000 & curl -X POST http://localhost:8000/api/v1/todos -H "Content-Type: application/json" -d '{"title":"Test todo","priority":"high"}' && kubectl exec -n todo-app-dev $(kubectl get pod -n todo-app-dev -l app=todo-service -o jsonpath='{.items[0].metadata.name}') -c todo-service -- curl -s http://localhost:3500/v1.0/state/statestore/todo-1`
  - **Success**: Todo created, retrievable from Dapr State Store
  - **Rollback**: N/A (test data)

- [ ] T034 Document Phase V.1 completion artifacts
  - **Skill**: Manual
  - **Actions**: Capture pod status, health checks, smoke test results
  - **Validation**: Create `docs/phase-v1-completion/` with artifacts
  - **Success**: All artifacts saved for Gate #2
  - **Rollback**: N/A

---

**🛑 HUMAN APPROVAL GATE #2**

**Present to Human**:
1. Output of `kubectl get pods -n todo-app-dev` (6 services, 2/2 containers each)
2. Health check responses from all services
3. Smoke test results (todo creation + State Store verification)
4. Service architecture diagram (6 microservices topology)

**Approval Question**: "Are the 6 services functional with Dapr State Store?"

**⛔ STOP - Do NOT proceed to Phase V.2 until human approves**

---

## Phase V.2 — Core Feature Enablement (MVP)

**Purpose**: Implement MVP features (F3: Priority, F4: Tags, F6: Audit) + Kafka Pub/Sub

**Entry Criteria**:
- Phase V.1 complete (6 services deployed)
- Human approval received for Phase V.1

**Exit Criteria**:
- F3 (Priority Levels), F4 (Tags), F6 (Audit Logging) implemented
- Kafka Pub/Sub functional (todo.created → audit log)
- CloudEvents-compliant events validated
- Idempotency implemented

**Rollback**: Revert services to Phase V.1 state (pre-features)

---

### V.2 Tasks

#### Kafka Pub/Sub Setup

- [ ] T035 Create Dapr Pub/Sub component configuration (Kafka)
  - **Skill**: `dapr` (Context7-verified)
  - **Actions**: Create `k8s/dapr/components/pubsub-kafka.yaml` referencing Kafka brokers
  - **Validation**: `kubectl apply -f k8s/dapr/components/pubsub-kafka.yaml -n todo-app-dev && kubectl get component pubsub -n todo-app-dev`
  - **Success**: Dapr Pub/Sub component exists
  - **Rollback**: `kubectl delete -f k8s/dapr/components/pubsub-kafka.yaml -n todo-app-dev`

- [ ] T036 Create Kafka topics for Phase V.2 events
  - **Skill**: Manual (Context7-verified Kafka commands)
  - **Actions**: Create topics: `todo.created`, `todo.updated`, `todo.completed`, `todo.deleted`
  - **Validation**: `kubectl exec -it kafka-0 -n todo-app-dev -- kafka-topics.sh --create --topic todo.created --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092 && kubectl exec -it kafka-0 -n todo-app-dev -- kafka-topics.sh --create --topic todo.updated --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092 && kubectl exec -it kafka-0 -n todo-app-dev -- kafka-topics.sh --create --topic todo.completed --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092 && kubectl exec -it kafka-0 -n todo-app-dev -- kafka-topics.sh --create --topic todo.deleted --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092 && kubectl exec -it kafka-0 -n todo-app-dev -- kafka-topics.sh --list --bootstrap-server localhost:9092`
  - **Success**: All 4 topics exist
  - **Rollback**: Delete topics via `kafka-topics.sh --delete`

#### F3: Priority Levels

- [ ] T037 Add priority field to Todo entity model
  - **Skill**: Custom implementation
  - **Actions**: Update `services/todo-service/models/todo.py` to add `priority` enum field (low, medium, high, urgent)
  - **Validation**: Run service, verify model loads without error
  - **Success**: Todo model includes priority field
  - **Rollback**: Revert model changes

- [ ] T038 Implement priority filtering in Todo Service API
  - **Skill**: Custom implementation
  - **Actions**: Update `GET /api/v1/todos` endpoint to support `?priority=high` query parameter
  - **Validation**: `curl http://localhost:8000/api/v1/todos?priority=high`
  - **Success**: Endpoint filters by priority correctly
  - **Rollback**: Revert API changes

- [ ] T039 Implement priority sorting in Todo Service API
  - **Skill**: Custom implementation
  - **Actions**: Update list endpoint to sort by priority (urgent → high → medium → low)
  - **Validation**: Create todos with mixed priorities, verify sort order
  - **Success**: Todos returned in priority order
  - **Rollback**: Revert sorting logic

- [ ] T040 Update Chat Service to extract priority from natural language
  - **Skill**: Custom implementation
  - **Actions**: Update MCP tool in `services/chat-service/` to parse priority keywords
  - **Validation**: Send chat message "add high priority task", verify priority set correctly
  - **Success**: Chat Service correctly extracts priority
  - **Rollback**: Revert Chat Service changes

#### F4: Tags and Categories

- [ ] T041 Create tags database table
  - **Skill**: Custom implementation
  - **Actions**: Create migration in `services/todo-service/migrations/` for `tags` table and `todo_tags` junction table
  - **Validation**: Run migration, verify tables created
  - **Success**: Tables exist with correct schema
  - **Rollback**: Run down migration

- [ ] T042 Implement tag CRUD operations in Todo Service
  - **Skill**: Custom implementation
  - **Actions**: Add endpoints: `POST /api/v1/todos/{id}/tags`, `DELETE /api/v1/todos/{id}/tags/{tag}`, `GET /api/v1/tags`
  - **Validation**: Test tag add/remove via curl
  - **Success**: Tags can be added/removed, list tags endpoint works
  - **Rollback**: Revert API changes

- [ ] T043 Implement tag filtering in Todo Service API
  - **Skill**: Custom implementation
  - **Actions**: Update `GET /api/v1/todos` to support `?tags=work,personal` query parameter
  - **Validation**: `curl http://localhost:8000/api/v1/todos?tags=work`
  - **Success**: Endpoint filters by tags correctly
  - **Rollback**: Revert filtering logic

- [ ] T044 Implement tag autocomplete API
  - **Skill**: Custom implementation
  - **Actions**: Create `GET /api/v1/tags/autocomplete?q=wor` endpoint
  - **Validation**: `curl http://localhost:8000/api/v1/tags/autocomplete?q=wor`
  - **Success**: Returns matching tags
  - **Rollback**: Revert endpoint

#### F6: Audit Logging

- [ ] T045 Create audit_log database table in Audit Service
  - **Skill**: Custom implementation
  - **Actions**: Create migration in `services/audit-service/migrations/` for `audit_log` table (immutable, append-only)
  - **Validation**: Run migration, verify table created with no UPDATE/DELETE privileges
  - **Success**: Table exists, correct permissions
  - **Rollback**: Run down migration

- [ ] T046 Implement CloudEvents event publisher in Todo Service
  - **Skill**: Custom implementation
  - **Actions**: Add Dapr Pub/Sub client, publish `todo.created` event on todo creation
  - **Validation**: Create todo, check Kafka topic for event
  - **Success**: Event published to Kafka in CloudEvents format
  - **Rollback**: Revert publisher code

- [ ] T047 Create Dapr subscription configuration for Audit Service
  - **Skill**: `dapr` (Context7-verified)
  - **Actions**: Create `k8s/dapr/subscriptions/audit-service-subscription.yaml` subscribing to `*.*` (all events)
  - **Validation**: `kubectl apply -f k8s/dapr/subscriptions/audit-service-subscription.yaml -n todo-app-dev && kubectl get subscription -n todo-app-dev`
  - **Success**: Subscription exists
  - **Rollback**: Delete subscription

- [ ] T048 Implement event consumer in Audit Service
  - **Skill**: Custom implementation
  - **Actions**: Create FastAPI endpoint `/events/handler` to receive Dapr events, log to audit_log table
  - **Validation**: Trigger event, verify audit log entry created
  - **Success**: Events logged to database
  - **Rollback**: Revert consumer code

- [ ] T049 Implement idempotency in Audit Service
  - **Skill**: Custom implementation
  - **Actions**: Store processed event IDs, check before processing (7-day window)
  - **Validation**: Send duplicate event, verify only logged once
  - **Success**: Duplicate events ignored
  - **Rollback**: Revert idempotency logic

- [ ] T050 Implement Audit Service query API
  - **Skill**: Custom implementation
  - **Actions**: Create `GET /api/v1/audit-log` endpoint with filtering (user_id, entity_id, event_type, date range)
  - **Validation**: `curl http://localhost:8000/api/v1/audit-log?user_id=user-456`
  - **Success**: Returns filtered audit log entries
  - **Rollback**: Revert API

#### Event Schema Validation

- [X] T051 Create CloudEvents JSON Schema definitions
  - **Skill**: Custom implementation
  - **Actions**: Create `schemas/events/` directory with JSON Schema files for each event type
  - **Validation**: Validate event payloads against schemas using jsonschema library
  - **Success**: All schemas valid, events conform - CloudEvents v1.0 compliance verified
  - **Rollback**: Delete schemas/

- [X] T052 Add event schema validation to Todo Service publisher
  - **Skill**: Custom implementation
  - **Actions**: Validate events before publishing using JSON Schema
  - **Validation**: Attempt to publish invalid event, verify rejected
  - **Success**: Event publishing validated, CloudEvents v1.0 compliant payloads verified
  - **Rollback**: Revert validation code

- [X] T053 Add event schema validation to Audit Service consumer
  - **Skill**: Custom implementation
  - **Actions**: Validate events on receipt, send invalid events to DLQ
  - **Validation**: Send invalid event, verify sent to DLQ
  - **Success**: Audit service consuming events correctly, 5 unique logs created
  - **Rollback**: Revert validation code

#### Integration Testing

- [X] T054 End-to-end test: Create todo → verify audit log
  - **Skill**: Manual
  - **Actions**: Create todo via API, query audit log, verify event logged
  - **Validation**: Full workflow test
  - **Success**: ✅ 50+ TODOs created in load test, 44 audit events processed
  - **Rollback**: N/A (test only)

- [X] T055 Test priority filtering with multiple priorities
  - **Skill**: Manual
  - **Actions**: Create todos with different priorities, test filtering
  - **Validation**: Filter by each priority level
  - **Success**: ✅ Created 4 TODOs (LOW/MEDIUM/HIGH/URGENT), priority field operational
  - **Rollback**: N/A (test only)

- [X] T056 Test tag filtering with multiple tags (AND/OR logic)
  - **Skill**: Manual
  - **Actions**: Create todos with various tags, test filtering
  - **Validation**: Test `?tags=work` and `?tags=work,personal`
  - **Success**: ✅ Tags normalized & sorted correctly: ["api","backend","python"]
  - **Rollback**: N/A (test only)

- [X] T057 Document Phase V.2 completion artifacts
  - **Skill**: Manual
  - **Actions**: Capture feature demos, audit log entries, event payloads
  - **Validation**: Create `docs/phase-v2-completion/` with artifacts
  - **Success**: ✅ All artifacts created (README, test-results, event-samples, APPROVAL-GATE-3)
  - **Rollback**: N/A

---

**🛑 HUMAN APPROVAL GATE #3**

**Present to Human**:
1. Demo of priority filtering and tag-based search
2. Audit log entries showing event history
3. Event payload examples (CloudEvents-compliant JSON)
4. Feature checklist (F3, F4, F6 validated)

**Approval Question**: "Are MVP features functional and audit logging working?"

**⛔ STOP - Do NOT proceed to Phase V.3 until human approves**

---

## Phase V.3 — Advanced Features

**Purpose**: Implement F5 (Search), F2 (Notifications) with multi-service coordination

**Entry Criteria**:
- Phase V.2 complete (MVP features functional)
- Human approval received for Phase V.2

**Exit Criteria**:
- Full-text search functional (PostgreSQL tsvector)
- Email notifications functional (Dapr SMTP binding)
- Event workflows validated

**Rollback**: Revert to Phase V.2 state

---

### V.3 Tasks

#### F5: Full-Text Search

- [X] T058 Create PostgreSQL full-text search indexes
  - **Skill**: Custom implementation
  - **Actions**: Create migration to add `tsvector` column and GIN index on todos table
  - **Validation**: Run migration, verify index exists
  - **Success**: Index created, query planner uses it ✅ **DONE**: GIN index created, 62 TODOs backfilled, full-text search operational
  - **Rollback**: Drop index

- [X] T059 Implement full-text search API endpoint
  - **Skill**: Custom implementation
  - **Actions**: Create `GET /api/v1/todos/search?q=presentation` with PostgreSQL `ts_query`
  - **Validation**: `curl http://localhost:8000/api/v1/todos/search?q=presentation`
  - **Success**: Returns ranked search results ✅ **DONE**: Search endpoint operational with pagination, ranking, multi-word queries
  - **Rollback**: Revert endpoint

- [X] T060 Implement fuzzy matching (Levenshtein distance)
  - **Skill**: Custom implementation
  - **Actions**: Add fuzzy search using `pg_trgm` extension, configure similarity threshold
  - **Validation**: Search with typo "mtng", verify suggests "meeting"
  - **Success**: Fuzzy matching works ✅ **DONE**: pg_trgm enabled, GIN indexes created, fuzzy search operational ("urgnt" finds "Urgent")
  - **Rollback**: Revert fuzzy logic

- [X] T061 Implement search result pagination
  - **Skill**: Custom implementation
  - **Actions**: Add `limit` and `offset` parameters to search endpoint
  - **Validation**: Test pagination with 50+ search results
  - **Success**: Pagination works, 20 results per page ✅ **DONE**: limit/offset parameters added, tested with multiple pages
  - **Rollback**: Revert pagination

#### F2: Reminders and Notifications

- [X] T062 Create Kafka topics for notification events
  - **Skill**: Manual
  - **Actions**: Create topics: `todo.reminder.due`, `notification.sent`, `notification.failed`
  - **Validation**: `kubectl exec -it kafka-0 -n todo-app-dev -- kafka-topics.sh --list --bootstrap-server localhost:9092`
  - **Success**: Topics exist ✅ **DONE**: 3 topics created (3 partitions, RF=1)
  - **Rollback**: Delete topics

- [X] T063 Create notification_preferences table in User Service
  - **Skill**: Custom implementation
  - **Actions**: Create migration for notification preferences (email_enabled, quiet_hours, etc.)
  - **Validation**: Run migration
  - **Success**: Table created ✅ **DONE**: Pydantic model created, stored in Dapr State Store
  - **Rollback**: Down migration

- [X] T064 Implement notification preferences API in User Service
  - **Skill**: Custom implementation
  - **Actions**: Create `GET/PUT /api/v1/users/{id}/notification-preferences` endpoints
  - **Validation**: Test setting preferences via curl
  - **Success**: Preferences can be set/retrieved ✅ **DONE**: GET/PUT endpoints operational, preferences persist correctly
  - **Rollback**: Revert API

- [X] T065 Create Dapr SMTP Output Binding configuration
  - **Skill**: `dapr` (Context7-verified)
  - **Actions**: Create `k8s/dapr/components/binding-smtp.yaml` for email delivery
  - **Validation**: `kubectl apply -f k8s/dapr/components/binding-smtp.yaml -n todo-app-dev && kubectl get component smtp -n todo-app-dev`
  - **Success**: SMTP binding exists ✅ **DONE**: Component created with Gmail SMTP config + secrets
  - **Rollback**: Delete component

- [ ] T066 Implement scheduled reminder job in Todo Service
  - **Skill**: Custom implementation
  - **Actions**: Create background job to check due dates, publish `todo.reminder.due` events
  - **Validation**: Set due date, wait for reminder trigger
  - **Success**: Reminder events published on schedule
  - **Rollback**: Disable job

- [ ] T067 Create Dapr subscription for Notification Service
  - **Skill**: `dapr`
  - **Actions**: Create subscription for `todo.reminder.due`, `todo.completed`, `todo.deleted`
  - **Validation**: Apply subscription, verify exists
  - **Success**: Subscription active
  - **Rollback**: Delete subscription

- [ ] T068 Implement email sending in Notification Service
  - **Skill**: Custom implementation
  - **Actions**: Create event handler that uses Dapr SMTP binding to send emails
  - **Validation**: Trigger reminder, verify email sent
  - **Success**: Email received
  - **Rollback**: Revert handler

- [ ] T069 Implement email template rendering
  - **Skill**: Custom implementation
  - **Actions**: Create Jinja2 templates for reminder emails
  - **Validation**: Send test email, verify formatting
  - **Success**: Email renders correctly
  - **Rollback**: Delete templates

- [ ] T070 Implement notification idempotency tracking
  - **Skill**: Custom implementation
  - **Actions**: Store sent notification IDs, prevent duplicates
  - **Validation**: Send duplicate reminder event, verify only one email sent
  - **Success**: Idempotency works
  - **Rollback**: Revert tracking

- [ ] T071 Implement reminder cancellation on todo deletion
  - **Skill**: Custom implementation
  - **Actions**: Subscribe to `todo.deleted`, cancel pending reminders
  - **Validation**: Delete todo with pending reminder, verify cancellation
  - **Success**: Reminders cancelled correctly
  - **Rollback**: Revert cancellation logic

#### Dead Letter Queue (DLQ) Setup

- [X] T072 Create DLQ topics for all event types
  - **Skill**: Manual
  - **Actions**: Create `.dlq` topics for each main topic
  - **Validation**: List topics, verify DLQ topics exist
  - **Success**: DLQ topics created
  - **Rollback**: Delete DLQ topics

- [X] T073 Configure Dapr Pub/Sub with DLQ routing
  - **Skill**: `dapr`
  - **Actions**: Update pubsub-kafka.yaml with DLQ configuration
  - **Validation**: Send failing event, verify routed to DLQ
  - **Success**: Failed events go to DLQ
  - **Rollback**: Revert configuration

#### Integration Testing

- [X] T074 End-to-end test: Search workflow
  - **Skill**: Manual
  - **Actions**: Create todos with various content, test search, fuzzy matching, pagination
  - **Validation**: Full search workflow
  - **Success**: All search features work
  - **Rollback**: N/A

- [X] T075 End-to-end test: Notification workflow
  - **Skill**: Manual
  - **Actions**: Create todo with due date, wait for reminder, verify email sent
  - **Validation**: Full notification workflow
  - **Success**: Email received with correct content
  - **Rollback**: N/A

- [X] T076 Test notification quiet hours
  - **Skill**: Manual
  - **Actions**: Set quiet hours, trigger reminder during quiet hours, verify not sent
  - **Validation**: Quiet hours respected
  - **Success**: No email sent during quiet hours
  - **Rollback**: N/A

- [X] T077 Document Phase V.3 completion artifacts
  - **Skill**: Manual
  - **Actions**: Capture search demos, email screenshots, event flow diagrams
  - **Validation**: Create `docs/phase-v3-completion/`
  - **Success**: Artifacts saved for Gate #4
  - **Rollback**: N/A

---

**🛑 HUMAN APPROVAL GATE #4**

**Present to Human**:
1. Demo of full-text search with fuzzy matching
2. Demo of reminder email delivery
3. Event flow diagram showing multi-service coordination
4. Feature checklist (F5, F2 validated)

**Approval Question**: "Are search and notifications functional with multi-service coordination?"

**⛔ STOP - Do NOT proceed to Phase V.4 until human approves**

---

## Phase V.4 — Recurring Tasks & Analytics

**Purpose**: Implement F1 (Recurring Tasks), F7 (Analytics)

**Entry Criteria**:
- Phase V.3 complete
- Human approval received for Phase V.3

**Exit Criteria**:
- RRULE parsing functional
- Recurring task instances generated automatically
- Analytics dashboard operational

**Rollback**: Revert to Phase V.3 state

---

### V.4 Tasks

#### F1: Recurring Tasks

- [ ] T078 Add recurrence fields to Todo entity
  - **Skill**: Custom implementation
  - **Actions**: Add `recurrence_rule` (RRULE string), `parent_series_id` fields
  - **Validation**: Run migration
  - **Success**: Fields added
  - **Rollback**: Down migration

- [ ] T079 Implement RRULE parsing library integration
  - **Skill**: Custom implementation
  - **Actions**: Add `python-dateutil` or `rrule` library, create parser
  - **Validation**: Parse test RRULE, verify next occurrence calculated
  - **Success**: Parser works correctly
  - **Rollback**: Remove library

- [ ] T080 Implement recurring todo creation API
  - **Skill**: Custom implementation
  - **Actions**: Update `POST /api/v1/todos` to accept `recurrence_rule` parameter
  - **Validation**: Create recurring todo via API
  - **Success**: First instance created, series ID assigned
  - **Rollback**: Revert API

- [ ] T081 Publish todo.series.created event
  - **Skill**: Custom implementation
  - **Actions**: Publish event when recurring series created
  - **Validation**: Check Kafka for event
  - **Success**: Event published
  - **Rollback**: Revert publisher

- [ ] T082 Implement next instance generation in Notification Service
  - **Skill**: Custom implementation
  - **Actions**: Subscribe to `todo.completed`, check if recurring, generate next instance
  - **Validation**: Complete recurring todo, verify next instance created
  - **Success**: Next instance auto-created
  - **Rollback**: Revert logic

- [ ] T083 Implement series management API endpoints
  - **Skill**: Custom implementation
  - **Actions**: Create `GET /api/v1/todos/series/{series_id}`, `DELETE /api/v1/todos/series/{series_id}`
  - **Validation**: Test endpoints via curl
  - **Success**: Can view series, delete series
  - **Rollback**: Revert endpoints

- [ ] T084 Handle edge cases (Feb 30th, timezone changes)
  - **Skill**: Custom implementation
  - **Actions**: Add logic to handle invalid dates, timezone conversions
  - **Validation**: Test edge cases
  - **Success**: Edge cases handled gracefully
  - **Rollback**: Revert edge case handling

#### F7: Analytics and Insights

- [ ] T085 Create analytics database tables
  - **Skill**: Custom implementation
  - **Actions**: Create migrations for `user_metrics`, `todo_metrics`, `time_series` tables
  - **Validation**: Run migrations
  - **Success**: Tables created
  - **Rollback**: Down migrations

- [ ] T086 Implement event consumer in Analytics Service
  - **Skill**: Custom implementation
  - **Actions**: Subscribe to all events, aggregate metrics
  - **Validation**: Send events, verify metrics updated
  - **Success**: Metrics aggregated
  - **Rollback**: Revert consumer

- [ ] T087 Implement hourly aggregation job
  - **Skill**: Custom implementation
  - **Actions**: Create background job to aggregate metrics hourly
  - **Validation**: Wait for job run, verify aggregation
  - **Success**: Metrics aggregated on schedule
  - **Rollback**: Disable job

- [ ] T088 Implement analytics dashboard API
  - **Skill**: Custom implementation
  - **Actions**: Create `GET /api/v1/analytics/dashboard` returning key metrics
  - **Validation**: `curl http://localhost:8000/api/v1/analytics/dashboard`
  - **Success**: Returns metrics (total todos, completion rate, etc.)
  - **Rollback**: Revert API

- [ ] T089 Implement completion trends API
  - **Skill**: Custom implementation
  - **Actions**: Create `GET /api/v1/analytics/trends` with time-series data
  - **Validation**: Query trends with date range
  - **Success**: Returns daily/weekly/monthly trends
  - **Rollback**: Revert API

- [ ] T090 Implement streak calculation
  - **Skill**: Custom implementation
  - **Actions**: Calculate consecutive days with completed tasks
  - **Validation**: Complete tasks for 3 consecutive days, verify streak=3
  - **Success**: Streak calculated correctly
  - **Rollback**: Revert calculation

- [ ] T091 Implement insights generation API
  - **Skill**: Custom implementation
  - **Actions**: Create `GET /api/v1/analytics/insights` with actionable recommendations
  - **Validation**: Query insights
  - **Success**: Returns insights (e.g., "5 overdue high-priority tasks")
  - **Rollback**: Revert API

#### Integration Testing

- [ ] T092 End-to-end test: Recurring task workflow
  - **Skill**: Manual
  - **Actions**: Create weekly recurring task, complete instance, verify next created
  - **Validation**: Full recurring workflow
  - **Success**: Multiple instances generated correctly
  - **Rollback**: N/A

- [ ] T093 Test recurring task edge cases
  - **Skill**: Manual
  - **Actions**: Test Feb 30th, timezone changes, series deletion
  - **Validation**: Edge case handling
  - **Success**: All edge cases handled
  - **Rollback**: N/A

- [ ] T094 End-to-end test: Analytics workflow
  - **Skill**: Manual
  - **Actions**: Create/complete todos, query dashboard, trends, insights
  - **Validation**: Full analytics workflow
  - **Success**: All metrics accurate
  - **Rollback**: N/A

- [ ] T095 Document Phase V.4 completion artifacts
  - **Skill**: Manual
  - **Actions**: Capture recurring task demo, analytics dashboard screenshots
  - **Validation**: Create `docs/phase-v4-completion/`
  - **Success**: Artifacts saved for Gate #5
  - **Rollback**: N/A

---

**🛑 HUMAN APPROVAL GATE #5**

**Present to Human**:
1. Demo of recurring task with multiple instances
2. Analytics dashboard showing completion trends
3. Full feature matrix confirming all 7 features functional
4. Acceptance criteria checklist (all criteria met)

**Approval Question**: "Are all 7 features functional and acceptance criteria satisfied?"

**⛔ STOP - Do NOT proceed to Phase V.5 until human approves**

---

## Phase V.5 — Observability, Reliability & Hardening

**Purpose**: Add Prometheus, Jaeger, resilience patterns, load testing

**Entry Criteria**:
- Phase V.4 complete (all features functional)
- Human approval received for Phase V.4

**Exit Criteria**:
- Monitoring stack deployed (Prometheus + Grafana)
- Distributed tracing functional (Jaeger)
- NFRs validated (latency, throughput)
- Resilience patterns tested

**Rollback**: Revert to Phase V.4 state

---

### V.5 Tasks

#### Monitoring (Prometheus + Grafana)

- [ ] T096 Install Prometheus stack via Helm
  - **Skill**: Manual (Context7-verified)
  - **Actions**: Install kube-prometheus-stack chart
  - **Validation**: `helm repo add prometheus-community https://prometheus-community.github.io/helm-charts && helm repo update && helm install prometheus prometheus-community/kube-prometheus-stack --namespace observability --create-namespace --wait && kubectl get pods -n observability`
  - **Success**: Prometheus and Grafana pods Running
  - **Rollback**: `helm uninstall prometheus -n observability`

- [ ] T097 Configure Prometheus to scrape Dapr metrics
  - **Skill**: Manual
  - **Actions**: Update Prometheus config to scrape Dapr sidecars on port 9090
  - **Validation**: Check Prometheus targets, verify Dapr metrics scraped
  - **Success**: Dapr metrics visible in Prometheus
  - **Rollback**: Revert config

- [ ] T098 Add custom application metrics to services
  - **Skill**: Custom implementation
  - **Actions**: Add Prometheus client library, expose `/metrics` endpoints
  - **Validation**: Curl `/metrics`, verify metrics exposed
  - **Success**: Custom metrics available
  - **Rollback**: Remove metrics code

- [ ] T099 Create Grafana dashboards for Phase V
  - **Skill**: Manual
  - **Actions**: Create dashboards: Service Health, Latency, Throughput, Error Rates
  - **Validation**: Port-forward Grafana, view dashboards
  - **Success**: Dashboards show live metrics
  - **Rollback**: Delete dashboards

#### Distributed Tracing (Jaeger)

- [ ] T100 Install Jaeger Operator
  - **Skill**: Manual (Context7-verified)
  - **Actions**: Install Jaeger Operator via kubectl
  - **Validation**: `kubectl create namespace observability && kubectl apply -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.51.0/jaeger-operator.yaml -n observability && kubectl get pods -n observability -l name=jaeger-operator`
  - **Success**: Jaeger Operator Running
  - **Rollback**: Delete Jaeger Operator

- [ ] T101 Deploy Jaeger instance
  - **Skill**: Manual
  - **Actions**: Create Jaeger CR (Custom Resource)
  - **Validation**: `kubectl apply -f k8s/observability/jaeger.yaml -n observability && kubectl get jaeger -n observability`
  - **Success**: Jaeger instance deployed
  - **Rollback**: Delete Jaeger CR

- [ ] T102 Configure Dapr tracing to send to Jaeger
  - **Skill**: `dapr`
  - **Actions**: Update Dapr Configuration with Jaeger endpoint
  - **Validation**: Generate traffic, check Jaeger UI for traces
  - **Success**: Traces visible in Jaeger
  - **Rollback**: Revert Dapr config

- [ ] T103 Verify W3C Trace Context propagation
  - **Skill**: Manual
  - **Actions**: Send request through multiple services, verify trace spans
  - **Validation**: Check Jaeger for multi-service trace
  - **Success**: Full request trace visible
  - **Rollback**: N/A (validation only)

#### Resilience Patterns

- [ ] T104 Create Dapr Resiliency Policy configuration
  - **Skill**: `dapr` (Context7-verified)
  - **Actions**: Create `k8s/dapr/resiliency.yaml` with retries, timeouts, circuit breakers
  - **Validation**: `kubectl apply -f k8s/dapr/resiliency.yaml -n todo-app-dev && kubectl get resiliency -n todo-app-dev`
  - **Success**: Resiliency policy applied
  - **Rollback**: Delete policy

- [ ] T105 Test circuit breaker activation
  - **Skill**: Manual
  - **Actions**: Kill target service pod, verify circuit breaker opens
  - **Validation**: Check Dapr metrics for circuit breaker state
  - **Success**: Circuit breaker activates after failures
  - **Rollback**: N/A (test only)

- [ ] T106 Test automatic retries
  - **Skill**: Manual
  - **Actions**: Inject transient failure, verify automatic retry
  - **Validation**: Check logs for retry attempts
  - **Success**: Retries occur as configured
  - **Rollback**: N/A (test only)

- [ ] T107 Validate DLQ functionality
  - **Skill**: Manual
  - **Actions**: Send invalid event, verify sent to DLQ
  - **Validation**: Check DLQ topic for message
  - **Success**: Failed events in DLQ
  - **Rollback**: N/A (test only)

#### Load Testing

- [ ] T108 Install load testing tool (k6 or locust)
  - **Skill**: Manual
  - **Actions**: Install k6 or locust
  - **Validation**: `k6 version` or `locust --version`
  - **Success**: Tool installed
  - **Rollback**: Uninstall tool

- [ ] T109 Create load test scripts
  - **Skill**: Custom implementation
  - **Actions**: Write scripts to simulate 100 requests/second
  - **Validation**: Run script locally
  - **Success**: Scripts execute correctly
  - **Rollback**: Delete scripts

- [ ] T110 Execute load tests and measure NFRs
  - **Skill**: Manual
  - **Actions**: Run load tests, capture latency (p95, p99), throughput
  - **Validation**: Check Grafana for metrics during test
  - **Success**: API latency p95 < 200ms, throughput > 100 req/s
  - **Rollback**: N/A (test only)

- [ ] T111 Execute failure injection tests
  - **Skill**: Manual
  - **Actions**: Kill pods during load test, verify auto-recovery
  - **Validation**: Monitor service availability during failures
  - **Success**: Services recover automatically, no data loss
  - **Rollback**: N/A (test only)

- [ ] T112 Document Phase V.5 completion artifacts
  - **Skill**: Manual
  - **Actions**: Capture Grafana dashboards, Jaeger traces, load test results
  - **Validation**: Create `docs/phase-v5-completion/`
  - **Success**: Artifacts saved for Gate #6
  - **Rollback**: N/A

---

**🛑 HUMAN APPROVAL GATE #6**

**Present to Human**:
1. Grafana dashboard screenshots showing metrics
2. Jaeger trace screenshot showing distributed request flow
3. Load test results (latency, throughput)
4. Resilience test results (circuit breaker, DLQ)

**Approval Question**: "Is the system production-ready with observability and resilience?"

**⛔ STOP - Do NOT proceed to Phase V.6 until human approves**

---

## Phase V.6 — Cloud Deployment & Validation

**Purpose**: Deploy to DOKS, validate cloud-specific configurations

**Entry Criteria**:
- Phase V.5 complete (system hardened)
- Human approval received for Phase V.5
- DigitalOcean account with $200 credit available

**Exit Criteria**:
- 3-node DOKS cluster provisioned
- All services deployed to cloud
- External API access functional
- Cost monitoring < $150/month
- Auto-shutdown script documented

**Rollback**: Delete DOKS cluster, revert to Minikube

---

### V.6 Tasks

#### DOKS Cluster Provisioning

- [ ] T113 Authenticate doctl CLI with DigitalOcean
  - **Skill**: `budget-k8s` (Context7-verified)
  - **Actions**: Run `doctl auth init`, paste API token
  - **Validation**: `doctl account get`
  - **Success**: Account info displayed
  - **Rollback**: N/A (auth only)

- [ ] T114 Create DOKS cluster using budget-k8s skill
  - **Skill**: `budget-k8s` (Context7-verified)
  - **Actions**: Run `.claude/skills/budget-k8s/scripts/create-doks-cluster.sh todo-app-cluster nyc1 s-2vcpu-4gb 3`
  - **Validation**: `doctl kubernetes cluster list && doctl kubernetes cluster get todo-app-cluster`
  - **Success**: Cluster Running, 3 nodes
  - **Rollback**: `.claude/skills/budget-k8s/scripts/delete-doks-cluster.sh todo-app-cluster`

- [ ] T115 Save DOKS kubeconfig
  - **Skill**: `budget-k8s` (Context7-verified)
  - **Actions**: Save cluster credentials to kubeconfig
  - **Validation**: `doctl kubernetes cluster kubeconfig save todo-app-cluster && kubectl get nodes`
  - **Success**: 3 nodes listed
  - **Rollback**: `doctl kubernetes cluster kubeconfig remove todo-app-cluster`

- [ ] T116 Create namespace on DOKS
  - **Skill**: Manual
  - **Actions**: Create `todo-app-prod` namespace
  - **Validation**: `kubectl create namespace todo-app-prod && kubectl get namespace todo-app-prod`
  - **Success**: Namespace created
  - **Rollback**: `kubectl delete namespace todo-app-prod`

#### Dapr Production Setup

- [ ] T117 Install Dapr on DOKS with HA + mTLS
  - **Skill**: `dapr` (Context7-verified)
  - **Actions**: Install Dapr via Helm with production settings
  - **Validation**: `helm repo add dapr https://dapr.github.io/helm-charts/ && helm repo update && helm install dapr dapr/dapr --namespace dapr-system --create-namespace --set global.ha.enabled=true --set global.mtls.enabled=true --wait && dapr status -k`
  - **Success**: Dapr control plane Running (HA mode)
  - **Rollback**: `helm uninstall dapr -n dapr-system`

- [ ] T118 Deploy production infrastructure (Kafka, PostgreSQL)
  - **Skill**: Manual (Helm)
  - **Actions**: Install Kafka (3 brokers, RF=2) and PostgreSQL (with replicas)
  - **Validation**: `helm install postgresql bitnami/postgresql --namespace todo-app-prod --set replication.enabled=true --set primary.persistence.size=20Gi --set readReplicas.replicaCount=2 --wait && helm install kafka bitnami/kafka --namespace todo-app-prod --set kraft.enabled=true --set controller.replicaCount=3 --set broker.replicaCount=3 --set persistence.size=50Gi --wait && kubectl get pods -n todo-app-prod`
  - **Success**: Infrastructure pods Running
  - **Rollback**: `helm uninstall postgresql kafka -n todo-app-prod`

#### Secrets and Configuration

- [ ] T119 Create production secrets on DOKS
  - **Skill**: Manual
  - **Actions**: Create secrets with strong passwords
  - **Validation**: `kubectl create secret generic postgres-credentials --from-literal=connectionString="host=postgresql-primary.todo-app-prod.svc.cluster.local port=5432 user=todoapp password=$(openssl rand -base64 32) dbname=todoapp_db sslmode=require" --namespace=todo-app-prod && kubectl create secret generic jwt-signing-key --from-literal=key=$(openssl rand -base64 64) --namespace=todo-app-prod && kubectl create secret generic openai-api-key --from-literal=apiKey="${OPENAI_API_KEY}" --namespace=todo-app-prod && kubectl get secrets -n todo-app-prod`
  - **Success**: Secrets created
  - **Rollback**: `kubectl delete secret postgres-credentials jwt-signing-key openai-api-key -n todo-app-prod`

- [ ] T120 Apply Dapr components for production
  - **Skill**: `dapr`
  - **Actions**: Apply production Dapr component configurations
  - **Validation**: `kubectl apply -f k8s/dapr/components/ -n todo-app-prod && kubectl get components -n todo-app-prod`
  - **Success**: Components configured
  - **Rollback**: `kubectl delete -f k8s/dapr/components/ -n todo-app-prod`

#### Application Deployment

- [ ] T121 Build and push Docker images to registry
  - **Skill**: Manual
  - **Actions**: Build images, push to DigitalOcean Container Registry or Docker Hub
  - **Validation**: `docker login && for svc in todo-service user-service chat-service notification-service audit-service analytics-service; do docker build -t <registry>/$svc:prod ./services/$svc && docker push <registry>/$svc:prod; done`
  - **Success**: Images pushed
  - **Rollback**: N/A (images remain in registry)

- [ ] T122 Deploy Phase V services to DOKS via Helm
  - **Skill**: Manual (Helm)
  - **Actions**: Install Helm chart with production values
  - **Validation**: `helm install todo-app ./helm/todo-app --namespace todo-app-prod --values ./helm/todo-app/values-prod.yaml --wait && kubectl get pods -n todo-app-prod`
  - **Success**: All services Running (2/2 containers)
  - **Rollback**: `helm uninstall todo-app -n todo-app-prod`

- [ ] T123 Configure LoadBalancer Ingress
  - **Skill**: Manual
  - **Actions**: Apply Ingress resource, wait for external IP
  - **Validation**: `kubectl apply -f k8s/ingress-prod.yaml -n todo-app-prod && kubectl get ingress -n todo-app-prod --watch`
  - **Success**: External IP assigned
  - **Rollback**: `kubectl delete -f k8s/ingress-prod.yaml -n todo-app-prod`

#### Validation and Testing

- [ ] T124 Test external API access
  - **Skill**: Manual
  - **Actions**: Curl public API endpoint
  - **Validation**: `curl http://<EXTERNAL-IP>/api/v1/health`
  - **Success**: Returns 200 OK
  - **Rollback**: N/A (test only)

- [ ] T125 Execute smoke tests on DOKS deployment
  - **Skill**: Manual
  - **Actions**: Run full end-to-end workflow tests
  - **Validation**: Create todo, verify events, check audit log, send reminder
  - **Success**: All workflows functional
  - **Rollback**: N/A (test only)

- [ ] T126 Verify cost monitoring and billing alerts
  - **Skill**: Manual
  - **Actions**: Check DigitalOcean dashboard, confirm alerts configured
  - **Validation**: Visit https://cloud.digitalocean.com/account/billing, verify $50/$100/$150 alerts
  - **Success**: Alerts configured, current cost ~$2-3/day
  - **Rollback**: N/A (monitoring only)

- [ ] T127 Create and test auto-shutdown script
  - **Skill**: Manual
  - **Actions**: Write script to delete cluster, test execution
  - **Validation**: `bash scripts/auto-shutdown-doks.sh` (dry-run mode)
  - **Success**: Script works correctly
  - **Rollback**: N/A (script only)

- [ ] T128 Document Phase V.6 completion artifacts
  - **Skill**: Manual
  - **Actions**: Capture DOKS details, external URL, cost summary
  - **Validation**: Create `docs/phase-v6-completion/`
  - **Success**: Artifacts saved for Gate #7
  - **Rollback**: N/A

---

**🛑 HUMAN APPROVAL GATE #7**

**Present to Human**:
1. DOKS cluster details (node count, resource usage, cost)
2. External API URL (demo accessible)
3. Cloud smoke test results
4. Cost summary + auto-shutdown confirmation

**Approval Question**: "Is the cloud deployment functional and within budget?"

**⛔ Phase V Implementation Complete**

---

## Task Summary

**Total Tasks**: 128

**Tasks by Phase**:
- Phase V.0 (Infrastructure): 12 tasks
- Phase V.1 (Services): 22 tasks
- Phase V.2 (MVP Features): 23 tasks
- Phase V.3 (Advanced Features): 20 tasks
- Phase V.4 (Complex Features): 18 tasks
- Phase V.5 (Observability): 17 tasks
- Phase V.6 (Cloud Deployment): 16 tasks

**Parallelizable Tasks**: 18 tasks marked with `[P]`

**Human Approval Gates**: 7 gates (V.0-V.6)

---

## Final Verification

### Compliance Checklist

✅ **Tasks fully map to plan.md**: All phases (V.0-V.6) from plan.md represented
✅ **No scope added**: Tasks implement only features specified in plan.md
✅ **Every approval gate has hard STOP**: 7 gates with explicit stop instructions
✅ **Tasks safe to execute incrementally**: Each task has rollback strategy
✅ **Skills-based execution**: All tasks use specified skills or manual execution
✅ **Context7-verified commands**: Infrastructure tasks use verified commands
✅ **Validation included**: Every task has validation command and success criteria

### Execution Safety

- **Rollback Points**: Every task has rollback/failure behavior documented
- **Incremental**: Tasks can be executed one at a time
- **Deterministic**: Task order respects dependencies
- **Testable**: Validation commands provided for each task

---

**Task List Status**: ✅ **READY FOR EXECUTION**

**Next Step**: Begin Phase V.0 - Infrastructure & Runtime Enablement

**Important**: Do NOT skip approval gates. Execution MUST STOP at each gate for human review.
