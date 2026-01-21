# Data Model Design: AI-Powered Todo Chatbot (Phase 3)

**Feature**: `003-phase3-ai-chatbot`
**Created**: 2026-01-21
**Status**: Design Complete
**Purpose**: Define database schemas for conversation persistence and task management in stateless architecture

---

## Overview

This data model extends the existing Phase 1/2 database schema with two new entities to support stateless AI chatbot functionality:

1. **Conversation**: Represents a chat session between user and AI agent
2. **Message**: Individual messages within a conversation (user or assistant)

**Existing Entities** (from Phase 1/2 - no modifications):
- **User**: User accounts and authentication
- **Task**: Todo items with title, description, completion status

**Design Principles**:
- ✅ **Stateless Architecture**: Database is the ONLY source of truth
- ✅ **User Isolation**: All entities scoped to user_id with FK constraints
- ✅ **Chronological Ordering**: Messages indexed for efficient conversation retrieval
- ✅ **Conversation Resume**: Full history loadable after server restart

---

## Entity 1: Conversation

### Purpose

Represents a persistent chat session between a user and the AI assistant. Each conversation has a unique ID that serves as the ONLY state token passed between client and server.

### SQLModel Schema

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique conversation identifier (UUIDv4)"
    )

    # Foreign Keys
    user_id: str = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Owner of this conversation (FK to users table)"
    )

    # Attributes
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional conversation title (e.g., 'Task Planning Session')"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When conversation was created"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last message timestamp (updated on each message)"
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        cascade_delete=True,
        description="All messages in this conversation"
    )
```

### Database Constraints

**Primary Key**:
- `id` (UUID): Unique conversation identifier

**Foreign Keys**:
- `user_id` → `users.id` (ON DELETE CASCADE)

**Indexes**:
- `idx_conversations_user_id` on `user_id` (for listing user's conversations)
- `idx_conversations_updated_at` on `updated_at` (for sorting by recency)

**NOT NULL Constraints**:
- `id`, `user_id`, `created_at`, `updated_at`

**Cascade Rules**:
- When conversation is deleted → all child messages are deleted (CASCADE)
- When user is deleted → all conversations are deleted (CASCADE)

### State Transitions

```
[New Conversation]
    ↓
[Active] ← messages being added
    ↓
[Archived] (future enhancement - not Phase 3 MVP)
```

**Phase 3 MVP**: Conversations remain in "active" state; archival is out of scope.

### Business Rules

1. **User Ownership**: Each conversation belongs to exactly one user
2. **Immutable ID**: Conversation ID never changes after creation
3. **Updated Timestamp**: Auto-updated whenever a message is added
4. **Title Optional**: Title can be null (system may auto-generate based on first message in future)

---

## Entity 2: Message

### Purpose

Represents a single message in a conversation. Messages are immutable after creation and ordered chronologically to reconstruct conversation history for agent context.

### SQLModel Schema

```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique message identifier (UUIDv4)"
    )

    # Foreign Keys
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        description="Parent conversation (FK to conversations table)"
    )

    user_id: str = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User who owns this conversation (denormalized for isolation)"
    )

    # Attributes
    role: str = Field(
        nullable=False,
        max_length=20,
        description="Message sender role: 'user' or 'assistant'"
    )

    content: str = Field(
        nullable=False,
        description="Message text content"
    )

    tool_calls: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="JSON array of MCP tool calls made by agent (if role=assistant)"
    )

    tool_call_id: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Tool call identifier for OpenAI SDK (if message is tool result)"
    )

    name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Tool name if message is a tool result"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Message timestamp for chronological ordering"
    )

    # Relationships
    conversation: Conversation = Relationship(
        back_populates="messages",
        description="Parent conversation"
    )
