/**
 * BionicButton - BIONIC TACTICAL Design System
 * Standardized button component with multiple variants
 */

import React from 'react';
import { cn } from '@/lib/utils';

const buttonVariants = {
  // Primary - Gold accent
  primary: cn(
    'bg-[#F5A623] text-black font-bold',
    'hover:bg-[#FFB84D] hover:shadow-[0_0_20px_rgba(245,166,35,0.4)]',
    'active:bg-[#E09000]',
    'disabled:bg-[#F5A623]/50 disabled:cursor-not-allowed'
  ),
  
  // Secondary - Tactical green outline
  secondary: cn(
    'bg-transparent text-[#10B981] border border-[#10B981]/50',
    'hover:bg-[#10B981]/10 hover:border-[#10B981]',
    'active:bg-[#10B981]/20',
    'disabled:opacity-50 disabled:cursor-not-allowed'
  ),
  
  // Ghost - Subtle hover
  ghost: cn(
    'bg-transparent text-gray-400',
    'hover:bg-white/5 hover:text-white',
    'active:bg-white/10',
    'disabled:opacity-50 disabled:cursor-not-allowed'
  ),
  
  // Outline - White border
  outline: cn(
    'bg-transparent text-white border border-white/20',
    'hover:bg-white/5 hover:border-white/40',
    'active:bg-white/10',
    'disabled:opacity-50 disabled:cursor-not-allowed'
  ),
  
  // Danger - Red
  danger: cn(
    'bg-red-600 text-white font-bold',
    'hover:bg-red-700 hover:shadow-[0_0_20px_rgba(239,68,68,0.4)]',
    'active:bg-red-800',
    'disabled:bg-red-600/50 disabled:cursor-not-allowed'
  ),
  
  // Success - Green
  success: cn(
    'bg-emerald-600 text-white font-bold',
    'hover:bg-emerald-700',
    'active:bg-emerald-800',
    'disabled:bg-emerald-600/50 disabled:cursor-not-allowed'
  ),
};

const buttonSizes = {
  xs: 'px-2 py-1 text-xs',
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
  xl: 'px-8 py-4 text-lg',
  icon: 'p-2',
  'icon-sm': 'p-1.5',
  'icon-lg': 'p-3',
};

export const BionicButton = React.forwardRef(({
  children,
  variant = 'primary',
  size = 'md',
  className,
  uppercase = true,
  tracking = true,
  icon: Icon,
  iconPosition = 'left',
  loading = false,
  disabled = false,
  ...props
}, ref) => {
  const isDisabled = disabled || loading;
  
  return (
    <button
      ref={ref}
      className={cn(
        // Base styles
        'inline-flex items-center justify-center gap-2',
        'rounded-sm font-semibold',
        'transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-[#F5A623]/50 focus:ring-offset-2 focus:ring-offset-[#0A0A0A]',
        
        // Variant
        buttonVariants[variant],
        
        // Size
        buttonSizes[size],
        
        // Optional uppercase
        uppercase && 'uppercase',
        
        // Optional tracking
        tracking && 'tracking-wider',
        
        // Custom classes
        className
      )}
      disabled={isDisabled}
      {...props}
    >
      {loading && (
        <svg
          className="animate-spin h-4 w-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      
      {Icon && iconPosition === 'left' && !loading && (
        <Icon className="h-4 w-4" />
      )}
      
      {children}
      
      {Icon && iconPosition === 'right' && !loading && (
        <Icon className="h-4 w-4" />
      )}
    </button>
  );
});

BionicButton.displayName = 'BionicButton';

export default BionicButton;
