#!/bin/bash
# Phase V.4 Todo Service Startup Script

set -e

# Colors for output
GREEN='\033[0.32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Phase V.4 Todo Service...${NC}"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}No .env file found. Copying from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}IMPORTANT: Update .env with your database credentials!${NC}"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if PostgreSQL is available
echo -e "${YELLOW}Checking PostgreSQL connection...${NC}"
python3 << EOF
import socket
import sys
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('${DB_HOST}', ${DB_PORT}))
    sock.close()
    if result != 0:
        print("❌ PostgreSQL is not accessible at ${DB_HOST}:${DB_PORT}")
        print("   Please start PostgreSQL or update DB_HOST in .env")
        sys.exit(1)
    else:
        print("✅ PostgreSQL is accessible")
except Exception as e:
    print(f"❌ Error checking PostgreSQL: {e}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}PostgreSQL check failed. See error above.${NC}"
    exit 1
fi

# Start the service
echo -e "${GREEN}Starting service on port ${SERVICE_PORT:-8001}...${NC}"
uvicorn main:app --reload --host ${SERVICE_HOST:-0.0.0.0} --port ${SERVICE_PORT:-8001}
