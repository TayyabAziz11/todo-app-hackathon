/**
 * Custom hook for tag autocomplete with debouncing
 *
 * Features:
 * - Debounced API calls (default 300ms)
 * - Minimum query length validation (2 chars)
 * - Loading state tracking
 * - Error handling with graceful degradation
 *
 * Usage:
 * ```tsx
 * const { suggestions, loading, search } = useTagAutocomplete();
 *
 * <input onChange={(e) => search(e.target.value)} />
 * {suggestions.map(s => <div key={s.tag}>{s.tag} ({s.count})</div>)}
 * ```
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { TagSuggestion } from '@/types/todo';

export interface UseTagAutocompleteResult {
  suggestions: TagSuggestion[];
  loading: boolean;
  search: (query: string) => void;
  clearSuggestions: () => void;
}

export function useTagAutocomplete(debounceMs: number = 300): UseTagAutocompleteResult {
  const { user } = useAuth();
  const [suggestions, setSuggestions] = useState<TagSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const abortControllerRef = useRef<AbortController | undefined>(undefined);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const search = useCallback((query: string) => {
    // Clear previous timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Abort previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Trim query
    const trimmedQuery = query.trim();

    // Don't search if query too short or user not authenticated
    if (!user || trimmedQuery.length < 2) {
      setSuggestions([]);
      setLoading(false);
      return;
    }

    // Set loading immediately for UX feedback
    setLoading(true);

    // Debounce API call
    timeoutRef.current = setTimeout(async () => {
      try {
        // Create abort controller for this request
        const abortController = new AbortController();
        abortControllerRef.current = abortController;

        const token = typeof window !== 'undefined' ? localStorage.getItem('jwt_token') : null;
        const response = await fetch(
          `/api/${user.id}/v1/tags/autocomplete?q=${encodeURIComponent(trimmedQuery)}&limit=10`,
          {
            signal: abortController.signal,
            headers: token ? { Authorization: `Bearer ${token}` } : {},
          }
        );

        if (response.ok) {
          const data: TagSuggestion[] = await response.json();
          setSuggestions(data);
        } else {
          console.warn(`Tag autocomplete failed: ${response.status}`);
          setSuggestions([]);
        }
      } catch (error: any) {
        // Ignore abort errors (expected when query changes)
        if (error.name !== 'AbortError') {
          console.error('Tag autocomplete error:', error);
          setSuggestions([]);
        }
      } finally {
        setLoading(false);
      }
    }, debounceMs);
  }, [user, debounceMs]);

  const clearSuggestions = useCallback(() => {
    setSuggestions([]);
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setLoading(false);
  }, []);

  return {
    suggestions,
    loading,
    search,
    clearSuggestions,
  };
}
