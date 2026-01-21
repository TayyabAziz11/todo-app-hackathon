# Skill: orchestrate-request-cycle

**Version**: 1.0.0
**Created**: 2026-01-19
**Category**: Phase 3 - Core Orchestration

---

## 1. Purpose

Define and document the complete stateless request lifecycle for the Phase 3 AI Chatbot, orchestrating all components (authentication, conversation persistence, agent runner, MCP tools, database) in a cohesive flow that ensures horizontal scalability, user isolation, and data consistency.

This skill serves as the architectural blueprint for how a single chat request flows through the entire system from HTTP entry to HTTP exit.

---

## 2. Applicable Agents

**Primary Agent**: `chat-api-orchestrator`
- Designs request/response cycles
- Ensures stateless patterns
- Coordinates multi-component flows

**Supporting Agents**:
- `todo-ai-agent-designer` - Agent execution understanding
- `mcp-tool-architect` - Tool invocation patterns
- `conversation-persistence` - Database operations
- `fastapi-backend-architect` - API design review

---

## 3. Input

### Prerequisites
- Chat endpoint implementation (`POST /api/{user_id}/chat`)
- AgentRunner with OpenAI SDK integration
- MCP tools (5 CRUD operations)
- Conversation persistence service
- User authentication system

### Requirements
- Complete request lifecycle definition
- Statelessness guarantees
- Error handling at each step
- Performance optimization points
- Observability hooks

---

## 4. Output

