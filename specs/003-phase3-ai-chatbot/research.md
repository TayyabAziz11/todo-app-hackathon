# Phase 3 Research & Technical Decisions

**Feature**: AI-Powered Todo Chatbot (Phase 3)
**Date**: 2026-01-21
**Status**: Complete
**Purpose**: Document technical research findings to inform implementation decisions

---

## Research Area 1: OpenAI Agents SDK (T001)

### Stateless Agent Instantiation Patterns

**Key Findings**:

The OpenAI Agents SDK supports **three execution approaches** for stateless operation:

1. **Async execution** via `Runner.run()` returning a `RunResult`
2. **Synchronous execution** via `Runner.run_sync()`
3. **Streaming execution** via `Runner.run_streamed()` for real-time LLM event access

**Basic Agent Creation** (Stateless by Default):
```python
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant"
)
```

Agents are stateless by default unless explicitly configured with session storage. Each agent instantiation is independent.

### Conversation History Management

The SDK provides **three approaches** for managing conversation context:

1. **Manual Context Management** (Recommended for Phase 3):
   - Use `RunResultBase.to_input_list()` to convert previous responses into input format
   - Chain turns explicitly by collecting outputs and resubmitting as input for next response
   - **Advantage**: Full control over statelessness, database as source of truth
   - **Pattern**: Load messages from DB → format to input list → run agent → save to DB

2. **Session-based** (Not recommended for stateless requirement):
   - `SQLiteSession` or `SQLAlchemy`-powered sessions automatically retrieve/store history
   - Violates stateless architecture requirement

3. **Server-managed** (Alternative approach):
   - Use OpenAI's Conversations API with `conversation_id` or `previous_response_id`
   - Requires reliance on OpenAI's hosted storage

**Decision for Phase 3**: Use **Manual Context Management** pattern to maintain full statelessness.

### Tool Attachment Patterns

The SDK supports two primary tool integration methods:

1. **Function tools**: Turn any Python function into a tool with automatic schema generation
2. **MCP server tool calling**: Built-in MCP server tool integration

**Integration Pattern**:
```python
# Tools are attached to agent during instantiation or runtime
agent = Agent(
    name="TodoAssistant",
    instructions="...",
    tools=[tool1, tool2, tool3]  # MCP tools attached here
)
```

### Error Handling

Domain-specific exceptions raised by the SDK:

- **`MaxTurnsExceeded`**: When interaction limits are breached
- **`ModelBehaviorError`**: For malformed LLM outputs
- **`InputGuardrailTripwireTriggered`**: Safety conditions on input
- **`OutputGuardrailTripwireTriggered`**: Safety conditions on output

**Decision**: Wrap agent execution in try-except blocks to catch these exceptions and return user-friendly error messages.

### Agent Loop Mechanics

The runner follows a repeating cycle:
1. Calls the LLM
2. Processes output (final_output, handoffs, or tool calls)
3. Either terminates (if final output with desired type and no tool calls) or continues

**Implementation Note**: Tool calls trigger continuation; final text output without tool calls terminates the loop.

