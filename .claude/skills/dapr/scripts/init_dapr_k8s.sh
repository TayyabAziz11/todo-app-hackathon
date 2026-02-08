#!/bin/bash
# Initialize Dapr on Kubernetes with production-ready settings

set -e

MODE=${1:-dev}  # dev or prod

echo "🚀 Initializing Dapr on Kubernetes (mode: $MODE)..."

# Check if Dapr CLI is installed
if ! command -v dapr &> /dev/null; then
    echo "❌ Dapr CLI not found. Please install it first."
    exit 1
fi

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ kubectl not configured or cluster not accessible."
    exit 1
fi

if [ "$MODE" == "prod" ]; then
    echo "📦 Installing Dapr in production mode (High Availability)..."

    # Add Dapr Helm repo
    helm repo add dapr https://dapr.github.io/helm-charts/
    helm repo update

    # Install with HA enabled
    helm upgrade --install dapr dapr/dapr \
        --version=1.15 \
        --namespace dapr-system \
        --create-namespace \
        --set global.ha.enabled=true \
        --set global.mtls.enabled=true \
        --wait

    echo "✅ Dapr installed in HA mode with mTLS enabled"
else
    echo "📦 Installing Dapr in development mode..."
    dapr init -k --dev
    echo "✅ Dapr installed with Redis and Zipkin for development"
fi

# Verify installation
echo "🔍 Verifying Dapr installation..."
dapr status -k

echo ""
echo "✅ Dapr Kubernetes environment ready!"
echo ""
echo "Next steps:"
echo "  1. Deploy your app with Dapr annotations"
echo "  2. Configure components in your namespace"
echo "  3. View dashboard: dapr dashboard -k"
