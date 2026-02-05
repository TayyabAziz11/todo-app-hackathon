"""
Pydantic schemas for todo CRUD endpoints.

These schemas define the request and response structures for:
- Creating todos
- Updating todos
- Retrieving todo data
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TodoCreate(BaseModel):
    """
    Request payload for creating a new todo.

    Validates:
        - Title is not empty (min_length=1)
        - Title does not exceed 200 characters
        - Description does not exceed 2000 characters (optional)
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Todo title (required, 1-200 characters)",
        examples=["Buy groceries", "Complete project report"]
    )

    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Detailed description (optional, max 2000 characters)",
        examples=["Pick up milk, eggs, and bread from the store"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread, and coffee"
                },
                {
                    "title": "Morning jog",
                    "description": None
                }
            ]
        }
    }


class TodoUpdate(BaseModel):
    """
    Request payload for updating an existing todo.

    All fields are optional - only provided fields will be updated.
    At least one field must be provided.
    """

    title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Updated title (optional, max 200 characters)",
        examples=["Updated task title"]
    )

    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Updated description (optional, max 2000 characters)",
        examples=["Updated task details"]
    )

    completed: Optional[bool] = Field(
        default=None,
        description="Completion status (optional)",
        examples=[True, False]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Buy groceries and cook dinner",
                    "completed": True
                },
                {
                    "description": "Updated: Also pick up cleaning supplies"
                },
                {
                    "completed": False
                }
            ]
        }
    }


class TodoResponse(BaseModel):
    """
    Response payload for todo data.

    Contains all todo fields including metadata (timestamps, completion status).
    """

    id: int = Field(
        ...,
        description="Unique todo identifier",
        examples=[1, 42, 123]
    )

    title: str = Field(
        ...,
        description="Todo title",
        examples=["Buy groceries"]
    )

    description: Optional[str] = Field(
        default=None,
        description="Todo description (may be null)",
        examples=["Milk, eggs, bread"]
    )

    completed: bool = Field(
        ...,
        description="Whether the todo is completed",
        examples=[False, True]
    )

    created_at: datetime = Field(
        ...,
        description="When the todo was created (ISO 8601 format)",
        examples=["2025-12-31T10:30:00Z"]
    )

    updated_at: datetime = Field(
        ...,
        description="When the todo was last updated (ISO 8601 format)",
        examples=["2025-12-31T14:45:00Z"]
    )

    model_config = {
        "from_attributes": True,  # Enable ORM mode for SQLModel compatibility
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread, and coffee",
                    "completed": False,
                    "created_at": "2025-12-31T10:00:00Z",
                    "updated_at": "2025-12-31T10:00:00Z"
                },
                {
                    "id": 2,
                    "title": "Morning jog",
                    "description": None,
                    "completed": True,
                    "created_at": "2025-12-30T06:00:00Z",
                    "updated_at": "2025-12-31T07:15:00Z"
                }
            ]
        }
    }
