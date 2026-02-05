"""
MCP Tool Implementations - Stateless task management tools.

All tools:
- Are stateless (no in-memory state)
- Persist data via SQLModel + PostgreSQL
- Enforce user ownership on all operations
- Return structured JSON responses
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlmodel import Session, select, func

from app.database import get_engine
from app.models.todo import Todo
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
    TaskSummary,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Helper Functions
# =============================================================================

def _todo_to_task_result(todo: Todo) -> TaskResult:
    """Convert SQLModel Todo to TaskResult schema."""
    return TaskResult(
        id=todo.id,
        title=todo.title,
        description=todo.description,
        completed=todo.completed,
        created_at=todo.created_at,
        updated_at=todo.updated_at,
    )


def _get_user_task(
    session: Session,
    user_id: UUID,
    task_id: int
) -> Optional[Todo]:
    """
    Get a task by ID, ensuring it belongs to the specified user.

    Returns None if task doesn't exist or doesn't belong to user.
    """
    statement = select(Todo).where(
        Todo.id == task_id,
        Todo.user_id == user_id
    )
    return session.exec(statement).first()


# =============================================================================
# add_task Tool
# =============================================================================

def add_task(input_data: AddTaskInput) -> AddTaskOutput:
    """
    Create a new task for a user.

    This tool is stateless - it creates a fresh database session,
    performs the operation, and closes the session.

    Args:
        input_data: Validated input containing user_id, title, and optional description

    Returns:
        AddTaskOutput with success status, created task, and message
    """
    logger.info(f"add_task called for user {input_data.user_id}")

    try:
        engine = get_engine()
        with Session(engine) as session:
            # Create the new todo
            todo = Todo(
                user_id=input_data.user_id,
                title=input_data.title,
                description=input_data.description,
                completed=False,
            )

            session.add(todo)
            session.commit()
            session.refresh(todo)

            logger.info(f"Created task {todo.id} for user {input_data.user_id}")

            return AddTaskOutput(
                success=True,
                task=_todo_to_task_result(todo),
                message=f"Task '{todo.title}' created successfully",
            )

    except Exception as e:
        logger.error(f"add_task failed: {e}")
        return AddTaskOutput(
            success=False,
            task=None,
            message="Failed to create task",
            error=f"DATABASE_ERROR: {str(e)}",
        )


# =============================================================================
# list_tasks Tool
# =============================================================================

def list_tasks(input_data: ListTasksInput) -> ListTasksOutput:
    """
    List tasks for a user with optional filtering.

    Supports filtering by:
    - completion status (completed=true/false)
    - title search (case-insensitive)
    - pagination (limit/offset)

    Args:
        input_data: Validated input containing user_id and optional filters

    Returns:
        ListTasksOutput with success status, tasks list, total count, and message
    """
    logger.info(f"list_tasks called for user {input_data.user_id}")

    try:
        engine = get_engine()
        with Session(engine) as session:
            # Build base query
            statement = select(Todo).where(Todo.user_id == input_data.user_id)

            # Apply completion filter if specified
            if input_data.completed is not None:
                statement = statement.where(Todo.completed == input_data.completed)

            # Apply search filter if specified
            if input_data.search:
                search_term = f"%{input_data.search}%"
                statement = statement.where(Todo.title.ilike(search_term))

            # Get total count before pagination
            count_statement = select(func.count()).select_from(statement.subquery())
            total = session.exec(count_statement).one()

            # Apply pagination and ordering
            statement = statement.order_by(Todo.created_at.desc())
            statement = statement.offset(input_data.offset).limit(input_data.limit)

            # Execute query
            todos = session.exec(statement).all()

            # Convert to response format
            tasks = [_todo_to_task_result(todo) for todo in todos]

            # Build message
            if input_data.completed is True:
                status_desc = "completed"
            elif input_data.completed is False:
                status_desc = "incomplete"
            else:
                status_desc = "total"

            if input_data.search:
                message = f"Found {total} {status_desc} tasks matching '{input_data.search}'"
            else:
                message = f"Found {total} {status_desc} tasks"

            logger.info(f"list_tasks returned {len(tasks)} tasks for user {input_data.user_id}")

            return ListTasksOutput(
                success=True,
                tasks=tasks,
                total=total,
                message=message,
            )

    except Exception as e:
        logger.error(f"list_tasks failed: {e}")
        return ListTasksOutput(
            success=False,
            tasks=[],
            total=0,
            message="Failed to list tasks",
            error=f"DATABASE_ERROR: {str(e)}",
        )


# =============================================================================
# update_task Tool
# =============================================================================

def update_task(input_data: UpdateTaskInput) -> UpdateTaskOutput:
    """
    Update an existing task's title and/or description.

    Only updates fields that are provided. To clear the description,
    pass an empty string.

    Args:
        input_data: Validated input containing user_id, task_id, and fields to update

    Returns:
        UpdateTaskOutput with success status, updated task, and message
    """
    logger.info(f"update_task called for task {input_data.task_id} by user {input_data.user_id}")

    try:
        engine = get_engine()
        with Session(engine) as session:
            # Get the task (with ownership check)
            todo = _get_user_task(session, input_data.user_id, input_data.task_id)

            if not todo:
                logger.warning(f"Task {input_data.task_id} not found for user {input_data.user_id}")
                return UpdateTaskOutput(
                    success=False,
                    task=None,
                    message="Task not found",
                    error=f"TASK_NOT_FOUND: Task {input_data.task_id} does not exist or does not belong to this user",
                )

            # Check if any updates were provided
            if input_data.title is None and input_data.description is None:
                return UpdateTaskOutput(
                    success=False,
                    task=_todo_to_task_result(todo),
                    message="No updates provided",
                    error="VALIDATION_ERROR: At least one of 'title' or 'description' must be provided",
                )

            # Apply updates
            if input_data.title is not None:
                todo.title = input_data.title

            if input_data.description is not None:
                # Empty string clears the description
                todo.description = input_data.description if input_data.description else None

            # Update timestamp
            todo.updated_at = datetime.now(timezone.utc)

            session.add(todo)
            session.commit()
            session.refresh(todo)

            logger.info(f"Updated task {todo.id} for user {input_data.user_id}")

            return UpdateTaskOutput(
                success=True,
                task=_todo_to_task_result(todo),
                message=f"Task {todo.id} updated successfully",
            )

    except Exception as e:
        logger.error(f"update_task failed: {e}")
        return UpdateTaskOutput(
            success=False,
            task=None,
            message="Failed to update task",
            error=f"DATABASE_ERROR: {str(e)}",
        )


# =============================================================================
# complete_task Tool
# =============================================================================

def complete_task(input_data: CompleteTaskInput) -> CompleteTaskOutput:
    """
    Mark a task as completed or incomplete.

    Args:
        input_data: Validated input containing user_id, task_id, and completed status

    Returns:
        CompleteTaskOutput with success status, updated task, and message
    """
    logger.info(f"complete_task called for task {input_data.task_id} by user {input_data.user_id}")

    try:
        engine = get_engine()
        with Session(engine) as session:
            # Get the task (with ownership check)
            todo = _get_user_task(session, input_data.user_id, input_data.task_id)

            if not todo:
                logger.warning(f"Task {input_data.task_id} not found for user {input_data.user_id}")
                return CompleteTaskOutput(
                    success=False,
                    task=None,
                    message="Task not found",
                    error=f"TASK_NOT_FOUND: Task {input_data.task_id} does not exist or does not belong to this user",
                )

            # Update completion status
            todo.completed = input_data.completed
            todo.updated_at = datetime.now(timezone.utc)

            session.add(todo)
            session.commit()
            session.refresh(todo)

            status_text = "completed" if input_data.completed else "marked as incomplete"
            logger.info(f"Task {todo.id} {status_text} for user {input_data.user_id}")

            return CompleteTaskOutput(
                success=True,
                task=_todo_to_task_result(todo),
                message=f"Task '{todo.title}' {status_text}",
            )

    except Exception as e:
        logger.error(f"complete_task failed: {e}")
        return CompleteTaskOutput(
            success=False,
            task=None,
            message="Failed to update task status",
            error=f"DATABASE_ERROR: {str(e)}",
        )


# =============================================================================
# delete_task Tool
# =============================================================================

def delete_task(input_data: DeleteTaskInput) -> DeleteTaskOutput:
    """
    Permanently delete a task.

    This operation cannot be undone.

    Args:
        input_data: Validated input containing user_id and task_id

    Returns:
        DeleteTaskOutput with success status, deleted task summary, and message
    """
    logger.info(f"delete_task called for task {input_data.task_id} by user {input_data.user_id}")

    try:
        engine = get_engine()
        with Session(engine) as session:
            # Get the task (with ownership check)
            todo = _get_user_task(session, input_data.user_id, input_data.task_id)

            if not todo:
                logger.warning(f"Task {input_data.task_id} not found for user {input_data.user_id}")
                return DeleteTaskOutput(
                    success=False,
                    deleted_task=None,
                    message="Task not found",
                    error=f"TASK_NOT_FOUND: Task {input_data.task_id} does not exist or does not belong to this user",
                )

            # Store task info before deletion
            deleted_summary = TaskSummary(id=todo.id, title=todo.title)

            # Delete the task
            session.delete(todo)
            session.commit()

            logger.info(f"Deleted task {deleted_summary.id} for user {input_data.user_id}")

            return DeleteTaskOutput(
                success=True,
                deleted_task=deleted_summary,
                message=f"Task '{deleted_summary.title}' has been deleted",
            )

    except Exception as e:
        logger.error(f"delete_task failed: {e}")
        return DeleteTaskOutput(
            success=False,
            deleted_task=None,
            message="Failed to delete task",
            error=f"DATABASE_ERROR: {str(e)}",
        )


# =============================================================================
# Tool Registry (for dynamic dispatch)
# =============================================================================

TOOL_HANDLERS = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "update_task": update_task,
    "complete_task": complete_task,
    "delete_task": delete_task,
}

INPUT_SCHEMAS = {
    "add_task": AddTaskInput,
    "list_tasks": ListTasksInput,
    "update_task": UpdateTaskInput,
    "complete_task": CompleteTaskInput,
    "delete_task": DeleteTaskInput,
}


def invoke_tool(tool_name: str, arguments: dict) -> dict:
    """
    Invoke an MCP tool by name with the given arguments.

    This is the main entry point for the MCP server to dispatch tool calls.

    Args:
        tool_name: Name of the tool to invoke
        arguments: Dictionary of arguments for the tool

    Returns:
        Dictionary result from the tool (JSON-serializable)

    Raises:
        ValueError: If tool_name is not recognized
        ValidationError: If arguments don't match the schema
    """
    if tool_name not in TOOL_HANDLERS:
        raise ValueError(f"Unknown tool: {tool_name}")

    # Validate and parse input
    input_schema = INPUT_SCHEMAS[tool_name]
    validated_input = input_schema(**arguments)

    # Invoke the tool
    handler = TOOL_HANDLERS[tool_name]
    result = handler(validated_input)

    # Return as dict for JSON serialization
    # TaskResult.model_dump() now handles datetime serialization
    return result.model_dump()
