# Phase V: Events Specification

**Feature Branch**: `005-name-phase5-cloud`
**Created**: 2026-02-06
**Status**: Draft

## Overview

This document defines all event schemas, topics, and event-driven workflows for Phase V. All events follow the [CloudEvents v1.0 specification](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md).

## Event Design Principles

1. **CloudEvents Compliance**: All events MUST include required CloudEvents attributes
2. **Versioning**: Event types include version (e.g., `com.todoapp.todo.created.v1`)
3. **Immutability**: Events are immutable once published
4. **Idempotency**: Consumers MUST handle duplicate events gracefully
5. **Payload Size**: Keep payloads < 1MB (use references for large data)
6. **Schema Evolution**: Backward-compatible changes only (expand-contract pattern)

## CloudEvents Envelope

All events follow this structure:

```json
{
  "specversion": "1.0",
  "type": "com.todoapp.todo.created.v1",
  "source": "//todoapp/services/todo-service",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "time": "2026-02-06T10:30:00Z",
  "datacontenttype": "application/json",
  "subject": "todo/12345",
  "data": {
    // Event-specific payload
  }
}
```

**Required Attributes:**
- `specversion`: CloudEvents version (always "1.0")
- `type`: Event type (hierarchical, versioned)
- `source`: URI identifying the event producer
- `id`: Unique event ID (UUID v4)
- `time`: Timestamp when event occurred (ISO 8601)

**Optional Attributes:**
- `datacontenttype`: MIME type of data (usually "application/json")
- `subject`: Entity this event is about (for filtering)

## Kafka Topics

### Topic Naming Convention

Format: `{domain}.{entity}.{action}.{version}`

Examples:
- `com.todoapp.todo.created.v1`
- `com.todoapp.user.deleted.v1`

### Topic Configuration

| Topic | Partitions | Replication | Retention | Compaction |
|-------|-----------|-------------|-----------|------------|
| todo.created | 3 | 2 | 7 days | No |
| todo.updated | 3 | 2 | 7 days | Yes (by todo_id) |
| todo.deleted | 3 | 2 | 7 days | No |
| todo.completed | 3 | 2 | 7 days | No |
| todo.reminder.due | 2 | 2 | 1 day | No |
| todo.series.* | 2 | 2 | 7 days | No |
| user.created | 1 | 2 | 7 days | No |
| user.updated | 1 | 2 | 7 days | Yes (by user_id) |
| user.deleted | 1 | 2 | 7 days | No |
| chat.message.sent | 3 | 2 | 3 days | No |
| notification.sent | 2 | 2 | 3 days | No |
| notification.failed | 2 | 2 | 7 days | No |

**Partitioning Strategy:**
- **Todo events**: Partition by `todo_id` (ensures per-todo ordering)
- **User events**: Partition by `user_id` (ensures per-user ordering)
- **Chat events**: Partition by `conversation_id`
- **Notification events**: Partition by `user_id`

**Compaction:**
- Enabled for `updated` topics to keep only latest state
- Disabled for `created`/`deleted` topics (need full history)

## Event Catalog

### Todo Domain Events

#### 1. todo.created.v1

**Description**: Published when a new todo is created.

**Producer**: Todo Service

**Consumers**: Audit Service, Analytics Service, Chat Service (context update)

**Schema**:
```json
{
  "type": "com.todoapp.todo.created.v1",
  "source": "//todoapp/services/todo-service",
  "subject": "todo/12345",
  "data": {
    "todo_id": "12345",
    "user_id": "user-456",
    "title": "Prepare Phase V documentation",
    "description": "Write comprehensive specs for all features",
    "status": "pending",
    "priority": "high",
    "tags": ["work", "documentation"],
    "due_date": "2026-02-15T17:00:00Z",
    "recurrence_rule": null,
    "parent_series_id": null,
    "created_at": "2026-02-06T10:30:00Z",
    "created_by": "user-456"
  }
}
```

