#!/bin/bash
# Create DigitalOcean Kubernetes cluster with cost-optimized settings
# All commands verified via Context7 from doctl documentation

set -e

CLUSTER_NAME=${1:-"hackathon-cluster"}
REGION=${2:-"nyc1"}
NODE_SIZE=${3:-"s-2vcpu-4gb"}  # $24/month per node
NODE_COUNT=${4:-2}

echo "🚀 Creating DOKS cluster: $CLUSTER_NAME"
echo "⚠️  COST WARNING: ~\$${NODE_COUNT}2/month (${NODE_COUNT} x ${NODE_SIZE} nodes)"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted"
    exit 1
fi

# Context7-verified command from doctl docs
echo "📦 Creating cluster (this takes 5-10 minutes)..."
doctl kubernetes cluster create "$CLUSTER_NAME" \
  --region "$REGION" \
  --size "$NODE_SIZE" \
  --count "$NODE_COUNT" \
  --wait

echo ""
echo "✅ Cluster created successfully!"
echo ""
echo "📋 Cluster details:"
doctl kubernetes cluster get "$CLUSTER_NAME"

echo ""
echo "🔧 Saving kubeconfig..."
doctl kubernetes cluster kubeconfig save "$CLUSTER_NAME"

echo ""
echo "✅ Setup complete! Verify with:"
echo "   kubectl get nodes"
echo ""
echo "⚠️  REMEMBER TO DELETE when done:"
echo "   .claude/skills/budget-k8s/scripts/delete-doks-cluster.sh $CLUSTER_NAME"
