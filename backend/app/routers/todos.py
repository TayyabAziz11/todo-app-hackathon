"""
Todo CRUD endpoints with JWT authentication and user ownership enforcement.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlmodel import Session, select, func, text, or_, and_
from sqlalchemy import cast, String as SQLAString
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.database import get_session
from app.models.todo import Todo, Priority
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

    # Create new todo with Phase V.4 fields
    new_todo = Todo(
        title=todo_data.title,
        description=todo_data.description,
        user_id=authenticated_user_id,  # Use authenticated user_id from JWT
        completed=False,
        priority=todo_data.priority,  # Phase V.4: Priority level
        tags=todo_data.tags,  # Phase V.4: Tags array
        due_date=todo_data.due_date  # Phase V.4: Due date
    )

    session.add(new_todo)
    session.commit()
    session.refresh(new_todo)

    # Update search_vector for full-text search (raw SQL — TSVECTOR not in ORM)
    if new_todo.title or new_todo.description:
        search_text = f"{new_todo.title or ''} {new_todo.description or ''}".strip()
        session.execute(
            text("UPDATE todos SET search_vector = to_tsvector('english', :txt) WHERE id = :id"),
            {"txt": search_text, "id": new_todo.id}
        )
        session.commit()

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

    # Update search_vector if title or description changed
    if 'title' in update_data or 'description' in update_data:
        search_text = f"{todo.title or ''} {todo.description or ''}".strip()
        if search_text:
            session.execute(
                text("UPDATE todos SET search_vector = to_tsvector('english', :text) WHERE id = :id"),
                {"text": search_text, "id": todo.id}
            )

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


# ============================================================================
# Phase V.4: Advanced Search & Tag Management Endpoints
# ============================================================================

@router.get("/{user_id}/v1/todos/search")
async def advanced_search_todos(
    user_id: str,
    q: Optional[str] = Query(None, description="Search query for title/description"),
    status_filter: Optional[str] = Query(None, alias="status", description="'active' or 'completed'"),
    priority: Optional[str] = Query(None, description="Comma-separated priorities (e.g., 'HIGH,URGENT')"),
    tags: Optional[str] = Query(None, description="Comma-separated tags (AND logic)"),
    due_date_from: Optional[str] = Query(None, description="ISO8601 date"),
    due_date_to: Optional[str] = Query(None, description="ISO8601 date"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="'asc' or 'desc'"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Phase V.4: Advanced search with filtering, sorting, and pagination.

    Supports:
    - Full-text search on title/description
    - Filter by status (active/completed)
    - Filter by priority levels
    - Filter by tags (AND logic)
    - Filter by due date range
    - Sorting by multiple fields
    - Pagination
    """
    # Authorization check
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only search your own todos"
        )

    # Base query: user's todos only
    query = select(Todo).where(Todo.user_id == authenticated_user_id)

    # Full-text search on title and description
    if q:
        search_term = f"%{q}%"
        query = query.where(
            or_(
                Todo.title.ilike(search_term),
                Todo.description.ilike(search_term)
            )
        )

    # Status filter
    if status_filter == "active":
        query = query.where(Todo.completed == False)
    elif status_filter == "completed":
        query = query.where(Todo.completed == True)

    # Priority filter
    if priority:
        priority_list = [p.strip().upper() for p in priority.split(',')]
        valid_priorities = [p for p in priority_list if p in [e.value for e in Priority]]
        if valid_priorities:
            query = query.where(cast(Todo.priority, SQLAString).in_(valid_priorities))

    # Tags filter (AND logic - todo must have ALL specified tags)
    if tags:
        tags_list = [t.strip().lower() for t in tags.split(',')]
        for tag in tags_list:
            # PostgreSQL array contains operator
            query = query.where(text(f"'{tag}' = ANY(tags)"))

    # Due date range filter
    if due_date_from:
        try:
            from_date = datetime.fromisoformat(due_date_from.replace('Z', '+00:00'))
            query = query.where(Todo.due_date >= from_date)
        except ValueError:
            pass

    if due_date_to:
        try:
            to_date = datetime.fromisoformat(due_date_to.replace('Z', '+00:00'))
            query = query.where(Todo.due_date <= to_date)
        except ValueError:
            pass

    # Count total matches (before pagination)
    count_query = select(func.count()).select_from(query.subquery())
    total_count = session.exec(count_query).one()

    # Sorting
    sort_field_map = {
        "created_at": Todo.created_at,
        "updated_at": Todo.updated_at,
        "due_date": Todo.due_date,
        "priority": Todo.priority,
        "title": Todo.title
    }

    if sort_by in sort_field_map:
        sort_column = sort_field_map[sort_by]
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

    # Pagination
    query = query.offset(offset).limit(limit)

    # Execute query
    results = session.exec(query).all()

    # Return structured response
    return {
        "results": [TodoResponse.model_validate(todo) for todo in results],
        "pagination": {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        },
        "filters_applied": {
            "search": q,
            "status": status_filter or "all",
            "priorities": priority.split(',') if priority else [],
            "tags": tags.split(',') if tags else [],
            "date_range": {
                "due_date_from": due_date_from,
                "due_date_to": due_date_to
            }
        },
        "sorting": {
            "sort_by": sort_by,
            "sort_order": sort_order
        }
    }


@router.get("/{user_id}/v1/tags")
async def list_unique_tags(
    user_id: str,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(get_current_user_id)
) -> List[str]:
    """
    Get all unique tags used by the authenticated user.
    """
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own tags"
        )

    # Query to get unique tags across all user's todos
    result = session.exec(
        select(func.unnest(Todo.tags).label('tag'))
        .where(Todo.user_id == authenticated_user_id)
        .where(Todo.tags.isnot(None))
        .distinct()
    ).all()

    return sorted([tag for tag in result if tag])


@router.get("/{user_id}/v1/tags/autocomplete")
async def autocomplete_tags(
    user_id: str,
    q: str = Query(..., description="Prefix to search for"),
    limit: int = Query(10, ge=1, le=50),
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(get_current_user_id)
) -> List[Dict[str, Any]]:
    """
    Get tag suggestions based on prefix (for autocomplete).
    Returns [{tag, count}] to match TagSuggestion frontend type.
    """
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only autocomplete your own tags"
        )

    # Get tags with frequency counts
    result = session.exec(
        select(
            func.unnest(Todo.tags).label('tag'),
            func.count().label('count')
        )
        .where(Todo.user_id == authenticated_user_id)
        .where(Todo.tags.isnot(None))
        .group_by(text('tag'))
        .order_by(text('count DESC'))
    ).all()

    # Filter by prefix
    prefix = q.lower()
    matching = [
        {"tag": row[0], "count": row[1]}
        for row in result
        if row[0] and row[0].lower().startswith(prefix)
    ]

    return matching[:limit]


@router.get("/{user_id}/v1/tags/popular")
async def get_popular_tags(
    user_id: str,
    limit: int = Query(10, ge=1, le=50),
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(get_current_user_id)
) -> List[Dict[str, Any]]:
    """
    Get most frequently used tags with usage counts.
    """
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own tags"
        )

    # Get tag frequency counts
    result = session.exec(
        select(
            func.unnest(Todo.tags).label('tag'),
            func.count().label('count')
        )
        .where(Todo.user_id == authenticated_user_id)
        .where(Todo.tags.isnot(None))
        .group_by(text('tag'))
        .order_by(text('count DESC'))
        .limit(limit)
    ).all()

    return [{"tag": row[0], "count": row[1]} for row in result if row[0]]
