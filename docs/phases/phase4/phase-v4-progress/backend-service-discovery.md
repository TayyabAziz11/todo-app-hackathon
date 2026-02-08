# Phase V.4 Backend Service Discovery Report

**Date**: 2026-02-07
**Issue**: Dashboard V4 UI complete but metadata not displaying
**Root Cause**: Wrong backend service running

---

## Discovery Summary

### ✅ Frontend Status
- **TodoItem Component**: Complete with Phase V.4 metadata rendering
- **UI Components**: PriorityBadge, TagChip, DueDateBadge all exist
- **Hook**: `useTodoSearch` calls `/api/v1/todos/search` endpoint
- **Dev Server**: Running on port 3000

### ❌ Backend Mismatch

**Expected Backend**: Phase V.4 Todo Service with advanced search
**Actual Backend**: Phase 3 Chatbot Backend

| Aspect | Phase 3 Backend (Running) | Phase V.4 Todo Service (Not Running) |
|--------|---------------------------|--------------------------------------|
| **Location** | `backend/` | `services/todo-service/` |
| **Port** | 8000 | N/A (not started) |
| **Process** | PID 106323 (uvicorn) | Not running |
| **Endpoints** | `/api/{user_id}/chat`<br/>`/api/{user_id}/tasks`<br/>`/health` | `/api/v1/todos/search` ✅<br/>`/api/v1/tags/autocomplete` ✅<br/>`/api/v1/tags/popular` ✅<br/>`/tags` ✅ |
| **Database** | SQLAlchemy + `DATABASE_URL` env var | asyncpg + `DB_HOST`, `DB_PORT`, etc. |
| **Purpose** | Phase 3: AI Chatbot with MCP tools | Phase V.4: Advanced search, tags, priority |

---

## Phase V.4 Backend Implementation Status

### Search Endpoint Found

**File**: `services/todo-service/main.py`
**Line**: 502
**Status**: ✅ Fully implemented

```python
@app.get("/api/v1/todos/search")
async def search_todos(
    user_id: str = "default-user",
    q: Optional[str] = None,
    fuzzy: bool = False,
    similarity_threshold: float = 0.3,
    status: Optional[str] = None,
    priority: Optional[str] = None,        # ✅ Phase V.4
    tags: Optional[str] = None,             # ✅ Phase V.4
    due_date_from: Optional[str] = None,    # ✅ Phase V.4
    due_date_to: Optional[str] = None,      # ✅ Phase V.4
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = 20,
    offset: int = 0
):
```

**Features Implemented**:
- ✅ Full-text search with `ts_query`
- ✅ Fuzzy matching with `pg_trgm` similarity
- ✅ Priority filtering (comma-separated)
- ✅ Tag filtering (AND logic)
- ✅ Due date range filtering
- ✅ Status filtering (all/active/completed)
- ✅ Sorting by multiple fields
- ✅ Pagination

### Additional Endpoints Found

1. **Tag Autocomplete**: `GET /api/v1/tags/autocomplete?q=<prefix>` (line ~480)
2. **Popular Tags**: `GET /api/v1/tags/popular?limit=<n>` (line ~490)
3. **List All Tags**: `GET /tags` (earlier in file)

All endpoints match the frontend hooks:
- `useTodoSearch` → `/api/v1/todos/search`
- `useTagAutocomplete` → `/api/v1/tags/autocomplete`
- `usePopularTags` → `/api/v1/tags/popular`

---

## Why It's Not Working

### Current Architecture

```
┌─────────────┐         ┌──────────────────┐
│  Frontend   │─────────│ Phase 3 Backend  │
│  (port 3000)│  HTTP   │   (port 8000)    │
└─────────────┘         └──────────────────┘
       │
       │ Expects:
       │ /api/v1/todos/search ❌ (404 Not Found)
       │
       ▼
   MISMATCH


┌──────────────────────────┐
│ Phase V.4 Todo Service   │
│  (NOT RUNNING)           │
│                          │
│  Has: /api/v1/todos/search ✅
└──────────────────────────┘
```

### Frontend Configuration

**File**: `frontend/next.config.ts`
```typescript
NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
```

**File**: `frontend/src/hooks/useTodoSearch.ts` (line 79)
```typescript
const response = await fetch(`/api/v1/todos/search?${params.toString()}`);
```

Frontend calls `/api/v1/todos/search` which proxies to `http://localhost:8000/api/v1/todos/search`.
But port 8000 is running Phase 3 backend, which doesn't have this endpoint.

---

## Solution Options

### Option 1: Start Phase V.4 Todo Service (Recommended)

**Pros**:
- Uses the complete, tested Phase V.4 backend
- All search features already implemented
- No code changes needed

**Cons**:
- Need to configure database connection
- Need to run two backend services (Phase 3 + Phase V.4)
- Port conflict (both want port 8000)