### Complete Request Lifecycle Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                          HTTP Request                                │
│   POST /api/{user_id}/chat                                          │
│   Headers: Authorization: Bearer <jwt_token>                        │
│   Body: {message: "...", conversation_id?: "..."}                   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: Authentication & Authorization                              │
│ ────────────────────────────────────────────────────────────────── │
│ • Validate JWT token                                                │
│ • Extract user from token                                           │
│ • Verify current_user.id == path.user_id                           │
│ • Raise 401 if token invalid                                        │
│ • Raise 403 if user_id mismatch                                     │
│                                                                      │
│ Dependencies: get_current_user(token) -> User                       │
│ Error Handling: HTTPException(401/403)                              │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: Database Session Acquisition                                │
│ ────────────────────────────────────────────────────────────────── │
│ • Create fresh database session (context manager)                   │
│ • Session scoped to request lifecycle                               │
│ • Auto-commit on success, rollback on error                         │
│ • Connection pool management                                         │
│                                                                      │
│ Dependencies: get_session() -> Session                              │
│ Pattern: Dependency injection via FastAPI Depends()                 │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: Conversation Resolution                                     │
│ ────────────────────────────────────────────────────────────────── │
│ IF conversation_id provided:                                        │
│   • Load conversation from DB                                       │
│   • Verify conversation.user_id == current_user.id                 │
│   • Raise 404 if not found or unauthorized                          │
│ ELSE:                                                                │
│   • Create new Conversation(user_id=current_user.id)               │
│   • Generate auto-title: "Chat YYYY-MM-DD HH:MM"                   │
│   • Persist to database                                             │
│   • Commit transaction                                              │
│                                                                      │
│ Output: conversation (Conversation object)                          │
│ Functions: get_conversation(), create_conversation()                │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: Conversation History Loading                                │
│ ────────────────────────────────────────────────────────────────── │
│ • Query messages WHERE conversation_id = conversation.id            │
│ • Order by created_at ASC (chronological)                           │
│ • Transform DB messages to AgentMessage format:                     │
│     - role: str ("user" | "assistant" | "tool")                    │
│     - content: str                                                  │
│     - tool_calls: List[Dict] (parsed from JSON)                    │
│     - tool_call_id: Optional[str]                                   │
│     - name: Optional[str]                                           │
│ • Return list of AgentMessage objects                               │
│                                                                      │
│ Output: history (List[AgentMessage])                                │
│ Function: get_conversation_history(session, conversation_id)        │
│ Performance: Index on (conversation_id, created_at)                 │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: Persist User Message                                        │
│ ────────────────────────────────────────────────────────────────── │
│ • Create Message object:                                            │
│     - conversation_id: conversation.id                              │
│     - role: "user"                                                  │
│     - content: request.message                                      │
│     - created_at: datetime.utcnow()                                 │
│ • Insert into messages table                                        │
│ • Update conversation.updated_at = datetime.utcnow()                │
│ • Commit transaction                                                │
│                                                                      │
│ Function: save_message(session, conversation_id, "user", content)   │
│ Why Before Agent: Ensures user input persisted before processing    │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 6: Agent Context Construction                                  │
│ ────────────────────────────────────────────────────────────────── │
│ • Prepare agent runner configuration:                               │
│     - openai_api_key: settings.OPENAI_API_KEY                      │
│     - model: settings.OPENAI_MODEL (default "gpt-4")               │
│     - temperature: 0.7                                              │
│     - max_tokens: 1000                                              │
│ • Create fresh AgentRunner instance (stateless)                     │
│ • Build agent run parameters:                                       │
│     - user_id: current_user.id (UUID)                              │
│     - user_message: request.message                                 │
│     - conversation_history: history (List[AgentMessage])           │
│     - user_name: current_user.name (optional personalization)      │
│                                                                      │
│ Function: create_agent_runner(...) -> AgentRunner                   │
│ Pattern: Factory function for clean instantiation                   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 7: Agent Execution                                             │
│ ────────────────────────────────────────────────────────────────── │
│ agent_runner.run() performs:                                        │
│                                                                      │
│ 7a. Build Message List                                              │
│     • System prompt (from get_system_prompt())                      │
│     • Conversation history (from Step 4)                            │
│     • Current user message                                          │
│                                                                      │
│ 7b. Get MCP Tools                                                   │
│     • Load from MCP server: get_mcp_server().get_tools_for_ai()   │
│     • Returns OpenAI-compatible tool definitions                    │
│                                                                      │
│ 7c. OpenAI API Call (First)                                         │
│     • client.chat.completions.create(                              │
│         model=model,                                                │
│         messages=messages,                                          │
│         tools=tools,                                                │
│         tool_choice="auto"                                          │
│       )                                                              │
│     • Agent decides which tools to call (if any)                    │
│                                                                      │
│ 7d. Tool Call Execution (if needed)                                 │
│     • For each tool_call in response.tool_calls:                   │
│         - Extract tool_name and arguments                           │
│         - Inject user_id into arguments                             │
│         - Call MCP server: mcp_server.call_tool(name, args)        │
│         - Collect tool results                                      │
│         - Append tool messages to message list                      │
│                                                                      │
│ 7e. OpenAI API Call (Second - if tools used)                        │
│     • Include tool results in messages                              │
│     • Agent synthesizes final response                              │
│                                                                      │
│ Output: AgentResponse(message, tool_calls, usage, finish_reason)    │
│ Error Handling: try/except -> HTTPException(500)                    │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 8: MCP Tool Invocation Details                                 │
│ ────────────────────────────────────────────────────────────────── │
│ For each tool call during Step 7d:                                  │
│                                                                      │
│ 8a. Tool Resolution                                                 │
│     • Lookup tool by name in MCP server registry                    │
│     • Validate tool exists                                          │
│                                                                      │
│ 8b. Input Validation                                                │
│     • Parse arguments JSON string                                   │
│     • Inject user_id: arguments["user_id"] = str(user_id)          │
│     • Validate with Pydantic schema (e.g., AddTaskInput)           │
│                                                                      │
│ 8c. Tool Execution (Stateless)                                      │
│     • Create fresh database session                                 │
│     • Execute tool function (add_task, list_tasks, etc.)           │
│     • Enforce user isolation in queries                             │
│     • Return structured result                                      │
│     • Close database session                                        │
│                                                                      │
│ 8d. Result Collection                                               │
│     • Wrap in MCPToolResult(success, result, error)                │
│     • Log tool call for debugging/observability                     │
│     • Return to agent for synthesis                                 │
│                                                                      │
│ Key Principle: Each tool call is independent and stateless          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 9: Persist Assistant Response                                  │
│ ────────────────────────────────────────────────────────────────── │
│ • Create Message object:                                            │
│     - conversation_id: conversation.id                              │
│     - role: "assistant"                                             │
│     - content: agent_response.message                               │
│     - tool_calls: JSON.dumps(agent_response.tool_calls)            │
│     - created_at: datetime.utcnow()                                 │
│ • Insert into messages table                                        │
│ • Update conversation.updated_at = datetime.utcnow()                │
│ • Commit transaction                                                │
│                                                                      │
│ Function: save_message(session, conversation_id, "assistant", ...)  │
│ Why: Preserve complete conversation for future requests             │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 10: Build HTTP Response                                        │
│ ────────────────────────────────────────────────────────────────── │
│ • Construct ChatResponse object:                                    │
│     - conversation_id: conversation.id (UUID)                       │
│     - message: agent_response.message (str)                         │
│     - tool_calls: agent_response.tool_calls (List[Dict])           │
│     - usage: agent_response.usage (token counts)                    │
│ • Serialize to JSON                                                 │
│ • Set HTTP status 200                                               │
│ • Return to client                                                  │
│                                                                      │
│ Format: {conversation_id, message, tool_calls, usage}               │
│ Validation: Pydantic ChatResponse model                             │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          HTTP Response                               │
│   Status: 200 OK                                                    │
│   Body: {                                                           │
│     "conversation_id": "uuid",                                      │
│     "message": "AI response",                                       │
│     "tool_calls": [...],                                            │
│     "usage": {tokens}                                               │
│   }                                                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Statelessness Guarantees

