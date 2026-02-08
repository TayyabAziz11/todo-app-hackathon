# Phase V.4: Frontend Advanced Search Panel - Implementation Plan

**Date**: 2026-02-07
**Task**: V4-T005
**Status**: 🔵 PLANNING COMPLETE - READY FOR IMPLEMENTATION

---

## Executive Summary

This document provides a complete implementation plan for the Advanced Search Panel frontend component. The backend APIs are operational (V4-T001 through V4-T004 complete). This plan enables rapid frontend implementation.

**Current State**:
- ✅ Backend search API operational (todo-service v4.3.1)
- ✅ Tag management APIs operational (autocomplete, popular)
- ✅ Frontend types updated to match backend (Todo, Priority, Tags, etc.)
- ⏳ Frontend components pending implementation

---

## Prerequisites Completed

### Backend APIs Available

1. **Advanced Search**: `GET /api/v1/todos/search`
   - Filters: status, priority, tags, due_date ranges
   - Sorting: 5 fields × 2 directions
   - Pagination with metadata

2. **Tag Autocomplete**: `GET /api/v1/tags/autocomplete?q=<prefix>`
   - Returns: `[{tag, count}]`
   - Latency: 0.47ms

3. **Popular Tags**: `GET /api/v1/tags/popular?limit=<n>`
   - Returns: `[{tag, count, percentage}]`
   - Latency: < 1ms

### Frontend Types Updated

**File**: `frontend/src/types/todo.ts`

- ✅ `Todo` interface updated with Phase V.4 fields
- ✅ `Priority` type added (LOW | MEDIUM | HIGH | URGENT)
- ✅ `TodoSearchFilters` interface added
- ✅ `TodoSearchResponse` interface added
- ✅ `TagSuggestion` and `PopularTag` interfaces added

---

## Architecture Decision

### State Management Approach: **URL Query Params**

**Rationale**:
- Shareable search URLs
- Browser back/forward works naturally
- No Redux dependency (per requirements)
- Stateless components (per requirements)

**Pattern**:
```typescript
const [searchParams, setSearchParams] = useSearchParams();

// Read filters from URL
const filters = {
  q: searchParams.get('q') || undefined,
  status: searchParams.get('status') || 'all',
  priority: searchParams.get('priority') || undefined,
  // ...
};

// Update URL when filters change
const updateFilters = (newFilters) => {
  const params = new URLSearchParams();
  Object.entries(newFilters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  setSearchParams(params);
};
```

---

## Component Structure

### Primary Component: `AdvancedSearchPanel.tsx`

**Location**: `frontend/src/components/todos/AdvancedSearchPanel.tsx`

**Props Interface**:
```typescript
interface AdvancedSearchPanelProps {
  filters: TodoSearchFilters;
  onFiltersChange: (filters: TodoSearchFilters) => void;
  isExpanded?: boolean;
  onToggle?: () => void;
}
```

**Subcomponents**:
1. `SearchInput` - Text search with fuzzy toggle
2. `StatusFilter` - Radio group (all / active / completed)
3. `PriorityFilter` - Checkbox group (LOW / MEDIUM / HIGH / URGENT)
4. `TagFilter` - Autocomplete multi-select
5. `DateRangeFilter` - Due date from/to pickers
6. `SortControls` - Dropdown + asc/desc toggle
7. `AppliedFilters` - Chips showing active filters with remove buttons

### Hook: `useTodoSearch.ts`

**Location**: `frontend/src/hooks/useTodoSearch.ts`

**Purpose**: Manage search state and API calls

**Interface**:
```typescript
interface UseTodoSearchResult {
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
```

### Hook: `useTagAutocomplete.ts`

**Location**: `frontend/src/hooks/useTagAutocomplete.ts`

**Purpose**: Debounced tag autocomplete

**Interface**:
```typescript
interface UseTagAutocompleteResult {
  suggestions: TagSuggestion[];
  loading: boolean;
  search: (query: string) => void;
}
```

---

## Implementation Tasks Breakdown

### Phase 1: Type Safety & API Layer (COMPLETE ✅)

- [X] Update `frontend/src/types/todo.ts` with V4 types
- [X] Add `Priority`, `TodoSearchFilters`, `TodoSearchResponse`
- [X] Add `TagSuggestion`, `PopularTag` types

### Phase 2: Core Hooks (45 mins)

