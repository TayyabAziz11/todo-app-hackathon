# Skill: implement-message-storage

**Version**: 1.0.0
**Created**: 2026-01-19
**Category**: Phase 3 - Service Layer

---

## 1. Purpose

Implement message persistence service functions for Phase 3 AI Chatbot conversation storage. This skill provides stateless service layer functions for creating conversations, saving messages (user and assistant), retrieving conversation history in chronological order, and managing multiple conversations per user.

All operations are database-backed with no in-memory caching, ensuring horizontal scalability and conversation resume capability.

---

## 2. Applicable Agents

**Primary Agent**: `conversation-persistence`
- Implements conversation storage logic
- Ensures stateless persistence patterns
- Manages message chronological ordering

**Supporting Agents**:
- `chat-api-orchestrator` - Endpoint integration
- `test-qa-validator` - Service function testing

---

## 3. Input

### Prerequisites
- Conversation and Message models (`backend/app/models/conversation.py`)
- Database session management (`backend/app/database.py`)
- User model with relationships
- Alembic migrations applied

### Requirements
- Store user messages with role="user"
- Store assistant messages with role="assistant"
- Preserve chronological order via timestamps
- Support tool call metadata storage
- Support multiple conversations per user
- No in-memory caching (stateless)

---

## 4. Output

### Service Module

**File**: `backend/app/services/conversation.py`

