# Todo Service PostgreSQL Migrations

## Phase V.3 - Full-Text Search Support

### Migration 001: Add Full-Text Search Infrastructure
**File**: `001_add_fulltext_search.sql`
**Date**: 2026-02-06
**Status**: ✅ Applied

**Changes**:
1. Added `search_vector` tsvector column to `dapr_state` table
2. Created `extract_todo_search_text(jsonb)` function to extract searchable text from TODO data
3. Created `update_search_vector()` trigger function
4. Created trigger `dapr_state_search_vector_trigger` to auto-populate search_vector on INSERT/UPDATE
5. Created GIN index `idx_dapr_state_search_vector` for efficient full-text search
6. Created partial B-tree index `idx_dapr_state_todo_keys` for efficient TODO queries

**Searchable Fields**:
- `title` (weighted highest)
- `description`
- `tags` (array elements)

### Migration 002: Fix for Dapr Namespaced Keys
**File**: `002_fix_search_namespace.sql`
**Date**: 2026-02-06
**Status**: ✅ Applied

**Changes**:
1. Updated trigger to handle Dapr's namespaced key format: `app-id||todo:{uuid}`
2. Updated partial index to match namespaced keys
3. Backfilled search_vector for 62 existing TODOs

**Validation Results**:
- ✅ 62 TODOs with search vectors populated
- ✅ Full-text search query works: `search_vector @@ to_tsquery('english', 'keyword')`
- ✅ Ranking works: `ts_rank(search_vector, query)`
- ✅ Tag search works: Tags extracted and indexed correctly

### Query Examples

#### Basic Search
```sql
SELECT key, value->>'title' as title
FROM dapr_state
WHERE key LIKE '%||todo:%'
  AND search_vector @@ to_tsquery('english', 'meeting');
```

#### Ranked Search
```sql
SELECT
    key,
    value->>'title' as title,
    ts_rank(search_vector, to_tsquery('english', 'urgent & deadline')) as rank
FROM dapr_state
WHERE key LIKE '%||todo:%'
  AND search_vector @@ to_tsquery('english', 'urgent & deadline')
ORDER BY rank DESC
LIMIT 20;
```

#### Phrase Search
```sql
SELECT key, value->>'title' as title
FROM dapr_state
WHERE key LIKE '%||todo:%'
  AND search_vector @@ phraseto_tsquery('english', 'quarterly review');
```

#### Fuzzy Search (coming in T060)
```sql
-- Requires pg_trgm extension
SELECT key, value->>'title' as title,
       similarity(value->>'title', 'meetng') as sim
FROM dapr_state
WHERE key LIKE '%||todo:%'
  AND similarity(value->>'title', 'meetng') > 0.3
ORDER BY sim DESC;
```

### Index Statistics

```sql
-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'dapr_state';
```

### Rollback Instructions

To rollback these migrations (if needed):

```sql
-- Drop trigger
DROP TRIGGER IF EXISTS dapr_state_search_vector_trigger ON dapr_state;

-- Drop functions
DROP FUNCTION IF EXISTS update_search_vector();
DROP FUNCTION IF EXISTS extract_todo_search_text(jsonb);

-- Drop indexes
DROP INDEX IF EXISTS idx_dapr_state_search_vector;
DROP INDEX IF EXISTS idx_dapr_state_todo_keys;

-- Drop column
ALTER TABLE dapr_state DROP COLUMN IF EXISTS search_vector;
```

### Performance Notes

- GIN index used automatically when table grows beyond ~100-200 rows
- For smaller datasets, PostgreSQL optimizer may choose sequential scan (faster for small tables)
- Search vector automatically updated via trigger on INSERT/UPDATE
- English stemming applied (e.g., "running" matches "run")

### Migration 003: Add Fuzzy Search Support
**File**: `003_add_fuzzy_search.sql`
**Date**: 2026-02-06
**Status**: ✅ Applied (partially - function created, complex index failed)

**Changes**:
1. Enabled `pg_trgm` extension for trigram-based similarity matching
2. Created `fuzzy_search_todos()` function for fuzzy queries
3. Attempted GiST index creation (failed due to subquery limitation)

### Migration 004: Fix Fuzzy Search Indexes
**File**: `004_fix_fuzzy_search.sql`
**Date**: 2026-02-06
**Status**: ✅ Applied

**Changes**:
1. Created GIN trigram index on title field: `idx_dapr_state_title_trgm`
2. Created GIN trigram index on description field: `idx_dapr_state_description_trgm`
3. Set database-level similarity threshold to 0.3
4. Fixed `fuzzy_search_todos()` function type mismatch (float → real)

**Fuzzy Search Capabilities**:
- Handles typos and misspellings
- Configurable similarity threshold (0.0-1.0)
- Examples:
  - "urgnt" finds "Urgent Task" (similarity: 0.28)
  - "meetng" would find "meeting" (similarity: 0.5)
  - "pririty" would find "priority" (similarity: 0.54)

### API Endpoint Status

**T058**: ✅ COMPLETE - Full-text search indexes created
**T059**: ✅ COMPLETE - Search API endpoint implemented (`/api/v1/todos/search`)
**T060**: ✅ COMPLETE - Fuzzy matching added (pg_trgm extension)
**T061**: ✅ COMPLETE - Pagination implemented (limit/offset parameters)

### Search Endpoint Features

```
GET /api/v1/todos/search?q=<query>&fuzzy=<bool>&limit=<int>&offset=<int>&similarity_threshold=<float>
```

**Parameters**:
- `q`: Search query (required)
- `fuzzy`: Enable fuzzy matching (default: false)
- `limit`: Max results (default: 20, max: 100)
- `offset`: Skip N results for pagination (default: 0)
- `similarity_threshold`: Min similarity for fuzzy (default: 0.3)

**Examples**:
```bash
# Regular full-text search
curl "http://localhost:8000/api/v1/todos/search?q=test"

# Multi-word search with AND logic
curl "http://localhost:8000/api/v1/todos/search?q=backend+python"

# Fuzzy search with typo
curl "http://localhost:8000/api/v1/todos/search?q=urgnt&fuzzy=true&similarity_threshold=0.25"

# Paginated results
curl "http://localhost:8000/api/v1/todos/search?q=test&limit=10&offset=0"
curl "http://localhost:8000/api/v1/todos/search?q=test&limit=10&offset=10"
```

### Performance Notes

- **Full-text search** (fuzzy=false): Uses GIN index on `search_vector`, very fast
- **Fuzzy search** (fuzzy=true): Uses GIN trigram indexes on title/description fields
- For best fuzzy results on longer words, use threshold 0.3-0.5
- For short words with typos, lower threshold to 0.2-0.3

### Next Steps (Phase V.3 Remaining Tasks)

- **T062-T071**: F2 Email Notifications implementation
- **T072-T073**: Dead Letter Queue setup
- **T074-T077**: Integration testing and documentation
