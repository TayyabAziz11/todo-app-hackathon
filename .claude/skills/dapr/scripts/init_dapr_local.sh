#!/bin/bash
# Initialize Dapr for local development with default components

set -e

echo "🚀 Initializing Dapr for local development..."

# Check if Dapr CLI is installed
if ! command -v dapr &> /dev/null; then
    echo "❌ Dapr CLI not found. Please install it first:"
    echo "   wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash"
    exit 1
fi

# Initialize Dapr runtime
echo "📦 Installing Dapr runtime..."
dapr init

# Verify installation
echo "✅ Verifying installation..."
dapr --version

echo ""
echo "✅ Dapr local environment ready!"
echo ""
echo "Default components installed:"
echo "  - State store: Redis (localhost:6379)"
echo "  - Pub/sub: Redis (localhost:6379)"
echo "  - Zipkin: localhost:9411"
echo ""
echo "Next steps:"
echo "  1. Run your app: dapr run --app-id myapp --app-port 5000 -- python app.py"
echo "  2. View dashboard: dapr dashboard"
echo "  3. Check components: ls ~/.dapr/components/"
