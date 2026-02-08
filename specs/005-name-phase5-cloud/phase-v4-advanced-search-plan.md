# Phase V.4: Advanced Search & Filtering - Implementation Plan

**Date**: 2026-02-06
**Status**: 🔵 IN PROGRESS
**Phase**: V.4 - Advanced Features with Frontend Integration

---

## Executive Summary

Phase V.4 extends the basic full-text search (Phase V.3) with advanced filtering, sorting, tagging, priorities, and frontend integration. This phase focuses on making features **visibly accessible** in the UI while maintaining Oracle Free Tier compliance.

---

## Current State Analysis

### Existing Infrastructure (Phase V.3)
- ✅ Full-text search with PostgreSQL tsvector + GIN indexes
- ✅ Fuzzy matching with pg_trgm trigram indexes
- ✅ Basic pagination (limit/offset)
- ✅ User-scoped queries
- ✅ Priority enum (LOW, MEDIUM, HIGH, URGENT)
- ✅ Tags array field (stored but not filterable)
- ✅ Due date field (stored but not filterable)

### Database Schema (dapr_state JSONB)
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string | null",
  "priority": "LOW | MEDIUM | HIGH | URGENT",
  "tags": ["string"],
  "due_date": "ISO8601 | null",
  "completed": "boolean",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "user_id": "string"
}
```

### Existing Indexes
- `idx_dapr_state_search_vector` - GIN on search_vector (full-text)
- `idx_dapr_state_title_trgm` - GIN on title (fuzzy)
- `idx_dapr_state_description_trgm` - GIN on description (fuzzy)
- `idx_dapr_state_todo_keys` - Partial B-tree on todo keys

---

## V4-T001: Advanced Search API Design

### 1. Enhanced Search Endpoint

**Endpoint**: `GET /api/v1/todos/search`

**Query Parameters** (backward compatible with Phase V.3):

#### Search & Fuzzy (Existing)
- `q` (string, optional): Search query for full-text or fuzzy matching
- `fuzzy` (boolean, default: false): Enable fuzzy matching for typos
- `similarity_threshold` (float, default: 0.3): Min similarity for fuzzy (0.0-1.0)

#### Filtering (NEW)
- `status` (string, optional): Filter by completion status
  - Values: `all` | `active` | `completed`
  - Default: `all`
- `priority` (string, optional): Filter by priority levels (comma-separated)
  - Values: `LOW`, `MEDIUM`, `HIGH`, `URGENT`
  - Example: `priority=HIGH,URGENT`
- `tags` (string, optional): Filter by tags (comma-separated, AND logic)
  - Example: `tags=backend,urgent`
- `due_date_from` (ISO8601, optional): Filter TODOs due after this date
  - Example: `due_date_from=2026-02-10T00:00:00Z`
- `due_date_to` (ISO8601, optional): Filter TODOs due before this date
  - Example: `due_date_to=2026-02-20T23:59:59Z`
- `created_after` (ISO8601, optional): Filter by creation date (after)
- `created_before` (ISO8601, optional): Filter by creation date (before)

#### Sorting (NEW)
- `sort_by` (string, optional): Field to sort by
  - Values: `created_at` | `updated_at` | `due_date` | `priority` | `title`
  - Default: `created_at` (for list), relevance rank (for search with q)
- `sort_order` (string, optional): Sort direction
  - Values: `asc` | `desc`
  - Default: `desc` (newest first)

#### Pagination (Existing)
- `limit` (int, default: 20, max: 100): Max results per page
- `offset` (int, default: 0): Number of results to skip

### 2. API Response Format

```json
{
  "results": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string | null",
      "priority": "LOW | MEDIUM | HIGH | URGENT",
      "tags": ["string"],
      "due_date": "ISO8601 | null",
      "completed": boolean,
      "created_at": "ISO8601",
      "updated_at": "ISO8601",
      "user_id": "string",
      "rank": float | null  // Only present when q parameter used
    }
  ],
  "pagination": {
    "total": int,
    "limit": int,
    "offset": int,
    "has_more": boolean
  },
  "filters_applied": {
    "search": "string | null",
    "status": "string",
    "priorities": ["string"],
    "tags": ["string"],
    "date_range": {
      "due_date_from": "ISO8601 | null",
      "due_date_to": "ISO8601 | null"
    }
  },
  "sorting": {
    "sort_by": "string",
    "sort_order": "string"
  }
}
```

### 3. Example API Calls

#### Search with Multiple Filters
```bash
GET /api/v1/todos/search?q=backend&priority=HIGH,URGENT&tags=api,python&status=active&sort_by=due_date&sort_order=asc&limit=20
```

#### List All Active TODOs Sorted by Priority
```bash
GET /api/v1/todos/search?status=active&sort_by=priority&sort_order=desc
```

#### Find Overdue TODOs
```bash
GET /api/v1/todos/search?due_date_to=2026-02-06T00:00:00Z&status=active&sort_by=due_date&sort_order=asc
```

#### Tag-Based Filtering
```bash
GET /api/v1/todos/search?tags=backend,urgent&sort_by=created_at&sort_order=desc
```

---

## V4-T002: Database Indexing Strategy

### 1. New Indexes Required

#### Index 1: Completed Status (for filtering active/completed)
```sql
CREATE INDEX idx_dapr_state_completed
ON dapr_state ((value->>'completed'))
WHERE key LIKE '%||todo:%';
```
**Purpose**: Fast filtering by completion status
**Size Estimate**: ~50KB per 1000 TODOs
**Impact**: Speeds up `status=active` queries by 100x

#### Index 2: Priority Filtering
```sql
CREATE INDEX idx_dapr_state_priority
ON dapr_state ((value->>'priority'))
WHERE key LIKE '%||todo:%';
```
**Purpose**: Fast priority-based filtering
**Size Estimate**: ~40KB per 1000 TODOs
**Impact**: Enables efficient multi-priority queries

#### Index 3: Tags (GIN Index for Array Containment)
```sql
CREATE INDEX idx_dapr_state_tags
ON dapr_state USING GIN ((value->'tags'))
WHERE key LIKE '%||todo:%';
```
**Purpose**: Fast tag-based filtering with @> operator
**Size Estimate**: ~100KB per 1000 TODOs (larger due to GIN)
**Impact**: Enables `WHERE value->'tags' @> '["backend","api"]'::jsonb`

#### Index 4: Due Date Range Filtering
```sql
CREATE INDEX idx_dapr_state_due_date
ON dapr_state ((value->>'due_date'))
WHERE key LIKE '%||todo:%' AND value->>'due_date' IS NOT NULL;
```
**Purpose**: Fast date range queries
**Size Estimate**: ~60KB per 1000 TODOs
**Impact**: Enables efficient `due_date_from`/`due_date_to` filtering

#### Index 5: Created At (for default sorting)
```sql
CREATE INDEX idx_dapr_state_created_at
ON dapr_state ((value->>'created_at'))
WHERE key LIKE '%||todo:%';
```
**Purpose**: Fast sorting by creation date
**Size Estimate**: ~50KB per 1000 TODOs
**Impact**: Default sort performance improvement

#### Index 6: Updated At
```sql
CREATE INDEX idx_dapr_state_updated_at
ON dapr_state ((value->>'updated_at'))
WHERE key LIKE '%||todo:%';
```
**Purpose**: Fast sorting by update timestamp
**Size Estimate**: ~50KB per 1000 TODOs

#### Index 7: Composite Index for Common Query Pattern
```sql
CREATE INDEX idx_dapr_state_user_completed_created
ON dapr_state (
    (value->>'user_id'),
    (value->>'completed'),
    (value->>'created_at') DESC
)
WHERE key LIKE '%||todo:%';
```
**Purpose**: Optimizes most common query: user's active TODOs sorted by creation
**Size Estimate**: ~100KB per 1000 TODOs
**Impact**: 10-50x faster for default dashboard queries

### 2. Index Size Budget (Oracle Free Tier)

**Total Estimated Index Size** (for 10,000 TODOs):
- Completed: ~500KB
- Priority: ~400KB
- Tags (GIN): ~1MB
- Due Date: ~600KB
- Created At: ~500KB
- Updated At: ~500KB
- Composite: ~1MB
- **TOTAL**: ~5MB

**Current Disk Usage**: ~8GB / 20GB (40%)
**After Indexes**: ~8.005GB / 20GB (40.025%)
✅ **Safe for Oracle Free Tier**

### 3. Migration File Structure

**File**: `services/todo-service/migrations/005_add_advanced_search_indexes.sql`

```sql
-- Migration: Add indexes for advanced filtering and sorting
-- Phase V.4 - Advanced Search & Filtering
-- Date: 2026-02-06

