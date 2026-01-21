# Skill: validate-mcp-architecture

**Version**: 1.0.0
**Created**: 2026-01-19
**Category**: Phase 3 - Validation

---

## 1. Purpose

Validate Model Context Protocol (MCP) architecture compliance for Phase 3 AI Chatbot, ensuring tools are stateless, properly registered, schema-correct, and maintain clean separation from FastAPI routing layer. This skill provides a comprehensive compliance checklist and violation detection methodology.

Proper MCP architecture is critical for horizontal scalability, agent determinism, and maintainability.

---

## 2. Applicable Agents

**Primary Agent**: `mcp-compliance-validator`
- Validates MCP protocol compliance
- Identifies architectural violations
- Ensures stateless tool design

**Supporting Agents**:
- `mcp-tool-architect` - Tool design review
- `test-qa-validator` - Automated compliance testing

---

## 3. Input

### Prerequisites
- MCP tools implementation (`backend/app/mcp/tools.py`)
- MCP server (`backend/app/mcp/server.py`)
- MCP schemas (`backend/app/mcp/schemas.py`)
- Chat API endpoint (`backend/app/api/routes/chat.py`)

### Requirements
- Verify all tools are stateless
- Verify tool registration correctness
- Verify schema accuracy
- Verify layer separation

---

## 4. Output

## MCP Compliance Checklist

### 1. Stateless Tool Design

#### 1.1 Database Session Management

**✅ COMPLIANT**:
```python
def add_task(input_data: AddTaskInput) -> AddTaskOutput:
    """Stateless tool - creates fresh DB session."""
    engine = get_engine()
    with Session(engine) as session:  # Fresh session
        todo = Todo(...)
        session.add(todo)
        session.commit()
        session.refresh(todo)
        # Session automatically closed
    return AddTaskOutput(...)
```

**❌ VIOLATION**:
```python
# Global session (STATEFUL)
global_session = Session(engine)

def add_task(input_data: AddTaskInput) -> AddTaskOutput:
    todo = Todo(...)
    global_session.add(todo)  # ❌ Shared state
    global_session.commit()
    return AddTaskOutput(...)
```

**Validation**:
- [ ] No module-level database sessions
- [ ] Each tool creates fresh session via `with Session(engine)`
- [ ] Sessions closed at tool completion
- [ ] No session passed between tools

---

#### 1.2 No In-Memory Caching

**✅ COMPLIANT**:
```python
def list_tasks(input_data: ListTasksInput) -> ListTasksOutput:
    """Queries database every time - no cache."""
    engine = get_engine()
    with Session(engine) as session:
        statement = select(Todo).where(Todo.user_id == input_data.user_id)
        todos = session.exec(statement).all()  # Fresh query
        return ListTasksOutput(tasks=[...])
```

**❌ VIOLATION**:
```python
# Module-level cache (STATEFUL)
task_cache = {}

def list_tasks(input_data: ListTasksInput) -> ListTasksOutput:
    # Check cache first
    if input_data.user_id in task_cache:  # ❌ In-memory state
        return task_cache[input_data.user_id]

    # Query and cache
    tasks = query_database(...)
    task_cache[input_data.user_id] = tasks  # ❌ Storing state
    return tasks
```

**Validation**:
- [ ] No module-level caches (dicts, lists, sets)
- [ ] No `lru_cache` decorators on tools
- [ ] All data queried from database
- [ ] No file-based caching

---

#### 1.3 No Global State

**✅ COMPLIANT**:
```python
def complete_task(input_data: CompleteTaskInput) -> CompleteTaskOutput:
    """Pure function - no global state."""
    engine = get_engine()
    with Session(engine) as session:
        todo = session.get(Todo, input_data.task_id)
        if not todo:
            return CompleteTaskOutput(success=False, error="Not found")

        todo.completed = input_data.completed
        session.commit()
        return CompleteTaskOutput(success=True, task=...)
```

