# kubectl-ai Operator Skill

**Skill Name**: `kubectl-ai-operator`
**Category**: Phase IV - Kubernetes Operations
**Purpose**: Operate Kubernetes clusters using natural language kubectl-ai commands for deployment, scaling, and diagnostics
**Version**: 1.0.0
**Created**: 2026-02-03

---

## Role

Operate Kubernetes using natural language commands via kubectl-ai to deploy applications, manage resources, diagnose issues, and perform operational tasks without manually writing YAML manifests.

## Responsibilities

- Deploy Helm charts to Kubernetes cluster via kubectl-ai
- Scale deployments up or down based on requirements
- Diagnose pod failures and troubleshoot issues
- Expose services and verify endpoints accessibility
- Monitor deployment health and status
- Perform rolling updates and rollbacks
- Manage Kubernetes resources (pods, services, deployments, configmaps)
- Execute cluster operations using natural language intent

## Applicable Agents

- **Primary**: kubectl-ai-operator agent
- **Supporting**: infra-spec-guardian (validation), kagent-aiops-analyst (diagnostics)
- **Context**: Kubernetes deployment and operations phase

## Input

- Helm charts from helm-chart-architect:
  - Chart directory path
  - Values files (values.yaml, values-dev.yaml)
  - Release name and namespace
- Operational requests:
  - Deployment commands (deploy, scale, update, rollback)
  - Diagnostic queries (pod status, logs, events)
  - Service exposure requirements (NodePort, LoadBalancer, Ingress)
  - Resource scaling parameters (replicas, CPU, memory)
- Cluster context:
  - Kubernetes cluster (Minikube for Phase IV)
  - Namespace preferences
  - Current deployment state

## Output

### kubectl-ai Commands
Natural language commands translated to Kubernetes operations:
```bash
# Deployment
kubectl-ai deploy my-app using helm chart ./charts/todo-backend

# Scaling
kubectl-ai scale deployment todo-backend to 5 replicas

# Diagnostics
kubectl-ai show me why pod todo-backend-xyz is failing
kubectl-ai get logs from todo-backend pods in the last 10 minutes

# Service exposure
kubectl-ai expose todo-backend on port 8000 as NodePort
```

### Deployment Status Summaries
Structured reports on deployment health and status:
```
Deployment Status: todo-backend
  Status: ✅ Running
  Replicas: 3/3 ready
  Image: todo-backend:v1.0.0
  Endpoint: http://192.168.49.2:30800
  Health: All pods healthy
  Last Updated: 2026-02-03 11:15:00
```

### Diagnostic Reports
Issue analysis and troubleshooting information:
```
Pod Failure Diagnosis: todo-backend-abc123
  Status: CrashLoopBackOff
  Reason: Application startup failure
  Last Exit Code: 1
  Error: ConnectionRefusedError: [Errno 111] Connection refused to DATABASE_URL
  Recommendation: Verify database service is running and DATABASE_URL is correct
```

### Operation Logs
Record of all kubectl-ai operations performed:
```
[2026-02-03 11:00:00] Deployed todo-backend v1.0.0 to todo-dev namespace
[2026-02-03 11:05:00] Scaled todo-backend from 2 to 3 replicas
[2026-02-03 11:10:00] Exposed todo-backend service on NodePort 30800
```

## Scope & Boundaries

### Can Do
- Deploy applications using Helm charts via kubectl-ai
- Scale deployments horizontally (replica count)
- Diagnose pod failures, CrashLoopBackOff, ImagePullBackOff
- Expose services with different types (ClusterIP, NodePort, LoadBalancer)
- Retrieve logs, events, and resource status
- Perform rolling updates and rollbacks
- Create and manage ConfigMaps and Secrets
- Monitor deployment health and readiness
- Execute operational tasks using natural language

### Cannot Do
- Manually edit raw Kubernetes YAML files (use kubectl-ai instead)
- Bypass infra-spec-guardian validation
- Make architectural decisions without spec authority
- Perform operations on production clusters without approval
- Ignore failed health checks or errors
- Deploy without proper validation and testing

## Constraints

- **Avoid Raw kubectl YAML Edits**: Use kubectl-ai natural language commands
- **Prefer Intent-Based Commands**: Express what you want, not how to do it
- **No Manual Manifest Authoring**: All resources created via kubectl-ai or Helm
- **Validation Required**: All operations must pass infra-spec-guardian checks
- **Minikube Context**: Phase IV targets local Minikube cluster
- **Safe Operations**: Use --dry-run for testing, rollback capability for updates