```python
"""
Conversation persistence service.

Provides stateless functions for managing conversations and messages
in PostgreSQL, enabling conversation resume and multi-conversation support.

All functions operate directly on the database with no in-memory caching.
"""

from sqlmodel import Session, select
from uuid import UUID
from typing import List, Optional
from datetime import datetime
import json
import logging

from app.models.conversation import Conversation, Message
from app.agent.runner import Message as AgentMessage

logger = logging.getLogger(__name__)


# ============================================================================
# Conversation Management
# ============================================================================

def create_conversation(
    session: Session,
    user_id: UUID,
    title: Optional[str] = None
) -> Conversation:
    """
    Create a new conversation for a user.

    Args:
        session: Database session
        user_id: Owner of the conversation
        title: Optional conversation title (auto-generated if not provided)

    Returns:
        Created Conversation object with id assigned

    Example:
        >>> conversation = create_conversation(session, user.id)
        >>> print(conversation.id)
        UUID('7c9e6679-7425-40de-944b-e07fc1f90ae7')
    """
    if title is None:
        title = f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"

    conversation = Conversation(
        user_id=user_id,
        title=title,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    logger.info(f"Created conversation {conversation.id} for user {user_id}")
    return conversation


def get_conversation(
    session: Session,
    conversation_id: UUID,
    user_id: UUID
) -> Optional[Conversation]:
    """
    Get a conversation by ID, verifying it belongs to the user.

    Args:
        session: Database session
        conversation_id: Conversation to retrieve
        user_id: User who must own the conversation

    Returns:
        Conversation if found and owned by user, None otherwise

    Security:
        Enforces conversation ownership - users cannot access
        other users' conversations.

    Example:
        >>> conv = get_conversation(session, conv_id, user.id)
        >>> if conv:
        ...     print(f"Found: {conv.title}")
        ... else:
        ...     print("Not found or unauthorized")
    """
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )
    conversation = session.exec(statement).first()

    if conversation:
        logger.debug(f"Retrieved conversation {conversation_id} for user {user_id}")
    else:
        logger.warning(f"Conversation {conversation_id} not found for user {user_id}")

    return conversation


def list_user_conversations(
    session: Session,
    user_id: UUID,
    limit: int = 50
) -> List[Conversation]:
    """
    List all conversations for a user, most recent first.

    Args:
        session: Database session
        user_id: User whose conversations to list
        limit: Maximum number of conversations to return (default 50)

    Returns:
        List of Conversation objects ordered by updated_at descending

    Example:
        >>> conversations = list_user_conversations(session, user.id, limit=10)
        >>> for conv in conversations:
        ...     print(f"{conv.title} - {conv.updated_at}")
    """
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    )

    conversations = list(session.exec(statement).all())
    logger.debug(f"Listed {len(conversations)} conversations for user {user_id}")
    return conversations


def delete_conversation(
    session: Session,
    conversation_id: UUID,
    user_id: UUID
) -> bool:
    """
    Delete a conversation and all its messages (cascade).

    Args:
        session: Database session
        conversation_id: Conversation to delete
        user_id: User who must own the conversation

    Returns:
        True if deleted, False if not found or not owned

    Note:
        All messages in the conversation are automatically deleted
        due to CASCADE delete constraint.

    Example:
        >>> if delete_conversation(session, conv_id, user.id):
        ...     print("Deleted successfully")
    """
    conversation = get_conversation(session, conversation_id, user_id)
    if not conversation:
        return False

    session.delete(conversation)
    session.commit()

    logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
    return True


# ============================================================================
# Message Storage
# ============================================================================

def save_message(
    session: Session,
    conversation_id: UUID,
    role: str,
    content: str,
    tool_calls: Optional[str] = None,
    tool_call_id: Optional[str] = None,
    name: Optional[str] = None,
) -> Message:
    """
    Save a message to a conversation.

    Args:
        session: Database session
        conversation_id: Conversation to add message to
        role: Message role ("user", "assistant", or "tool")
        content: Message text content
        tool_calls: Optional JSON string of tool calls (for assistant messages)
        tool_call_id: Optional tool call ID (for tool result messages)
        name: Optional tool name (for tool result messages)

    Returns:
        Created Message object with id assigned

    Side Effects:
        Updates conversation.updated_at to current time

    Example:
        >>> # Save user message
        >>> msg = save_message(
        ...     session,
        ...     conversation_id=conv.id,
        ...     role="user",
        ...     content="Show me all my tasks"
        ... )

        >>> # Save assistant message with tool calls
        >>> tool_calls_json = json.dumps([{...}])
        >>> msg = save_message(
        ...     session,
        ...     conversation_id=conv.id,
        ...     role="assistant",
        ...     content="You have 3 tasks...",
        ...     tool_calls=tool_calls_json
        ... )
    """
    # Create message
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls,
        tool_call_id=tool_call_id,
        name=name,
        created_at=datetime.utcnow(),
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

    logger.debug(
        f"Saved {role} message to conversation {conversation_id}: "
        f"{content[:50]}..."
    )

    return message


def save_user_message(
    session: Session,
    conversation_id: UUID,
    content: str
) -> Message:
    """
    Save a user message (convenience wrapper).

    Args:
        session: Database session
        conversation_id: Conversation to add message to
        content: User's input text

    Returns:
        Created Message object

    Example:
        >>> msg = save_user_message(session, conv.id, "Hello")
        >>> assert msg.role == "user"
    """
    return save_message(
        session=session,
        conversation_id=conversation_id,
        role="user",
        content=content,
    )


def save_assistant_message(
    session: Session,
    conversation_id: UUID,
    content: str,
    tool_calls: Optional[List[dict]] = None
) -> Message:
    """
    Save an assistant message (convenience wrapper).

    Args:
        session: Database session
        conversation_id: Conversation to add message to
        content: Assistant's response text
        tool_calls: Optional list of tool call dictionaries

    Returns:
        Created Message object

    Example:
        >>> msg = save_assistant_message(
        ...     session,
        ...     conv.id,
        ...     "Task created successfully",
        ...     tool_calls=[{"tool_name": "add_task", ...}]
        ... )
        >>> assert msg.role == "assistant"
    """
    tool_calls_json = None
    if tool_calls:
        tool_calls_json = json.dumps(tool_calls)

    return save_message(
        session=session,
        conversation_id=conversation_id,
        role="assistant",
        content=content,
        tool_calls=tool_calls_json,
    )


# ============================================================================
# Message Retrieval
# ============================================================================

def get_conversation_history(
    session: Session,
    conversation_id: UUID,
    limit: Optional[int] = None
) -> List[AgentMessage]:
    """
    Get conversation history formatted for AgentRunner.

    Args:
        session: Database session
        conversation_id: Conversation to retrieve messages from
        limit: Optional maximum number of recent messages to return

    Returns:
        List of AgentMessage objects in chronological order

    Performance:
        - If limit provided, fetches last N messages in reverse order,
          then reverses list to get chronological
        - Uses composite index on (conversation_id, created_at)

    Example:
        >>> history = get_conversation_history(session, conv.id, limit=100)
        >>> for msg in history:
        ...     print(f"{msg.role}: {msg.content}")
    """
    if limit:
        # Get last N messages in descending order, then reverse
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        db_messages = list(reversed(session.exec(statement).all()))
    else:
        # Get all messages in ascending order
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        db_messages = list(session.exec(statement).all())

    # Convert to AgentMessage format
    agent_messages = []
    for msg in db_messages:
        # Parse tool_calls JSON if present
        tool_calls = None
        if msg.tool_calls:
            try:
                tool_calls = json.loads(msg.tool_calls)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse tool_calls for message {msg.id}")
                tool_calls = None

        agent_messages.append(AgentMessage(
            role=msg.role,
            content=msg.content,
            tool_calls=tool_calls,
            tool_call_id=msg.tool_call_id,
            name=msg.name,
        ))

    logger.debug(
        f"Retrieved {len(agent_messages)} messages for conversation {conversation_id}"
    )

    return agent_messages


def get_message_count(
    session: Session,
    conversation_id: UUID
) -> int:
    """
    Get total number of messages in a conversation.

    Args:
        session: Database session
        conversation_id: Conversation to count messages for

    Returns:
        Total message count

    Example:
        >>> count = get_message_count(session, conv.id)
        >>> print(f"Conversation has {count} messages")
    """
    from sqlalchemy import func

    statement = (
        select(func.count(Message.id))
        .where(Message.conversation_id == conversation_id)
    )
    count = session.exec(statement).one()
    return count


def get_latest_messages(
    session: Session,
    conversation_id: UUID,
    limit: int = 10
) -> List[Message]:
    """
    Get the most recent messages from a conversation.

    Args:
        session: Database session
        conversation_id: Conversation to retrieve from
        limit: Number of recent messages to return

    Returns:
        List of Message objects in chronological order

    Example:
        >>> recent = get_latest_messages(session, conv.id, limit=5)
        >>> for msg in recent:
        ...     print(f"{msg.role}: {msg.content}")
    """
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )

    # Reverse to get chronological order
    messages = list(reversed(session.exec(statement).all()))
    return messages


# ============================================================================
# Batch Operations
# ============================================================================

def save_messages_batch(
    session: Session,
    conversation_id: UUID,
    messages: List[dict]
) -> List[Message]:
    """
    Save multiple messages in a single transaction.

    Args:
        session: Database session
        conversation_id: Conversation to add messages to
        messages: List of message dictionaries with keys:
            - role: str
            - content: str
            - tool_calls: Optional[str]
            - tool_call_id: Optional[str]
            - name: Optional[str]

    Returns:
        List of created Message objects

    Example:
        >>> messages = [
        ...     {"role": "user", "content": "Hello"},
        ...     {"role": "assistant", "content": "Hi there!"}
        ... ]
        >>> saved = save_messages_batch(session, conv.id, messages)
        >>> assert len(saved) == 2
    """
    message_objects = []

    for msg_data in messages:
        message = Message(
            conversation_id=conversation_id,
            role=msg_data["role"],
            content=msg_data["content"],
            tool_calls=msg_data.get("tool_calls"),
            tool_call_id=msg_data.get("tool_call_id"),
            name=msg_data.get("name"),
            created_at=datetime.utcnow(),
        )
        session.add(message)
        message_objects.append(message)

    # Update conversation timestamp
    conversation = session.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)

    session.commit()

    # Refresh all messages to get IDs
    for msg in message_objects:
        session.refresh(msg)

    logger.info(
        f"Saved {len(message_objects)} messages to conversation {conversation_id}"
    )

    return message_objects


# ============================================================================
# Search and Filter
# ============================================================================

def search_conversations(
    session: Session,
    user_id: UUID,
    search_term: str,
    limit: int = 20
) -> List[Conversation]:
    """
    Search user's conversations by title.

    Args:
        session: Database session
        user_id: User whose conversations to search
        search_term: Term to search for in titles
        limit: Maximum results to return

    Returns:
        List of matching Conversation objects

    Example:
        >>> results = search_conversations(session, user.id, "project")
        >>> for conv in results:
        ...     print(conv.title)
    """
    statement = (
        select(Conversation)
        .where(
            Conversation.user_id == user_id,
            Conversation.title.ilike(f"%{search_term}%")
        )
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    )

    conversations = list(session.exec(statement).all())
    logger.debug(
        f"Found {len(conversations)} conversations matching '{search_term}' "
        f"for user {user_id}"
    )
    return conversations


def get_conversations_by_date_range(
    session: Session,
    user_id: UUID,
    start_date: datetime,
    end_date: datetime
) -> List[Conversation]:
    """
    Get conversations created within a date range.

    Args:
        session: Database session
        user_id: User whose conversations to retrieve
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)

    Returns:
        List of Conversation objects in date range

    Example:
        >>> from datetime import datetime, timedelta
        >>> today = datetime.utcnow()
        >>> week_ago = today - timedelta(days=7)
        >>> recent = get_conversations_by_date_range(
        ...     session, user.id, week_ago, today
        ... )
    """
    statement = (
        select(Conversation)
        .where(
            Conversation.user_id == user_id,
            Conversation.created_at >= start_date,
            Conversation.created_at <= end_date,
        )
        .order_by(Conversation.created_at.desc())
    )

    return list(session.exec(statement).all())
```

