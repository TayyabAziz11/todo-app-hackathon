# Tasks: Phase IV Local Kubernetes Deployment

**Input**: Design documents from `/specs/004-phase4-local-k8s/`
**Prerequisites**: plan.md (complete), spec.md (complete)

**Tests**: No explicit test tasks included - validation occurs through operational acceptance scenarios defined in each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/`, `frontend/`, `charts/` at repository root
- Infrastructure artifacts: `charts/todo-backend/`, `charts/todo-frontend/`
- Tests: `tests/backend/`, `tests/frontend/`

---

## Phase 1: Setup (Prerequisites Validation)

**Purpose**: Validate infrastructure prerequisites and prepare environment for Phase IV deployment

- [ ] T001 Verify Minikube installed (v1.30+) using `minikube version`
- [ ] T002 Verify Docker installed (v24.0+) using `docker --version`
- [ ] T003 Verify Helm installed (v3.14+) using `helm version`
- [ ] T004 Verify kubectl installed (v1.28+) using `kubectl version`
- [ ] T005 [P] Check kubectl-ai availability (optional) using `kubectl-ai --version`
- [ ] T006 [P] Check kagent availability (optional) using `kagent --version`
- [ ] T007 Start Minikube cluster with `minikube start --cpus=4 --memory=8192 --kubernetes-version=v1.28.0`
- [ ] T008 Verify Minikube status with `minikube status`
- [ ] T009 Enable Minikube Docker daemon with `eval $(minikube docker-env)`
- [ ] T010 Validate Phase III backend and frontend source code exists at backend/ and frontend/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure preparation that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T011 Create namespace todo-dev using `kubectl create namespace todo-dev`
- [ ] T012 Verify namespace creation with `kubectl get namespaces | grep todo-dev`
- [ ] T013 Create Kubernetes Secret todo-backend-secrets with DATABASE_URL, SECRET_KEY, OPENAI_API_KEY in namespace todo-dev
- [ ] T014 Verify Secret creation with `kubectl get secret todo-backend-secrets -n todo-dev`
- [ ] T015 Document Secret creation command in charts/todo-backend/README.md
- [ ] T016 Create charts/ directory structure at repository root

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Local Development Environment Setup (Priority: P1) 🎯 MVP

**Goal**: Deploy complete Todo AI Chatbot application (frontend + backend) to local Minikube cluster with all pods Running and end-to-end functionality working

**Independent Test**: Deploy both services to Minikube, access frontend via browser at http://<minikube-ip>:30080, register user, login, navigate to /chat, send message to chatbot, verify response within 3 seconds matching Phase III performance

### Backend Containerization

- [ ] T017 [P] [US1] Read backend/main.py to identify Python version, dependencies, health endpoint, and port configuration
- [ ] T018 [P] [US1] Read backend/requirements.txt to extract dependency list
- [ ] T019 [P] [US1] Read backend/.env.example to identify required environment variables
- [ ] T020 [US1] Generate backend Dockerfile using Docker AI (Gordon) or Claude Code fallback with prompt: "Create optimized multi-stage Dockerfile for Python 3.11 FastAPI application with uvicorn server, non-root user (UID 1000), health check on /health, port 8000, target image size <200MB"
- [ ] T021 [US1] Create backend/.dockerignore excluding venv/, tests/, .env, __pycache__/, *.log, .git/, docs/
- [ ] T022 [US1] Build backend Docker image with `docker build -t todo-backend:v1.0.0 ./backend`
- [ ] T023 [US1] Tag backend image with `docker tag todo-backend:v1.0.0 todo-backend:latest`
- [ ] T024 [US1] Verify backend image size <200MB with `docker images | grep todo-backend`
- [ ] T025 [US1] Test backend container locally with `docker run -p 8000:8000 todo-backend:v1.0.0` and verify /health endpoint
- [ ] T026 [US1] Load backend image into Minikube with `minikube image load todo-backend:v1.0.0`

### Frontend Containerization

- [ ] T027 [P] [US1] Read frontend/package.json to identify Node version, dependencies, and build commands
- [ ] T028 [P] [US1] Read frontend/next.config.js to identify Next.js configuration
- [ ] T029 [P] [US1] Read frontend/.env.example to identify build-time environment variables
- [ ] T030 [US1] Generate frontend Dockerfile using Docker AI (Gordon) or Claude Code fallback with prompt: "Create optimized multi-stage Dockerfile for Next.js 15 application with standalone mode, non-root user (UID 1001), port 3000, include NEXT_PUBLIC_* build args, target image size <100MB"
- [ ] T031 [US1] Create frontend/.dockerignore excluding node_modules/, .next/, .env, *.log, .git/, tests/
- [ ] T032 [US1] Build frontend Docker image with build args: `docker build --build-arg NEXT_PUBLIC_API_URL=http://todo-backend:8000 --build-arg NEXT_PUBLIC_CHAT_API_URL=http://todo-backend:8000/api --build-arg NEXT_PUBLIC_OPENAI_DOMAIN_KEY=placeholder -t todo-frontend:v1.0.0 ./frontend`
- [ ] T033 [US1] Tag frontend image with `docker tag todo-frontend:v1.0.0 todo-frontend:latest`
- [ ] T034 [US1] Verify frontend image size <100MB with `docker images | grep todo-frontend`
- [ ] T035 [US1] Load frontend image into Minikube with `minikube image load todo-frontend:v1.0.0`

