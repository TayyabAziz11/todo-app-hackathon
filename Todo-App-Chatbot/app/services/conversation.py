"""
Conversation Persistence Service - Stateless conversation management for AI chatbot.

This service provides CRUD operations for conversations and messages with:
- Stateless architecture (no in-memory state)
- User isolation enforcement
- Chronological message retrieval
- Request-scoped database sessions

All functions use dependency injection for database sessions to ensure
horizontal scalability and stateless operation.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select, desc, asc
from sqlalchemy.exc import SQLAlchemyError

from app.models.conversation import Conversation
from app.models.message import Message

logger = logging.getLogger(__name__)


# =============================================================================
# Conversation Operations
# =============================================================================

def create_conversation(
    db: Session,
    user_id: UUID,
    title: Optional[str] = None
) -> Conversation:
    """
    Create a new conversation for a user.

    Args:
        db: Database session (request-scoped)
        user_id: User identifier (UUID)
        title: Optional conversation title

    Returns:
        Conversation: Created conversation with generated UUID

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        logger.info(f"Created conversation {conversation.id} for user {user_id}")
        return conversation

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to create conversation: {e}")
        raise


def get_conversation(
    db: Session,
    conversation_id: UUID,
    user_id: UUID
) -> Optional[Conversation]:
    """
    Retrieve a conversation by ID with user isolation.

    Args:
        db: Database session (request-scoped)
        conversation_id: Conversation identifier
        user_id: User identifier for ownership validation

    Returns:
        Conversation or None if not found or user doesn't own it

    Raises:
        SQLAlchemyError: If database query fails
    """
    try:
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id  # CRITICAL: User isolation
        )
        conversation = db.exec(statement).first()

        if conversation:
            logger.debug(f"Retrieved conversation {conversation_id}")
        else:
            logger.warning(
                f"Conversation {conversation_id} not found or not owned by user {user_id}"
            )

        return conversation

    except SQLAlchemyError as e:
        logger.error(f"Failed to retrieve conversation {conversation_id}: {e}")
        raise


def list_user_conversations(
    db: Session,
    user_id: UUID,
    limit: int = 20,
    offset: int = 0
) -> List[Conversation]:
    """
    List conversations for a user, ordered by most recent activity.

    Args:
        db: Database session (request-scoped)
        user_id: User identifier
        limit: Maximum number of conversations to return (default: 20)
        offset: Number of conversations to skip (default: 0)

    Returns:
        List[Conversation]: User's conversations, newest first

    Raises:
        SQLAlchemyError: If database query fails
    """
    try:
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .offset(offset)
        )
        conversations = list(db.exec(statement).all())

        logger.debug(f"Listed {len(conversations)} conversations for user {user_id}")
        return conversations

    except SQLAlchemyError as e:
        logger.error(f"Failed to list conversations for user {user_id}: {e}")
        raise


# =============================================================================
# Message Operations
# =============================================================================

def save_message(
    db: Session,
    conversation_id: UUID,
    user_id: UUID,
    role: str,
    content: str,
    tool_calls: Optional[dict] = None,
    tool_call_id: Optional[str] = None,
    name: Optional[str] = None
) -> Message:
    """
    Save a message to a conversation and update conversation timestamp.

    Args:
        db: Database session (request-scoped)
        conversation_id: Parent conversation ID
        user_id: User identifier (denormalized for isolation)
        role: Message role ('user', 'assistant', or 'tool')
        content: Message text content
        tool_calls: Optional JSON object of tool invocations (for assistant messages)
        tool_call_id: Optional tool call identifier (for tool result messages)
        name: Optional tool name (for tool result messages)

    Returns:
        Message: Created message with generated UUID

    Raises:
        SQLAlchemyError: If database operation fails
        ValueError: If conversation not found or user doesn't own it
    """
    try:
        # Verify conversation exists and belongs to user
        conversation = get_conversation(db, conversation_id, user_id)
        if not conversation:
            raise ValueError(
                f"Conversation {conversation_id} not found or not owned by user {user_id}"
            )

        # Create message
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_call_id=tool_call_id,
            name=name
        )
        db.add(message)

        # Update conversation timestamp
        conversation.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(message)

        logger.info(
            f"Saved {role} message {message.id} to conversation {conversation_id}"
        )
        return message

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to save message to conversation {conversation_id}: {e}")
        raise


def get_conversation_history(
    db: Session,
    conversation_id: UUID,
    user_id: UUID,
    limit: int = 50
) -> List[Message]:
    """
    Retrieve conversation messages in chronological order.

    This is the MOST COMMON QUERY for conversation resume.
    Uses composite index (conversation_id, created_at) for O(log N + K) performance.

    Args:
        db: Database session (request-scoped)
        conversation_id: Conversation identifier
        user_id: User identifier for ownership validation
        limit: Maximum number of messages to return (default: 50)

    Returns:
        List[Message]: Messages ordered by created_at ascending (oldest first)

    Raises:
        SQLAlchemyError: If database query fails
        ValueError: If conversation not found or user doesn't own it
    """
    try:
        # Verify conversation exists and belongs to user
        conversation = get_conversation(db, conversation_id, user_id)
        if not conversation:
            raise ValueError(
                f"Conversation {conversation_id} not found or not owned by user {user_id}"
            )

        # Query messages with composite index optimization
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(asc(Message.created_at))
            .limit(limit)
        )
        messages = list(db.exec(statement).all())

        logger.debug(
            f"Retrieved {len(messages)} messages for conversation {conversation_id}"
        )
        return messages

    except SQLAlchemyError as e:
        logger.error(
            f"Failed to retrieve history for conversation {conversation_id}: {e}"
        )
        raise


# =============================================================================
# Stateless Architecture Notes
# =============================================================================

"""
CRITICAL DESIGN PRINCIPLES:

1. Request-Scoped Sessions:
   - ALL functions receive db: Session via dependency injection
   - NO module-level database sessions or connections
   - Each request gets fresh session, auto-closed after response

2. User Isolation:
   - ALL queries filter by user_id
   - get_conversation() enforces ownership before any operation
   - save_message() validates conversation ownership

3. Chronological Ordering:
   - Messages ALWAYS ordered by created_at ascending
   - Composite index (conversation_id, created_at) enables O(log N + K) retrieval
   - Updated_at on conversations tracks last activity

4. Horizontal Scalability:
   - NO in-memory state or caching
   - Database is single source of truth
   - Any server instance can handle any request
   - Stateless conversation resume after server restart

5. Validation Test:
   - Create conversation with 3 messages
   - Restart backend server
   - Send new message with same conversation_id
   - Verify agent has full context (proves statelessness)
"""