**Validation Rules**:
- `todo_id`: UUID v4, required
- `user_id`: UUID v4, required
- `title`: String (1-200 chars), required
- `description`: String (0-5000 chars), optional
- `status`: Enum ["pending", "in_progress", "completed"], required
- `priority`: Enum ["low", "medium", "high", "urgent"], required
- `tags`: Array of strings (max 10), optional
- `due_date`: ISO 8601 timestamp, optional
- `recurrence_rule`: iCalendar RRULE string, optional

**Idempotency**: Consumer stores `todo_id` in processed events table (7-day window).

---

#### 2. todo.updated.v1

**Description**: Published when a todo is modified (title, description, status, priority, tags, due_date).

**Producer**: Todo Service

**Consumers**: Audit Service, Analytics Service, Chat Service, Notification Service (cancel reminders if deleted)

**Schema**:
```json
{
  "type": "com.todoapp.todo.updated.v1",
  "source": "//todoapp/services/todo-service",
  "subject": "todo/12345",
  "data": {
    "todo_id": "12345",
    "user_id": "user-456",
    "changes": {
      "priority": {
        "old": "medium",
        "new": "high"
      },
      "due_date": {
        "old": "2026-02-20T17:00:00Z",
        "new": "2026-02-15T17:00:00Z"
      }
    },
    "updated_at": "2026-02-06T11:00:00Z",
    "updated_by": "user-456",
    "version": 2
  }
}
```

**Validation Rules**:
- `todo_id`: UUID v4, required
- `changes`: Object with field-level deltas, required (at least one field changed)
- `version`: Integer (optimistic locking version), required

**Idempotency**: Consumer compares `version` field; ignore if version ≤ last processed.

---

#### 3. todo.completed.v1

**Description**: Published when a todo is marked as completed.

**Producer**: Todo Service

**Consumers**: Audit Service, Analytics Service, Notification Service (generate next recurring instance)

**Schema**:
```json
{
  "type": "com.todoapp.todo.completed.v1",
  "source": "//todoapp/services/todo-service",
  "subject": "todo/12345",
  "data": {
    "todo_id": "12345",
    "user_id": "user-456",
    "completed_at": "2026-02-06T15:30:00Z",
    "completed_by": "user-456",
    "parent_series_id": "series-789",
    "is_recurring": true
  }
}
```

**Workflow**:
1. Todo Service publishes event
2. Analytics Service increments completion counter
3. Notification Service checks if todo is recurring:
   - If yes, calculate next instance and publish `todo.series.instance.created`
4. Audit Service logs completion

---

#### 4. todo.deleted.v1

**Description**: Published when a todo is soft-deleted.

**Producer**: Todo Service

**Consumers**: Audit Service, Analytics Service, Notification Service (cancel reminders)

**Schema**:
```json
{
  "type": "com.todoapp.todo.deleted.v1",
  "source": "//todoapp/services/todo-service",
  "subject": "todo/12345",
  "data": {
    "todo_id": "12345",
    "user_id": "user-456",
    "deleted_at": "2026-02-06T16:00:00Z",
    "deleted_by": "user-456",
    "soft_delete": true
  }
}
```

**Workflow**:
1. Todo Service publishes event
2. Notification Service cancels all pending reminders for this todo
3. Analytics Service marks as deleted (excluded from active metrics)
4. Audit Service logs deletion

---

#### 5. todo.reminder.due.v1

**Description**: Published when a reminder is due (scheduled by Todo Service or Notification Service).

**Producer**: Todo Service (scheduled job) or Notification Service (recurring reminders)

**Consumers**: Notification Service (send email/push)

**Schema**:
```json
{
  "type": "com.todoapp.todo.reminder.due.v1",
  "source": "//todoapp/services/todo-service",
  "subject": "todo/12345",
  "data": {
    "reminder_id": "reminder-999",
    "todo_id": "12345",
    "user_id": "user-456",
    "reminder_type": "before_due",
    "offset_minutes": 60,
    "due_at": "2026-02-15T17:00:00Z",
    "triggered_at": "2026-02-15T16:00:00Z"
  }
}
```

**Validation Rules**:
- `reminder_type`: Enum ["before_due", "overdue"], required
- `offset_minutes`: Integer (minutes before due date), required for "before_due"

