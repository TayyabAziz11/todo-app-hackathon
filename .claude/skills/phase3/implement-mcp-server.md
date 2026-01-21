# Skill: implement-mcp-server

## 1. Skill Name
`implement-mcp-server`

## 2. Purpose
Implement a production-ready MCP (Model Context Protocol) server using the Official MCP SDK that registers all task-related tools, connects them to database operations, and exposes them for invocation by the OpenAI Agents SDK. The server must be completely stateless with the database as the single source of truth.

## 3. Applicable Agents
- **mcp-tool-architect** (primary)
- chat-api-orchestrator (integration consumer)
- mcp-compliance-validator (validation)
- test-qa-validator (testing)
- fastapi-backend-architect (backend alignment)

## 4. Inputs
- **Tool Definitions**: MCP tool schemas from `design-mcp-tools` skill
- **Database Models**: SQLModel schemas (User, Todo) from Phase 2
- **Database Connection**: Engine and session management from `app.database`
- **MCP SDK Documentation**: Official MCP protocol specification
- **OpenAI Agents SDK Requirements**: Tool invocation interface requirements

## 5. Outputs
- **MCP Server Class**: `MCPToolServer` with tool registration and invocation
- **Tool Registry**: Dynamic tool discovery and listing
- **Invocation Handler**: `call_tool(name, arguments)` method
- **OpenAI SDK Integration**: `get_tools_for_ai()` method returning SDK-compatible format
- **Error Handling**: Structured error responses for all failure modes
- **Server Info Endpoint**: Metadata about server capabilities

## 6. Scope & Boundaries

### In Scope
- MCP server class implementation with singleton pattern
- Tool registration from schema definitions
- Tool invocation with input validation
- Database session management per tool call
- Structured JSON responses (success and error)
- OpenAI Agents SDK compatible tool format export
- Batch tool invocation support
- Server capability introspection

### Out of Scope
- HTTP/WebSocket transport layer (handled by chat API)
- Authentication/authorization (handled by chat API)
- Tool definition schemas (handled by `design-mcp-tools`)
- Tool business logic (handled by `tools.py`)
- Rate limiting or throttling
- Tool versioning or deprecation
- Caching or memoization

## 7. Reusability Notes
- **Phase 3**: Core MCP server for AI chatbot
- **Phase 4**: Same server, extended with collaboration tools
- **Phase 5**: Same pattern for advanced features
- **Cross-Project**: MCP server pattern reusable for any tool domain

### Reusability Mechanisms
- Tool registry is dynamic (add tools without code changes)
- Server interface is protocol-agnostic
- OpenAI SDK format exportable to other AI providers
- Singleton pattern allows global access

## 8. Dependencies

### Upstream Dependencies
- `design-mcp-tools` (tool definitions and schemas)
- `app.database` (database engine and session)
- `app.models` (SQLModel entities)
- MCP SDK (protocol compliance)

### Downstream Dependencies
- `chat-api-orchestrator` (invokes server from API)
- `todo-ai-agent-designer` (agent calls tools via server)
- `mcp-compliance-validator` (validates implementation)

### Parallel Dependencies
- `conversation-persistence` (runs alongside in chat flow)

## 9. Quality Expectations

### Statelessness
- Zero global mutable state
- Fresh database session per tool invocation
- No caching between calls
- Server instance holds only immutable configuration

### Correctness
- All tool invocations return structured responses
- Validation errors caught before database operations
- Unknown tools return clear error messages
- Database errors wrapped in error responses

### Robustness
- Exception handling on all code paths
- Graceful degradation on database failures
- Input validation before processing
- Timeout handling for long operations

### Testability
- Server instantiable without database for unit tests
- Mock database injectable for integration tests
- Each method independently testable
- Error paths verifiable

## 10. Example Usage (Implementation-Level)

### Scenario: Complete MCP Server Implementation

---

