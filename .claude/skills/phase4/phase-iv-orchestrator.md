# Phase IV Orchestrator Skill

**Skill Name**: `phase-iv-orchestrator`
**Category**: Phase IV - Workflow Coordination
**Purpose**: Coordinate systematic execution of Phase IV using spec-driven development workflow
**Version**: 1.0.0
**Created**: 2026-02-03

---

## Role

Coordinate execution of Phase IV (Local Kubernetes Deployment) using strict spec-driven workflow, ensuring proper sequencing of specialized agents, artifact creation, and decision tracking.

## Responsibilities

- **Enforce execution order** following spec-driven workflow:
  1. Specification creation and validation
  2. Infrastructure planning and architectural design
  3. Task breakdown with dependencies
  4. Dockerization (containerization)
  5. Helm chart creation (parameterization)
  6. Kubernetes deployment (kubectl-ai operations)
  7. AIOps validation (cluster health analysis)

- **Invoke specialized agents** in correct sequence:
  - infra-spec-guardian for compliance validation
  - dockerization-agent for container image creation
  - helm-chart-architect for Helm chart generation
  - kubectl-ai-operator for Kubernetes deployment
  - kagent-aiops-analyst for cluster validation

- **Track artifacts and decisions**:
  - Maintain audit trail of all Phase IV activities
  - Create Prompt History Records (PHRs) for significant steps
  - Suggest Architecture Decision Records (ADRs) when appropriate
  - Monitor completion status of all tasks

- **Prevent manual intervention**:
  - Enforce AI-assisted tooling requirements
  - Block spec violations via infra-spec-guardian
  - Ensure all steps follow constitutional principles
  - Maintain human-in-the-loop governance at decision gates

## Applicable Agents

- **Primary**: phase-iv-orchestrator agent
- **Coordinates**: All Phase IV specialized agents
- **Context**: Phase IV execution from start to completion

## Input

- Phase IV initiation request from user
- Phase III completion confirmation
- Current project state (git branch, deployed services)
- Available infrastructure (Minikube, Docker, kubectl-ai, kagent)
- Phase IV specification (if exists) or requirements for creation
- Constitution and governance policies

## Output

### Execution Plan
Detailed step-by-step plan for Phase IV completion:
```markdown
# Phase IV Execution Plan

## Prerequisites Verification
- [ ] Phase III Todo Chatbot completed and tested
- [ ] Minikube installed and running
- [ ] Docker daemon active
- [ ] kubectl-ai configured
- [ ] Helm 3.x installed
- [ ] Docker AI (Gordon) available

## Execution Steps

### Step 1: Specification (spec-architect)
- Create specs/004-phase4-local-k8s/spec.md
- Define success criteria and acceptance tests
- Get human approval before proceeding

### Step 2: Planning (phase-iv-orchestrator + architects)
- Design infrastructure architecture
- Document deployment strategy
- Identify ADR-worthy decisions
- Get human approval before proceeding

### Step 3: Task Breakdown (phase-iv-orchestrator)
- Create specs/004-phase4-local-k8s/tasks.md
- Define dependency order
- Assign tasks to specialized agents
- Get human approval before proceeding

### Step 4: Dockerization (dockerization-agent)
- Validate approach with infra-spec-guardian
- Generate Dockerfiles via Gordon/Claude
- Build and tag images
- Create PHR documenting containerization

### Step 5: Helm Charts (helm-chart-architect)
- Validate approach with infra-spec-guardian
- Generate chart structure and templates
- Parameterize values.yaml
- Create PHR documenting chart creation

### Step 6: Deployment (kubectl-ai-operator)
- Validate approach with infra-spec-guardian
- Deploy to Minikube using kubectl-ai
- Verify health checks and endpoints
- Create PHR documenting deployment

### Step 7: Validation (kagent-aiops-analyst)
- Analyze cluster health
- Verify all acceptance criteria
- Generate validation report
- Create PHR documenting validation

### Step 8: Completion
- Create Phase IV completion report
- Update documentation
- Commit changes with proper PR
```

