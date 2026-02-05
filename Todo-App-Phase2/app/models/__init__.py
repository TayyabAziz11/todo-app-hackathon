"""
SQLModel database models for the Todo application.

Phase 2: User authentication and Todo CRUD only.
Phase 3 models (Conversation, Message) are in separate deployment.
"""

from app.models.user import User
from app.models.todo import Todo

__all__ = ["User", "Todo"]