### Backend Helm Chart Generation

- [ ] T036 [P] [US1] Create directory structure charts/todo-backend/templates/
- [ ] T037 [P] [US1] Generate backend Chart.yaml with apiVersion v2, name todo-backend, version 1.0.0, appVersion v1.0.0
- [ ] T038 [US1] Generate backend values.yaml with replicaCount 1, image todo-backend:v1.0.0, service ClusterIP port 8000, resources requests 256Mi/250m limits 512Mi/500m, liveness/readiness probes on /health, env DATABASE_URL/SECRET_KEY/OPENAI_API_KEY/FRONTEND_URL, autoscaling disabled
- [ ] T039 [US1] Generate backend values-dev.yaml with Minikube overrides: replicaCount 1, resources requests 128Mi/100m limits 256Mi/250m, env FRONTEND_URL http://todo-frontend:3000
- [ ] T040 [US1] Generate backend templates/deployment.yaml with parameterized replicas, image, resources, probes, env from ConfigMap/Secret, rolling update strategy
- [ ] T041 [US1] Generate backend templates/service.yaml with ClusterIP exposing port 8000, selector app=todo-backend
- [ ] T042 [US1] Generate backend templates/configmap.yaml with FRONTEND_URL configuration
- [ ] T043 [US1] Generate backend templates/secrets.yaml template (no actual values) with DATABASE_URL, SECRET_KEY, OPENAI_API_KEY fields
- [ ] T044 [US1] Generate backend templates/hpa.yaml with autoscaling configuration (optional)
- [ ] T045 [US1] Generate backend templates/_helpers.tpl with reusable functions: todo-backend.name, todo-backend.fullname, todo-backend.labels, todo-backend.selectorLabels
- [ ] T046 [US1] Generate backend README.md with installation instructions, configuration options, Secret creation examples, upgrade/rollback commands
- [ ] T047 [US1] Validate backend Helm chart with `helm lint charts/todo-backend`

### Frontend Helm Chart Generation

- [ ] T048 [P] [US1] Create directory structure charts/todo-frontend/templates/
- [ ] T049 [P] [US1] Generate frontend Chart.yaml with apiVersion v2, name todo-frontend, version 1.0.0, appVersion v1.0.0
- [ ] T050 [US1] Generate frontend values.yaml with replicaCount 1, image todo-frontend:v1.0.0, service NodePort port 3000 nodePort 30080, resources requests 128Mi/100m limits 256Mi/250m, liveness/readiness probes on /, env NEXT_PUBLIC_API_URL/NEXT_PUBLIC_CHAT_API_URL/NEXT_PUBLIC_OPENAI_DOMAIN_KEY, autoscaling disabled
- [ ] T051 [US1] Generate frontend values-dev.yaml with Minikube overrides: replicaCount 1, service nodePort 30080, resources requests 64Mi/50m limits 128Mi/150m
- [ ] T052 [US1] Generate frontend templates/deployment.yaml with parameterized replicas, image, resources, probes, build-time env vars baked into image
- [ ] T053 [US1] Generate frontend templates/service.yaml with NodePort exposing port 3000 on nodePort 30080
- [ ] T054 [US1] Generate frontend templates/configmap.yaml with NEXT_PUBLIC_* build-time configuration
- [ ] T055 [US1] Generate frontend templates/_helpers.tpl with reusable functions: todo-frontend.name, todo-frontend.fullname, todo-frontend.labels, todo-frontend.selectorLabels
- [ ] T056 [US1] Generate frontend README.md with installation instructions, NodePort access documentation, configuration options
- [ ] T057 [US1] Validate frontend Helm chart with `helm lint charts/todo-frontend`

