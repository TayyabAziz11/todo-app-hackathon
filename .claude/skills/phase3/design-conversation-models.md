# Skill: design-conversation-models

**Version**: 1.0.0
**Created**: 2026-01-19
**Category**: Phase 3 - Database Layer

---

## 1. Purpose

Design SQLModel database models for conversation persistence in Phase 3 AI Chatbot, including `Conversation` for chat sessions and `Message` for individual exchanges. These models enable stateless chat by persisting all conversation history in PostgreSQL, supporting conversation resume, ordering, and user isolation.

This skill provides the complete database schema foundation for chat history management.

---

## 2. Applicable Agents

**Primary Agent**: `conversation-persistence`
- Designs database schemas for chat data
- Implements conversation storage patterns
- Ensures data integrity and relationships

**Supporting Agents**:
- `fastapi-backend-architect` - API integration review
- `chat-api-orchestrator` - Request lifecycle integration

---

## 3. Input

### Requirements
- User association (conversations belong to users)
- Temporal ordering (messages in chronological order)
- Conversation resume capability
- Tool call metadata storage
- Message role support (user, assistant, tool)
- Efficient querying for conversation history

### Existing Models
- `User` model (`backend/app/models/user.py`)
- `Todo` model (`backend/app/models/todo.py`)

---

## 4. Output

### SQLModel Class Definitions

**File**: `backend/app/models/conversation.py`

```python
"""
Database models for conversation persistence.

This module provides SQLModel models for storing chat conversations
and messages in PostgreSQL, enabling stateless chat with full history.
"""

from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List


class Conversation(SQLModel, table=True):
    """
    Represents a chat conversation session.

    A conversation is a container for a series of messages between
    a user and the AI assistant. Each conversation has:
    - A unique identifier
    - An owner (user_id)
    - A title for display
    - Creation and update timestamps

    Conversations support resume functionality - users can return
    to previous conversations and continue the discussion.
    """
    __tablename__ = "conversations"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique conversation identifier"
    )

    # Foreign Keys
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="Owner of this conversation"
    )

    # Attributes
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Human-readable conversation title"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When conversation was created"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When conversation was last updated"
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin"
        }
    )

    user: Optional["User"] = Relationship(back_populates="conversations")

    class Config:
        """SQLModel configuration."""
        arbitrary_types_allowed = True

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, user_id={self.user_id}, title='{self.title}')>"


class Message(SQLModel, table=True):
    """
    Represents a single message in a conversation.

    Messages can have different roles:
    - "user": User input
    - "assistant": AI agent response
    - "tool": Tool call result (for OpenAI function calling)

    Messages preserve the complete conversation history including:
    - Message content (text)
    - Tool calls made by the agent
    - Tool results returned
    - Chronological ordering via created_at

    This enables stateless chat by loading history from database.
    """
    __tablename__ = "messages"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier"
    )

    # Foreign Keys
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        description="Conversation this message belongs to"
    )

    # Message Attributes
    role: str = Field(
        max_length=20,
        nullable=False,
        description="Message role: 'user', 'assistant', or 'tool'"
    )

    content: str = Field(
        default="",
        sa_column_kwargs={"server_default": ""},
        description="Message text content"
    )

    # OpenAI Function Calling Support
    tool_calls: Optional[str] = Field(
        default=None,
        description="JSON string of tool calls made (for assistant messages)"
    )

    tool_call_id: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Tool call ID (for tool result messages)"
    )

    name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Tool name (for tool result messages)"
    )

    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="When message was created (for ordering)"
    )

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    class Config:
        """SQLModel configuration."""
        arbitrary_types_allowed = True

    def __repr__(self) -> str:
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message(id={self.id}, role={self.role}, content='{preview}')>"
```

---

### Model Integration

**File**: `backend/app/models/__init__.py` (update)

```python
"""
Database models for the Todo application.

This module exports all SQLModel models for database operations.
"""

from app.models.user import User
from app.models.todo import Todo
from app.models.conversation import Conversation, Message

__all__ = [
    "User",
    "Todo",
    "Conversation",
    "Message",
]
```

---

### User Model Extension

**File**: `backend/app/models/user.py` (add relationship)

```python
from sqlmodel import Relationship
from typing import List, Optional

class User(SQLModel, table=True):
    # ... existing fields ...

    # Relationships
    todos: List["Todo"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")  # ADD THIS
```

---

### Database Migration

**File**: `backend/alembic/versions/004_add_conversations.py`

