/**
 * Advanced Search Panel Component
 *
 * Features:
 * - Multi-criteria search (text, status, priority, tags, dates)
 * - Tag autocomplete integration
 * - Popular tags quick-add
 * - Sort controls
 * - Applied filters display
 * - Collapsible panel
 * - Keyboard accessible
 * - Responsive design
 */

'use client';

import { useState } from 'react';
import { TodoSearchFilters, Priority } from '@/types/todo';
import { useTagAutocomplete } from '@/hooks/useTagAutocomplete';
import { usePopularTags } from '@/hooks/usePopularTags';

export interface AdvancedSearchPanelProps {
  filters: TodoSearchFilters;
  onFiltersChange: (filters: Partial<TodoSearchFilters>) => void;
  isExpanded?: boolean;
  onToggle?: () => void;
}

export function AdvancedSearchPanel({
  filters,
  onFiltersChange,
  isExpanded = true,
  onToggle,
}: AdvancedSearchPanelProps) {
  const [searchText, setSearchText] = useState(filters.q || '');
  const [tagInput, setTagInput] = useState('');
  const { suggestions, loading: tagsLoading, search: searchTags, clearSuggestions } = useTagAutocomplete();
  const { tags: popularTags, loading: popularLoading } = usePopularTags(10);

  // Parse selected tags from filters
  const selectedTags = filters.tags ? filters.tags.split(',').filter(Boolean) : [];

  // Parse selected priorities from filters
  const selectedPriorities = filters.priority ? filters.priority.split(',') as Priority[] : [];

  // Handle search text input
  const handleSearchChange = (value: string) => {
    setSearchText(value);
  };

  // Handle search text submit (debounced via blur or enter)
  const handleSearchSubmit = () => {
    onFiltersChange({ q: searchText || undefined });
  };

  // Handle status filter change
  const handleStatusChange = (status: 'all' | 'active' | 'completed') => {
    onFiltersChange({ status });
  };

  // Handle priority toggle
  const handlePriorityToggle = (priority: Priority) => {
    const newPriorities = selectedPriorities.includes(priority)
      ? selectedPriorities.filter(p => p !== priority)
      : [...selectedPriorities, priority];

    onFiltersChange({
      priority: newPriorities.length > 0 ? newPriorities.join(',') : undefined,
    });
  };

  // Handle tag autocomplete input
  const handleTagInputChange = (value: string) => {
    setTagInput(value);
    searchTags(value);
  };

  // Handle tag selection from autocomplete or popular tags
  const handleTagAdd = (tag: string) => {
    if (!selectedTags.includes(tag)) {
      const newTags = [...selectedTags, tag];
      onFiltersChange({ tags: newTags.join(',') });
    }
    setTagInput('');
    clearSuggestions();
  };

  // Handle tag removal
  const handleTagRemove = (tag: string) => {
    const newTags = selectedTags.filter(t => t !== tag);
    onFiltersChange({ tags: newTags.length > 0 ? newTags.join(',') : undefined });
  };

  // Handle sort change
  const handleSortChange = (sortBy: TodoSearchFilters['sort_by']) => {
    onFiltersChange({ sort_by: sortBy });
  };

  // Handle sort order toggle
  const handleSortOrderToggle = () => {
    onFiltersChange({ sort_order: filters.sort_order === 'asc' ? 'desc' : 'asc' });
  };

  // Clear all filters
  const handleClearAll = () => {
    setSearchText('');
    setTagInput('');
    onFiltersChange({
      q: undefined,
      status: 'all',
      priority: undefined,
      tags: undefined,
      due_date_from: undefined,
      due_date_to: undefined,
      sort_by: 'created_at',
      sort_order: 'desc',
    });
  };

  // Count active filters
  const activeFilterCount = [
    filters.q,
    filters.status !== 'all' ? filters.status : null,
    filters.priority,
    filters.tags,
    filters.due_date_from,
    filters.due_date_to,
  ].filter(Boolean).length;

  if (!isExpanded) {
    return (
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm p-4 mb-4">
        <button
          onClick={onToggle}
          className="w-full flex items-center justify-between text-left"
          aria-expanded={false}
          aria-controls="advanced-search-panel"
        >
          <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Advanced Search
            {activeFilterCount > 0 && (
              <span className="ml-2 text-sm font-normal text-blue-600">
                ({activeFilterCount} active)
              </span>
            )}
          </span>
          <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
    );
  }

  return (
    <div
      id="advanced-search-panel"
      className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-md p-6 mb-6"
      role="search"
      aria-label="Advanced todo search"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Advanced Search
          {activeFilterCount > 0 && (
            <span className="ml-2 text-sm font-normal text-blue-600">
              ({activeFilterCount} filters)
            </span>
          )}
        </h2>
        {onToggle && (
          <button
            onClick={onToggle}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            aria-label="Collapse search panel"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
            </svg>
          </button>
        )}
      </div>

      {/* Search Input */}
      <div className="mb-4">
        <label htmlFor="search-input" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Search
        </label>
        <div className="flex gap-2">
          <input
            id="search-input"
            type="text"
            value={searchText}
            onChange={(e) => handleSearchChange(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearchSubmit()}
            onBlur={handleSearchSubmit}
            placeholder="Search by title or description..."
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
            aria-label="Search todos by title or description"
          />
          {searchText && (
            <button
              onClick={() => {
                setSearchText('');
                onFiltersChange({ q: undefined });
              }}
              className="px-3 py-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
              aria-label="Clear search"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
        <label className="flex items-center mt-2 text-sm text-gray-600 dark:text-gray-400">
          <input
            type="checkbox"
            checked={filters.fuzzy || false}
            onChange={(e) => onFiltersChange({ fuzzy: e.target.checked || undefined })}
            className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          Enable fuzzy matching
        </label>
      </div>

      {/* Status Filter */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Status
        </label>
        <div className="flex gap-3" role="radiogroup" aria-label="Filter by status">
          {(['all', 'active', 'completed'] as const).map((status) => (
            <label key={status} className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="status"
                value={status}
                checked={filters.status === status}
                onChange={() => handleStatusChange(status)}
                className="mr-2 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">{status}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Priority Filter */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Priority
        </label>
        <div className="flex flex-wrap gap-3">
          {(['LOW', 'MEDIUM', 'HIGH', 'URGENT'] as Priority[]).map((priority) => (
            <label key={priority} className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={selectedPriorities.includes(priority)}
                onChange={() => handlePriorityToggle(priority)}
                className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">{priority}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Tag Filter with Autocomplete */}
      <div className="mb-4">
        <label htmlFor="tag-input" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Tags
        </label>

        {/* Selected Tags */}
        {selectedTags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {selectedTags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200"
              >
                {tag}
                <button
                  onClick={() => handleTagRemove(tag)}
                  className="ml-2 text-blue-600 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-100"
                  aria-label={`Remove tag ${tag}`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </span>
            ))}
          </div>
        )}

        {/* Tag Input with Autocomplete */}
        <div className="relative">
          <input
            id="tag-input"
            type="text"
            value={tagInput}
            onChange={(e) => handleTagInputChange(e.target.value)}
            placeholder="Type to search tags..."
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
            aria-label="Search and add tags"
            aria-autocomplete="list"
            aria-controls="tag-suggestions"
          />

          {/* Autocomplete Suggestions */}
          {tagInput.length >= 2 && suggestions.length > 0 && (
            <ul
              id="tag-suggestions"
              className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto"
              role="listbox"
            >
              {suggestions.map((suggestion) => (
                <li key={suggestion.tag}>
                  <button
                    onClick={() => handleTagAdd(suggestion.tag)}
                    className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-600 text-gray-900 dark:text-gray-100"
                    role="option"
                  >
                    <span>{suggestion.tag}</span>
                    <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">({suggestion.count})</span>
                  </button>
                </li>
              ))}
            </ul>
          )}

          {tagsLoading && (
            <div className="absolute right-3 top-3 text-gray-400">
              <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
          )}
        </div>

        {/* Popular Tags */}
        {!popularLoading && popularTags.length > 0 && (
          <div className="mt-3">
            <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">Popular tags:</p>
            <div className="flex flex-wrap gap-2">
              {popularTags.map((tag) => (
                <button
                  key={tag.tag}
                  onClick={() => handleTagAdd(tag.tag)}
                  disabled={selectedTags.includes(tag.tag)}
                  className="px-3 py-1 text-sm rounded-full bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 hover:bg-purple-200 dark:hover:bg-purple-800 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {tag.tag} ({tag.count})
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Sort Controls */}
      <div className="mb-4">
        <label htmlFor="sort-by" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Sort By
        </label>
        <div className="flex gap-2">
          <select
            id="sort-by"
            value={filters.sort_by || 'created_at'}
            onChange={(e) => handleSortChange(e.target.value as any)}
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
          >
            <option value="created_at">Created Date</option>
            <option value="updated_at">Updated Date</option>
            <option value="due_date">Due Date</option>
            <option value="priority">Priority</option>
            <option value="title">Title</option>
          </select>
          <button
            onClick={handleSortOrderToggle}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 dark:text-gray-100"
            aria-label={`Sort ${filters.sort_order === 'asc' ? 'ascending' : 'descending'}`}
          >
            {filters.sort_order === 'asc' ? '↑ Asc' : '↓ Desc'}
          </button>
        </div>
      </div>

      {/* Applied Filters Summary & Clear All */}
      {activeFilterCount > 0 && (
        <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {activeFilterCount} filter{activeFilterCount !== 1 ? 's' : ''} applied
            </p>
            <button
              onClick={handleClearAll}
              className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
            >
              Clear All
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
