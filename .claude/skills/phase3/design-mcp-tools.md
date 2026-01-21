# Skill: design-mcp-tools

## 1. Skill Name
`design-mcp-tools`

## 2. Purpose
Design and implement stateless MCP (Model Context Protocol) tools for AI chatbot task management. This skill creates tool definitions, parameter schemas, and implementations that allow AI agents to perform CRUD operations on todos through natural language commands while persisting all state to PostgreSQL.

## 3. Applicable Agents
- **mcp-tool-architect** (primary)
- todo-ai-agent-designer (consumer perspective)
- chat-api-orchestrator (integration)
- mcp-compliance-validator (validation)
- fastapi-backend-architect (backend alignment)

## 4. Inputs
- **Existing Database Models**: SQLModel schemas (User, Todo) from Phase 2
- **User Stories**: Natural language commands the AI should understand
- **MCP Protocol Specification**: Official MCP SDK requirements
- **Security Requirements**: User isolation and ownership enforcement rules
- **Phase 3 Specification**: AI chatbot architecture requirements

## 5. Outputs
- **MCP Tool Definitions**: Complete schemas for each tool (JSON Schema format)
- **Tool Input Schemas**: Pydantic models for request validation
- **Tool Output Schemas**: Pydantic models for structured responses
- **Tool Implementations**: Stateless Python functions for each operation
- **MCP Server**: Server wrapper for tool discovery and invocation
- **Example Inputs/Outputs**: JSON examples for each tool

## 6. Scope & Boundaries

### In Scope
- Tool schemas for: `add_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task`
- Input parameter definitions with types, constraints, and validation rules
- Output response structures with success/error handling
- User ownership enforcement on all operations
- PostgreSQL persistence via SQLModel ORM
- Stateless design (no in-memory state between calls)
- JSON-RPC style tool invocation pattern

### Out of Scope
- FastAPI route exposure (tools are internal, not HTTP endpoints)
- WebSocket/real-time tool notifications
- Tool versioning or deprecation
- Multi-tenant isolation beyond user_id
- Caching or performance optimization
- Rate limiting (handled at API gateway level)
- Authentication/authorization (handled by chat API layer)

## 7. Reusability Notes
- **Phase 3**: Core MCP tools for AI chatbot task management
- **Phase 4**: Extend with collaboration tools (share_task, assign_task)
- **Phase 5**: Add advanced tools (set_reminder, create_recurring_task)
- **Cross-Project**: MCP tool patterns reusable for any domain (notes, calendar, etc.)

### Reusability Mechanisms
- Tool definitions exportable as OpenAPI/JSON Schema
- Input/output schemas versioned via Pydantic model inheritance
- Tool registry pattern enables dynamic tool discovery
- Stateless design allows horizontal scaling

## 8. Dependencies

### Upstream Dependencies
- `relational-schema-design` (Todo, User models from Phase 2)
- `data-ownership-enforcement` (user_id filtering pattern)
- MCP Protocol specification (tool definition format)

### Downstream Dependencies
- `todo-ai-agent-designer` (maps NL commands to tool calls)
- `chat-api-orchestrator` (invokes tools from chat endpoint)
- `mcp-compliance-validator` (validates tool correctness)

### Parallel Dependencies
- `conversation-persistence` (chat history storage)
- `chatkit-frontend-integrator` (UI sends chat messages)

## 9. Quality Expectations

### Completeness
- Every tool has complete input schema with all parameters documented
- Every tool has complete output schema covering success and error cases
- All error codes documented with human-readable messages
- Example inputs/outputs provided for each tool

### Correctness
- Tools are 100% stateless (fresh DB session per call)
- User ownership enforced on every query (WHERE user_id = ?)
- Input validation catches all invalid data before DB operations
- Output serialization handles all edge cases (null, empty, datetime)

### Clarity
- Tool names are action-oriented verbs (add, list, update, complete, delete)
- Parameter names are self-documenting (task_id not id)
- Error messages actionable for AI agent reasoning
- JSON Schema descriptions explain purpose and constraints

### Testability
- Each tool testable in isolation with mock database
- Input validation testable with edge cases
- Error handling testable with failure scenarios
- Integration testable with real PostgreSQL

## 10. Example Usage (Spec-Level)

### Scenario: Complete MCP Tools for Phase 3 AI Chatbot

---

#### Tool 1: add_task

**Purpose**: Create a new task for the authenticated user.