```python
"""add conversations and messages tables

Revision ID: 004_add_conversations
Revises: 003_add_todos
Create Date: 2026-01-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '004_add_conversations'
down_revision = '003_add_todos'  # Update to your actual previous revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create conversations and messages tables."""

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            name='fk_conversations_user_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name='pk_conversations')
    )

    # Indexes for conversations
    op.create_index(
        'ix_conversations_user_id',
        'conversations',
        ['user_id']
    )
    op.create_index(
        'ix_conversations_updated_at',
        'conversations',
        ['updated_at']
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False, server_default=''),
        sa.Column('tool_calls', sa.Text(), nullable=True),
        sa.Column('tool_call_id', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['conversation_id'],
            ['conversations.id'],
            name='fk_messages_conversation_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name='pk_messages')
    )

    # Indexes for messages
    op.create_index(
        'ix_messages_conversation_id',
        'messages',
        ['conversation_id']
    )
    op.create_index(
        'ix_messages_created_at',
        'messages',
        ['created_at']
    )
    # Composite index for efficient history queries
    op.create_index(
        'ix_messages_conversation_created',
        'messages',
        ['conversation_id', 'created_at']
    )


def downgrade() -> None:
    """Drop conversations and messages tables."""

    # Drop indexes first
    op.drop_index('ix_messages_conversation_created', table_name='messages')
    op.drop_index('ix_messages_created_at', table_name='messages')
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_table('messages')

    op.drop_index('ix_conversations_updated_at', table_name='conversations')
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
```

---

## 5. Design Rationale

### Key Design Decisions

**1. UUID Primary Keys**
```python
id: UUID = Field(default_factory=uuid4, primary_key=True)
```
- **Why**: Globally unique, suitable for distributed systems
- **Benefit**: No collisions when merging data from multiple sources
- **Tradeoff**: Slightly larger than SERIAL, but better for scalability

**2. Cascade Delete**
```python
sa_relationship_kwargs={"cascade": "all, delete-orphan"}
```
- **Why**: When conversation deleted, all messages should be deleted
- **Benefit**: Maintains referential integrity automatically
- **PostgreSQL**: Uses `ON DELETE CASCADE` at database level

**3. Timestamps for Ordering**
```python
created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```
- **Why**: Messages must be displayed in chronological order
- **Benefit**: Index enables fast ORDER BY queries
- **Pattern**: Use `utcnow()` for timezone consistency

**4. Updated Timestamp**
```python
updated_at: datetime = Field(default_factory=datetime.utcnow)
```
- **Why**: Track conversation activity for sorting user's conversation list
- **Benefit**: Recent conversations appear first
- **Update Pattern**: Set `updated_at = datetime.utcnow()` when adding messages

**5. Tool Call JSON Storage**
```python
tool_calls: Optional[str] = Field(default=None)
```
- **Why**: Preserve complete tool call metadata for debugging/transparency
- **Format**: JSON string (PostgreSQL JSONB could be used for querying)
- **Alternative**: Separate `tool_calls` table for normalized storage

**6. Role-Based Messages**
```python
role: str = Field(max_length=20)  # "user" | "assistant" | "tool"
```
- **Why**: OpenAI API requires role-based message format
- **Benefit**: Direct mapping to OpenAI chat completion messages
- **Constraint**: Could use ENUM for type safety

**7. User Isolation**
```python
user_id: UUID = Field(foreign_key="users.id", index=True)
```
- **Why**: Conversations belong to specific users
- **Benefit**: Fast queries: `WHERE user_id = ?`
- **Security**: Enforce ownership at database level

---

## 6. Query Patterns

### Common Operations

**Create New Conversation**
```python
from app.models.conversation import Conversation

conversation = Conversation(
    user_id=user.id,
    title=f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
)
session.add(conversation)
session.commit()
session.refresh(conversation)
```

**Add Message to Conversation**
```python
from app.models.conversation import Message

message = Message(
    conversation_id=conversation.id,
    role="user",
    content="Show me all my tasks"
)
session.add(message)

# Update conversation timestamp
conversation.updated_at = datetime.utcnow()
session.add(conversation)

session.commit()
```

**Get Conversation History (Ordered)**
```python
from sqlmodel import select

# Get all messages in chronological order
statement = (
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.asc())
)
messages = session.exec(statement).all()
```

**Get Conversation History (Limited)**
```python
# Get last 100 messages (for performance)
statement = (
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.desc())
    .limit(100)
)
messages = list(reversed(session.exec(statement).all()))
```

**List User's Conversations**
```python
# Get user's conversations, most recent first
statement = (
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.updated_at.desc())
    .limit(50)
)
conversations = session.exec(statement).all()
```

**Get Conversation with Messages (Eager Loading)**
```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

statement = (
    select(Conversation)
    .where(Conversation.id == conversation_id)
    .options(selectinload(Conversation.messages))
)
conversation = session.exec(statement).first()
# conversation.messages is now loaded
```

**Delete Conversation (Cascades to Messages)**
```python
conversation = session.get(Conversation, conversation_id)
if conversation:
    session.delete(conversation)
    session.commit()
    # All related messages are automatically deleted
```