**Steps**:
1. Configure database environment variables:
   ```bash
   export DB_HOST=localhost  # or actual DB host
   export DB_PORT=5432
   export DB_NAME=todoapp_db
   export DB_USER=todoapp
   export DB_PASSWORD=your_password
   ```

2. Start todo-service on port 8001:
   ```bash
   cd services/todo-service
   uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

3. Update frontend to use port 8001:
   ```bash
   # In frontend/.env.local
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8001
   ```

4. Restart frontend dev server

### Option 2: Merge Phase V.4 Endpoints into Phase 3 Backend

**Pros**:
- Single backend service
- No port conflicts
- No frontend config changes

**Cons**:
- Requires code migration
- Phase 3 uses SQLAlchemy, Phase V.4 uses asyncpg
- Different database access patterns

**Steps**:
1. Copy search endpoint from `services/todo-service/main.py` to `backend/app/main.py`
2. Adapt asyncpg queries to SQLAlchemy ORM
3. Add tag autocomplete and popular tags endpoints
4. Restart Phase 3 backend

### Option 3: Add Next.js API Route Proxy

**Pros**:
- Frontend doesn't need config changes
- Can route different endpoints to different backends
- Clean separation of concerns

**Cons**:
- Extra network hop (latency)
- More complex architecture
- Still need to start Phase V.4 service

**Steps**:
1. Create `frontend/src/app/api/v1/todos/search/route.ts`
2. Proxy requests to `http://localhost:8001`
3. Start Phase V.4 service on port 8001
4. Frontend calls stay the same (`/api/v1/todos/search`)

### Option 4: Use Phase 3 `/api/{user_id}/tasks` Endpoint

**Pros**:
- Backend already running
- No new services needed

**Cons**:
- Missing Phase V.4 features (tags, priority filtering, advanced search)
- Would need to add all Phase V.4 features to Phase 3 backend
- Essentially same as Option 2

---

## Recommended Path Forward

### **Immediate (Quick Test)**:

**Option 1**: Start Phase V.4 Todo Service on port 8001

```bash
# Terminal 1: Phase V.4 Backend
cd services/todo-service
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=todoapp_db
export DB_USER=todoapp
export DB_PASSWORD=dev_password
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2: Update Frontend
cd frontend
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8001" > .env.local
npm run dev

# Terminal 3: Test
curl "http://localhost:8001/api/v1/todos/search?limit=5"
```

### **Long-term (Production)**:

**Option 2**: Merge backends or use Kubernetes services with proper routing

---

## Database Requirements

### Phase V.4 Todo Service Expects:

**Required Extensions**:
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For fuzzy search
```

**Required Table** (if using Dapr State Store):
```sql
CREATE TABLE IF NOT EXISTS dapr_state (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    search_vector tsvector,  -- For full-text search
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- GIN indexes for performance
CREATE INDEX IF NOT EXISTS idx_dapr_state_search ON dapr_state USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS idx_dapr_state_value_tags ON dapr_state USING GIN ((value->'tags'));
```

**Environment Variables**:
- `DB_HOST`: PostgreSQL host (default: `postgresql.todo-app-dev.svc.cluster.local`)
- `DB_PORT`: PostgreSQL port (default: `5432`)
- `DB_NAME`: Database name (default: `todoapp_db`)
- `DB_USER`: Database user (default: `todoapp`)
- `DB_PASSWORD`: Database password (default: `dev_password`)
- `DAPR_HTTP_ENDPOINT`: Dapr sidecar URL (default: `http://localhost:3500`)

---

## Files Reference

### Phase V.4 Backend
- **Main Service**: `services/todo-service/main.py` (32KB, 850+ lines)
- **Requirements**: `services/todo-service/requirements.txt`
- **Migrations**: `services/todo-service/migrations/`
- **Documentation**: `services/todo-service/docs/phase-v4-progress/`

### Phase 3 Backend (Currently Running)
- **Main Service**: `backend/app/main.py`
- **Database**: `backend/app/database.py`
- **Config**: `backend/app/config.py`

### Frontend
- **Search Hook**: `frontend/src/hooks/useTodoSearch.ts`
- **Autocomplete Hook**: `frontend/src/hooks/useTagAutocomplete.ts`
- **Popular Tags Hook**: `frontend/src/hooks/usePopularTags.ts`
- **Dashboard**: `frontend/src/app/dashboard-v4/page.tsx`
- **TodoItem**: `frontend/src/components/todos/TodoItem.tsx`

---

## Next Steps

**Choose one option and execute**:

1. **Quick Test** (Option 1): Start Phase V.4 service, update frontend env, test
2. **Production** (Option 2): Merge backends or use proper service routing
3. **Intermediate** (Option 3): Add Next.js API proxy

**After backend is running**:
1. Navigate to `http://localhost:3000/dashboard-v4`
2. Create test todo with Phase V.4 metadata
3. Verify priority, tags, due dates display
4. Test tag filtering
5. Document with screenshots

---

**Report Created**: 2026-02-07
**Status**: Backend service identified, not running
**Resolution**: Start `services/todo-service` on port 8001
