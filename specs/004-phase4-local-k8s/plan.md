# Implementation Plan: Phase IV Local Kubernetes Deployment

**Branch**: `004-phase4-local-k8s` | **Date**: 2026-02-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/004-phase4-local-k8s/spec.md`

**Note**: This plan follows the Spec-Driven Development workflow. See `.specify/templates/commands/plan.md` for execution workflow.

---

## 1. Planning Overview

### Summary

Deploy the Phase III Todo AI Chatbot application (FastAPI backend + Next.js frontend) to a local Minikube Kubernetes cluster using AI-assisted infrastructure tooling, enabling cloud-native development patterns and infrastructure validation in a local environment that mirrors production Kubernetes.

### Technical Approach from Research

**AI-First Infrastructure**: All infrastructure artifacts (Dockerfiles, Kubernetes manifests, Helm charts) will be generated using AI-assisted tools:
- **Docker AI Agent "Gordon"** (preferred) or **Claude Code** (fallback) for Dockerfile generation
- **kubectl-ai** for natural language Kubernetes operations
- **Helm 3** for parameterized deployment packaging
- **kagent** for cluster health analysis and AIOps validation

**Containerization Strategy**: Multi-stage Docker builds optimized for size and security, running as non-root users with health check endpoints exposed for Kubernetes liveness/readiness probes.

**Deployment Model**: Helm charts package all Kubernetes resources (Deployment, Service, ConfigMap, Secrets templates) with environment-specific values files for Minikube overrides.

**Success Definition**: Complete deployment workflow (build → chart → deploy) completes in under 15 minutes with all pods reaching Running state within 2 minutes, frontend accessible via NodePort, and end-to-end chatbot functionality matching Phase III performance (<3 seconds response time).

---

## 2. Technical Context

**Language/Version**: Python 3.11+ (backend), Node.js 18+ / TypeScript 5+ (frontend)

**Primary Dependencies**:
- Backend: FastAPI 0.115.0, SQLModel 0.0.22, OpenAI SDK >=1.30.0, MCP SDK >=1.0.0, uvicorn[standard] 0.32.0
- Frontend: Next.js ^15.1.3, React ^19.0.0, jose ^5.9.6 (JWT handling)

**Storage**: External Neon Serverless PostgreSQL (not containerized in Phase IV), frontend uses sessionStorage for conversation_id persistence only

**Testing**: pytest (backend), Jest/React Testing Library (frontend), Kubernetes deployment validation via kubectl-ai and kagent

**Target Platform**: Linux Minikube cluster (single-node, Kubernetes v1.28+), Docker Desktop or Minikube container runtime

**Project Type**: Web application (frontend + backend services)

**Performance Goals**:
- Container image sizes: Backend <200MB, Frontend <100MB
- Deployment time: <15 minutes end-to-end
- Pod startup: <2 minutes to Running state
- Application responsiveness: Frontend loads <5 seconds, chatbot responses <3 seconds

**Constraints**:
- AI-assisted tooling mandatory (no manual Dockerfile/YAML authoring)
- Minikube resource limits: 2-4 CPU cores, 4-8GB RAM
- External dependencies (PostgreSQL, OpenAI API) not containerized
- NodePort service exposure (no cloud LoadBalancer available)

**Scale/Scope**:
- 2 services (frontend, backend)
- Initial replica count: 1 per service (scalable to 5 via kubectl-ai)
- Single namespace: `todo-dev`
- Development/testing workload (not production-grade)

---

## 3. Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Constitutional Compliance Review

**Spec-Driven Development Adherence**:
- ✅ Specification created and validated (23 functional requirements, 10 success criteria)
- ✅ Planning phase underway with architecture design
- ✅ Human approval gate enforced before task generation
- ✅ Implementation deferred until `/sp.tasks` completion

**AI-First Infrastructure Mandate**:
- ✅ All infrastructure artifacts must be AI-generated per FR-001, FR-006, FR-011
- ✅ infra-spec-guardian agent validates compliance before execution
- ✅ Manual authoring of Dockerfiles, YAML, Helm charts prohibited

**Phase Isolation**:
- ✅ Phase IV scope clearly bounded (local Minikube only)
- ✅ No scope creep into Phase V (production Kubernetes)
- ✅ External dependencies from Phase III reused (Neon DB, OpenAI API)

**Human-in-the-Loop Governance**:
- ✅ Approval required at spec, plan, tasks phases
- ✅ Infra-spec-guardian provides APPROVED/REJECTED verdicts before actions
- ✅ No autonomous infrastructure changes without validation

**No Violations Detected**: All constitutional principles satisfied. Phase IV design aligns with project governance policies.

---

## 4. Project Structure

### Documentation (this feature)

```text
specs/004-phase4-local-k8s/
├── spec.md                      # Feature specification (approved 2026-02-03)
├── plan.md                      # This file - implementation plan
├── checklists/
│   └── requirements.md          # Specification validation checklist (14/14 passed)
├── tasks.md                     # Task breakdown (/sp.tasks output - NOT YET CREATED)
└── research.md                  # Research findings (if needed)
```

### Source Code (repository root)

**Option 2: Web application** (frontend + backend detected)

```text
backend/
├── app/
│   ├── routers/
│   │   ├── auth.py              # JWT authentication endpoints
│   │   ├── todos.py             # Traditional REST API (Phase II)
│   │   └── chat.py              # AI chatbot endpoint (Phase III)
│   ├── models/
│   │   ├── user.py              # User SQLModel
│   │   ├── todo.py              # Todo SQLModel
│   │   ├── conversation.py      # Conversation SQLModel
│   │   └── message.py           # Message SQLModel
│   ├── agent/
│   │   ├── runner.py            # OpenAI Agent Runner
│   │   ├── prompts.py           # System prompts
│   │   └── intent_classifier.py # Intent classification
│   ├── mcp/
│   │   ├── server.py            # MCP server setup
│   │   ├── tools.py             # MCP tool implementations
│   │   └── schemas.py           # MCP schemas
│   ├── auth/
│   │   ├── jwt.py               # JWT token handling
│   │   ├── password.py          # Password hashing
│   │   └── dependencies.py      # Auth dependencies
│   ├── services/
│   │   └── conversation.py      # Conversation service
│   ├── config.py                # Settings via pydantic-settings
│   └── database.py              # SQLModel database connection
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
└── Dockerfile                   # **TO BE CREATED BY DOCKERIZATION-AGENT**

frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx             # Home page with todo list
│   │   ├── layout.tsx           # Root layout
│   │   ├── login/
│   │   │   └── page.tsx         # Login page
│   │   ├── register/
│   │   │   └── page.tsx         # Register page
│   │   └── chat/
│   │       └── page.tsx         # ChatKit integration page (Phase III)
│   ├── components/
│   │   ├── TodoList.tsx         # Todo list component
│   │   ├── AuthForm.tsx         # Authentication form
│   │   └── ChatInterface.tsx    # ChatKit wrapper
│   └── lib/
│       ├── api.ts               # Backend API client
│       └── auth.ts              # JWT token management
├── package.json                 # Node dependencies
├── next.config.js               # Next.js configuration
├── .env.example                 # Environment variable template
└── Dockerfile                   # **TO BE CREATED BY DOCKERIZATION-AGENT**

charts/                          # **TO BE CREATED BY HELM-CHART-ARCHITECT**
├── todo-backend/
│   ├── Chart.yaml               # Helm chart metadata
│   ├── values.yaml              # Default configuration values
│   ├── values-dev.yaml          # Minikube-specific overrides
│   ├── templates/
│   │   ├── deployment.yaml      # Backend Deployment manifest
│   │   ├── service.yaml         # Backend Service (ClusterIP)
│   │   ├── configmap.yaml       # Non-sensitive config
│   │   ├── secrets.yaml         # Secret template (values injected at deploy)
│   │   ├── hpa.yaml             # HorizontalPodAutoscaler
│   │   └── _helpers.tpl         # Reusable template functions
│   └── README.md                # Installation and usage docs
└── todo-frontend/
    ├── Chart.yaml
    ├── values.yaml
    ├── values-dev.yaml
    ├── templates/
    │   ├── deployment.yaml      # Frontend Deployment manifest
    │   ├── service.yaml         # Frontend Service (NodePort)
    │   ├── configmap.yaml
    │   └── _helpers.tpl
    └── README.md

