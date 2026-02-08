# AI-Powered Todo Application

A full-stack, cloud-native task management platform built through five progressive phases of spec-driven development — from a Python CLI to a production deployment on Oracle Kubernetes Engine.

---

## Overview

This project is the result of Hackathon 2, demonstrating how a real software system evolves across well-defined phases using a structured, specification-first development methodology. Each phase builds on the previous, introducing new layers of complexity: authentication, AI integration, containerization, and finally cloud deployment.

The application allows users to manage tasks through a modern web interface or a natural language AI chatbot. It is built on FastAPI, Next.js, and PostgreSQL, deployed to Oracle Cloud Infrastructure with Kubernetes and Helm.

**What makes it different:**

- Every feature was specified before being built — no ad-hoc coding
- An AI agent (OpenAI Agents SDK + MCP) handles task management via natural language
- The system was designed for cloud-native deployment from Phase 2 onwards
- All infrastructure is codified as Helm charts and Kubernetes manifests
- The deployment runs on a real cloud Kubernetes cluster (OKE, Oracle Cloud)

---

## Key Features

- **AI-powered task management** — interact with todos using natural language via an embedded chatbot
- **Priority levels** — LOW, MEDIUM, HIGH, URGENT with visual indicators
- **Due dates** — deadline tracking with overdue detection
- **Tags** — flexible categorization with autocomplete
- **Advanced search** — client-side filtering by title, status, priority, and tags
- **Authentication** — email/password registration and Google OAuth 2.0
- **JWT-based sessions** — stateless, horizontally scalable auth
- **Responsive dashboard** — clean, mobile-friendly UI built with Tailwind CSS
- **MCP tool transparency** — the UI shows which AI tools were invoked per message

---

## Architecture Overview

```
Browser (Next.js)
      |
      | HTTP (relative /api/* paths proxied by Next.js server)
      v
Next.js Server (port 3000)
      |
      | Proxy rewrites via INTERNAL_BACKEND_URL
      v
FastAPI Backend (port 8000)
      |
      |--- JWT auth, user isolation
      |--- SQLModel ORM
      |--- OpenAI Agents SDK
      |       |
      |       +--- MCP tool server (add/list/update/complete/delete tasks)
      |
      v
PostgreSQL (Neon Serverless)
      |
      +--- users, todos, conversations, messages
```

**Frontend** — Next.js 15 with App Router, TypeScript, Tailwind CSS. Standalone Docker output. Rewrites handle proxying to the backend, decoupling the browser from internal service addresses.

**Backend** — FastAPI with async Python. SQLModel ORM for type-safe database access. Lazy engine initialization allows the app to start even before the database is reachable.

**Database** — Neon Serverless PostgreSQL. Used for user data, task storage, and AI conversation history. Full-text search indexes added in Phase 5.

**AI / MCP** — The chatbot uses OpenAI Agents SDK with a Model Context Protocol (MCP) tool server. The agent is stateless per request — all conversation history is loaded from PostgreSQL on each call. This makes the system horizontally scalable with no sticky sessions.

**Event-driven architecture** — Phase 5 introduced Dapr components and Kafka pub/sub for an event-driven microservices prototype (analytics, audit, notification services). These are defined in `services/` and `k8s/dapr/` and demonstrate the architecture's extensibility.

---

## Phase-by-Phase Breakdown

### Phase 1 — CLI Foundations

**Goals:** Establish the development methodology, build confidence with spec-driven delivery.

**What was built:**
- Interactive Python CLI (REPL) for todo management
- In-memory storage using a plain dictionary
- Full CRUD: add, view, update, delete, toggle completion
- Input validation, error handling, graceful exit

**Key technical wins:**
- Three-module architecture (`todo.py`, `cli.py`, `todo_manager.py`) with clean separation of concerns
- Zero external dependencies — Python standard library only
- Established the spec → plan → tasks → implement workflow that carried through all subsequent phases

---

### Phase 2 — Core Backend and Authentication

**Goals:** Move from CLI to a production-grade web application with secure authentication.

**What was built:**
- FastAPI backend with JWT authentication
- PostgreSQL database via SQLModel ORM
- User registration, login, and per-user data isolation
- Next.js frontend with Tailwind CSS
- Full todo CRUD via REST API
- Google and GitHub OAuth 2.0

**Key technical wins:**
- Stateless JWT auth — each token encodes the user ID, no server-side session storage
- User isolation enforced at both the route level (JWT claim) and database level (user_id filter)
- OWASP-compliant: bcrypt password hashing, parameterized queries, CORS configuration
- Three Architecture Decision Records (ADRs) documenting key choices: JWT, SQLModel, monorepo structure

---

### Phase 3 — AI Todo Chatbot (MCP-based)

**Goals:** Integrate a natural language interface for task management using OpenAI and MCP.