---

### Service Module Exports

**File**: `backend/app/services/__init__.py`

```python
"""
Service layer for business logic.

Services provide reusable functions for common operations,
keeping endpoint code clean and testable.
"""

from app.services import conversation

__all__ = ["conversation"]
```

---

## 5. Key Design Patterns

### Stateless Operation

**No Caching**:
```python
# EVERY call queries database
def get_conversation_history(session, conversation_id):
    # Fresh query each time - no cache
    statement = select(Message).where(...)
    return session.exec(statement).all()
```

**Why**: Ensures any API instance can serve any request (horizontal scalability)

---

### Chronological Ordering

**Always Order by created_at**:
```python
# Ascending for full history
.order_by(Message.created_at.asc())

# Descending + reverse for limited history
.order_by(Message.created_at.desc()).limit(100)
messages = list(reversed(results))
```

**Why**: Messages must appear in conversation order for agent context

---

### Timestamp Updates

**Update conversation.updated_at on new messages**:
```python
def save_message(...):
    # Save message
    session.add(message)

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)

    session.commit()
```

**Why**: Enables "most recent conversation" sorting

---

### User Isolation

**Always filter by user_id**:
```python
def get_conversation(session, conversation_id, user_id):
    # Enforce ownership
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id  # SECURITY
    )
```

