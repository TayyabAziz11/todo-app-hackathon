/**
 * Todo type definitions
 *
 * Matches backend Todo model and Pydantic schemas (Phase V.4):
 * - TodoResponse
 * - TodoCreate
 * - TodoUpdate
 */

/**
 * Priority levels for todos (Phase V.2 - F3)
 */
export type Priority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';

/**
 * Complete todo object as returned from the API (Phase V.4)
 */
export interface Todo {
  id: string; // UUID from backend
  title: string;
  description: string | null;
  priority: Priority; // Phase V.2
  tags: string[]; // Phase V.2 (F4)
  due_date: string | null; // Phase V.3 (T066) - ISO 8601 datetime
  completed: boolean;
  created_at: string; // ISO 8601 datetime string
  updated_at: string; // ISO 8601 datetime string
  user_id: string;
  rank?: number; // Optional: relevance rank from search API
}

/**
 * Payload for creating a new todo (Phase V.4)
 */
export interface TodoCreate {
  title: string;
  description?: string | null;
  priority?: Priority; // Default: MEDIUM
  tags?: string[]; // Default: []
  due_date?: string | null; // ISO 8601 format
}

/**
 * Payload for updating an existing todo (Phase V.4)
 * All fields are optional - only provided fields will be updated
 */
export interface TodoUpdate {
  title?: string;
  description?: string | null;
  priority?: Priority;
  tags?: string[];
  due_date?: string | null;
  completed?: boolean;
}

/**
 * Search filters for advanced search (Phase V.4)
 */
export interface TodoSearchFilters {
  q?: string; // Full-text search query
  fuzzy?: boolean; // Enable fuzzy matching
  status?: 'all' | 'active' | 'completed';
  priority?: string; // Comma-separated priorities (e.g., "HIGH,URGENT")
  tags?: string; // Comma-separated tags (e.g., "backend,api")
  due_date_from?: string; // ISO 8601
  due_date_to?: string; // ISO 8601
  created_after?: string; // ISO 8601
  created_before?: string; // ISO 8601
  sort_by?: 'created_at' | 'updated_at' | 'due_date' | 'priority' | 'title';
  sort_order?: 'asc' | 'desc';
  limit?: number; // Default: 20, max: 100
  offset?: number; // Default: 0
}

/**
 * Search response from backend (Phase V.4)
 */
export interface TodoSearchResponse {
  results: Todo[];
  pagination: {
    total: number;
    limit: number;
    offset: number;
    has_more: boolean;
  };
  filters_applied: {
    search: string | null;
    status: string;
    priorities: string[];
    tags: string[];
    date_range: {
      due_date_from: string | null;
      due_date_to: string | null;
    };
  };
  sorting: {
    sort_by: string;
    sort_order: string;
  };
}

/**
 * Tag autocomplete response (Phase V.4)
 */
export interface TagSuggestion {
  tag: string;
  count: number;
}

/**
 * Popular tag response (Phase V.4)
 */
export interface PopularTag {
  tag: string;
  count: number;
  percentage: number;
}
