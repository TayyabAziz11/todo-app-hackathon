# ArgoCD Applications Reference

Complete guide to creating and managing ArgoCD Applications.

## Table of Contents
1. [Basic Application Structure](#basic-application-structure)
2. [Git Directory Applications](#git-directory-applications)
3. [Helm Applications](#helm-applications)
4. [Kustomize Applications](#kustomize-applications)
5. [Multi-Source Applications](#multi-source-applications)
6. [Sync Policies](#sync-policies)
7. [CLI Commands](#cli-commands)

---

## Basic Application Structure

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io  # Cleanup on deletion
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myrepo.git
    targetRevision: main
    path: k8s/manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

**Key fields**:
- `metadata.finalizers`: Ensures proper resource cleanup
- `spec.project`: AppProject name (default: `default`)
- `spec.source`: Where manifests come from
- `spec.destination`: Where to deploy
- `spec.syncPolicy`: How to sync

---

## Git Directory Applications

**Plain YAML:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: guestbook
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/argoproj/argocd-example-apps.git
    targetRevision: HEAD
    path: guestbook
  destination:
    server: https://kubernetes.default.svc
    namespace: default
```

**CLI equivalent:**
```bash
argocd app create guestbook \
  --repo https://github.com/argoproj/argocd-example-apps.git \
  --path guestbook \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace default
```

---

## Helm Applications

**From Helm repository:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: nginx
  namespace: argocd
spec:
  project: default
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
        - name: service.type
          value: LoadBalancer
  destination:
    server: https://kubernetes.default.svc
    namespace: webapps
```

**From Git (Helm chart in Git):**
```yaml
source:
  repoURL: https://github.com/myorg/charts.git
  path: charts/myapp
  targetRevision: main
  helm:
    valueFiles:
      - values-prod.yaml
    parameters:
      - name: image.tag
        value: "v1.2.3"
```

**CLI:**
```bash
argocd app create nginx-helm \
  --repo https://charts.bitnami.com/bitnami \
  --helm-chart nginx \
  --revision 13.2.0 \
  --dest-namespace webapps \
  --dest-server https://kubernetes.default.svc \
  --helm-set replicaCount=3 \
  --helm-set service.type=LoadBalancer
```

---

## Kustomize Applications

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: kustomize-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/argoproj/argocd-example-apps.git
    path: kustomize-guestbook
    targetRevision: HEAD
    kustomize:
      namePrefix: prod-
      nameSuffix: -v1
      images:
        - gcr.io/heptio-images/ks-guestbook-demo:0.2
      commonLabels:
        environment: production
  destination:
    server: https://kubernetes.default.svc
    namespace: kustomize-demo
```

**CLI:**
```bash
argocd app create kustomize-app \
  --repo https://github.com/argoproj/argocd-example-apps.git \
  --path kustomize-guestbook \
  --dest-namespace kustomize-demo \
  --dest-server https://kubernetes.default.svc \
  --kustomize-image gcr.io/heptio-images/ks-guestbook-demo:0.2
```

---

## Multi-Source Applications

Combine multiple Git repos or Helm charts:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: multi-source-app
  namespace: argocd
spec:
  project: default
  sources:
    # Base Helm chart
    - repoURL: https://charts.bitnami.com/bitnami
      chart: postgresql
      targetRevision: 12.1.0
      helm:
        valueFiles:
          - $values/helm-values/postgres-prod.yaml  # From another source
      ref: postgres-chart

    # Custom values repository
    - repoURL: https://github.com/myorg/helm-values.git
      targetRevision: main
      ref: values  # Referenced by $values

    # Additional manifests
    - repoURL: https://github.com/myorg/k8s-configs.git
      path: postgresql/monitoring
      targetRevision: main

  destination:
    server: https://kubernetes.default.svc
    namespace: databases
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

**Use case**: Separate Helm chart, values repo, and additional configs (monitoring, policies).

---

## Sync Policies

**Manual sync (default):**
```yaml
spec:
  syncPolicy: {}  # or omit entirely
```

**Automated sync:**
```yaml
spec:
  syncPolicy:
    automated:
      prune: true        # Delete resources removed from Git
      selfHeal: true     # Revert manual changes to Git state
      allowEmpty: false  # Prevent deploying empty app
```

**Sync options:**
```yaml
spec:
  syncPolicy:
    syncOptions:
      - CreateNamespace=true          # Create namespace if missing
      - PrunePropagationPolicy=foreground  # How to delete resources
      - PruneLast=true                # Prune after other resources synced
      - Replace=true                  # Use replace instead of apply
      - ServerSideApply=true          # Use server-side apply
      - Validate=false                # Skip kubectl validation
```

**Retry policy:**
```yaml
spec:
  syncPolicy:
    retry:
      limit: 5
      backoff:
        duration: 5s      # Initial wait
        factor: 2         # Exponential multiplier
        maxDuration: 3m   # Max wait between retries
```

**Ignore differences:**
```yaml
spec:
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas
      jqPathExpressions:
        - '.spec.template.spec.containers[]?.image'
```

---

## CLI Commands

**Create application:**
```bash
argocd app create APP_NAME \
  --repo REPO_URL \
  --path PATH \
  --dest-server SERVER \
  --dest-namespace NAMESPACE
```

**List applications:**
```bash
argocd app list
argocd app list --project my-project
argocd app list --selector environment=production
```

**Get application details:**
```bash
argocd app get APP_NAME
argocd app get APP_NAME --refresh  # Force refresh from Git
```

**Sync application:**
```bash
argocd app sync APP_NAME
argocd app sync APP_NAME --prune  # Also delete orphaned resources
argocd app sync APP_NAME --dry-run  # Preview changes
argocd app sync APP_NAME --force  # Force sync even if no changes
```

**Enable auto-sync:**
```bash
argocd app set APP_NAME --sync-policy automated
argocd app set APP_NAME --sync-policy automated --auto-prune --self-heal
```

**Disable auto-sync:**
```bash
argocd app set APP_NAME --sync-policy none
```

**Delete application:**
```bash
argocd app delete APP_NAME
argocd app delete APP_NAME --cascade=false  # Keep K8s resources
```

**Diff (show differences):**
```bash
argocd app diff APP_NAME
argocd app diff APP_NAME --local PATH  # Compare with local manifests
```

**Rollback:**
```bash
argocd app rollback APP_NAME  # Rollback to previous synced state
argocd app rollback APP_NAME HISTORY_ID  # Rollback to specific version
```

**History:**
```bash
argocd app history APP_NAME
```

**Terminate operation:**
```bash
argocd app terminate-op APP_NAME
```

**Wait for sync:**
```bash
argocd app wait APP_NAME --sync
argocd app wait APP_NAME --health
argocd app wait APP_NAME --timeout 300  # 5 minutes
```

**Resource actions:**
```bash
argocd app resources APP_NAME
argocd app manifests APP_NAME  # Show generated manifests
```

**Patch application:**
```bash
argocd app patch APP_NAME --patch '{"spec": {"source": {"targetRevision": "v2.0.0"}}}' --type merge
```

---

## Best Practices

1. **Always use finalizers** to ensure proper cleanup
2. **Use Projects** to organize and secure applications
3. **Enable auto-sync** with prune + self-heal for GitOps
4. **Ignore expected differences** (like HPA-managed replicas)
5. **Use sync waves** for ordered deployments
6. **Test with --dry-run** before syncing to production
7. **Monitor sync health** with alerts
8. **Version control everything** including Application manifests