**What was built:**
- OpenAI Agents SDK integration with a custom MCP tool server
- Five MCP tools: `add_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task`
- Stateless conversation architecture — all history stored in PostgreSQL
- Frontend chat UI using OpenAI ChatKit with `conversation_id` persistence via sessionStorage
- Deployed to Hugging Face Spaces (backend) and Vercel (frontend)

**Key technical wins:**
- Agent reconstructed from scratch on every HTTP request — no in-memory state
- `conversation_id` token passed by client enables full context recovery
- Multi-step operations handled in a single API call (e.g., "add task and mark it done")
- Tool call transparency exposed in the UI — users see which MCP tools were invoked

---

### Phase 4 — Kubernetes Deployment (Local)

**Goals:** Containerize the application and deploy it to a local Kubernetes cluster with Helm.

**What was built:**
- Multi-stage Dockerfiles for both backend (Python/FastAPI) and frontend (Next.js standalone)
- Helm charts for backend (ClusterIP) and frontend (LoadBalancer)
- Kubernetes manifests: Deployments, Services, ConfigMaps, Secrets, HPA
- Multi-environment values files (local, dev, production)
- Minikube-based local cluster deployment

**Key technical wins:**
- Parameterized Helm charts deployable across environments with values overrides
- Kubernetes Secrets for credential management — never in version control
- Health probes (liveness + readiness) on `/health` for reliable pod lifecycle management
- HPA configured for CPU-based autoscaling

---

### Phase 5 — Cloud Deployment (Oracle OKE)

**Goals:** Deploy the full application to a real cloud Kubernetes cluster on Oracle Cloud Infrastructure.

**What was built:**
- Oracle Kubernetes Engine (OKE) cluster on the Always Free tier (2x VM.Standard.A1.Flex nodes)
- Docker images published to Docker Hub (`tayyabaziz11/todo-backend:v5.0.0-oracle`, `tayyabaziz11/todo-frontend:v5.0.0-oracle`)
- Dedicated Helm chart (`helm/todo-app-oracle/`) for OKE deployment
- NAT Gateway + separate route table for pod internet egress (Neon DB access)
- Kubernetes Secret for Google OAuth credentials (`google-oauth-secret`)
- Advanced search backend: PostgreSQL full-text search with tsvector indexes
- Phase 5 also prototypes a Dapr + Kafka event-driven architecture in `services/`

**Key technical wins:**
- Resolved CRI-O short name enforcement by prefixing all images with `docker.io/`
- Fixed Next.js proxy loop by splitting `NEXT_PUBLIC_API_BASE_URL` (browser) from `INTERNAL_BACKEND_URL` (server-side proxy) — baked at build time
- Configured Oracle VCN networking: Internet Gateway for K8s API and LB subnets, NAT Gateway for pod egress
- Google OAuth injected via `secretKeyRef` — no inline credentials in Helm values
- Production URL: `http://129.151.136.242`

---

## Cloud and DevOps (Phase 5 Focus)

### Oracle Cloud Infrastructure

- **Region:** `me-abudhabi-1`
- **Cluster:** `taskflow-cluster` (OKE Free Tier)
- **Nodes:** 2x VM.Standard.A1.Flex (ARM-based, Oracle Linux 8)
- **Container runtime:** CRI-O (requires fully qualified image names)
- **VCN:** Custom subnet routing — Internet Gateway for API/LB, NAT Gateway for worker nodes

### Docker

Multi-stage builds minimize image size. The backend uses `python:3.11-slim` with a non-root user. The frontend uses Next.js standalone output (`output: 'standalone'`) to reduce the runtime image to under 100MB.

```bash
# Build backend
docker build -t docker.io/tayyabaziz11/todo-backend:v5.0.0-oracle ./backend

# Build frontend (proxy target baked in at build time)
docker build \
  --build-arg INTERNAL_BACKEND_URL=http://todo-backend:8000 \
  -t docker.io/tayyabaziz11/todo-frontend:v5.0.0-oracle ./frontend
```

### Helm

```bash
# Deploy to OKE
helm upgrade todo-app helm/todo-app-oracle \
  -n todo-app \
  -f helm/todo-app-oracle/values.yaml \
  -f helm/todo-app-oracle/values-oracle.yaml \
  --set backend.env.DATABASE_URL="..." \
  --set backend.env.JWT_SECRET_KEY="..."
```

### Kubernetes Operations

```bash
# Check deployment status
kubectl get all -n todo-app

# View backend logs
kubectl logs -n todo-app deployment/todo-backend -f

# Verify Google OAuth credentials injected
kubectl exec -n todo-app deployment/todo-backend -- env | grep GOOGLE
```

---

## Repository Structure

