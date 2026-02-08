# V4-T008: Dashboard & Backend Consolidation Report

**Task**: Dashboard & Backend Consolidation
**Date Started**: 2026-02-07
**Status**: 🟡 IN PROGRESS (70% Complete)
**Goal**: Unify Phase V.4 features into existing dashboard and backend, eliminating parallel systems

---

## Executive Summary

Consolidating the separate `dashboard-v4` route and `services/todo-service/` backend into the main dashboard and backend. This eliminates architectural drift and creates a single unified system.

### Architecture Transformation

**Before Consolidation:**
```
Frontend (3000)
  ├─ /dashboard → Basic features (port 8000)
  └─ /dashboard-v4 → Phase V.4 features (port 8001)

Backend Services:
  ├─ backend/ (port 8000) → Phase 3 chatbot + basic CRUD
  └─ services/todo-service/ (port 8001) → Phase V.4 advanced search
```

**After Consolidation:**
```
Frontend (3000)
  └─ /dashboard → ALL features unified

Backend:
  └─ backend/ (port 8000) → Phase 3 + Phase V.4 unified
     ├─ Basic CRUD (existing)
     ├─ AI Chat (existing)
     ├─ Advanced Search (NEW)
     ├─ Tag Management (NEW)
     └─ Priority/Due Dates (NEW)
```

---

## ✅ Completed Work (70%)

### 1. Backend Data Model Updates
**File**: `backend/app/models/todo.py`

✅ **Added Priority Enum:**
```python
class Priority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"
```

✅ **Added Phase V.4 Fields to Todo Model:**
- `priority`: Optional[Priority] - Priority level
- `tags`: Optional[List[str]] - Array of tags
- `due_date`: Optional[datetime] - When todo is due
- `search_vector`: Optional[str] - Full-text search vector

### 2. Schema Updates
**File**: `backend/app/schemas/todo.py`

✅ **Updated TodoCreate, TodoUpdate, TodoResponse:**
- All schemas now include priority, tags, due_date fields
- Proper validation and examples added
- Type safety maintained throughout

### 3. Database Migration
**File**: `backend/alembic/versions/add_phase_v4_fields_to_todos.py`

✅ **Created Migration Script:**
- Adds 4 new columns: priority (enum), tags (array), due_date (timestamp), search_vector (tsvector)
- Creates 4 indexes:
  * GIN index on search_vector for full-text search
  * GIN index on tags for tag queries
  * B-tree index on due_date for sorting
  * B-tree index on priority for sorting
- Enables pg_trgm extension for fuzzy search

**Status**: Migration created, needs to be run via `alembic upgrade head`

### 4. Router Updates - CRUD Operations
**File**: `backend/app/routers/todos.py`

✅ **Updated create_todo:**
- Accepts priority, tags, due_date from request
- Populates search_vector on creation

✅ **Updated update_todo:**
- Handles Phase V.4 fields in updates
- Regenerates search_vector when title/description changes

### 5. Router Updates - Advanced Search Endpoint
**File**: `backend/app/routers/todos.py`

✅ **Added `/v1/todos/search` endpoint:**
- Full-text search on title/description
- Filter by status (active/completed)
- Filter by priority levels (comma-separated)
- Filter by tags (AND logic)
- Filter by due date range
- Sorting by multiple fields
- Pagination support
- Returns structured response with metadata

### 6. Router Updates - Tag Management Endpoints
**File**: `backend/app/routers/todos.py`

✅ **Added `/v1/tags` endpoint:**
- Lists all unique tags for authenticated user
- Returns sorted array of tags

✅ **Added `/v1/tags/autocomplete` endpoint:**
- Prefix-based tag suggestions
- Configurable limit (1-50)

✅ **Added `/v1/tags/popular` endpoint:**
- Most frequently used tags with counts
- Configurable limit (1-50)
- Returns array of `{tag, count}` objects

### 7. Frontend Configuration
**File**: `frontend/.env.local`

✅ **Updated API URLs:**
```bash
# Before:
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001  # Separate Phase V.4 backend
NEXT_PUBLIC_CHAT_API_URL=http://localhost:8000  # Phase 3 backend

# After:
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000  # UNIFIED BACKEND
NEXT_PUBLIC_CHAT_API_URL=http://localhost:8000  # Same backend
```

### 8. Frontend Hook Path Updates
**Files**:
- `frontend/src/hooks/useTodoSearch.ts`
- `frontend/src/hooks/useTagAutocomplete.ts`
- `frontend/src/hooks/usePopularTags.ts`

✅ **Updated API paths to include user_id:**
- All hooks now use `useAuth()` to get current user
- API calls follow pattern: `/api/${user.id}/v1/...`
- Hooks skip API calls when user not authenticated
- Matches backend router expectations perfectly

---

## ⏳ Remaining Work (30%)