-- Index 1: Completed status filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dapr_state_completed
ON dapr_state ((value->>'completed'))
WHERE key LIKE '%||todo:%';

-- Index 2: Priority filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dapr_state_priority
ON dapr_state ((value->>'priority'))
WHERE key LIKE '%||todo:%';

-- Index 3: Tags array containment (GIN)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dapr_state_tags
ON dapr_state USING GIN ((value->'tags'))
WHERE key LIKE '%||todo:%';

-- Index 4: Due date range queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dapr_state_due_date
ON dapr_state ((value->>'due_date'))
WHERE key LIKE '%||todo:%' AND value->>'due_date' IS NOT NULL;

-- Index 5: Created at sorting
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dapr_state_created_at
ON dapr_state ((value->>'created_at'))
WHERE key LIKE '%||todo:%';

-- Index 6: Updated at sorting
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dapr_state_updated_at
ON dapr_state ((value->>'updated_at'))
WHERE key LIKE '%||todo:%';

-- Index 7: Composite index for common pattern
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dapr_state_user_completed_created
ON dapr_state (
    (value->>'user_id'),
    (value->>'completed'),
    (value->>'created_at') DESC
)
WHERE key LIKE '%||todo:%';

-- Add comments
COMMENT ON INDEX idx_dapr_state_completed IS 'Phase V.4: Fast filtering by completion status';
COMMENT ON INDEX idx_dapr_state_priority IS 'Phase V.4: Fast priority-based filtering';
COMMENT ON INDEX idx_dapr_state_tags IS 'Phase V.4: Fast tag containment queries';
COMMENT ON INDEX idx_dapr_state_due_date IS 'Phase V.4: Fast due date range filtering';
COMMENT ON INDEX idx_dapr_state_created_at IS 'Phase V.4: Fast sorting by creation date';
COMMENT ON INDEX idx_dapr_state_updated_at IS 'Phase V.4: Fast sorting by update date';
COMMENT ON INDEX idx_dapr_state_user_completed_created IS 'Phase V.4: Optimized for dashboard queries';
```

**Note**: Using `CREATE INDEX CONCURRENTLY` to avoid table locking during index creation (important for production).

---

## V4-T003: Search Query Builder Implementation

### 1. Query Construction Strategy

**Approach**: Build dynamic SQL query based on provided filters

**Base Query**:
```sql
SELECT key, value, ts_rank(search_vector, query) as rank
FROM dapr_state
WHERE key LIKE '%||todo:%'
  AND (value->>'user_id') = $1
