---
name: argocd
description: |
  Comprehensive ArgoCD GitOps skill for automating Kubernetes deployments from hello-world to production pipelines. Use this skill when working with:
  (1) GitOps workflows and continuous deployment to Kubernetes
  (2) ArgoCD applications, projects, sync policies, or multi-cluster deployments
  (3) Declarative Kubernetes deployments using Git as source of truth
  (4) Installing or configuring ArgoCD (basic or HA mode)
  (5) Application manifests (Git directories, Helm charts, Kustomize, multi-source)
  (6) Sync waves, resource hooks, or deployment ordering
  (7) Multi-tenancy with AppProjects and RBAC
  (8) Production GitOps including automated sync, self-healing, rollbacks
  (9) Any task involving "ArgoCD", "GitOps", "continuous deployment", "declarative deployments"
---

# ArgoCD - GitOps for Kubernetes

Automate Kubernetes deployments using Git as the single source of truth with ArgoCD's declarative GitOps approach.

## Overview

ArgoCD is a declarative GitOps continuous delivery tool for Kubernetes that:
- **Syncs Git to Kubernetes**: Automatically deploys what's in Git
- **Detects Drift**: Monitors cluster state vs Git state
- **Self-Heals**: Reverts manual changes back to Git
- **Multi-Cluster**: Manage deployments across multiple K8s clusters
- **Multi-Tenancy**: Projects + RBAC for team isolation

## Core Workflow

1. **Install ArgoCD**: Deploy ArgoCD control plane to Kubernetes cluster
2. **Connect Repository**: Configure Git repo access
3. **Create Application**: Define what to deploy (source, destination, sync policy)
4. **Sync**: ArgoCD applies manifests from Git to cluster
5. **Monitor**: Track sync status, health, and drift
6. **Update**: Push changes to Git → ArgoCD auto-syncs (if configured)

## Quick Start

### 1. Install ArgoCD

**Development mode:**
```bash
.claude/skills/argocd/scripts/install_argocd.sh dev
```

**High Availability mode:**
```bash
.claude/skills/argocd/scripts/install_argocd.sh ha
```

**Manual installation:**
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

**Access UI:**
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Visit https://localhost:8080
# Username: admin
```

### 2. Install ArgoCD CLI

```bash
# Linux
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd

# macOS
brew install argocd

# Login
argocd login localhost:8080 --username admin --password <password> --insecure
```

### 3. Deploy First Application

**Using hello-world template:**
```bash
# Copy template
cp -r .claude/skills/argocd/assets/hello-world ./my-gitops-repo
cd my-gitops-repo

# Push to Git
git init
git add .
git commit -m "Initial GitOps setup"
git remote add origin https://github.com/YOUR-ORG/YOUR-REPO.git
git push -u origin main

# Update application.yaml with your repo URL
# Then apply
kubectl apply -f application.yaml
```

**Using CLI:**
```bash
argocd app create hello-app \
  --repo https://github.com/YOUR-ORG/YOUR-REPO.git \
  --path k8s \
  --dest-namespace default \
  --dest-server https://kubernetes.default.svc \
  --sync-policy automated \
  --auto-prune \
  --self-heal
```

**Watch deployment:**
```bash
argocd app get hello-app
argocd app sync hello-app  # Manual sync if needed
```

## Creating Applications

### Generator Script

```bash
# Basic Git application
python .claude/skills/argocd/scripts/create_application.py myapp \
  --repo https://github.com/myorg/myapp.git \
  --path k8s/manifests \
  --dest-namespace production \
  --auto-sync \
  --output myapp.yaml

# Helm application
python .claude/skills/argocd/scripts/create_application.py nginx \
  --repo https://charts.bitnami.com/bitnami \
  --path "" \
  --helm-chart nginx \
  --dest-namespace webapps \
  --helm-set replicaCount=3 \
  --helm-set service.type=LoadBalancer \
  --auto-sync \
  --output nginx.yaml
```

### Application Types

**1. Git Directory (plain YAML):**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myapp.git
    targetRevision: main
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

**2. Helm Chart:**
```yaml
spec:
  source:
    repoURL: https://charts.bitnami.com/bitnami
    chart: nginx
    targetRevision: 13.2.0
    helm:
      releaseName: my-nginx
      valueFiles:
        - values-prod.yaml
      parameters:
        - name: replicaCount
          value: "3"
```

**3. Kustomize:**
```yaml
spec:
  source:
    path: kustomize-guestbook
    kustomize:
      namePrefix: prod-
      images:
        - gcr.io/heptio-images/ks-guestbook-demo:0.2
```

**Reference**: See `references/applications.md` for complete guide including multi-source apps.

## Sync Policies

**Automated Sync** (GitOps best practice):
```yaml
spec:
  syncPolicy:
    automated:
      prune: true        # Delete resources removed from Git
      selfHeal: true     # Revert manual changes
    syncOptions:
      - CreateNamespace=true
```

**Manual Sync** (requires explicit trigger):
```yaml
spec:
  syncPolicy: {}  # or omit
