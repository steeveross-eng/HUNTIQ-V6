/**
 * LoadingSpinner - Core Component
 * ================================
 * Reusable loading spinner with various sizes and styles.
 * Architecture LEGO V5 - Core Component (no business logic)
 * 
 * @module core/components
 */
import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({
  size = 'md',
  color = '#f5a623',
  text = null,
  fullScreen = false,
  overlay = false,
  className = ''
}) => {
  const sizeClasses = {
    xs: 'h-4 w-4',
    sm: 'h-6 w-6',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16'
  };

  const spinner = (
    <div className={`flex flex-col items-center justify-center gap-3 ${className}`}>
      <Loader2 
        className={`${sizeClasses[size]} animate-spin`}
        style={{ color }}
      />
      {text && (
        <span className="text-gray-400 text-sm">{text}</span>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-background z-50">
        {spinner}
      </div>
    );
  }

  if (overlay) {
    return (
      <div className="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-40 rounded-lg">
        {spinner}
      </div>
    );
  }

  return spinner;
};

/**
 * LoadingSkeleton - Animated placeholder
 */
export const LoadingSkeleton = ({
  width = '100%',
  height = '20px',
  rounded = 'md',
  className = ''
}) => {
  const roundedClasses = {
    none: 'rounded-none',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    xl: 'rounded-xl',
    full: 'rounded-full'
  };

  return (
    <div 
      className={`bg-gray-800 animate-pulse ${roundedClasses[rounded]} ${className}`}
      style={{ width, height }}
    />
  );
};

/**
 * CardSkeleton - Card placeholder
 */
export const CardSkeleton = ({ className = '' }) => (
  <div className={`bg-card border border-border rounded-xl p-4 space-y-3 ${className}`}>
    <LoadingSkeleton height="12px" width="60%" />
    <LoadingSkeleton height="20px" width="80%" />
    <LoadingSkeleton height="100px" rounded="lg" />
    <div className="flex gap-2">
      <LoadingSkeleton height="32px" width="80px" rounded="lg" />
      <LoadingSkeleton height="32px" width="80px" rounded="lg" />
    </div>
  </div>
);

/**
 * TableSkeleton - Table placeholder
 */
export const TableSkeleton = ({ rows = 5, columns = 4, className = '' }) => (
  <div className={`space-y-2 ${className}`}>
    <div className="flex gap-4 p-2 border-b border-border">
      {Array.from({ length: columns }).map((_, i) => (
        <LoadingSkeleton key={i} height="16px" width={`${100 / columns - 2}%`} />
      ))}
    </div>
    {Array.from({ length: rows }).map((_, rowIdx) => (
      <div key={rowIdx} className="flex gap-4 p-2">
        {Array.from({ length: columns }).map((_, colIdx) => (
          <LoadingSkeleton key={colIdx} height="14px" width={`${100 / columns - 2}%`} />
        ))}
      </div>
    ))}
  </div>
);

export default LoadingSpinner;
