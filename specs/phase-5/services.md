# Phase V: Services API Specification

**Feature Branch**: `005-name-phase5-cloud`
**Created**: 2026-02-06
**Status**: Draft

## Overview

This document defines the REST API contracts for all microservices in Phase V, including request/response schemas, error handling, and authentication.

## API Design Principles

1. **RESTful**: Follow REST conventions (GET, POST, PUT, DELETE)
2. **Versioned**: All endpoints under `/api/v1/`
3. **JSON**: Request and response bodies in JSON format
4. **Authenticated**: All endpoints require JWT token (except public endpoints)
5. **Paginated**: List endpoints support pagination (limit/offset or cursor-based)
6. **Error Consistent**: Standard error response format across all services

## Common Patterns

### Authentication Header

All authenticated requests require JWT token:
```
Authorization: Bearer <jwt-token>
```

### Standard Error Response

```json
{
  "error": {
    "code": "TODO_NOT_FOUND",
    "message": "Todo with ID 12345 not found",
    "details": {
      "todo_id": "12345"
    },
    "request_id": "req-abc-123",
    "timestamp": "2026-02-06T10:30:00Z"
  }
}
```

### Pagination (Cursor-based)

**Request**:
```
GET /api/v1/todos?limit=20&cursor=eyJpZCI6MTIzNDV9
```

**Response**:
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTIzNjV9",
    "has_more": true,
    "total_count": 150
  }
}
```

## 1. Todo Service API

**Base URL**: `http://todo-service.todo-app-prod.svc.cluster.local:8000`

### POST /api/v1/todos - Create Todo

**Request**:
```json
{
  "title": "Prepare Phase V documentation",
  "description": "Write comprehensive specs",
  "priority": "high",
  "tags": ["work", "documentation"],
  "due_date": "2026-02-15T17:00:00Z",
  "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO"
}
```

**Response** (201 Created):
```json
{
  "id": "12345",
  "title": "Prepare Phase V documentation",
  "status": "pending",
  "priority": "high",
  "tags": ["work", "documentation"],
  "due_date": "2026-02-15T17:00:00Z",
  "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO",
  "parent_series_id": "series-789",
  "created_at": "2026-02-06T10:30:00Z",
  "updated_at": "2026-02-06T10:30:00Z"
}
```

### GET /api/v1/todos - List Todos

**Query Parameters**:
- `status`: Filter by status (pending, in_progress, completed)
- `priority`: Filter by priority (low, medium, high, urgent)
- `tags`: Filter by tags (comma-separated)
- `due_before`: Filter by due date (ISO 8601)
- `limit`: Page size (default 20, max 100)
- `cursor`: Pagination cursor

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "12345",
      "title": "Prepare Phase V documentation",
      "status": "pending",
      "priority": "high"
    }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6MTIzNjV9",
    "has_more": true
  }
}
```

### GET /api/v1/todos/{id} - Get Todo

**Response** (200 OK):
```json
{
  "id": "12345",
  "title": "Prepare Phase V documentation",
  "description": "Write comprehensive specs",
  "status": "pending",
  "priority": "high",
  "tags": ["work", "documentation"],
  "due_date": "2026-02-15T17:00:00Z",
  "created_at": "2026-02-06T10:30:00Z",
  "updated_at": "2026-02-06T10:30:00Z"
}
```

**Error** (404 Not Found):
```json
{
  "error": {
    "code": "TODO_NOT_FOUND",
    "message": "Todo with ID 12345 not found"
  }
}
```

### PUT /api/v1/todos/{id} - Update Todo

**Request**:
```json
{
  "title": "Updated title",
  "priority": "urgent"
}
```

**Response** (200 OK): Returns updated todo

### DELETE /api/v1/todos/{id} - Delete Todo

**Response** (204 No Content)

### POST /api/v1/todos/{id}/complete - Complete Todo

**Response** (200 OK): Returns completed todo with `completed_at` timestamp

### GET /api/v1/todos/search - Search Todos

**Query Parameters**:
- `q`: Search query (full-text search)
- `status`, `priority`, `tags`: Filters

**Response** (200 OK):
```json
{
  "data": [...],
  "total_results": 15,
  "query": "presentation"
}
```

### GET /api/v1/todos/series/{series_id} - Get Series Instances

Returns all instances of a recurring series.

## 2. User Service API

**Base URL**: `http://user-service.todo-app-prod.svc.cluster.local:8001`

### POST /api/v1/users - Create User (Public)

**Request**:
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "hashed_password",
  "timezone": "America/New_York"
}
```

**Response** (201 Created):
```json
{
  "id": "user-456",
  "email": "user@example.com",
  "name": "John Doe",
  "timezone": "America/New_York",
  "created_at": "2026-02-06T08:00:00Z"
}
```

### GET /api/v1/users/{id} - Get User Profile

**Response** (200 OK):
```json
{
  "id": "user-456",
  "email": "user@example.com",
  "name": "John Doe",
  "timezone": "America/New_York",
  "notification_preferences": {
    "email_enabled": true,
    "quiet_hours": {"start": "22:00", "end": "07:00"}
  }
}
```

### PUT /api/v1/users/{id}/notification-preferences - Update Preferences

**Request**:
```json
{
  "email_enabled": false,
  "push_enabled": true
}
```

**Response** (200 OK): Returns updated preferences

### DELETE /api/v1/users/{id} - Delete User (GDPR)

Triggers cascade deletion across all services.

**Response** (202 Accepted):
```json
{
  "message": "User deletion initiated",
  "request_id": "req-delete-456"
}
```

## 3. Chat Service API

**Base URL**: `http://chat-service.todo-app-prod.svc.cluster.local:8002`