### Kubernetes Deployment

- [ ] T058 [US1] Deploy backend via Helm: `helm install todo-backend charts/todo-backend --values charts/todo-backend/values-dev.yaml --namespace todo-dev`
- [ ] T059 [US1] Verify backend Helm release with `helm list -n todo-dev`
- [ ] T060 [US1] Wait for backend pods to reach Running state with `kubectl get pods -n todo-dev | grep todo-backend` (verify within 2 minutes)
- [ ] T061 [US1] Verify backend service ClusterIP assigned with `kubectl get service -n todo-dev | grep todo-backend`
- [ ] T062 [US1] Test backend health endpoint from within cluster: `kubectl run -n todo-dev curl-test --image=curlimages/curl --rm -it --restart=Never -- curl http://todo-backend:8000/health`
- [ ] T063 [US1] Deploy frontend via Helm: `helm install todo-frontend charts/todo-frontend --values charts/todo-frontend/values-dev.yaml --namespace todo-dev`
- [ ] T064 [US1] Verify frontend Helm release with `helm list -n todo-dev`
- [ ] T065 [US1] Wait for frontend pods to reach Running state with `kubectl get pods -n todo-dev | grep todo-frontend` (verify within 2 minutes)
- [ ] T066 [US1] Verify frontend service NodePort 30080 assigned with `kubectl get service -n todo-dev | grep todo-frontend`
- [ ] T067 [US1] Get Minikube IP with `minikube ip` and document access URL: http://<minikube-ip>:30080

### End-to-End Validation

- [ ] T068 [US1] Access frontend at http://<minikube-ip>:30080 and verify page loads within 5 seconds
- [ ] T069 [US1] Register new user via frontend /register page
- [ ] T070 [US1] Login with credentials via frontend /login page
- [ ] T071 [US1] Navigate to /chat page and verify ChatKit loads
- [ ] T072 [US1] Send test message "show my todos" to chatbot and verify response within 3 seconds
- [ ] T073 [US1] Verify chatbot functionality matches Phase III Hugging Face deployment performance
- [ ] T074 [US1] Check backend pod logs with `kubectl logs -n todo-dev -l app=todo-backend --tail=50` for errors
- [ ] T075 [US1] Check frontend pod logs with `kubectl logs -n todo-dev -l app=todo-frontend --tail=50` for errors
- [ ] T076 [US1] Verify health endpoints return 200 with `kubectl run -n todo-dev curl-test --image=curlimages/curl --rm -it --restart=Never -- curl http://todo-backend:8000/health`
- [ ] T077 [US1] Document deployment time from T058 to T067 (verify <15 minutes per SC-001)

**Checkpoint**: At this point, User Story 1 should be fully functional - complete Phase IV MVP deployment working on Minikube with end-to-end chatbot functionality validated

---

## Phase 4: User Story 2 - Container Image Optimization (Priority: P2)

**Goal**: Ensure containerized services are optimized for size, security, and Kubernetes deployment following cloud-native best practices

**Independent Test**: Inspect Docker images for size verification (<200MB backend, <100MB frontend), run security scans, verify non-root users, and confirm health checks functional - all measurable independently of deployment

### Image Size Optimization Validation

- [ ] T078 [P] [US2] Inspect backend image layers with `docker history todo-backend:v1.0.0` to verify multi-stage build structure
- [ ] T079 [P] [US2] Confirm backend final image size <200MB per SC-005 with `docker images todo-backend:v1.0.0 --format "{{.Size}}"`
- [ ] T080 [P] [US2] Inspect frontend image layers with `docker history todo-frontend:v1.0.0` to verify multi-stage build structure
- [ ] T081 [P] [US2] Confirm frontend final image size <100MB per SC-005 with `docker images todo-frontend:v1.0.0 --format "{{.Size}}"`
- [ ] T082 [US2] Document image sizes in charts/todo-backend/README.md and charts/todo-frontend/README.md

