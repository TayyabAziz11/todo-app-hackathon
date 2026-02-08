# Event-Driven Architecture Patterns with Kafka

> **Sources**: Apache Kafka Documentation, Redpanda Architecture Guide, Industry Best Practices

## Table of Contents
- [Event Design Principles](#event-design-principles)
- [Domain Event Patterns](#domain-event-patterns)
- [Idempotency Strategies](#idempotency-strategies)
- [Schema Evolution](#schema-evolution)
- [Error Handling Patterns](#error-handling-patterns)
- [Observability](#observability)

## Event Design Principles

### Event Structure

**CloudEvents specification** (recommended for Dapr):
```json
{
  "specversion": "1.0",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "source": "todo-backend",
  "type": "com.todoapp.task.completed",
  "datacontenttype": "application/json",
  "time": "2026-02-05T10:30:00Z",
  "subject": "task/task-456",
  "data": {
    "task_id": "task-456",
    "user_id": "user-123",
    "completed_at": "2026-02-05T10:30:00Z",
    "previous_status": "in_progress"
  }
}
```

**Event naming conventions**:
```
Pattern: <domain>.<entity>.<action>

Examples:
- com.todoapp.task.created
- com.todoapp.task.updated
- com.todoapp.task.completed
- com.todoapp.task.deleted
- com.todoapp.reminder.scheduled
- com.todoapp.user.registered
```

**Event versioning**:
```json
{
  "type": "com.todoapp.task.completed.v2",
  "data_schema": "https://schemas.todoapp.com/task/completed/v2.json",
  "data": { ... }
}
```

### Event vs. Command

**Event** (past tense, fact):
- `task.completed` - Something that happened
- Published by the entity that owns the state
- Multiple consumers can react independently
- Immutable historical record

**Command** (imperative, request):
- `complete.task` - Request for action
- Sent to a specific handler
- Single consumer processes and may reject
- Not stored as historical record

**Rule**: Kafka is ideal for **events**, not commands. Use request-response patterns for commands.

## Domain Event Patterns

### Pattern 1: Task Lifecycle Events

**Single topic for all task events**:
```
Topic: task-events
Partition key: user_id (ensures ordering per user)

Events:
- task.created
- task.updated
- task.completed
- task.deleted
```

**Producer** (FastAPI backend):
```python
from dapr.clients import DaprClient
import json
from datetime import datetime, UTC

def publish_task_completed(user_id: str, task_id: str):
    event = {
        "specversion": "1.0",
        "id": str(uuid.uuid4()),
        "source": "todo-backend",
        "type": "com.todoapp.task.completed",
        "datacontenttype": "application/json",
        "time": datetime.now(UTC).isoformat(),
        "subject": f"task/{task_id}",
        "data": {
            "task_id": task_id,
            "user_id": user_id,
            "completed_at": datetime.now(UTC).isoformat()
        }
    }

    with DaprClient() as client:
        client.publish_event(
            pubsub_name="kafka-pubsub",
            topic_name="task-events",
            data=json.dumps(event["data"]),
            data_content_type="application/json",
            metadata={
                "rawPayload": "true",  # Send as-is
                "partitionKey": user_id  # Route to same partition
            }
        )
```

**Consumer** (Recurring Task Service):
```python
from flask import Flask, request, jsonify
from cloudevents.http import from_http

app = Flask(__name__)

@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    return jsonify([{
        'pubsubname': 'kafka-pubsub',
        'topic': 'task-events',
        'route': '/task-events'
    }])

@app.route('/task-events', methods=['POST'])
def handle_task_event():
    event = from_http(request.headers, request.get_data())

    if event['type'] == 'com.todoapp.task.completed':
        task_data = event.data

        # Process recurring task
        if task_data.get('is_recurring'):
            create_next_occurrence(task_data)

    return jsonify({'status': 'SUCCESS'})
```

### Pattern 2: Event Sourcing Lite

**Store all events for audit trail**:
```
Topic: task-audit
Partition key: task_id
Cleanup policy: compact (keep latest per task)
Retention: 365 days
```

**Audit service** rebuilds task history:
```python
@app.route('/task-events', methods=['POST'])
def audit_task_event():
    event = from_http(request.headers, request.get_data())

    # Store in audit database
    audit_entry = {
        'event_id': event['id'],
        'event_type': event['type'],
        'task_id': event.data['task_id'],
        'user_id': event.data['user_id'],
        'timestamp': event['time'],
        'payload': event.data
    }

    db.audit_log.insert(audit_entry)

    return jsonify({'status': 'SUCCESS'})
```

### Pattern 3: Real-Time Client Sync

**WebSocket/SSE service consumes task updates**:
```
Topic: task-updates
Partition key: user_id

Event types:
- task.created
- task.updated
- task.deleted
```

**WebSocket broadcaster**:
```python
connected_clients = {}  # user_id → websocket

@app.route('/task-events', methods=['POST'])
async def broadcast_update():
    event = from_http(request.headers, request.get_data())
    user_id = event.data['user_id']

    # Broadcast to connected clients
    if user_id in connected_clients:
        await connected_clients[user_id].send_json({
            'type': event['type'],
            'data': event.data
        })

    return jsonify({'status': 'SUCCESS'})
```

## Idempotency Strategies

**Why idempotency matters**:
- Kafka provides **at-least-once** delivery
- Network failures cause retries
- Same event may be delivered multiple times
- Processing must be **idempotent** (safe to retry)

### Strategy 1: Event ID Deduplication

**Store processed event IDs**:
```python
from redis import Redis

redis_client = Redis(host='redis', port=6379)
PROCESSED_TTL = 86400  # 24 hours

@app.route('/task-events', methods=['POST'])
def handle_task_event():
    event = from_http(request.headers, request.get_data())
    event_id = event['id']

    # Check if already processed
    if redis_client.exists(f"processed:{event_id}"):
        return jsonify({'status': 'SUCCESS'})  # Duplicate, skip

    # Process event
    process_task_event(event.data)

    # Mark as processed
    redis_client.setex(f"processed:{event_id}", PROCESSED_TTL, "1")

    return jsonify({'status': 'SUCCESS'})
```

### Strategy 2: Database Constraint

**Use unique constraints to prevent duplicates**:
```python
from sqlalchemy.exc import IntegrityError

@app.route('/task-events', methods=['POST'])
def handle_task_event():
    event = from_http(request.headers, request.get_data())

    try:
        # Database has unique constraint on event_id
        db.execute("""
            INSERT INTO processed_events (event_id, task_id, processed_at)
            VALUES (:event_id, :task_id, NOW())
        """, {
            'event_id': event['id'],
            'task_id': event.data['task_id']
        })

        # Process event
        process_task_event(event.data)

    except IntegrityError:
        # Duplicate event, already processed
        pass

    return jsonify({'status': 'SUCCESS'})
```

### Strategy 3: Idempotent Operations

**Design operations to be naturally idempotent**:
```python
# NOT idempotent (increments counter each time)
def mark_complete(task_id):
    db.execute("UPDATE tasks SET completion_count = completion_count + 1 WHERE id = :id", {'id': task_id})

# Idempotent (sets value directly)
def mark_complete(task_id, completed_at):
    db.execute("""
        UPDATE tasks
        SET status = 'completed',
            completed_at = :completed_at
        WHERE id = :id AND status != 'completed'
    """, {'id': task_id, 'completed_at': completed_at})
```

## Schema Evolution

**Versioning strategy**:

### Approach 1: Event Type Versioning

```python
# v1 event
{
  "type": "com.todoapp.task.created.v1",
  "data": {
    "task_id": "task-123",
    "title": "Buy groceries"
  }
}

# v2 event (added due_date)
{
  "type": "com.todoapp.task.created.v2",
  "data": {
    "task_id": "task-123",
    "title": "Buy groceries",
    "due_date": "2026-02-10T12:00:00Z"
  }
}
```

**Consumer handles both versions**:
```python
@app.route('/task-events', methods=['POST'])
def handle_task_event():
    event = from_http(request.headers, request.get_data())

    if event['type'] == 'com.todoapp.task.created.v1':
        task_data = {
            'task_id': event.data['task_id'],
            'title': event.data['title'],
            'due_date': None  # Default for v1
        }
    elif event['type'] == 'com.todoapp.task.created.v2':
        task_data = event.data

    create_task(task_data)
    return jsonify({'status': 'SUCCESS'})
```

### Approach 2: Data Schema Field

```python
{
  "type": "com.todoapp.task.created",
  "dataschema": "https://schemas.todoapp.com/task/created/v2.json",
  "data": { ... }
}
```

**Schema registry** (future extension):
- Store JSON schemas centrally
- Validate events against schemas
- Enforce backward compatibility

## Error Handling Patterns

### Pattern 1: Retry with Exponential Backoff

**Dapr built-in retry**:
```python
@app.route('/task-events', methods=['POST'])
def handle_task_event():
    event = from_http(request.headers, request.get_data())

    try:
        process_task_event(event.data)
        return jsonify({'status': 'SUCCESS'})

    except TransientError as e:
        # Dapr will retry
        return jsonify({'status': 'RETRY'}), 500

    except PermanentError as e:
        # Log and skip (poison message)
        logger.error(f"Permanent error: {e}")
        return jsonify({'status': 'DROP'})
```

### Pattern 2: Dead Letter Queue

**Route failed events to DLQ topic**:
```python
@app.route('/task-events', methods=['POST'])
def handle_task_event():
    event = from_http(request.headers, request.get_data())

    try:
        process_task_event(event.data)
        return jsonify({'status': 'SUCCESS'})

    except Exception as e:
        # Publish to dead letter queue
        publish_to_dlq(event, str(e))
        return jsonify({'status': 'DROP'})

def publish_to_dlq(original_event, error_message):
    with DaprClient() as client:
        client.publish_event(
            pubsub_name="kafka-pubsub",
            topic_name="task-events-dlq",
            data=json.dumps({
                'original_event': original_event.data,
                'error': error_message,
                'failed_at': datetime.now(UTC).isoformat()
            })
        )
```

### Pattern 3: Circuit Breaker

**Prevent cascading failures**:
```python
from pybreaker import CircuitBreaker

circuit_breaker = CircuitBreaker(
    fail_max=5,  # Open after 5 failures
    timeout_duration=60  # Reset after 60s
)

@app.route('/task-events', methods=['POST'])
def handle_task_event():
    event = from_http(request.headers, request.get_data())

    try:
        circuit_breaker.call(process_task_event, event.data)
        return jsonify({'status': 'SUCCESS'})

    except CircuitBreakerError:
        # Service is down, retry later
        return jsonify({'status': 'RETRY'}), 503
```

## Observability

**Metrics to track**:
- Consumer lag (events waiting to be processed)
- Processing latency (time from publish to consume)
- Error rate (failures / total events)
- Throughput (events/second)

**Prometheus metrics** (via Dapr):
```python
from prometheus_client import Counter, Histogram

events_processed = Counter('task_events_processed_total', 'Total events processed', ['event_type'])
processing_duration = Histogram('task_event_processing_duration_seconds', 'Event processing duration')

@app.route('/task-events', methods=['POST'])
def handle_task_event():
    event = from_http(request.headers, request.get_data())

    with processing_duration.time():
        process_task_event(event.data)
        events_processed.labels(event_type=event['type']).inc()

    return jsonify({'status': 'SUCCESS'})
```

**Distributed tracing** (OpenTelemetry + Dapr):
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@app.route('/task-events', methods=['POST'])
def handle_task_event():
    event = from_http(request.headers, request.get_data())

    with tracer.start_as_current_span("process_task_event") as span:
        span.set_attribute("event.type", event['type'])
        span.set_attribute("event.id", event['id'])

        process_task_event(event.data)

    return jsonify({'status': 'SUCCESS'})
```

**Logging best practices**:
```python
import structlog

logger = structlog.get_logger()

@app.route('/task-events', methods=['POST'])
def handle_task_event():
    event = from_http(request.headers, request.get_data())

    logger.info(
        "event_received",
        event_id=event['id'],
        event_type=event['type'],
        task_id=event.data.get('task_id'),
        user_id=event.data.get('user_id')
    )

    process_task_event(event.data)

    logger.info(
        "event_processed",
        event_id=event['id'],
        event_type=event['type']
    )

    return jsonify({'status': 'SUCCESS'})
```