tests/
├── backend/
│   ├── integration/
│   │   └── test_k8s_backend.py  # Backend Kubernetes integration tests
│   └── unit/
│       └── test_docker_build.py # Docker build validation tests
└── frontend/
    └── integration/
        └── test_k8s_frontend.py # Frontend Kubernetes integration tests

.dockerignore                    # **TO BE CREATED (backend/frontend root)**
```

**Structure Decision**: Web application structure selected based on existing Phase III codebase with `backend/` and `frontend/` directories. New `charts/` directory will contain Helm chart packages for both services. Dockerfiles will be placed in service roots (`backend/Dockerfile`, `frontend/Dockerfile`). All infrastructure artifacts will be AI-generated following Phase IV specification requirements.

---

## 5. Complexity Tracking

**No Constitutional Violations Requiring Justification**

Phase IV design adheres to all constitutional principles without requiring complexity exceptions. All infrastructure work follows AI-first mandate with proper human-in-the-loop governance.

---

## 6. Codebase Analysis Summary

### Backend Architecture (FastAPI)

**Entry Point**: `backend/main.py`
- FastAPI application with CORS middleware
- ReverseProxyMiddleware for Hugging Face Spaces compatibility (X-Forwarded-Prefix handling)
- Health endpoint: `GET /health` returns `{"status": "healthy"}`
- Configurable port: 7860 (Hugging Face) or 8000 (local development)

**API Routes**:
- `/api/auth/` - JWT authentication (login, register)
- `/api/{user_id}/todos/` - Traditional REST API for todo CRUD (Phase II)
- `/api/{user_id}/chat/` - AI chatbot endpoint using OpenAI Agent Runner + MCP tools (Phase III)

**Database Models** (SQLModel):
- `User`: Authentication and user management
- `Todo`: Todo items with user ownership
- `Conversation`: Chatbot conversation tracking
- `Message`: Individual messages in conversations

**External Dependencies**:
- Neon PostgreSQL: `DATABASE_URL` environment variable required
- OpenAI API: `OPENAI_API_KEY` environment variable required
- JWT: `SECRET_KEY` environment variable required

**Containerization Requirements**:
- Python 3.11+ runtime
- Dependencies from `requirements.txt` (FastAPI, SQLModel, OpenAI SDK, MCP SDK)
- Health endpoint `/health` for Kubernetes probes
- Port 8000 exposure (standardize on local port, not HF Spaces 7860)
- Environment variables: DATABASE_URL, SECRET_KEY, OPENAI_API_KEY, FRONTEND_URL

### Frontend Architecture (Next.js)

**Entry Point**: Next.js 15 App Router
- React 19.0.0 with TypeScript
- Tailwind CSS for styling
- JWT authentication using `jose` library

**Pages**:
- `/` - Home page with todo list (requires authentication)
- `/login` - Login form
- `/register` - Registration form
- `/chat` - ChatKit-based AI chatbot interface (Phase III)

**API Integration**:
- Backend API client in `src/lib/api.ts`
- JWT token management in `src/lib/auth.ts`
- Conversation ID persistence via sessionStorage

**External Dependencies**:
- Backend API: `NEXT_PUBLIC_API_URL` environment variable
- ChatKit API: `NEXT_PUBLIC_CHAT_API_URL` environment variable (Phase III)
- OpenAI Domain Key: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` for ChatKit allowlist

**Containerization Requirements**:
- Node.js 18+ for build stage
- Production server (next start or nginx for static export)
- Port 3000 exposure
- Environment variables injected at runtime via NEXT_PUBLIC_* prefix

### Phase III Chatbot Integration Points

**Backend Chatbot Flow** (`backend/app/routers/chat.py`):
1. Receive POST `/api/{user_id}/chat` with message and optional conversation_id
2. Load conversation history from PostgreSQL
3. Invoke OpenAI Agent Runner with MCP tools (add_task, list_tasks, update_task, complete_task, delete_task)
4. Save conversation and messages to PostgreSQL
5. Return response with conversation_id and assistant message

**Frontend Chatbot Flow** (`frontend/src/app/chat/page.tsx`):
1. Load ChatKit component with OpenAI configuration
2. Persist conversation_id in sessionStorage for continuity
3. Send messages to `NEXT_PUBLIC_CHAT_API_URL` endpoint
4. Display responses in ChatKit UI

**Critical Configuration**:
- Backend must be accessible from frontend (ClusterIP service with Kubernetes DNS)
- Frontend must expose NodePort for browser access
- Environment variables must propagate correctly through ConfigMaps/Secrets

---

## 7. Containerization Strategy

### Backend Containerization (FastAPI + Python 3.11)

**Base Image Selection**:
- **Build Stage**: `python:3.11-slim` (Debian-based, includes build tools)
- **Runtime Stage**: `python:3.11-slim` (minimal attack surface)

**Multi-Stage Build Design**:
1. **Stage 1 (builder)**:
   - Copy `requirements.txt`
   - Install build dependencies (gcc, python3-dev for compiled packages)
   - Install Python packages to `/opt/venv`

2. **Stage 2 (runtime)**:
   - Copy virtual environment from builder stage
   - Create non-root user `appuser` (UID 1000)
   - Copy application code to `/app`
   - Set ownership to `appuser:appuser`
   - Expose port 8000
   - Health check: `curl -f http://localhost:8000/health || exit 1`
   - CMD: `uvicorn main:app --host 0.0.0.0 --port 8000`

**Security Hardening**:
- Run as non-root user (UID 1000)
- No secrets baked into image (inject via Kubernetes Secrets)
- Minimal base image (python:3.11-slim ~150MB final size)
- Pin dependency versions in requirements.txt

**Environment Variables** (externalized):
- `DATABASE_URL`: PostgreSQL connection string (from Secret)
- `SECRET_KEY`: JWT signing key (from Secret)
- `OPENAI_API_KEY`: OpenAI API key (from Secret)
- `FRONTEND_URL`: CORS origin (from ConfigMap, defaults to `http://localhost:3000`)

**Health Endpoints**:
- Liveness probe: `GET /health` (returns 200 if application is running)
- Readiness probe: `GET /health` (same endpoint, validates database connectivity in future enhancement)

**Build Command** (AI-generated via dockerization-agent):
```bash
docker build -t todo-backend:v1.0.0 ./backend
docker tag todo-backend:v1.0.0 todo-backend:latest
```

**Target Image Size**: <200MB (Success Criteria SC-005)

---

### Frontend Containerization (Next.js + Node 18)

**Base Image Selection**:
- **Build Stage**: `node:18-alpine` (lightweight, includes npm)
- **Runtime Stage**: `node:18-alpine` or `nginx:alpine` (depends on deployment mode)

**Multi-Stage Build Design**:

**Option A: Next.js Standalone Mode** (Recommended for Kubernetes)
1. **Stage 1 (dependencies)**:
   - Copy `package.json`, `package-lock.json`
   - Run `npm ci` to install dependencies

2. **Stage 2 (builder)**:
   - Copy source code
   - Set `NEXT_PUBLIC_*` build-time environment variables
   - Run `npm run build`
   - Next.js generates standalone server in `.next/standalone/`

3. **Stage 3 (runtime)**:
   - Copy standalone server from builder
   - Create non-root user `nextjs` (UID 1001)
   - Expose port 3000
   - CMD: `node server.js`

**Option B: Static Export + nginx** (Alternative)
- Export static site via `next export`
- Serve with nginx:alpine
- Smaller image size but loses SSR capabilities

**Recommendation**: Use **Option A (Standalone Mode)** to preserve Server-Side Rendering and API route capabilities used in ChatKit integration.

**Security Hardening**:
- Run as non-root user `nextjs` (UID 1001)
- No secrets in image (NEXT_PUBLIC_* vars injected at build time via ConfigMap)
- Minimal base image (node:18-alpine ~180MB with Next.js standalone)

**Environment Variables**:
- Build-time (baked into bundle):
  - `NEXT_PUBLIC_API_URL`: Backend API base URL (from ConfigMap, e.g., `http://todo-backend:8000`)
  - `NEXT_PUBLIC_CHAT_API_URL`: Chatbot API URL (from ConfigMap)
  - `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`: OpenAI domain allowlist key (from ConfigMap)

