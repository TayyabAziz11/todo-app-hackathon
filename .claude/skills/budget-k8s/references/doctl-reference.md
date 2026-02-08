# doctl Command Reference - Context7 Verified

All commands in this document have been verified against official doctl documentation via Context7.

## Installation

**Source: Official DigitalOcean Documentation**

```bash
# Linux
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.104.0/doctl-1.104.0-linux-amd64.tar.gz
tar xf doctl-1.104.0-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin

# macOS (Homebrew)
brew install doctl

# Verify installation
doctl version
```

## Authentication

**Context7-verified commands:**

```bash
# Method 1: Interactive (prompts for token)
doctl auth init

# Method 2: Environment variable (for CI/CD)
export DIGITALOCEAN_ACCESS_TOKEN=dop_v1_your_api_token_here
doctl account get

# Verify authentication
doctl account get
```

## Cluster Creation

**Context7-verified from doctl docs:**

```bash
# Minimal cluster (default: 3 nodes, nyc1, latest version)
doctl kubernetes cluster create my-cluster

# Cost-optimized cluster
doctl kubernetes cluster create hackathon-cluster \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 2 \
  --wait

# Production cluster with all options
doctl kubernetes cluster create production-cluster \
  --region nyc1 \
  --version 1.28.2-do.0 \
  --node-pool "name=worker-pool;size=s-4vcpu-8gb;count=3;auto-scale=true;min-nodes=2;max-nodes=5;label=env=production;taint=dedicated=app:NoSchedule" \
  --ha \
  --auto-upgrade \
  --maintenance-window saturday=02:00 \
  --wait
```

**Available flags:**
- `--region`: Datacenter region (nyc1, nyc3, sfo3, etc.)
- `--version`: Kubernetes version (e.g., 1.28.2-do.0)
- `--size`: Node size (s-2vcpu-4gb, s-4vcpu-8gb, etc.)
- `--count`: Number of nodes
- `--node-pool`: Complex node pool configuration
- `--ha`: Enable high availability (3 control plane nodes)
- `--auto-upgrade`: Enable automatic version upgrades
- `--maintenance-window`: Schedule for maintenance
- `--wait`: Wait for cluster to be ready

## Kubeconfig Management

**Context7-verified commands:**

```bash
# Save cluster credentials to ~/.kube/config
doctl kubernetes cluster kubeconfig save production-cluster

# Show kubeconfig YAML
doctl kubernetes cluster kubeconfig show production-cluster

# Remove cluster from kubeconfig
doctl kubernetes cluster kubeconfig remove production-cluster
```

## Cluster Management

**Context7-verified commands:**

```bash
# List all clusters
doctl kubernetes cluster list

# Get detailed cluster info
doctl kubernetes cluster get production-k8s --format ID,Name,Endpoint,Status

# List clusters as JSON (for scripting)
cluster_id=$(doctl kubernetes cluster list -o json | jq -r '.[0].id')
echo "First cluster ID: $cluster_id"

# Delete cluster (STOPS BILLING)
doctl kubernetes cluster delete my-cluster --force
```

## Node Pool Management

**Context7-verified commands:**

```bash
# Create additional node pool
doctl kubernetes cluster node-pool create production-cluster \
  --name gpu-pool \
  --size g-4vcpu-16gb \
  --count 2 \
  --auto-scale \
  --min-nodes 1 \
  --max-nodes 4 \
  --label workload=ml \
  --taint "gpu=true:NoSchedule"

# Update node pool size
doctl kubernetes cluster node-pool update production-cluster worker-pool --count 5

# Delete node pool
doctl kubernetes cluster node-pool delete production-cluster gpu-pool --force
```

## Cost-Optimized Configurations

**Verified node sizes (as of 2026):**

| Size | vCPU | RAM | Monthly Cost | Best For |
|------|------|-----|--------------|----------|
| s-2vcpu-2gb | 2 | 2GB | $18 | Dev/Test |
| s-2vcpu-4gb | 2 | 4GB | $24 | Hackathons |
| s-4vcpu-8gb | 4 | 8GB | $48 | Small prod |

**Minimum cluster cost:** ~$48/month (2 x s-2vcpu-4gb nodes)

## Common Workflows

### Quick Hackathon Cluster

```bash
# Create
doctl kubernetes cluster create hack-cluster \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 2 \
  --wait

# Get kubeconfig
doctl kubernetes cluster kubeconfig save hack-cluster

# Verify
kubectl get nodes

# Deploy app
kubectl apply -f app.yaml

# TEARDOWN (important!)
doctl kubernetes cluster delete hack-cluster --force
```

### Multiple Clusters

```bash
# List all
doctl kubernetes cluster list

# Switch between clusters
doctl kubernetes cluster kubeconfig save cluster-1
kubectl config use-context do-nyc1-cluster-1

doctl kubernetes cluster kubeconfig save cluster-2
kubectl config use-context do-nyc1-cluster-2

# View contexts
kubectl config get-contexts
```

## Troubleshooting

### Authentication Failures

```bash
# Verify token is set
echo $DIGITALOCEAN_ACCESS_TOKEN

# Re-authenticate
doctl auth init

# Test authentication
doctl account get
```

### Kubeconfig Issues

```bash
# Re-save kubeconfig
doctl kubernetes cluster kubeconfig save my-cluster

# Check kubectl context
kubectl config current-context

# List all contexts
kubectl config get-contexts

# Switch context
kubectl config use-context do-nyc1-my-cluster
```

### Cluster Not Ready

```bash
# Check cluster status
doctl kubernetes cluster get my-cluster

# Wait for cluster
doctl kubernetes cluster create my-cluster --wait

# Check node status
kubectl get nodes
kubectl describe node <node-name>
```

## Official Documentation

For commands not covered by Context7:
- **Official docs:** https://docs.digitalocean.com/reference/doctl/
- **GitHub:** https://github.com/digitalocean/doctl
- **API docs:** https://docs.digitalocean.com/reference/api/