```

**Sync Waves** (control deployment order):
```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "1"  # Deploy in order: -5, 0, 1, 5, 10
```

**Resource Hooks** (run jobs at specific phases):
```yaml
metadata:
  annotations:
    argocd.argoproj.io/hook: PreSync  # or Sync, PostSync, SyncFail
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
```

**Example - Database migration before deployment:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrate
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
    argocd.argoproj.io/sync-wave: "-1"
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: myapp:migrations
        command: ["./migrate.sh"]
      restartPolicy: Never
```

## Projects (Multi-Tenancy)

AppProjects provide logical grouping and access control:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: team-alpha
  namespace: argocd
spec:
  description: Team Alpha Projects
  sourceRepos:
    - https://github.com/myorg/team-alpha-*
  destinations:
    - namespace: team-alpha-*
      server: https://kubernetes.default.svc
  clusterResourceWhitelist:
    - group: ''
      kind: Namespace
  roles:
    - name: developer
      policies:
        - p, proj:team-alpha:developer, applications, *, team-alpha/*, allow
      groups:
        - team-alpha-devs
```

**Benefits**:
- Restrict Git repos teams can deploy from
- Limit K8s clusters/namespaces teams can deploy to
- Control resource types (prevent creating cluster-wide resources)
- RBAC with roles and group mappings

## CLI Commands

**Application management:**
```bash
# List apps
argocd app list

# Get details
argocd app get APP_NAME

# Sync (deploy)
argocd app sync APP_NAME
argocd app sync APP_NAME --prune --dry-run  # Preview

# Enable auto-sync
argocd app set APP_NAME --sync-policy automated --auto-prune --self-heal

# Diff (show changes)
argocd app diff APP_NAME

# Rollback
argocd app rollback APP_NAME

# Delete
argocd app delete APP_NAME
```

**Monitoring:**
```bash
# Watch sync status
argocd app wait APP_NAME --sync --health

# View history
argocd app history APP_NAME

# Get generated manifests
argocd app manifests APP_NAME
```

## Production Patterns

### High Availability

Use HA installation:
```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/ha/install.yaml
```

Features:
- 3 replicas for each component
- Redis HA with Sentinel
- Leader election for controllers

### Multi-Cluster

Add external clusters:
```bash
# List contexts
kubectl config get-contexts

# Add cluster
argocd cluster add CONTEXT_NAME

# List clusters
argocd cluster list
```

Deploy to multiple clusters from single ArgoCD instance.

### App of Apps Pattern

Manage multiple applications with one parent app:

```yaml
# apps/team-alpha.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: team-alpha-apps
  namespace: argocd
spec:
  project: team-alpha
  source:
    repoURL: https://github.com/myorg/argocd-apps.git
    path: team-alpha/applications
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
```

Directory structure:
```
team-alpha/
└── applications/
    ├── frontend-app.yaml
    ├── backend-app.yaml
    └── database-app.yaml
```

### Environment Promotion

Use branches or directories for environments:

**Branch-based:**
- `dev` branch → dev cluster
- `staging` branch → staging cluster
- `main` branch → production cluster

**Directory-based:**
```
apps/
├── base/
│   └── deployment.yaml
├── dev/
│   └── kustomization.yaml
├── staging/
│   └── kustomization.yaml
└── prod/
    └── kustomization.yaml
```

### GitOps Workflow

1. Developer creates PR with manifest changes
2. CI validates manifests (kubeval, policy checks)
3. PR merged to `dev` branch → ArgoCD syncs to dev cluster
4. After testing, promote to `staging` branch
5. After validation, promote to `main` → production deployment
6. All changes tracked in Git history

## Reference Files

- **`references/core-concepts.md`**: Core terminology, states, sync phases, hooks
- **`references/applications.md`**: Complete application creation guide (Git, Helm, Kustomize, multi-source)

## Scripts

- **`scripts/install_argocd.sh <mode>`**: Install ArgoCD (dev/ha modes)
- **`scripts/create_application.py`**: Generate Application YAML files

## Assets

- **`assets/hello-world/`**: Complete GitOps repository template with Deployment, Service, and Application manifest

## Troubleshooting

**App stuck OutOfSync:**
- Check: `argocd app get APP_NAME`
- View diff: `argocd app diff APP_NAME`
- Force sync: `argocd app sync APP_NAME --force`

**Sync fails:**
- Check app logs: `kubectl logs -n argocd deployment/argocd-application-controller`
- View sync operation: `argocd app get APP_NAME`
- Check RBAC: Ensure ArgoCD service account has permissions

**Slow syncs:**
- Increase timeout: Add annotation `argocd.argoproj.io/sync-options: Timeout=600`
- Check webhook: Use webhooks instead of polling

## Best Practices

1. **Use automated sync + prune + self-heal** for true GitOps
2. **Organize with Projects** for multi-tenancy
3. **Use sync waves** for ordered deployments (DB before app)
4. **Test in dev** before promoting to production
5. **Version everything** in Git including Application manifests
6. **Monitor drift** with alerts on OutOfSync status
7. **Use hooks** for migrations, smoke tests, notifications
8. **Implement RBAC** with Projects and roles
9. **Enable HA** for production ArgoCD installations
10. **Backup Git repos** - they're your source of truth

## Additional Resources

- Official Docs: https://argo-cd.readthedocs.io
- GitHub: https://github.com/argoproj/argo-cd
- Slack: https://argoproj.github.io/community/join-slack
- Examples: https://github.com/argoproj/argocd-example-apps
