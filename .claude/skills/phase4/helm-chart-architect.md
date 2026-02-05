# Helm Chart Architect Skill

**Skill Name**: `helm-chart-architect`
**Category**: Phase IV - Kubernetes Deployment
**Purpose**: Design and generate parameterized Helm charts for Kubernetes deployment of Todo App services
**Version**: 1.0.0
**Created**: 2026-02-03

---

## Role

Design and generate production-ready Helm charts for Kubernetes deployment of the Todo App frontend and backend services using AI-assisted tooling.

## Responsibilities

- Create Helm charts for frontend and backend services
- Parameterize all deployment configurations:
  - Image repository and tag
  - Replica counts
  - Port mappings
  - Environment variables
  - Resource limits and requests
  - Health check configurations
- Ensure Minikube compatibility for local development
- Support scaling and upgrade operations
- Follow Helm best practices and conventions
- Generate comprehensive documentation

## Applicable Agents

- **Primary**: helm-chart-architect agent
- **Supporting**: infra-spec-guardian (validation), dockerization-agent (image metadata)
- **Context**: After containerization, before Kubernetes deployment

## Input

- Containerized application images (from dockerization-agent):
  - Image names and tags (e.g., `todo-backend:v1.0.0`)
  - Exposed ports and protocols
  - Environment variable requirements
  - Health check endpoints
- Application requirements:
  - Service dependencies (backend requires database)
  - Resource requirements (CPU, memory)
  - Scaling parameters (min/max replicas)
  - ConfigMaps and Secrets needed
- Deployment context:
  - Target environment (Minikube for Phase IV)
  - Namespace preferences
  - Ingress requirements

## Output

### Helm Chart Structure
```
charts/
├── todo-backend/
│   ├── Chart.yaml          # Chart metadata
│   ├── values.yaml         # Default configuration values
│   ├── values-dev.yaml     # Development/Minikube overrides
│   ├── templates/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   ├── secrets.yaml    # Template only, values externalized
│   │   ├── ingress.yaml    # Optional
│   │   ├── hpa.yaml        # Horizontal Pod Autoscaler
│   │   ├── _helpers.tpl    # Template helpers
│   │   └── NOTES.txt       # Post-install instructions
│   └── README.md
└── todo-frontend/
    └── [same structure]
```

### Chart.yaml
- Chart name, version, description
- API version (v2)
- App version matching container image tag
- Dependencies (if any)
- Maintainer information

### values.yaml
- Parameterized configuration with sensible defaults
- Image repository and tag
- Replica count
- Service type and ports
- Resource limits and requests
- Environment variables (non-sensitive)
- Ingress configuration
- Autoscaling parameters

### templates/*
- Kubernetes manifests with Go templating
- Deployment, Service, ConfigMap, Ingress, HPA
- Proper label selectors and annotations
- Health check configurations
- Resource requests/limits

## Scope & Boundaries

### Can Do
- Generate complete Helm chart structure
- Parameterize all deployment configurations
- Create reusable templates with helpers
- Design for scalability and upgrades
- Include documentation and examples
- Support multiple environments (dev, prod)
- Implement best practices (labels, annotations, health checks)
- Create values files for different environments

### Cannot Do
- Manually write raw Kubernetes YAML outside Helm templates
- Deploy charts to Kubernetes (use kubectl-ai-operator)
- Include sensitive secrets in values files
- Bypass infra-spec-guardian validation
- Create charts without parameterization

## Constraints

- **No Raw Kubernetes YAML**: All Kubernetes resources must be Helm templates
- **Charts Must Support Scaling**: Horizontal Pod Autoscaler templates included
- **Charts Must Support Upgrades**: Proper versioning and rollback capability
- **Minikube Compatible**: Work with local Kubernetes clusters
- **Secrets Externalized**: No hardcoded secrets in values files
- **Fully Parameterized**: All environment-specific values in values.yaml

## Reusability Notes

- Template structure reusable for any microservice deployment
- Helm helpers (_helpers.tpl) provide reusable label generation
- Values files support environment-specific overrides
- Chart versioning enables controlled upgrades
- Applicable to Phase IV and future production deployments

## Dependencies

- Helm 3.x installed
- Docker images from dockerization-agent
- Kubernetes cluster access (Minikube for Phase IV)
- infra-spec-guardian approval
- kubectl for validation

## Quality Expectations

### Chart Quality Standards
- [ ] Chart.yaml complete with all metadata
- [ ] values.yaml with comprehensive parameterization
- [ ] All templates use Go templating (no hardcoded values)
- [ ] _helpers.tpl defines reusable functions
- [ ] NOTES.txt provides clear post-install instructions
- [ ] README.md documents all values and usage

### Kubernetes Resource Quality
- [ ] Deployments use rolling update strategy
- [ ] Services properly expose application ports
- [ ] Health checks (liveness, readiness) configured
- [ ] Resource limits and requests defined
- [ ] Labels follow Kubernetes conventions
- [ ] Annotations include deployment metadata