```
Todo-app/
├── backend/              FastAPI application (Python 3.11+)
│   ├── app/              Routes, models, schemas, auth, agent, MCP tools
│   ├── alembic/          Database migrations
│   └── Dockerfile        Multi-stage production image
├── frontend/             Next.js 15 application (TypeScript)
│   ├── src/              Pages, components, hooks, API client
│   └── Dockerfile        Standalone production image
├── helm/
│   ├── todo-app-oracle/  Helm chart for Oracle Cloud deployment
│   └── todo-app/         Helm chart for Dapr microservices prototype
├── k8s/
│   └── dapr/             Dapr component manifests (pub/sub, state, secrets)
├── services/             Dapr microservices (analytics, audit, notification, etc.)
├── charts/               Phase 4 Helm charts (local Kubernetes)
├── specs/                Feature specifications, plans, and task breakdowns
│   ├── 001-phase1-todo-cli/
│   ├── 002-fullstack-web-app/
│   ├── 003-phase3-ai-chatbot/
│   ├── 004-phase4-local-k8s/
│   └── 005-name-phase5-cloud/
├── docs/                 Architecture decisions, deployment guides, phase reports
│   ├── adr/              Architecture Decision Records
│   ├── deployment/       HuggingFace, OAuth, Kubernetes guides
│   ├── phases/           Per-phase completion documentation
│   └── fixes/            Technical fix write-ups
├── history/              Prompt History Records (spec-driven development audit trail)
├── tests/                Test suites
├── scripts/              Deployment and health check automation
├── app.py                Phase 1 CLI entry point
├── cli.py                Phase 1 interactive menu
└── todo_manager.py       Phase 1 business logic
```

---

## How to Run

### Local Development (without Kubernetes)

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Create .env with DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY
uvicorn main:app --reload
# API at http://localhost:8000

# Frontend (separate terminal)
cd frontend
npm install
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev
# UI at http://localhost:3000
```

### Local Kubernetes (Minikube)

```bash
minikube start --cpus=4 --memory=8192
helm install todo-app charts/todo-backend -f charts/todo-backend/values-local.yaml -n todo-dev --create-namespace
helm install todo-frontend charts/todo-frontend -f charts/todo-frontend/values-local.yaml -n todo-dev
kubectl port-forward -n todo-dev svc/todo-frontend 3000:3000
```

### Oracle Kubernetes Engine (Cloud)

```bash
# Configure kubectl with OKE kubeconfig
oci ce cluster create-kubeconfig --cluster-id <cluster-ocid> --region me-abudhabi-1

# Create secrets
kubectl create secret generic google-oauth-secret -n todo-app \
  --from-literal=GOOGLE_CLIENT_ID=... \
  --from-literal=GOOGLE_CLIENT_SECRET=...

# Deploy
helm upgrade todo-app helm/todo-app-oracle -n todo-app \
  -f helm/todo-app-oracle/values.yaml \
  -f helm/todo-app-oracle/values-oracle.yaml \
  --set backend.env.DATABASE_URL="..." \
  --set backend.env.JWT_SECRET_KEY="..."
```

---

## What Makes This Project Advanced

**Spec-driven development.** Every phase starts with a specification (`spec.md`), moves to an architecture plan (`plan.md`), generates a task list (`tasks.md`), and only then proceeds to implementation. This produces a traceable development history and ensures features are built intentionally, not reactively.

**Agentic workflows.** The AI chatbot uses an agent that operates over a defined set of MCP tools. The agent is stateless — it reconstructs context from the database on every request. This is a practical implementation of production-grade agentic architecture.

**Cloud-native design.** The application was designed for containerization from Phase 2. Environment variables, secrets management, health probes, and proxy routing all follow cloud-native patterns. Helm parameterization allows the same codebase to deploy to local Minikube or Oracle Cloud with only values file changes.

**Production thinking throughout.** Every phase considers security (OWASP, JWT, no secrets in code), scalability (stateless auth, stateless AI agent, horizontal pod autoscaling), and observability (structured logging, health endpoints, liveness/readiness probes).

**Hackathon to real system.** The progression from a 200-line Python CLI to a Kubernetes-deployed, AI-integrated, OAuth-authenticated web application demonstrates the discipline of incremental delivery with consistent quality standards.

---

## Future Enhancements

- **Server-side search** — PostgreSQL full-text search is implemented at the database layer; the frontend can be extended to use it directly
- **Push notifications** — the Dapr notification service prototype in `services/` can be extended with real email/SMS delivery
- **Analytics dashboard** — the Kafka event stream captures task lifecycle events; an analytics service can aggregate and visualize them
- **Recurring tasks** — scheduled job integration for daily/weekly task generation
- **Mobile application** — the REST API is already designed for multi-client use

---

## Author

**Tayyab Aziz**
Hackathon 2 Participant — Certified Cloud Native Generative and Agentic AI Engineer Program

---

*Built with Spec-Driven Development. Every decision documented, every feature specified.*