**❌ VIOLATION**:
```python
# Global state (STATEFUL)
last_operation_time = None
operation_count = 0

def complete_task(input_data: CompleteTaskInput) -> CompleteTaskOutput:
    global last_operation_time, operation_count  # ❌ Global state

    last_operation_time = datetime.now()  # ❌ Side effect
    operation_count += 1  # ❌ Mutation

    # ... rest of logic
```

**Validation**:
- [ ] No global variables in tool module
- [ ] No `global` keyword usage
- [ ] No class-level state
- [ ] No singleton patterns (except get_engine)

---

#### 1.4 Deterministic Behavior

**✅ COMPLIANT**:
```python
def update_task(input_data: UpdateTaskInput) -> UpdateTaskOutput:
    """Same inputs → same outputs (deterministic)."""
    engine = get_engine()
    with Session(engine) as session:
        todo = session.get(Todo, input_data.task_id)

        # Deterministic: only depends on input
        if input_data.title:
            todo.title = input_data.title
        if input_data.description:
            todo.description = input_data.description

        session.commit()
        return UpdateTaskOutput(success=True, task=...)
```

**❌ VIOLATION**:
```python
def update_task(input_data: UpdateTaskInput) -> UpdateTaskOutput:
    # Non-deterministic: depends on request count
    if operation_count > 100:  # ❌ External state
        return UpdateTaskOutput(success=False, error="Quota exceeded")

    # Non-deterministic: random behavior
    if random.random() > 0.5:  # ❌ Random
        add_bonus_points()  # ❌ Side effect

    # ... rest of logic
```

**Validation**:
- [ ] No random number generation
- [ ] No dependency on request counters
- [ ] No time-based logic (except timestamps)
- [ ] No external API calls during tool execution

---

### 2. Tool Registration

#### 2.1 Tool Definition Completeness

**✅ COMPLIANT**:
```python
# In backend/app/mcp/server.py
def get_tool_definitions() -> List[MCPToolDefinition]:
    """Returns all 5 CRUD tools."""
    return [
        MCPToolDefinition(
            name="add_task",
            description="Create a new task for the user",
            input_schema=AddTaskInput.model_json_schema(),
        ),
        MCPToolDefinition(
            name="list_tasks",
            description="List user's tasks with optional filtering",
            input_schema=ListTasksInput.model_json_schema(),
        ),
        MCPToolDefinition(
            name="update_task",
            description="Update task title or description",
            input_schema=UpdateTaskInput.model_json_schema(),
        ),
        MCPToolDefinition(
            name="complete_task",
            description="Mark task as complete or incomplete",
            input_schema=CompleteTaskInput.model_json_schema(),
        ),
        MCPToolDefinition(
            name="delete_task",
            description="Delete a task permanently",
            input_schema=DeleteTaskInput.model_json_schema(),
        ),
    ]
```

**❌ VIOLATION**:
```python
def get_tool_definitions() -> List[MCPToolDefinition]:
    return [
        MCPToolDefinition(
            name="add_task",
            description="Create task",  # ❌ Vague description
            # ❌ Missing input_schema
        ),
        # ❌ Missing list_tasks
        # ❌ Missing update_task
        MCPToolDefinition(name="complete_task", ...),
        MCPToolDefinition(name="delete_task", ...),
    ]
```

**Validation**:
- [ ] All 5 CRUD tools registered
- [ ] Each tool has clear description
- [ ] Each tool has input_schema
- [ ] No duplicate tool names

---

#### 2.2 Tool Invocation Mapping

**✅ COMPLIANT**:
```python
# In backend/app/mcp/server.py
TOOL_REGISTRY: Dict[str, Callable] = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "update_task": update_task,
    "complete_task": complete_task,
    "delete_task": delete_task,
}

def invoke_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Maps tool name to function."""
    if name not in TOOL_REGISTRY:
        return {"success": False, "error": f"Unknown tool: {name}"}

    tool_func = TOOL_REGISTRY[name]
    # ... validation and invocation
```

**❌ VIOLATION**:
```python
def invoke_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    # ❌ Hard-coded if/else (not scalable)
    if name == "add_task":
        return add_task(...)
    elif name == "list_tasks":
        return list_tasks(...)
    # ❌ Missing complete_task, delete_task
```