### Parameterization Quality
- [ ] All environment-specific values externalized
- [ ] Sensible defaults in values.yaml
- [ ] Support for values file overrides (-f flag)
- [ ] No hardcoded secrets or credentials
- [ ] Image repository and tag parameterized
- [ ] Replica count configurable

### Minikube Compatibility
- [ ] Service type supports NodePort or LoadBalancer
- [ ] Resource requests fit Minikube constraints
- [ ] Ingress configured for Minikube ingress addon
- [ ] No external dependencies on cloud services
- [ ] Works with local Docker registry

## Execution Workflow

### Step 1: Chart Structure Creation
1. Create directory structure for each service (backend, frontend)
2. Initialize Chart.yaml with metadata
3. Create templates directory
4. Add _helpers.tpl for reusable functions
5. Create README.md template

### Step 2: Template Generation
For each service:
1. **Deployment**: Pod template, replicas, rolling strategy, health checks
2. **Service**: Expose ports, service type, selectors
3. **ConfigMap**: Non-sensitive environment configuration
4. **Secrets**: Template for sensitive data (values externalized)
5. **Ingress**: Optional HTTP routing rules
6. **HPA**: Horizontal Pod Autoscaler for scaling

### Step 3: Parameterization
1. Create values.yaml with defaults
2. Parameterize all environment-specific values
3. Create values-dev.yaml for Minikube overrides
4. Add validation for required values
5. Document all parameters in README

### Step 4: Helper Functions
Create _helpers.tpl with:
- Chart name generator
- Full name generator
- Label selectors (app, version, component)
- Service account name
- Common annotations

### Step 5: Documentation
1. Chart README with installation instructions
2. NOTES.txt with post-install guidance
3. values.yaml comments explaining each parameter
4. Example values files for different environments

### Step 6: Validation
1. Lint chart: `helm lint charts/todo-backend`
2. Template rendering: `helm template charts/todo-backend`
3. Dry-run install: `helm install --dry-run --debug`
4. Verify against infra-spec-guardian requirements

## Example Use Case

```
Context: Creating Helm chart for Todo Backend (FastAPI)

Input from dockerization-agent:
  - Image: todo-backend:v1.0.0
  - Port: 8000
  - Health endpoint: /health
  - Environment variables: DATABASE_URL, SECRET_KEY, CORS_ORIGINS
  - Resource recommendations: 256Mi memory, 0.25 CPU

Execution:

Step 1: Create Chart Structure
  charts/todo-backend/
  ├── Chart.yaml
  ├── values.yaml
  ├── values-dev.yaml
  ├── templates/
  └── README.md

Step 2: Chart.yaml
  ```yaml
  apiVersion: v2
  name: todo-backend
  description: Todo App Backend API
  type: application
  version: 1.0.0
  appVersion: "v1.0.0"
  maintainers:
    - name: Todo App Team
  ```

Step 3: values.yaml
  ```yaml
  replicaCount: 2

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

  env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: todo-backend-secrets
          key: database-url
    - name: SECRET_KEY
      valueFrom:
        secretKeyRef:
          name: todo-backend-secrets
          key: secret-key
    - name: CORS_ORIGINS
      value: "http://localhost:3000,http://localhost:8080"

  healthCheck:
    livenessProbe:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 30
    readinessProbe:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 5
      periodSeconds: 10

  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 80
  ```

Step 4: values-dev.yaml (Minikube overrides)
  ```yaml
  replicaCount: 1

  service:
    type: NodePort
    nodePort: 30800

  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "250m"

  autoscaling:
    enabled: false
  ```

Step 5: templates/deployment.yaml
  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: {{ include "todo-backend.fullname" . }}
    labels:
      {{- include "todo-backend.labels" . | nindent 4 }}
  spec:
    replicas: {{ .Values.replicaCount }}
    selector:
      matchLabels:
        {{- include "todo-backend.selectorLabels" . | nindent 6 }}
    template:
      metadata:
        labels:
          {{- include "todo-backend.selectorLabels" . | nindent 8 }}
      spec:
        containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
          - name: http
            containerPort: {{ .Values.service.targetPort }}
            protocol: TCP
          env:
          {{- toYaml .Values.env | nindent 10 }}
          livenessProbe:
            {{- toYaml .Values.healthCheck.livenessProbe | nindent 10 }}
          readinessProbe:
            {{- toYaml .Values.healthCheck.readinessProbe | nindent 10 }}
          resources:
            {{- toYaml .Values.resources | nindent 10 }}
  ```