### Security Validation

- [ ] T083 [P] [US2] Verify backend container runs as non-root user with `docker inspect todo-backend:v1.0.0 | grep User` (should show UID 1000)
- [ ] T084 [P] [US2] Verify frontend container runs as non-root user with `docker inspect todo-frontend:v1.0.0 | grep User` (should show UID 1001)
- [ ] T085 [P] [US2] Run security scan on backend image with `docker scout cves todo-backend:v1.0.0` or trivy scan
- [ ] T086 [P] [US2] Run security scan on frontend image with `docker scout cves todo-frontend:v1.0.0` or trivy scan
- [ ] T087 [US2] Verify no critical/high vulnerabilities in base images per acceptance scenario 4
- [ ] T088 [US2] Document security scan results and remediation if needed

### Health Check Validation

- [ ] T089 [P] [US2] Test backend liveness probe locally: `docker run -d -p 8000:8000 todo-backend:v1.0.0` and curl http://localhost:8000/health
- [ ] T090 [P] [US2] Test frontend liveness probe locally: `docker run -d -p 3000:3000 todo-frontend:v1.0.0` and curl http://localhost:3000/
- [ ] T091 [US2] Verify health endpoints return HTTP 200 status within 1 second per SC-007
- [ ] T092 [US2] Confirm Kubernetes readiness probes configured correctly in Helm templates with proper initialDelaySeconds and periodSeconds

**Checkpoint**: At this point, User Story 2 complete - container images verified optimized, secure, and properly configured for Kubernetes health checks

---

## Phase 5: User Story 3 - Parameterized Helm Deployment (Priority: P2)

**Goal**: Validate Helm charts enable flexible deployment configurations through parameterization, supporting multiple environments and easy customization

**Independent Test**: Deploy with different values files, verify parameterization works (custom replicas, resources, env vars), test upgrade/rollback workflows - all testable independently using Helm commands

### Parameterization Testing

- [ ] T093 [P] [US3] Test backend chart with custom replica count: `helm upgrade todo-backend charts/todo-backend --set replicaCount=3 --values charts/todo-backend/values-dev.yaml --namespace todo-dev`
- [ ] T094 [P] [US3] Verify backend scaled to 3 replicas with `kubectl get pods -n todo-dev | grep todo-backend` (should show 3 pods)
- [ ] T095 [P] [US3] Test frontend chart with custom resources: `helm upgrade todo-frontend charts/todo-frontend --set resources.requests.memory=256Mi --values charts/todo-frontend/values-dev.yaml --namespace todo-dev`
- [ ] T096 [US3] Verify frontend resource changes applied with `kubectl describe deployment todo-frontend -n todo-dev | grep -A 5 "Requests"`
- [ ] T097 [US3] Test custom environment variable override: `helm upgrade todo-backend charts/todo-backend --set env.FRONTEND_URL=http://custom-frontend:3000 --values charts/todo-backend/values-dev.yaml --namespace todo-dev`
- [ ] T098 [US3] Verify environment variable change with `kubectl describe deployment todo-backend -n todo-dev | grep -A 10 "Environment"`

### Rolling Update Testing

- [ ] T099 [US3] Create minor backend code change (update health endpoint response)
- [ ] T100 [US3] Rebuild backend image: `docker build -t todo-backend:v1.0.1 ./backend`
- [ ] T101 [US3] Load new image into Minikube: `minikube image load todo-backend:v1.0.1`
- [ ] T102 [US3] Upgrade backend via Helm: `helm upgrade todo-backend charts/todo-backend --set image.tag=v1.0.1 --values charts/todo-backend/values-dev.yaml --namespace todo-dev`
- [ ] T103 [US3] Monitor rolling update with `kubectl rollout status deployment/todo-backend -n todo-dev`
- [ ] T104 [US3] Verify rolling update completes within 1 minute per SC-006
- [ ] T105 [US3] Test application functionality during update to verify zero request failures per SC-006
- [ ] T106 [US3] Verify new pods running v1.0.1 image with `kubectl describe pod -n todo-dev -l app=todo-backend | grep Image:`

