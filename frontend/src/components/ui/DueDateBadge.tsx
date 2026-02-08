/**
 * Due Date Badge Component
 *
 * Displays todo due date with visual indicators:
 * - Overdue → red text + warning icon
 * - Due soon (≤ 3 days) → amber
 * - Future → muted
 */

interface DueDateBadgeProps {
  dueDate: string | null;
  completed?: boolean;
  size?: 'sm' | 'md';
  className?: string;
}

export function DueDateBadge({ dueDate, completed = false, size = 'md', className = '' }: DueDateBadgeProps) {
  if (!dueDate) return null;

  const now = new Date();
  const due = new Date(dueDate);
  const diffDays = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

  // Determine status
  let status: 'overdue' | 'due-soon' | 'future' = 'future';
  let statusText = '';
  let colorClasses = '';

  if (completed) {
    // Completed tasks show neutral styling
    colorClasses = 'text-gray-400 bg-gray-50 border-gray-200';
    statusText = formatDate(due);
  } else if (diffDays < 0) {
    // Overdue
    status = 'overdue';
    const daysOverdue = Math.abs(diffDays);
    statusText = `${daysOverdue} ${daysOverdue === 1 ? 'day' : 'days'} overdue`;
    colorClasses = 'text-red-700 bg-red-50 border-red-200';
  } else if (diffDays === 0) {
    // Due today
    status = 'due-soon';
    statusText = 'Due today';
    colorClasses = 'text-amber-700 bg-amber-50 border-amber-200';
  } else if (diffDays <= 3) {
    // Due soon (within 3 days)
    status = 'due-soon';
    statusText = `Due in ${diffDays} ${diffDays === 1 ? 'day' : 'days'}`;
    colorClasses = 'text-amber-600 bg-amber-50 border-amber-200';
  } else {
    // Future
    status = 'future';
    statusText = `Due ${formatDate(due)}`;
    colorClasses = 'text-gray-600 bg-gray-50 border-gray-200';
  }

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1 font-medium rounded-full border ${colorClasses} ${sizeClasses} ${className}`}
      aria-label={`Due date: ${statusText}`}
    >
      {!completed && status === 'overdue' && (
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
            clipRule="evenodd"
          />
        </svg>
      )}
      {!completed && status === 'due-soon' && (
        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      )}
      {(completed || status === 'future') && (
        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      )}
      <span>{statusText}</span>
    </span>
  );
}

function formatDate(date: Date): string {
  const now = new Date();
  const isThisYear = date.getFullYear() === now.getFullYear();

  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    ...(isThisYear ? {} : { year: 'numeric' }),
  });
}