### 8. Database Migration Execution
**Priority**: 🔴 CRITICAL - Required before backend restart

**Steps:**
```bash
cd backend
alembic upgrade head
```

**Validation:**
```sql
-- Verify columns added
\d todos

-- Should show:
-- priority (priority enum)
-- tags (character varying[])
-- due_date (timestamp with time zone)
-- search_vector (tsvector)

-- Verify indexes created
\di
-- Should show idx_todos_search_vector, idx_todos_tags, idx_todos_due_date, idx_todos_priority
```

### 9. Router Path Adjustments ✅ (COMPLETE)
**Priority**: ✅ COMPLETE

**Issue**: Router endpoints used `/{user_id}/v1/...` but frontend hooks were calling `/api/v1/...` without user_id.

**Solution Implemented**: Updated all Phase V.4 hooks to include user.id in API paths:
- `useTodoSearch.ts`: Now calls `/api/${user.id}/v1/todos/search`
- `useTagAutocomplete.ts`: Now calls `/api/${user.id}/v1/tags/autocomplete`
- `usePopularTags.ts`: Now calls `/api/${user.id}/v1/tags/popular`

**Backend Routes**: Updated router endpoint decorators to include `/{user_id}` prefix:
- `@router.get("/{user_id}/v1/todos/search")`
- `@router.get("/{user_id}/v1/tags")`
- `@router.get("/{user_id}/v1/tags/autocomplete")`
- `@router.get("/{user_id}/v1/tags/popular")`

**Result**: All paths now follow consistent pattern: `/api/{user_id}/...` ✅

### 10. Frontend Dashboard Consolidation
**Priority**: 🟡 MEDIUM - Merge dashboard-v4 into main dashboard

**Files to Update:**
- `frontend/src/app/dashboard/page.tsx` - Integrate Phase V.4 features
- Keep existing components: `PriorityBadge.tsx`, `TagChip.tsx`, `DueDateBadge.tsx` (already exist)
- Keep existing hooks: `useTodoSearch.ts`, `useTagAutocomplete.ts` (already exist)

**Option A (Recommended)**: Copy advanced search panel from dashboard-v4 into main dashboard
**Option B (Simpler)**: Redirect /dashboard to /dashboard-v4 temporarily, rename later

### 11. Stop Separate Backend Service
**Priority**: 🔴 CRITICAL - Prevent port conflicts

**Steps:**
```bash
# Find and stop Phase V.4 backend on port 8001
ps aux | grep "uvicorn.*8001"
kill <PID>

# Or if running in Docker:
docker stop todo-service
```

### 12. Remove Obsolete Code
**Priority**: 🟢 LOW - Cleanup after verification

**Directories to Archive/Remove:**
- `services/todo-service/` - Separate Phase V.4 backend (no longer needed)
- `frontend/src/app/dashboard-v4/` - Separate dashboard route (after features merged)

**Before deleting**, archive to:
```bash
mkdir -p archive/phase-v4-original/
mv services/todo-service/ archive/phase-v4-original/
mv frontend/src/app/dashboard-v4/ archive/phase-v4-original/
```

### 13. Runtime Verification
**Priority**: 🔴 CRITICAL - Validate consolidation works

**Backend Verification:**
```bash
# Start unified backend
cd backend
uvicorn main:app --reload --port 8000

# Test Phase V.4 endpoints
curl "http://localhost:8000/api/<user-id>/v1/todos/search?limit=5"
curl "http://localhost:8000/api/<user-id>/v1/tags"
curl "http://localhost:8000/api/<user-id>/v1/tags/autocomplete?q=test"
curl "http://localhost:8000/api/<user-id>/v1/tags/popular?limit=10"
```

**Frontend Verification:**
```bash
# Restart frontend to pick up new env vars
cd frontend
npm run dev

# Navigate to http://localhost:3000/dashboard
# Verify:
# - Priority badges display
# - Tag chips display and are clickable
# - Due dates display with correct colors
# - Advanced search works
# - Tag filtering works
```

### 14. Update Documentation
**Priority**: 🟢 LOW - Document final architecture

**Files to Update:**
- `docs/phase-v4-progress/README.md` - Mark V4-T008 complete
- `services/README.md` - Remove references to separate Phase V.4 backend
- `README.md` - Update architecture diagram

---

## Technical Decisions Made

### 1. Storage Architecture
**Decision**: Use existing SQLModel + PostgreSQL (NOT Dapr State Store)

**Rationale**:
- Existing backend already uses SQLModel with proper migrations
- Maintains JWT authentication and user ownership
- Simpler than introducing Dapr State Store
- Phase V.4 features work identically with direct PostgreSQL

**Impact**: Advanced search query adapted from Dapr JSON queries to SQLModel queries

### 2. Authentication Approach
**Decision**: Keep JWT authentication and user ownership enforcement

