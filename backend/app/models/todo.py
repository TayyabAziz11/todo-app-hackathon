"""
Todo model for task management.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class Todo(SQLModel, table=True):
    """
    Todo model representing individual tasks owned by users.

    Each todo belongs to exactly one user. When a user is deleted,
    all their todos are also deleted (CASCADE).
    """

    __tablename__ = "todos"

    id: int = Field(
        default=None,
        primary_key=True,
        nullable=False,
        description="Auto-incrementing unique identifier for the todo"
    )

    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        ondelete="CASCADE",
        description="Owner of this todo (foreign key to users.id)"
    )

    title: str = Field(
        max_length=255,
        nullable=False,
        description="Brief description of the todo task"
    )

    description: Optional[str] = Field(
        default=None,
        nullable=True,
        description="Detailed description of the todo (optional)"
    )

    completed: bool = Field(
        default=False,
        nullable=False,
        description="Whether the todo has been completed"
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Timestamp when todo was created"
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Timestamp when todo was last modified"
    )

    def __repr__(self) -> str:
        status = "✓" if self.completed else "○"
        return f"<Todo(id={self.id}, {status} {self.title[:30]})>"
