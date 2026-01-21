# MCP Tools Specification - Todo AI Chatbot

## Overview

This document defines the Model Context Protocol (MCP) tools for the Todo AI Chatbot. All tools are **stateless**, persisting data via SQLModel + PostgreSQL.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI Agent Layer                               │
│                   (OpenAI Agents SDK / Claude)                       │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ Tool Calls (JSON-RPC)
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         MCP Server                                   │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┬────────┐ │
│  │  add_task   │ list_tasks  │ update_task │complete_task│delete_ │ │
│  │             │             │             │             │ task   │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┴────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ SQLModel ORM
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                             │
│                    (todos table, users table)                        │
└─────────────────────────────────────────────────────────────────────┘
```

## Design Principles

1. **Stateless**: No in-memory state between tool calls
2. **User-Scoped**: All operations require `user_id` and enforce ownership
3. **Idempotent**: Safe to retry (where applicable)
4. **Structured Output**: JSON responses only
5. **Error Handling**: Graceful failures with meaningful messages

---

## Tool Definitions

### 1. add_task

**Purpose**: Create a new task/todo for a user.

**Input Schema**:
```json
{
  "name": "add_task",
  "description": "Create a new task for the user",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "The authenticated user's unique identifier"
      },
      "title": {
        "type": "string",
        "minLength": 1,
        "maxLength": 255,
        "description": "Brief title describing the task"
      },
      "description": {
        "type": "string",
        "maxLength": 2000,
        "description": "Optional detailed description of the task"
      }
    },
    "required": ["user_id", "title"]
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "task": {
      "type": "object",
      "properties": {
        "id": { "type": "integer" },
        "title": { "type": "string" },
        "description": { "type": "string", "nullable": true },
        "completed": { "type": "boolean" },
        "created_at": { "type": "string", "format": "date-time" }
      }
    },
    "message": { "type": "string" }
  }
}
```

**Example**:
```json
// Input
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}

// Output
{
  "success": true,
  "task": {
    "id": 42,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-01-19T10:30:00Z"
  },
  "message": "Task 'Buy groceries' created successfully"
}
```

---

### 2. list_tasks

**Purpose**: Retrieve all tasks for a user with optional filtering.

**Input Schema**:
```json
{
  "name": "list_tasks",
  "description": "List all tasks for a user with optional filtering",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "The authenticated user's unique identifier"
      },
      "completed": {
        "type": "boolean",
        "description": "Filter by completion status (omit for all tasks)"
      },
      "search": {
        "type": "string",
        "description": "Search term to filter tasks by title"
      },
      "limit": {
        "type": "integer",
        "minimum": 1,
        "maximum": 100,
        "default": 50,
        "description": "Maximum number of tasks to return"
      },
      "offset": {
        "type": "integer",
        "minimum": 0,
        "default": 0,
        "description": "Number of tasks to skip for pagination"
      }
    },
    "required": ["user_id"]
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "title": { "type": "string" },
          "description": { "type": "string", "nullable": true },
          "completed": { "type": "boolean" },
          "created_at": { "type": "string", "format": "date-time" },
          "updated_at": { "type": "string", "format": "date-time" }
        }
      }
    },
    "total": { "type": "integer" },
    "message": { "type": "string" }
  }
}
```

**Example**:
```json
// Input
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "completed": false
}

// Output
{
  "success": true,
  "tasks": [
    {
      "id": 42,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-01-19T10:30:00Z",
      "updated_at": "2026-01-19T10:30:00Z"
    },
    {
      "id": 43,
      "title": "Call dentist",
      "description": null,
      "completed": false,
      "created_at": "2026-01-19T11:00:00Z",
      "updated_at": "2026-01-19T11:00:00Z"
    }
  ],
  "total": 2,
  "message": "Found 2 incomplete tasks"
}
```

---

### 3. update_task

**Purpose**: Update an existing task's title and/or description.

**Input Schema**:
```json
{
  "name": "update_task",
  "description": "Update an existing task's title or description",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "The authenticated user's unique identifier"
      },
      "task_id": {
        "type": "integer",
        "description": "The ID of the task to update"
      },
      "title": {
        "type": "string",
        "minLength": 1,
        "maxLength": 255,
        "description": "New title for the task (optional)"
      },
      "description": {
        "type": "string",
        "maxLength": 2000,
        "description": "New description for the task (optional, use empty string to clear)"
      }
    },
    "required": ["user_id", "task_id"]
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "task": {
      "type": "object",
      "properties": {
        "id": { "type": "integer" },
        "title": { "type": "string" },
        "description": { "type": "string", "nullable": true },
        "completed": { "type": "boolean" },
        "updated_at": { "type": "string", "format": "date-time" }
      }
    },
    "message": { "type": "string" },
    "error": { "type": "string" }
  }
}
```

**Example**:
```json
// Input
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": 42,
  "title": "Buy groceries at Costco"
}

