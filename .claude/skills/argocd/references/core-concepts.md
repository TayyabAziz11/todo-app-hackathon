# ArgoCD Core Concepts

Essential ArgoCD terminology and architecture.

## Core Components

**Application**: A Kubernetes Custom Resource (CRD) representing a deployed app. Contains source (Git repo), destination (K8s cluster/namespace), and sync configuration.

**Project (AppProject)**: Logical grouping providing multi-tenancy via source repo restrictions, destination limits, and RBAC.

**Repository**: Git repos or Helm chart repos containing application manifests.

**Cluster**: Kubernetes clusters where applications deploy (can manage multiple clusters from one ArgoCD instance).

## Key States

**Target State**: Desired state defined in Git (the "source of truth").

**Live State**: Current state running in Kubernetes cluster.

**Sync Status**:
- **Synced**: Live state matches target state
- **OutOfSync**: Differences detected between Git and cluster
- **Unknown**: Unable to determine status

**Health Status**:
- **Healthy**: App running correctly, can serve requests
- **Progressing**: Deployment in progress
- **Degraded**: App experiencing issues
- **Suspended**: Manually paused
- **Missing**: Resources don't exist
- **Unknown**: Cannot determine health

**Sync Operation**: Process of applying Git manifests to cluster to achieve target state.

**Refresh**: Compare Git with live state without applying changes (detect drift).

## Application Source Types

**Git Directory**: Plain YAML/JSON manifests

**Helm**: Helm charts with custom values

**Kustomize**: Kustomize applications with overlays

**Jsonnet**: Jsonnet files

**Plugin**: Custom config management tools

## Sync Policies

**Manual Sync**: Requires explicit user trigger

**Automated Sync**: Applies changes automatically when Git changes
- **Prune**: Delete resources removed from Git
- **Self-Heal**: Revert manual cluster changes back to Git state
- **Allow Empty**: Allow syncing with no resources

## Sync Phases & Waves

**Phases** (order of execution):
1. **PreSync**: Run before main sync (e.g., database migrations)
2. **Sync**: Apply main application resources
3. **PostSync**: Run after sync succeeds (e.g., notifications, smoke tests)
4. **SyncFail**: Run if sync fails (e.g., rollback, alerts)

**Waves**: Fine-grained ordering within each phase using annotation `argocd.argoproj.io/sync-wave: "N"`. Lower numbers deploy first (can be negative).

**Example**: Wave -5 → Wave 0 → Wave 5 → Wave 10

## Hooks

Resource hooks execute at specific sync phases:

```yaml
metadata:
  annotations:
    argocd.argoproj.io/hook: PreSync  # or Sync, PostSync, SyncFail, Skip
    argocd.argoproj.io/hook-delete-policy: HookSucceeded  # or HookFailed, BeforeHookCreation
```

Common hook patterns:
- **PreSync**: Database migrations, schema updates
- **PostSync**: Smoke tests, notifications, cache warming
- **SyncFail**: Rollback procedures, incident alerts

## GitOps Workflow

1. Developer commits code → CI builds container image
2. Developer/CI updates manifest in Git with new image tag
3. ArgoCD detects Git change (polling or webhook)
4. ArgoCD compares Git (target) vs cluster (live)
5. If automated sync enabled: ArgoCD applies changes
6. If manual sync: User reviews diff and triggers sync
7. ArgoCD monitors deployment health
8. App reaches Healthy state or reports issues

## Multi-Tenancy with Projects

Projects enable:
- **Source restrictions**: Limit which repos teams can deploy from
- **Destination restrictions**: Limit which clusters/namespaces teams can deploy to
- **Resource whitelists/blacklists**: Control which K8s resource types are allowed
- **RBAC**: Define roles with granular permissions per project
- **JWT tokens**: Generate tokens for CI/CD systems

## Health Assessment

ArgoCD assesses health for standard K8s resources:
- **Deployment/ReplicaSet**: Check replicas available
- **StatefulSet**: Check ready replicas
- **DaemonSet**: Check desired vs current
- **Service**: Always healthy if exists
- **Ingress**: Healthy if backend services healthy
- **PersistentVolumeClaim**: Healthy if bound

Custom health checks via Lua scripts for CRDs.

## Comparison & Diff

**Diff strategies**:
- **Structured**: Compare parsed manifests (default)
- **Text**: Line-by-line comparison

**Ignore differences**: Exclude certain fields from sync status:
```yaml
spec:
  ignoreDifferences:
  - group: apps
    kind: Deployment
    jsonPointers:
    - /spec/replicas  # Ignore replica count differences
```

## Resource Tracking

ArgoCD tracks resources using labels:
- Default: `app.kubernetes.io/instance: <app-name>`
- Alternative: Annotations (for resources that don't support labels)

## Orphaned Resources

Resources in cluster not defined in Git but previously managed by ArgoCD. Can be pruned or adopted.