**Rationale**:
- Existing security model working correctly
- Phase V.4 endpoints need same user isolation
- All new endpoints require `authenticated_user_id` from JWT

**Impact**: All Phase V.4 endpoints include authorization checks

### 3. Endpoint Path Structure
**Decision**: New endpoints follow pattern `/{user_id}/v1/...`

**Current Challenge**: Frontend expects `/api/v1/...` without user_id in path

**Options**:
- A. Update frontend to include user_id in API calls
- B. Add route aliases in backend
- C. Use Next.js API routes as proxy (NOT recommended - violates no-proxy rule)

**Recommendation**: Option A - Update frontend hooks to extract user_id from auth context

### 4. Dashboard Consolidation Strategy
**Decision**: Phased approach

**Phase 1** (Current): Consolidate backend, update configuration
**Phase 2** (Next): Integrate Phase V.4 UI into main dashboard
**Phase 3** (Final): Remove dashboard-v4, cleanup

**Rationale**: Reduces risk, allows incremental testing

---

## Known Issues & Blockers

### Issue 1: Alembic Migration Not Run
**Status**: 🔴 BLOCKING
**Impact**: Backend will fail to start without new columns
**Resolution**: Run `cd backend && alembic upgrade head`

### Issue 2: Endpoint Path Mismatch ✅ (RESOLVED)
**Status**: ✅ RESOLVED (2026-02-07)
**Impact**: None - fixed before deployment
**Resolution**: Updated both backend router decorators and frontend hooks to use consistent `/{user_id}/v1/...` path pattern

### Issue 3: Phase V.4 Backend Still Running
**Status**: 🟡 NON-BLOCKING
**Impact**: Port conflict if unified backend tries to start
**Resolution**: Stop Phase V.4 backend process on port 8001

---

## Quick Start Guide (Complete Consolidation)

### Step 1: Run Database Migration
```bash
cd backend
alembic upgrade head
```

### Step 2: Stop Separate Phase V.4 Backend
```bash
ps aux | grep "uvicorn.*8001"
kill <PID>
```

### Step 3: Start Unified Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Step 4: Restart Frontend
```bash
cd frontend
npm run dev
```

### Step 5: Test Advanced Search
```bash
# Backend endpoint test (replace <user-id>)
curl "http://localhost:8000/api/<user-id>/v1/todos/search?status=active&limit=5"
```

### Step 6: Visual Verification
1. Open http://localhost:3000/dashboard
2. Create a todo with priority, tags, and due date
3. Verify metadata displays correctly
4. Test advanced search filters
5. Test tag filtering by clicking tags

---

## Success Criteria

### Backend Consolidation ✅ (100% Complete)
- [X] Todo model includes Phase V.4 fields
- [X] Schemas updated for Phase V.4
- [X] Database migration created
- [X] CRUD operations handle Phase V.4 fields
- [X] Advanced search endpoint implemented
- [X] Tag management endpoints implemented
- [X] All endpoints include authentication/authorization

### Frontend Configuration ✅ (100% Complete)
- [X] `.env.local` points to port 8000 (unified backend)
- [X] API URLs updated

### Deployment & Verification ⏳ (0% Complete)
- [ ] Database migration executed
- [ ] Unified backend running on port 8000
- [ ] Separate Phase V.4 backend stopped
- [ ] Frontend connected to unified backend
- [ ] Advanced search working
- [ ] Tag management working
- [ ] Priority/due dates displaying

### Cleanup ⏳ (0% Complete)
- [ ] dashboard-v4 features merged into main dashboard
- [ ] dashboard-v4 route removed
- [ ] services/todo-service/ archived or removed
- [ ] Documentation updated

---

## Rollback Plan

If consolidation fails, revert to dual-backend architecture:

```bash
# 1. Revert frontend config
cd frontend
git checkout .env.local

# 2. Restart Phase V.4 backend
cd services/todo-service
./start.sh

# 3. Restart Phase 3 backend
cd backend
uvicorn main:app --reload --port 8000

# 4. Revert database migration
cd backend
alembic downgrade -1
```

---

## Next Steps (Priority Order)

1. 🔴 **CRITICAL**: Run database migration (`alembic upgrade head`)
2. 🔴 **CRITICAL**: Stop Phase V.4 backend on port 8001
3. 🟡 **MEDIUM**: Test unified backend with all endpoints
4. 🟡 **MEDIUM**: Merge dashboard-v4 UI into main dashboard
5. 🟢 **LOW**: Archive obsolete code
6. 🟢 **LOW**: Update documentation

---

**Report Created**: 2026-02-07
**Last Updated**: 2026-02-07 (Path mismatch fixed)
**Status**: Backend consolidation complete (70%), deployment pending
**Next Action**: Run database migration and test unified backend
**Estimated Time to Complete**: 1-2 hours remaining
