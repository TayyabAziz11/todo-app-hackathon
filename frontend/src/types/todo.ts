/**
 * Todo type definitions
 *
 * Matches backend Todo model and Pydantic schemas:
 * - TodoResponse
 * - TodoCreate
 * - TodoUpdate
 */

/**
 * Complete todo object as returned from the API
 */
export interface Todo {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string; // ISO 8601 datetime string
  updated_at: string; // ISO 8601 datetime string
}

/**
 * Payload for creating a new todo
 */
export interface TodoCreate {
  title: string;
  description?: string | null;
}

/**
 * Payload for updating an existing todo
 * All fields are optional - only provided fields will be updated
 */
export interface TodoUpdate {
  title?: string;
  description?: string | null;
  completed?: boolean;
}
