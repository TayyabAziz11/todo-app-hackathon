# Kafka Core Concepts

> **Source**: Apache Kafka Official Documentation (kafka.apache.org)

## Table of Contents
- [Events and Records](#events-and-records)
- [Topics and Logs](#topics-and-logs)
- [Partitions](#partitions)
- [Producers](#producers)
- [Consumers and Consumer Groups](#consumers-and-consumer-groups)
- [Offsets](#offsets)
- [Replication and Durability](#replication-and-durability)
- [Brokers and Clusters](#brokers-and-clusters)

## Events and Records

An **event** represents something that happened. In Kafka, events are also called **records** or **messages**.

**Event structure**:
- **Key**: Used for partitioning (can be null)
- **Value**: The actual event payload (can be null)
- **Timestamp**: Event time or ingestion time
- **Headers** (optional): Metadata key-value pairs

Example event: User completed a task
```json
{
  "key": "user-123",
  "value": {
    "event_type": "task.completed",
    "task_id": "task-456",
    "user_id": "user-123",
    "completed_at": "2026-02-05T10:30:00Z"
  },
  "timestamp": 1738753800000,
  "headers": {
    "correlation_id": "req-789",
    "source": "todo-backend"
  }
}
```

## Topics and Logs

A **topic** is similar to a folder in a filesystem, and events are the files in that folder.

**Key characteristics**:
- Topics are **append-only logs** — events are added to the end
- Events are **immutable** once written
- Topics support **multi-producer** (many apps can write)
- Topics support **multi-subscriber** (many apps can read)
- Events are **not deleted after consumption** (unlike traditional queues)
- Retention is **time-based or size-based** (configurable per topic)

**Topic naming for domain events**:
```
task-events          # All task lifecycle events
task-reminders       # Reminder notifications
task-audit           # Audit trail / event sourcing
task-updates         # Real-time sync events
```

## Partitions

Topics are divided into **partitions** — the fundamental unit of parallelism.

**Partition characteristics**:
- Each partition is an **ordered, immutable log**
- Partitions can reside on **different brokers** (distributed)
- Events with **the same key go to the same partition**
- Ordering is **guaranteed within a partition**, not across partitions
- Partition count determines **max consumer parallelism**

**Partitioning strategy**:
```
Event Key → Hash(Key) % num_partitions → Partition Assignment

Example:
- Task event with key="user-123" → always goes to same partition
- Guarantees ordering for all events from user-123
```

**Choosing partition count**:
- Start with 3-6 partitions for small topics
- Use `max(expected_throughput_MB/s / 10MB/s, max_consumers)` for production
- More partitions = more parallelism but higher overhead
- Cannot decrease partition count (only increase)

## Producers

**Producers** are client applications that publish (write) events to Kafka.

**Producer behavior**:
- Send events to specific topics
- Optionally specify partition key for ordering
- Can configure acknowledgment level (acks)
- Support batching and compression
- Idempotent by default in modern Kafka

**Acknowledgment levels** (`acks`):
- `acks=0`: Fire-and-forget (no confirmation, fastest, data loss possible)
- `acks=1`: Leader acknowledges (moderate durability)
- `acks=all`: All in-sync replicas acknowledge (strongest durability, slowest)

**Production setting**: `acks=all` for critical domain events

## Consumers and Consumer Groups

**Consumers** are applications that subscribe to topics and process events.

**Consumer Group**:
- A set of consumers working together to consume a topic
- Each partition is assigned to **exactly one consumer** in the group
- Enables **horizontal scaling** — add more consumers to handle load
- Messages are **load-balanced** across consumers in the group

**Partition assignment**:
```
Topic: task-events (3 partitions)
Consumer Group: recurring-task-service

If 1 consumer:  C1 reads [P0, P1, P2]
If 2 consumers: C1 reads [P0, P1], C2 reads [P2]
If 3 consumers: C1 reads [P0], C2 reads [P1], C3 reads [P2]
If 4 consumers: C1 reads [P0], C2 reads [P1], C3 reads [P2], C4 idle
```

**Multiple consumer groups**:
```
task-events topic
├── recurring-task-service (consumer group 1) → processes recurring tasks
├── audit-service (consumer group 2) → writes to audit log
└── notification-service (consumer group 3) → sends notifications

Each group receives ALL events independently.
```

## Offsets

An **offset** is a unique integer that marks the position of an event within a partition.

**Offset characteristics**:
- Offsets are **sequential** within a partition (0, 1, 2, ...)
- Offsets are **partition-specific** (partition 0 offset 5 ≠ partition 1 offset 5)
- Offsets are **immutable** (never change once assigned)

**Committed offset**:
- The last offset a consumer has **successfully processed**
- Stored in internal topic `__consumer_offsets`
- Enables consumers to **stop and restart** without losing position
- Supports **at-least-once** delivery semantics

**Offset commit strategies**:
- **Auto-commit** (default): Commits every 5s automatically
- **Manual commit**: Commit after processing completes
- **Manual commit async**: Non-blocking commit

**Production recommendation**: Manual commit after processing to avoid message loss.

## Replication and Durability

**Replication** ensures fault tolerance by copying partitions across multiple brokers.

**Replication factor**:
- Number of copies of each partition
- **Common production setting**: replication factor of 3
- Example: 3 copies = 1 leader + 2 followers

**In-Sync Replicas (ISR)**:
- Replicas that are fully caught up with the leader
- Only ISR replicas count for `acks=all` acknowledgments
- If leader fails, new leader elected from ISR

**Durability guarantees**:
```
Producer: acks=all + min.insync.replicas=2
→ Ensures at least 2 replicas acknowledge before success
→ Tolerates 1 broker failure without data loss
```

**Production configuration**:
```yaml
replication-factor: 3
min.insync.replicas: 2
acks: all
```

## Brokers and Clusters

**Broker**: A single Kafka server that stores data and serves clients.

**Cluster**: A group of brokers working together.

**Broker responsibilities**:
- Store partition replicas
- Handle producer writes
- Handle consumer reads
- Participate in partition rebalancing

**Controller** (one per cluster):
- Manages broker membership
- Handles partition leadership elections
- Coordinates cluster metadata

**KRaft mode** (Kafka 4.0+):
- **No ZooKeeper dependency** (removed in Kafka 4.0)
- Uses **Kafka Raft metadata mode** for consensus
- Simpler architecture and faster metadata propagation

**Strimzi default**: Uses KRaft mode for new deployments.