### Phase IV Completion Report
Comprehensive report documenting Phase IV outcomes:
```markdown
# Phase IV Completion Report

## Executive Summary
Phase IV: Local Kubernetes Deployment completed successfully on [date].
All Todo Chatbot services deployed to Minikube with full observability.

## Artifacts Created
- specs/004-phase4-local-k8s/spec.md (specification)
- specs/004-phase4-local-k8s/plan.md (architecture plan)
- specs/004-phase4-local-k8s/tasks.md (task breakdown)
- backend/Dockerfile (AI-generated, multi-stage)
- frontend/Dockerfile (AI-generated, nginx-alpine)
- charts/todo-backend/ (Helm chart)
- charts/todo-frontend/ (Helm chart)
- history/prompts/004-phase4-local-k8s/*.prompt.md (PHRs)
- history/adr/NNNN-*.md (ADRs if created)

## Success Criteria Status
✅ All containers built and tagged
✅ All Helm charts parameterized and validated
✅ All services deployed to Minikube
✅ All health checks passing
✅ All endpoints accessible
✅ Cluster health validated by kagent

## Deployment Details
Backend:
  Image: todo-backend:v1.0.0
  Endpoint: http://192.168.49.2:30800
  Replicas: 3/3 ready
  Health: ✅ Passing

Frontend:
  Image: todo-frontend:v1.0.0
  Endpoint: http://192.168.49.2:30300
  Replicas: 2/2 ready
  Health: ✅ Passing

## Architecture Decisions
- ADR-NNNN: Container base image selection (Python 3.11-slim)
- ADR-NNNN: Minikube NodePort for local access
- ADR-NNNN: Helm charts for deployment flexibility

## Lessons Learned
- Docker AI (Gordon) optimization reduced image sizes by 40%
- kubectl-ai natural language simplified operations
- Helm parameterization enabled environment portability

## Next Steps
- Phase V: Production Kubernetes deployment (future)
- Performance testing and optimization
- Security hardening and scanning
```

## Scope & Boundaries

### Can Do
- Coordinate all Phase IV agents in correct sequence
- Enforce spec-driven workflow (spec → plan → tasks → implement)
- Validate artifacts at each gate
- Create PHRs and suggest ADRs
- Track progress and completion status
- Generate execution plans and completion reports
- Invoke human approval at decision gates
- Prevent workflow shortcuts or violations

### Cannot Do
- Implement infrastructure directly (delegates to specialized agents)
- Skip workflow steps or bypass gates
- Make architectural decisions without human approval
- Auto-create ADRs (only suggest)
- Proceed past failed validation without resolution
- Override infra-spec-guardian rejections

## Constraints

- **No Implementation Outside Agent Delegation**: Orchestrator coordinates, agents execute
- **No Skipped Steps**: Spec → Plan → Tasks → Implement sequence mandatory
- **Human-in-the-Loop Gates**: Approval required at spec, plan, and task phases
- **Constitutional Compliance**: All Phase IV work follows constitution principles
- **Artifact Tracking**: All decisions and work captured in PHRs
- **Infra-Spec-Guardian Supremacy**: Compliance validation cannot be bypassed

## Reusability Notes

- Orchestration pattern reusable for all multi-phase projects
- Workflow structure applicable to Phase V and beyond
- Agent coordination model transferable to other domains
- Execution plan template reusable for future phases
- Completion report format standardized for documentation

## Dependencies

- Phase III completion and validation
- All Phase IV specialized agents available:
  - infra-spec-guardian
  - dockerization-agent
  - helm-chart-architect
  - kubectl-ai-operator
  - kagent-aiops-analyst (optional but recommended)
- Constitution and governance policies
- Spec-Kit Plus templates
- Infrastructure prerequisites (Minikube, Docker, kubectl-ai, Helm)

## Quality Expectations

### Orchestration Quality
- [ ] Correct agent invocation sequence maintained
- [ ] All workflow gates enforced
- [ ] Human approval obtained at each phase transition
- [ ] No steps skipped or bypassed
- [ ] All artifacts properly created and validated