## Reusability Notes

- Pattern reusable for any Kubernetes cluster operations
- kubectl-ai commands applicable across environments (dev, staging, prod)
- Diagnostic workflows reusable for troubleshooting
- Deployment patterns transferable to production clusters
- Operational playbooks can be documented and repeated

## Dependencies

- **kubectl-ai** installed and configured
- Kubernetes cluster access (Minikube for Phase IV)
- Helm 3.x (for chart deployments)
- Helm charts from helm-chart-architect
- Docker images from dockerization-agent
- infra-spec-guardian for validation
- kubectl configured with proper context

## Quality Expectations

### Command Quality
- [ ] Natural language expressions clear and unambiguous
- [ ] Intent clearly stated (what, not how)
- [ ] All operations validated before execution
- [ ] Dry-run used for testing when appropriate
- [ ] Commands are idempotent where possible

### Deployment Quality
- [ ] All pods reach Running state
- [ ] Health checks pass (liveness, readiness)
- [ ] Services are accessible at expected endpoints
- [ ] Resources within cluster capacity
- [ ] No CrashLoopBackOff or ImagePullBackOff errors

### Operational Quality
- [ ] All operations logged with timestamps
- [ ] Errors diagnosed with root cause analysis
- [ ] Rollback plan available for all changes
- [ ] Documentation of all manual interventions
- [ ] Status summaries accurate and up-to-date

### Diagnostic Quality
- [ ] Root cause identified for failures
- [ ] Actionable recommendations provided
- [ ] Logs and events correlated
- [ ] Relevant context included (config, resources, events)
- [ ] Clear next steps for resolution

## Execution Workflow

### Step 1: Pre-Deployment Validation
1. Verify Kubernetes cluster is accessible
2. Check Minikube status and resources
3. Validate Helm charts are ready
4. Confirm Docker images are available
5. Review infra-spec-guardian approval

### Step 2: Deploy Application
Using kubectl-ai natural language:
```bash
# Deploy backend using Helm chart
kubectl-ai deploy todo-backend using helm chart ./charts/todo-backend \
  with values ./charts/todo-backend/values-dev.yaml \
  in namespace todo-dev

# Deploy frontend
kubectl-ai deploy todo-frontend using helm chart ./charts/todo-frontend \
  with values ./charts/todo-frontend/values-dev.yaml \
  in namespace todo-dev
```

### Step 3: Verify Deployment
```bash
# Check deployment status
kubectl-ai show me status of all deployments in todo-dev

# Verify pods are running
kubectl-ai list all pods in todo-dev namespace

# Check service endpoints
kubectl-ai show me all services in todo-dev
```

### Step 4: Expose Services
```bash
# Expose backend service
kubectl-ai expose todo-backend service on port 8000 as NodePort

# Expose frontend service
kubectl-ai expose todo-frontend service on port 3000 as NodePort

# Get access URLs
kubectl-ai show me how to access todo-backend service
kubectl-ai show me how to access todo-frontend service
```

### Step 5: Health Verification
```bash
# Check pod health
kubectl-ai are all pods in todo-dev healthy?

# Verify readiness probes
kubectl-ai show me readiness status of todo-backend pods

# Check recent events
kubectl-ai show me recent events in todo-dev namespace
```

### Step 6: Monitor and Diagnose
If issues arise:
```bash
# Diagnose failing pod
kubectl-ai why is pod todo-backend-xyz failing?

# Get logs
kubectl-ai show me logs from todo-backend pods

# Check resource usage
kubectl-ai show me resource usage for todo-backend deployment

# Describe pod details
kubectl-ai describe pod todo-backend-xyz in detail
```

### Step 7: Operational Tasks

**Scaling**:
```bash
# Scale up
kubectl-ai scale todo-backend deployment to 5 replicas

# Scale down
kubectl-ai scale todo-frontend deployment to 2 replicas

# Verify scaling
kubectl-ai show me replica count for all deployments
```

**Updates**:
```bash
# Rolling update with new image
kubectl-ai update todo-backend deployment to use image todo-backend:v1.1.0

# Check rollout status
kubectl-ai show me rollout status of todo-backend

# Rollback if needed
kubectl-ai rollback todo-backend deployment to previous version
```

