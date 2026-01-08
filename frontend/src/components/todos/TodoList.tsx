'use client';

/**
 * Todo List Component
 *
 * Displays a list of todos with filter options and skeleton loading states.
 */

import { Todo, TodoUpdate } from '@/types/todo';
import TodoItem from './TodoItem';
import { SkeletonTodoList } from '@/components/ui/Skeleton';

interface TodoListProps {
  todos: Todo[];
  isLoading: boolean;
  onUpdate: (id: number, data: TodoUpdate) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

export default function TodoList({ todos, isLoading, onUpdate, onDelete }: TodoListProps) {
  if (isLoading) {
    return <SkeletonTodoList count={4} />;
  }

  if (todos.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No todos</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by creating a new todo above.
        </p>
      </div>
    );
  }

  // Separate completed and pending todos
  const pendingTodos = todos.filter((todo) => !todo.completed);
  const completedTodos = todos.filter((todo) => todo.completed);

  return (
    <div className="space-y-8">
      {/* Pending Todos */}
      {pendingTodos.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <span className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></span>
            Pending ({pendingTodos.length})
          </h3>
          <div className="space-y-3">
            {pendingTodos.map((todo, index) => (
              <div
                key={todo.id}
                className="animate-slide-up-fade"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <TodoItem
                  todo={todo}
                  onUpdate={onUpdate}
                  onDelete={onDelete}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Completed Todos */}
      {completedTodos.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            Completed ({completedTodos.length})
          </h3>
          <div className="space-y-3">
            {completedTodos.map((todo, index) => (
              <div
                key={todo.id}
                className="animate-slide-up-fade"
                style={{ animationDelay: `${(pendingTodos.length + index) * 50}ms` }}
              >
                <TodoItem
                  todo={todo}
                  onUpdate={onUpdate}
                  onDelete={onDelete}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