**Health Endpoints**:
- Liveness probe: `GET /` (returns 200 if Next.js server is running)
- Readiness probe: `GET /` (same endpoint, validates application is ready to serve traffic)

**Build Command** (AI-generated via dockerization-agent):
```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://todo-backend:8000 \
  --build-arg NEXT_PUBLIC_CHAT_API_URL=http://todo-backend:8000/api \
  --build-arg NEXT_PUBLIC_OPENAI_DOMAIN_KEY=<placeholder> \
  -t todo-frontend:v1.0.0 ./frontend
docker tag todo-frontend:v1.0.0 todo-frontend:latest
```

**Target Image Size**: <100MB (Success Criteria SC-005)

---

### .dockerignore Configuration

**Backend `.dockerignore`**:
```
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
.env
.env.local
*.log
.git/
.gitignore
README.md
tests/
docs/
```

**Frontend `.dockerignore`**:
```
node_modules/
.next/
.env
.env.local
*.log
.git/
.gitignore
README.md
tests/
```

---

## 8. Helm Chart Architecture

### Chart Structure Overview

Two independent Helm charts will be created:
1. **`charts/todo-backend/`**: Backend FastAPI service
2. **`charts/todo-frontend/`**: Frontend Next.js service

Each chart follows standard Helm 3 structure with parameterized values for environment-specific deployments.

---

### Backend Helm Chart (`charts/todo-backend/`)

**Chart.yaml**:
```yaml
apiVersion: v2
name: todo-backend
description: FastAPI backend for Todo AI Chatbot
type: application
version: 1.0.0
appVersion: "v1.0.0"
```

**values.yaml** (default configuration):
```yaml
replicaCount: 1

image:
  repository: todo-backend
  tag: v1.0.0
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8000
  targetPort: 8000

resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"

livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5

env:
  DATABASE_URL: ""  # Injected from Secret
  SECRET_KEY: ""    # Injected from Secret
  OPENAI_API_KEY: "" # Injected from Secret
  FRONTEND_URL: "http://localhost:3000"

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 80
```

**values-dev.yaml** (Minikube overrides):
```yaml
replicaCount: 1

resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "250m"

env:
  FRONTEND_URL: "http://todo-frontend:3000"
```

**templates/deployment.yaml**:
- Kubernetes Deployment manifest
- Parameterized replicas, image, resources, probes
- Environment variables from ConfigMap and Secret
- Pod template with labels and selectors
- Rolling update strategy (maxSurge: 1, maxUnavailable: 0)

**templates/service.yaml**:
- ClusterIP service exposing port 8000
- Selector matches Deployment pod labels
- Internal DNS: `todo-backend.todo-dev.svc.cluster.local`

**templates/configmap.yaml**:
- Non-sensitive configuration (FRONTEND_URL)

**templates/secrets.yaml**:
- Template for Secret creation (values not included in chart)
- Fields: DATABASE_URL, SECRET_KEY, OPENAI_API_KEY
- Values must be base64-encoded and injected at deployment time

**templates/hpa.yaml** (optional):
- HorizontalPodAutoscaler for autoscaling
- Enabled via `autoscaling.enabled: true`
- Requires Metrics Server installed in cluster

**templates/_helpers.tpl**:
- Reusable template functions:
  - `todo-backend.name`: Chart name
  - `todo-backend.fullname`: Release name + chart name
  - `todo-backend.labels`: Standard Kubernetes labels
  - `todo-backend.selectorLabels`: Pod selector labels

**README.md**:
- Installation instructions
- Configuration options
- Example deployment commands
- Secret creation instructions

---

### Frontend Helm Chart (`charts/todo-frontend/`)

**Chart.yaml**:
```yaml
apiVersion: v2
name: todo-frontend
description: Next.js frontend for Todo AI Chatbot
type: application
version: 1.0.0
appVersion: "v1.0.0"
```

**values.yaml** (default configuration):
```yaml
replicaCount: 1

image:
  repository: todo-frontend
  tag: v1.0.0
  pullPolicy: IfNotPresent

service:
  type: NodePort
  port: 3000
  targetPort: 3000
  nodePort: 30080  # Fixed NodePort for predictable access

resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "250m"

livenessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 5

env:
  NEXT_PUBLIC_API_URL: "http://todo-backend:8000"
  NEXT_PUBLIC_CHAT_API_URL: "http://todo-backend:8000/api"
  NEXT_PUBLIC_OPENAI_DOMAIN_KEY: ""  # From ConfigMap

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 3
  targetCPUUtilizationPercentage: 80
```

**values-dev.yaml** (Minikube overrides):
```yaml
replicaCount: 1

service:
  nodePort: 30080  # Consistent NodePort for Minikube

resources:
  requests:
    memory: "64Mi"
    cpu: "50m"
  limits:
    memory: "128Mi"
    cpu: "150m"
```

**templates/deployment.yaml**:
- Kubernetes Deployment manifest
- Parameterized replicas, image, resources, probes
- Build-time environment variables (NEXT_PUBLIC_*) baked into image
- Pod template with labels and selectors

**templates/service.yaml**:
- NodePort service exposing port 3000
- Fixed NodePort 30080 for consistent access URL
- Accessible via `http://<minikube-ip>:30080`

**templates/configmap.yaml**:
- Build-time configuration for NEXT_PUBLIC_* variables

**templates/_helpers.tpl**:
- Reusable template functions (same pattern as backend)

**README.md**:
- Installation instructions
- Accessing frontend via NodePort
- Configuration options

---

### Deployment Workflow via Helm

**Namespace Creation**:
```bash
kubectl create namespace todo-dev
```

**Secret Creation** (manual step before Helm install):
```bash
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@host/db" \
  --from-literal=SECRET_KEY="your-secret-key" \
  --from-literal=OPENAI_API_KEY="sk-..." \
  -n todo-dev
```

**Backend Deployment**:
```bash
helm install todo-backend charts/todo-backend \
  --values charts/todo-backend/values-dev.yaml \
  --namespace todo-dev
```

**Frontend Deployment**:
```bash
helm install todo-frontend charts/todo-frontend \
  --values charts/todo-frontend/values-dev.yaml \
  --namespace todo-dev
```

**Upgrade Example**:
```bash
helm upgrade todo-backend charts/todo-backend \
  --values charts/todo-backend/values-dev.yaml \
  --namespace todo-dev
```

**Rollback Example**:
```bash
helm rollback todo-backend 1 --namespace todo-dev
```

---

## 9. Deployment Sequence Plan

### Phase 0: Prerequisites Validation

**Human Action**: Verify infrastructure prerequisites are installed and operational.

**Checklist**:
- [ ] Minikube installed (v1.30+)
- [ ] Docker installed (v24.0+)
- [ ] Helm installed (v3.14+)
- [ ] kubectl installed (v1.28+)
- [ ] kubectl-ai installed (v0.5+) - optional but recommended
- [ ] Docker AI (Gordon) available OR Claude Code accessible as fallback
- [ ] kagent installed - optional but recommended for validation

**Validation Commands**:
```bash
minikube version   # Should show v1.30+
docker --version   # Should show 24.0+
helm version       # Should show v3.14+
kubectl version    # Should show v1.28+
kubectl-ai --version  # Optional
kagent --version      # Optional
```

**Start Minikube** (if not running):
```bash
minikube start --cpus=4 --memory=8192 --kubernetes-version=v1.28.0
minikube status    # Verify cluster is running
```

**Enable Minikube Docker Daemon** (for local image loading):
```bash
eval $(minikube docker-env)  # Use Minikube's Docker daemon
```

**Gate**: All prerequisites installed and Minikube cluster running. Proceed to Phase 1.

---

### Phase 1: Containerization (dockerization-agent)

**Agent**: `dockerization-agent` (invoked via `/sp.tasks` or direct skill invocation)

**Input Requirements**:
- Phase III codebase at `backend/` and `frontend/`
- `backend/requirements.txt` and `frontend/package.json`
- `.env.example` files for environment variable reference

**Tasks**:

