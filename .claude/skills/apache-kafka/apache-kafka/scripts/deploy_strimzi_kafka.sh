#!/bin/bash
# Deploy Strimzi Kafka cluster to Kubernetes
# Usage: ./deploy_strimzi_kafka.sh [namespace] [cluster-name] [replicas]

set -e

NAMESPACE="${1:-kafka}"
CLUSTER_NAME="${2:-kafka-cluster}"
REPLICAS="${3:-1}"

echo "=== Deploying Strimzi Kafka Cluster ==="
echo "Namespace: $NAMESPACE"
echo "Cluster Name: $CLUSTER_NAME"
echo "Replicas: $REPLICAS"

# Create namespace if it doesn't exist
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo "Creating namespace: $NAMESPACE"
    kubectl create namespace "$NAMESPACE"
else
    echo "Namespace $NAMESPACE already exists"
fi

# Install Strimzi operator if not already installed
if ! kubectl get deployment strimzi-cluster-operator -n "$NAMESPACE" &> /dev/null; then
    echo "Installing Strimzi Cluster Operator..."
    kubectl create -f "https://strimzi.io/install/latest?namespace=$NAMESPACE" -n "$NAMESPACE"

    echo "Waiting for operator to be ready..."
    kubectl wait deployment/strimzi-cluster-operator \
        --for=condition=Available \
        --timeout=300s \
        -n "$NAMESPACE"
else
    echo "Strimzi Cluster Operator already installed"
fi

# Determine storage and replication based on replicas
if [ "$REPLICAS" -eq 1 ]; then
    STORAGE_TYPE="ephemeral"
    REPLICATION_FACTOR=1
    MIN_INSYNC_REPLICAS=1
    echo "Development mode: ephemeral storage, replication factor 1"
else
    STORAGE_TYPE="persistent-claim"
    REPLICATION_FACTOR=3
    MIN_INSYNC_REPLICAS=2
    echo "Production mode: persistent storage, replication factor 3"
fi

# Create Kafka cluster CR
cat <<EOF | kubectl apply -n "$NAMESPACE" -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: $CLUSTER_NAME
spec:
  kafka:
    version: 3.9.0
    replicas: $REPLICAS
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: $REPLICATION_FACTOR
      transaction.state.log.replication.factor: $REPLICATION_FACTOR
      transaction.state.log.min.isr: $MIN_INSYNC_REPLICAS
      default.replication.factor: $REPLICATION_FACTOR
      min.insync.replicas: $MIN_INSYNC_REPLICAS
      log.retention.hours: 168
      log.segment.bytes: 1073741824
      num.network.threads: 3
      num.io.threads: 8
    storage:
      type: $STORAGE_TYPE
$([ "$STORAGE_TYPE" = "persistent-claim" ] && cat <<STORAGE
      size: 100Gi
      deleteClaim: false
STORAGE
)
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF

echo ""
echo "=== Kafka cluster deployment started ==="
echo ""
echo "Monitor deployment:"
echo "  kubectl get kafka $CLUSTER_NAME -n $NAMESPACE -w"
echo ""
echo "Check broker pods:"
echo "  kubectl get pods -n $NAMESPACE -l strimzi.io/name=${CLUSTER_NAME}-kafka"
echo ""
echo "Service endpoint (internal):"
echo "  ${CLUSTER_NAME}-kafka-bootstrap.${NAMESPACE}:9092 (plain)"
echo "  ${CLUSTER_NAME}-kafka-bootstrap.${NAMESPACE}:9093 (tls)"
echo ""
echo "Full service endpoint:"
echo "  ${CLUSTER_NAME}-kafka-bootstrap.${NAMESPACE}.svc.cluster.local:9092"
