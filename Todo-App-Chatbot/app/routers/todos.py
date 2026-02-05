"""
Todo CRUD endpoints with JWT authentication and user ownership enforcement.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.auth.dependencies import get_current_user_id

router = APIRouter()


@router.post("/{user_id}/tasks", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    user_id: str,
    todo_data: TodoCreate,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(get_current_user_id)
) -> TodoResponse:
    """
    Create a new todo for the authenticated user.

    **Process:**
    1. Validate JWT token and extract user_id
    2. Verify path user_id matches authenticated user_id (authorization)
    3. Create todo with user ownership
    4. Return created todo with 201 status

    **Security:**
    - Requires valid JWT token in Authorization header
    - Users can only create todos for themselves (path user_id must match JWT user_id)
    - Prevents unauthorized todo creation for other users

    **Error Responses:**
    - 401 Unauthorized: Missing, invalid, or expired JWT token
    - 403 Forbidden: Authenticated user_id doesn't match path user_id
    - 422 Unprocessable Entity: Invalid todo data (empty title, etc.)
    """
    # Authorization check: ensure authenticated user can only create for themselves
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create todos for yourself"
        )

    # Create new todo
    new_todo = Todo(
        title=todo_data.title,
        description=todo_data.description,
        user_id=authenticated_user_id,  # Use authenticated user_id from JWT
        completed=False
    )

    session.add(new_todo)
    session.commit()
    session.refresh(new_todo)

    return TodoResponse.model_validate(new_todo)


@router.get("/{user_id}/tasks", response_model=List[TodoResponse], status_code=status.HTTP_200_OK)
async def list_todos(
    user_id: str,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(get_current_user_id)
) -> List[TodoResponse]:
    """
    List all todos for the authenticated user, ordered by creation date (newest first).

    **Process:**
    1. Validate JWT token and extract user_id
    2. Verify path user_id matches authenticated user_id (authorization)
    3. Query todos owned by authenticated user
    4. Return todos ordered by created_at DESC

    **Security:**
    - Requires valid JWT token in Authorization header
    - Users can only view their own todos (strict ownership filtering)
    - Path user_id must match JWT user_id

    **Error Responses:**
    - 401 Unauthorized: Missing, invalid, or expired JWT token
    - 403 Forbidden: Authenticated user_id doesn't match path user_id
    """
    # Authorization check: ensure authenticated user can only list their own todos
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own todos"
        )

    # Query todos for authenticated user, ordered by created_at DESC
    statement = (
        select(Todo)
        .where(Todo.user_id == authenticated_user_id)
        .order_by(Todo.created_at.desc())
    )
    todos = session.exec(statement).all()

    return [TodoResponse.model_validate(todo) for todo in todos]


@router.put("/{user_id}/tasks/{task_id}", response_model=TodoResponse, status_code=status.HTTP_200_OK)
async def update_todo(
    user_id: str,
    task_id: int,
    todo_data: TodoUpdate,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(get_current_user_id)
) -> TodoResponse:
    """
    Update an existing todo owned by the authenticated user.

    **Process:**
    1. Validate JWT token and extract user_id
    2. Verify path user_id matches authenticated user_id (authorization)
    3. Query todo by task_id
    4. Verify todo ownership (todo.user_id == authenticated_user_id)
    5. Apply partial updates (only provided fields)
    6. Return updated todo

    **Security:**
    - Requires valid JWT token in Authorization header
    - Users can only update their own todos
    - Returns 404 for non-existent or non-owned todos (prevents enumeration)

    **Error Responses:**
    - 401 Unauthorized: Missing, invalid, or expired JWT token
    - 403 Forbidden: Authenticated user_id doesn't match path user_id
    - 404 Not Found: Todo doesn't exist or is not owned by authenticated user
    - 422 Unprocessable Entity: Invalid update data
    """
    # Authorization check: ensure authenticated user can only update their own todos
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own todos"
        )

    # Query todo and verify ownership
    statement = select(Todo).where(
        Todo.id == task_id,
        Todo.user_id == authenticated_user_id
    )
    todo = session.exec(statement).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or you don't have permission to update it"
        )

    # Apply partial updates (only update provided fields)
    update_data = todo_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field must be provided for update"
        )

    for field, value in update_data.items():
        setattr(todo, field, value)

    session.add(todo)
    session.commit()
    session.refresh(todo)

    return TodoResponse.model_validate(todo)


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(get_current_user_id)
) -> None:
    """
    Delete a todo owned by the authenticated user.

    **Process:**
    1. Validate JWT token and extract user_id
    2. Verify path user_id matches authenticated user_id (authorization)
    3. Query todo by task_id
    4. Verify todo ownership (todo.user_id == authenticated_user_id)
    5. Delete todo from database
    6. Return 204 No Content

    **Security:**
    - Requires valid JWT token in Authorization header
    - Users can only delete their own todos
    - Returns 404 for non-existent or non-owned todos (prevents enumeration)

    **Error Responses:**
    - 401 Unauthorized: Missing, invalid, or expired JWT token
    - 403 Forbidden: Authenticated user_id doesn't match path user_id
    - 404 Not Found: Todo doesn't exist or is not owned by authenticated user
    """
    # Authorization check: ensure authenticated user can only delete their own todos
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own todos"
        )

    # Query todo and verify ownership
    statement = select(Todo).where(
        Todo.id == task_id,
        Todo.user_id == authenticated_user_id
    )
    todo = session.exec(statement).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or you don't have permission to delete it"
        )

    session.delete(todo)
    session.commit()

    # FastAPI automatically returns 204 No Content (no return statement needed)