#### Server Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MCPToolServer                                │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    Tool Registry                                 ││
│  │  ┌─────────┬─────────┬─────────┬─────────┬─────────────────────┐││
│  │  │add_task │list_task│update_  │complete_│    delete_task      │││
│  │  │         │    s    │  task   │  task   │                     │││
│  │  └─────────┴─────────┴─────────┴─────────┴─────────────────────┘││
│  └─────────────────────────────────────────────────────────────────┘│
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    Invocation Handler                            ││
│  │  1. Validate tool name                                           ││
│  │  2. Parse & validate arguments                                   ││
│  │  3. Create fresh DB session                                      ││
│  │  4. Execute tool function                                        ││
│  │  5. Close session                                                ││
│  │  6. Return structured response                                   ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

---

#### Implementation: MCPToolServer Class

**File**: `backend/app/mcp/server.py`

```python
"""
MCP Server - Model Context Protocol server for Todo AI Chatbot.

This module implements the MCP server that exposes task management tools
to AI agents. The server is stateless and uses PostgreSQL for persistence.
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ValidationError

from app.mcp.schemas import get_tool_definitions, MCPToolDefinition
from app.mcp.tools import invoke_tool, TOOL_HANDLERS

logger = logging.getLogger(__name__)


class MCPToolCall(BaseModel):
    """Represents a tool call request from an AI agent."""
    name: str
    arguments: Dict[str, Any]


class MCPToolResult(BaseModel):
    """Represents the result of a tool call."""
    tool_name: str
    success: bool
    result: Dict[str, Any]
    error: Optional[str] = None


class MCPToolServer:
    """
    MCP Server for Todo AI Chatbot task management.

    This server exposes five stateless tools:
    - add_task: Create a new task
    - list_tasks: List tasks with filtering
    - update_task: Modify task properties
    - complete_task: Mark task complete/incomplete
    - delete_task: Remove a task

    All tools are stateless and persist data via SQLModel + PostgreSQL.
    """

    def __init__(self):
        """Initialize the MCP server with tool definitions."""
        self._tool_definitions = {t.name: t for t in get_tool_definitions()}
        logger.info(f"MCPToolServer initialized with {len(self._tool_definitions)} tools")

    # -------------------------------------------------------------------------
    # Tool Discovery (for AI agents)
    # -------------------------------------------------------------------------

    def list_tools(self) -> List[MCPToolDefinition]:
        """
        List all available tools with their schemas.

        Returns:
            List of MCPToolDefinition objects
        """
        return list(self._tool_definitions.values())

    def get_tool(self, name: str) -> Optional[MCPToolDefinition]:
        """
        Get a specific tool definition by name.

        Args:
            name: Tool name (e.g., "add_task")

        Returns:
            MCPToolDefinition if found, None otherwise
        """
        return self._tool_definitions.get(name)

    def get_tools_for_ai(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions in OpenAI Agents SDK format.

        Returns:
            List of tools compatible with OpenAI function calling
        """
        tools = []
        for tool_def in self._tool_definitions.values():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_def.name,
                    "description": tool_def.description,
                    "parameters": tool_def.inputSchema.model_dump(),
                }
            })
        return tools

    # -------------------------------------------------------------------------
    # Tool Invocation (stateless, fresh session per call)
    # -------------------------------------------------------------------------

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """
        Call a tool with the given arguments.

        This is the main entry point for tool invocation. Each call:
        1. Validates tool existence
        2. Validates arguments against schema
        3. Creates fresh database session
        4. Executes tool function
        5. Returns structured response

        Args:
            name: Tool name (e.g., "add_task")
            arguments: Dictionary of arguments

        Returns:
            MCPToolResult with success status and result data
        """
        logger.info(f"Tool call: {name}")

        # Check if tool exists
        if name not in TOOL_HANDLERS:
            logger.warning(f"Unknown tool: {name}")
            return MCPToolResult(
                tool_name=name,
                success=False,
                result={},
                error=f"UNKNOWN_TOOL: Tool '{name}' not found. Available: {list(TOOL_HANDLERS.keys())}",
            )

        try:
            # Invoke tool (creates its own DB session)
            result = invoke_tool(name, arguments)

            return MCPToolResult(
                tool_name=name,
                success=result.get("success", True),
                result=result,
                error=result.get("error"),
            )

        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return MCPToolResult(
                tool_name=name,
                success=False,
                result={},
                error=f"VALIDATION_ERROR: {str(e)}",
            )

        except Exception as e:
            logger.error(f"Tool failed: {e}")
            return MCPToolResult(
                tool_name=name,
                success=False,
                result={},
                error=f"INTERNAL_ERROR: {str(e)}",
            )

    def call_tool_raw(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool and return raw dictionary result.

        Convenience method for direct result access.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Dictionary result from the tool
        """
        return invoke_tool(name, arguments)

    # -------------------------------------------------------------------------
    # Batch Operations
    # -------------------------------------------------------------------------

    def call_tools_batch(self, tool_calls: List[MCPToolCall]) -> List[MCPToolResult]:
        """
        Call multiple tools in sequence.

        Args:
            tool_calls: List of MCPToolCall objects

        Returns:
            List of MCPToolResult objects
        """
        return [self.call_tool(call.name, call.arguments) for call in tool_calls]

    # -------------------------------------------------------------------------
    # Server Metadata
    # -------------------------------------------------------------------------

    def get_server_info(self) -> Dict[str, Any]:
        """
        Get server metadata and capabilities.

        Returns:
            Dictionary with server information
        """
        return {
            "name": "todo-mcp-server",
            "version": "1.0.0",
            "protocol_version": "2024-11-05",
            "capabilities": {
                "tools": True,
                "resources": False,
                "prompts": False,
            },
            "tools_count": len(self._tool_definitions),
            "tool_names": list(self._tool_definitions.keys()),
        }


# =============================================================================
# Singleton Access
# =============================================================================

_server_instance: Optional[MCPToolServer] = None


def get_mcp_server() -> MCPToolServer:
    """Get the singleton MCP server instance."""
    global _server_instance
    if _server_instance is None:
        _server_instance = MCPToolServer()
    return _server_instance
```

