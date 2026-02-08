---
name: budget-k8s
description: |
  Budget-friendly Kubernetes cluster provisioning on DigitalOcean for hackathons and learning. Use this skill when:
  (1) Need cheap Kubernetes cluster for hackathons or prototypes
  (2) Want to learn Kubernetes without expensive cloud bills
  (3) Need to quickly spin up and tear down clusters
  (4) Working with DigitalOcean Kubernetes (DOKS)
  (5) Using doctl CLI for cluster management
  (6) Cost control is a priority (~$48/month minimum)
  (7) Any mention of "cheap kubernetes", "budget k8s", "hackathon deployment", "DOKS", or "doctl"

  ALL COMMANDS VERIFIED VIA CONTEXT7 - No hallucinated flags.
---

# Budget Kubernetes - DigitalOcean Edition

Spin up cost-optimized Kubernetes clusters on DigitalOcean for hackathons and learning. Fast setup, easy teardown, ~$48/month minimum.

## Overview

DigitalOcean Kubernetes (DOKS) is the easiest and most affordable managed Kubernetes for learning and hackathons:
- **Setup**: 5-10 minutes from zero to working cluster
- **Cost**: ~$48/month for 2-node cluster (s-2vcpu-4gb nodes @ $24 each)
- **Free trial**: $200 credit for new accounts
- **Teardown**: One command to stop all charges

**⚠️ COST WARNING:** Clusters bill hourly. Always delete when done!

## Prerequisites

### 1. DigitalOcean Account

Sign up at https://www.digitalocean.com/
- New accounts get $200 credit (60 days)
- Requires credit card for verification

### 2. Install doctl

**Context7-verified installation:**

```bash
# Linux
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.104.0/doctl-1.104.0-linux-amd64.tar.gz
tar xf doctl-1.104.0-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin

# macOS
brew install doctl

# Windows (via Chocolatey)
choco install doctl

# Verify
doctl version
```

### 3. Create API Token

1. Go to https://cloud.digitalocean.com/account/api/tokens
2. Click "Generate New Token"
3. Name: `doctl-access` (or any name)
4. Scopes: **Read + Write**
5. Copy the token (shown only once!)

### 4. Authenticate doctl

**Context7-verified command:**

```bash
doctl auth init
# Paste your API token when prompted

# Verify authentication
doctl account get
```

**For CI/CD (environment variable):**
```bash
export DIGITALOCEAN_ACCESS_TOKEN=dop_v1_your_token_here
doctl account get
```

## Quick Start (5-Minute Cluster)

### Using the Automated Script

**Context7-verified commands used in script:**

```bash
# Create cluster (prompts for confirmation)
.claude/skills/budget-k8s/scripts/create-doks-cluster.sh hackathon-cluster nyc1 s-2vcpu-4gb 2

# This runs (Context7-verified):
# doctl kubernetes cluster create hackathon-cluster \
#   --region nyc1 \
#   --size s-2vcpu-4gb \
#   --count 2 \
#   --wait
```

**What happens:**
1. Shows cost estimate (~$48/month)
2. Creates 2-node cluster
3. Waits for cluster to be ready (5-10 min)
4. Saves kubeconfig to `~/.kube/config`
5. Displays teardown command

### Manual Creation

**Context7-verified commands:**

```bash
# Create cluster
doctl kubernetes cluster create my-cluster \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 2 \
  --wait

# Get kubeconfig
doctl kubernetes cluster kubeconfig save my-cluster

# Verify
kubectl get nodes
```

### Deploy Your App

```bash
# Standard kubectl commands (works across all K8s)
kubectl apply -f deployment.yaml
kubectl get pods
kubectl expose deployment myapp --type=LoadBalancer --port=80
```

### 🗑️ TEARDOWN (Stop Charges!)

**Context7-verified deletion:**

```bash
# Using script (prompts for confirmation)
.claude/skills/budget-k8s/scripts/delete-doks-cluster.sh hackathon-cluster

# Manual
doctl kubernetes cluster delete my-cluster --force
doctl kubernetes cluster kubeconfig remove my-cluster
```