#### T1: Create `useTodoSearch.ts`
```typescript
// frontend/src/hooks/useTodoSearch.ts
import { useState, useCallback, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { TodoSearchFilters, TodoSearchResponse, Todo } from '@/types/todo';

export function useTodoSearch() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [results, setResults] = useState<Todo[]>([]);
  const [pagination, setPagination] = useState({ total: 0, limit: 20, offset: 0, has_more: false });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Parse filters from URL
  const filters: TodoSearchFilters = {
    q: searchParams.get('q') || undefined,
    status: (searchParams.get('status') as any) || 'all',
    priority: searchParams.get('priority') || undefined,
    tags: searchParams.get('tags') || undefined,
    sort_by: (searchParams.get('sort_by') as any) || 'created_at',
    sort_order: (searchParams.get('sort_order') as any) || 'desc',
    limit: Number(searchParams.get('limit')) || 20,
    offset: Number(searchParams.get('offset')) || 0,
  };

  // Fetch search results
  const executeSearch = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== 'all') {
          params.set(key, String(value));
        }
      });

      const response = await fetch(`/api/v1/todos/search?${params}`);
      if (!response.ok) throw new Error('Search failed');

      const data: TodoSearchResponse = await response.json();
      setResults(data.results);
      setPagination(data.pagination);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Update filters (updates URL)
  const setFilters = useCallback((newFilters: Partial<TodoSearchFilters>) => {
    const params = new URLSearchParams(searchParams);
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.set(key, String(value));
      } else {
        params.delete(key);
      }
    });
    setSearchParams(params);
  }, [searchParams, setSearchParams]);

  const clearFilters = () => setSearchParams(new URLSearchParams());
  const nextPage = () => setFilters({ offset: pagination.offset + pagination.limit });
  const prevPage = () => setFilters({ offset: Math.max(0, pagination.offset - pagination.limit) });

  // Auto-execute search when URL changes
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
```

#### T2: Create `useTagAutocomplete.ts`
```typescript
// frontend/src/hooks/useTagAutocomplete.ts
import { useState, useCallback, useRef } from 'react';
import { TagSuggestion } from '@/types/todo';

export function useTagAutocomplete(debounceMs: number = 300) {
  const [suggestions, setSuggestions] = useState<TagSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout>();

  const search = useCallback((query: string) => {
    // Clear previous timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Don't search if query too short
    if (query.length < 2) {
      setSuggestions([]);
      return;
    }

    // Debounce API call
    timeoutRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/v1/tags/autocomplete?q=${encodeURIComponent(query)}&limit=10`);
        if (response.ok) {
          const data: TagSuggestion[] = await response.json();
          setSuggestions(data);
        }
      } catch (error) {
        console.error('Tag autocomplete failed:', error);
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    }, debounceMs);
  }, [debounceMs]);

  return { suggestions, loading, search };
}
```

#### T3: Create `usePopularTags.ts`
```typescript
// frontend/src/hooks/usePopularTags.ts
import { useState, useEffect } from 'react';
import { PopularTag } from '@/types/todo';