```

### Database Constraints

**Primary Key**:
- `id` (UUID): Unique message identifier

**Foreign Keys**:
- `conversation_id` → `conversations.id` (ON DELETE CASCADE)
- `user_id` → `users.id` (ON DELETE CASCADE)

**Indexes** (CRITICAL for performance):
- `idx_messages_conversation_created` on `(conversation_id, created_at)` **COMPOSITE INDEX**
  - Enables efficient chronological message retrieval
  - Most common query: "Get all messages for conversation X ordered by time"
- `idx_messages_user_id` on `user_id` (for user isolation enforcement)

**NOT NULL Constraints**:
- `id`, `conversation_id`, `user_id`, `role`, `content`, `created_at`

**CHECK Constraints** (application-level validation):
- `role` IN ('user', 'assistant', 'tool')

**Cascade Rules**:
- When conversation is deleted → all messages are deleted (CASCADE)
- When user is deleted → all messages are deleted (CASCADE)

### State Transitions

Messages are **immutable** after creation:

```
[Message Created] → [Persisted] (no state changes)
```

**No updates or deletions**: Messages are append-only for conversation integrity.

### Business Rules

1. **Immutability**: Messages cannot be edited after creation
2. **Chronological Order**: Messages ordered by `created_at` ascending
3. **Role Validation**: `role` must be 'user', 'assistant', or 'tool'
4. **User Isolation**: `user_id` denormalized for fast isolation checks
5. **Tool Calls**: Only assistant messages can have tool_calls (JSON array)
6. **Tool Results**: Tool result messages have `tool_call_id` and `name` fields

### Message Roles

**Role: `user`**
- Content: User's natural language input
- tool_calls: null
- Example: "Add a task to buy groceries"

**Role: `assistant`**
- Content: Agent's response text
- tool_calls: JSON array of MCP tool invocations (if any)
- Example: "I've created the task 'Buy groceries' for you."

**Role: `tool`** (for tool results, if needed by OpenAI SDK)
- Content: Tool execution result
- tool_call_id: Links to assistant's tool_call
- name: Tool name (e.g., "add_task")

---

## Entity 3: Task (Existing - Reference Only)

### Purpose

Existing entity from Phase 1. MCP tools will query and modify this table.

### Schema Reference

```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int = Field(primary_key=True)
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(nullable=False, max_length=255)
    description: Optional[str] = None
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**No modifications needed**: MCP tools will perform CRUD operations on existing schema.

---

## Entity 4: User (Existing - Reference Only)

### Purpose

Existing entity from Phase 2 (Better Auth integration). No modifications needed.

### Schema Reference

```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True)  # Better Auth user ID
    email: str = Field(nullable=False, unique=True)
    # ... other Better Auth fields
```

**No modifications needed**: Authentication handled by Better Auth from Phase 2.

---

## Relationships Diagram

```
┌──────────┐
│  User    │
│          │
│ id (PK)  │
│ email    │
└─────┬────┘
      │ 1
      │
      │ Has Many
      │
      ├──────────────────────────────────────┐
      │                                      │
      │ N                                    │ N
┌─────┴─────────────┐              ┌────────┴──────────┐
│  Conversation     │              │      Task         │
│                   │              │                   │
│ id (PK)          │              │ id (PK)           │
│ user_id (FK)     │              │ user_id (FK)      │
│ title            │              │ title             │
│ created_at       │              │ completed         │
│ updated_at       │              │ created_at        │
└─────┬─────────────┘              └───────────────────┘
      │ 1
      │
      │ Has Many
      │
      │ N
┌─────┴─────────────┐
│    Message        │
│                   │
│ id (PK)          │
│ conversation_id  │
│ user_id (FK)     │
│ role             │
│ content          │
│ tool_calls       │
│ created_at       │
└───────────────────┘
```

---

## Migration Strategy

### Alembic Migration

**File**: `alembic/versions/xxx_add_conversation_tables.py`

**Changes**:
1. Create `conversations` table with indexes
2. Create `messages` table with composite index
3. Add foreign key constraints
4. Add cascade delete rules

**Backward Compatibility**: New tables are additive; existing Phase 1/2 functionality unaffected.

**Rollback**: Drop `messages` table first (due to FK), then `conversations` table.

### Migration Command

```bash
# Generate migration
alembic revision --autogenerate -m "add conversation tables"

# Review generated SQL
alembic show xxx

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

---

## Query Patterns

### Get Conversation History (Most Common Query)

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

**Index Used**: `idx_messages_conversation_created` (composite)

**Performance**: O(log N + K) where K = limit
- Index seek on conversation_id
- Sequential scan of sorted messages (limited)

### Create New Conversation

```python
def create_conversation(user_id: str, title: Optional[str] = None):
    with Session(engine) as db:
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation
```

### Save Message

```python
def save_message(
    conversation_id: UUID,
    user_id: str,
    role: str,
    content: str,
    tool_calls: Optional[dict] = None
):
    with Session(engine) as db:
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        db.add(message)

        # Update conversation timestamp
        conversation = db.get(Conversation, conversation_id)
        conversation.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(message)
        return message