### Rollback Testing

- [ ] T107 [US3] Execute Helm rollback to previous version: `helm rollback todo-backend 1 --namespace todo-dev`
- [ ] T108 [US3] Verify rollback completes with `kubectl rollout status deployment/todo-backend -n todo-dev`
- [ ] T109 [US3] Verify pods restored to v1.0.0 image with `kubectl describe pod -n todo-dev -l app=todo-backend | grep Image:`
- [ ] T110 [US3] Test application functionality after rollback

### Multi-Environment Testing

- [ ] T111 [US3] Create test namespace todo-staging: `kubectl create namespace todo-staging`
- [ ] T112 [US3] Create staging Secret with different DATABASE_URL in namespace todo-staging
- [ ] T113 [US3] Deploy backend to staging with different values: `helm install todo-backend-staging charts/todo-backend --set replicaCount=2 --values charts/todo-backend/values-dev.yaml --namespace todo-staging`
- [ ] T114 [US3] Verify both todo-dev and todo-staging deployments coexist independently
- [ ] T115 [US3] Verify staging deployment has 2 replicas while dev has configured replica count
- [ ] T116 [US3] Cleanup staging deployment: `helm uninstall todo-backend-staging -n todo-staging && kubectl delete namespace todo-staging`

**Checkpoint**: At this point, User Story 3 complete - Helm parameterization validated through custom deployments, rolling updates, rollbacks, and multi-environment testing

---

## Phase 6: User Story 4 - Service Discovery and Networking (Priority: P3)

**Goal**: Validate Kubernetes service discovery enables frontend-to-backend communication via DNS, and external access works correctly via NodePort

