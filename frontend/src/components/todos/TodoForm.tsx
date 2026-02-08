'use client';

/**
 * Todo Form Component
 *
 * Modern form for creating new todos with validation and animations.
 * Includes Phase V.4 fields: priority and due date.
 */

import { useState, FormEvent } from 'react';
import { TodoCreate, Priority } from '@/types/todo';

interface TodoFormProps {
  onCreate: (data: TodoCreate) => Promise<void>;
}

const PRIORITY_OPTIONS: { value: Priority; label: string; color: string }[] = [
  { value: 'LOW', label: 'Low', color: 'bg-gray-100 text-gray-700 border-gray-300 hover:border-gray-400' },
  { value: 'MEDIUM', label: 'Medium', color: 'bg-blue-50 text-blue-700 border-blue-300 hover:border-blue-400' },
  { value: 'HIGH', label: 'High', color: 'bg-orange-50 text-orange-700 border-orange-300 hover:border-orange-400' },
  { value: 'URGENT', label: 'Urgent', color: 'bg-red-50 text-red-700 border-red-300 hover:border-red-400' },
];

const SELECTED_COLORS: Record<Priority, string> = {
  LOW: 'bg-gray-200 text-gray-800 border-gray-400 ring-2 ring-gray-300',
  MEDIUM: 'bg-blue-100 text-blue-800 border-blue-400 ring-2 ring-blue-300',
  HIGH: 'bg-orange-100 text-orange-800 border-orange-400 ring-2 ring-orange-300',
  URGENT: 'bg-red-100 text-red-800 border-red-400 ring-2 ring-red-300',
};

export default function TodoForm({ onCreate }: TodoFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<Priority>('MEDIUM');
  const [dueDate, setDueDate] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');

    if (!title.trim()) {
      setError('Please enter a task title');
      return;
    }

    if (title.length > 200) {
      setError('Title must be 200 characters or less');
      return;
    }

    if (description.length > 2000) {
      setError('Description must be 2000 characters or less');
      return;
    }

    try {
      setIsLoading(true);

      const todoData: TodoCreate = {
        title: title.trim(),
        description: description.trim() || null,
        priority,
        due_date: dueDate ? `${dueDate}T23:59:59.000Z` : null,
      };

      await onCreate(todoData);

      // Clear form on success
      setTitle('');
      setDescription('');
      setPriority('MEDIUM');
      setDueDate('');
      setIsExpanded(false);
    } catch (err: any) {
      setError(err.message || 'Failed to create task');
    } finally {
      setIsLoading(false);
    }
  };

  // Minimum date for the date picker: today
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="bg-white shadow-sm rounded-2xl border border-gray-100 overflow-hidden">
      <form onSubmit={handleSubmit}>
        {/* Main Input */}
        <div className="p-4 sm:p-6">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              onFocus={() => setIsExpanded(true)}
              maxLength={200}
              className="flex-1 px-4 py-3 text-lg border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all bg-gray-50 focus:bg-white placeholder-gray-400"
              placeholder="What needs to be done?"
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Expanded Section */}
        <div className={`transition-all duration-300 ease-in-out overflow-hidden ${
          isExpanded ? 'max-h-[32rem] opacity-100' : 'max-h-0 opacity-0'
        }`}>
          <div className="px-4 sm:px-6 pb-4 sm:pb-6 space-y-4">
            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Description <span className="text-gray-400">(optional)</span>
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                maxLength={2000}
                rows={3}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all bg-gray-50 focus:bg-white resize-none placeholder-gray-400"
                placeholder="Add more details about this task..."
                disabled={isLoading}
              />
              <div className="flex justify-between mt-1">
                <span className="text-xs text-gray-400">
                  {description.length}/2000 characters
                </span>
                <span className="text-xs text-gray-400">
                  {title.length}/200 characters
                </span>
              </div>
            </div>

            {/* Priority + Due Date row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Priority Selector */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Priority
                </label>
                <div className="flex gap-2 flex-wrap">
                  {PRIORITY_OPTIONS.map(({ value, label, color }) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() => setPriority(value)}
                      disabled={isLoading}
                      className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all ${
                        priority === value ? SELECTED_COLORS[value] : color
                      } disabled:opacity-50`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Due Date Picker */}
              <div>
                <label htmlFor="due-date" className="block text-sm font-medium text-gray-700 mb-2">
                  Due Date <span className="text-gray-400">(optional)</span>
                </label>
                <input
                  id="due-date"
                  type="date"
                  value={dueDate}
                  min={today}
                  onChange={(e) => setDueDate(e.target.value)}
                  disabled={isLoading}
                  className="w-full px-4 py-2.5 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all bg-gray-50 focus:bg-white text-gray-700 disabled:opacity-50"
                />
                {dueDate && (
                  <button
                    type="button"
                    onClick={() => setDueDate('')}
                    className="mt-1 text-xs text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    Clear date
                  </button>
                )}
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm animate-fade-in">
                <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {error}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => {
                  setIsExpanded(false);
                  setTitle('');
                  setDescription('');
                  setPriority('MEDIUM');
                  setDueDate('');
                  setError('');
                }}
                disabled={isLoading}
                className="px-4 py-2 text-gray-600 font-medium rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading || !title.trim()}
                className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg shadow-md shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all"
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Creating...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Add Task
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}
