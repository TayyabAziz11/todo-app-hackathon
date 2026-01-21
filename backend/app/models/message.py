"""
Message model for AI chatbot conversation messages.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship, Column, JSON

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class Message(SQLModel, table=True):
    """
    Message model representing a single message in a conversation.

    Messages are immutable after creation and ordered chronologically to
    reconstruct conversation history for agent context.

    Each message has a role ('user', 'assistant', or 'tool') and may include
    tool call information for transparency.

    When a conversation is deleted, all its messages are deleted (CASCADE).
    When a user is deleted, all their messages are deleted (CASCADE).
    """

    __tablename__ = "messages"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
        description="Unique message identifier (UUIDv4)"
    )

    conversation_id: uuid.UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        ondelete="CASCADE",
        description="Parent conversation (foreign key to conversations.id)"
    )

    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        ondelete="CASCADE",
        description="User who owns this conversation (denormalized for isolation)"
    )

    role: str = Field(
        nullable=False,
        max_length=20,
        description="Message sender role: 'user', 'assistant', or 'tool'"
    )

    content: str = Field(
        nullable=False,
        description="Message text content"
    )

    tool_calls: Optional[Dict[str, Any]] = Field(
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
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        description="Message timestamp for chronological ordering"
    )

    # Relationships
    conversation: "Conversation" = Relationship(
        back_populates="messages"
    )

    def __repr__(self) -> str:
        content_preview = self.content[:50] if self.content else ""
        return f"<Message(id={str(self.id)[:8]}, role={self.role}, {content_preview}...)>"