**ConfigMaps and Secrets**:
```bash
# Create ConfigMap
kubectl-ai create configmap todo-config from file ./config/app.conf

# Create Secret
kubectl-ai create secret todo-secrets with DATABASE_URL and SECRET_KEY

# Update deployment to use secret
kubectl-ai add secret todo-secrets to todo-backend deployment
```

## Example Use Case

```
Context: Deploy Phase III Todo Chatbot to Minikube using Helm charts

Step 1: Validate Prerequisites
  $ minikube status
  ✅ Minikube running
  ✅ kubectl configured to minikube context
  ✅ Helm charts ready: charts/todo-backend, charts/todo-frontend
  ✅ Images available: todo-backend:v1.0.0, todo-frontend:v1.0.0

Step 2: Create Namespace
  $ kubectl-ai create namespace todo-dev
  Output: Namespace "todo-dev" created

Step 3: Deploy Backend
  $ kubectl-ai deploy todo-backend using helm chart ./charts/todo-backend \
      with values ./charts/todo-backend/values-dev.yaml \
      in namespace todo-dev

  Output:
    ✅ Release "todo-backend" deployed to todo-dev
    ✅ Deployment "todo-backend" created with 1 replica
    ✅ Service "todo-backend" created (NodePort)
    📊 Waiting for pods to be ready...
    ✅ Pod todo-backend-abc123 is Running
    ✅ Health checks passing

Step 4: Deploy Frontend
  $ kubectl-ai deploy todo-frontend using helm chart ./charts/todo-frontend \
      with values ./charts/todo-frontend/values-dev.yaml \
      in namespace todo-dev

  Output:
    ✅ Release "todo-frontend" deployed to todo-dev
    ✅ Deployment "todo-frontend" created with 1 replica
    ✅ Service "todo-frontend" created (NodePort)
    ✅ Pod todo-frontend-xyz789 is Running
    ✅ Health checks passing

Step 5: Verify Deployments
  $ kubectl-ai show me all resources in todo-dev namespace

  Output:
    DEPLOYMENTS:
      todo-backend    1/1 ready    todo-backend:v1.0.0
      todo-frontend   1/1 ready    todo-frontend:v1.0.0

    SERVICES:
      todo-backend    NodePort    10.96.100.10   30800/TCP
      todo-frontend   NodePort    10.96.100.11   30300/TCP

    PODS:
      todo-backend-abc123    Running    Healthy
      todo-frontend-xyz789   Running    Healthy

Step 6: Get Access URLs
  $ kubectl-ai show me how to access todo-backend service

  Output:
    Service: todo-backend
    Type: NodePort
    Internal: http://10.96.100.10:8000
    External: http://192.168.49.2:30800
    Health Check: http://192.168.49.2:30800/health

    Access via:
      curl http://192.168.49.2:30800/health
      or visit in browser: http://192.168.49.2:30800

  $ kubectl-ai show me how to access todo-frontend service

  Output:
    Service: todo-frontend
    Type: NodePort
    Internal: http://10.96.100.11:3000
    External: http://192.168.49.2:30300

    Access via browser: http://192.168.49.2:30300

Step 7: Test Health Endpoints
  $ curl http://192.168.49.2:30800/health
  Output: {"status": "healthy", "database": "connected"}

  $ curl http://192.168.49.2:30300
  Output: [Frontend loads successfully]

Step 8: Scale Backend (if needed)
  $ kubectl-ai scale todo-backend deployment to 3 replicas

  Output:
    ✅ Scaling todo-backend from 1 to 3 replicas
    📊 Waiting for new pods...
    ✅ Pod todo-backend-def456 is Running
    ✅ Pod todo-backend-ghi789 is Running
    ✅ All 3 replicas ready

Step 9: Monitor Deployment
  $ kubectl-ai show me deployment status summary

  Output:
    Deployment Status Summary (todo-dev namespace)

    todo-backend:
      Replicas: 3/3 ready
      Image: todo-backend:v1.0.0
      Endpoint: http://192.168.49.2:30800
      Health: ✅ All pods healthy
      CPU: 15% average
      Memory: 180Mi average
      Uptime: 5 minutes

    todo-frontend:
      Replicas: 1/1 ready
      Image: todo-frontend:v1.0.0
      Endpoint: http://192.168.49.2:30300
      Health: ✅ All pods healthy
      CPU: 8% average
      Memory: 95Mi average
      Uptime: 5 minutes

Deployment Status: ✅ SUCCESS
All services running and accessible on Minikube
```

