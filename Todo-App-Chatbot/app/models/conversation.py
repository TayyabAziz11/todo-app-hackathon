"""
Conversation model for AI chatbot conversation persistence.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.message import Message


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a persistent chat session between user and AI assistant.

    Each conversation has a unique ID (UUID) that serves as the ONLY state token
    passed between client and server for stateless architecture.

    When a conversation is deleted, all its messages are also deleted (CASCADE).
    When a user is deleted, all their conversations are deleted (CASCADE).
    """

    __tablename__ = "conversations"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
        description="Unique conversation identifier (UUIDv4)"
    )

    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        ondelete="CASCADE",
        description="Owner of this conversation (foreign key to users.id)"
    )

    title: Optional[str] = Field(
        default=None,
        max_length=255,
        nullable=True,
        description="Optional conversation title (e.g., 'Task Planning Session')"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Timestamp when conversation was created"
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Timestamp of last message (updated on each message)"
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    def __repr__(self) -> str:
        title_preview = self.title[:30] if self.title else "Untitled"
        return f"<Conversation(id={str(self.id)[:8]}, {title_preview})>"