---

#### Implementation: Tool Invocation Handler

**File**: `backend/app/mcp/tools.py` (invoke_tool function)

```python
"""
Tool invocation handler - dispatches calls to individual tool functions.
"""

from app.mcp.schemas import (
    AddTaskInput, ListTasksInput, UpdateTaskInput,
    CompleteTaskInput, DeleteTaskInput,
)

# Tool function registry
TOOL_HANDLERS = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "update_task": update_task,
    "complete_task": complete_task,
    "delete_task": delete_task,
}

# Input schema registry
INPUT_SCHEMAS = {
    "add_task": AddTaskInput,
    "list_tasks": ListTasksInput,
    "update_task": UpdateTaskInput,
    "complete_task": CompleteTaskInput,
    "delete_task": DeleteTaskInput,
}


def invoke_tool(tool_name: str, arguments: dict) -> dict:
    """
    Invoke an MCP tool by name with the given arguments.

    This is the main dispatch function:
    1. Validates tool name exists
    2. Parses arguments through Pydantic schema
    3. Calls the tool handler function
    4. Returns result as JSON-serializable dict

    Args:
        tool_name: Name of the tool to invoke
        arguments: Dictionary of arguments

    Returns:
        Dictionary result (JSON-serializable)

    Raises:
        ValueError: If tool_name is not recognized
        ValidationError: If arguments don't match schema
    """
    if tool_name not in TOOL_HANDLERS:
        raise ValueError(f"Unknown tool: {tool_name}")

    # Validate and parse input through Pydantic
    input_schema = INPUT_SCHEMAS[tool_name]
    validated_input = input_schema(**arguments)

    # Invoke the tool (each tool creates its own DB session)
    handler = TOOL_HANDLERS[tool_name]
    result = handler(validated_input)

    # Return as dict for JSON serialization
    return result.model_dump()
```

---

#### Implementation: Individual Tool (Stateless Pattern)

**File**: `backend/app/mcp/tools.py` (tool function example)