```

### List User Conversations

```python
def list_user_conversations(user_id: str, limit: int = 20):
    with Session(engine) as db:
        conversations = db.query(Conversation)\
            .filter(Conversation.user_id == user_id)\
            .order_by(Conversation.updated_at.desc())\
            .limit(limit)\
            .all()
        return conversations
```

**Index Used**: `idx_conversations_user_id` + `idx_conversations_updated_at`

---

## Stateless Architecture Validation

### Conversation Resume After Restart

**Scenario**: Backend server restarts mid-conversation

**Flow**:
1. User sends new message with `conversation_id` from previous session
2. Server (fresh instance, no memory) receives request
3. Server loads conversation history from database via `get_conversation_history(conversation_id)`
4. Server formats messages for agent context
5. Server runs agent with full history
6. Server saves new messages to database
7. Server returns response

**Proof of Statelessness**: No in-memory state required; conversation continues seamlessly.

### Horizontal Scaling Validation

**Scenario**: Multiple backend instances behind load balancer

**Flow**:
1. User sends message 1 → routed to Instance A
2. Instance A loads history, runs agent, saves response
3. User sends message 2 → routed to Instance B
4. Instance B loads SAME history from database, runs agent
5. Both instances operate independently with shared database as truth

**Proof of Horizontal Scalability**: Any instance can handle any request; no sticky sessions needed.

---

## Performance Considerations

### Index Strategy

1. **Composite Index**: `(conversation_id, created_at)`
   - Single index covers most common query pattern
   - Avoids separate seeks on both columns
   - Enables efficient chronological message retrieval

2. **User Isolation Index**: `user_id`
   - Fast enforcement of user data boundaries
   - Required for listing conversations per user

3. **Updated Timestamp Index**: `updated_at`
   - Enables sorting conversations by recency
   - Used in "recent conversations" queries

### Conversation Length Limits

**Phase 3 MVP**: No conversation length limits enforced.

**Future Optimization** (post-MVP):
- Truncate to last N messages (e.g., 50) for agent context
- Implement pagination for very long conversations
- Add summarization for conversations exceeding token limits

**Current Approach**: Load full conversation history (acceptable for MVP with typical conversation lengths < 100 messages).

### Database Connection Pooling

**Pattern**: FastAPI lifespan context manager

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create connection pool
    app.state.db_pool = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
    yield
    # Shutdown: close pool
    app.state.db_pool.dispose()

app = FastAPI(lifespan=lifespan)
```

**Request-Scoped Sessions**:
```python
def get_db_session():
    with Session(engine) as session:
        yield session
        # Auto-closes after request
```

---

## Security Considerations

### User Isolation Enforcement

**Database Level**:
- Every query MUST filter by `user_id`
- Foreign key constraints prevent cross-user data access

**Application Level**:
- JWT token validation extracts `user_id`
- Path parameter `{user_id}` MUST match token user_id
- All MCP tools receive and validate `user_id`

**Example** (enforcing isolation):
```python
def get_conversation(conversation_id: UUID, user_id: str):
    with Session(engine) as db:
        conversation = db.query(Conversation)\
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id  # CRITICAL: user isolation
            )\
            .first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return conversation
```

### Cascade Delete Rules

**Conversation Deletion**:
- When user is deleted → all conversations deleted (CASCADE)
- When conversation is deleted → all messages deleted (CASCADE)

**Rationale**: Complete data removal for GDPR compliance and data hygiene.

---

## Data Model Summary

| Entity | Purpose | Key Attributes | Relationships |
|--------|---------|----------------|---------------|
| **Conversation** | Chat session container | id, user_id, title, timestamps | Has many Messages, belongs to User |
| **Message** | Individual chat message | id, conversation_id, role, content, tool_calls | Belongs to Conversation |
| **Task** | Todo item (existing) | id, user_id, title, completed | Belongs to User (no direct link to Conversation) |
| **User** | User account (existing) | id, email | Has many Conversations and Tasks |

**State Token**: `conversation_id` (UUID) is the ONLY state passed between client and server.

**Source of Truth**: PostgreSQL database; no in-memory state.

**Scalability**: Horizontally scalable (stateless servers + shared database).

---

**Design Status**: ✅ COMPLETE - Ready for implementation in Phase 2 (Foundational Tasks)

**Next Artifact**: Chat API Contract Specification (`contracts/chat-api.yaml`)