**Validation**:
- [ ] Tool registry maps all 5 tools
- [ ] Registry keys match tool definition names
- [ ] invoke_tool handles all tools
- [ ] No missing mappings

---

#### 2.3 OpenAI SDK Integration

**✅ COMPLIANT**:
```python
# In backend/app/mcp/server.py
def get_tools_for_ai(self) -> List[Dict[str, Any]]:
    """Convert MCP tool definitions to OpenAI format."""
    tools = []
    for tool_def in self._tool_definitions.values():
        tools.append({
            "type": "function",
            "function": {
                "name": tool_def.name,
                "description": tool_def.description,
                "parameters": tool_def.input_schema,
            }
        })
    return tools
```

**❌ VIOLATION**:
```python
def get_tools_for_ai(self) -> List[Dict[str, Any]]:
    return [
        {
            "name": "add_task",  # ❌ Missing "type": "function"
            "description": "...",
            # ❌ Wrong key: should be "parameters" not "schema"
            "schema": AddTaskInput.model_json_schema(),
        }
    ]
```

**Validation**:
- [ ] Correct OpenAI tool format
- [ ] `type: "function"` present
- [ ] `function.name`, `function.description`, `function.parameters`
- [ ] Parameters use JSON Schema format

---

### 3. Schema Correctness

#### 3.1 Input Schema Validation

**✅ COMPLIANT**:
```python
# In backend/app/mcp/schemas.py
class AddTaskInput(BaseModel):
    """Input for add_task tool."""
    user_id: UUID = Field(..., description="User ID")
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task details")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        }
```

**❌ VIOLATION**:
```python
class AddTaskInput(BaseModel):
    # ❌ Missing field descriptions
    user_id: UUID
    title: str  # ❌ No length constraints
    # ❌ Missing description field entirely
```

**Validation**:
- [ ] All required fields marked with `...`
- [ ] Field descriptions present
- [ ] Length/range constraints where applicable
- [ ] Example provided in schema

---

#### 3.2 Output Schema Validation

**✅ COMPLIANT**:
```python
class AddTaskOutput(BaseModel):
    """Output from add_task tool."""
    success: bool = Field(..., description="Whether operation succeeded")
    task: Optional[TaskResult] = Field(None, description="Created task")
    message: str = Field(..., description="Human-readable result")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "task": {"id": 1, "title": "Buy groceries", ...},
                "message": "Task created successfully",
                "error": None
            }
        }
```

**❌ VIOLATION**:
```python
class AddTaskOutput(BaseModel):
    success: bool
    # ❌ Inconsistent: sometimes returns task, sometimes dict
    result: Union[TaskResult, Dict, None]
    # ❌ Missing message and error fields
```

**Validation**:
- [ ] Consistent structure across all outputs
- [ ] `success: bool` always present
- [ ] `message: str` for user feedback
- [ ] `error: Optional[str]` for failures
- [ ] Result field appropriately typed

---

#### 3.3 Schema-to-Tool Alignment

**✅ COMPLIANT**:
```python
# Schema
class CompleteTaskInput(BaseModel):
    user_id: UUID
    task_id: int
    completed: bool = True

# Tool uses exact schema
def complete_task(input_data: CompleteTaskInput) -> CompleteTaskOutput:
    # Direct access to validated fields
    user_id = input_data.user_id
    task_id = input_data.task_id
    completed = input_data.completed
    # ... logic
```

**❌ VIOLATION**:
```python
# Schema defines one thing
class CompleteTaskInput(BaseModel):
    user_id: UUID
    task_id: int
    completed: bool

# Tool expects different structure
def complete_task(input_data: dict) -> dict:  # ❌ Not using schema
    user_id = input_data["userId"]  # ❌ Wrong key (camelCase)
    # ... logic
```

**Validation**:
- [ ] Tool function signature uses schema types
- [ ] Tool accesses schema fields correctly
- [ ] No manual dict parsing in tools
- [ ] Field names match between schema and tool

---

### 4. Layer Separation

#### 4.1 No FastAPI in MCP Layer

