/**
 * Priority Badge Component
 *
 * Displays todo priority with consistent color coding:
 * - LOW → gray
 * - MEDIUM → blue
 * - HIGH → orange
 * - URGENT → red
 */

import React from 'react';
import { Priority } from '@/types/todo';

interface PriorityBadgeProps {
  priority: Priority;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const PRIORITY_STYLES: Record<Priority, string> = {
  LOW: 'bg-gray-100 text-gray-700 border-gray-200',
  MEDIUM: 'bg-blue-100 text-blue-700 border-blue-200',
  HIGH: 'bg-orange-100 text-orange-700 border-orange-200',
  URGENT: 'bg-red-100 text-red-700 border-red-200',
};

const PRIORITY_ICONS: Record<Priority, React.ReactElement> = {
  LOW: (
    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
    </svg>
  ),
  MEDIUM: (
    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
    </svg>
  ),
  HIGH: (
    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
    </svg>
  ),
  URGENT: (
    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
    </svg>
  ),
};

const SIZE_CLASSES = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-xs',
  lg: 'px-3 py-1.5 text-sm',
};

export function PriorityBadge({ priority, size = 'md', className = '' }: PriorityBadgeProps) {
  return (
    <span
      className={`inline-flex items-center gap-1 font-medium rounded-full border ${PRIORITY_STYLES[priority]} ${SIZE_CLASSES[size]} ${className}`}
      aria-label={`Priority: ${priority}`}
    >
      {PRIORITY_ICONS[priority]}
      <span className="capitalize">{priority.toLowerCase()}</span>
    </span>
  );
}
