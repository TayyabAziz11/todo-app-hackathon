-- Migration: Add Full-Text Search Support to Dapr State Store
-- Phase V.3 - T058: Create PostgreSQL full-text search indexes
-- Date: 2026-02-06

-- Step 1: Add tsvector column for full-text search
-- This column will contain searchable text extracted from JSONB data
ALTER TABLE dapr_state
ADD COLUMN IF NOT EXISTS search_vector tsvector;

-- Step 2: Create function to extract searchable text from TODO JSONB
-- Extracts: title, description, tags
CREATE OR REPLACE FUNCTION extract_todo_search_text(jsonb_data jsonb)
RETURNS text AS $$
BEGIN
    -- Only process keys that start with "todo:" (not audit: or other keys)
    -- Extract title, description, and tags for search
    RETURN COALESCE(jsonb_data->>'title', '') || ' ' ||
           COALESCE(jsonb_data->>'description', '') || ' ' ||
           COALESCE(array_to_string(ARRAY(SELECT jsonb_array_elements_text(jsonb_data->'tags')), ' '), '');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Step 3: Create function to update search_vector automatically
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    -- Only update search vector for todo keys (not audit or other keys)
    IF NEW.key LIKE 'todo:%' THEN
        NEW.search_vector := to_tsvector('english', extract_todo_search_text(NEW.value));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Step 4: Create trigger to automatically update search_vector on INSERT/UPDATE
DROP TRIGGER IF EXISTS dapr_state_search_vector_trigger ON dapr_state;
CREATE TRIGGER dapr_state_search_vector_trigger
    BEFORE INSERT OR UPDATE OF value ON dapr_state
    FOR EACH ROW
    EXECUTE FUNCTION update_search_vector();

-- Step 5: Backfill search_vector for existing todos
UPDATE dapr_state
SET search_vector = to_tsvector('english', extract_todo_search_text(value))
WHERE key LIKE 'todo:%' AND search_vector IS NULL;

-- Step 6: Create GIN index for efficient full-text search
CREATE INDEX IF NOT EXISTS idx_dapr_state_search_vector
ON dapr_state USING GIN(search_vector);

-- Step 7: Create index on key prefix for efficient TODO queries
CREATE INDEX IF NOT EXISTS idx_dapr_state_todo_keys
ON dapr_state(key)
WHERE key LIKE 'todo:%';

-- Step 8: Add comment for documentation
COMMENT ON COLUMN dapr_state.search_vector IS 'Full-text search vector for TODO items (Phase V.3 - F5)';
COMMENT ON INDEX idx_dapr_state_search_vector IS 'GIN index for full-text search on TODO title, description, tags';

-- Migration complete
-- Validation:
-- 1. Check index exists: SELECT * FROM pg_indexes WHERE tablename = 'dapr_state';
-- 2. Test search: SELECT key, value FROM dapr_state WHERE search_vector @@ to_tsquery('english', 'test') AND key LIKE 'todo:%';
