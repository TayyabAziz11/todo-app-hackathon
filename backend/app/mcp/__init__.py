"""
MCP (Model Context Protocol) Tools for Todo AI Chatbot.

This module provides stateless MCP tools for task management:
- add_task: Create a new task
- list_tasks: Retrieve tasks with optional filtering
- update_task: Modify task title/description
- complete_task: Mark task as complete/incomplete
- delete_task: Remove a task

All tools are stateless and persist data via SQLModel + PostgreSQL.
"""

from app.mcp.server import MCPToolServer, get_mcp_server
from app.mcp.tools import (
    add_task,
    list_tasks,
    update_task,
    complete_task,
    delete_task,
)
from app.mcp.schemas import (
    AddTaskInput,
    AddTaskOutput,
    ListTasksInput,
    ListTasksOutput,
    UpdateTaskInput,
    UpdateTaskOutput,
    CompleteTaskInput,
    CompleteTaskOutput,
    DeleteTaskInput,
    DeleteTaskOutput,
    TaskResult,
    MCPToolDefinition,
)

__all__ = [
    # Server
    "MCPToolServer",
    "get_mcp_server",
    # Tools
    "add_task",
    "list_tasks",
    "update_task",
    "complete_task",
    "delete_task",
    # Schemas
    "AddTaskInput",
    "AddTaskOutput",
    "ListTasksInput",
    "ListTasksOutput",
    "UpdateTaskInput",
    "UpdateTaskOutput",
    "CompleteTaskInput",
    "CompleteTaskOutput",
    "DeleteTaskInput",
    "DeleteTaskOutput",
    "TaskResult",
    "MCPToolDefinition",
]