**Sources**:
- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [Running Agents - OpenAI Agents SDK](https://openai.github.io/openai-agents-python/running_agents/)
- [Sessions - OpenAI Agents SDK](https://openai.github.io/openai-agents-python/sessions/)
- [GitHub - openai/openai-agents-python](https://github.com/openai/openai-agents-python)

---

## Research Area 2: Official MCP SDK (T002)

### MCP Server Initialization

**Pattern**: Use `FastMCP` for decorator-based tool registration.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Test Server", json_response=True)

# Launch server
mcp.run(transport="streamable-http")
```

**Decision**: Initialize MCP server during FastAPI lifespan startup event to ensure tools are registered before first request.

### Tool Registration and Schema Definition

**Decorator-Based Registration**:
```python
@mcp.tool()
def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Add a new task for the user"""
    # Implementation
    return {"success": True, "task": {...}}
```

**Schema Format**:
Tools use JSON Schema format for `inputSchema`:

```python
Tool(
    name="add_task",
    description="Add a new task for the user",
    inputSchema={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "User identifier"},
            "title": {"type": "string", "description": "Task title"},
            "description": {"type": "string", "description": "Task description (optional)"}
        },
        "required": ["user_id", "title"]
    }
)
```

**Automatic Schema Generation**: The SDK uses `func_metadata` to introspect Python function signatures and automatically generate JSON schemas from type hints and docstrings.

**Decision**: Use `@mcp.tool()` decorator with typed parameters and docstrings for automatic schema generation.

### Stateless Tool Execution Requirements

**Critical Pattern**: Tools MUST NOT maintain state between invocations.

**Database Access Pattern** (Stateless):
```python
@mcp.tool()
def list_tasks(user_id: str, status: str = "all") -> dict:
    """List tasks for a user"""
    # Use context manager for database session (stateless)
    with get_db_session() as db:
        tasks = db.query(Task).filter(Task.user_id == user_id).all()
        return {"success": True, "tasks": [task.dict() for task in tasks]}
    # Session closes automatically, no state retained
```

**Anti-Pattern** (Stateful - DO NOT USE):
```python
# WRONG: Module-level database session
db_session = create_db_session()  # Shared state across requests

@mcp.tool()
def list_tasks(user_id: str) -> dict:
    tasks = db_session.query(Task).all()  # Uses shared session
    return {"success": True, "tasks": tasks}
```

**Decision**: All MCP tools MUST use database context managers, not module-level sessions.

### Error Response Structure

**Structured Response Pattern**:
```python
# Success response
{"success": True, "data": {...}}

# Error response
{"success": False, "error": "Task not found"}
```

**Decision**: All tools return `{"success": bool, "data"?: any, "error"?: string}` for consistency.

### Tool Discovery

Clients discover available tools through:
- **`tools/list` endpoint**: Returns all registered tools with schemas
- **`tools/call` endpoint**: Invokes specific tool by name

**Integration with OpenAI Agents SDK**: Tools registered with MCP server are automatically discoverable by agents through built-in MCP integration.

**Sources**:
- [MCP Server - Model Context Protocol Python SDK](https://modelcontextprotocol.github.io/python-sdk/)
- [GitHub - modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [Tools – Model Context Protocol](https://modelcontextprotocol.info/docs/concepts/tools/)

---

## Research Area 3: Hugging Face Spaces Deployment (T003)

### Port Configuration

**Required Port**: `7860` (default for Hugging Face Spaces)

**Dockerfile CMD**:
```dockerfile
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

**Alternative Configuration**: Set `app_port: 7860` in README.md metadata to change exposed port.

**Decision**: Configure FastAPI to listen on `0.0.0.0:7860` via environment variable for flexibility.

### Environment Variables

**Critical Limitation**: You can ONLY write to the `/tmp` directory in Spaces.

**Required Cache Redirects**:
```dockerfile
ENV NUMBA_CACHE_DIR=/tmp/numba_cache
ENV TRANSFORMERS_CACHE=/tmp/hf_cache/transformers
ENV TORCH_HOME=/tmp/hf_cache/torch
ENV HF_HUB_CACHE=/tmp/hf_cache/hub
```

**Custom Environment Variables**:
- Configure via Space settings → Variables & secrets tab
- Access in Python: `os.environ.get("VARIABLE_NAME")`

**Required Variables for Phase 3**:
- `DATABASE_URL`: Neon PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for agent
- `BETTER_AUTH_SECRET`: JWT signing secret
- `PORT`: Optional override for 7860 default

**Decision**: Document all required environment variables in `.env.example` with Hugging Face-specific notes.

### Startup Command

**Standard Pattern**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

**With Reload** (development only):
```bash
uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload
```

**Decision**: Use standard uvicorn command without reload for production deployment.

### Resource Limits

**Important Limitations**:
- Model files in `/tmp` are temporary and redownload each session
- Persistent caching is NOT possible in Spaces
- Limited to `/tmp` directory for writes

**Decision**: Accept temporary storage limitation; database (Neon PostgreSQL) is persistent and external.

### Docker Configuration

**Dockerfile Structure**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Redirect caches to /tmp
ENV TRANSFORMERS_CACHE=/tmp/hf_cache/transformers
ENV TORCH_HOME=/tmp/hf_cache/torch

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

**Decision**: Create Dockerfile with Python 3.11-slim base image and proper cache configuration.

**Sources**:
- [Deploying Your FastAPI Applications on Huggingface Via Docker](https://huggingface.co/blog/HemanthSai7/deploy-applications-on-huggingface-spaces)
- [🚀 Deploying a FastAPI App on Hugging Face Spaces — and Handling All Its Restrictions](https://medium.com/@na.mazaheri/deploying-a-fastapi-app-on-hugging-face-spaces-and-handling-all-its-restrictions-d494d97a78fa)
- [Docker Spaces - Hugging Face](https://huggingface.co/docs/hub/en/spaces-sdks-docker)

---

## Research Area 4: OpenAI ChatKit Integration (T004)

### Domain Allowlist Configuration (CRITICAL)

**The Most Important Setup Step**: ChatKit widgets will NOT render if your domain is not explicitly allowed.

**Symptom**: Console shows no errors, network tab shows successful API calls, session creation returns 200 OK, but widget doesn't render.

**Solution**:
1. Go to https://platform.openai.com/settings/organization/security/domain-allowlist
2. Add your production domain (e.g., `your-app.vercel.app`)
3. Add `localhost` for local development (NOTE: localhost cannot be added to dashboard, special handling required)

**Localhost Workaround**: Localhost is not a verified domain and cannot be added to the allowed domain list, causing issues during local development.

**Decision**: Document domain allowlist setup as REQUIRED step in quickstart guide. Add production domain before deployment.

### Next.js 15 Integration

**Installation**:
```bash
npm install @openai/chatkit
```

**Basic Integration Pattern**:
```typescript
import { useChatKit } from '@openai/chatkit';

function ChatInterface() {
  const { session, sendMessage } = useChatKit({
    getClientSecret: async () => {
      // Fetch client secret from your backend
      const response = await fetch('/api/chat/session');
      return response.json();
    }
  });

  // Handle messages
  const handleSend = async (message: string) => {
    await sendMessage(message);
  };

  return <ChatKitComponent session={session} onSend={handleSend} />;
}
```

**Key Configuration Points**:
- API key must be from same organization and project as Agent Builder workflow
- `getClientSecret` is the recommended approach (backend handles auth, OpenAI handles rest)
- ChatKit works with Next.js, React, or vanilla JavaScript

**Decision**: Use `getClientSecret` pattern with backend endpoint for session creation.

### Environment Variables

**Required**:
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`: Domain verification key from OpenAI dashboard

**Decision**: Add to `frontend/.env.local.example` with setup instructions.

### Agent Builder vs Custom Backend

**Two Approaches**:

1. **Agent Builder Workflow** (OpenAI-hosted):
   - ChatKit connects to OpenAI-hosted agent
   - Workflow defined in OpenAI dashboard
   - Less control, easier setup

2. **Custom Backend** (Recommended for Phase 3):
   - ChatKit connects to your FastAPI backend
   - Custom agent logic with MCP tools
   - Full control, stateless architecture

**Decision**: Use custom backend approach with POST /api/{user_id}/chat endpoint.

### Session Management

**Pattern**: ChatKit manages session lifecycle, but conversation_id must be persisted client-side.

```typescript
// Store conversation_id in sessionStorage
sessionStorage.setItem('conversation_id', conversationId);

// Retrieve on page load
const savedConversationId = sessionStorage.getItem('conversation_id');
```

**Decision**: Persist conversation_id in sessionStorage for page refresh resume.

**Sources**:
- [OpenAI ChatKit + Next.js: Complete Integration Guide](https://www.buildwithmatija.com/blog/chatkit-nextjs-integration)
- [Getting Started with OpenAI ChatKit: The One Setup Step You Can't Skip](https://medium.com/@mcraddock/getting-started-with-openai-chatkit-the-one-setup-step-you-cant-skip-7d4c0110404a)
- [ChatKit | OpenAI API](https://platform.openai.com/docs/guides/chatkit)
- [Domain verification for hosted integration · Issue #62 · openai/chatkit-js](https://github.com/openai/chatkit-js/issues/62)

---

## Research Area 5: Stateless Conversation Management (T005)

### Recommended Pattern: External Database (PostgreSQL)

**Architecture**: Agent pods/servers are stateless with all state persisted to managed database (PostgreSQL on Neon).

**Key Benefits**:
- Simple, scalable, and durable
- Easier to scale and deploy (any instance can handle any request)
- Stateless servers don't store session data between requests

**Pattern for Phase 3**:
```
Request arrives
    ↓
Load conversation history from PostgreSQL
    ↓
Format messages for agent context
    ↓
Run agent with full history
    ↓
Save agent response to PostgreSQL
    ↓
Return response to client
    ↓
(No state retained in server memory)
```

### Database Schema Pattern

**Conversation Table**:
```python
class Conversation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Message Table**:
```python
class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="users.id")
    role: str  # "user" or "assistant"
    content: str
    tool_calls: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

**Critical Index**: Composite index on `(conversation_id, created_at)` for efficient chronological message retrieval.

### Connection Pool Management

**FastAPI Pattern**: Use lifespan context manager for database connection pool.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create connection pool
    app.state.db_pool = create_db_pool()
    yield
    # Shutdown: close connection pool
    app.state.db_pool.close()

app = FastAPI(lifespan=lifespan)
```

**Request-Level Sessions**:
```python
from fastapi import Depends
from sqlmodel import Session

def get_db_session():
    with Session(engine) as session:
        yield session
        # Session closes automatically after request
```

**Anti-Pattern**: Don't share a connection, share the connection pool. Pass pool to every route via `request.state` or dependency injection.

**Decision**: Use FastAPI lifespan for pool management and dependency injection for request-scoped sessions.

### Message Ordering

**Query Pattern**:
```python
def get_conversation_history(conversation_id: UUID, limit: int = 50):
    with Session(engine) as db:
        messages = db.query(Message)\
            .filter(Message.conversation_id == conversation_id)\
            .order_by(Message.created_at.asc())\
            .limit(limit)\
            .all()
        return messages
```

**Decision**: Order by `created_at ASC` for chronological agent context.

### Conversation Resume Pattern

**Flow**:
1. Client sends `conversation_id` with new message
2. Server loads all messages for conversation_id from DB
3. Server formats messages for agent (user/assistant turns)
4. Server runs agent with full context
5. Server saves new user message and agent response
6. Server returns response with same conversation_id

**Server Restart Verification**: After restart, server has no memory, but can still load conversation from DB and continue seamlessly.

**Decision**: conversation_id is the ONLY state token passed between client and server.

**Sources**:
- [How to Build an Agentic Chatbot with FastAPI and PostgreSQL](https://www.orfium.com/engineering/how-to-build-an-agentic-chatbot-with-fastapi-and-postgresql/)
- [State Management Patterns for Long-Running AI Agents](https://dev.to/inboryn_99399f96579fcd705/state-management-patterns-for-long-running-ai-agents-redis-vs-statefulsets-vs-external-databases-39c5)
- [Building Stateful Conversations with Postgres and LLMs](https://medium.com/@levi_stringer/building-stateful-conversations-with-postgres-and-llms-e6bb2a5ff73e)
- [FastAPI: SQL Databases Tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/)

---

## Research Area 6: Better Auth JWT Integration (T006)

### JWT Token Validation Pattern

**Standard FastAPI Pattern**:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(
            token.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### User ID Extraction

**Token Payload Structure** (Better Auth):
```json
{
  "sub": "user_id_here",
  "email": "user@example.com",
  "iat": 1234567890,
  "exp": 1234567890
}
```

**Extraction Pattern**:
```python
# Extract user_id from "sub" claim
user_id = payload.get("sub")

# Validate it exists
if not user_id:
    raise HTTPException(status_code=401, detail="Token missing user ID")
```

### Path Parameter Verification

**Critical Security Check**: Verify `{user_id}` path parameter matches JWT token user_id.

```python
@app.post("/api/{user_id}/chat")
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    token_user_id: str = Depends(get_current_user)
):
    # Verify path parameter matches token
    if user_id != token_user_id:
        raise HTTPException(status_code=403, detail="Forbidden: User ID mismatch")

    # Proceed with authorized request
    ...
```

**Decision**: Always verify path parameter user_id matches token user_id to prevent unauthorized access.

### Libraries

**Recommended**:
- `python-jose[cryptography]`: JWT encoding/decoding
- `passlib[bcrypt]`: Password hashing (if needed)

**Installation**:
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

**Decision**: Use `python-jose` for JWT validation (industry standard for FastAPI).

### Error Response Codes

**Authentication Errors**:
- `401 Unauthorized`: Invalid/missing/expired token
- `403 Forbidden`: Valid token but user_id mismatch (authorization failure)

**Pattern**:
```python
# 401: Token invalid
raise HTTPException(status_code=401, detail="Invalid authentication token")

# 403: Token valid but wrong user
raise HTTPException(status_code=403, detail="Forbidden: Cannot access other user's data")
```

**Decision**: Use standard HTTP status codes for auth errors.

### Integration with Better Auth

**Note**: Better Auth is a frontend authentication library. The backend receives JWT tokens that Better Auth generates.

**Backend Responsibilities**:
1. Validate JWT signature using shared secret
2. Verify token expiration
3. Extract user_id from token payload
4. Enforce user_id matching in endpoints

**Frontend Responsibilities** (Better Auth):
1. Handle user login/logout
2. Store JWT token
3. Send JWT token in Authorization header
4. Refresh tokens when expired

**Decision**: Backend treats Better Auth tokens as standard JWT tokens; no special Better Auth SDK needed on backend.

**Sources**:
- [Securing FastAPI with JWT Token-based Authentication](https://testdriven.io/blog/fastapi-jwt-auth/)
- [FastAPI Security Essentials: Using OAuth2 and JWT](https://medium.com/@suganthi2496/fastapi-security-essentials-using-oauth2-and-jwt-for-authentication-7e007d9d473c)
- [OAuth2 with Password (and hashing), Bearer with JWT tokens - FastAPI](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Authentication and Authorization with FastAPI: A Complete Guide](https://betterstack.com/community/guides/scaling-python/authentication-fastapi/)

---

## Summary of Decisions

### Phase 3 Architecture Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **Agent Pattern** | Manual context management with stateless agent instantiation | Full control over conversation history, database as source of truth |
| **MCP Tools** | Decorator-based registration with automatic schema generation | Simplifies tool definition, ensures JSON Schema compliance |
| **Conversation Storage** | PostgreSQL with connection pooling and request-scoped sessions | Scalable, durable, supports horizontal scaling |
| **Deployment Platform** | Hugging Face Spaces on port 7860 with `/tmp` cache redirects | Required by specification, free tier available |
| **Frontend UI** | OpenAI ChatKit with custom backend | Full control over agent logic while leveraging ChatKit UX |
| **Authentication** | JWT validation with python-jose, user_id path parameter verification | Industry standard, compatible with Better Auth |
| **Session Management** | conversation_id as only state token, persisted in sessionStorage | True statelessness, conversation resume after restart |

### Critical Constraints Identified

1. **Hugging Face Spaces**: Only `/tmp` directory is writable; all caches must redirect there
2. **ChatKit Domain Allowlist**: Production domain MUST be added before deployment or widget won't render
3. **Stateless Requirement**: NO module-level database sessions, NO in-memory caches
4. **User Isolation**: All MCP tools MUST validate user ownership before write operations
5. **Connection Pooling**: Use FastAPI lifespan for pool, dependency injection for sessions

### Unknown/Uncertain Areas

1. **OpenAI Agents SDK + MCP SDK Integration**: Official documentation shows MCP support, but exact integration pattern needs validation during implementation
2. **ChatKit Custom Backend**: Exact API contract between ChatKit and custom backend needs clarification (likely SSE streaming)
3. **Hugging Face Spaces Resource Limits**: Exact memory/CPU limits not documented; may need testing

**Recommendation**: Proceed to Phase 1 (Design Artifacts) to create detailed schemas and contracts based on these research findings. Unknown areas will be validated during Phase 2 (Foundational Implementation).

---

**Research Complete**: 2026-01-21
**Next Phase**: Phase 1 - Design Artifacts (T007-T011)
