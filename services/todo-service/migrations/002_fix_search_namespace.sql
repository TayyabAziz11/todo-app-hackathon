-- Migration: Fix Full-Text Search for Dapr Namespaced Keys
-- Phase V.3 - T058: Update trigger to handle todo-service||todo: format
-- Date: 2026-02-06

-- Drop and recreate trigger function with correct namespace handling
DROP TRIGGER IF EXISTS dapr_state_search_vector_trigger ON dapr_state;

CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    -- Handle Dapr namespaced keys: "todo-service||todo:..." or "app||todo:..."
    IF NEW.key LIKE '%||todo:%' THEN
        NEW.search_vector := to_tsvector('english', extract_todo_search_text(NEW.value));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER dapr_state_search_vector_trigger
    BEFORE INSERT OR UPDATE OF value ON dapr_state
    FOR EACH ROW
    EXECUTE FUNCTION update_search_vector();

-- Drop old index and create new one for namespaced keys
DROP INDEX IF EXISTS idx_dapr_state_todo_keys;
CREATE INDEX IF NOT EXISTS idx_dapr_state_todo_keys
ON dapr_state(key)
WHERE key LIKE '%||todo:%';

-- Backfill search_vector for existing todos (with namespace)
UPDATE dapr_state
SET search_vector = to_tsvector('english', extract_todo_search_text(value))
WHERE key LIKE '%||todo:%' AND search_vector IS NULL;

-- Verify: Show count of todos with search vectors
SELECT COUNT(*) as todos_with_search_vectors FROM dapr_state WHERE key LIKE '%||todo:%' AND search_vector IS NOT NULL;