// Output (Success)
{
  "success": true,
  "task": {
    "id": 42,
    "title": "Buy groceries at Costco",
    "description": "Milk, eggs, bread",
    "completed": false,
    "updated_at": "2026-01-19T12:00:00Z"
  },
  "message": "Task 42 updated successfully"
}

// Output (Not Found)
{
  "success": false,
  "task": null,
  "message": "Task not found",
  "error": "Task 999 does not exist or does not belong to this user"
}
```

---

### 4. complete_task

**Purpose**: Mark a task as completed or incomplete (toggle).

**Input Schema**:
```json
{
  "name": "complete_task",
  "description": "Mark a task as completed or incomplete",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "The authenticated user's unique identifier"
      },
      "task_id": {
        "type": "integer",
        "description": "The ID of the task to mark complete/incomplete"
      },
      "completed": {
        "type": "boolean",
        "default": true,
        "description": "Set to true to complete, false to uncomplete"
      }
    },
    "required": ["user_id", "task_id"]
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "task": {
      "type": "object",
      "properties": {
        "id": { "type": "integer" },
        "title": { "type": "string" },
        "completed": { "type": "boolean" },
        "updated_at": { "type": "string", "format": "date-time" }
      }
    },
    "message": { "type": "string" },
    "error": { "type": "string" }
  }
}
```

**Example**:
```json
// Input
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": 42,
  "completed": true
}

// Output
{
  "success": true,
  "task": {
    "id": 42,
    "title": "Buy groceries",
    "completed": true,
    "updated_at": "2026-01-19T14:00:00Z"
  },
  "message": "Task 'Buy groceries' marked as completed"
}
```

---

### 5. delete_task

**Purpose**: Permanently delete a task.

**Input Schema**:
```json
{
  "name": "delete_task",
  "description": "Permanently delete a task",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "The authenticated user's unique identifier"
      },
      "task_id": {
        "type": "integer",
        "description": "The ID of the task to delete"
      }
    },
    "required": ["user_id", "task_id"]
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "deleted_task": {
      "type": "object",
      "properties": {
        "id": { "type": "integer" },
        "title": { "type": "string" }
      }
    },
    "message": { "type": "string" },
    "error": { "type": "string" }
  }
}
```

**Example**:
```json
// Input
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": 42
}

// Output (Success)
{
  "success": true,
  "deleted_task": {
    "id": 42,
    "title": "Buy groceries"
  },
  "message": "Task 'Buy groceries' has been deleted"
}

// Output (Not Found)
{
  "success": false,
  "deleted_task": null,
  "message": "Task not found",
  "error": "Task 999 does not exist or does not belong to this user"
}
```

---

## Error Handling

All tools return structured error responses:

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Human-readable error description"
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `TASK_NOT_FOUND` | Task ID does not exist or doesn't belong to user |
| `USER_NOT_FOUND` | Invalid user_id |
| `VALIDATION_ERROR` | Invalid input parameters |
| `DATABASE_ERROR` | Database operation failed |
| `PERMISSION_DENIED` | User doesn't have access to this task |

---

## Security Considerations

1. **User Isolation**: All queries include `WHERE user_id = ?` to enforce ownership
2. **Input Validation**: All inputs validated before database queries
3. **No SQL Injection**: SQLModel ORM with parameterized queries
4. **Rate Limiting**: Implemented at API gateway level (not in MCP tools)

---

## Implementation Notes

### Stateless Design
- No in-memory caching
- Each tool call creates a fresh database session
- Database is the single source of truth

### Database Connection
```python
from app.database import get_session

def tool_handler(user_id: str, ...):
    with get_session() as session:
        # Perform operations
        session.commit()
```

### User Ownership Enforcement
```python
def get_user_task(session: Session, user_id: UUID, task_id: int) -> Optional[Todo]:
    return session.exec(
        select(Todo).where(
            Todo.id == task_id,
            Todo.user_id == user_id
        )
    ).first()
```