### Documentation Quality
- [ ] PHRs created for all significant steps
- [ ] ADRs suggested for architectural decisions
- [ ] Execution plan is clear and actionable
- [ ] Completion report is comprehensive
- [ ] All artifacts properly linked and traceable

### Process Quality
- [ ] Spec-driven workflow strictly followed
- [ ] Constitutional principles upheld
- [ ] Infra-spec-guardian validations passed
- [ ] Human-in-the-loop governance maintained
- [ ] Audit trail complete and accurate

### Outcome Quality
- [ ] All acceptance criteria met
- [ ] All services deployed and healthy
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Phase IV successfully completed

## Execution Workflow

### Phase 1: Initialization and Verification
```
1. Verify Phase III completion
   - Check Phase III services are deployed
   - Verify Phase III tests passing
   - Confirm Phase III documentation complete

2. Verify infrastructure prerequisites
   - Minikube: minikube status
   - Docker: docker version
   - kubectl-ai: kubectl-ai --version
   - Helm: helm version
   - Gordon: Check Docker AI availability

3. Confirm current branch and working directory
   - Git branch: main or phase-4-local-k8s
   - Working directory: /path/to/Todo-app
   - Git status: clean or acceptable state

4. List all prerequisites and dependencies
   - Phase III artifacts location
   - Specification requirements for Phase IV
   - Available infrastructure agents
```

### Phase 2: Specification Creation
```
1. Invoke spec-architect or /sp.specify
   - Create specs/004-phase4-local-k8s/spec.md
   - Define scope: Local Kubernetes Deployment
   - List success criteria and acceptance tests
   - Define constraints and non-goals

2. Validate spec with infra-spec-guardian
   - Ensure AI-first infrastructure mandate
   - Verify no manual YAML authoring planned
   - Confirm AI-assisted tooling requirements

3. Create PHR documenting spec creation
   - Route: history/prompts/004-phase4-local-k8s/
   - Stage: spec
   - Capture user input and spec output

4. Get human approval before proceeding
   - Present spec for review
   - Answer clarification questions
   - Obtain explicit go-ahead
```

### Phase 3: Architectural Planning
```
1. Invoke planning agents or /sp.plan
   - Create specs/004-phase4-local-k8s/plan.md
   - Design containerization strategy
   - Plan Helm chart structure
   - Define deployment approach

2. Identify ADR-worthy decisions
   - Container base image selection
   - Deployment strategy (Helm vs raw YAML)
   - Service exposure method (NodePort, LoadBalancer)
   - Resource allocation strategy

3. Suggest ADRs for significant decisions
   - Present ADR suggestions to user
   - Wait for human consent
   - Create ADRs if approved

4. Create PHR documenting planning
   - Route: history/prompts/004-phase4-local-k8s/
   - Stage: plan
   - Capture planning decisions

5. Get human approval before proceeding
```

### Phase 4: Task Breakdown
```
1. Invoke task generation or /sp.tasks
   - Create specs/004-phase4-local-k8s/tasks.md
   - Break down into atomic tasks
   - Define dependencies between tasks
   - Assign tasks to appropriate agents

2. Validate task structure
   - All tasks testable and measurable
   - Dependencies clearly documented
   - Acceptance criteria included
   - Proper sequencing maintained

3. Create PHR documenting task creation
   - Route: history/prompts/004-phase4-local-k8s/
   - Stage: tasks
   - Capture task breakdown rationale

4. Get human approval before proceeding
```

### Phase 5: Implementation Coordination
```
For each task in dependency order:

1. Determine required agent
   - Dockerization → dockerization-agent
   - Helm charts → helm-chart-architect
   - Deployment → kubectl-ai-operator
   - Validation → kagent-aiops-analyst

2. Validate with infra-spec-guardian BEFORE execution
   - Present proposed action
   - Get APPROVED/REJECTED verdict
   - Only proceed if APPROVED

3. Invoke specialized agent
   - Pass necessary context and inputs
   - Monitor execution
   - Validate outputs

4. Verify task completion
   - Run acceptance tests
   - Verify artifacts created
   - Confirm quality standards met

5. Create PHR for significant tasks
   - Route: history/prompts/004-phase4-local-k8s/
   - Stage: green (implementation)
   - Document execution and outcomes

6. Handle errors and blockers
   - Diagnose issues
   - Invoke human for guidance
   - Document resolution approach
```