**Idempotency**: Notification Service stores `reminder_id` to prevent duplicate sends.

---

#### 6. todo.series.created.v1

**Description**: Published when a recurring todo series is created.

**Producer**: Todo Service

**Consumers**: Audit Service, Analytics Service

**Schema**:
```json
{
  "type": "com.todoapp.todo.series.created.v1",
  "source": "//todoapp/services/todo-service",
  "subject": "series/789",
  "data": {
    "series_id": "series-789",
    "user_id": "user-456",
    "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0",
    "first_instance_id": "12345",
    "created_at": "2026-02-06T10:30:00Z"
  }
}
```

---

#### 7. todo.series.instance.created.v1

**Description**: Published when a new instance of a recurring series is generated.

**Producer**: Notification Service (when previous instance completes)

**Consumers**: Todo Service (store new instance), Audit Service, Analytics Service

**Schema**:
```json
{
  "type": "com.todoapp.todo.series.instance.created.v1",
  "source": "//todoapp/services/notification-service",
  "subject": "series/789",
  "data": {
    "series_id": "series-789",
    "instance_id": "54321",
    "user_id": "user-456",
    "title": "Weekly team meeting",
    "due_date": "2026-02-13T09:00:00Z",
    "instance_number": 2,
    "created_at": "2026-02-06T15:30:00Z"
  }
}
```

---

### User Domain Events

#### 8. user.created.v1

**Description**: Published when a new user registers.

**Producer**: User Service

**Consumers**: Audit Service, Analytics Service, Chat Service (create default conversation)

**Schema**:
```json
{
  "type": "com.todoapp.user.created.v1",
  "source": "//todoapp/services/user-service",
  "subject": "user/456",
  "data": {
    "user_id": "user-456",
    "email": "user@example.com",
    "name": "John Doe",
    "timezone": "America/New_York",
    "notification_preferences": {
      "email_enabled": true,
      "push_enabled": false,
      "quiet_hours": {
        "start": "22:00",
        "end": "07:00"
      }
    },
    "created_at": "2026-02-06T08:00:00Z"
  }
}
```

---

#### 9. user.updated.v1

**Description**: Published when user profile or preferences are modified.

**Producer**: User Service

**Consumers**: Audit Service, Notification Service (update notification preferences)

**Schema**:
```json
{
  "type": "com.todoapp.user.updated.v1",
  "source": "//todoapp/services/user-service",
  "subject": "user/456",
  "data": {
    "user_id": "user-456",
    "changes": {
      "timezone": {
        "old": "America/New_York",
        "new": "Europe/London"
      }
    },
    "updated_at": "2026-02-06T12:00:00Z",
    "version": 3
  }
}
```

---

#### 10. user.deleted.v1

**Description**: Published when a user account is deleted (GDPR right to be forgotten).

**Producer**: User Service

**Consumers**: Todo Service (cascade delete todos), Chat Service (delete conversations), Notification Service (cancel notifications), Audit Service

**Schema**:
```json
{
  "type": "com.todoapp.user.deleted.v1",
  "source": "//todoapp/services/user-service",
  "subject": "user/456",
  "data": {
    "user_id": "user-456",
    "deleted_at": "2026-02-06T18:00:00Z",
    "reason": "user_request"
  }
}
```

**Workflow** (Saga Pattern):
1. User Service publishes `user.deleted`
2. Todo Service deletes all todos for user
3. Chat Service deletes all conversations
4. Notification Service cancels all pending notifications
5. Analytics Service anonymizes metrics
6. Audit Service logs deletion (but preserves audit log per compliance)

---

### Chat Domain Events

#### 11. chat.message.sent.v1

**Description**: Published when a user sends a message to the chatbot.

**Producer**: Chat Service

**Consumers**: Audit Service, Analytics Service

**Schema**:
```json
{
  "type": "com.todoapp.chat.message.sent.v1",
  "source": "//todoapp/services/chat-service",
  "subject": "conversation/conv-123",
  "data": {
    "message_id": "msg-555",
    "conversation_id": "conv-123",
    "user_id": "user-456",
    "message": "Add a high priority task to buy groceries",
    "response": "I've created a high priority task: 'Buy groceries'. Would you like to set a due date?",
    "action_performed": "todo.created",
    "action_entity_id": "12345",
    "sent_at": "2026-02-06T10:30:00Z"
  }
}
```

