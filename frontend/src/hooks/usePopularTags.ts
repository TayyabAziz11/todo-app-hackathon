/**
 * Custom hook for fetching popular tags
 *
 * Features:
 * - Fetches most-used tags from backend
 * - Loading state tracking
 * - Error handling with graceful degradation
 * - Simple caching (no refetch unless limit changes)
 *
 * Usage:
 * ```tsx
 * const { tags, loading } = usePopularTags(10);
 *
 * {tags.map(tag => (
 *   <button key={tag.tag}>
 *     {tag.tag} ({tag.count}) - {tag.percentage.toFixed(1)}%
 *   </button>
 * ))}
 * ```
 */

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { PopularTag } from '@/types/todo';

export interface UsePopularTagsResult {
  tags: PopularTag[];
  loading: boolean;
  error: Error | null;
  refresh: () => void;
}

export function usePopularTags(limit: number = 10): UsePopularTagsResult {
  const { user } = useAuth();
  const [tags, setTags] = useState<PopularTag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [refreshCounter, setRefreshCounter] = useState(0);

  useEffect(() => {
    let isMounted = true;

    async function fetchPopularTags() {
      // Skip if user not authenticated
      if (!user) {
        setTags([]);
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const token = typeof window !== 'undefined' ? localStorage.getItem('jwt_token') : null;
        const response = await fetch(`/api/${user.id}/v1/tags/popular?limit=${limit}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch popular tags: ${response.status}`);
        }

        const data: PopularTag[] = await response.json();

        if (isMounted) {
          setTags(data);
        }
      } catch (err) {
        if (isMounted) {
          console.error('Failed to fetch popular tags:', err);
          setError(err as Error);
          setTags([]);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchPopularTags();

    return () => {
      isMounted = false;
    };
  }, [user, limit, refreshCounter]);

  const refresh = () => {
    setRefreshCounter(prev => prev + 1);
  };

  return {
    tags,
    loading,
    error,
    refresh,
  };
}