**✅ COMPLIANT**:
```python
# backend/app/mcp/tools.py - Pure MCP layer
from sqlmodel import Session
from app.database import get_engine

def add_task(input_data: AddTaskInput) -> AddTaskOutput:
    """Pure tool - no FastAPI dependencies."""
    engine = get_engine()
    with Session(engine) as session:
        # Pure database logic
        todo = Todo(...)
        session.add(todo)
        session.commit()
        return AddTaskOutput(...)
```

**❌ VIOLATION**:
```python
# backend/app/mcp/tools.py
from fastapi import HTTPException, Depends  # ❌ FastAPI imports

def add_task(
    input_data: AddTaskInput,
    session: Session = Depends(get_session)  # ❌ FastAPI dependency
) -> AddTaskOutput:
    if not input_data.title:
        raise HTTPException(400, "Title required")  # ❌ HTTP exception
    # ... logic
```

**Validation**:
- [ ] No `from fastapi import ...` in MCP modules
- [ ] No `HTTPException` usage
- [ ] No `Depends()` usage
- [ ] No `Request` or `Response` objects

---

#### 4.2 No MCP Logic in FastAPI Layer

**✅ COMPLIANT**:
```python
# backend/app/api/routes/chat.py - FastAPI layer
from app.mcp import get_mcp_server

@router.post("/{user_id}/chat")
async def chat(...):
    # FastAPI layer: routing, auth, orchestration
    # Delegates to MCP server
    mcp_server = get_mcp_server()
    tools = mcp_server.get_tools_for_ai()

    # Agent runner uses tools via MCP server
    response = agent_runner.run(...)
    return ChatResponse(...)
```

**❌ VIOLATION**:
```python
# backend/app/api/routes/chat.py
from app.mcp.tools import add_task  # ❌ Direct tool import

@router.post("/{user_id}/chat")
async def chat(...):
    # ❌ Calling tool directly (bypassing MCP server)
    result = add_task(AddTaskInput(user_id=user_id, title="Test"))

    # ❌ Tool invocation logic in FastAPI layer
    if message.contains("add task"):
        tool_result = add_task(...)  # ❌ Intent classification here
```

**Validation**:
- [ ] FastAPI routes don't import tools directly
- [ ] FastAPI routes use `get_mcp_server()` API
- [ ] No tool invocation logic in routes
- [ ] No intent classification in routes

---

#### 4.3 Clean Dependency Flow

**✅ COMPLIANT**:
```
┌─────────────────────────────────────┐
│      FastAPI API Layer              │
│  (routes/chat.py)                   │
│  - Routing                          │
│  - Authentication                   │
│  - Orchestration                    │
└─────────────┬───────────────────────┘
              │ Uses
              ▼
┌─────────────────────────────────────┐
│      Agent Runner                   │
│  (agent/runner.py)                  │
│  - Conversation context             │
│  - OpenAI API calls                 │
└─────────────┬───────────────────────┘
              │ Gets tools from
              ▼
┌─────────────────────────────────────┐
│      MCP Server                     │
│  (mcp/server.py)                    │
│  - Tool registry                    │
│  - Tool invocation                  │
└─────────────┬───────────────────────┘
              │ Invokes
              ▼
┌─────────────────────────────────────┐
│      MCP Tools                      │
│  (mcp/tools.py)                     │
│  - Stateless operations             │
│  - Database access                  │
└─────────────────────────────────────┘
```

**❌ VIOLATION**:
```
┌─────────────────────────────────────┐
│      FastAPI API Layer              │
│  (routes/chat.py)                   │
│  ❌ Direct tool imports              │
│  ❌ Tool invocation logic            │
└─────────────┬───────────────────────┘
              │ Skips MCP server
              ▼
┌─────────────────────────────────────┐
│      MCP Tools                      │
│  ❌ HTTPException usage              │
│  ❌ FastAPI Depends                  │
└─────────────────────────────────────┘
```

**Validation**:
- [ ] Dependency flow follows architecture diagram
- [ ] No layer skipping
- [ ] No circular dependencies
- [ ] Clear separation of concerns

---

## 5. Automated Validation Script