### What Makes This Flow Stateless

**1. No In-Memory Session State**
- ❌ No global variables for user sessions
- ❌ No in-memory conversation cache
- ❌ No server-side chat state
- ✅ All state loaded from PostgreSQL per request

**2. Fresh Component Instantiation**
- ✅ New database session per request
- ✅ New AgentRunner instance per request
- ✅ New MCP tool sessions per invocation
- ✅ No shared state between requests

**3. Database as Single Source of Truth**
- ✅ Conversations persisted in `conversations` table
- ✅ Messages persisted in `messages` table
- ✅ User data in `users` table
- ✅ Todo data in `todos` table
- ✅ All history loaded from DB, not memory

**4. Horizontal Scalability**
- ✅ Any API instance can handle any request
- ✅ Load balancer can distribute freely
- ✅ No sticky sessions required
- ✅ Auto-scaling friendly

**5. Request Independence**
- ✅ Request N does not depend on Request N-1 being on same server
- ✅ Server crash does not lose conversation state
- ✅ Deployment/restart safe

---

## 6. Error Handling Strategy

### Error Points and Handling

```python
# STEP 1: Authentication
try:
    current_user = get_current_user(token)
except JWTError:
    raise HTTPException(status_code=401, detail="Invalid token")

if current_user.id != user_id:
    raise HTTPException(status_code=403, detail="Forbidden")

# STEP 3: Conversation Resolution
conversation = get_conversation(session, conversation_id, user_id)
if not conversation and conversation_id:
    raise HTTPException(status_code=404, detail="Conversation not found")

# STEP 7: Agent Execution
try:
    agent_response = agent_runner.run(...)
except OpenAIError as e:
    raise HTTPException(status_code=502, detail=f"OpenAI API error: {e}")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Agent failed: {e}")

# Database Operations
try:
    session.commit()
except IntegrityError as e:
    session.rollback()
    raise HTTPException(status_code=409, detail="Database conflict")
```

### Rollback Strategy

**Database Rollback**:
- User message saved before agent run
- If agent fails, user message already persisted
- Assistant message only saved on success
- Conversation remains consistent

**No Rollback Needed For**:
- OpenAI API calls (external, idempotent)
- MCP tool calls (each has own session)

---

## 7. Performance Optimization Points

### Database Query Optimization

