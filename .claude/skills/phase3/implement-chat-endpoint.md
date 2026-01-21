# Skill: implement-chat-endpoint

**Version**: 1.0.0
**Created**: 2026-01-19
**Category**: Phase 3 - API Layer

---

## 1. Purpose

Implement the stateless POST `/api/{user_id}/chat` endpoint that accepts user messages, manages conversation history persistence, orchestrates the AI agent via AgentRunner, and returns structured chat responses with conversation continuity.

This skill bridges the Phase 3 foundation (MCP tools, system prompt, intent classifier, agent runner) with the frontend ChatKit UI by providing a production-ready REST API for chat interactions.

---

## 2. Applicable Agents

**Primary Agent**: `chat-api-orchestrator`
- Designs and implements stateless chat API endpoints
- Integrates conversation history storage
- Connects OpenAI Agent Runner to HTTP layer
- Ensures horizontal scalability

**Supporting Agents**:
- `conversation-persistence` - Database models for chat history
- `test-qa-validator` - Endpoint testing and validation
- `fastapi-backend-architect` - REST API design review

---

## 3. Input

### Required Artifacts
1. **AgentRunner Implementation**: `backend/app/agent/runner.py`
2. **MCP Tools**: `backend/app/mcp/tools.py` (5 CRUD operations)
3. **Database Configuration**: `backend/app/database.py`
4. **User Model**: `backend/app/models/user.py`
5. **Todo Model**: `backend/app/models/todo.py`

### Requirements
- POST `/api/{user_id}/chat` endpoint specification
- Conversation persistence requirements
- Stateless design constraints
- User authentication integration

---

## 4. Output

### Database Models

**File**: `backend/app/models/conversation.py`

```python
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List

class Conversation(SQLModel, table=True):
    """
    Conversation session for a user's chat interactions.

    Each conversation maintains a separate context and history.
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
    user: Optional["User"] = Relationship(back_populates="conversations")


class Message(SQLModel, table=True):
    """
    Individual message in a conversation.

    Stores user inputs, assistant responses, and tool call metadata.
    """
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # "user", "assistant", "tool"
    content: str = Field(default="")
    tool_calls: Optional[str] = Field(default=None)  # JSON string
    tool_call_id: Optional[str] = Field(default=None, max_length=255)
    name: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

### Conversation Service

**File**: `backend/app/services/conversation.py`

```python
from sqlmodel import Session, select
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from app.models.conversation import Conversation, Message
from app.agent.runner import Message as AgentMessage

def create_conversation(session: Session, user_id: UUID, title: Optional[str] = None) -> Conversation:
    """Create a new conversation for a user."""
    conversation = Conversation(
        user_id=user_id,
        title=title or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def get_conversation(session: Session, conversation_id: UUID, user_id: UUID) -> Optional[Conversation]:
    """Get a conversation by ID, ensuring it belongs to the user."""
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )
    return session.exec(statement).first()