---

### Notification Domain Events

#### 12. notification.sent.v1

**Description**: Published when a notification is successfully delivered.

**Producer**: Notification Service

**Consumers**: Audit Service, Analytics Service

**Schema**:
```json
{
  "type": "com.todoapp.notification.sent.v1",
  "source": "//todoapp/services/notification-service",
  "subject": "notification/notif-888",
  "data": {
    "notification_id": "notif-888",
    "user_id": "user-456",
    "type": "reminder",
    "channel": "email",
    "recipient": "user@example.com",
    "subject": "Reminder: Prepare Phase V documentation due in 1 hour",
    "sent_at": "2026-02-15T16:00:00Z",
    "delivery_status": "delivered"
  }
}
```

---

#### 13. notification.failed.v1

**Description**: Published when a notification delivery fails (retry needed).

**Producer**: Notification Service

**Consumers**: Notification Service (retry queue), Audit Service

**Schema**:
```json
{
  "type": "com.todoapp.notification.failed.v1",
  "source": "//todoapp/services/notification-service",
  "subject": "notification/notif-888",
  "data": {
    "notification_id": "notif-888",
    "user_id": "user-456",
    "type": "reminder",
    "channel": "email",
    "error_code": "SMTP_CONNECTION_TIMEOUT",
    "error_message": "Failed to connect to SMTP server",
    "failed_at": "2026-02-15T16:00:05Z",
    "retry_count": 1,
    "max_retries": 3
  }
}
```

**Workflow**:
1. Notification Service publishes `notification.failed`
2. Notification Service re-queues for retry with exponential backoff (1s, 2s, 4s)
3. If `retry_count` >= `max_retries`, send to dead letter queue

---

## Event Workflows

### Workflow 1: Create Recurring Todo with Reminders

```
User → Chat Service: "Add weekly meeting every Monday at 9am"
  ↓
Chat Service → Todo Service: POST /api/v1/todos (with recurrence_rule)
  ↓
Todo Service publishes: todo.created.v1 + todo.series.created.v1
  ↓
  ├─→ Audit Service: Log creation
  ├─→ Analytics Service: Increment todo count
  └─→ Notification Service: Schedule reminder for first instance
      ↓
      Notification Service publishes: todo.reminder.due.v1 (1 hour before)
      ↓
      Notification Service sends email → publishes: notification.sent.v1
```

### Workflow 2: Complete Recurring Todo Instance

```
User → Todo Service: PUT /api/v1/todos/12345/complete
  ↓
Todo Service publishes: todo.completed.v1
  ↓
  ├─→ Audit Service: Log completion
  ├─→ Analytics Service: Increment completion count
  └─→ Notification Service: Check if recurring
      ↓
      If recurring:
        Calculate next instance due date
        ↓
        Notification Service publishes: todo.series.instance.created.v1
        ↓
        Todo Service consumes event → creates new todo instance
        ↓
        Todo Service publishes: todo.created.v1 (for new instance)
```

### Workflow 3: User Deletion (GDPR Cascade)

```
User → User Service: DELETE /api/v1/users/{id}
  ↓
User Service publishes: user.deleted.v1
  ↓
  ├─→ Todo Service: DELETE all todos for user
  │   ↓
  │   Todo Service publishes: todo.deleted.v1 (for each todo)
  │
  ├─→ Chat Service: DELETE all conversations
  ├─→ Notification Service: CANCEL all pending notifications
  └─→ Audit Service: LOG deletion (preserve audit log)
```

## Error Handling

### Dead Letter Queue (DLQ)

**Configuration:**
- Each consumer group has a DLQ topic: `{original-topic}.dlq`
- Messages sent to DLQ after max retries exceeded
- DLQ retention: 30 days

**DLQ Processing:**
1. Monitoring alerts on DLQ message arrival
2. Manual investigation of failure reason
3. Fix consumer bug or data issue
4. Replay from DLQ to original topic