export function usePopularTags(limit: number = 10) {
  const [tags, setTags] = useState<PopularTag[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPopularTags() {
      try {
        const response = await fetch(`/api/v1/tags/popular?limit=${limit}`);
        if (response.ok) {
          const data: PopularTag[] = await response.json();
          setTags(data);
        }
      } catch (error) {
        console.error('Failed to fetch popular tags:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchPopularTags();
  }, [limit]);

  return { tags, loading };
}
```

### Phase 3: UI Components (90 mins)

#### T4: Create `AdvancedSearchPanel.tsx` (Main Component)

**Features Required**:
- Collapsible panel (expand/collapse button)
- Search input with clear button
- Status radio group
- Priority checkboxes (multi-select)
- Tag autocomplete input with chips
- Popular tag quick-add buttons
- Date range picker for due dates
- Sort dropdown + order toggle
- Applied filters chips with remove

**Accessibility**:
- Keyboard navigation
- ARIA labels
- Focus management

#### T5: Create Subcomponents

**`SearchInput.tsx`**:
```typescript
interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  onClear: () => void;
  placeholder?: string;
}
```

**`PriorityFilter.tsx`**:
```typescript
interface PriorityFilterProps {
  selected: Priority[];
  onChange: (priorities: Priority[]) => void;
}
```

**`TagAutocompleteInput.tsx`**:
```typescript
interface TagAutocompleteInputProps {
  selectedTags: string[];
  onTagsChange: (tags: string[]) => void;
}
```

**`PopularTagsPanel.tsx`**:
```typescript
interface PopularTagsPanelProps {
  onTagClick: (tag: string) => void;
  selectedTags: string[];
}
```

**`AppliedFilters.tsx`**:
```typescript
interface AppliedFiltersProps {
  filters: TodoSearchFilters;
  onRemoveFilter: (filterKey: keyof TodoSearchFilters) => void;
  onClearAll: () => void;
}
```

### Phase 4: Dashboard Integration (30 mins)

#### T6: Update Dashboard Page

**File**: `frontend/src/app/dashboard/page.tsx`

**Changes**:
1. Import `useTodoSearch` hook
2. Replace static todo list with search results
3. Add `<AdvancedSearchPanel>` above TodoList
4. Add pagination controls below TodoList
5. Handle loading and error states

**Skeleton Code**:
```typescript
'use client';

import { AdvancedSearchPanel } from '@/components/todos/AdvancedSearchPanel';
import TodoList from '@/components/todos/TodoList';
import { useTodoSearch } from '@/hooks/useTodoSearch';

export default function DashboardPage() {
  const {
    results,
    pagination,
    filters,
    loading,
    error,
    setFilters,
    clearFilters,
    nextPage,
    prevPage,
  } = useTodoSearch();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">My TODOs</h1>

      {/* Advanced Search Panel */}
      <AdvancedSearchPanel
        filters={filters}
        onFiltersChange={setFilters}
      />

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-4 mb-4">
          <p className="text-red-800">{error.message}</p>
        </div>
      )}

      {/* Results */}
      <TodoList
        todos={results}
        isLoading={loading}
        onUpdate={async (id, data) => {/* TODO */}}
        onDelete={async (id) => {/* TODO */}}
      />

      {/* Pagination */}
      {!loading && pagination.total > 0 && (
        <div className="flex justify-between items-center mt-6">
          <p className="text-sm text-gray-600">
            Showing {pagination.offset + 1}-{Math.min(pagination.offset + pagination.limit, pagination.total)} of {pagination.total}
          </p>
          <div className="flex gap-2">
            <button
              onClick={prevPage}
              disabled={pagination.offset === 0}
              className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={nextPage}
              disabled={!pagination.has_more}
              className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
```

### Phase 5: Testing (30 mins)

#### T7: Component Tests

**Framework**: Jest + React Testing Library

**Test Cases**:
1. Search input triggers debounced API call
2. Priority filter updates URL params
3. Tag autocomplete shows suggestions
4. Popular tags clickable and add to filter
5. Applied filters chips removable
6. Pagination buttons work correctly
7. Clear all filters resets to defaults
8. Keyboard navigation works

**Example Test**:
```typescript
// frontend/__tests__/components/AdvancedSearchPanel.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AdvancedSearchPanel } from '@/components/todos/AdvancedSearchPanel';

describe('AdvancedSearchPanel', () => {
  it('updates filters when search input changes', async () => {
    const onFiltersChange = jest.fn();
    render(<AdvancedSearchPanel filters={{}} onFiltersChange={onFiltersChange} />);

    const input = screen.getByPlaceholderText(/search/i);
    fireEvent.change(input, { target: { value: 'test query' } });

    await waitFor(() => {
      expect(onFiltersChange).toHaveBeenCalledWith({ q: 'test query' });
    });
  });

  it('adds tag when popular tag clicked', () => {
    const onFiltersChange = jest.fn();
    render(<AdvancedSearchPanel filters={{}} onFiltersChange={onFiltersChange} />);

    const tag = screen.getByText('urgent');
    fireEvent.click(tag);

    expect(onFiltersChange).toHaveBeenCalledWith({ tags: 'urgent' });
  });
});
```

---

## UI/UX Design Specifications

### Color Scheme (Tailwind CSS)

**Filter Panel**:
- Background: `bg-white dark:bg-gray-800`
- Border: `border border-gray-200 dark:border-gray-700`
- Shadow: `shadow-md`

**Filter Controls**:
- Active filter: `bg-blue-50 border-blue-500`
- Inactive filter: `bg-gray-50 border-gray-300`

**Applied Filters Chips**:
- Background: `bg-blue-100`
- Text: `text-blue-800`
- Remove button: `text-blue-600 hover:text-blue-900`

**Popular Tags**:
- Badge: `bg-purple-100 text-purple-800`
- Hover: `hover:bg-purple-200`

### Layout Structure

```
┌─────────────────────────────────────────────────┐
│ Advanced Search                         [Toggle]│
├─────────────────────────────────────────────────┤
│ Search: [_____________________] [Fuzzy: ☐]      │
│                                                  │
│ Status:  ( ) All  ( ) Active  (●) Completed     │
│                                                  │
│ Priority: [☐] LOW  [☑] MEDIUM  [☑] HIGH  [☐] URGENT │
│                                                  │
│ Tags: [backend_____v]  [x backend] [x api]      │
│   Suggestions: backend-api, backend-python       │
│                                                  │
│ Popular: [urgent (50)] [test (8)] [api (5)]     │
│                                                  │
│ Due Date: [From: ____] [To: ____]               │
│                                                  │
│ Sort: [Created At ▼]  [▲ Desc]                  │
│                                                  │
│ Applied: [x Status: Completed] [x Priority: MEDIUM, HIGH] │
│          [Clear All]                             │
└─────────────────────────────────────────────────┘
```

### Responsive Behavior

**Desktop (>= 1024px)**:
- Full panel visible by default
- Filters in 2-column grid
- Tags and popular tags side-by-side

**Tablet (768px - 1023px)**:
- Panel collapsible
- Filters in 1-column grid
- Tags and popular tags stacked

**Mobile (<= 767px)**:
- Panel collapsed by default
- Full-screen overlay when expanded
- Touch-optimized controls

---

## API Integration Points

### 1. Search Endpoint

**URL**: `GET /api/v1/todos/search`

**Request Parameters** (from `TodoSearchFilters`):
```typescript
{
  q?: string,
  status?: 'all' | 'active' | 'completed',
  priority?: 'LOW,MEDIUM,HIGH',
  tags?: 'backend,api',
  sort_by?: 'created_at',
  sort_order?: 'desc',
  limit?: 20,
  offset?: 0
}
```

**Response**: `TodoSearchResponse`

**Error Handling**:
- Network error → Show retry button
- 400 Bad Request → Display validation error
- 500 Server Error → Show generic error message

### 2. Tag Autocomplete

**URL**: `GET /api/v1/tags/autocomplete?q=<prefix>&limit=10`

**Debounce**: 300ms

**Min Query Length**: 2 characters

**Response**: `TagSuggestion[]`

### 3. Popular Tags

**URL**: `GET /api/v1/tags/popular?limit=10`

**Cache**: 5 minutes (local state)

**Response**: `PopularTag[]`

---

## Performance Optimization

### Debouncing

- Search input: 300ms debounce
- Tag autocomplete: 300ms debounce

### Caching

- Popular tags: Cache for 5 minutes
- Search results: Cache by URL params (SWR pattern)

### Code Splitting

```typescript
// Lazy load panel if not visible initially
const AdvancedSearchPanel = dynamic(() => import('@/components/todos/AdvancedSearchPanel'), {
  loading: () => <PanelSkeleton />,
});
```

### Request Deduplication

- Use SWR or React Query to avoid duplicate API calls
- Abort ongoing requests when filters change

---

## Accessibility Requirements

### Keyboard Navigation

- Tab order: Search input → Status → Priority → Tags → Sort → Filters
- Enter key: Submit search
- Escape key: Close tag suggestions / Clear search
- Arrow keys: Navigate tag suggestions

### Screen Reader Support

```tsx
<label htmlFor="search-input" className="sr-only">
  Search todos
</label>
<input
  id="search-input"
  type="text"
  aria-label="Search todos by title, description, or tags"
  aria-describedby="search-hint"
/>
<div id="search-hint" className="sr-only">
  Type at least 2 characters to search
</div>
```

### Focus Management

- Focus search input when panel expands
- Return focus to toggle button when panel collapses
- Focus first tag suggestion when dropdown opens

---

## Error Handling Strategies

### Network Errors

```typescript
if (error) {
  return (
    <div className="bg-red-50 border border-red-200 rounded p-4">
      <p className="text-red-800 mb-2">Failed to load search results</p>
      <button onClick={refresh} className="text-red-600 underline">
        Retry
      </button>
    </div>
  );
}
```

### Empty States

```typescript
if (!loading && results.length === 0 && Object.keys(filters).length > 0) {
  return (
    <div className="text-center py-12">
      <p className="text-gray-600 mb-4">No results found for your search</p>
      <button onClick={clearFilters} className="text-blue-600 underline">
        Clear all filters
      </button>
    </div>
  );
}
```

### Validation Errors

```typescript
// Validate date ranges
if (filters.due_date_from && filters.due_date_to) {
  if (new Date(filters.due_date_from) > new Date(filters.due_date_to)) {
    return <ErrorMessage>Start date must be before end date</ErrorMessage>;
  }
}
```

---

## Testing Strategy

### Unit Tests

**Tools**: Jest + React Testing Library

**Coverage Targets**:
- Hooks: 90%
- Components: 80%
- Utils: 100%

**Test Files**:
```
frontend/__tests__/
├── hooks/
│   ├── useTodoSearch.test.ts
│   ├── useTagAutocomplete.test.ts
│   └── usePopularTags.test.ts
├── components/
│   ├── AdvancedSearchPanel.test.tsx
│   ├── TagAutocompleteInput.test.tsx
│   └── AppliedFilters.test.tsx
└── integration/
    └── searchFlow.test.tsx
```

### Integration Tests

**Scenarios**:
1. User searches for "backend", selects "HIGH" priority, clicks "Search"
2. User adds tag via autocomplete, tag appears in applied filters
3. User clicks popular tag, search executes automatically
4. User clears all filters, URL resets to default
5. User navigates to next page, URL updates with offset

### E2E Tests (Optional)

**Tool**: Playwright

**Critical Paths**:
1. Full search workflow end-to-end
2. Pagination through multiple pages
3. Filter combination (search + tags + priority)

---

## Deployment Checklist

### Pre-Deployment

- [ ] All TypeScript types updated
- [ ] All hooks implemented and tested
- [ ] AdvancedSearchPanel component complete
- [ ] Dashboard integration complete
- [ ] Unit tests passing (>80% coverage)
- [ ] Accessibility audit passed
- [ ] Responsive design tested (mobile, tablet, desktop)
- [ ] Error handling implemented
- [ ] Loading states implemented

### Post-Deployment Validation

- [ ] Search endpoint returns results
- [ ] Tag autocomplete works on live API
- [ ] Popular tags load correctly
- [ ] Pagination works end-to-end
- [ ] URL params update correctly
- [ ] Browser back/forward works
- [ ] No console errors
- [ ] Performance metrics acceptable (< 3s page load)

---

## Next Steps

### Immediate (V4-T005 Execution)

1. **Implement Core Hooks** (45 mins)
   - `useTodoSearch.ts`
   - `useTagAutocomplete.ts`
   - `usePopularTags.ts`

2. **Build UI Components** (90 mins)
   - `AdvancedSearchPanel.tsx` (main component)
   - Subcomponents (SearchInput, PriorityFilter, TagAutocompleteInput, etc.)

3. **Dashboard Integration** (30 mins)
   - Update dashboard page
   - Connect hooks to components
   - Add pagination controls

4. **Testing** (30 mins)
   - Unit tests for hooks
   - Component tests
   - Integration test for search flow

**Total Estimated Time**: 3 hours

### After V4-T005

- **V4-T006**: Dashboard enhancements (quick filter buttons, improved layout)
- **V4-T007**: Integration testing across all V4 features
- **V4-T008**: Documentation (API guide, component usage, troubleshooting)

---

## Risk Mitigation

### Risk: Type Mismatches with Backend

**Mitigation**: Updated `frontend/src/types/todo.ts` to exactly match backend Pydantic models

### Risk: Performance Issues with Many Filters

**Mitigation**: Debouncing, request cancellation, SWR caching

### Risk: Complex State Management

**Mitigation**: URL-based state (shareable, no Redux complexity)

### Risk: Accessibility Gaps

**Mitigation**: ARIA labels, keyboard navigation plan, focus management

---

## Conclusion

This implementation plan provides a complete roadmap for V4-T005. The backend APIs are operational, types are updated, and the component architecture is designed for maintainability and scalability.

**Ready for Implementation**: All prerequisites met. Frontend development can proceed immediately using this plan as specification.

---

**Last Updated**: 2026-02-07
**Status**: Planning Complete - Ready for Frontend Development
**Estimated Completion**: 3 hours of frontend development time