**1.1 Analyze Backend Structure**:
- Read `backend/main.py`, `backend/requirements.txt`, `backend/.env.example`
- Identify Python version (3.11), dependencies, health endpoint (`/health`), port (8000)
- Determine environment variables (DATABASE_URL, SECRET_KEY, OPENAI_API_KEY, FRONTEND_URL)

**1.2 Generate Backend Dockerfile**:
- Use Docker AI (Gordon) or Claude Code fallback
- Prompt: "Create optimized multi-stage Dockerfile for Python 3.11 FastAPI application with uvicorn server, non-root user, health check on /health, port 8000"
- Output: `backend/Dockerfile`
- Include health check: `HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1`
- Validate: Final image runs as non-root, exposes port 8000, includes all dependencies

**1.3 Generate Backend .dockerignore**:
- Create `backend/.dockerignore` excluding venv/, tests/, .env, __pycache__/, *.log

**1.4 Build Backend Image**:
```bash
cd backend
docker build -t todo-backend:v1.0.0 .
docker tag todo-backend:v1.0.0 todo-backend:latest
docker images | grep todo-backend  # Verify image <200MB
```

**1.5 Analyze Frontend Structure**:
- Read `frontend/package.json`, `frontend/next.config.js`, `frontend/.env.example`
- Identify Node version (18), framework (Next.js 15), build command (`npm run build`), port (3000)
- Determine build-time environment variables (NEXT_PUBLIC_API_URL, NEXT_PUBLIC_CHAT_API_URL, NEXT_PUBLIC_OPENAI_DOMAIN_KEY)

**1.6 Generate Frontend Dockerfile**:
- Use Docker AI (Gordon) or Claude Code fallback
- Prompt: "Create optimized multi-stage Dockerfile for Next.js 15 application with standalone mode, non-root user, port 3000, include NEXT_PUBLIC_* build args"
- Output: `frontend/Dockerfile`
- Validate: Final image runs as non-root, exposes port 3000, standalone server functional

**1.7 Generate Frontend .dockerignore**:
- Create `frontend/.dockerignore` excluding node_modules/, .next/, .env, *.log

**1.8 Build Frontend Image**:
```bash
cd frontend
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://todo-backend:8000 \
  --build-arg NEXT_PUBLIC_CHAT_API_URL=http://todo-backend:8000/api \
  --build-arg NEXT_PUBLIC_OPENAI_DOMAIN_KEY=placeholder \
  -t todo-frontend:v1.0.0 .
docker tag todo-frontend:v1.0.0 todo-frontend:latest
docker images | grep todo-frontend  # Verify image <100MB
```

**1.9 Load Images into Minikube**:
```bash
minikube image load todo-backend:v1.0.0
minikube image load todo-frontend:v1.0.0
minikube image ls | grep todo  # Verify images available in Minikube
```

**Outputs**:
- `backend/Dockerfile` (multi-stage, non-root, <200MB)
- `backend/.dockerignore`
- `frontend/Dockerfile` (multi-stage, non-root, <100MB)
- `frontend/.dockerignore`
- Docker images: `todo-backend:v1.0.0`, `todo-frontend:v1.0.0` loaded in Minikube

**Validation**:
- Images build successfully without errors
- Image sizes meet SC-005 (<200MB backend, <100MB frontend)
- Images run as non-root users (inspect with `docker inspect`)
- Health endpoints functional (`docker run -p 8000:8000 todo-backend:v1.0.0` and `curl localhost:8000/health`)

**Gate**: Docker images built, validated, and loaded into Minikube. Proceed to Phase 2.

---

### Phase 2: Helm Chart Generation (helm-chart-architect)

**Agent**: `helm-chart-architect` (invoked via `/sp.tasks` or direct skill invocation)

**Input Requirements**:
- Docker images: `todo-backend:v1.0.0`, `todo-frontend:v1.0.0`
- Image metadata: ports (8000, 3000), health endpoints, environment variables

**Tasks**:

**2.1 Create Backend Helm Chart Structure**:
```bash
mkdir -p charts/todo-backend/templates
```

**2.2 Generate Backend Chart Metadata** (`charts/todo-backend/Chart.yaml`):
- Chart name: `todo-backend`
- Version: `1.0.0`
- appVersion: `v1.0.0`
- Description: "FastAPI backend for Todo AI Chatbot"

**2.3 Generate Backend Default Values** (`charts/todo-backend/values.yaml`):
- Image: `todo-backend:v1.0.0`
- ReplicaCount: 1
- Service type: ClusterIP, port 8000
- Resource requests/limits
- Liveness/readiness probe configuration
- Environment variables (externalized to ConfigMap/Secret)
- Autoscaling configuration (disabled by default)

**2.4 Generate Backend Minikube Values** (`charts/todo-backend/values-dev.yaml`):
- Reduced resource requests/limits for local development
- FRONTEND_URL: `http://todo-frontend:3000`

**2.5 Generate Backend Templates**:
- `templates/deployment.yaml`: Deployment manifest with parameterized values
- `templates/service.yaml`: ClusterIP service exposing port 8000
- `templates/configmap.yaml`: Non-sensitive config (FRONTEND_URL)
- `templates/secrets.yaml`: Secret template (DATABASE_URL, SECRET_KEY, OPENAI_API_KEY)
- `templates/hpa.yaml`: HorizontalPodAutoscaler (optional)
- `templates/_helpers.tpl`: Reusable template functions

**2.6 Generate Backend README** (`charts/todo-backend/README.md`):
- Installation instructions
- Configuration options
- Secret creation examples
- Upgrade and rollback commands

**2.7 Create Frontend Helm Chart Structure**:
```bash
mkdir -p charts/todo-frontend/templates
```

**2.8 Generate Frontend Chart Metadata** (`charts/todo-frontend/Chart.yaml`):
- Chart name: `todo-frontend`
- Version: `1.0.0`
- appVersion: `v1.0.0`
- Description: "Next.js frontend for Todo AI Chatbot"

**2.9 Generate Frontend Default Values** (`charts/todo-frontend/values.yaml`):
- Image: `todo-frontend:v1.0.0`
- ReplicaCount: 1
- Service type: NodePort, port 3000, nodePort 30080
- Resource requests/limits
- Liveness/readiness probe configuration
- Build-time environment variables (NEXT_PUBLIC_*)
- Autoscaling configuration (disabled by default)

**2.10 Generate Frontend Minikube Values** (`charts/todo-frontend/values-dev.yaml`):
- Reduced resource requests/limits
- Consistent NodePort: 30080

**2.11 Generate Frontend Templates**:
- `templates/deployment.yaml`: Deployment manifest
- `templates/service.yaml`: NodePort service exposing port 3000 on nodePort 30080
- `templates/configmap.yaml`: NEXT_PUBLIC_* configuration
- `templates/_helpers.tpl`: Reusable template functions

**2.12 Generate Frontend README** (`charts/todo-frontend/README.md`):
- Installation instructions
- Accessing frontend via NodePort
- Configuration options

**2.13 Validate Helm Charts**:
```bash
helm lint charts/todo-backend
helm lint charts/todo-frontend
```

**Outputs**:
- `charts/todo-backend/` (complete Helm chart)
- `charts/todo-frontend/` (complete Helm chart)
- Both charts pass `helm lint` validation

**Gate**: Helm charts generated and validated. Proceed to Phase 3.

---

### Phase 3: Kubernetes Deployment (kubectl-ai-operator)

**Agent**: `kubectl-ai-operator` (invoked via `/sp.tasks` or direct skill invocation)

**Input Requirements**:
- Helm charts: `charts/todo-backend/`, `charts/todo-frontend/`
- Minikube cluster running
- Docker images loaded in Minikube

**Tasks**:

**3.1 Create Namespace**:
```bash
kubectl create namespace todo-dev
kubectl get namespaces | grep todo-dev  # Verify creation
```

**3.2 Create Backend Secrets** (manual step or kubectl-ai):
```bash
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL="postgresql://user:password@neon-host/dbname" \
  --from-literal=SECRET_KEY="your-jwt-secret-key-here" \
  --from-literal=OPENAI_API_KEY="sk-your-openai-api-key" \
  --namespace todo-dev

kubectl get secret todo-backend-secrets -n todo-dev  # Verify creation
```

