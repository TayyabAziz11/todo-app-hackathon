# Phase IV Skills: Local Kubernetes Deployment

**Phase**: Phase IV - Local Kubernetes Deployment
**Version**: 1.0.0
**Created**: 2026-02-03
**Status**: ✅ **100% Complete** (5/5 skills operational)
**Purpose**: Infrastructure and containerization skills for deploying Todo App to local Kubernetes

---

## Overview

Phase IV skills focus on containerizing the Phase III Todo Chatbot application and deploying it to a local Kubernetes cluster using AI-assisted tooling and spec-driven infrastructure practices.

**Core Principle**: **AI-First Infrastructure** - All infrastructure artifacts (Dockerfiles, Kubernetes manifests, Helm charts) must be generated using AI-assisted tools, not manually authored.

---

## Skills in This Category

### 1. Infrastructure Spec Guardian
**File**: `infra-spec-guardian.md`
**Purpose**: Enforce strict compliance with Phase IV specification requirements

**Key Capabilities**:
- Validate all infrastructure actions against Phase IV spec
- Reject manual Dockerfile, Kubernetes YAML, or Helm authoring
- Enforce AI-assisted tooling (Docker AI, kubectl-ai, kagent)
- Prevent spec drift and workflow shortcuts
- Provide clear APPROVED/REJECTED verdicts with reasoning

**When to Use**:
- BEFORE any infrastructure work begins
- Before Dockerfile creation
- Before Kubernetes manifest authoring
- Before Helm chart development
- During plan and task validation

**Example Invocation**:
```
User: "I need to create a deployment.yaml for the backend"
Guardian: REJECTED - Use kubectl-ai or kagent for manifest generation per Phase IV spec
```

---

### 2. Dockerization Agent
**File**: `dockerization-agent.md`
**Purpose**: Containerize frontend and backend services for Kubernetes deployment

**Key Capabilities**:
- Analyze application structure and dependencies
- Use Docker AI (Gordon) for Dockerfile generation
- Create optimized multi-stage builds
- Ensure Kubernetes compatibility (health checks, env vars, signals)
- Generate build commands and documentation
- Apply security best practices (non-root, minimal attack surface)

**When to Use**:
- After Phase III implementation complete
- Before Helm chart creation
- When preparing services for Kubernetes deployment

**Example Output**:
```
Generated:
- backend/Dockerfile (Python 3.11-slim, multi-stage, non-root)
- frontend/Dockerfile (Node 18-alpine → nginx-alpine)
- .dockerignore files
- Build commands with semantic versioning
- Documentation (env vars, ports, health checks)
```

---

### 3. Helm Chart Architect
**File**: `helm-chart-architect.md`
**Purpose**: Design and generate parameterized Helm charts for Kubernetes deployment

**Key Capabilities**:
- Create complete Helm chart structure (Chart.yaml, values.yaml, templates/)
- Parameterize all deployment configurations (image, replicas, ports, env vars)
- Generate Kubernetes resource templates (Deployment, Service, ConfigMap, Ingress, HPA)
- Support scaling and upgrade operations
- Ensure Minikube compatibility for local development
- Follow Helm and Kubernetes best practices

**When to Use**:
- After Docker images are built and tagged
- Before deploying to Kubernetes cluster
- When creating reusable deployment configurations

**Example Output**:
```
Generated:
- charts/todo-backend/
  ├── Chart.yaml (metadata, version)
  ├── values.yaml (default config)
  ├── values-dev.yaml (Minikube overrides)
  ├── templates/
  │   ├── deployment.yaml (replicas, health checks)
  │   ├── service.yaml (ports, selectors)
  │   ├── configmap.yaml (non-sensitive config)
  │   ├── secrets.yaml (template for secrets)
  │   ├── hpa.yaml (autoscaling)
  │   └── _helpers.tpl (reusable functions)
  └── README.md (installation docs)
```

---

### 4. kubectl-ai Operator
**File**: `kubectl-ai-operator.md`
**Purpose**: Operate Kubernetes using natural language kubectl-ai commands

**Key Capabilities**:
- Deploy Helm charts to Kubernetes via kubectl-ai
- Scale deployments horizontally (replica management)
- Diagnose pod failures and troubleshoot issues
- Expose services and verify endpoint accessibility
- Monitor deployment health and status
- Perform rolling updates and rollbacks
- Execute cluster operations using natural language intent

**When to Use**:
- After Helm charts are generated
- When deploying to Minikube cluster
- For operational tasks (scaling, diagnostics, monitoring)
- When troubleshooting deployment issues