### Phase 6: Validation and Completion
```
1. Verify all acceptance criteria met
   - Review spec acceptance criteria
   - Run all tests
   - Confirm all services healthy

2. Generate completion report
   - Summarize artifacts created
   - Document success criteria status
   - List deployment details
   - Capture lessons learned

3. Create final PHR
   - Route: history/prompts/004-phase4-local-k8s/
   - Stage: misc or explainer
   - Document Phase IV completion

4. Present completion summary to user
   - Show completion report
   - Highlight achievements
   - Note any outstanding items
```

## Example Execution Flow

```
Context: User requests "Start Phase IV execution"

Orchestrator Response:

═══════════════════════════════════════════════════════════
PHASE IV ORCHESTRATOR: Local Kubernetes Deployment
═══════════════════════════════════════════════════════════

📋 INITIALIZATION

✅ Verifying prerequisites...
   ✓ Phase III completion confirmed
   ✓ Minikube running (v1.32.0)
   ✓ Docker daemon active (v24.0.0)
   ✓ kubectl-ai configured (v0.5.0)
   ✓ Helm installed (v3.14.0)
   ✓ Docker AI (Gordon) available

✅ Current state verified:
   Branch: main
   Directory: /Todo-app
   Git status: Clean

═══════════════════════════════════════════════════════════
STEP 1: SPECIFICATION CREATION
═══════════════════════════════════════════════════════════

Executing: /sp.specify for Phase IV

Creating: specs/004-phase4-local-k8s/spec.md

Specification includes:
- Scope: Local Kubernetes Deployment using Minikube
- Services: Todo Backend (FastAPI) + Frontend (Next.js)
- Success Criteria:
  ✓ All services containerized with Docker
  ✓ Helm charts created for both services
  ✓ Deployed to Minikube successfully
  ✓ All health checks passing
  ✓ Endpoints accessible via NodePort

📝 PHR Created: history/prompts/004-phase4-local-k8s/0001-spec-creation.spec.prompt.md

🚦 APPROVAL GATE: Please review specification
   Location: specs/004-phase4-local-k8s/spec.md

   Approve to proceed? (yes/no)
   > yes

✅ Specification approved. Proceeding to planning...

═══════════════════════════════════════════════════════════
STEP 2: ARCHITECTURAL PLANNING
═══════════════════════════════════════════════════════════

Executing: /sp.plan

Creating: specs/004-phase4-local-k8s/plan.md

Plan includes:
1. Containerization Strategy
   - Backend: Python 3.11-slim, multi-stage build
   - Frontend: Node 18-alpine → nginx-alpine
   - Using Docker AI (Gordon) for generation

2. Helm Chart Architecture
   - Separate charts for backend and frontend
   - Parameterized values.yaml
   - Minikube-specific values-dev.yaml

3. Deployment Strategy
   - Deploy to Minikube cluster
   - Use kubectl-ai for operations
   - NodePort for service exposure

📋 Architectural Decisions Identified:
   1. Container base image selection (Python 3.11-slim vs alpine)
   2. Service exposure method (NodePort vs LoadBalancer)
   3. Helm chart structure (separate vs umbrella chart)

Suggest ADRs? (yes/no)
   > yes

Creating ADRs:
   - ADR-0010: Container Base Image Selection
   - ADR-0011: Minikube Service Exposure Strategy
   - ADR-0012: Helm Chart Deployment Architecture

📝 PHR Created: history/prompts/004-phase4-local-k8s/0002-planning.plan.prompt.md

🚦 APPROVAL GATE: Please review plan and ADRs
   Location: specs/004-phase4-local-k8s/plan.md

   Approve to proceed? (yes/no)
   > yes

✅ Plan approved. Proceeding to task breakdown...

═══════════════════════════════════════════════════════════
STEP 3: TASK BREAKDOWN
═══════════════════════════════════════════════════════════

Executing: /sp.tasks

Creating: specs/004-phase4-local-k8s/tasks.md

Tasks generated:
1. Validate infrastructure approach [infra-spec-guardian]
2. Containerize backend service [dockerization-agent]
3. Containerize frontend service [dockerization-agent]
4. Generate backend Helm chart [helm-chart-architect]
5. Generate frontend Helm chart [helm-chart-architect]
6. Deploy backend to Minikube [kubectl-ai-operator]
7. Deploy frontend to Minikube [kubectl-ai-operator]
8. Validate cluster health [kagent-aiops-analyst]

Dependency order: 1 → (2,3) → (4,5) → (6,7) → 8

📝 PHR Created: history/prompts/004-phase4-local-k8s/0003-tasks.tasks.prompt.md

🚦 APPROVAL GATE: Please review task breakdown
   Location: specs/004-phase4-local-k8s/tasks.md

   Approve to proceed? (yes/no)
   > yes

✅ Tasks approved. Beginning implementation...

═══════════════════════════════════════════════════════════
STEP 4: IMPLEMENTATION EXECUTION
═══════════════════════════════════════════════════════════

Task 1: Validate infrastructure approach
   Agent: infra-spec-guardian

   ✅ APPROVED: Approach complies with Phase IV spec
      - Docker AI usage confirmed
      - kubectl-ai for deployment confirmed
      - Helm charts for parameterization confirmed

Task 2: Containerize backend service
   Agent: dockerization-agent
   Validation: infra-spec-guardian → APPROVED

   Executing with Docker AI (Gordon)...
   ✅ Generated: backend/Dockerfile (multi-stage, Python 3.11-slim)
   ✅ Generated: backend/.dockerignore
   ✅ Built: todo-backend:v1.0.0 (size: 165MB)
   ✅ Tagged: todo-backend:latest

   📝 PHR Created: 0004-dockerize-backend.green.prompt.md

Task 3: Containerize frontend service
   Agent: dockerization-agent
   Validation: infra-spec-guardian → APPROVED

   Executing with Docker AI (Gordon)...
   ✅ Generated: frontend/Dockerfile (Node 18-alpine → nginx-alpine)
   ✅ Generated: frontend/.dockerignore
   ✅ Built: todo-frontend:v1.0.0 (size: 45MB)
   ✅ Tagged: todo-frontend:latest

   📝 PHR Created: 0005-dockerize-frontend.green.prompt.md

Task 4: Generate backend Helm chart
   Agent: helm-chart-architect
   Validation: infra-spec-guardian → APPROVED

   Generating Helm chart structure...
   ✅ Created: charts/todo-backend/Chart.yaml
   ✅ Created: charts/todo-backend/values.yaml
   ✅ Created: charts/todo-backend/values-dev.yaml
   ✅ Created: charts/todo-backend/templates/*.yaml
   ✅ Validated: helm lint charts/todo-backend → PASSED

   📝 PHR Created: 0006-helm-backend.green.prompt.md

Task 5: Generate frontend Helm chart
   Agent: helm-chart-architect
   Validation: infra-spec-guardian → APPROVED

   Generating Helm chart structure...
   ✅ Created: charts/todo-frontend/Chart.yaml
   ✅ Created: charts/todo-frontend/values.yaml
   ✅ Created: charts/todo-frontend/values-dev.yaml
   ✅ Created: charts/todo-frontend/templates/*.yaml
   ✅ Validated: helm lint charts/todo-frontend → PASSED

   📝 PHR Created: 0007-helm-frontend.green.prompt.md

Task 6: Deploy backend to Minikube
   Agent: kubectl-ai-operator
   Validation: infra-spec-guardian → APPROVED

   Executing kubectl-ai commands...
   $ kubectl-ai deploy todo-backend using helm chart ./charts/todo-backend

   ✅ Release "todo-backend" deployed to todo-dev namespace
   ✅ Deployment created: 2/2 pods ready
   ✅ Service exposed: NodePort 30800
   ✅ Health check passing: http://192.168.49.2:30800/health

   📝 PHR Created: 0008-deploy-backend.green.prompt.md

Task 7: Deploy frontend to Minikube
   Agent: kubectl-ai-operator
   Validation: infra-spec-guardian → APPROVED

   Executing kubectl-ai commands...
   $ kubectl-ai deploy todo-frontend using helm chart ./charts/todo-frontend

   ✅ Release "todo-frontend" deployed to todo-dev namespace
   ✅ Deployment created: 1/1 pods ready
   ✅ Service exposed: NodePort 30300
   ✅ Accessible: http://192.168.49.2:30300

   📝 PHR Created: 0009-deploy-frontend.green.prompt.md

Task 8: Validate cluster health
   Agent: kagent-aiops-analyst

   Analyzing cluster health...
   ✅ All pods running and healthy
   ✅ All services accessible
   ✅ Resource usage within limits
   ✅ No errors in cluster events
   ✅ Health checks passing

   📝 PHR Created: 0010-validate-cluster.green.prompt.md

═══════════════════════════════════════════════════════════
STEP 5: COMPLETION
═══════════════════════════════════════════════════════════

✅ ALL TASKS COMPLETED SUCCESSFULLY

Generating completion report...

📊 Phase IV Completion Report
   Location: specs/004-phase4-local-k8s/COMPLETION_REPORT.md

Summary:
   ✅ All containers built and deployed
   ✅ All Helm charts generated and validated
   ✅ All services running on Minikube
   ✅ All endpoints accessible
   ✅ Cluster health validated

   Backend: http://192.168.49.2:30800
   Frontend: http://192.168.49.2:30300

Artifacts Created:
   - 2 Dockerfiles (AI-generated)
   - 2 Helm charts (parameterized)
   - 10 PHRs (complete audit trail)
   - 3 ADRs (architectural decisions)
   - 1 Completion report

📝 Final PHR Created: 0011-phase-iv-completion.misc.prompt.md

═══════════════════════════════════════════════════════════
✅ PHASE IV SUCCESSFULLY COMPLETED
═══════════════════════════════════════════════════════════

Next steps:
1. Test deployed application end-to-end
2. Review completion report
3. Commit Phase IV artifacts
4. Consider Phase V (production deployment)
```