**Alternative kubectl-ai**:
```bash
kubectl-ai create a secret named todo-backend-secrets with DATABASE_URL, SECRET_KEY, and OPENAI_API_KEY in namespace todo-dev
```

**3.3 Deploy Backend via Helm**:
```bash
helm install todo-backend charts/todo-backend \
  --values charts/todo-backend/values-dev.yaml \
  --namespace todo-dev

helm list -n todo-dev  # Verify release
```

**Alternative kubectl-ai**:
```bash
kubectl-ai deploy todo-backend using helm chart ./charts/todo-backend with values-dev.yaml in namespace todo-dev
```

**3.4 Verify Backend Deployment**:
```bash
kubectl get pods -n todo-dev | grep todo-backend  # Should show Running status within 2 minutes
kubectl get service -n todo-dev | grep todo-backend  # Should show ClusterIP assigned
kubectl describe pod -n todo-dev -l app=todo-backend  # Check events and status
```

**Alternative kubectl-ai**:
```bash
kubectl-ai show me the status of todo-backend deployment in namespace todo-dev
```

**3.5 Test Backend Health Endpoint** (from within cluster):
```bash
kubectl run -n todo-dev curl-test --image=curlimages/curl --rm -it --restart=Never -- curl http://todo-backend:8000/health
# Should return {"status": "healthy"}
```

**3.6 Deploy Frontend via Helm**:
```bash
helm install todo-frontend charts/todo-frontend \
  --values charts/todo-frontend/values-dev.yaml \
  --namespace todo-dev

helm list -n todo-dev  # Verify both releases
```

**3.7 Verify Frontend Deployment**:
```bash
kubectl get pods -n todo-dev | grep todo-frontend  # Should show Running status
kubectl get service -n todo-dev | grep todo-frontend  # Should show NodePort 30080
```

**3.8 Get Minikube IP and Access Frontend**:
```bash
minikube ip  # e.g., 192.168.49.2
# Access frontend at http://<minikube-ip>:30080
```

**Alternative kubectl-ai**:
```bash
kubectl-ai what is the URL to access todo-frontend service in namespace todo-dev?
```

**3.9 Test End-to-End Chatbot Functionality**:
- Open browser to `http://<minikube-ip>:30080`
- Register new user
- Login with credentials
- Navigate to `/chat` page
- Send test message to chatbot
- Verify response within 3 seconds (SC-004)

**Outputs**:
- Namespace: `todo-dev` created
- Secret: `todo-backend-secrets` created
- Helm releases: `todo-backend`, `todo-frontend` installed
- Pods: Both backend and frontend in Running state
- Services: Backend ClusterIP accessible internally, Frontend NodePort accessible externally

**Validation** (Success Criteria):
- ✅ SC-001: Deployment workflow completed in <15 minutes
- ✅ SC-002: All pods reach Running state within 2 minutes
- ✅ SC-003: Frontend loads in browser within 5 seconds
- ✅ SC-004: Chatbot response <3 seconds
- ✅ SC-007: Health endpoints return 200 within 1 second
- ✅ SC-009: First-attempt deployment success

**Gate**: Application deployed and accessible. Proceed to Phase 4.

---

### Phase 4: Operational Validation (kubectl-ai + kagent)

**Agent**: `kubectl-ai-operator` and `kagent-aiops-analyst` (future skill)

**Tasks**:

**4.1 Check Deployment Status**:
```bash
kubectl-ai show me deployment status summary for namespace todo-dev
```

**4.2 View Pod Logs**:
```bash
kubectl logs -n todo-dev -l app=todo-backend --tail=50
kubectl logs -n todo-dev -l app=todo-frontend --tail=50
```

**Alternative kubectl-ai**:
```bash
kubectl-ai show me recent logs from todo-backend pods in namespace todo-dev
```

**4.3 Test Scaling** (SC-010):
```bash
kubectl scale deployment todo-backend --replicas=5 -n todo-dev
kubectl get pods -n todo-dev | grep todo-backend  # Should show 5 pods within 30 seconds
kubectl wait --for=condition=Ready pod -l app=todo-backend -n todo-dev --timeout=30s
```

**Alternative kubectl-ai**:
```bash
kubectl-ai scale todo-backend to 5 replicas in namespace todo-dev
```

**4.4 Verify Service Discovery**:
```bash
kubectl run -n todo-dev curl-test --image=curlimages/curl --rm -it --restart=Never -- curl http://todo-backend:8000/health
# Should succeed regardless of replica count (service load balances)
```

**4.5 Test Rolling Update** (SC-006):
```bash
# Rebuild backend image with minor change (e.g., update health response)
docker build -t todo-backend:v1.0.1 ./backend
minikube image load todo-backend:v1.0.1

# Upgrade Helm release
helm upgrade todo-backend charts/todo-backend \
  --set image.tag=v1.0.1 \
  --values charts/todo-backend/values-dev.yaml \
  --namespace todo-dev

# Monitor rollout
kubectl rollout status deployment/todo-backend -n todo-dev
# Should complete within 1 minute with zero request failures
```

**4.6 Test Rollback**:
```bash
helm rollback todo-backend 1 --namespace todo-dev
kubectl rollout status deployment/todo-backend -n todo-dev
```

**4.7 Cluster Health Analysis** (using kagent - future skill):
```bash
kagent analyze cluster health for namespace todo-dev
# Expected: All pods healthy, resource usage within limits, no critical issues
```

**Outputs**:
- Deployment status validated
- Logs accessible and error-free
- Scaling tested (1 → 5 replicas within 30 seconds)
- Rolling update tested (<1 minute, zero failures)
- Rollback tested successfully
- Cluster health report generated (if kagent available)

**Validation** (Success Criteria):
- ✅ SC-006: Rolling updates complete <1 minute, zero failures
- ✅ SC-008: kubectl-ai commands execute 95% successfully
- ✅ SC-010: Scaling to 5 replicas, all pods healthy within 30 seconds

**Gate**: Operational workflows validated. Phase IV complete.

---

### Phase 5: Cleanup (Optional)

**Tasks**:

**5.1 Uninstall Helm Releases**:
```bash
helm uninstall todo-backend -n todo-dev
helm uninstall todo-frontend -n todo-dev
```

**5.2 Delete Namespace**:
```bash
kubectl delete namespace todo-dev
```

**5.3 Stop Minikube** (if no longer needed):
```bash
minikube stop
```

**5.4 Delete Minikube Cluster** (complete reset):
```bash
minikube delete
```

---

## 10. AI-Agent Responsibilities

### infra-spec-guardian

**Role**: Compliance validation gatekeeper

**Responsibilities**:
- Validate all infrastructure actions against Phase IV spec before execution
- Reject manual Dockerfile, Kubernetes YAML, or Helm chart authoring
- Enforce AI-assisted tooling usage (Docker AI, kubectl-ai, kagent)
- Provide APPROVED/REJECTED verdicts with clear reasoning
- Prevent spec drift and workflow shortcuts

**Invocation Points**:
- Before dockerization-agent generates Dockerfiles
- Before helm-chart-architect generates Helm charts
- Before kubectl-ai-operator deploys to Kubernetes
- During plan and task validation phases

**Example Verdict**:
```
REQUEST: "I need to create deployment.yaml for the backend"
VERDICT: REJECTED
REASON: Manual YAML authoring violates Phase IV spec FR-011. Use kubectl-ai or helm-chart-architect for manifest generation.
APPROVED APPROACH: "Use helm-chart-architect to generate Helm chart templates, then deploy via helm install"
```

---

### dockerization-agent

**Role**: Container image builder

**Responsibilities**:
- Analyze application structure (backend Python, frontend Node.js)
- Generate optimized Dockerfiles using AI-assisted tooling (Docker AI/Gordon or Claude Code)
- Create multi-stage builds with minimal final image sizes
- Ensure non-root user execution and security hardening
- Generate .dockerignore files
- Produce build commands and documentation
- Validate health check endpoints and Kubernetes readiness

**Invocation Points**:
- After Phase IV spec approval
- Before Helm chart generation
- When preparing services for Kubernetes deployment

**Input**:
- Application source code (backend/, frontend/)
- Dependency files (requirements.txt, package.json)
- Environment variable requirements (.env.example)