def save_message(
    session: Session,
    conversation_id: UUID,
    role: str,
    content: str,
    tool_calls: Optional[str] = None,
    tool_call_id: Optional[str] = None,
    name: Optional[str] = None,
) -> Message:
    """Save a message to a conversation."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls,
        tool_call_id=tool_call_id,
        name=name,
    )
    session.add(message)
    session.commit()
    session.refresh(message)

    # Update conversation timestamp
    conversation = session.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()

    return message


def get_conversation_history(session: Session, conversation_id: UUID) -> List[AgentMessage]:
    """
    Get conversation history as AgentMessage list for AgentRunner.

    Returns messages in chronological order, formatted for agent consumption.
    """
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at)

    db_messages = session.exec(statement).all()

    # Convert to AgentMessage format
    agent_messages = []
    for msg in db_messages:
        import json
        tool_calls = None
        if msg.tool_calls:
            try:
                tool_calls = json.loads(msg.tool_calls)
            except json.JSONDecodeError:
                pass

        agent_messages.append(AgentMessage(
            role=msg.role,
            content=msg.content,
            tool_calls=tool_calls,
            tool_call_id=msg.tool_call_id,
            name=msg.name,
        ))

    return agent_messages


def list_user_conversations(session: Session, user_id: UUID, limit: int = 50) -> List[Conversation]:
    """List all conversations for a user, most recent first."""
    statement = select(Conversation).where(
        Conversation.user_id == user_id
    ).order_by(Conversation.updated_at.desc()).limit(limit)

    return list(session.exec(statement).all())
```

### Chat API Endpoint

**File**: `backend/app/api/routes/chat.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session
from uuid import UUID
from typing import Optional, List, Dict, Any

from app.database import get_session
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.conversation import (
    create_conversation,
    get_conversation,
    save_message,
    get_conversation_history,
)
from app.agent.runner import create_agent_runner, AgentResponse
from app.config import settings
import json

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=2000, description="User's input message")
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID (creates new if not provided)")


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    conversation_id: UUID = Field(..., description="Conversation ID for future messages")
    message: str = Field(..., description="Agent's response")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="Tools used by the agent")
    usage: Dict[str, int] = Field(default_factory=dict, description="Token usage statistics")


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ChatResponse:
    """
    Stateless chat endpoint for AI-powered task management.

    This endpoint:
    1. Verifies user authorization
    2. Loads or creates conversation
    3. Fetches conversation history from database
    4. Runs AI agent with AgentRunner
    5. Saves user message and agent response to database
    6. Returns structured response with conversation_id

    **Statelessness**:
    - No in-memory session state
    - All history loaded from PostgreSQL
    - Fresh AgentRunner instance per request
    - Any API instance can handle any request

    **User Isolation**:
    - Conversation belongs to authenticated user
    - AgentRunner injects user_id into all tool calls
    - Tools enforce user ownership on all operations
    """
    # 1. Verify authorization
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's chat"
        )

    # 2. Load or create conversation
    conversation = None
    if request.conversation_id:
        conversation = get_conversation(session, request.conversation_id, user_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {request.conversation_id} not found"
            )
    else:
        # Create new conversation
        conversation = create_conversation(session, user_id)

    # 3. Fetch conversation history
    history = get_conversation_history(session, conversation.id)

    # 4. Save user message
    save_message(
        session=session,
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )

    # 5. Run AI agent
    agent_runner = create_agent_runner(
        openai_api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL or "gpt-4",
        temperature=0.7,
        max_tokens=1000,
    )

    try:
        agent_response: AgentResponse = agent_runner.run(
            user_id=user_id,
            user_message=request.message,
            conversation_history=history,
            user_name=current_user.name,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )

    # 6. Save assistant response
    # If there were tool calls, save the assistant message with tool_calls
    # then save each tool result, then save the final response
    if agent_response.tool_calls:
        # This is handled internally by AgentRunner - it makes multiple API calls
        # We just save the final assistant response
        pass

    save_message(
        session=session,
        conversation_id=conversation.id,
        role="assistant",
        content=agent_response.message,
        tool_calls=json.dumps(agent_response.tool_calls) if agent_response.tool_calls else None,
    )

    # 7. Return response
    return ChatResponse(
        conversation_id=conversation.id,
        message=agent_response.message,
        tool_calls=agent_response.tool_calls,
        usage=agent_response.usage,
    )
```

### Router Integration

**File**: `backend/app/api/routes/__init__.py` (update)

```python
from app.api.routes import auth, todos, chat

# Export routers
__all__ = ["auth", "todos", "chat"]
```

**File**: `backend/app/main.py` (update)

```python
from app.api.routes import auth, todos, chat

# Include chat router
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(chat.router)  # Add this line
```

### Configuration Updates

**File**: `backend/app/config.py` (add OpenAI settings)

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")

    class Config:
        env_file = ".env"
```

**File**: `backend/.env.example` (add)

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4  # Optional: gpt-4, gpt-3.5-turbo, etc.
```

### Database Migration

**File**: `backend/alembic/versions/xxx_add_conversations.py`

```python
"""add conversations and messages tables

Revision ID: xxx
Revises: yyy
Create Date: 2026-01-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'xxx'
down_revision = 'yyy'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', sa.Text(), nullable=True),
        sa.Column('tool_call_id', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])

def downgrade() -> None:
    op.drop_index('ix_messages_conversation_id')
    op.drop_table('messages')
    op.drop_index('ix_conversations_user_id')
    op.drop_table('conversations')