**Independent Test**: Verify frontend successfully calls backend using service DNS (http://todo-backend:8000), confirm external NodePort access functional, test service discovery survives pod restarts and scaling

### Service Discovery Validation

- [ ] T117 [P] [US4] Test backend service DNS resolution from frontend pod: `kubectl exec -n todo-dev deployment/todo-frontend -- nslookup todo-backend`
- [ ] T118 [P] [US4] Test frontend-to-backend API call using service DNS: `kubectl exec -n todo-dev deployment/todo-frontend -- curl http://todo-backend:8000/health`
- [ ] T119 [US4] Verify service ClusterIP assigned correctly with `kubectl get svc todo-backend -n todo-dev -o wide`
- [ ] T120 [US4] Verify service endpoints map to pod IPs with `kubectl get endpoints todo-backend -n todo-dev`

### External Access Validation

- [ ] T121 [P] [US4] Verify frontend accessible via NodePort with browser test at http://<minikube-ip>:30080
- [ ] T122 [P] [US4] Test API calls from frontend to backend work through browser DevTools Network tab
- [ ] T123 [US4] Verify NodePort assignment with `kubectl get svc todo-frontend -n todo-dev` (should show 30080:xxxxx/TCP)
- [ ] T124 [US4] Alternative access test: Use `minikube service todo-frontend -n todo-dev --url` to get service URL

### Service Discovery Resilience Testing

- [ ] T125 [US4] Scale backend to 3 replicas: `kubectl scale deployment todo-backend --replicas=3 -n todo-dev`
- [ ] T126 [US4] Wait for all backend pods Running: `kubectl wait --for=condition=Ready pod -l app=todo-backend -n todo-dev --timeout=60s`
- [ ] T127 [US4] Test service discovery still works with multiple backend pods: `kubectl exec -n todo-dev deployment/todo-frontend -- curl http://todo-backend:8000/health` (repeat 10 times)
- [ ] T128 [US4] Delete one backend pod: `kubectl delete pod -n todo-dev -l app=todo-backend --field-selector=status.phase=Running | head -1`
- [ ] T129 [US4] Verify service discovery continues working during pod restart: `kubectl exec -n todo-dev deployment/todo-frontend -- curl http://todo-backend:8000/health`
- [ ] T130 [US4] Verify new pod automatically added to service endpoints: `kubectl get endpoints todo-backend -n todo-dev`

### Network Configuration Documentation

- [ ] T131 [US4] Document service discovery patterns in charts/todo-backend/README.md (ClusterIP access via DNS)
- [ ] T132 [US4] Document external access pattern in charts/todo-frontend/README.md (NodePort access via minikube-ip)
- [ ] T133 [US4] Document service endpoint inspection commands for troubleshooting

**Checkpoint**: At this point, User Story 4 complete - Kubernetes networking validated including service discovery, external access, and resilience to pod changes

---

## Phase 7: User Story 5 - Operational Observability (Priority: P3)

**Goal**: Validate kubectl-ai and standard kubectl commands provide sufficient observability for monitoring health, viewing logs, and diagnosing failures

**Independent Test**: Use kubectl-ai natural language commands and standard kubectl to query deployment status, view logs, diagnose intentional failures, and analyze cluster health

### kubectl-ai Natural Language Operations

- [ ] T134 [P] [US5] Test deployment status query: `kubectl-ai show me deployment status summary for namespace todo-dev`
- [ ] T135 [P] [US5] Test pod health query: `kubectl-ai are all pods healthy in namespace todo-dev?`
- [ ] T136 [P] [US5] Test service listing: `kubectl-ai what services are running in namespace todo-dev?`
- [ ] T137 [US5] Test replica query: `kubectl-ai how many replicas does todo-backend have in namespace todo-dev?`
- [ ] T138 [US5] Document kubectl-ai command success rate (verify ≥95% per SC-008)

### Log Access and Monitoring

- [ ] T139 [P] [US5] View backend logs: `kubectl logs -n todo-dev -l app=todo-backend --tail=50`
- [ ] T140 [P] [US5] View frontend logs: `kubectl logs -n todo-dev -l app=todo-frontend --tail=50`
- [ ] T141 [US5] Test streaming logs: `kubectl logs -n todo-dev -l app=todo-backend --follow` (verify real-time updates)
- [ ] T142 [US5] Test kubectl-ai log access: `kubectl-ai show me recent logs from todo-backend pods in namespace todo-dev`
- [ ] T143 [US5] Verify structured logs show API requests and responses in backend logs

### Failure Diagnosis Testing

- [ ] T144 [US5] Create intentional failure: Remove required environment variable from backend deployment
- [ ] T145 [US5] Apply broken configuration: `kubectl set env deployment/todo-backend -n todo-dev DATABASE_URL-`
- [ ] T146 [US5] Observe pod enter CrashLoopBackOff: `kubectl get pods -n todo-dev | grep todo-backend`
- [ ] T147 [US5] Use kubectl-ai to diagnose: `kubectl-ai why is pod todo-backend-xxx failing in namespace todo-dev?`
- [ ] T148 [US5] Verify kubectl-ai provides actionable root cause (missing DATABASE_URL)
- [ ] T149 [US5] View failure logs: `kubectl logs -n todo-dev -l app=todo-backend --tail=20`
- [ ] T150 [US5] Restore configuration: `helm upgrade todo-backend charts/todo-backend --values charts/todo-backend/values-dev.yaml --namespace todo-dev`
- [ ] T151 [US5] Verify pods recover to Running state

### Cluster Health Analysis (kagent - optional)

- [ ] T152 [US5] If kagent available: Run `kagent analyze cluster health for namespace todo-dev`
- [ ] T153 [US5] If kagent available: Review resource usage report from kagent
- [ ] T154 [US5] If kagent available: Verify kagent identifies any potential issues
- [ ] T155 [US5] Document kagent findings (or note if unavailable)

### Scaling Operations via kubectl-ai

- [ ] T156 [US5] Scale backend using kubectl-ai: `kubectl-ai scale todo-backend to 5 replicas in namespace todo-dev`
- [ ] T157 [US5] Verify scaling completes within 30 seconds per SC-010: `kubectl get pods -n todo-dev | grep todo-backend`
- [ ] T158 [US5] Verify all 5 pods reach Ready state: `kubectl wait --for=condition=Ready pod -l app=todo-backend -n todo-dev --timeout=30s`
- [ ] T159 [US5] Test service load balancing across 5 replicas: Curl backend health endpoint 20 times and observe pod distribution

### Observability Documentation

- [ ] T160 [US5] Document common kubectl-ai commands in docs/operations.md or README
- [ ] T161 [US5] Document troubleshooting workflows (logs, describe, events) in charts/README files
- [ ] T162 [US5] Document scaling procedures using kubectl-ai and Helm

**Checkpoint**: At this point, User Story 5 complete - Operational observability validated through kubectl-ai, log access, failure diagnosis, and scaling operations

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, documentation, and validation across all user stories

- [ ] T163 [P] Update repository README.md with Phase IV deployment instructions
- [ ] T164 [P] Create comprehensive DEPLOYMENT.md guide covering all user stories
- [ ] T165 [P] Document prerequisites checklist (Minikube, Docker, Helm, kubectl versions)
- [ ] T166 [P] Document deployment time benchmarks from testing (verify SC-001: <15 minutes)
- [ ] T167 [P] Document image size metrics from US2 (backend <200MB, frontend <100MB per SC-005)
- [ ] T168 [P] Create troubleshooting guide with common issues and resolutions
- [ ] T169 [P] Document cleanup procedures: `helm uninstall`, `kubectl delete namespace`, `minikube stop/delete`
- [ ] T170 Create Phase IV completion report summarizing all success criteria validations
- [ ] T171 Verify all 10 success criteria met (SC-001 through SC-010)
- [ ] T172 Create ADR for Multi-Stage Docker Builds (ADR-001 from plan.md)
- [ ] T173 Create ADR for Helm Charts Parameterization (ADR-002 from plan.md)
- [ ] T174 Create ADR for NodePort vs ClusterIP Service Strategy (ADR-003 from plan.md)
- [ ] T175 Create ADR for External PostgreSQL Database (ADR-004 from plan.md)
- [ ] T176 Create ADR for AI-Assisted Infrastructure Generation (ADR-005 from plan.md)
- [ ] T177 Run final validation: Deploy to fresh Minikube cluster and verify first-attempt success per SC-009
- [ ] T178 Cleanup test deployments and document Phase IV artifacts (Dockerfiles, Helm charts, documentation)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after US1 containers built (T022, T032) - Tests optimization independently
  - User Story 3 (P2): Can start after US1 Helm charts generated (T047, T057) - Tests parameterization independently
  - User Story 4 (P3): Can start after US1 deployment complete (T067) - Tests networking of running system
  - User Story 5 (P3): Can start after US1 deployment complete (T067) - Tests operations on running system
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation only - delivers complete MVP deployment ✅ MVP READY
- **User Story 2 (P2)**: Requires US1 containers (T022, T032) - independently tests image optimization
- **User Story 3 (P2)**: Requires US1 Helm charts (T047, T057) - independently tests parameterization
- **User Story 4 (P3)**: Requires US1 running deployment (T067) - independently tests networking
- **User Story 5 (P3)**: Requires US1 running deployment (T067) - independently tests operations

### Within Each User Story

**User Story 1** (MVP):
1. Backend containerization (T017-T026) can run parallel with frontend (T027-T035)
2. Backend Helm chart (T036-T047) can run parallel with frontend Helm chart (T048-T057)
3. After both charts ready → Deploy backend (T058-T062) THEN frontend (T063-T067)
4. End-to-end validation (T068-T077) must run sequentially after deployment

**User Story 2** (Optimization):
- All validation tasks (T078-T092) can run in parallel since they inspect existing artifacts

**User Story 3** (Parameterization):
- Parameterization tests (T093-T098) can run in parallel
- Rolling update (T099-T106) must run sequentially
- Rollback test (T107-T110) depends on rolling update
- Multi-environment (T111-T116) can run after parameterization tests

**User Story 4** (Networking):
- Service discovery validation (T117-T120) can run in parallel
- External access (T121-T124) can run in parallel with service discovery
- Resilience testing (T125-T130) must run sequentially
- Documentation (T131-T133) can run anytime

**User Story 5** (Observability):
- kubectl-ai tests (T134-T138) can run in parallel
- Log access (T139-T143) can run in parallel
- Failure diagnosis (T144-T151) must run sequentially
- Scaling operations (T156-T159) can run after failure tests

### Parallel Opportunities

**Setup Phase**:
- T005 (kubectl-ai check) parallel with T006 (kagent check)

**Foundational Phase**:
- T011-T014 (namespace and Secret creation) sequential
- T015-T016 (documentation) can run parallel with T014

**User Story 1 - Backend & Frontend Parallel**:
```bash
# Backend containerization
Task Group A: T017, T018, T019 → T020 → T021 → T022 → T023 → T024 → T025 → T026

# Frontend containerization (parallel with backend)
Task Group B: T027, T028, T029 → T030 → T031 → T032 → T033 → T034 → T035

# After both complete, Helm charts
Task Group C: T036, T037 → T038 → T039 → T040-T047 (backend Helm)
Task Group D: T048, T049 → T050 → T051 → T052-T057 (frontend Helm - parallel with backend Helm)
```

**User Story 2 - All Validations Parallel**:
```bash
# Image size checks
Parallel: T078, T079, T080, T081

# Security checks
Parallel: T083, T084, T085, T086

# Health checks
Parallel: T089, T090
```

**Polish Phase**:
```bash
# Documentation tasks all parallel
Parallel: T163, T164, T165, T166, T167, T168, T169
```

---

## Parallel Example: User Story 1 MVP Deployment

```bash
# Step 1: Containerization (parallel streams)
Stream A (Backend):
  T017 → T018 → T019 → T020 → T021 → T022 → T023 → T024 → T025 → T026

Stream B (Frontend):
  T027 → T028 → T029 → T030 → T031 → T032 → T033 → T034 → T035

# Step 2: Helm Charts (parallel after Step 1)
Stream C (Backend Helm):
  T036 → T037 → T038 → T039 → T040 → T041 → T042 → T043 → T044 → T045 → T046 → T047

Stream D (Frontend Helm - parallel with C):
  T048 → T049 → T050 → T051 → T052 → T053 → T054 → T055 → T056 → T057

# Step 3: Deployment (sequential)
  T058 → T059 → T060 → T061 → T062 → T063 → T064 → T065 → T066 → T067

# Step 4: Validation (sequential)
  T068 → T069 → T070 → T071 → T072 → T073 → T074 → T075 → T076 → T077
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) ⭐ RECOMMENDED

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T016) - CRITICAL
3. Complete Phase 3: User Story 1 (T017-T077) - Full MVP deployment
4. **STOP and VALIDATE**: Test complete deployment end-to-end
5. **SUCCESS**: Working Minikube deployment with frontend and backend ✅

**Estimated Time**: 2-4 hours for experienced developer

**Deliverable**: Complete Phase IV MVP - locally deployed Todo AI Chatbot on Kubernetes

### Incremental Delivery (Add Validation Stories)

After MVP complete, add validation stories incrementally:

1. **Foundation + US1** → Working deployment ✅ MVP
2. **+ US2** → Validated image optimization and security
3. **+ US3** → Validated Helm parameterization and upgrade/rollback
4. **+ US4** → Validated networking and service discovery
5. **+ US5** → Validated operational observability
6. **+ Polish** → Complete documentation and ADRs

Each addition validates a specific aspect without breaking previous functionality.

### Parallel Team Strategy

With multiple developers or agents:

1. **Team completes Setup + Foundational together** (T001-T016)
2. **Once Foundational done, parallel work**:
   - Developer A: User Story 1 (T017-T077) - MVP deployment
   - Developer B: Prepare for US2 - Image optimization validation scripts
   - Developer C: Prepare for US3 - Helm testing procedures
3. **After US1 complete**:
   - Developer B: Execute US2 (T078-T092)
   - Developer C: Execute US3 (T093-T116)
   - Developer A: Start US4 (T117-T133)
4. **Final validation**:
   - Any developer: US5 (T134-T162)
   - All together: Polish (T163-T178)

---

## Notes

- **[P]** tasks = different files or independent validations, no dependencies
- **[Story]** label maps task to specific user story for traceability (US1-US5)
- Each user story should be independently completable and testable
- User Story 1 is the MVP - delivers complete working deployment
- User Stories 2-5 are validation and enhancement stories
- Commit after each logical task group
- Stop at any checkpoint to validate story independently
- Phase IV heavily emphasizes operational validation over unit testing
- kubectl-ai commands may require adaptation based on tool version
- Docker AI (Gordon) may be unavailable - fallback to Claude Code documented in tasks
- Total estimated time: 6-10 hours for complete Phase IV (all 5 user stories + polish)