**Output**:
- `backend/Dockerfile` (multi-stage, non-root, <200MB)
- `frontend/Dockerfile` (multi-stage, non-root, <100MB)
- `backend/.dockerignore`, `frontend/.dockerignore`
- Build commands with semantic versioning
- Documentation (ports, health endpoints, env vars)

**Success Criteria**:
- Images build without errors
- Final image sizes meet SC-005 (<200MB backend, <100MB frontend)
- Containers run as non-root users
- Health endpoints functional

---

### helm-chart-architect

**Role**: Helm chart generator

**Responsibilities**:
- Create complete Helm chart structures (Chart.yaml, values.yaml, templates/)
- Parameterize all deployment configurations (image, replicas, ports, resources, env vars)
- Generate Kubernetes resource templates (Deployment, Service, ConfigMap, Secrets, HPA)
- Create environment-specific values files (values-dev.yaml for Minikube)
- Ensure Minikube compatibility and best practices
- Provide installation and upgrade documentation

**Invocation Points**:
- After Docker images are built and validated
- Before deploying to Kubernetes cluster
- When creating reusable deployment configurations

**Input**:
- Docker images: `todo-backend:v1.0.0`, `todo-frontend:v1.0.0`
- Image metadata (ports, health endpoints, environment variables)
- Resource requirements and scaling policies

**Output**:
- `charts/todo-backend/` (complete Helm chart)
- `charts/todo-frontend/` (complete Helm chart)
- values.yaml (default configuration)
- values-dev.yaml (Minikube overrides)
- templates/ (Deployment, Service, ConfigMap, Secrets, HPA, _helpers.tpl)
- README.md (installation docs)

**Success Criteria**:
- Charts pass `helm lint` validation
- Parameterization supports multiple environments
- First-attempt deployment succeeds (SC-009)

---

### kubectl-ai-operator

**Role**: Kubernetes operations executor

**Responsibilities**:
- Deploy Helm charts to Kubernetes using natural language commands
- Scale deployments horizontally (replica management)
- Diagnose pod failures and troubleshoot issues
- Expose services and verify endpoint accessibility
- Monitor deployment health and status
- Perform rolling updates and rollbacks
- Execute cluster operations via natural language intent

**Invocation Points**:
- After Helm charts are generated and validated
- When deploying to Minikube cluster
- During operational tasks (scaling, diagnostics, monitoring)
- When troubleshooting deployment issues

**Input**:
- Helm charts: `charts/todo-backend/`, `charts/todo-frontend/`
- Kubernetes cluster: Minikube running and accessible
- Natural language commands from user or orchestrator

**Output**:
- Deployed Kubernetes resources (Deployments, Services, Pods)
- Deployment status reports
- Diagnostic information and logs
- Scaling operations executed
- Service exposure confirmed

**Success Criteria**:
- 95% of natural language commands execute successfully (SC-008)
- Deployments reach Running state within 2 minutes (SC-002)
- Scaling operations complete within 30 seconds (SC-010)

**Example Commands**:
```bash
kubectl-ai deploy todo-backend using helm chart ./charts/todo-backend with values-dev.yaml in namespace todo-dev
kubectl-ai scale todo-backend to 5 replicas in namespace todo-dev
kubectl-ai why is pod todo-backend-xyz failing in namespace todo-dev?
kubectl-ai show me deployment status summary for namespace todo-dev
```

---

### kagent-aiops-analyst (Future Skill - Phase IV Extension)

**Role**: Cluster health analyzer

**Responsibilities**:
- Analyze Kubernetes cluster health and resource utilization
- Diagnose performance issues and bottlenecks
- Identify resource inefficiencies
- Investigate pod failures and deployment issues
- Validate cluster readiness against operational criteria
- Generate health reports and recommendations

**Invocation Points**:
- After deployment completion for validation
- When troubleshooting performance degradation
- Before Phase IV completion for readiness assessment
- During routine health checks

**Input**:
- Kubernetes cluster state (pods, deployments, services, nodes)
- Resource metrics (CPU, memory, network)
- Application logs and events

**Output**:
- Cluster health assessment report
- Resource utilization analysis
- Identified issues and recommendations
- Readiness validation (pass/fail against Phase IV success criteria)

**Success Criteria**:
- Accurate identification of resource bottlenecks
- Actionable recommendations for issue resolution
- Comprehensive readiness validation

---

### phase-iv-orchestrator

**Role**: Workflow coordinator

**Responsibilities**:
- Enforce strict execution order (spec → plan → tasks → implement → validate)
- Invoke specialized agents in correct sequence
- Track artifacts and decisions (PHRs, ADRs)
- Prevent manual intervention and workflow shortcuts
- Maintain human-in-the-loop governance at decision gates
- Generate execution plans and completion reports

**Invocation Points**:
- At start of Phase IV execution (`/sp.plan` after spec approval)
- When systematic coordination across all agents is needed
- For tracking Phase IV progress and completion
- To ensure spec-driven workflow compliance

**Workflow Coordination**:
1. **Initialization**: Verify prerequisites (Minikube, Docker, Helm, kubectl)
2. **Specification**: Ensure spec.md is approved (already complete)
3. **Planning**: Generate plan.md (this document)
4. **Tasks**: Invoke `/sp.tasks` to generate task breakdown
5. **Implementation**:
   - Phase 1: Invoke `dockerization-agent` → Docker images
   - Phase 2: Invoke `helm-chart-architect` → Helm charts
   - Phase 3: Invoke `kubectl-ai-operator` → Kubernetes deployment
   - Phase 4: Invoke `kagent-aiops-analyst` → Cluster validation
6. **Completion**: Generate Phase IV completion report, create PHRs

**Outputs**:
- Execution plan (this plan.md)
- Task breakdown (tasks.md via `/sp.tasks`)
- Artifact tracking (Docker images, Helm charts, K8s resources)
- PHRs documenting each phase
- ADRs for significant decisions
- Final completion report

**Success Criteria**:
- All phases complete in specified order
- Human approval obtained at each gate
- All artifacts generated and validated
- Complete audit trail (PHRs, ADRs)

---

## 11. ADR Candidates

### Significant Architectural Decisions Requiring Documentation

**ADR-001: Multi-Stage Docker Builds for Size Optimization**

**Context**: Backend and frontend container images must be optimized for size (<200MB and <100MB respectively per SC-005) while maintaining full functionality.

**Decision**: Use multi-stage Docker builds with separate builder and runtime stages.

**Alternatives Considered**:
1. Single-stage builds with full dependency installation (rejected: bloated images 500MB+)
2. Alpine-based images for all services (rejected: Python 3.11-alpine has compatibility issues with compiled dependencies)
3. Distroless images (rejected: increases complexity, limits debugging capabilities)

**Rationale**:
- Multi-stage builds separate build-time dependencies from runtime dependencies
- Python 3.11-slim provides good balance of size (~150MB) and compatibility
- Node 18-alpine excellent for Next.js (final image ~180MB with standalone mode)
- Proven pattern in production Kubernetes deployments

**Tradeoffs**:
- **Pro**: Minimal final image sizes, faster deployments, reduced attack surface
- **Pro**: Compatible with all dependencies (no Alpine compilation issues)
- **Con**: Slightly longer build times due to multiple stages
- **Con**: Requires understanding of multi-stage build patterns

**Recommendation**: **APPROVE** - Multi-stage builds with debian-slim (Python) and alpine (Node) base images

---

**ADR-002: Helm Charts for Deployment Parameterization**

**Context**: Kubernetes deployments require configuration management for multiple environments (dev, staging, prod) with different resource limits, replica counts, and environment variables.

**Decision**: Use Helm 3 charts with parameterized values files instead of raw Kubernetes YAML manifests.

**Alternatives Considered**:
1. Raw kubectl YAML manifests (rejected: no parameterization, duplication across environments)
2. Kustomize overlays (rejected: less mature ecosystem, limited templating)
3. Terraform Kubernetes provider (rejected: overkill for local deployment, stateful complexity)

**Rationale**:
- Helm is industry-standard Kubernetes package manager
- Parameterization via values.yaml enables environment-specific overrides
- Helm release management provides upgrade/rollback capabilities (SC-006)
- Templates with _helpers.tpl enable DRY principle
- Phase IV spec explicitly requires Helm (FR-006 through FR-010)

