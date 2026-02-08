"""
Todo Service - Phase V.2
Microservice for TODO CRUD operations with Priority and Event Publishing
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime
import logging
import httpx
import os
import json
import uuid
import asyncpg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dapr configuration
DAPR_SIDECAR_URL = os.getenv("DAPR_HTTP_ENDPOINT", "http://localhost:3500")
STATE_STORE_NAME = "statestore"
PUBSUB_NAME = "pubsub"

# PostgreSQL configuration for direct database access (F5: Full-Text Search)
DB_HOST = os.getenv("DB_HOST", "postgresql.todo-app-dev.svc.cluster.local")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "todoapp_db")
DB_USER = os.getenv("DB_USER", "todoapp")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dev_password")

# Global database connection pool (lazy initialized)
db_pool = None

async def get_db_pool():
    """Get or create database connection pool"""
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            min_size=1,
            max_size=10
        )
    return db_pool

# Priority enumeration (F3)
class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

# Pydantic models
class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Priority = Field(default=Priority.MEDIUM)
    tags: List[str] = Field(default_factory=list)  # F4: Tags support
    due_date: Optional[str] = Field(default=None, description="Due date in ISO 8601 format (e.g., '2026-12-31T23:59:59Z')")  # T066: Reminder support

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[Priority] = None
    completed: Optional[bool] = None
    tags: Optional[List[str]] = None  # F4: Tags can be updated
    due_date: Optional[str] = None  # T066: Update due date

class TodoResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    priority: Priority
    completed: bool
    tags: List[str]  # F4: Tags in response
    due_date: Optional[str] = None  # T066: Due date in response
    created_at: str
    updated_at: str
    user_id: str

# Initialize FastAPI app
app = FastAPI(
    title="Todo Service",
    description="Microservice for managing TODO items with Priority and Events",
    version="2.0.0"
)

# Helper functions for Dapr State Store
async def save_todo_to_state(todo_id: str, todo_data: dict):
    """Save todo to Dapr State Store"""
    async with httpx.AsyncClient() as client:
        save_url = f"{DAPR_SIDECAR_URL}/v1.0/state/{STATE_STORE_NAME}"
        payload = [{"key": f"todo:{todo_id}", "value": todo_data}]
        response = await client.post(save_url, json=payload)
        if response.status_code != 204:
            raise HTTPException(status_code=500, detail="Failed to save todo to state store")

async def get_todo_from_state(todo_id: str) -> Optional[dict]:
    """Retrieve todo from Dapr State Store"""
    async with httpx.AsyncClient() as client:
        get_url = f"{DAPR_SIDECAR_URL}/v1.0/state/{STATE_STORE_NAME}/todo:{todo_id}"
        response = await client.get(get_url)
        if response.status_code == 200:
            data = response.json()
            return data if data else None
        return None

async def delete_todo_from_state(todo_id: str):
    """Delete todo from Dapr State Store"""
    async with httpx.AsyncClient() as client:
        delete_url = f"{DAPR_SIDECAR_URL}/v1.0/state/{STATE_STORE_NAME}/todo:{todo_id}"
        response = await client.delete(delete_url)
        if response.status_code != 204:
            raise HTTPException(status_code=500, detail="Failed to delete todo from state store")

async def publish_event(topic: str, event_data: dict):
    """Publish CloudEvents v1.0 compliant event to Dapr Pub/Sub"""
    async with httpx.AsyncClient() as client:
        publish_url = f"{DAPR_SIDECAR_URL}/v1.0/publish/{PUBSUB_NAME}/{topic}"

        # CloudEvents v1.0 structure
        cloud_event = {
            "specversion": "1.0",
            "type": f"com.todoapp.{topic}",
            "source": "todo-service",
            "id": str(uuid.uuid4()),
            "time": datetime.utcnow().isoformat() + "Z",
            "datacontenttype": "application/json",
            "data": event_data
        }

        response = await client.post(publish_url, json=cloud_event)
        if response.status_code not in [200, 204]:
            logger.error(f"Failed to publish event to {topic}: {response.text}")
            raise HTTPException(status_code=500, detail="Failed to publish event")

@app.get("/health/ready")
async def readiness_probe():
    """
    Kubernetes readiness probe endpoint.
    Returns 200 when service is ready to accept traffic.
    """
    return JSONResponse(
        status_code=200,
        content={"status": "ready", "service": "todo-service"}
    )

@app.get("/health/live")
async def liveness_probe():
    """
    Kubernetes liveness probe endpoint.
    Returns 200 when service is alive.
    """
    return JSONResponse(
        status_code=200,
        content={"status": "alive", "service": "todo-service"}
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "todo-service",
        "version": "2.0.0",
        "status": "operational",
        "features": ["priority-levels", "event-driven"]
    }

@app.post("/todos", response_model=TodoResponse, status_code=201)
async def create_todo(todo: TodoCreate, user_id: str = "default-user"):
    """
    Create a new TODO item (F3: with Priority, F4: with Tags)
    Publishes: todo.created event
    """
    todo_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"

    # Normalize tags: lowercase, unique, sorted
    normalized_tags = sorted(list(set(tag.lower().strip() for tag in todo.tags if tag.strip())))

    todo_data = {
        "id": todo_id,
        "title": todo.title,
        "description": todo.description,
        "priority": todo.priority.value,
        "tags": normalized_tags,  # F4: Tags stored
        "due_date": todo.due_date,  # T066: Store due date
        "completed": False,
        "created_at": now,
        "updated_at": now,
        "user_id": user_id
    }

    # Save to state store
    await save_todo_to_state(todo_id, todo_data)

    # Publish event
    await publish_event("todo.created", todo_data)

    logger.info(f"Created todo {todo_id} with priority {todo.priority} and tags {normalized_tags}")
    return TodoResponse(**todo_data)

@app.get("/todos", response_model=List[TodoResponse])
async def list_todos(
    user_id: str = "default-user",
    priority: Optional[Priority] = None,
    completed: Optional[bool] = None
):
    """
    List all TODO items with optional filters (F3: Priority filtering)
    """
    # Note: In production, this would use bulk query or index
    # For Phase V.2 MVP, returning empty list (would need index implementation)
    logger.info(f"List todos for user {user_id}, priority={priority}, completed={completed}")
    return []

@app.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: str, user_id: str = "default-user"):
    """Get a specific TODO item by ID"""
    todo_data = await get_todo_from_state(todo_id)

    if not todo_data:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todo_data.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this todo")

    return TodoResponse(**todo_data)

@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: str, todo_update: TodoUpdate, user_id: str = "default-user"):
    """
    Update a TODO item (F3: Priority can be updated, F4: Tags can be updated)
    Publishes: todo.updated event
    """
    todo_data = await get_todo_from_state(todo_id)

    if not todo_data:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todo_data.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this todo")

    # Update fields
    if todo_update.title is not None:
        todo_data["title"] = todo_update.title
    if todo_update.description is not None:
        todo_data["description"] = todo_update.description
    if todo_update.priority is not None:
        todo_data["priority"] = todo_update.priority.value
    if todo_update.tags is not None:  # F4: Update tags
        # Normalize tags: lowercase, unique, sorted
        todo_data["tags"] = sorted(list(set(tag.lower().strip() for tag in todo_update.tags if tag.strip())))
    if todo_update.due_date is not None:  # T066: Update due date
        todo_data["due_date"] = todo_update.due_date
    if todo_update.completed is not None:
        was_completed = todo_data["completed"]
        todo_data["completed"] = todo_update.completed

        # If marked completed, publish todo.completed event
        if not was_completed and todo_update.completed:
            await publish_event("todo.completed", todo_data)

    todo_data["updated_at"] = datetime.utcnow().isoformat() + "Z"

    # Save updated todo
    await save_todo_to_state(todo_id, todo_data)

    # Publish update event
    await publish_event("todo.updated", todo_data)

    logger.info(f"Updated todo {todo_id}")
    return TodoResponse(**todo_data)

@app.delete("/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: str, user_id: str = "default-user"):
    """
    Delete a TODO item
    Publishes: todo.deleted event
    """
    todo_data = await get_todo_from_state(todo_id)

    if not todo_data:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todo_data.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this todo")

    # Delete from state store
    await delete_todo_from_state(todo_id)

    # Publish deletion event
    await publish_event("todo.deleted", {"id": todo_id, "user_id": user_id})

    logger.info(f"Deleted todo {todo_id}")
    return None

@app.get("/tags", response_model=List[str])
async def list_tags(user_id: str = "default-user"):
    """
    Phase V.4: List all unique tags used by user's todos

    Uses the existing GIN index on tags for efficient retrieval.
    Returns alphabetically sorted list of all tags across user's TODOs.

    Args:
        user_id: User ID filter (default: "default-user")

    Returns:
        List of unique tag strings (sorted alphabetically)

    Example:
        GET /tags
        Response: ["api", "backend", "frontend", "urgent"]
    """
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Query distinct tags using jsonb_array_elements_text
            # This leverages the GIN index on value->'tags'
            query = """
                SELECT DISTINCT tag_elem as tag
                FROM dapr_state ds,
                jsonb_array_elements_text(ds.value->'tags') as tag_elem
                WHERE ds.key LIKE '%||todo:%'
                  AND (ds.value->>'user_id') = $1
                ORDER BY tag_elem
            """
            rows = await conn.fetch(query, user_id)
            tags = [row['tag'] for row in rows]

            logger.info(f"Retrieved {len(tags)} unique tags for user {user_id}")
            return tags

    except Exception as e:
        logger.error(f"Failed to list tags: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list tags: {str(e)}")

@app.get("/api/v1/tags/autocomplete")
async def autocomplete_tags(
    q: str,
    user_id: str = "default-user",
    limit: int = 10
):
    """
    Phase V.4: Tag autocomplete API for frontend search UX

    Provides tag suggestions matching a prefix query, sorted by usage frequency
    to prioritize commonly used tags in autocomplete dropdowns.

    Args:
        q: Prefix query string (case-insensitive)
        user_id: User ID filter (default: "default-user")
        limit: Maximum suggestions to return (default: 10, max: 20)

    Returns:
        JSON array of tag objects with usage counts:
        [
          {"tag": "backend", "count": 15},
          {"tag": "backend-api", "count": 8}
        ]

    Performance:
        - Target p95 latency: < 20ms
        - Uses GIN index on tags for efficient matching

    Examples:
        GET /api/v1/tags/autocomplete?q=back
        GET /api/v1/tags/autocomplete?q=api&limit=5
    """
    try:
        # Validate and sanitize parameters
        limit = min(max(1, limit), 20)
        prefix = q.strip().lower()

        if not prefix:
            return []

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Query tags matching prefix, ordered by usage frequency
            query = """
                SELECT tag_elem as tag, COUNT(*) as usage_count
                FROM dapr_state ds,
                jsonb_array_elements_text(ds.value->'tags') as tag_elem
                WHERE ds.key LIKE '%||todo:%'
                  AND (ds.value->>'user_id') = $1
                  AND tag_elem ILIKE $2 || '%'
                GROUP BY tag_elem
                ORDER BY usage_count DESC, tag_elem ASC
                LIMIT $3
            """
            rows = await conn.fetch(query, user_id, prefix, limit)

            results = [
                {"tag": row['tag'], "count": row['usage_count']}
                for row in rows
            ]

            logger.info(f"Autocomplete '{prefix}' returned {len(results)} suggestions for user {user_id}")
            return results

    except Exception as e:
        logger.error(f"Tag autocomplete failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tag autocomplete failed: {str(e)}")

@app.get("/api/v1/tags/popular")
async def get_popular_tags(
    user_id: str = "default-user",
    limit: int = 20,
    days: int = 90
):
    """
    Phase V.4: Popular tags API for quick filtering

    Returns most frequently used tags across user's TODOs within a time window,
    sorted by usage frequency. Helps users discover and filter by their most
    common tags.

    Args:
        user_id: User ID filter (default: "default-user")
        limit: Maximum tags to return (default: 20, max: 50)
        days: Time window in days (default: 90, max: 365)

    Returns:
        JSON array of tag objects with usage counts:
        [
          {"tag": "urgent", "count": 42, "percentage": 15.2},
          {"tag": "backend", "count": 38, "percentage": 13.8}
        ]

    Performance:
        - Target p95 latency: < 30ms
        - Uses GIN index on tags + created_at index

    Examples:
        GET /api/v1/tags/popular
        GET /api/v1/tags/popular?limit=10&days=30
    """
    try:
        from datetime import datetime, timedelta, timezone

        # Validate and sanitize parameters
        limit = min(max(1, limit), 50)
        days = min(max(1, days), 365)

        # Calculate time window cutoff
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Get total TODO count for percentage calculation
            total_query = """
                SELECT COUNT(*) as total
                FROM dapr_state
                WHERE key LIKE '%||todo:%'
                  AND (value->>'user_id') = $1
                  AND (value->>'created_at') >= $2
            """
            total_result = await conn.fetchrow(total_query, user_id, cutoff_date)
            total_todos = total_result['total'] if total_result else 0

            if total_todos == 0:
                return []

            # Query popular tags with usage counts
            query = """
                SELECT tag_elem as tag, COUNT(*) as usage_count
                FROM dapr_state ds,
                jsonb_array_elements_text(ds.value->'tags') as tag_elem
                WHERE ds.key LIKE '%||todo:%'
                  AND (ds.value->>'user_id') = $1
                  AND (ds.value->>'created_at') >= $2
                GROUP BY tag_elem
                ORDER BY usage_count DESC, tag_elem ASC
                LIMIT $3
            """
            rows = await conn.fetch(query, user_id, cutoff_date, limit)

            results = [
                {
                    "tag": row['tag'],
                    "count": row['usage_count'],
                    "percentage": round((row['usage_count'] / total_todos) * 100, 1)
                }
                for row in rows
            ]

            logger.info(f"Retrieved {len(results)} popular tags (last {days} days) for user {user_id}")
            return results

    except Exception as e:
        logger.error(f"Popular tags query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Popular tags query failed: {str(e)}")

@app.get("/api/v1/todos/search")
async def search_todos(
    user_id: str = "default-user",
    q: Optional[str] = None,
    fuzzy: bool = False,
    similarity_threshold: float = 0.3,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[str] = None,
    due_date_from: Optional[str] = None,
    due_date_to: Optional[str] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = 20,
    offset: int = 0
):
    """
    Phase V.4: Advanced Search with filtering, sorting, and pagination

    Search and filter TODOs with multiple criteria. Backward compatible with Phase V.3 search.

    Query Parameters:
    - q: Search query for full-text or fuzzy matching (optional)
    - fuzzy: Enable fuzzy matching for typos (default: False)
    - similarity_threshold: Min similarity for fuzzy (0.0-1.0, default: 0.3)

    Filters (NEW in V.4):
    - status: 'all' | 'active' | 'completed' (default: 'all')
    - priority: Comma-separated priorities (e.g., 'HIGH,URGENT')
    - tags: Comma-separated tags (AND logic, e.g., 'backend,api')
    - due_date_from: ISO8601 date (e.g., '2026-02-10T00:00:00Z')
    - due_date_to: ISO8601 date (e.g., '2026-02-20T23:59:59Z')
    - created_after: ISO8601 date
    - created_before: ISO8601 date

    Sorting (NEW in V.4):
    - sort_by: 'created_at' | 'updated_at' | 'due_date' | 'priority' | 'title' (default: 'created_at')
    - sort_order: 'asc' | 'desc' (default: 'desc')

    Pagination:
    - limit: Max results (1-100, default: 20)
    - offset: Skip N results (default: 0)

    Returns:
        JSON with results, pagination, filters_applied, sorting metadata

    Examples:
        GET /api/v1/todos/search?status=active&sort_by=due_date
        GET /api/v1/todos/search?q=backend&priority=HIGH,URGENT&tags=api,python
        GET /api/v1/todos/search?due_date_to=2026-02-10T00:00:00Z&status=active
    """
    try:
        # Validate and sanitize parameters
        limit = min(max(1, limit), 100)
        offset = max(0, offset)
        similarity_threshold = max(0.0, min(1.0, similarity_threshold))

        # Parse comma-separated lists
        priority_list = [p.strip().upper() for p in priority.split(',')] if priority else []
        tags_list = [t.strip().lower() for t in tags.split(',')] if tags else []

        # Validate sort_by values
        valid_sort_fields = ['created_at', 'updated_at', 'due_date', 'priority', 'title']
        if sort_by not in valid_sort_fields:
            raise HTTPException(status_code=400, detail=f"Invalid sort_by. Must be one of: {', '.join(valid_sort_fields)}")

        # Validate sort_order
        if sort_order.lower() not in ['asc', 'desc']:
            raise HTTPException(status_code=400, detail="Invalid sort_order. Must be 'asc' or 'desc'")

        # Get database connection pool
        pool = await get_db_pool()

        # Build dynamic query
        query_parts = ["SELECT key, value"]
        params = [user_id]
        param_index = 2

        # Add rank column if searching
        if q:
            if fuzzy:
                query_parts.append(", GREATEST(similarity(COALESCE(value->>'title', ''), $2), similarity(COALESCE(value->>'description', ''), $2)) as rank")
            else:
                query_parts.append(f", ts_rank(search_vector, to_tsquery('english', ${param_index})) as rank")
            params.append(' & '.join(q.strip().split()) if not fuzzy else q.strip())
            param_index += 1

        query_parts.append("FROM dapr_state")
        query_parts.append("WHERE key LIKE '%||todo:%'")
        query_parts.append("AND (value->>'user_id') = $1")

        # Full-text or fuzzy search
        if q:
            if fuzzy:
                query_parts.append(f"AND (similarity(COALESCE(value->>'title', ''), ${param_index - 1}) > ${param_index} OR similarity(COALESCE(value->>'description', ''), ${param_index - 1}) > ${param_index})")
                params.append(similarity_threshold)
                param_index += 1
            else:
                query_parts.append(f"AND search_vector @@ to_tsquery('english', ${param_index - 1})")

        # Status filter
        if status == 'active':
            query_parts.append(f"AND (value->>'completed')::boolean = ${param_index}")
            params.append(False)
            param_index += 1
        elif status == 'completed':
            query_parts.append(f"AND (value->>'completed')::boolean = ${param_index}")
            params.append(True)
            param_index += 1

        # Priority filter
        if priority_list:
            placeholders = ', '.join([f'${param_index + i}' for i in range(len(priority_list))])
            query_parts.append(f"AND (value->>'priority') IN ({placeholders})")
            params.extend(priority_list)
            param_index += len(priority_list)

        # Tags filter (array containment)
        if tags_list:
            query_parts.append(f"AND value->'tags' @> ${param_index}::jsonb")
            params.append(json.dumps(tags_list))
            param_index += 1

        # Due date range
        if due_date_from and due_date_to:
            query_parts.append(f"AND (value->>'due_date') BETWEEN ${param_index} AND ${param_index + 1}")
            params.extend([due_date_from, due_date_to])
            param_index += 2
        elif due_date_from:
            query_parts.append(f"AND (value->>'due_date') >= ${param_index}")
            params.append(due_date_from)
            param_index += 1
        elif due_date_to:
            query_parts.append(f"AND (value->>'due_date') <= ${param_index}")
            params.append(due_date_to)
            param_index += 1

        # Created date range
        if created_after:
            query_parts.append(f"AND (value->>'created_at') >= ${param_index}")
            params.append(created_after)
            param_index += 1
        if created_before:
            query_parts.append(f"AND (value->>'created_at') <= ${param_index}")
            params.append(created_before)
            param_index += 1

        # Sorting
        if q and not sort_by:
            # Default: rank by relevance when searching
            query_parts.append("ORDER BY rank DESC")
        elif sort_by == 'priority':
            priority_order = "CASE (value->>'priority') WHEN 'URGENT' THEN 4 WHEN 'HIGH' THEN 3 WHEN 'MEDIUM' THEN 2 ELSE 1 END"
            query_parts.append(f"ORDER BY {priority_order} {sort_order.upper()}")
        elif sort_by == 'due_date':
            query_parts.append(f"ORDER BY (value->>'due_date') {sort_order.upper()} NULLS LAST")
        else:
            query_parts.append(f"ORDER BY (value->>'{sort_by}') {sort_order.upper()}")

        # Pagination
        query_parts.append(f"LIMIT ${param_index}")
        params.append(limit)
        param_index += 1

        query_parts.append(f"OFFSET ${param_index}")
        params.append(offset)

        # Execute query
        async with pool.acquire() as conn:
            query_sql = '\n'.join(query_parts)
            rows = await conn.fetch(query_sql, *params)

            # Get total count (for pagination metadata)
            # Build a clean count query from the WHERE clauses only
            count_parts = ["SELECT COUNT(*)", "FROM dapr_state"]
            # Copy all WHERE clauses (skip SELECT and ORDER BY parts)
            for part in query_parts:
                if part.startswith("WHERE") or part.startswith("AND"):
                    count_parts.append(part)
            count_query = '\n'.join(count_parts)
            # Use params without limit/offset (last 2 params)
            total_count = await conn.fetchval(count_query, *params[:-2])

            # Convert results to TodoResponse
            results = []
            for row in rows:
                todo_data = row['value']
                if isinstance(todo_data, str):
                    todo_data = json.loads(todo_data)

                # Ensure backward compatibility
                if 'tags' not in todo_data:
                    todo_data['tags'] = []

                # Add rank if present
                result_dict = TodoResponse(**todo_data).dict()
                if 'rank' in row:
                    result_dict['rank'] = float(row['rank'])

                results.append(result_dict)

            # Build response with metadata
            response = {
                "results": results,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count
                },
                "filters_applied": {
                    "search": q,
                    "status": status or "all",
                    "priorities": priority_list,
                    "tags": tags_list,
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

            logger.info(f"Advanced search returned {len(results)} of {total_count} results for user {user_id}")
            return JSONResponse(content=response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/smoke-test")
async def smoke_test():
    """
    Smoke test endpoint for Phase V.1 - Tests Dapr State Store integration
    """
    try:
        # Save test data to Dapr State Store
        async with httpx.AsyncClient() as client:
            save_url = f"{DAPR_SIDECAR_URL}/v1.0/state/{STATE_STORE_NAME}"
            test_data = [{
                "key": "smoke-test",
                "value": {
                    "message": "Phase V.1 smoke test successful",
                    "service": "todo-service",
                    "dapr_enabled": True
                }
            }]
            save_response = await client.post(save_url, json=test_data)

            if save_response.status_code != 204:
                return JSONResponse(
                    status_code=500,
                    content={"status": "failed", "error": "Failed to save to state store"}
                )

            # Retrieve test data from Dapr State Store
            get_url = f"{DAPR_SIDECAR_URL}/v1.0/state/{STATE_STORE_NAME}/smoke-test"
            get_response = await client.get(get_url)

            if get_response.status_code == 200:
                return {
                    "status": "success",
                    "message": "Dapr State Store integration verified",
                    "data": get_response.json()
                }
            else:
                return JSONResponse(
                    status_code=500,
                    content={"status": "failed", "error": "Failed to retrieve from state store"}
                )

    except Exception as e:
        logger.error(f"Smoke test failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "failed", "error": str(e)}
        )

@app.post("/check-reminders")
async def check_reminders():
    """
    T066: Check for TODOs with due dates approaching and publish reminder events

    This endpoint scans all TODOs for upcoming due dates and publishes
    reminder events to the `todo.reminder.due` Kafka topic.

    In production, this would be called by a scheduled job (e.g., Kubernetes CronJob)
    running every hour or as needed.

    Returns:
        Summary of reminders checked and events published
    """
    try:
        from datetime import datetime, timedelta, timezone

        # Get current time and reminder window (e.g., 1 hour from now)
        now = datetime.now(timezone.utc)
        reminder_window = now + timedelta(hours=1)

        # Query all todos with due dates via direct database access
        pool = await get_db_pool()
        reminders_sent = 0

        async with pool.acquire() as conn:
            # Find TODOs with due dates in the next hour that aren't completed
            query = """
                SELECT key, value
                FROM dapr_state
                WHERE key LIKE '%||todo:%'
                  AND (value->>'completed')::boolean = false
                  AND value->>'due_date' IS NOT NULL
            """

            rows = await conn.fetch(query)

            for row in rows:
                todo_data = row['value']
                # Handle potential string-encoded JSON from asyncpg
                if isinstance(todo_data, str):
                    todo_data = json.loads(todo_data)
                due_date_str = todo_data.get('due_date')

                if not due_date_str:
                    continue

                try:
                    # Parse due date
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))

                    # Debug logging
                    logger.debug(f"Checking TODO {todo_data['id']}: now={now}, due={due_date}, window={reminder_window}, in_window={now <= due_date <= reminder_window}")

                    # Check if due date is within reminder window
                    if now <= due_date <= reminder_window:
                        # Publish reminder event
                        reminder_event = {
                            "todo_id": todo_data['id'],
                            "title": todo_data['title'],
                            "description": todo_data.get('description'),
                            "priority": todo_data['priority'],
                            "due_date": due_date_str,
                            "user_id": todo_data['user_id'],
                            "reminder_time": now.isoformat().replace('+00:00', 'Z')
                        }

                        await publish_event("todo.reminder.due", reminder_event)
                        reminders_sent += 1
                        logger.info(f"Published reminder for TODO {todo_data['id']}: {todo_data['title']}")

                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to parse due date for TODO {todo_data.get('id')}: {e}")
                    continue

        return {
            "status": "success",
            "reminders_checked": len(rows) if rows else 0,
            "reminders_sent": reminders_sent,
            "check_time": now.isoformat().replace('+00:00', 'Z'),
            "reminder_window_hours": 1
        }

    except Exception as e:
        logger.error(f"Reminder check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Reminder check failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
