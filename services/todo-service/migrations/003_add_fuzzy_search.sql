-- Migration: Add Fuzzy Matching Support with pg_trgm
-- Phase V.3 - T060: Implement fuzzy matching (Levenshtein distance)
-- Date: 2026-02-06

-- Step 1: Enable pg_trgm extension for trigram-based similarity matching
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Step 2: Add GIN index for trigram similarity on key column
-- This enables fast similarity searches on TODO keys (which contain UUIDs)
CREATE INDEX IF NOT EXISTS idx_dapr_state_key_trgm
ON dapr_state USING GIN (key gin_trgm_ops)
WHERE key LIKE '%||todo:%';

-- Step 3: Create GiST index for trigram similarity on searchable text
-- This enables ranked similarity searches on TODO content
-- We create a computed column expression for this
CREATE INDEX IF NOT EXISTS idx_dapr_state_text_similarity
ON dapr_state USING GIST (
    (COALESCE(value->>'title', '') || ' ' ||
     COALESCE(value->>'description', '') || ' ' ||
     COALESCE(array_to_string(ARRAY(SELECT jsonb_array_elements_text(value->'tags')), ' '), ''))
    gist_trgm_ops
)
WHERE key LIKE '%||todo:%';

-- Step 4: Create helper function for fuzzy search
CREATE OR REPLACE FUNCTION fuzzy_search_todos(
    search_text text,
    similarity_threshold float DEFAULT 0.3,
    max_results int DEFAULT 20
)
RETURNS TABLE (
    key text,
    value jsonb,
    similarity_score float
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ds.key,
        ds.value,
        GREATEST(
            similarity(COALESCE(ds.value->>'title', ''), search_text),
            similarity(COALESCE(ds.value->>'description', ''), search_text),
            similarity(
                COALESCE(array_to_string(ARRAY(SELECT jsonb_array_elements_text(ds.value->'tags')), ' '), ''),
                search_text
            )
        ) as similarity_score
    FROM dapr_state ds
    WHERE
        ds.key LIKE '%||todo:%'
        AND (
            similarity(COALESCE(ds.value->>'title', ''), search_text) > similarity_threshold
            OR similarity(COALESCE(ds.value->>'description', ''), search_text) > similarity_threshold
            OR similarity(
                COALESCE(array_to_string(ARRAY(SELECT jsonb_array_elements_text(ds.value->'tags')), ' '), ''),
                search_text
            ) > similarity_threshold
        )
    ORDER BY similarity_score DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Step 5: Add comments for documentation
COMMENT ON EXTENSION pg_trgm IS 'Trigram similarity matching for fuzzy text search (Phase V.3 - F5)';
COMMENT ON FUNCTION fuzzy_search_todos IS 'Fuzzy search function using trigram similarity (handles typos and misspellings)';

-- Step 6: Test fuzzy matching capability
-- Example: SELECT * FROM fuzzy_search_todos('meetng', 0.3, 10);
-- This should find "meeting" even with typo

-- Migration complete
-- Validation:
-- 1. Check extension: SELECT * FROM pg_extension WHERE extname = 'pg_trgm';
-- 2. Test fuzzy search: SELECT * FROM fuzzy_search_todos('tset', 0.3, 5); (should find "test")
-- 3. Test similarity: SELECT similarity('meeting', 'meetng'); (should return ~0.5)
