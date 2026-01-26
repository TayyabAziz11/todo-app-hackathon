"""
MCP Tool Schemas - Pydantic models for input/output validation.

All schemas enforce strict validation for MCP tool calls.
"""

from datetime import datetime
from typing import Any, Optional, List, Literal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Base Result Types
# =============================================================================

class TaskResult(BaseModel):
    """Serialized task for MCP tool responses."""

    id: int = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: bool = Field(..., description="Completion status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

    def model_dump(self, **kwargs):
        """Override model_dump to ensure datetime serialization."""
        # Get the default dump
        data = super().model_dump(**kwargs)
        # Manually serialize datetime objects
        if isinstance(data.get('created_at'), datetime):
            data['created_at'] = data['created_at'].isoformat()
        if isinstance(data.get('updated_at'), datetime):
            data['updated_at'] = data['updated_at'].isoformat()
        return data


class TaskSummary(BaseModel):
    """Minimal task info for deletion responses."""

    id: int = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")


# =============================================================================
# add_task Schemas
# =============================================================================

class AddTaskInput(BaseModel):
    """Input schema for add_task tool."""

    user_id: UUID = Field(
        ...,
        description="The authenticated user's unique identifier"
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Brief title describing the task"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional detailed description of the task"
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Strip whitespace and validate non-empty."""
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty or whitespace only")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace, convert empty to None."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class AddTaskOutput(BaseModel):
    """Output schema for add_task tool."""

    success: bool = Field(..., description="Whether the operation succeeded")
    task: Optional[TaskResult] = Field(None, description="The created task")
    message: str = Field(..., description="Human-readable result message")
    error: Optional[str] = Field(None, description="Error code if failed")

    def model_dump(self, **kwargs):
        """Override model_dump to ensure datetime serialization."""
        data = super().model_dump(**kwargs)
        if data.get('task'):
            if isinstance(data['task'].get('created_at'), datetime):
                data['task']['created_at'] = data['task']['created_at'].isoformat()
            if isinstance(data['task'].get('updated_at'), datetime):
                data['task']['updated_at'] = data['task']['updated_at'].isoformat()
        return data


# =============================================================================
# list_tasks Schemas
# =============================================================================

class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""

    user_id: UUID = Field(
        ...,
        description="The authenticated user's unique identifier"
    )
    completed: Optional[bool] = Field(
        None,
        description="Filter by completion status (omit for all tasks)"
    )
    search: Optional[str] = Field(
        None,
        max_length=255,
        description="Search term to filter tasks by title"
    )
    limit: int = Field(
        50,
        ge=1,
        le=100,
        description="Maximum number of tasks to return"
    )
    offset: int = Field(
        0,
        ge=0,
        description="Number of tasks to skip for pagination"
    )

    @field_validator("search")
    @classmethod
    def validate_search(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace, convert empty to None."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class ListTasksOutput(BaseModel):
    """Output schema for list_tasks tool."""

    success: bool = Field(..., description="Whether the operation succeeded")
    tasks: List[TaskResult] = Field(
        default_factory=list,
        description="List of tasks matching criteria"
    )
    total: int = Field(0, description="Total number of matching tasks")
    message: str = Field(..., description="Human-readable result message")
    error: Optional[str] = Field(None, description="Error code if failed")

    def model_dump(self, **kwargs):
        """Override model_dump to ensure datetime serialization in task list."""
        data = super().model_dump(**kwargs)
        # Serialize each task's datetime fields
        if data.get('tasks'):
            for task in data['tasks']:
                if isinstance(task.get('created_at'), datetime):
                    task['created_at'] = task['created_at'].isoformat()
                if isinstance(task.get('updated_at'), datetime):
                    task['updated_at'] = task['updated_at'].isoformat()
        return data


# =============================================================================
# update_task Schemas
# =============================================================================

class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""

    user_id: UUID = Field(
        ...,
        description="The authenticated user's unique identifier"
    )
    task_id: int = Field(
        ...,
        description="The ID of the task to update"
    )
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="New title for the task (optional)"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="New description (optional, use empty string to clear)"
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace and validate non-empty if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty or whitespace only")
        return v


class UpdateTaskOutput(BaseModel):
    """Output schema for update_task tool."""

    success: bool = Field(..., description="Whether the operation succeeded")
    task: Optional[TaskResult] = Field(None, description="The updated task")
    message: str = Field(..., description="Human-readable result message")
    error: Optional[str] = Field(None, description="Error code if failed")

    def model_dump(self, **kwargs):
        """Override model_dump to ensure datetime serialization."""
        data = super().model_dump(**kwargs)
        if data.get('task'):
            if isinstance(data['task'].get('created_at'), datetime):
                data['task']['created_at'] = data['task']['created_at'].isoformat()
            if isinstance(data['task'].get('updated_at'), datetime):
                data['task']['updated_at'] = data['task']['updated_at'].isoformat()
        return data


# =============================================================================
# complete_task Schemas
# =============================================================================

class CompleteTaskInput(BaseModel):
    """Input schema for complete_task tool."""

    user_id: UUID = Field(
        ...,
        description="The authenticated user's unique identifier"
    )
    task_id: int = Field(
        ...,
        description="The ID of the task to mark complete/incomplete"
    )
    completed: bool = Field(
        True,
        description="Set to true to complete, false to uncomplete"
    )


class CompleteTaskOutput(BaseModel):
    """Output schema for complete_task tool."""

    success: bool = Field(..., description="Whether the operation succeeded")
    task: Optional[TaskResult] = Field(None, description="The updated task")
    message: str = Field(..., description="Human-readable result message")
    error: Optional[str] = Field(None, description="Error code if failed")

    def model_dump(self, **kwargs):
        """Override model_dump to ensure datetime serialization."""
        data = super().model_dump(**kwargs)
        if data.get('task'):
            if isinstance(data['task'].get('created_at'), datetime):
                data['task']['created_at'] = data['task']['created_at'].isoformat()
            if isinstance(data['task'].get('updated_at'), datetime):
                data['task']['updated_at'] = data['task']['updated_at'].isoformat()
        return data


# =============================================================================
# delete_task Schemas
# =============================================================================

class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool."""

    user_id: UUID = Field(
        ...,
        description="The authenticated user's unique identifier"
    )
    task_id: int = Field(
        ...,
        description="The ID of the task to delete"
    )


class DeleteTaskOutput(BaseModel):
    """Output schema for delete_task tool."""

    success: bool = Field(..., description="Whether the operation succeeded")
    deleted_task: Optional[TaskSummary] = Field(
        None,
        description="Summary of the deleted task"
    )
    message: str = Field(..., description="Human-readable result message")
    error: Optional[str] = Field(None, description="Error code if failed")


# =============================================================================
# MCP Tool Definition (for registration)
# =============================================================================

class MCPToolParameter(BaseModel):
    """JSON Schema property definition for MCP tools."""

    type: str = Field(..., description="JSON type (string, integer, boolean, etc.)")
    description: str = Field(..., description="Parameter description")
    format: Optional[str] = Field(None, description="Format hint (uuid, date-time, etc.)")
    minimum: Optional[int] = Field(None, description="Minimum value for integers")
    maximum: Optional[int] = Field(None, description="Maximum value for integers")
    minLength: Optional[int] = Field(None, description="Minimum string length")
    maxLength: Optional[int] = Field(None, description="Maximum string length")
    default: Optional[Any] = Field(None, description="Default value")


class MCPToolInputSchema(BaseModel):
    """JSON Schema for MCP tool input."""

    type: Literal["object"] = "object"
    properties: dict[str, MCPToolParameter] = Field(
        default_factory=dict,
        description="Parameter definitions"
    )
    required: List[str] = Field(
        default_factory=list,
        description="Required parameter names"
    )


class MCPToolDefinition(BaseModel):
    """MCP tool definition for registration."""

    name: str = Field(..., description="Tool name (e.g., 'add_task')")
    description: str = Field(..., description="Tool description for the AI agent")
    inputSchema: MCPToolInputSchema = Field(..., description="Input parameter schema")


# =============================================================================
# Tool Definitions Export
# =============================================================================

def get_tool_definitions() -> List[MCPToolDefinition]:
    """Return all MCP tool definitions for registration."""
    return [
        MCPToolDefinition(
            name="add_task",
            description="Create a new task for the user. Use when the user wants to add, create, or make a new todo item.",
            inputSchema=MCPToolInputSchema(
                properties={
                    "user_id": MCPToolParameter(
                        type="string",
                        format="uuid",
                        description="The authenticated user's unique identifier"
                    ),
                    "title": MCPToolParameter(
                        type="string",
                        minLength=1,
                        maxLength=255,
                        description="Brief title describing the task"
                    ),
                    "description": MCPToolParameter(
                        type="string",
                        maxLength=2000,
                        description="Optional detailed description of the task"
                    ),
                },
                required=["user_id", "title"]
            )
        ),
        MCPToolDefinition(
            name="list_tasks",
            description="List all tasks for a user with optional filtering. Use when the user wants to see, view, show, or get their tasks/todos.",
            inputSchema=MCPToolInputSchema(
                properties={
                    "user_id": MCPToolParameter(
                        type="string",
                        format="uuid",
                        description="The authenticated user's unique identifier"
                    ),
                    "completed": MCPToolParameter(
                        type="boolean",
                        description="Filter by completion status (omit for all tasks)"
                    ),
                    "search": MCPToolParameter(
                        type="string",
                        maxLength=255,
                        description="Search term to filter tasks by title"
                    ),
                    "limit": MCPToolParameter(
                        type="integer",
                        minimum=1,
                        maximum=100,
                        default=50,
                        description="Maximum number of tasks to return"
                    ),
                    "offset": MCPToolParameter(
                        type="integer",
                        minimum=0,
                        default=0,
                        description="Number of tasks to skip for pagination"
                    ),
                },
                required=["user_id"]
            )
        ),
        MCPToolDefinition(
            name="update_task",
            description="Update an existing task's title or description. Use when the user wants to change, modify, edit, or rename a task.",
            inputSchema=MCPToolInputSchema(
                properties={
                    "user_id": MCPToolParameter(
                        type="string",
                        format="uuid",
                        description="The authenticated user's unique identifier"
                    ),
                    "task_id": MCPToolParameter(
                        type="integer",
                        description="The ID of the task to update"
                    ),
                    "title": MCPToolParameter(
                        type="string",
                        minLength=1,
                        maxLength=255,
                        description="New title for the task (optional)"
                    ),
                    "description": MCPToolParameter(
                        type="string",
                        maxLength=2000,
                        description="New description (optional, use empty string to clear)"
                    ),
                },
                required=["user_id", "task_id"]
            )
        ),
        MCPToolDefinition(
            name="complete_task",
            description="Mark a task as completed or incomplete. Use when the user wants to finish, complete, done, check off, or undo a task.",
            inputSchema=MCPToolInputSchema(
                properties={
                    "user_id": MCPToolParameter(
                        type="string",
                        format="uuid",
                        description="The authenticated user's unique identifier"
                    ),
                    "task_id": MCPToolParameter(
                        type="integer",
                        description="The ID of the task to mark complete/incomplete"
                    ),
                    "completed": MCPToolParameter(
                        type="boolean",
                        default=True,
                        description="Set to true to complete, false to uncomplete"
                    ),
                },
                required=["user_id", "task_id"]
            )
        ),
        MCPToolDefinition(
            name="delete_task",
            description="Permanently delete a task. Use when the user wants to remove, delete, or get rid of a task.",
            inputSchema=MCPToolInputSchema(
                properties={
                    "user_id": MCPToolParameter(
                        type="string",
                        format="uuid",
                        description="The authenticated user's unique identifier"
                    ),
                    "task_id": MCPToolParameter(
                        type="integer",
                        description="The ID of the task to delete"
                    ),
                },
                required=["user_id", "task_id"]
            )
        ),
    ]