```

---

## 5. Scope & Boundaries

### In Scope
✅ Conversation and Message database models
✅ Conversation persistence service functions
✅ POST `/api/{user_id}/chat` endpoint implementation
✅ AgentRunner integration with conversation history
✅ User authorization and conversation ownership enforcement
✅ Stateless design (no session memory)
✅ Database migration for new tables
✅ Error handling for agent failures

### Out of Scope
❌ WebSocket/streaming responses (use HTTP POST only)
❌ Conversation title auto-generation from content
❌ Message editing or deletion
❌ Conversation search or filtering
❌ Rate limiting implementation
❌ Frontend ChatKit integration (separate skill)
❌ Conversation export functionality

### Design Constraints
- **Statelessness**: No in-memory session state between requests
- **User Isolation**: Conversations belong to users; enforce ownership on all operations
- **Database as Source of Truth**: All history loaded from PostgreSQL
- **Horizontal Scalability**: Any API instance can handle any request
- **Tool Call Transparency**: Return tool_calls list in response for debugging

---

## 6. Reusability Notes

This skill creates reusable components:

1. **Conversation Models** - Can be extended for:
   - Conversation sharing between users
   - Conversation templates
   - Conversation analytics

2. **Conversation Service** - Reusable functions for:
   - Listing conversations
   - Deleting conversations
   - Exporting conversation history

3. **Chat Endpoint Pattern** - Template for:
   - Other AI agent endpoints
   - Streaming chat endpoints
   - Multi-agent chat systems

### Extension Points
- Add `conversation.metadata` JSON field for custom tags
- Add `message.metadata` for client-side rendering hints
- Add `conversation.shared_with` for collaboration features
- Add `message.feedback` for thumbs up/down ratings

---

## 7. Dependencies

### Code Dependencies
- `backend/app/agent/runner.py` - AgentRunner for AI orchestration
- `backend/app/mcp/server.py` - MCP tools for task operations
- `backend/app/models/user.py` - User model for authentication
- `backend/app/auth/dependencies.py` - get_current_user dependency
- `backend/app/database.py` - Database session management
- `backend/app/config.py` - Settings including OPENAI_API_KEY

### External Dependencies
- SQLModel for ORM
- FastAPI for routing
- OpenAI SDK (already in agent runner)
- Alembic for migrations

### Environment Variables
```bash
OPENAI_API_KEY=sk-...  # Required
OPENAI_MODEL=gpt-4     # Optional (defaults to gpt-4)
```

---

## 8. Quality Expectations

### Code Quality
- ✅ Type hints on all functions
- ✅ Docstrings on all public functions
- ✅ Pydantic validation on request/response
- ✅ Proper error handling with HTTP status codes
- ✅ Database transaction management (commit/rollback)

### Security
- ✅ User authorization (current_user.id == user_id)
- ✅ Conversation ownership enforcement
- ✅ Input validation (max message length)
- ✅ SQL injection prevention (SQLModel ORM)
- ✅ API key in environment (not hardcoded)

### Performance
- ✅ Database indexes on foreign keys
- ✅ Conversation history limit (prevent unbounded queries)
- ✅ Efficient message ordering (created_at index)
- ✅ Single database session per request

### Testability
- ✅ Service functions separated from endpoint
- ✅ Dependency injection (session, current_user)
- ✅ Unit testable conversation service
- ✅ Integration testable endpoint with test database

---

## 9. Example Use Case

### Scenario: User Creates and Continues a Chat

**Step 1: User sends first message (new conversation)**

```bash
POST /api/550e8400-e29b-41d4-a716-446655440000/chat
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "message": "Show me all my tasks"
}
```

**Response**:
```json
{
  "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "message": "You have 3 tasks:\n\n1. Buy groceries (incomplete)\n2. Finish project report (incomplete)\n3. Call dentist (completed)\n\nWould you like to filter by status or add a new task?",
  "tool_calls": [
    {
      "tool_name": "list_tasks",
      "arguments": {"user_id": "550e8400-e29b-41d4-a716-446655440000"},
      "result": {"success": true, "tasks": [...]}
    }
  ],
  "usage": {
    "prompt_tokens": 450,
    "completion_tokens": 85,
    "total_tokens": 535
  }
}
```

**Step 2: User continues conversation**

```bash
POST /api/550e8400-e29b-41d4-a716-446655440000/chat
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "message": "Mark task 1 as done"
}
```

**Response**:
```json
{
  "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "message": "I've marked 'Buy groceries' as complete. Great job! You now have 1 completed task and 1 remaining task.",
  "tool_calls": [
    {
      "tool_name": "complete_task",
      "arguments": {"user_id": "550e8400-...", "task_id": 1},
      "result": {"success": true, "task": {...}}
    }
  ],
  "usage": {
    "prompt_tokens": 580,
    "completion_tokens": 45,
    "total_tokens": 625
  }
}
```

### Database State After Step 2

**conversations table**:
```
id                                   | user_id                              | title              | created_at          | updated_at
7c9e6679-7425-40de-944b-e07fc1f90ae7 | 550e8400-e29b-41d4-a716-446655440000 | Chat 2026-01-19... | 2026-01-19 10:00:00 | 2026-01-19 10:02:15
```

**messages table**:
```
id   | conversation_id | role      | content                  | tool_calls | created_at
...  | 7c9e6679...     | user      | "Show me all my tasks"   | null       | 10:00:00
...  | 7c9e6679...     | assistant | "You have 3 tasks..."    | [{"tool... | 10:00:02
...  | 7c9e6679...     | user      | "Mark task 1 as done"    | null       | 10:02:14
...  | 7c9e6679...     | assistant | "I've marked 'Buy gro... | [{"tool... | 10:02:15
```

---

## 10. Testing Strategy

### Unit Tests

**Test conversation service functions**:

```python
# tests/test_conversation_service.py
def test_create_conversation(session, user):
    conv = create_conversation(session, user.id)
    assert conv.user_id == user.id
    assert conv.title.startswith("Chat")

def test_save_and_get_history(session, conversation):
    save_message(session, conversation.id, "user", "Hello")
    save_message(session, conversation.id, "assistant", "Hi there!")

    history = get_conversation_history(session, conversation.id)
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[1].role == "assistant"

def test_conversation_ownership(session, user1, user2, conversation1):
    # conversation1 belongs to user1
    result = get_conversation(session, conversation1.id, user2.id)
    assert result is None  # User2 cannot access user1's conversation
```

### Integration Tests

**Test chat endpoint flow**:

```python
# tests/test_chat_endpoint.py
def test_chat_new_conversation(client, auth_headers):
    response = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Add task to buy milk"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "Buy milk" in data["message"].lower()
    assert len(data["tool_calls"]) > 0

def test_chat_continue_conversation(client, auth_headers, conversation_id):
    response = client.post(
        f"/api/{user_id}/chat",
        json={
            "conversation_id": conversation_id,
            "message": "Show my tasks"
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] == conversation_id

def test_chat_unauthorized_conversation(client, user1_headers, user2_conversation):
    response = client.post(
        f"/api/{user1_id}/chat",
        json={
            "conversation_id": user2_conversation.id,
            "message": "Hello"
        },
        headers=user1_headers,
    )
    assert response.status_code == 404  # Conversation not found
```

---

## Implementation Checklist

- [ ] Create `backend/app/models/conversation.py` with Conversation and Message models
- [ ] Create `backend/app/services/conversation.py` with persistence functions
- [ ] Create `backend/app/api/routes/chat.py` with POST endpoint
- [ ] Update `backend/app/api/routes/__init__.py` to export chat router
- [ ] Update `backend/app/main.py` to include chat router
- [ ] Update `backend/app/config.py` with OPENAI_API_KEY and OPENAI_MODEL
- [ ] Update `backend/.env.example` with OpenAI settings
- [ ] Create Alembic migration for conversations and messages tables
- [ ] Run migration: `alembic upgrade head`
- [ ] Write unit tests for conversation service
- [ ] Write integration tests for chat endpoint
- [ ] Test with Postman/curl for manual verification
- [ ] Update API documentation with chat endpoint

---

**Skill Version**: 1.0.0
**Last Updated**: 2026-01-19
**Status**: Ready for Implementation