**File**: `backend/tests/test_mcp_compliance.py`

```python
"""
MCP Architecture Compliance Tests.

Validates that MCP layer follows protocol specifications.
"""

import ast
import inspect
from pathlib import Path
from typing import Set

import pytest
from app.mcp import get_mcp_server
from app.mcp.tools import (
    add_task,
    list_tasks,
    update_task,
    complete_task,
    delete_task,
)


class TestStatelessDesign:
    """Test MCP tools are stateless."""

    def test_no_global_sessions(self):
        """Verify no module-level database sessions."""
        tools_file = Path("app/mcp/tools.py")
        source = tools_file.read_text()
        tree = ast.parse(source)

        # Check for global Session creation
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.Call):
                    if hasattr(node.value.func, 'id'):
                        assert node.value.func.id != 'Session', \
                            "Found global Session - tools must create fresh sessions"

    def test_no_global_caches(self):
        """Verify no module-level caches."""
        tools_file = Path("app/mcp/tools.py")
        source = tools_file.read_text()

        # Check for common cache patterns
        forbidden_patterns = [
            "cache = {}",
            "cache = []",
            "@lru_cache",
            "global cache",
        ]

        for pattern in forbidden_patterns:
            assert pattern not in source, \
                f"Found forbidden pattern: {pattern}"

    def test_tools_use_context_managers(self):
        """Verify tools use 'with Session(engine)' pattern."""
        tool_funcs = [add_task, list_tasks, update_task, complete_task, delete_task]

        for tool_func in tool_funcs:
            source = inspect.getsource(tool_func)
            assert "with Session(engine)" in source or "with Session(" in source, \
                f"{tool_func.__name__} doesn't use context manager for session"


class TestToolRegistration:
    """Test tool registration completeness."""

    def test_all_tools_registered(self):
        """Verify all 5 CRUD tools are registered."""
        mcp_server = get_mcp_server()
        tool_names = set(mcp_server._tool_definitions.keys())

        expected_tools = {
            "add_task",
            "list_tasks",
            "update_task",
            "complete_task",
            "delete_task",
        }

        assert tool_names == expected_tools, \
            f"Missing tools: {expected_tools - tool_names}"

    def test_tool_definitions_complete(self):
        """Verify each tool has complete definition."""
        mcp_server = get_mcp_server()

        for tool_name, tool_def in mcp_server._tool_definitions.items():
            # Has name
            assert tool_def.name, f"{tool_name}: missing name"

            # Has description
            assert tool_def.description, f"{tool_name}: missing description"
            assert len(tool_def.description) > 10, f"{tool_name}: description too short"

            # Has input schema
            assert tool_def.input_schema, f"{tool_name}: missing input_schema"
            assert "properties" in tool_def.input_schema, \
                f"{tool_name}: invalid schema format"

    def test_openai_format_correct(self):
        """Verify OpenAI SDK format is correct."""
        mcp_server = get_mcp_server()
        tools = mcp_server.get_tools_for_ai()

        for tool in tools:
            # Check structure
            assert "type" in tool, "Missing 'type' field"
            assert tool["type"] == "function", "Type must be 'function'"

            assert "function" in tool, "Missing 'function' field"
            func = tool["function"]

            assert "name" in func, "Missing 'name' in function"
            assert "description" in func, "Missing 'description' in function"
            assert "parameters" in func, "Missing 'parameters' in function"


class TestSchemaCorrectness:
    """Test schema definitions are correct."""

    def test_input_schemas_have_descriptions(self):
        """Verify input schemas have field descriptions."""
        from app.mcp.schemas import (
            AddTaskInput,
            ListTasksInput,
            UpdateTaskInput,
            CompleteTaskInput,
            DeleteTaskInput,
        )

        schemas = [
            AddTaskInput,
            ListTasksInput,
            UpdateTaskInput,
            CompleteTaskInput,
            DeleteTaskInput,
        ]

        for schema in schemas:
            json_schema = schema.model_json_schema()
            properties = json_schema.get("properties", {})

            for field_name, field_def in properties.items():
                assert "description" in field_def, \
                    f"{schema.__name__}.{field_name} missing description"

    def test_output_schemas_consistent(self):
        """Verify output schemas have consistent structure."""
        from app.mcp.schemas import (
            AddTaskOutput,
            ListTasksOutput,
            UpdateTaskOutput,
            CompleteTaskOutput,
            DeleteTaskOutput,
        )

        outputs = [
            AddTaskOutput,
            ListTasksOutput,
            UpdateTaskOutput,
            CompleteTaskOutput,
            DeleteTaskOutput,
        ]

        for output_schema in outputs:
            schema = output_schema.model_json_schema()
            properties = schema.get("properties", {})

            # All outputs should have 'success'
            assert "success" in properties, \
                f"{output_schema.__name__} missing 'success' field"

            # All outputs should have 'message'
            assert "message" in properties, \
                f"{output_schema.__name__} missing 'message' field"


class TestLayerSeparation:
    """Test clean layer separation."""

    def test_no_fastapi_in_mcp_tools(self):
        """Verify MCP tools don't import FastAPI."""
        tools_file = Path("app/mcp/tools.py")
        source = tools_file.read_text()

        forbidden_imports = [
            "from fastapi import",
            "import fastapi",
            "HTTPException",
            "Depends",
            "Request",
            "Response",
        ]

        for forbidden in forbidden_imports:
            assert forbidden not in source, \
                f"MCP tools contain forbidden FastAPI import: {forbidden}"

    def test_no_fastapi_in_mcp_server(self):
        """Verify MCP server doesn't import FastAPI."""
        server_file = Path("app/mcp/server.py")
        source = server_file.read_text()

        forbidden_imports = [
            "from fastapi import",
            "import fastapi",
        ]

        for forbidden in forbidden_imports:
            assert forbidden not in source, \
                f"MCP server contains forbidden FastAPI import: {forbidden}"

    def test_fastapi_routes_use_mcp_server(self):
        """Verify FastAPI routes use MCP server (not direct imports)."""
        chat_file = Path("app/api/routes/chat.py")
        source = chat_file.read_text()

        # Should import get_mcp_server
        assert "from app.mcp import get_mcp_server" in source or \
               "from app.mcp import" in source and "get_mcp_server" in source, \
            "Chat route should import get_mcp_server"

        # Should NOT import tools directly
        forbidden_imports = [
            "from app.mcp.tools import add_task",
            "from app.mcp.tools import list_tasks",
            "from app.mcp.tools import update_task",
            "from app.mcp.tools import complete_task",
            "from app.mcp.tools import delete_task",
        ]

        for forbidden in forbidden_imports:
            assert forbidden not in source, \
                f"Chat route contains direct tool import: {forbidden}"


def test_run_compliance_suite():
    """Run full MCP compliance test suite."""
    pytest.main([__file__, "-v"])
```