**Tradeoffs**:
- **Pro**: Reusable charts across environments (dev, staging, prod)
- **Pro**: Built-in versioning and rollback (helm rollback)
- **Pro**: Strong ecosystem and community support
- **Con**: Learning curve for Helm templating syntax
- **Con**: Adds Helm as a prerequisite dependency

**Recommendation**: **APPROVE** - Helm charts with environment-specific values files

---

**ADR-003: NodePort for Frontend, ClusterIP for Backend**

**Context**: Frontend must be externally accessible from browser, backend should only be accessible from within cluster. Minikube does not support cloud LoadBalancer type.

**Decision**: Expose frontend via NodePort (fixed port 30080), backend via ClusterIP (internal only).

**Alternatives Considered**:
1. Ingress controller for frontend (rejected: adds complexity, requires nginx-ingress setup in Minikube)
2. LoadBalancer for frontend (rejected: not available in Minikube)
3. Port-forward for both services (rejected: manual step, not suitable for testing deployment patterns)
4. NodePort for both services (rejected: exposes backend unnecessarily)

**Rationale**:
- NodePort provides direct external access suitable for local development
- Fixed NodePort 30080 ensures consistent access URL across deployments
- ClusterIP keeps backend internal, accessible only from frontend pods via Kubernetes DNS
- Mirrors production pattern where backend is behind API gateway/ingress
- Phase IV spec requires external frontend access (FR-013) and internal backend (FR-012)

