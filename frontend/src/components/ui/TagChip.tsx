/**
 * Tag Chip Component
 *
 * Displays todo tags as compact, clickable chips.
 * Supports click handler for filtering by tag.
 */

interface TagChipProps {
  tag: string;
  onClick?: (tag: string) => void;
  onRemove?: (tag: string) => void;
  variant?: 'default' | 'filter' | 'selected';
  size?: 'sm' | 'md';
  className?: string;
}

const VARIANT_STYLES = {
  default: 'bg-purple-100 text-purple-700 border-purple-200 hover:bg-purple-200',
  filter: 'bg-indigo-100 text-indigo-700 border-indigo-200 hover:bg-indigo-200',
  selected: 'bg-blue-100 text-blue-800 border-blue-300',
};

const SIZE_CLASSES = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-xs',
};

export function TagChip({
  tag,
  onClick,
  onRemove,
  variant = 'default',
  size = 'md',
  className = '',
}: TagChipProps) {
  const handleClick = () => {
    if (onClick) {
      onClick(tag);
    }
  };

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onRemove) {
      onRemove(tag);
    }
  };

  return (
    <span
      onClick={onClick ? handleClick : undefined}
      className={`inline-flex items-center gap-1 font-medium rounded-full border ${VARIANT_STYLES[variant]} ${SIZE_CLASSES[size]} ${
        onClick ? 'cursor-pointer transition-colors' : ''
      } ${className}`}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleClick();
              }
            }
          : undefined
      }
      aria-label={`Tag: ${tag}`}
    >
      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
        />
      </svg>
      <span>{tag}</span>
      {onRemove && (
        <button
          onClick={handleRemove}
          className="ml-0.5 hover:text-current transition-colors"
          aria-label={`Remove tag ${tag}`}
          type="button"
        >
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </span>
  );
}