**Example Commands**:
```bash
# Deploy
kubectl-ai deploy todo-backend using helm chart ./charts/todo-backend

# Scale
kubectl-ai scale todo-backend to 5 replicas

# Diagnose
kubectl-ai why is pod todo-backend-xyz failing?

# Expose
kubectl-ai expose todo-backend on port 8000 as NodePort

# Monitor
kubectl-ai show me deployment status summary
```

---

### 5. Phase IV Orchestrator
**File**: `phase-iv-orchestrator.md`
**Purpose**: Coordinate systematic execution of Phase IV using spec-driven workflow

**Key Capabilities**:
- Enforce strict execution order (spec → plan → tasks → implement → validate)
- Invoke specialized agents in correct sequence
- Track artifacts and decisions (PHRs, ADRs)
- Prevent manual intervention and workflow shortcuts
- Maintain human-in-the-loop governance at decision gates
- Generate execution plans and completion reports

**When to Use**:
- At the start of Phase IV execution
- When systematic coordination across all agents is needed
- For tracking Phase IV progress and completion
- To ensure spec-driven workflow compliance

**Example Execution**:
```
Phase IV Workflow:
1. Initialization → Verify prerequisites
2. Specification → Create/validate spec.md
3. Planning → Design architecture, identify ADRs
4. Tasks → Break down into dependency-ordered tasks
5. Implementation:
   - Dockerization (images)
   - Helm Charts (deployment configs)
   - Kubernetes Deployment (kubectl-ai)
   - Cluster Validation (kagent)
6. Completion → Generate report, create PHRs
```

---

## Phase IV Workflow Integration

```
Phase IV Spec-Driven Workflow:

1. /sp.specify → Create Phase IV specification
   ↓
2. /sp.plan → Design infrastructure architecture
   ↓
3. [INFRA-SPEC-GUARDIAN] → Validate plan compliance
   ↓
4. /sp.tasks → Break down containerization and deployment tasks
   ↓
5. [DOCKERIZATION-AGENT] → Create container images
   ↓
6. [HELM-CHART-ARCHITECT] → Generate Helm charts ✅
   ↓
7. [KUBECTL-AI-OPERATOR] → Deploy to Kubernetes ✅
   ↓
8. [KAGENT-AIOPS-ANALYST] → Validate cluster health (future skill)

Coordinated by: [PHASE-IV-ORCHESTRATOR] ✅
```

---

## Skill Dependencies

### Infrastructure Spec Guardian
- **Depends On**: Phase IV specification document
- **Used By**: All infrastructure agents (dockerization, helm, kubectl)
- **Validates**: Compliance before any infrastructure work

### Dockerization Agent
- **Depends On**:
  - Phase III application codebase
  - Docker AI (Gordon) or Claude Code
  - infra-spec-guardian approval
- **Used By**:
  - helm-chart-architect (for image references)
  - kubectl-ai-operator (for deployment)
- **Produces**: Container images ready for Kubernetes

### Helm Chart Architect
- **Depends On**:
  - Docker images from dockerization-agent
  - Image metadata (tags, ports, health endpoints)
  - infra-spec-guardian approval
  - Helm 3.x installed
- **Used By**:
  - kubectl-ai-operator (for deployment)
  - kagent-aiops-analyst (for validation)
- **Produces**: Parameterized Helm charts ready for deployment

### kubectl-ai Operator
- **Depends On**:
  - Helm charts from helm-chart-architect
  - Docker images from dockerization-agent
  - Kubernetes cluster (Minikube) running
  - kubectl-ai installed and configured
  - infra-spec-guardian approval
- **Used By**:
  - kagent-aiops-analyst (for cluster state)
  - Operational monitoring and alerting
- **Produces**: Running deployments, services, and operational status

### Phase IV Orchestrator
- **Depends On**:
  - All Phase IV specialized agents
  - Phase III completion
  - Constitution and governance policies
  - Infrastructure prerequisites (Minikube, Docker, kubectl-ai, Helm)
- **Coordinates**:
  - infra-spec-guardian (validation)
  - dockerization-agent (containerization)
  - helm-chart-architect (charts)
  - kubectl-ai-operator (deployment)
  - kagent-aiops-analyst (validation)
- **Produces**: Complete Phase IV execution with full audit trail

---

## AI-Assisted Tooling Requirements

Phase IV mandates the following AI-assisted tools:

| Tool | Purpose | Required For |
|------|---------|--------------|
| **Docker AI (Gordon)** | Dockerfile generation | Containerization |
| **Claude Code** | Fallback Dockerfile generation | Containerization |
| **kubectl-ai** | Kubernetes manifest generation | K8s deployment |
| **kagent** | Cluster analysis and operations | AIOps validation |
| **Helm AI assistance** | Helm chart generation | Parameterized deployment |

**Manual authoring of infrastructure artifacts is strictly prohibited** per Phase IV specification.

---

## Quality Standards

### For All Infrastructure Skills

1. **Spec Compliance**: Every action validated against Phase IV spec
2. **AI-First**: No manual authoring of Dockerfiles, YAML, or Helm
3. **Security**: Non-root users, no secrets in images, minimal attack surface
4. **Kubernetes Ready**: Health checks, graceful shutdown, 12-factor compliance
5. **Documentation**: Clear build/deployment instructions with all requirements
6. **Reproducibility**: Pinned versions, deterministic builds
7. **Observability**: Logs, health endpoints, proper error handling

---

## Example Usage Flow

### Scenario: Containerize Phase III Todo Chatbot

**Step 1: Validate Approach**
```
User: "I want to create Dockerfiles for the backend and frontend"
→ Invoke: infra-spec-guardian
→ Guardian: "Use Docker AI (Gordon) for Dockerfile generation per Phase IV spec"
→ Verdict: APPROVED (with AI-assisted tooling)
```

**Step 2: Analyze Services**
```
→ Invoke: dockerization-agent
→ Agent analyzes:
  - Backend: Python FastAPI, requirements.txt
  - Frontend: Next.js, package.json
```

**Step 3: Generate Dockerfiles**
```
→ Agent uses Gordon:
  "Gordon, create optimized Dockerfile for Python FastAPI app..."
→ Output:
  - backend/Dockerfile (multi-stage, Python 3.11-slim, non-root)
  - frontend/Dockerfile (Node 18-alpine → nginx-alpine)
  - .dockerignore files
```

**Step 4: Build Images**
```
→ Agent provides build commands:
  docker build -t todo-backend:v1.0.0 ./backend
  docker build -t todo-frontend:v1.0.0 ./frontend
→ Images tagged with semantic versions
```

**Step 5: Validate Kubernetes Readiness**
```
→ Agent verifies:
  ✅ Health check endpoints documented
  ✅ Environment variables externalized
  ✅ Non-root user configured
  ✅ Graceful shutdown handling
  ✅ 12-factor app compliance
```

**Step 6: Handoff to Helm**
```
→ Images ready for helm-chart-architect
→ Image references: todo-backend:v1.0.0, todo-frontend:v1.0.0
```

---

## Future Skills (Planned)

The following Phase IV skills are planned for future implementation:

1. **kagent-aiops-analyst**: Analyze cluster health and diagnose issues using kagent AI
3. **k8s-config-validator**: Validate Kubernetes configurations for best practices
4. **k8s-secret-manager**: Manage Kubernetes secrets securely

---

## Skill Maintenance

### Adding New Phase IV Skills

When adding new infrastructure skills:
1. Follow the same structure as existing skills (Role, Responsibilities, Input, Output, etc.)
2. Add to `.claude/skills/phase4/` directory
3. Update this README with skill description
4. Ensure alignment with Phase IV specification
5. Coordinate with infra-spec-guardian for validation

### Updating Existing Skills

When modifying Phase IV skills:
1. Update version number in skill file
2. Document changes in skill file header
3. Update this README if capabilities change
4. Ensure backward compatibility where possible
5. Re-validate against Phase IV spec

---

## Related Documentation

- **Phase IV Specification**: `specs/004-phase4-*/spec.md` (to be created)
- **Phase IV Plan**: `specs/004-phase4-*/plan.md` (to be created)
- **Phase IV Tasks**: `specs/004-phase4-*/tasks.md` (to be created)
- **Constitution**: `.specify/memory/constitution.md`
- **Agent Definitions**: `.claude/agents/infra-spec-guardian.md`, `.claude/agents/dockerization-agent.md`

---

## Key Principles

1. **AI-First Infrastructure**: Never manually author infrastructure artifacts
2. **Spec-Driven**: All work validated against Phase IV specification
3. **Kubernetes Native**: Design for K8s from the start (health, signals, config)
4. **Security Hardened**: Non-root, no secrets, minimal attack surface
5. **Production Ready**: Even for local deployment, maintain production standards
6. **Fully Documented**: Every artifact comes with clear documentation

---

**Status**: Active
**Maintained by**: Phase IV Infrastructure Team
**Last Updated**: 2026-02-03