**Why**: Users cannot access other users' conversations

---

### Tool Call Serialization

**Store as JSON string**:
```python
def save_assistant_message(..., tool_calls: List[dict]):
    tool_calls_json = json.dumps(tool_calls)
    message.tool_calls = tool_calls_json

def get_conversation_history(...):
    tool_calls = json.loads(msg.tool_calls) if msg.tool_calls else None
```

**Why**: Preserves complete tool metadata for transparency/debugging

---

## 6. Integration with Chat Endpoint

### Usage in Chat Flow

```python
# In app/api/routes/chat.py
from app.services.conversation import (
    create_conversation,
    get_conversation,
    save_user_message,
    save_assistant_message,
    get_conversation_history,
)

@router.post("/{user_id}/chat")
async def chat(user_id: UUID, request: ChatRequest, ...):
    # 1. Get or create conversation
    if request.conversation_id:
        conversation = get_conversation(session, request.conversation_id, user_id)
        if not conversation:
            raise HTTPException(404, "Conversation not found")
    else:
        conversation = create_conversation(session, user_id)

    # 2. Load history
    history = get_conversation_history(session, conversation.id, limit=100)

    # 3. Save user message
    save_user_message(session, conversation.id, request.message)

    # 4. Run agent
    agent_response = agent_runner.run(
        user_id=user_id,
        user_message=request.message,
        conversation_history=history,
    )

    # 5. Save assistant response
    save_assistant_message(
        session,
        conversation.id,
        agent_response.message,
        tool_calls=agent_response.tool_calls,
    )

    # 6. Return
    return ChatResponse(
        conversation_id=conversation.id,
        message=agent_response.message,
        tool_calls=agent_response.tool_calls,
    )
```

---

## 7. Performance Optimization

### Limited History Queries

