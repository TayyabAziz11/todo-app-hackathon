#!/bin/bash
# Delete DigitalOcean Kubernetes cluster to stop charges
# All commands verified via Context7 from doctl documentation

set -e

CLUSTER_NAME=${1}

if [ -z "$CLUSTER_NAME" ]; then
    echo "Usage: $0 <cluster-name>"
    echo ""
    echo "Available clusters:"
    doctl kubernetes cluster list
    exit 1
fi

echo "🗑️  Deleting DOKS cluster: $CLUSTER_NAME"
echo "⚠️  This will PERMANENTLY delete the cluster and all resources!"
echo ""
read -p "Are you sure? (yes/N): " -r
echo
if [[ ! $REPLY == "yes" ]]; then
    echo "❌ Aborted"
    exit 1
fi

# Context7-verified: doctl kubernetes cluster delete
echo "🗑️  Deleting cluster..."
doctl kubernetes cluster delete "$CLUSTER_NAME" --force

echo ""
echo "🧹 Removing kubeconfig..."
doctl kubernetes cluster kubeconfig remove "$CLUSTER_NAME" || true

echo ""
echo "✅ Cluster deleted! Charges stopped."
echo ""
echo "Verify deletion:"
echo "   doctl kubernetes cluster list"