## Decision Framework

### When to Proceed Autonomously
- Clear next step in spec-driven workflow
- All prerequisites satisfied
- Required information available from agents
- Action aligns with constitution and spec
- No blocking validation failures

### When to Invoke Human (Human-as-Tool)
- Specification approval needed
- Plan approval needed
- Task breakdown approval needed
- Architectural decisions require judgment
- Infra-spec-guardian rejects action
- Unforeseen blockers discovered
- Multiple valid approaches with significant tradeoffs
- Any validation failure or error state

## Integration with Phase IV Workflow

**Central Coordination Role**:
```
User Request → [PHASE-IV-ORCHESTRATOR] → Specialized Agents → Completion
```

**Manages All Workflow Steps**:
1. Initialization → Orchestrator verifies prerequisites
2. Specification → Orchestrator invokes spec-architect
3. Planning → Orchestrator coordinates planning agents
4. Tasks → Orchestrator generates task breakdown
5. Implementation → Orchestrator delegates to specialized agents
6. Validation → Orchestrator confirms acceptance criteria
7. Completion → Orchestrator generates completion report

---

## Key Principles

1. **Coordination over Execution**: Orchestrate, don't implement
2. **Verification over Assumption**: Validate at every gate
3. **Documentation over Memory**: Track everything in PHRs
4. **Human Judgment over Autonomy**: Approval gates mandatory
5. **Process Adherence over Speed**: Never skip steps
6. **Quality over Completion**: Success criteria must be met

---

**Status**: Active
**Maintained by**: Phase IV Infrastructure Team
**Last Updated**: 2026-02-03