```

**Dynamic Clauses** (added conditionally):
- Full-text search: `AND search_vector @@ to_tsquery('english', $2)`
- Status filter: `AND (value->>'completed')::boolean = $3`
- Priority filter: `AND (value->>'priority') IN ($4, $5, ...)`
- Tag filter: `AND value->'tags' @> $6::jsonb`
- Due date range: `AND (value->>'due_date') BETWEEN $7 AND $8`
- Created date range: `AND (value->>'created_at') BETWEEN $9 AND $10`

**Dynamic Sorting** (ORDER BY clause):
- `sort_by=created_at`: `ORDER BY (value->>'created_at') DESC`
- `sort_by=due_date`: `ORDER BY (value->>'due_date') DESC NULLS LAST`
- `sort_by=priority`: `ORDER BY CASE (value->>'priority') WHEN 'URGENT' THEN 4 WHEN 'HIGH' THEN 3 WHEN 'MEDIUM' THEN 2 ELSE 1 END DESC`
- `sort_by=title`: `ORDER BY (value->>'title') ASC`
- Default (with q): `ORDER BY rank DESC`
- Default (no q): `ORDER BY (value->>'created_at') DESC`

### 2. Python Implementation Skeleton

```python
async def build_search_query(
    user_id: str,
    q: Optional[str] = None,
    status: Optional[str] = None,
    priorities: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    due_date_from: Optional[str] = None,
    due_date_to: Optional[str] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = 20,
    offset: int = 0
) -> Tuple[str, List[Any]]:
    """
    Build dynamic SQL query with filters and sorting

    Returns:
        (query_string, parameters)
    """
    # Base query
    query_parts = [
        "SELECT key, value"
    ]

    # Add rank if full-text search
    if q:
        query_parts.append(", ts_rank(search_vector, to_tsquery('english', $2)) as rank")

    query_parts.append("FROM dapr_state")
    query_parts.append("WHERE key LIKE '%||todo:%'")
    query_parts.append("AND (value->>'user_id') = $1")

    params = [user_id]
    param_index = 2

    # Full-text search
    if q:
        tsquery = ' & '.join(q.strip().split())
        query_parts.append(f"AND search_vector @@ to_tsquery('english', ${param_index})")
        params.append(tsquery)
        param_index += 1

    # Status filter
    if status == "active":
        query_parts.append(f"AND (value->>'completed')::boolean = ${param_index}")
        params.append(False)
        param_index += 1
    elif status == "completed":
        query_parts.append(f"AND (value->>'completed')::boolean = ${param_index}")
        params.append(True)
        param_index += 1

    # Priority filter (IN clause)
    if priorities:
        placeholders = ', '.join([f'${param_index + i}' for i in range(len(priorities))])
        query_parts.append(f"AND (value->>'priority') IN ({placeholders})")
        params.extend(priorities)
        param_index += len(priorities)

    # Tag filter (array containment)
    if tags:
        import json
        query_parts.append(f"AND value->'tags' @> ${param_index}::jsonb")
        params.append(json.dumps(tags))
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

    # Sorting
    if q and sort_by == "created_at":
        # Default: rank by relevance when searching
        query_parts.append("ORDER BY rank DESC")
    elif sort_by == "priority":
        priority_order = "CASE (value->>'priority') WHEN 'URGENT' THEN 4 WHEN 'HIGH' THEN 3 WHEN 'MEDIUM' THEN 2 ELSE 1 END"
        query_parts.append(f"ORDER BY {priority_order} {sort_order.upper()}")
    elif sort_by == "due_date":
        query_parts.append(f"ORDER BY (value->>'due_date') {sort_order.upper()} NULLS LAST")
    else:
        query_parts.append(f"ORDER BY (value->>'{sort_by}') {sort_order.upper()}")

    # Pagination
    query_parts.append(f"LIMIT ${param_index}")
    params.append(limit)
    param_index += 1

    query_parts.append(f"OFFSET ${param_index}")
    params.append(offset)

    return '\n'.join(query_parts), params