Step 6: templates/service.yaml
  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: {{ include "todo-backend.fullname" . }}
    labels:
      {{- include "todo-backend.labels" . | nindent 4 }}
  spec:
    type: {{ .Values.service.type }}
    ports:
    - port: {{ .Values.service.port }}
      targetPort: {{ .Values.service.targetPort }}
      protocol: TCP
      name: http
      {{- if and (eq .Values.service.type "NodePort") .Values.service.nodePort }}
      nodePort: {{ .Values.service.nodePort }}
      {{- end }}
    selector:
      {{- include "todo-backend.selectorLabels" . | nindent 4 }}
  ```

Step 7: templates/_helpers.tpl
  ```yaml
  {{- define "todo-backend.name" -}}
  {{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
  {{- end }}

  {{- define "todo-backend.fullname" -}}
  {{- printf "%s-%s" .Release.Name (include "todo-backend.name" .) | trunc 63 | trimSuffix "-" }}
  {{- end }}

  {{- define "todo-backend.labels" -}}
  helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
  app.kubernetes.io/name: {{ include "todo-backend.name" . }}
  app.kubernetes.io/instance: {{ .Release.Name }}
  app.kubernetes.io/version: {{ .Chart.AppVersion }}
  app.kubernetes.io/managed-by: {{ .Release.Service }}
  {{- end }}

  {{- define "todo-backend.selectorLabels" -}}
  app.kubernetes.io/name: {{ include "todo-backend.name" . }}
  app.kubernetes.io/instance: {{ .Release.Name }}
  {{- end }}
  ```

Step 8: Installation Commands
  ```bash
  # Lint the chart
  helm lint charts/todo-backend

  # Install to Minikube with dev values
  helm install todo-backend charts/todo-backend \
    -f charts/todo-backend/values-dev.yaml \
    --namespace todo-dev \
    --create-namespace

  # Verify deployment
  kubectl get all -n todo-dev

  # Upgrade
  helm upgrade todo-backend charts/todo-backend \
    -f charts/todo-backend/values-dev.yaml

  # Rollback if needed
  helm rollback todo-backend 1
  ```

Output Delivered:
  ✅ Complete Helm chart structure for backend
  ✅ Parameterized values.yaml with sensible defaults
  ✅ Minikube-compatible values-dev.yaml
  ✅ All Kubernetes resources as Helm templates
  ✅ Health checks configured
  ✅ Autoscaling support (HPA)
  ✅ Documentation and installation instructions
```

## Best Practices Enforced

### Helm Chart Best Practices
1. **Versioning**: Semantic versioning for chart and app
2. **Labels**: Standard Kubernetes labels on all resources
3. **Helpers**: Reusable template functions in _helpers.tpl
4. **NOTES.txt**: Clear post-install instructions
5. **README**: Comprehensive documentation

### Kubernetes Best Practices
1. **Rolling Updates**: Deployment strategy for zero-downtime upgrades
2. **Health Checks**: Liveness and readiness probes
3. **Resource Limits**: CPU and memory requests/limits
4. **Secrets Management**: Externalized, never in values
5. **Service Discovery**: Proper service selectors and ports

### Parameterization Best Practices
1. **Sensible Defaults**: Values work out-of-box
2. **Environment Overrides**: Separate values files per environment
3. **Required Values**: Validation for mandatory parameters
4. **Documentation**: Comments explaining each value
5. **Flexibility**: Support multiple deployment scenarios

## Integration with Phase IV Workflow

**Position in Workflow**:
```
Phase IV: Dockerization → [HELM CHART ARCHITECT] → K8s Deployment
```

**Coordination Points**:
1. After dockerization-agent produces container images
2. Before kubectl-ai-operator deploys to Kubernetes
3. Validated by infra-spec-guardian for compliance
4. Used by kagent-aiops-analyst for operational validation

**Inputs From**:
- dockerization-agent: Image names, tags, ports, health endpoints
- Phase IV spec: Resource requirements, scaling parameters
- infra-spec-guardian: Compliance requirements

**Outputs To**:
- kubectl-ai-operator: Charts ready for deployment
- kagent-aiops-analyst: Deployment targets for monitoring

## Common Patterns

### Pattern 1: Microservice Chart
Standard chart for stateless application services (backend API, frontend).

### Pattern 2: Stateful Service Chart
Chart for databases or persistent services (PostgreSQL, Redis).

### Pattern 3: Multi-Environment Chart
Single chart with values overrides for dev, staging, production.

### Pattern 4: Umbrella Chart
Parent chart that deploys multiple sub-charts (full stack).

## Troubleshooting Guide

### Chart Lint Failures
```bash
helm lint charts/todo-backend
# Fix YAML syntax, indentation, or missing required fields
```

### Template Rendering Errors
```bash
helm template charts/todo-backend --debug
# Check for undefined values or template syntax errors
```

### Installation Failures
```bash
helm install --dry-run --debug todo-backend charts/todo-backend
# Identify Kubernetes resource validation errors
```

### Upgrade Issues
```bash
helm diff upgrade todo-backend charts/todo-backend
# Preview changes before applying upgrade
```

---

## Key Principles

1. **Parameterization over Hardcoding**: Everything configurable via values
2. **Reusability over Duplication**: Helpers for common patterns
3. **Convention over Configuration**: Follow Helm and K8s standards
4. **Documentation over Assumption**: Clear README and comments
5. **Validation over Hope**: Lint, template, dry-run before deploy
6. **Scalability over Static**: Support autoscaling and upgrades

---

**Status**: Active
**Maintained by**: Phase IV Infrastructure Team
**Last Updated**: 2026-02-03