```python
# STEP 4: Optimize history loading
# Index: CREATE INDEX idx_messages_conversation_created
#        ON messages(conversation_id, created_at)

# Limit history to prevent unbounded queries
def get_conversation_history(session, conversation_id, limit=100):
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = session.exec(statement).all()
    return list(reversed(messages))  # Return chronological
```

### Connection Pooling

```python
# Database engine configuration
engine = create_engine(
    database_url,
    pool_size=20,           # Base connections
    max_overflow=10,        # Burst capacity
    pool_pre_ping=True,     # Verify connections
    pool_recycle=3600,      # Recycle after 1 hour
)
```

### AgentRunner Caching (Optional)

```python
# Cache expensive OpenAI embeddings if using RAG
# NOT conversation state (that breaks statelessness)

# Example: Cache system prompt
@lru_cache(maxsize=1)
def get_system_prompt():
    return TODO_AGENT_SYSTEM_PROMPT
```

### Async Processing (Future Enhancement)

```python
# Convert to async for I/O parallelization
async def chat(
    user_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    # Parallel DB queries
    conversation, history = await asyncio.gather(
        get_conversation_async(session, conversation_id),
        get_conversation_history_async(session, conversation_id),
    )
```

---

## 8. Observability Hooks

### Logging Points

```python
import logging
logger = logging.getLogger(__name__)

# STEP 3: Conversation resolution
logger.info(f"Chat request for user {user_id}, conv {conversation_id}")

# STEP 7: Agent execution
logger.info(f"Running agent for user {user_id}")
logger.debug(f"History length: {len(history)} messages")

# STEP 8: Tool calls
logger.info(f"Tool call: {tool_name} with args: {arg_keys}")
logger.debug(f"Tool result: {result.success}")

# STEP 9: Response
logger.info(f"Chat response: {len(agent_response.message)} chars, "
            f"{len(agent_response.tool_calls)} tools used")
```

### Metrics Collection

```python
# Prometheus metrics (example)
from prometheus_client import Counter, Histogram

chat_requests_total = Counter('chat_requests_total', 'Total chat requests')
chat_duration_seconds = Histogram('chat_duration_seconds', 'Chat latency')
tool_calls_total = Counter('tool_calls_total', 'Total MCP tool calls', ['tool_name'])
openai_tokens_total = Counter('openai_tokens_total', 'OpenAI token usage', ['type'])

# In endpoint
@chat_duration_seconds.time()
async def chat(...):
    chat_requests_total.inc()
    # ... execution ...
    for tool_call in agent_response.tool_calls:
        tool_calls_total.labels(tool_name=tool_call['tool_name']).inc()
    openai_tokens_total.labels(type='prompt').inc(usage['prompt_tokens'])
```

### Tracing (OpenTelemetry)

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@router.post("/{user_id}/chat")
async def chat(...):
    with tracer.start_as_current_span("chat_request") as span:
        span.set_attribute("user_id", str(user_id))
        span.set_attribute("conversation_id", str(conversation_id))

        with tracer.start_as_current_span("load_history"):
            history = get_conversation_history(...)

        with tracer.start_as_current_span("agent_run"):
            response = agent_runner.run(...)

        span.set_attribute("tool_calls_count", len(response.tool_calls))
```

---

## 9. Security Checkpoints

### Defense in Depth

**Layer 1: Network**
- ✅ HTTPS only (no HTTP)
- ✅ CORS configured for known origins
- ✅ Rate limiting on chat endpoint

**Layer 2: Authentication**
- ✅ JWT token validation
- ✅ Token expiry enforcement
- ✅ User extraction from claims

**Layer 3: Authorization**
- ✅ User ID path param matches token user
- ✅ Conversation ownership verification
- ✅ No cross-user data access

**Layer 4: Input Validation**
- ✅ Pydantic request validation
- ✅ Message length limits (max 2000 chars)
- ✅ SQL injection prevention (ORM)

**Layer 5: Tool Isolation**
- ✅ user_id injected into all tool calls
- ✅ Database queries filtered by user_id
- ✅ Tools cannot access other users' data

**Layer 6: Data Protection**
- ✅ API keys in environment (not code)
- ✅ Database credentials in secrets
- ✅ Sensitive logs redacted

---

## 10. Testing Strategy

### Unit Tests

```python
# Test conversation service functions
def test_create_conversation(session, user):
    conv = create_conversation(session, user.id)
    assert conv.user_id == user.id

