/**
 * Custom hook for managing todo search state and API calls
 *
 * Features:
 * - React state-based filter management
 * - Auto-executes search when filters change
 * - Pagination support with metadata
 * - Error handling and loading states
 *
 * Usage:
 * ```tsx
 * const { results, pagination, filters, loading, error, setFilters, nextPage, prevPage } = useTodoSearch();
 * ```
 */

import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { TodoSearchFilters, TodoSearchResponse, Todo } from '@/types/todo';

export interface UseTodoSearchResult {
  // Data
  results: Todo[];
  pagination: TodoSearchResponse['pagination'];
  filters: TodoSearchFilters;
  loading: boolean;
  error: Error | null;

  // Actions
  setFilters: (filters: Partial<TodoSearchFilters>) => void;
  clearFilters: () => void;
  nextPage: () => void;
  prevPage: () => void;
  refresh: () => void;
}

const DEFAULT_FILTERS: TodoSearchFilters = {
  status: 'all',
  sort_by: 'created_at',
  sort_order: 'desc',
  limit: 20,
  offset: 0,
};

export function useTodoSearch(): UseTodoSearchResult {
  const { user } = useAuth();
  const [filters, setFiltersState] = useState<TodoSearchFilters>(DEFAULT_FILTERS);
  const [results, setResults] = useState<Todo[]>([]);
  const [pagination, setPagination] = useState<TodoSearchResponse['pagination']>({
    total: 0,
    limit: 20,
    offset: 0,
    has_more: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Fetch search results from backend
  const executeSearch = useCallback(async () => {
    if (!user) {
      setResults([]);
      setPagination({ total: 0, limit: 20, offset: 0, has_more: false });
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Build query params from filters
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== 'all' && value !== '') {
          params.set(key, String(value));
        }
      });

      const token = typeof window !== 'undefined' ? localStorage.getItem('jwt_token') : null;
      const response = await fetch(`/api/${user.id}/v1/todos/search?${params.toString()}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status} ${response.statusText}`);
      }

      const data: TodoSearchResponse = await response.json();
      setResults(data.results);
      setPagination(data.pagination);
    } catch (err) {
      setError(err as Error);
      setResults([]);
      setPagination({ total: 0, limit: 20, offset: 0, has_more: false });
    } finally {
      setLoading(false);
    }
  }, [user, filters]);

  // Update filters (merges with existing)
  const setFilters = useCallback((newFilters: Partial<TodoSearchFilters>) => {
    setFiltersState((prev) => {
      const updated = { ...prev, ...newFilters };
      // Reset offset when filters change (except when explicitly setting offset)
      if (!('offset' in newFilters)) {
        updated.offset = 0;
      }
      return updated;
    });
  }, []);

  // Clear all filters (reset to defaults)
  const clearFilters = useCallback(() => {
    setFiltersState(DEFAULT_FILTERS);
  }, []);

  // Pagination actions
  const nextPage = useCallback(() => {
    if (pagination.has_more) {
      setFiltersState((prev) => ({
        ...prev,
        offset: (prev.offset || 0) + (prev.limit || 20),
      }));
    }
  }, [pagination.has_more]);

  const prevPage = useCallback(() => {
    setFiltersState((prev) => ({
      ...prev,
      offset: Math.max(0, (prev.offset || 0) - (prev.limit || 20)),
    }));
  }, []);

  // Auto-execute search when filters change
  useEffect(() => {
    executeSearch();
  }, [executeSearch]);

  return {
    results,
    pagination,
    filters,
    loading,
    error,
    setFilters,
    clearFilters,
    nextPage,
    prevPage,
    refresh: executeSearch,
  };
}