## Common kubectl-ai Command Patterns

### Deployment Commands
```bash
kubectl-ai deploy <app> using helm chart <path> in namespace <ns>
kubectl-ai install <chart> as <release-name> in <namespace>
kubectl-ai upgrade <release> with values <values-file>
kubectl-ai rollback <release> to revision <number>
kubectl-ai delete deployment <name> in <namespace>
```

### Scaling Commands
```bash
kubectl-ai scale <deployment> to <N> replicas
kubectl-ai autoscale <deployment> with min <N> max <M> CPU <percent>
kubectl-ai show me replica count for <deployment>
```

### Diagnostic Commands
```bash
kubectl-ai why is pod <name> failing?
kubectl-ai show me logs from <pod/deployment>
kubectl-ai describe <resource> <name>
kubectl-ai show me events in <namespace>
kubectl-ai get resource usage for <deployment>
```

### Service Commands
```bash
kubectl-ai expose <deployment> on port <N> as <type>
kubectl-ai show me how to access <service>
kubectl-ai list all services in <namespace>
kubectl-ai show me endpoints for <service>
```

### Status Commands
```bash
kubectl-ai show me status of all deployments
kubectl-ai are all pods healthy in <namespace>?
kubectl-ai show me deployment status summary
kubectl-ai list all resources in <namespace>
```

## Diagnostic Playbooks

### Pod CrashLoopBackOff
```bash
1. kubectl-ai why is pod <name> crashing?
2. kubectl-ai show me logs from pod <name>
3. kubectl-ai describe pod <name> in detail
4. Check common causes:
   - Missing environment variables
   - Database connection failures
   - Port conflicts
   - Resource limits too low
5. kubectl-ai show me events for pod <name>
6. Fix issue and redeploy
```

### ImagePullBackOff
```bash
1. kubectl-ai why can't pod <name> pull image?
2. kubectl-ai describe pod <name>
3. Check:
   - Image name and tag correct?
   - Image exists in registry?
   - Registry credentials configured?
4. kubectl-ai show me image pull secrets
5. Fix image reference or add pull secret
```

### Service Not Accessible
```bash
1. kubectl-ai show me how to access <service>
2. kubectl-ai list endpoints for <service>
3. kubectl-ai are pods behind <service> ready?
4. Check:
   - Service selector matches pod labels?
   - Pods are running and ready?
   - NodePort/LoadBalancer configured?
5. kubectl-ai show me service details for <service>
```

## Best Practices Enforced

### Intent-Based Commands
✅ **Good**: "kubectl-ai deploy my-app using helm chart ./charts/my-app"
❌ **Bad**: Manually creating deployment YAML and applying with kubectl

### Natural Language
✅ **Good**: "kubectl-ai show me why pod X is failing"
❌ **Bad**: "kubectl get pod X -o yaml | grep -A 10 status"

### Validation First
✅ **Good**: Use --dry-run to test before applying
❌ **Bad**: Apply changes directly to production without testing

### Clear Intent
✅ **Good**: "kubectl-ai scale backend to 5 replicas for increased load"
❌ **Bad**: "kubectl-ai do something with backend"

## Integration with Phase IV Workflow

**Position in Workflow**:
```
Phase IV: Helm Charts → [KUBECTL-AI OPERATOR] → Cluster Validation
```

**Coordination Points**:
1. After helm-chart-architect generates charts
2. Before kagent-aiops-analyst validates cluster
3. Validated by infra-spec-guardian for compliance
4. Monitored by operational dashboards

**Inputs From**:
- helm-chart-architect: Helm charts and values files
- dockerization-agent: Container image tags
- infra-spec-guardian: Operational approval

**Outputs To**:
- kagent-aiops-analyst: Deployment status for validation
- Operational logs: Audit trail of all operations
- Status dashboards: Real-time deployment health

---

## Key Principles

1. **Natural Language over YAML**: Express intent, not implementation
2. **Intent-Based over Imperative**: What you want, not how to do it
3. **Validation over Hope**: Test with --dry-run first
4. **Diagnosis over Guessing**: Use kubectl-ai to understand failures
5. **Automation over Manual**: Repeatable, documented operations
6. **Safety over Speed**: Rollback capability, health checks, gradual rollout

---

**Status**: Active
**Maintained by**: Phase IV Infrastructure Team
**Last Updated**: 2026-02-03
