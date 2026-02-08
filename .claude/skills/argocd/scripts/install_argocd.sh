#!/bin/bash
# Install ArgoCD on Kubernetes with different configurations

set -e

MODE=${1:-dev}  # dev or ha

echo "🚀 Installing ArgoCD (mode: $MODE)..."

# Check kubectl
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ kubectl not configured or cluster not accessible"
    exit 1
fi

# Create namespace
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

if [ "$MODE" == "ha" ]; then
    echo "📦 Installing ArgoCD in High Availability mode..."
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/ha/install.yaml
else
    echo "📦 Installing ArgoCD in development mode..."
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
fi

# Wait for pods
echo "⏳ Waiting for ArgoCD pods to be ready..."
kubectl wait --for=condition=Ready pods --all -n argocd --timeout=300s

# Get initial admin password
echo ""
echo "✅ ArgoCD installed successfully!"
echo ""
echo "Initial admin password:"
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
echo ""
echo ""
echo "Access ArgoCD:"
echo "  kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "  Open: https://localhost:8080"
echo "  Username: admin"