### POST /api/v1/chat/message - Send Chat Message

**Request**:
```json
{
  "conversation_id": "conv-123",
  "message": "Add a high priority task to buy groceries"
}
```

**Response** (200 OK):
```json
{
  "message_id": "msg-555",
  "conversation_id": "conv-123",
  "response": "I've created a high priority task: 'Buy groceries'. Would you like to set a due date?",
  "action_performed": {
    "type": "todo.created",
    "entity_id": "12345"
  }
}
```

### GET /api/v1/chat/conversations - List Conversations

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "conv-123",
      "title": "Task Management Chat",
      "last_message_at": "2026-02-06T10:30:00Z"
    }
  ]
}
```

### GET /api/v1/chat/conversations/{id}/messages - Get Conversation History

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "msg-555",
      "role": "user",
      "content": "Add a task",
      "timestamp": "2026-02-06T10:30:00Z"
    },
    {
      "id": "msg-556",
      "role": "assistant",
      "content": "I've created the task",
      "timestamp": "2026-02-06T10:30:01Z"
    }
  ]
}
```

## 4. Notification Service API

**Base URL**: `http://notification-service.todo-app-prod.svc.cluster.local:8003`

### POST /api/v1/notifications/send - Send Notification (Internal)

**Request**:
```json
{
  "user_id": "user-456",
  "type": "reminder",
  "channel": "email",
  "template": "todo_reminder",
  "data": {
    "todo_title": "Prepare documentation",
    "due_at": "2026-02-15T17:00:00Z"
  }
}
```

**Response** (202 Accepted):
```json
{
  "notification_id": "notif-888",
  "status": "queued"
}
```

### GET /api/v1/notifications - List User Notifications

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "notif-888",
      "type": "reminder",
      "subject": "Reminder: Task due soon",
      "sent_at": "2026-02-15T16:00:00Z",
      "status": "delivered"
    }
  ]
}
```

## 5. Audit Service API

**Base URL**: `http://audit-service.todo-app-prod.svc.cluster.local:8004`

### GET /api/v1/audit-log - Query Audit Log

**Query Parameters**:
- `user_id`: Filter by user
- `entity_id`: Filter by entity (todo_id, conversation_id, etc.)
- `event_type`: Filter by event type
- `start_date`, `end_date`: Date range

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "audit-1001",
      "event_type": "com.todoapp.todo.created.v1",
      "entity_id": "12345",
      "user_id": "user-456",
      "timestamp": "2026-02-06T10:30:00Z",
      "payload": {...}
    }
  ]
}
```

### GET /api/v1/audit-log/export - Export User Audit Log (GDPR)

**Query Parameters**:
- `user_id`: Required

**Response** (200 OK): JSON file download with full audit history

## 6. Analytics Service API

**Base URL**: `http://analytics-service.todo-app-prod.svc.cluster.local:8005`

### GET /api/v1/analytics/dashboard - Get Dashboard Metrics

**Response** (200 OK):
```json
{
  "total_todos": 150,
  "completed_todos": 95,
  "completion_rate": 0.63,
  "avg_completion_time_hours": 24.5,
  "overdue_count": 5,
  "high_priority_count": 12
}
```

### GET /api/v1/analytics/trends - Get Completion Trends

**Query Parameters**:
- `start_date`, `end_date`: Date range
- `granularity`: day, week, month

**Response** (200 OK):
```json
{
  "data": [
    {"date": "2026-02-01", "completed": 15, "created": 20},
    {"date": "2026-02-02", "completed": 12, "created": 18}
  ]
}
```

### GET /api/v1/analytics/insights - Get AI Insights

**Response** (200 OK):
```json
{
  "insights": [
    {
      "type": "productivity_warning",
      "message": "You have 5 overdue high-priority tasks",
      "action": "Focus on completing overdue tasks first"
    },
    {
      "type": "streak",
      "message": "7-day completion streak! Keep it up!",
      "action": null
    }
  ]
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| TODO_NOT_FOUND | 404 | Todo does not exist |
| USER_NOT_FOUND | 404 | User does not exist |
| UNAUTHORIZED | 401 | Missing or invalid JWT token |
| FORBIDDEN | 403 | User lacks permission for resource |
| VALIDATION_ERROR | 400 | Request validation failed |
| CONFLICT | 409 | Resource already exists or version mismatch |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Unexpected server error |

## Rate Limiting

All endpoints are rate-limited:
- **Authenticated users**: 100 requests/minute
- **Public endpoints**: 10 requests/minute per IP

**Response** (429 Too Many Requests):
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Retry after 60 seconds",
    "retry_after": 60
  }
}
```

## Health Checks

All services expose health check endpoints:

### GET /health/live - Liveness Probe

**Response** (200 OK): `{"status": "ok"}`

### GET /health/ready - Readiness Probe

**Response** (200 OK): `{"status": "ok", "dependencies": {"postgres": "ok", "kafka": "ok"}}`

### GET /health/startup - Startup Probe

**Response** (200 OK): `{"status": "ok", "startup_time": "2.5s"}`

## References

- [REST API Design Best Practices](https://restfulapi.net/)
- [OpenAPI 3.1 Specification](https://swagger.io/specification/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Next Steps:**
1. Generate OpenAPI 3.1 specs for each service
2. Implement API endpoints in FastAPI
3. Add API integration tests
4. Set up API documentation portal (Swagger UI)