---

## 6. Manual Review Checklist

### Code Review Template

Use this checklist when reviewing MCP implementation:

```markdown
## MCP Architecture Review

### Stateless Design
- [ ] No module-level database sessions
- [ ] No global caches or variables
- [ ] All tools use `with Session(engine)` pattern
- [ ] No shared state between tool invocations
- [ ] Tools are deterministic (same input → same output)

### Tool Registration
- [ ] All 5 CRUD tools registered in `get_tool_definitions()`
- [ ] Tool registry maps all tools to functions
- [ ] OpenAI SDK format correct (`type: function`, `function.parameters`)
- [ ] Tool descriptions are clear and actionable
- [ ] No duplicate tool names

### Schema Correctness
- [ ] All input schemas have field descriptions
- [ ] Length/range constraints present where needed
- [ ] All output schemas have `success`, `message`, `error` fields
- [ ] Schemas align with tool function signatures
- [ ] Examples provided in schemas

### Layer Separation
- [ ] No `from fastapi import` in MCP modules
- [ ] No `HTTPException` in MCP tools
- [ ] FastAPI routes use `get_mcp_server()` API
- [ ] No direct tool imports in routes
- [ ] Clean dependency flow maintained

### Documentation
- [ ] Tool docstrings explain purpose
- [ ] Schema docstrings explain usage
- [ ] Examples in code comments
- [ ] README updated with MCP architecture

**Reviewer**: _______________
**Date**: _______________
**Status**: ☐ Approved ☐ Changes Requested
```