---

## 7. Index Strategy

### Primary Indexes

```sql
-- Conversations
CREATE INDEX ix_conversations_user_id ON conversations(user_id);
CREATE INDEX ix_conversations_updated_at ON conversations(updated_at);

-- Messages
CREATE INDEX ix_messages_conversation_id ON messages(conversation_id);
CREATE INDEX ix_messages_created_at ON messages(created_at);

-- Composite (most important for performance)
CREATE INDEX ix_messages_conversation_created ON messages(conversation_id, created_at);
```

### Index Usage

**1. User's Conversation List**
```sql
-- Uses: ix_conversations_user_id + ix_conversations_updated_at
SELECT * FROM conversations
WHERE user_id = 'uuid'
ORDER BY updated_at DESC
LIMIT 50;
```

**2. Conversation History**
```sql
-- Uses: ix_messages_conversation_created (composite)
SELECT * FROM messages
WHERE conversation_id = 'uuid'
ORDER BY created_at ASC;
```

**3. Recent Activity**
```sql
-- Uses: ix_messages_created_at
SELECT * FROM messages
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

---

## 8. Data Integrity

### Foreign Key Constraints

```python
# Conversation → User
user_id: UUID = Field(foreign_key="users.id")
# ON DELETE CASCADE: When user deleted, conversations deleted

# Message → Conversation
conversation_id: UUID = Field(foreign_key="conversations.id")
# ON DELETE CASCADE: When conversation deleted, messages deleted
```

### Validation Rules

```python
# In application code
def validate_message_role(role: str) -> None:
    """Ensure message role is valid."""
    valid_roles = {"user", "assistant", "tool"}
    if role not in valid_roles:
        raise ValueError(f"Invalid role: {role}. Must be one of {valid_roles}")

# In Pydantic schemas
from pydantic import validator

class MessageCreate(BaseModel):
    role: str
    content: str

    @validator('role')
    def validate_role(cls, v):
        if v not in {"user", "assistant", "tool"}:
            raise ValueError("Invalid role")
        return v
```

---

## 9. Conversation Resume Support

### Resume Flow

**1. User Opens Existing Conversation**
```python
# Frontend sends conversation_id in request
POST /api/{user_id}/chat
{
  "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "message": "Continue previous discussion"
}
```

**2. Backend Loads History**
```python
# Get conversation (verify ownership)
conversation = session.exec(
    select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
).first()

if not conversation:
    raise HTTPException(404, "Conversation not found")

# Load message history
history = session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.asc())
).all()
```

**3. Agent Uses History**
```python
# Convert to AgentMessage format
agent_messages = [
    AgentMessage(
        role=msg.role,
        content=msg.content,
        tool_calls=json.loads(msg.tool_calls) if msg.tool_calls else None,
        tool_call_id=msg.tool_call_id,
        name=msg.name
    )
    for msg in history
]

# Run agent with history
response = agent_runner.run(
    user_id=user_id,
    user_message=request.message,
    conversation_history=agent_messages  # Resume context
)
```

**4. New Messages Appended**
```python
# Save user message
save_message(session, conversation_id, "user", request.message)

# Save assistant response
save_message(session, conversation_id, "assistant", response.message)

# Update conversation timestamp (maintains "recently active" sort)
conversation.updated_at = datetime.utcnow()
session.commit()
```

---

## 10. Example Usage

### Complete Conversation Lifecycle

```python
from app.models.conversation import Conversation, Message
from sqlmodel import Session, select
from datetime import datetime
import json

# 1. Create new conversation
conversation = Conversation(
    user_id=user.id,
    title="Task Management Chat"
)
session.add(conversation)
session.commit()
session.refresh(conversation)
print(f"Created: {conversation.id}")

# 2. Add first user message
msg1 = Message(
    conversation_id=conversation.id,
    role="user",
    content="Show me all my tasks"
)
session.add(msg1)
conversation.updated_at = datetime.utcnow()
session.commit()

# 3. Add assistant response (with tool calls)
tool_calls_json = json.dumps([{
    "tool_name": "list_tasks",
    "arguments": {"user_id": str(user.id)},
    "result": {"success": True, "tasks": [...]}
}])

msg2 = Message(
    conversation_id=conversation.id,
    role="assistant",
    content="You have 3 tasks: Buy groceries, Finish report, Call dentist",
    tool_calls=tool_calls_json
)
session.add(msg2)
conversation.updated_at = datetime.utcnow()
session.commit()

# 4. Resume conversation later
# User returns and sends new message
msg3 = Message(
    conversation_id=conversation.id,
    role="user",
    content="Mark the first task as done"
)
session.add(msg3)

# Load history for agent
history = session.exec(
    select(Message)
    .where(Message.conversation_id == conversation.id)
    .order_by(Message.created_at.asc())
).all()

