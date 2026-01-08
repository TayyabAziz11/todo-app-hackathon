'use client';

/**
 * Skeleton Loading Component
 *
 * Provides various skeleton loading states for a polished loading experience.
 */

import { ReactNode } from 'react';

interface SkeletonProps {
  className?: string;
  children?: ReactNode;
}

// Base skeleton with shimmer effect
export function Skeleton({ className = '' }: SkeletonProps) {
  return (
    <div
      className={`animate-pulse bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 bg-[length:200%_100%] animate-shimmer rounded ${className}`}
      style={{
        animation: 'shimmer 1.5s infinite',
      }}
    />
  );
}

// Text skeleton
export function SkeletonText({ lines = 1, className = '' }: { lines?: number; className?: string }) {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className={`h-4 ${i === lines - 1 && lines > 1 ? 'w-3/4' : 'w-full'}`}
        />
      ))}
    </div>
  );
}

// Avatar skeleton
export function SkeletonAvatar({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-14 h-14',
  };

  return <Skeleton className={`${sizes[size]} rounded-full`} />;
}

// Button skeleton
export function SkeletonButton({ className = '' }: { className?: string }) {
  return <Skeleton className={`h-10 w-24 rounded-lg ${className}`} />;
}

// Card skeleton
export function SkeletonCard({ className = '' }: { className?: string }) {
  return (
    <div className={`bg-white rounded-xl p-4 shadow-sm ${className}`}>
      <div className="flex items-start gap-4">
        <Skeleton className="w-6 h-6 rounded-full flex-shrink-0" />
        <div className="flex-1 space-y-3">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-1/2" />
        </div>
        <Skeleton className="w-16 h-6 rounded-full" />
      </div>
    </div>
  );
}

// Todo item skeleton
export function SkeletonTodoItem() {
  return (
    <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        <Skeleton className="w-6 h-6 rounded-full flex-shrink-0" />

        {/* Content */}
        <div className="flex-1 min-w-0">
          <Skeleton className="h-5 w-3/4 mb-2" />
          <Skeleton className="h-3 w-full mb-1" />
          <Skeleton className="h-3 w-1/2 mb-3" />
          <div className="flex gap-3">
            <Skeleton className="h-3 w-16" />
            <Skeleton className="h-3 w-12" />
          </div>
        </div>

        {/* Badge */}
        <Skeleton className="w-16 h-6 rounded-full hidden sm:block" />

        {/* Action buttons */}
        <div className="flex gap-1">
          <Skeleton className="w-8 h-8 rounded-lg" />
          <Skeleton className="w-8 h-8 rounded-lg" />
        </div>
      </div>
    </div>
  );
}

// Todo list skeleton
export function SkeletonTodoList({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonTodoItem key={i} />
      ))}
    </div>
  );
}

// Stats skeleton
export function SkeletonStats() {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="bg-white rounded-xl p-4 shadow-sm">
          <Skeleton className="h-8 w-16 mb-2" />
          <Skeleton className="h-3 w-20" />
        </div>
      ))}
    </div>
  );
}

// Form skeleton
export function SkeletonForm() {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      <div className="flex items-center gap-4 mb-4">
        <Skeleton className="w-10 h-10 rounded-full" />
        <Skeleton className="flex-1 h-12 rounded-xl" />
      </div>
      <div className="space-y-4 pl-14">
        <Skeleton className="h-20 rounded-xl" />
        <div className="flex justify-end gap-3">
          <Skeleton className="w-20 h-10 rounded-lg" />
          <Skeleton className="w-28 h-10 rounded-lg" />
        </div>
      </div>
    </div>
  );
}

// Dashboard header skeleton
export function SkeletonDashboardHeader() {
  return (
    <div className="mb-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <Skeleton className="h-8 w-48 mb-2" />
          <Skeleton className="h-4 w-72" />
        </div>
        <div className="flex gap-3">
          <Skeleton className="w-10 h-10 rounded-lg" />
          <Skeleton className="w-10 h-10 rounded-lg" />
        </div>
      </div>
    </div>
  );
}

// Full dashboard skeleton
export function SkeletonDashboard() {
  return (
    <div className="min-h-screen bg-gray-50 pt-20 pb-8">
      <div className="max-w-4xl mx-auto px-4">
        <SkeletonDashboardHeader />
        <div className="mb-8">
          <SkeletonStats />
        </div>
        <div className="mb-8">
          <SkeletonForm />
        </div>
        <SkeletonTodoList count={5} />
      </div>
    </div>
  );
}
