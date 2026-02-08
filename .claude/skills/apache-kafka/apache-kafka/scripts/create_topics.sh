#!/bin/bash
# Create Kafka topics for event-driven Todo app
# Usage: ./create_topics.sh [namespace] [cluster-name]

set -e

NAMESPACE="${1:-kafka}"
CLUSTER_NAME="${2:-kafka-cluster}"

echo "=== Creating Kafka Topics ==="
echo "Namespace: $NAMESPACE"
echo "Cluster: $CLUSTER_NAME"
echo ""

# Determine replication factor based on cluster size
REPLICAS=$(kubectl get kafka "$CLUSTER_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.kafka.replicas}' 2>/dev/null || echo "1")
if [ "$REPLICAS" -eq 1 ]; then
    REPLICATION_FACTOR=1
    MIN_INSYNC_REPLICAS=1
else
    REPLICATION_FACTOR=3
    MIN_INSYNC_REPLICAS=2
fi

echo "Detected $REPLICAS broker(s), using replication factor $REPLICATION_FACTOR"
echo ""

# Task lifecycle events topic
cat <<EOF | kubectl apply -n "$NAMESPACE" -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  labels:
    strimzi.io/cluster: $CLUSTER_NAME
spec:
  partitions: 6
  replicas: $REPLICATION_FACTOR
  config:
    retention.ms: 604800000
    min.insync.replicas: $MIN_INSYNC_REPLICAS
    compression.type: producer
    cleanup.policy: delete
EOF

echo "✓ Created topic: task-events (6 partitions, ${REPLICATION_FACTOR}x replication)"

# Reminder notifications topic
cat <<EOF | kubectl apply -n "$NAMESPACE" -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-reminders
  labels:
    strimzi.io/cluster: $CLUSTER_NAME
spec:
  partitions: 3
  replicas: $REPLICATION_FACTOR
  config:
    retention.ms: 2592000000
    min.insync.replicas: $MIN_INSYNC_REPLICAS
    compression.type: producer
    cleanup.policy: delete
EOF

echo "✓ Created topic: task-reminders (3 partitions, ${REPLICATION_FACTOR}x replication)"

# Audit log topic (long retention, compacted)
cat <<EOF | kubectl apply -n "$NAMESPACE" -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-audit
  labels:
    strimzi.io/cluster: $CLUSTER_NAME
spec:
  partitions: 3
  replicas: $REPLICATION_FACTOR
  config:
    retention.ms: 31536000000
    min.insync.replicas: $MIN_INSYNC_REPLICAS
    compression.type: producer
    cleanup.policy: compact
EOF

echo "✓ Created topic: task-audit (3 partitions, ${REPLICATION_FACTOR}x replication, compacted)"

# Real-time updates topic
cat <<EOF | kubectl apply -n "$NAMESPACE" -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  labels:
    strimzi.io/cluster: $CLUSTER_NAME
spec:
  partitions: 3
  replicas: $REPLICATION_FACTOR
  config:
    retention.ms: 86400000
    min.insync.replicas: $MIN_INSYNC_REPLICAS
    compression.type: producer
    cleanup.policy: delete
EOF

echo "✓ Created topic: task-updates (3 partitions, ${REPLICATION_FACTOR}x replication)"

echo ""
echo "=== Topics created successfully ==="
echo ""
echo "List topics:"
echo "  kubectl get kafkatopics -n $NAMESPACE"
echo ""
echo "Describe a topic:"
echo "  kubectl describe kafkatopic task-events -n $NAMESPACE"