**Input Schema**:
```json
{
  "name": "add_task",
  "description": "Create a new task for the user. Use when the user wants to add, create, or make a new todo item.",
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

**Example Input**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Example Output (Success)**:
```json
{
  "success": true,
  "task": {
    "id": 42,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-01-19T10:30:00Z",
    "updated_at": "2026-01-19T10:30:00Z"
  },
  "message": "Task 'Buy groceries' created successfully"
}
```

**Example Output (Error)**:
```json
{
  "success": false,
  "task": null,
  "message": "Failed to create task",
  "error": "VALIDATION_ERROR: Title cannot be empty"
}
```

---

#### Tool 2: list_tasks

**Purpose**: Retrieve user's tasks with optional filtering.

**Input Schema**:
```json
{
  "name": "list_tasks",
  "description": "List all tasks for a user with optional filtering. Use when the user wants to see, view, show, or get their tasks/todos.",
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
        "maxLength": 255,
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

**Example Input**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "completed": false
}
```

**Example Output**:
```json
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

#### Tool 3: update_task

**Purpose**: Modify an existing task's title or description.

**Input Schema**:
```json
{
  "name": "update_task",
  "description": "Update an existing task's title or description. Use when the user wants to change, modify, edit, or rename a task.",
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
        "description": "New description (optional, use empty string to clear)"
      }
    },
    "required": ["user_id", "task_id"]
  }
}
```

**Example Input**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": 42,
  "title": "Buy groceries at Costco"
}
```

**Example Output (Success)**:
```json
{
  "success": true,
  "task": {
    "id": 42,
    "title": "Buy groceries at Costco",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-01-19T10:30:00Z",
    "updated_at": "2026-01-19T12:00:00Z"
  },
  "message": "Task 42 updated successfully"
}
```

**Example Output (Not Found)**:
```json
{
  "success": false,
  "task": null,
  "message": "Task not found",
  "error": "TASK_NOT_FOUND: Task 999 does not exist or does not belong to this user"
}
```

---

#### Tool 4: complete_task

**Purpose**: Mark a task as completed or incomplete.

**Input Schema**:
```json
{
  "name": "complete_task",
  "description": "Mark a task as completed or incomplete. Use when the user wants to finish, complete, done, check off, or undo a task.",
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

**Example Input**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": 42,
  "completed": true
}
```

**Example Output**:
```json
{
  "success": true,
  "task": {
    "id": 42,
    "title": "Buy groceries",
    "completed": true,
    "created_at": "2026-01-19T10:30:00Z",
    "updated_at": "2026-01-19T14:00:00Z"
  },
  "message": "Task 'Buy groceries' marked as completed"
}
```

---

#### Tool 5: delete_task

**Purpose**: Permanently delete a task.

**Input Schema**:
```json
{
  "name": "delete_task",
  "description": "Permanently delete a task. Use when the user wants to remove, delete, or get rid of a task.",
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

**Example Input**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": 42
}
```

**Example Output (Success)**:
```json
{
  "success": true,
  "deleted_task": {
    "id": 42,
    "title": "Buy groceries"
  },
  "message": "Task 'Buy groceries' has been deleted"
}
```

**Example Output (Not Found)**:
```json
{
  "success": false,
  "deleted_task": null,
  "message": "Task not found",
  "error": "TASK_NOT_FOUND: Task 999 does not exist or does not belong to this user"
}
```

---

#### Error Response Standard

All tools return errors in this format:
```json
{
  "success": false,
  "error": "ERROR_CODE: Human-readable description",
  "message": "Short user-facing message"
}
```

**Error Codes**:
| Code | Meaning |
|------|---------|
| `TASK_NOT_FOUND` | Task doesn't exist or doesn't belong to user |
| `USER_NOT_FOUND` | Invalid user_id |
| `VALIDATION_ERROR` | Invalid input parameters |
| `DATABASE_ERROR` | Database operation failed |
| `INTERNAL_ERROR` | Unexpected server error |

---

#### MCP Server Usage

```python
from app.mcp import MCPToolServer

# Initialize server
server = MCPToolServer()

# Get tools for AI agent
tools = server.get_tools_for_ai()
# Returns: [{"type": "function", "function": {...}}, ...]

# Call a tool
result = server.call_tool("add_task", {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
})

# Check result
if result.success:
    print(f"Created task: {result.result['task']['id']}")
else:
    print(f"Error: {result.error}")
```

---

#### Implementation Files

| File | Purpose |
|------|---------|
| `backend/app/mcp/__init__.py` | Module exports |
| `backend/app/mcp/schemas.py` | Pydantic input/output schemas |
| `backend/app/mcp/tools.py` | Tool implementations |
| `backend/app/mcp/server.py` | MCP server wrapper |
| `specs/003-phase3-ai-chatbot/mcp-tools-spec.md` | Full specification |

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 3
- **Last Updated**: 2026-01-19
- **Skill Type**: Design + Implementation
- **Execution Surface**: Agent (mcp-tool-architect)