### Poison Messages

**Detection:**
- Message fails deserialization (invalid JSON)
- Message fails schema validation (missing required fields)
- Message processing throws unrecoverable exception

**Handling:**
1. Log error with full message payload
2. Send to DLQ immediately (do not retry)
3. Alert on-call engineer

### Duplicate Events

**Prevention:**
- Producer assigns unique `id` (UUID v4)
- Consumer stores processed event IDs (7-day sliding window)
- Consumer checks ID before processing (idempotency check)

**Implementation** (pseudo-code):
```python
def process_event(event):
    event_id = event['id']
    if redis.exists(f"processed:{event_id}"):
        logger.info(f"Duplicate event {event_id}, skipping")
        return

    # Process event
    handle_business_logic(event)

    # Mark as processed
    redis.setex(f"processed:{event_id}", 604800, "1")  # 7 days TTL
```

## Testing Strategy

### Unit Tests

Test each event producer and consumer in isolation:
- Producer: Verify correct event schema is published
- Consumer: Verify correct business logic executes for each event type

### Integration Tests

Test event flows end-to-end:
- Publish event to test Kafka cluster
- Assert consumer processes event correctly
- Verify state changes in database

### Contract Tests

Use JSON Schema to validate event contracts:
```python
from jsonschema import validate

def test_todo_created_schema():
    event = {...}  # Sample event
    schema = load_schema("todo.created.v1.json")
    validate(instance=event, schema=schema)  # Raises exception if invalid
```

### Load Tests

Simulate high event volume:
- Produce 10,000 events/second
- Measure consumer lag
- Verify no message loss

## Monitoring

### Metrics

**Producer Metrics:**
- `kafka_producer_messages_sent_total{topic}`
- `kafka_producer_errors_total{topic, error_type}`
- `kafka_producer_latency_seconds{topic}`

**Consumer Metrics:**
- `kafka_consumer_messages_received_total{topic, consumer_group}`
- `kafka_consumer_lag{topic, partition, consumer_group}`
- `kafka_consumer_processing_duration_seconds{topic}`

**Alerting Rules:**
- Alert if consumer lag > 10,000 messages for > 5 minutes
- Alert if consumer error rate > 5% for > 1 minute
- Alert if DLQ receives any messages

### Logging

**Event Logging:**
- Log every event produced (DEBUG level)
- Log every event consumed (DEBUG level)
- Log processing errors (ERROR level)

**Log Format** (structured JSON):
```json
{
  "timestamp": "2026-02-06T10:30:00Z",
  "level": "INFO",
  "service": "todo-service",
  "event_type": "com.todoapp.todo.created.v1",
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "action": "event_published",
  "topic": "todo.created",
  "partition": 2,
  "offset": 123456
}
```

## Schema Registry

**Tool**: [Confluent Schema Registry](https://docs.confluent.io/platform/current/schema-registry/index.html) or [Apicurio Registry](https://www.apicur.io/registry/)

**Purpose**:
- Centralized storage of event schemas
- Schema evolution validation (backward compatibility)
- Schema versioning and history

**Workflow**:
1. Developer defines event schema (JSON Schema or Avro)
2. Developer registers schema with registry (API call)
3. Producer validates event against schema before publishing
4. Consumer fetches schema from registry for deserialization

**Example Schema** (JSON Schema):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TodoCreated",
  "type": "object",
  "properties": {
    "todo_id": {"type": "string", "format": "uuid"},
    "user_id": {"type": "string", "format": "uuid"},
    "title": {"type": "string", "minLength": 1, "maxLength": 200}
  },
  "required": ["todo_id", "user_id", "title"]
}
```

## References

- [CloudEvents Specification v1.0](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Dapr Pub/Sub Building Block](https://docs.dapr.io/developing-applications/building-blocks/pubsub/)
- [Saga Pattern](https://microservices.io/patterns/data/saga.html)

---

**Next Steps:**
1. Define Dapr Pub/Sub component configurations in `dapr.md`
2. Implement event producers in each service
3. Implement event consumers with idempotency checks
4. Set up monitoring and alerting for event flows