```python
# DON'T: Load unlimited history
history = get_conversation_history(session, conv_id)  # Could be 10,000 msgs

# DO: Limit to recent context
history = get_conversation_history(session, conv_id, limit=100)  # Last 100 only
```

**Benefits**:
- Faster queries (uses index efficiently)
- Less memory usage
- Faster agent processing (smaller context)

---

### Composite Index Usage

```sql
-- Index used for limited history queries
CREATE INDEX ix_messages_conversation_created
ON messages(conversation_id, created_at);

-- Query plan:
EXPLAIN SELECT * FROM messages
WHERE conversation_id = 'uuid'
ORDER BY created_at DESC
LIMIT 100;

-- Index Scan using ix_messages_conversation_created
```

---

### Batch Inserts

```python
# DON'T: Multiple commits
for msg_data in messages:
    save_message(session, conv_id, ...)  # Commit per message

# DO: Single transaction
save_messages_batch(session, conv_id, messages)  # One commit
```

---

## 8. Testing Strategy

### Unit Tests

**File**: `tests/services/test_conversation_service.py`

```python
import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from app.services.conversation import (
    create_conversation,
    get_conversation,
    save_user_message,
    save_assistant_message,
    get_conversation_history,
    list_user_conversations,
)


def test_create_conversation(session, user):
    """Test conversation creation."""
    conv = create_conversation(session, user.id, title="Test Chat")

    assert conv.id is not None
    assert conv.user_id == user.id
    assert conv.title == "Test Chat"
    assert conv.created_at is not None
    assert conv.updated_at is not None


def test_create_conversation_auto_title(session, user):
    """Test auto-generated title."""
    conv = create_conversation(session, user.id)

    assert conv.title.startswith("Chat 20")  # "Chat YYYY-MM-DD..."


def test_save_user_message(session, conversation):
    """Test saving user message."""
    msg = save_user_message(session, conversation.id, "Hello")

    assert msg.id is not None
    assert msg.conversation_id == conversation.id
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.created_at is not None


def test_save_assistant_message_with_tools(session, conversation):
    """Test saving assistant message with tool calls."""
    tool_calls = [{"tool_name": "list_tasks", "result": {...}}]
    msg = save_assistant_message(
        session,
        conversation.id,
        "You have 3 tasks",
        tool_calls=tool_calls
    )

    assert msg.role == "assistant"
    assert msg.tool_calls is not None

    import json
    parsed = json.loads(msg.tool_calls)
    assert parsed[0]["tool_name"] == "list_tasks"


def test_conversation_history_ordering(session, conversation):
    """Test messages returned in chronological order."""
    import time

    # Save messages with slight delay
    save_user_message(session, conversation.id, "First")
    time.sleep(0.01)
    save_assistant_message(session, conversation.id, "Second")
    time.sleep(0.01)
    save_user_message(session, conversation.id, "Third")

    # Get history
    history = get_conversation_history(session, conversation.id)

    assert len(history) == 3
    assert history[0].content == "First"
    assert history[1].content == "Second"
    assert history[2].content == "Third"


def test_conversation_history_limit(session, conversation):
    """Test limited history retrieval."""
    # Create 10 messages
    for i in range(10):
        save_user_message(session, conversation.id, f"Message {i}")

    # Get last 5
    history = get_conversation_history(session, conversation.id, limit=5)

    assert len(history) == 5
    assert history[0].content == "Message 5"  # 6th message
    assert history[4].content == "Message 9"  # 10th message


def test_conversation_ownership(session, user1, user2, conversation1):
    """Test conversation ownership enforcement."""
    # conversation1 belongs to user1
    result = get_conversation(session, conversation1.id, user2.id)

    assert result is None  # user2 cannot access user1's conversation


def test_list_user_conversations(session, user):
    """Test listing user's conversations."""
    # Create 3 conversations
    conv1 = create_conversation(session, user.id, "Chat 1")
    conv2 = create_conversation(session, user.id, "Chat 2")
    conv3 = create_conversation(session, user.id, "Chat 3")

    conversations = list_user_conversations(session, user.id)

    assert len(conversations) == 3
    # Most recent first (conv3 created last)
    assert conversations[0].id == conv3.id


def test_conversation_updated_on_message(session, conversation):
    """Test conversation.updated_at updates when message added."""
    original_updated = conversation.updated_at

    import time
    time.sleep(0.1)

    save_user_message(session, conversation.id, "New message")

    session.refresh(conversation)
    assert conversation.updated_at > original_updated


def test_multiple_conversations_per_user(session, user):
    """Test user can have multiple conversations."""
    conv1 = create_conversation(session, user.id, "Project A")
    conv2 = create_conversation(session, user.id, "Project B")

    # Add messages to both
    save_user_message(session, conv1.id, "Message in A")
    save_user_message(session, conv2.id, "Message in B")

    # Retrieve histories
    history1 = get_conversation_history(session, conv1.id)
    history2 = get_conversation_history(session, conv2.id)

    assert len(history1) == 1
    assert history1[0].content == "Message in A"

    assert len(history2) == 1
    assert history2[0].content == "Message in B"
```

