-- Migration: Fix Fuzzy Search Index
-- Phase V.3 - T060: Fix GiST index for fuzzy matching
-- Date: 2026-02-06

-- Note: The previous migration created pg_trgm extension and fuzzy_search_todos function successfully.
-- This migration fixes the GiST index which failed due to subquery in expression.

-- Instead of a complex computed index, we'll rely on the function-based approach
-- and create simpler indexes on individual fields

-- Step 1: Create GIN trigram index on title (extracted from JSONB)
CREATE INDEX IF NOT EXISTS idx_dapr_state_title_trgm
ON dapr_state USING GIN ((value->>'title') gin_trgm_ops)
WHERE key LIKE '%||todo:%';

-- Step 2: Create GIN trigram index on description (extracted from JSONB)
CREATE INDEX IF NOT EXISTS idx_dapr_state_description_trgm
ON dapr_state USING GIN ((value->>'description') gin_trgm_ops)
WHERE key LIKE '%||todo:%';

-- Step 3: Set similarity threshold for session (default 0.3)
-- This can be overridden per query: SET pg_trgm.similarity_threshold = 0.4;
ALTER DATABASE todoapp_db SET pg_trgm.similarity_threshold = 0.3;

-- Step 4: Test fuzzy matching
-- Show current similarity threshold
SHOW pg_trgm.similarity_threshold;

-- Migration complete
-- Validation:
-- 1. Test fuzzy search: SELECT * FROM fuzzy_search_todos('meetng', 0.3, 5);
-- 2. Test similarity with typo: SELECT title FROM (SELECT value->>'title' as title FROM dapr_state WHERE key LIKE '%||todo:%') t WHERE similarity(title, 'tset') > 0.3;