```python
"""
Example tool implementation showing stateless pattern.
Each tool creates a fresh database session.
"""

from sqlmodel import Session
from app.database import get_engine
from app.models.todo import Todo


def add_task(input_data: AddTaskInput) -> AddTaskOutput:
    """
    Create a new task for a user.

    STATELESS: Creates fresh DB session, commits, closes.
    No in-memory state retained between calls.
    """
    logger.info(f"add_task called for user {input_data.user_id}")

    try:
        # Fresh database session (stateless)
        engine = get_engine()
        with Session(engine) as session:
            # Create the todo
            todo = Todo(
                user_id=input_data.user_id,
                title=input_data.title,
                description=input_data.description,
                completed=False,
            )

            session.add(todo)
            session.commit()
            session.refresh(todo)

            # Return structured response
            return AddTaskOutput(
                success=True,
                task=_todo_to_task_result(todo),
                message=f"Task '{todo.title}' created successfully",
            )

    except Exception as e:
        logger.error(f"add_task failed: {e}")
        return AddTaskOutput(
            success=False,
            task=None,
            message="Failed to create task",
            error=f"DATABASE_ERROR: {str(e)}",
        )
```

---

#### Integration: OpenAI Agents SDK

**Usage in Chat API**:

```python
from openai import OpenAI
from app.mcp import get_mcp_server

# Initialize
client = OpenAI()
mcp_server = get_mcp_server()

# Get tools for AI agent
tools = mcp_server.get_tools_for_ai()

# Create agent with tools
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Add a task to buy groceries"}],
    tools=tools,
    tool_choice="auto",
)

# Handle tool calls from AI
for tool_call in response.choices[0].message.tool_calls:
    result = mcp_server.call_tool(
        tool_call.function.name,
        json.loads(tool_call.function.arguments)
    )
    # Return result to AI for response generation
```

---

#### Statelessness Verification Checklist

| Requirement | Implementation |
|-------------|----------------|
| No global mutable state | `_server_instance` is singleton but immutable after init |
| Fresh DB session per call | `with Session(engine)` in each tool function |
| No caching | Results computed fresh each invocation |
| Database is source of truth | All state read/written to PostgreSQL |
| Independent tool calls | Each `call_tool()` is self-contained |
| Horizontal scalability | Any server instance can handle any request |

---

#### Error Response Contract

All errors follow this structure:

```json
{
  "tool_name": "add_task",
  "success": false,
  "result": {},
  "error": "ERROR_CODE: Human-readable description"
}
```

**Error Codes**:

| Code | When |
|------|------|
| `UNKNOWN_TOOL` | Tool name not in registry |
| `VALIDATION_ERROR` | Input fails Pydantic validation |
| `TASK_NOT_FOUND` | Task ID doesn't exist or wrong owner |
| `DATABASE_ERROR` | Database operation failed |
| `INTERNAL_ERROR` | Unexpected exception |

---

#### Testing the Server

```python
import pytest
from app.mcp import MCPToolServer

def test_server_initialization():
    """Server initializes with all tools registered."""
    server = MCPToolServer()
    assert len(server.list_tools()) == 5

def test_unknown_tool_error():
    """Unknown tools return structured error."""
    server = MCPToolServer()
    result = server.call_tool("unknown_tool", {})
    assert result.success is False
    assert "UNKNOWN_TOOL" in result.error

def test_validation_error():
    """Invalid arguments return validation error."""
    server = MCPToolServer()
    result = server.call_tool("add_task", {"user_id": "not-a-uuid"})
    assert result.success is False
    assert "VALIDATION_ERROR" in result.error

def test_openai_format():
    """Tools export in OpenAI SDK format."""
    server = MCPToolServer()
    tools = server.get_tools_for_ai()
    assert all(t["type"] == "function" for t in tools)
    assert all("function" in t for t in tools)
```

---

## Metadata
- **Version**: 1.0.0
- **Phase Introduced**: Phase 3
- **Last Updated**: 2026-01-19
- **Skill Type**: Implementation
- **Execution Surface**: Agent (mcp-tool-architect)
- **Prerequisite Skills**: `design-mcp-tools`