---

## 7. Common Violations and Remediation

### Violation 1: Stateful Tool (Global Session)

**Problem**:
```python
# ❌ Global session
session = Session(engine)

def add_task(input_data: AddTaskInput):
    session.add(...)
    session.commit()
```

**Fix**:
```python
# ✅ Fresh session per call
def add_task(input_data: AddTaskInput):
    engine = get_engine()
    with Session(engine) as session:
        session.add(...)
        session.commit()
```

---

### Violation 2: Missing Tool Registration

**Problem**:
```python
# Only 3 tools registered
def get_tool_definitions():
    return [
        MCPToolDefinition(name="add_task", ...),
        MCPToolDefinition(name="list_tasks", ...),
        MCPToolDefinition(name="delete_task", ...),
        # Missing: update_task, complete_task
    ]
```

**Fix**:
```python
# All 5 tools registered
def get_tool_definitions():
    return [
        MCPToolDefinition(name="add_task", ...),
        MCPToolDefinition(name="list_tasks", ...),
        MCPToolDefinition(name="update_task", ...),        # Added
        MCPToolDefinition(name="complete_task", ...),      # Added
        MCPToolDefinition(name="delete_task", ...),
    ]
```

---

### Violation 3: Schema Mismatch

**Problem**:
```python
# Schema defines one thing
class AddTaskInput(BaseModel):
    title: str
    description: str

# Tool expects different structure
def add_task(data: dict):  # ❌ Not using schema
    title = data.get("taskTitle")  # ❌ Different field name
```

**Fix**:
```python
# Schema and tool aligned
class AddTaskInput(BaseModel):
    title: str
    description: str

def add_task(input_data: AddTaskInput):  # ✅ Use schema
    title = input_data.title  # ✅ Direct access
```

---

### Violation 4: FastAPI in MCP Layer

**Problem**:
```python
# backend/app/mcp/tools.py
from fastapi import HTTPException  # ❌

def add_task(input_data: AddTaskInput):
    if not input_data.title:
        raise HTTPException(400, "Invalid")  # ❌
```

**Fix**:
```python
# backend/app/mcp/tools.py
# No FastAPI imports

def add_task(input_data: AddTaskInput) -> AddTaskOutput:
    if not input_data.title:
        return AddTaskOutput(
            success=False,
            error="Title required"  # ✅ Return error
        )
```

---

## 8. Continuous Compliance

### Pre-Commit Hook

**File**: `.git/hooks/pre-commit`

```bash
#!/bin/bash

echo "Running MCP compliance checks..."

# Run compliance tests
pytest backend/tests/test_mcp_compliance.py -v

if [ $? -ne 0 ]; then
    echo "❌ MCP compliance tests failed"
    exit 1
fi

echo "✅ MCP compliance verified"
exit 0
```

### CI/CD Integration

**File**: `.github/workflows/mcp-compliance.yml`

```yaml
name: MCP Compliance

on: [push, pull_request]

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run MCP compliance tests
        run: |
          cd backend
          pytest tests/test_mcp_compliance.py -v

      - name: Check for violations
        run: |
          if grep -r "from fastapi import" app/mcp/; then
            echo "❌ Found FastAPI imports in MCP layer"
            exit 1
          fi
```

---

## Implementation Checklist

- [ ] Create compliance test file: `tests/test_mcp_compliance.py`
- [ ] Run stateless design tests
- [ ] Run tool registration tests
- [ ] Run schema correctness tests
- [ ] Run layer separation tests
- [ ] Perform manual code review using checklist
- [ ] Fix any detected violations
- [ ] Re-run tests to verify fixes
- [ ] Set up pre-commit hook
- [ ] Configure CI/CD pipeline
- [ ] Document compliance in README
- [ ] Train team on MCP architecture principles

---

**Skill Version**: 1.0.0
**Last Updated**: 2026-01-19
**Status**: Ready for Implementation