**Tradeoffs**:
- **Pro**: Simple access model for Minikube (http://<minikube-ip>:30080)
- **Pro**: Backend protected from direct external access
- **Pro**: No additional infrastructure required (Ingress controller)
- **Con**: Fixed NodePort may conflict if port 30080 in use
- **Con**: Not production-ready (production uses Ingress with TLS)

**Recommendation**: **APPROVE** - NodePort for frontend, ClusterIP for backend

---

**ADR-004: External PostgreSQL Database (Not Containerized)**

**Context**: Backend requires PostgreSQL database for user authentication, todos, conversations, and messages. Phase III uses Neon Serverless PostgreSQL.

**Decision**: Continue using external Neon PostgreSQL database (not containerized in Phase IV). Inject DATABASE_URL via Kubernetes Secret.

**Alternatives Considered**:
1. PostgreSQL StatefulSet in Kubernetes (rejected: adds complexity, requires persistent volumes, out of Phase IV scope)
2. Ephemeral PostgreSQL pod (rejected: data loss on pod restart, unsuitable for testing)
3. External managed database (Neon) (approved: reuses Phase III infrastructure, stateless backend pods)

**Rationale**:
- Phase IV focuses on application containerization and deployment, not database management
- External database aligns with cloud-native pattern (managed database services)
- Keeps backend pods stateless (can scale horizontally without data concerns)
- DATABASE_URL injected as Secret enables environment-specific databases
- Database management (backups, migrations, HA) deferred to Phase V or production planning

**Tradeoffs**:
- **Pro**: Stateless backend pods (no persistent volume complexity)
- **Pro**: Reuses existing Neon database from Phase III
- **Pro**: Faster deployment (no database initialization)
- **Con**: Requires network access to external database from Minikube
- **Con**: Not fully self-contained local environment

**Recommendation**: **APPROVE** - External Neon PostgreSQL with DATABASE_URL in Secret

---

**ADR-005: AI-Assisted Dockerfile Generation (Docker AI or Claude Code)**

**Context**: Phase IV specification mandates AI-first infrastructure with all Dockerfiles generated by AI-assisted tools, not manually authored (FR-001).

**Decision**: Use Docker AI Agent "Gordon" (preferred) or Claude Code (fallback) for Dockerfile generation. Prohibit manual Dockerfile authoring.

**Alternatives Considered**:
1. Manual Dockerfile authoring (rejected: violates Phase IV spec, reduces learning opportunity)
2. Template-based Dockerfile generation (rejected: not AI-assisted, less intelligent optimization)
3. AI-assisted only (approved: enforces AI-first mandate, demonstrates agentic reasoning)

**Rationale**:
- Phase IV is hackathon project demonstrating AI-native development workflow
- AI tools can optimize Dockerfiles based on best practices (multi-stage, security, size)
- Enforces spec-driven development with AI-assisted tooling as first-class requirement
- Docker AI (Gordon) provides conversational Dockerfile generation
- Claude Code fallback ensures execution even if Gordon unavailable

**Tradeoffs**:
- **Pro**: Demonstrates AI-native infrastructure workflow
- **Pro**: AI can apply optimization patterns (multi-stage, layer caching)
- **Pro**: Enforces constitutional principle of AI-first infrastructure
- **Con**: Requires Docker AI or Claude Code availability
- **Con**: May require human validation/iteration if AI generates suboptimal Dockerfile

**Recommendation**: **APPROVE** - AI-assisted Dockerfile generation with Docker AI (preferred) or Claude Code (fallback)

---

### ADR Summary Table

| ID | Decision | Significance | Status |
|----|----------|--------------|--------|
| ADR-001 | Multi-Stage Docker Builds | Image size optimization, security, performance | Recommended |
| ADR-002 | Helm Charts for Deployment | Configuration management, environment portability | Recommended |
| ADR-003 | NodePort (Frontend) + ClusterIP (Backend) | Service exposure strategy for Minikube | Recommended |
| ADR-004 | External PostgreSQL Database | Database management, pod statelessness | Recommended |
| ADR-005 | AI-Assisted Dockerfile Generation | AI-first infrastructure mandate | Recommended |

**Next Step**: Create formal ADRs using `/sp.adr <decision-title>` command after plan approval.

---

## 12. Risks & Mitigations

### Risk 1: Minikube Resource Exhaustion

**Description**: Minikube cluster runs out of CPU or memory resources during deployment, causing pods to fail or never reach Running state.

**Likelihood**: Medium (common on developer machines with limited resources)

**Impact**: High (blocks Phase IV completion)

**Mitigation**:
- Configure Minikube with at least 4 CPU cores and 8GB RAM: `minikube start --cpus=4 --memory=8192`
- Set conservative resource requests/limits in values-dev.yaml (backend: 128Mi/256Mi, frontend: 64Mi/128Mi)
- Monitor resource usage: `kubectl top nodes`, `kubectl top pods -n todo-dev`
- If resources insufficient, reduce replica counts to 1 (already default)
- Fallback: Deploy only backend OR frontend to validate workflow, then deploy second service after cleanup

**Early Warning Signs**:
- Pods stuck in Pending state with "Insufficient cpu" or "Insufficient memory" events
- `kubectl describe pod` shows FailedScheduling events
- Minikube node CPU/memory >90% utilization

---

### Risk 2: Docker Image Pull Failures in Minikube

**Description**: Kubernetes pods fail to pull Docker images because images aren't available in Minikube's local registry.

**Likelihood**: High (common mistake when using Minikube)

**Impact**: High (pods stuck in ImagePullBackOff, blocks deployment)

**Mitigation**:
- Load images into Minikube after building: `minikube image load todo-backend:v1.0.0`
- Verify images available: `minikube image ls | grep todo`
- Set `imagePullPolicy: IfNotPresent` in values.yaml (already configured)
- Alternative: Configure Minikube to use Docker daemon: `eval $(minikube docker-env)`, then build images directly in Minikube's Docker
- Document image loading steps in deployment sequence (Section 9, Phase 1.9)

**Early Warning Signs**:
- Pods stuck in ImagePullBackOff or ErrImagePull state
- `kubectl describe pod` shows "image not found" or "pull access denied" errors

---

### Risk 3: External Database Connection Failures

**Description**: Backend pods cannot connect to external Neon PostgreSQL database due to network restrictions, incorrect DATABASE_URL, or firewall rules.

**Likelihood**: Medium (network configuration issues)

**Impact**: High (backend pods in CrashLoopBackOff, chatbot non-functional)

**Mitigation**:
- Validate DATABASE_URL format before creating Secret (must include credentials, host, database name)
- Test database connectivity from local machine before deployment: `psql $DATABASE_URL`
- Ensure Neon database allows connections from Minikube cluster IP range
- Add startup validation in backend code to fail fast with clear error if DATABASE_URL missing or invalid (FR-019)
- Implement readiness probe that checks database connectivity (future enhancement)
- Document DATABASE_URL creation in deployment sequence (Section 9, Phase 3.2)

**Early Warning Signs**:
- Backend pods stuck in CrashLoopBackOff
- Pod logs show "connection refused" or "could not connect to database" errors
- Health endpoint `/health` returns 500 or times out

---

### Risk 4: Environment Variable Misconfiguration

**Description**: Required environment variables (DATABASE_URL, SECRET_KEY, OPENAI_API_KEY) missing or incorrectly formatted, causing application failures.

**Likelihood**: Medium (common configuration mistake)

**Impact**: Medium (application fails to start or function incorrectly)

**Mitigation**:
- Validate required environment variables at application startup (FR-019)
- Fail fast with descriptive error messages if critical env vars missing
- Create Secret BEFORE Helm install (documented in Section 9, Phase 3.2)
- Provide .env.example files with correct format examples
- Use ConfigMap for non-sensitive vars (FRONTEND_URL) and Secret for sensitive vars (DATABASE_URL, SECRET_KEY, OPENAI_API_KEY)
- Document Secret creation with example values in Helm chart README

**Early Warning Signs**:
- Pods in CrashLoopBackOff immediately after startup
- Pod logs show "KeyError" or "environment variable not set" errors
- Application starts but fails on first API call

---

### Risk 5: AI Tool Unavailability (Docker AI, kubectl-ai)

**Description**: Docker AI (Gordon) or kubectl-ai not available during implementation, blocking AI-assisted infrastructure generation.

**Likelihood**: Low (fallback mechanisms exist)

**Impact**: Medium (requires fallback to alternative tools)

**Mitigation**:
- **Docker AI fallback**: Use Claude Code for Dockerfile generation if Docker AI unavailable
- **kubectl-ai fallback**: Use standard kubectl and helm commands (documented in deployment sequence)
- infra-spec-guardian validates approach before execution
- Document fallback procedures in agent skills (dockerization-agent, kubectl-ai-operator)
- Test both primary and fallback workflows during planning phase

**Early Warning Signs**:
- Docker AI command not found or returns errors
- kubectl-ai installation fails or plugin not recognized

---

### Risk 6: Helm Chart Template Errors

**Description**: Generated Helm chart templates contain syntax errors, incorrect indentation, or invalid Kubernetes manifest structures.

**Likelihood**: Medium (complex templating, AI generation may have issues)

**Impact**: High (helm install fails, blocks deployment)

**Mitigation**:
- Run `helm lint` on all charts before deployment (documented in Section 9, Phase 2.13)
- Use `helm template` to render and validate manifests: `helm template todo-backend charts/todo-backend --values charts/todo-backend/values-dev.yaml`
- Validate rendered YAML with `kubectl apply --dry-run=client -f -`
- Follow Helm best practices (use _helpers.tpl for labels, consistent naming)
- Human review of generated templates before deployment
- Iterative correction if AI-generated templates have issues

**Early Warning Signs**:
- `helm lint` reports errors or warnings
- `helm install` fails with template rendering errors
- `kubectl apply --dry-run` shows validation errors

---

### Risk 7: NodePort Conflicts

**Description**: Fixed NodePort 30080 already in use by another service, causing frontend service creation to fail.

**Likelihood**: Low (unlikely in fresh Minikube cluster)

**Impact**: Low (easily resolved by changing NodePort)

**Mitigation**:
- Check existing NodePorts before deployment: `kubectl get svc --all-namespaces | grep NodePort`
- Allow Kubernetes to auto-assign NodePort if 30080 unavailable (remove `nodePort: 30080` from values.yaml)
- Document NodePort as configurable parameter in values.yaml
- Alternative: Use `minikube service todo-frontend -n todo-dev --url` to get dynamically assigned URL

**Early Warning Signs**:
- Service creation fails with "port already allocated" error
- `kubectl describe service` shows "provided port is already allocated"

---

### Risk 8: Incomplete Phase III Dependencies

**Description**: Phase III chatbot implementation incomplete or broken, preventing full end-to-end testing of Phase IV deployment.

**Likelihood**: Low (Phase III marked complete in conversation summary)

**Impact**: Medium (chatbot functionality untestable, but infrastructure deployment still validates)

**Mitigation**:
- Validate Phase III functionality locally before Phase IV deployment
- Test backend `/api/{user_id}/chat` endpoint with curl before containerization
- Test frontend `/chat` page in local dev environment
- If Phase III issues found, document as Phase IV blocker and fix before proceeding
- Phase IV infrastructure deployment can still proceed independently of chatbot functionality

**Early Warning Signs**:
- Backend /chat endpoint returns 500 errors locally
- Frontend /chat page fails to load in local dev
- OpenAI API key invalid or quota exceeded

---

### Risk Summary Table

| Risk ID | Risk | Likelihood | Impact | Mitigation Priority |
|---------|------|------------|--------|---------------------|
| R1 | Minikube resource exhaustion | Medium | High | **High** |
| R2 | Docker image pull failures | High | High | **High** |
| R3 | Database connection failures | Medium | High | **High** |
| R4 | Environment variable misconfiguration | Medium | Medium | **Medium** |
| R5 | AI tool unavailability | Low | Medium | **Low** |
| R6 | Helm chart template errors | Medium | High | **High** |
| R7 | NodePort conflicts | Low | Low | **Low** |
| R8 | Incomplete Phase III dependencies | Low | Medium | **Medium** |

---

## 13. Exit Criteria for Planning Phase

### Planning Phase Completion Checklist

**Documentation Completeness**:
- [x] Section 1: Planning Overview completed
- [x] Section 2: Technical Context completed
- [x] Section 3: Constitution Check completed
- [x] Section 4: Project Structure completed
- [x] Section 5: Complexity Tracking completed (no violations)
- [x] Section 6: Codebase Analysis Summary completed
- [x] Section 7: Containerization Strategy completed
- [x] Section 8: Helm Chart Architecture completed
- [x] Section 9: Deployment Sequence Plan completed
- [x] Section 10: AI-Agent Responsibilities completed
- [x] Section 11: ADR Candidates completed (5 ADRs identified)
- [x] Section 12: Risks & Mitigations completed (8 risks documented)
- [x] Section 13: Exit Criteria completed (this section)

**Artifact Validation**:
- [x] plan.md follows template structure from `.specify/templates/commands/plan.md`
- [x] All placeholders resolved (no `[NEEDS CLARIFICATION]` markers)
- [x] Technical decisions align with Phase IV specification
- [x] AI-agent coordination clearly defined
- [x] Deployment sequence is actionable and dependency-ordered

**Constitutional Compliance**:
- [x] AI-first infrastructure mandate validated (Section 10, ADR-005)
- [x] Spec-driven workflow adherence confirmed (Section 3)
- [x] Human approval gates defined (Section 9 phases)
- [x] No manual infrastructure authoring planned
- [x] Phase isolation maintained (no Phase V scope creep)

**Readiness for /sp.tasks**:
- [x] Architecture designed and documented
- [x] AI-agent responsibilities clearly defined
- [x] Deployment sequence provides task breakdown structure
- [x] ADR candidates identified for formal documentation
- [x] Risks documented with mitigations
- [x] Success criteria from spec mapped to plan

### Approval Gate

**Status**: ✅ **Planning Phase Complete**

**Next Steps**:
1. **Human Approval Required**: Review this plan.md for accuracy, completeness, and alignment with Phase IV specification
2. **Create PHR**: Document planning phase execution in `history/prompts/004-phase4-local-k8s/0002-phase-iv-planning.plan.prompt.md`
3. **Create ADRs** (optional but recommended): Run `/sp.adr <decision-title>` for each ADR candidate from Section 11
4. **Proceed to /sp.tasks**: After approval, generate atomic task breakdown with `/sp.tasks` command
5. **Implementation**: After tasks approved, execute deployment workflow via specialized agents

**Blocking Issues**: None identified. Plan is complete and ready for review.

---

**Plan Author**: Claude Sonnet 4.5 (phase-iv-orchestrator coordination)
**Plan Date**: 2026-02-03
**Plan Version**: 1.0.0
**Specification Version**: 004-phase4-local-k8s/spec.md (approved 2026-02-03)