def test_get_conversation_history(session, conversation):
    save_message(session, conversation.id, "user", "Hello")
    save_message(session, conversation.id, "assistant", "Hi")
    history = get_conversation_history(session, conversation.id)
    assert len(history) == 2
```

### Integration Tests

```python
# Test complete request cycle
def test_chat_new_conversation(client, auth_headers):
    response = client.post(
        "/api/{user_id}/chat",
        json={"message": "Add task to buy milk"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "message" in data

def test_chat_continue_conversation(client, auth_headers, conversation_id):
    response = client.post(
        "/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": "Show my tasks"
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
```

### End-to-End Tests

```python
# Test multi-turn conversation
def test_multi_turn_chat(client, auth_headers):
    # Turn 1: Create task
    resp1 = client.post("/api/{user_id}/chat",
                        json={"message": "Add buy groceries"})
    conv_id = resp1.json()["conversation_id"]

    # Turn 2: List tasks
    resp2 = client.post("/api/{user_id}/chat",
                        json={"conversation_id": conv_id,
                              "message": "What's on my list?"})
    assert "groceries" in resp2.json()["message"].lower()

    # Turn 3: Complete task
    resp3 = client.post("/api/{user_id}/chat",
                        json={"conversation_id": conv_id,
                              "message": "Mark groceries as done"})
    assert "complete" in resp3.json()["message"].lower()
```

---

## 11. Example Trace

### Complete Request Flow with Timings

```
[T+0ms]     POST /api/550e8400.../chat
[T+2ms]     ├─ Validate JWT token ✓
[T+3ms]     ├─ Verify user_id match ✓
[T+5ms]     ├─ Create DB session
[T+15ms]    ├─ Load conversation (ID: 7c9e6679...)
[T+25ms]    ├─ Load conversation history (3 messages)
[T+30ms]    ├─ Save user message ("Show my tasks")
[T+35ms]    ├─ Create AgentRunner
[T+40ms]    ├─ Build message list (5 messages total)
[T+45ms]    ├─ Load MCP tools (5 tools)
[T+50ms]    ├─ OpenAI API call #1
[T+1200ms]  │  └─ Response: tool_calls=[{name: "list_tasks"}]
[T+1205ms]  ├─ Execute MCP tool: list_tasks
[T+1210ms]  │  ├─ Inject user_id
[T+1215ms]  │  ├─ Validate input
[T+1220ms]  │  ├─ Create DB session
[T+1235ms]  │  ├─ Query todos WHERE user_id=...
[T+1250ms]  │  ├─ Return 3 tasks
[T+1255ms]  │  └─ Close DB session
[T+1260ms]  ├─ Append tool result to messages
[T+1265ms]  ├─ OpenAI API call #2
[T+2400ms]  │  └─ Response: "You have 3 tasks: ..."
[T+2405ms]  ├─ Save assistant message
[T+2420ms]  ├─ Build ChatResponse
[T+2425ms]  └─ Return HTTP 200
[T+2430ms]  Total: 2.43 seconds
```

**Breakdown**:
- Auth/DB setup: 50ms
- OpenAI calls: 2.1s (87% of time)
- MCP tool execution: 50ms
- Database operations: 70ms
- Overhead: 160ms

---

## 12. Common Pitfalls to Avoid

### ❌ Anti-Pattern: Server-Side Chat State

```python
# WRONG: Storing conversation in memory
chat_sessions = {}  # Global dict

@router.post("/chat")
def chat(...):
    if user_id not in chat_sessions:
        chat_sessions[user_id] = []  # BAD!
    chat_sessions[user_id].append(message)
```

**Why Wrong**: Not horizontally scalable, lost on restart

### ✅ Correct Pattern: Database State

```python
# RIGHT: Load from database
@router.post("/chat")
def chat(...):
    history = get_conversation_history(session, conversation_id)
    # Use history, discard after request
```

---

### ❌ Anti-Pattern: Reusing AgentRunner

```python
# WRONG: Global agent runner
agent_runner = create_agent_runner(...)  # Module level

@router.post("/chat")
def chat(...):
    return agent_runner.run(...)  # Shared state!
```

**Why Wrong**: May leak conversation between users

### ✅ Correct Pattern: Fresh Instance

```python
# RIGHT: Create per request
@router.post("/chat")
def chat(...):
    agent_runner = create_agent_runner(...)  # Request scoped
    return agent_runner.run(...)
```

---

### ❌ Anti-Pattern: Unbounded History

```python
# WRONG: Load all messages
def get_conversation_history(session, conversation_id):
    return session.exec(select(Message)
                       .where(Message.conversation_id == conversation_id)
                       .all())
```

**Why Wrong**: 1000-message conversation = OOM, slow queries

### ✅ Correct Pattern: Limited History

```python
# RIGHT: Limit with window
def get_conversation_history(session, conversation_id, limit=100):
    return session.exec(select(Message)
                       .where(Message.conversation_id == conversation_id)
                       .order_by(Message.created_at.desc())
                       .limit(limit)
                       .all())[::-1]  # Reverse to chronological
```

---

## 13. Future Enhancements

### Streaming Responses

```python
# SSE (Server-Sent Events) for real-time streaming
@router.post("/chat/stream")
async def chat_stream(...):
    async for chunk in agent_runner.run_stream(...):
        yield f"data: {json.dumps(chunk)}\n\n"
```

### Conversation Summarization

```python
# Compress old messages to stay within token limits
def get_conversation_history_with_summary(session, conversation_id):
    recent = get_last_n_messages(session, conversation_id, 20)
    older = get_older_messages(session, conversation_id)
    summary = summarize_messages(older)  # LLM call
    return [summary_message] + recent
```

### Multi-Agent Routing

```python
# Route to specialized agents based on intent
if intent == Intent.COMPLEX_QUERY:
    agent_runner = create_analysis_agent()
elif intent == Intent.TASK_MANAGEMENT:
    agent_runner = create_todo_agent()
```

---

## 14. Deployment Checklist

### Pre-Deployment

- [ ] Database migrations applied (`alembic upgrade head`)
- [ ] Environment variables configured (OPENAI_API_KEY, DATABASE_URL)
- [ ] Database indexes created (conversation_id, user_id, created_at)
- [ ] Connection pool sized appropriately
- [ ] Rate limiting configured
- [ ] CORS origins whitelisted
- [ ] Logging level set (INFO in production)
- [ ] Health check endpoint working

### Post-Deployment

- [ ] Monitor error rates (4xx, 5xx)
- [ ] Monitor latency (p50, p95, p99)
- [ ] Monitor OpenAI API costs
- [ ] Monitor database connection pool usage
- [ ] Set up alerts for failures
- [ ] Test chat flow end-to-end
- [ ] Verify conversation persistence
- [ ] Check tool call execution

---

## Orchestration Summary

This skill defines the complete stateless request lifecycle where:

1. **Every request is independent** - No dependency on previous requests being on same server
2. **Database is source of truth** - All state loaded from PostgreSQL
3. **Components are ephemeral** - Fresh instances created per request
4. **User isolation is enforced** - At authentication, authorization, and tool layers
5. **Observability is built-in** - Logging, metrics, and tracing at each step
6. **Errors are handled gracefully** - HTTP status codes and structured responses
7. **Performance is optimized** - Indexes, connection pooling, limited queries

The orchestration ensures the Phase 3 AI Chatbot is production-ready, scalable, and maintainable.

---

**Skill Version**: 1.0.0
**Last Updated**: 2026-01-19
**Status**: Ready for Reference
