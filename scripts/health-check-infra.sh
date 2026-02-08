#!/bin/bash
# Phase V.0 Infrastructure Health Check Script
# Validates: Minikube, Dapr, PostgreSQL, Kafka

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "Phase V.0 Infrastructure Health Check"
echo "========================================="
echo ""

# Check 1: Minikube Status
echo -n "🔍 Checking Minikube status... "
if minikube status | grep -q "Running"; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

# Check 2: kubectl connectivity
echo -n "🔍 Checking kubectl connectivity... "
if kubectl cluster-info >/dev/null 2>&1; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

# Check 3: Dapr Control Plane
echo -n "🔍 Checking Dapr control plane... "
DAPR_PODS=$(kubectl get pods -n dapr-system -o jsonpath='{range .items[*]}{.status.phase}{"\n"}{end}' | grep -c "Running" || echo "0")
if [ "$DAPR_PODS" -ge 3 ]; then
    echo -e "${GREEN}✓ HEALTHY (${DAPR_PODS} pods running)${NC}"
else
    echo -e "${RED}✗ FAILED (${DAPR_PODS} pods running, expected >= 3)${NC}"
    exit 1
fi

# Check 4: PostgreSQL
echo -n "🔍 Checking PostgreSQL... "
PG_READY=$(kubectl get pods -n todo-app-dev -l app.kubernetes.io/name=postgresql -o jsonpath='{.items[0].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "False")
if [ "$PG_READY" == "True" ]; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

# Check 5: Kafka
echo -n "🔍 Checking Kafka cluster... "
KAFKA_READY=$(kubectl get kafka todo-kafka -n todo-app-dev -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "False")
if [ "$KAFKA_READY" == "True" ]; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

# Check 6: Kafka Broker Pod
echo -n "🔍 Checking Kafka broker pod... "
KAFKA_POD=$(kubectl get pods -n todo-app-dev -l strimzi.io/cluster=todo-kafka,strimzi.io/kind=Kafka -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "Unknown")
if [ "$KAFKA_POD" == "Running" ]; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${RED}✗ FAILED (Status: ${KAFKA_POD})${NC}"
    exit 1
fi

# Check 7: Namespace
echo -n "🔍 Checking todo-app-dev namespace... "
if kubectl get namespace todo-app-dev >/dev/null 2>&1; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

# Check 8: Secrets
echo -n "🔍 Checking Kubernetes secrets... "
SECRETS=$(kubectl get secrets -n todo-app-dev | grep -E "(postgres-credentials|jwt-signing-key|openai-api-key)" | wc -l)
if [ "$SECRETS" -eq 3 ]; then
    echo -e "${GREEN}✓ HEALTHY (3/3 secrets present)${NC}"
else
    echo -e "${RED}✗ FAILED (${SECRETS}/3 secrets present)${NC}"
    exit 1
fi

echo ""
echo "========================================="
echo -e "${GREEN}✅ ALL INFRASTRUCTURE CHECKS PASSED${NC}"
echo "========================================="
echo ""
echo "Summary:"
echo "  ✓ Minikube cluster: Running"
echo "  ✓ Dapr control plane: ${DAPR_PODS} pods"
echo "  ✓ PostgreSQL: Ready"
echo "  ✓ Kafka: Ready"
echo "  ✓ Namespace: Active"
echo "  ✓ Secrets: 3/3 configured"
echo ""
echo "Phase V.0 infrastructure is ready for service deployment."