```

---

## V4-T004: Frontend Integration Plan

### 1. Advanced Search UI Component

**Location**: `frontend/src/components/todo/AdvancedSearchPanel.tsx`

**Features**:
- Search input with fuzzy toggle
- Filter dropdowns:
  - Status (All, Active, Completed)
  - Priority (multi-select checkboxes)
  - Tags (multi-select with autocomplete)
  - Due date range picker
- Sort controls:
  - Sort by dropdown (Created, Updated, Due Date, Priority, Title)
  - Sort order toggle (Asc/Desc)
- Clear filters button
- Applied filters chips display

### 2. Dashboard Integration

**Location**: `frontend/src/app/dashboard/page.tsx`

**Enhanced Features**:
- Quick filter buttons: "Active", "Completed", "Overdue", "High Priority"
- Search bar (top of page)
- Advanced filters panel (expandable)
- Sort dropdown (top-right)
- Results display with pagination
- "No results" state with clear filters CTA

### 3. API Integration Hook

**Location**: `frontend/src/hooks/useTodoSearch.ts`

```typescript
export interface SearchFilters {
  q?: string;
  fuzzy?: boolean;
  status?: 'all' | 'active' | 'completed';
  priorities?: string[];
  tags?: string[];
  due_date_from?: string;
  due_date_to?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

export function useTodoSearch(initialFilters?: SearchFilters) {
  const [filters, setFilters] = useState<SearchFilters>(initialFilters || {});
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({});

  const search = useCallback(async (newFilters?: SearchFilters) => {
    const searchParams = new URLSearchParams({
      ...filters,
      ...newFilters
    });

    const response = await fetch(`/api/v1/todos/search?${searchParams}`);
    const data = await response.json();

    setResults(data.results);
    setPagination(data.pagination);
  }, [filters]);

  return { filters, setFilters, results, loading, error, pagination, search };
}
```

---

## V4-T005: Tag Management Features

### 1. Tag Autocomplete API

**Endpoint**: `GET /api/v1/tags/autocomplete?q=<prefix>&limit=10`

**Purpose**: Provide tag suggestions for search filter
**Implementation**: Query distinct tags matching prefix

```python
@app.get("/api/v1/tags/autocomplete")
async def autocomplete_tags(q: str, user_id: str = "default-user", limit: int = 10):
    """
    Get tag suggestions for autocomplete
    Returns tags matching the query prefix
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Query distinct tags using jsonb_array_elements
        query = """
            SELECT DISTINCT tag
            FROM dapr_state,
            jsonb_array_elements_text(value->'tags') as tag
            WHERE key LIKE '%||todo:%'
              AND (value->>'user_id') = $1
              AND tag ILIKE $2 || '%'
            ORDER BY tag
            LIMIT $3
        """
        rows = await conn.fetch(query, user_id, q.lower(), limit)
        return [row['tag'] for row in rows]
```

### 2. Popular Tags API

**Endpoint**: `GET /api/v1/tags/popular?limit=20`

**Purpose**: Show most-used tags for quick filtering

```python
@app.get("/api/v1/tags/popular")
async def get_popular_tags(user_id: str = "default-user", limit: int = 20):
    """
    Get most frequently used tags
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        query = """
            SELECT tag, COUNT(*) as usage_count
            FROM dapr_state,
            jsonb_array_elements_text(value->'tags') as tag
            WHERE key LIKE '%||todo:%'
              AND (value->>'user_id') = $1
            GROUP BY tag
            ORDER BY usage_count DESC, tag
            LIMIT $2
        """
        rows = await conn.fetch(query, user_id, limit)
        return [{"tag": row['tag'], "count": row['usage_count']} for row in rows]
```

---

## Non-Functional Requirements

### 1. Performance Targets
- Search with filters: < 50ms (p95)
- Autocomplete: < 20ms (p95)
- Popular tags: < 30ms (p95)
- Index scan vs seq scan: Verify EXPLAIN shows index usage

### 2. Resource Constraints (Oracle Free Tier)
- ✅ Index size budget: ~5MB (< 1% disk usage)
- ✅ No additional services required
- ✅ Reuse existing PostgreSQL and Dapr infrastructure

### 3. Backward Compatibility
- ✅ All new query parameters are optional
- ✅ Existing `/api/v1/todos/search?q=...` calls continue to work
- ✅ Response format extended (pagination, filters_applied), not breaking

### 4. Security
- ✅ User-scoped queries (all filters respect user_id)
- ✅ SQL injection protection via parameterized queries
- ✅ Input validation (limit <= 100, valid enums, ISO8601 dates)

---

## Implementation Tasks Breakdown

### V4-T001: ✅ COMPLETE (this document)
- API design specification
- Database indexing strategy
- Query builder approach

### V4-T002: Create Database Migration (005_add_advanced_search_indexes.sql)
- 7 new indexes (completed, priority, tags, due_date, created_at, updated_at, composite)
- Apply with `CREATE INDEX CONCURRENTLY`
- Validate index usage with EXPLAIN

### V4-T003: Implement Enhanced Search Endpoint
- Extend `/api/v1/todos/search` with new parameters
- Build dynamic query constructor
- Add comprehensive input validation
- Update response format with pagination metadata

### V4-T004: Implement Tag Management APIs
- `/api/v1/tags/autocomplete` endpoint
- `/api/v1/tags/popular` endpoint
- Update existing `/tags` endpoint to use indexes

### V4-T005: Frontend - Advanced Search Panel Component
- Create `AdvancedSearchPanel.tsx`
- Filter UI (status, priority, tags, dates)
- Sort controls
- Applied filters chips

### V4-T006: Frontend - Dashboard Integration
- Update dashboard page with search/filter UI
- Quick filter buttons
- Results display with pagination
- Create `useTodoSearch` hook

### V4-T007: Integration Testing
- Test all filter combinations
- Verify index usage (EXPLAIN plans)
- Performance benchmarks (< 50ms target)
- Edge cases (empty results, invalid inputs)

### V4-T008: Documentation
- API documentation with examples
- Frontend component usage guide
- Performance tuning recommendations

---

## Success Criteria

1. ✅ All 7 indexes created and validated
2. ✅ Enhanced search API supports 10+ filter/sort combinations
3. ✅ Frontend UI exposes all filtering capabilities
4. ✅ Performance targets met (< 50ms p95 search latency)
5. ✅ Backward compatible with Phase V.3 API
6. ✅ Resource usage remains within Oracle Free Tier limits
7. ✅ Zero breaking changes to existing functionality

---

## Next Steps

**Immediate**: Execute V4-T002 (database migration)
**After**: Implement V4-T003 (enhanced search endpoint)
**Then**: Frontend integration (V4-T005, V4-T006)
**Finally**: Testing and documentation (V4-T007, V4-T008)

**STOP**: After documentation, await approval for next phase features (recurring tasks, notification history, etc.)