print(f"Conversation has {len(history)} messages")
# Conversation has 3 messages (2 previous + 1 new)

# 5. List user's active conversations
conversations = session.exec(
    select(Conversation)
    .where(Conversation.user_id == user.id)
    .order_by(Conversation.updated_at.desc())
).all()

for conv in conversations:
    print(f"{conv.title} - Last active: {conv.updated_at}")
```

---

## 11. Performance Considerations

### Query Optimization

**Problem**: Loading 1000-message conversation
```python
# BAD: Unbounded query
messages = session.exec(
    select(Message).where(Message.conversation_id == conv_id)
).all()
```

**Solution**: Limit with window
```python
# GOOD: Limited query
messages = session.exec(
    select(Message)
    .where(Message.conversation_id == conv_id)
    .order_by(Message.created_at.desc())
    .limit(100)  # Last 100 messages only
).all()[::-1]  # Reverse to chronological
```

### Database Connection Pooling

```python
# In app/database.py
from sqlmodel import create_engine

engine = create_engine(
    database_url,
    pool_size=20,           # Base pool size
    max_overflow=10,        # Burst capacity
    pool_pre_ping=True,     # Connection health check
    pool_recycle=3600,      # Recycle connections hourly
    echo=False,             # Disable SQL logging in production
)
```

### Pagination for Large Result Sets

```python
def get_user_conversations_paginated(
    session: Session,
    user_id: UUID,
    page: int = 1,
    page_size: int = 20
) -> List[Conversation]:
    """Get user's conversations with pagination."""
    offset = (page - 1) * page_size
    return session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(page_size)
        .offset(offset)
    ).all()
```

---

## 12. Testing

### Model Tests

```python
# tests/test_conversation_models.py
from app.models.conversation import Conversation, Message
from uuid import uuid4
from datetime import datetime

def test_create_conversation(session, user):
    """Test conversation creation."""
    conv = Conversation(
        user_id=user.id,
        title="Test Chat"
    )
    session.add(conv)
    session.commit()
    session.refresh(conv)

    assert conv.id is not None
    assert conv.user_id == user.id
    assert conv.title == "Test Chat"
    assert isinstance(conv.created_at, datetime)

def test_add_message_to_conversation(session, conversation):
    """Test adding messages."""
    msg = Message(
        conversation_id=conversation.id,
        role="user",
        content="Hello"
    )
    session.add(msg)
    session.commit()
    session.refresh(msg)

    assert msg.id is not None
    assert msg.conversation_id == conversation.id
    assert msg.role == "user"
    assert msg.content == "Hello"

def test_cascade_delete(session, conversation):
    """Test that deleting conversation deletes messages."""
    # Add messages
    for i in range(3):
        msg = Message(
            conversation_id=conversation.id,
            role="user",
            content=f"Message {i}"
        )
        session.add(msg)
    session.commit()

    # Delete conversation
    session.delete(conversation)
    session.commit()

    # Verify messages deleted
    messages = session.exec(
        select(Message).where(Message.conversation_id == conversation.id)
    ).all()
    assert len(messages) == 0

def test_message_ordering(session, conversation):
    """Test messages return in chronological order."""
    import time
    messages_content = ["First", "Second", "Third"]

    for content in messages_content:
        msg = Message(
            conversation_id=conversation.id,
            role="user",
            content=content
        )
        session.add(msg)
        session.commit()
        time.sleep(0.01)  # Ensure different timestamps

    # Query with order by
    ordered = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    ).all()

    assert [m.content for m in ordered] == messages_content
```

---

## 13. Migration Execution

### Running the Migration

```bash
# Generate migration (if using auto-generation)
alembic revision --autogenerate -m "add conversations and messages tables"

# Review generated migration in alembic/versions/

# Run migration
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt conversations"
psql $DATABASE_URL -c "\dt messages"

# Check indexes
psql $DATABASE_URL -c "\di" | grep -E "conversations|messages"
```

### Rollback (if needed)

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade 003_add_todos
```

---

## Implementation Checklist

- [ ] Create `backend/app/models/conversation.py` with Conversation and Message models
- [ ] Update `backend/app/models/__init__.py` to export new models
- [ ] Add `conversations` relationship to User model
- [ ] Create Alembic migration for conversations and messages tables
- [ ] Add indexes: user_id, updated_at, conversation_id, created_at, composite
- [ ] Run migration: `alembic upgrade head`
- [ ] Verify tables and indexes in PostgreSQL
- [ ] Write unit tests for model creation
- [ ] Write tests for cascade delete behavior
- [ ] Write tests for message ordering
- [ ] Test conversation resume flow
- [ ] Document query patterns in code comments

---

**Skill Version**: 1.0.0
**Last Updated**: 2026-01-19
**Status**: Ready for Implementation