---

### Integration Tests

**File**: `tests/integration/test_chat_with_persistence.py`

```python
def test_conversation_resume(client, auth_headers, user):
    """Test resuming a conversation across requests."""
    # Request 1: Start conversation
    resp1 = client.post(
        f"/api/{user.id}/chat",
        json={"message": "Add task to buy milk"},
        headers=auth_headers,
    )
    assert resp1.status_code == 200
    conv_id = resp1.json()["conversation_id"]

    # Request 2: Continue conversation
    resp2 = client.post(
        f"/api/{user.id}/chat",
        json={
            "conversation_id": conv_id,
            "message": "What's on my list?"
        },
        headers=auth_headers,
    )
    assert resp2.status_code == 200
    assert resp2.json()["conversation_id"] == conv_id
    assert "milk" in resp2.json()["message"].lower()
```

---

## 9. Error Handling

### Common Errors

```python
# Conversation not found
conversation = get_conversation(session, conv_id, user_id)
if not conversation:
    raise HTTPException(status_code=404, detail="Conversation not found")

# Invalid role
VALID_ROLES = {"user", "assistant", "tool"}
if role not in VALID_ROLES:
    raise ValueError(f"Invalid role: {role}")

# Database errors
from sqlalchemy.exc import IntegrityError

try:
    save_message(session, conv_id, "user", content)
except IntegrityError as e:
    session.rollback()
    raise HTTPException(status_code=400, detail="Database constraint error")
```

---

## 10. Future Enhancements

### Conversation Export

```python
def export_conversation(
    session: Session,
    conversation_id: UUID,
    user_id: UUID
) -> dict:
    """Export conversation as JSON."""
    conversation = get_conversation(session, conversation_id, user_id)
    if not conversation:
        return None

    messages = get_conversation_history(session, conversation_id)

    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat(),
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]
    }
```

### Conversation Analytics

```python
def get_conversation_stats(session: Session, user_id: UUID) -> dict:
    """Get user's conversation statistics."""
    from sqlalchemy import func

    total_conversations = session.exec(
        select(func.count(Conversation.id))
        .where(Conversation.user_id == user_id)
    ).one()

    total_messages = session.exec(
        select(func.count(Message.id))
        .join(Conversation)
        .where(Conversation.user_id == user_id)
    ).one()

    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "avg_messages_per_conversation": total_messages / total_conversations if total_conversations else 0
    }
```

---

## Implementation Checklist

- [ ] Create `backend/app/services/conversation.py` with all functions
- [ ] Create `backend/app/services/__init__.py` for exports
- [ ] Implement conversation management functions (create, get, list, delete)
- [ ] Implement message storage functions (save_message, save_user_message, save_assistant_message)
- [ ] Implement message retrieval functions (get_conversation_history, get_latest_messages)
- [ ] Implement batch operations (save_messages_batch)
- [ ] Implement search functions (search_conversations, get_conversations_by_date_range)
- [ ] Add logging statements for observability
- [ ] Write unit tests for all service functions
- [ ] Write integration tests for conversation resume
- [ ] Test multi-conversation support per user
- [ ] Test chronological ordering with various message counts
- [ ] Test conversation ownership enforcement
- [ ] Verify no in-memory caching (stateless verification)
- [ ] Performance test with large message counts (100+)
- [ ] Document usage examples in code comments

---

**Skill Version**: 1.0.0
**Last Updated**: 2026-01-19
**Status**: Ready for Implementation