**IMPORTANT:** Deleting the cluster stops all charges immediately.

## Cost Breakdown (as of 2026-02)

**Node Sizes:**

| Size | vCPU | RAM | Cost/Month | Cost/Hour | Best For |
|------|------|-----|------------|-----------|----------|
| s-2vcpu-2gb | 2 | 2GB | $18 | $0.024 | Tiny apps |
| s-2vcpu-4gb | 2 | 4GB | $24 | $0.032 | Hackathons ✅ |
| s-4vcpu-8gb | 4 | 8GB | $48 | $0.064 | Small prod |

**Minimum Cluster:**
- 2 x s-2vcpu-4gb nodes = **~$48/month**
- Control plane: **FREE** (managed by DigitalOcean)
- Load Balancer: **$12/month** (only if you create one)

**Cost Examples:**
- 8-hour hackathon: 2 nodes @ $0.032/hr = **$0.51**
- Weekend project (48 hours): **$3.07**
- Full month development: **$48**

**⚠️ Billing Notes:**
- Charged hourly (minimum 1 hour)
- Rounds to nearest hour
- Check current prices: https://www.digitalocean.com/pricing/kubernetes

## Cluster Management

### List Clusters

**Context7-verified:**

```bash
doctl kubernetes cluster list
```

### Get Cluster Details

```bash
doctl kubernetes cluster get my-cluster
```

### Add Nodes

```bash
# Scale existing pool (Context7-verified)
doctl kubernetes cluster node-pool update my-cluster default-pool --count 3
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
```

## Common Workflows

### Hackathon Pattern

```bash
# Day 1: Create
.claude/skills/budget-k8s/scripts/create-doks-cluster.sh hack-cluster

# Deploy your app
kubectl apply -f app/

# Day 3: Teardown
.claude/skills/budget-k8s/scripts/delete-doks-cluster.sh hack-cluster

# Total cost: ~$2-3
```

### Learning Pattern

```bash
# Create for week
doctl kubernetes cluster create learning-cluster \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 2 \
  --wait

# Practice daily
kubectl apply -f tutorials/

# Delete on weekend
doctl kubernetes cluster delete learning-cluster --force

# Weekly cost: ~$12
```

## Troubleshooting

### "Insufficient quota" Error

**Problem:** Account has quota limits for new users.

**Solution:**
1. Verify account: https://cloud.digitalocean.com/account/billing
2. Contact support for quota increase
3. Try different region (nyc1, nyc3, sfo3)

### Kubeconfig Not Working

```bash
# Re-save kubeconfig (Context7-verified)
doctl kubernetes cluster kubeconfig save my-cluster

# Check context
kubectl config current-context

# Should see: do-{region}-{cluster-name}
```

### Cluster Creation Hangs

```bash
# Check status
doctl kubernetes cluster get my-cluster

# If stuck, delete and retry
doctl kubernetes cluster delete my-cluster --force
```

### Authentication Failures

```bash
# Re-authenticate
doctl auth init

# Verify
doctl account get
```

## Reference Files

- **`references/doctl-reference.md`**: Complete doctl command reference with all Context7-verified commands, flags, and examples

## Scripts

- **`scripts/create-doks-cluster.sh <name> <region> <size> <count>`**: Create cluster with cost warnings
- **`scripts/delete-doks-cluster.sh <name>`**: Delete cluster and stop charges

## Best Practices

1. **Always use --wait flag** when creating clusters (ensures it's ready)
2. **Set calendar reminder** to delete cluster (avoid forgotten charges)
3. **Use smallest size that works** (s-2vcpu-4gb sufficient for learning)
4. **Delete, don't stop** - paused clusters still charge for nodes
5. **Check billing daily** during learning: https://cloud.digitalocean.com/account/billing
6. **Use $200 credit wisely** - monitor usage in DO dashboard

## Additional Resources

- **Official Docs:** https://docs.digitalocean.com/products/kubernetes/
- **Pricing:** https://www.digitalocean.com/pricing/kubernetes
- **doctl Docs:** https://docs.digitalocean.com/reference/doctl/
- **Free Credit:** https://try.digitalocean.com/ (referral programs)
