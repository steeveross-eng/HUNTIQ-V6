/**
 * CoreButton - V5-ULTIME
 * ======================
 * 
 * Bouton de base pour tous les modules.
 */

import React from 'react';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

const variants = {
  primary: 'bg-[#F5A623] text-black hover:bg-[#F5A623]/90',
  secondary: 'bg-white/10 text-white hover:bg-white/20',
  outline: 'border border-white/20 text-white hover:bg-white/10',
  ghost: 'text-gray-400 hover:text-white hover:bg-white/10',
  danger: 'bg-red-500 text-white hover:bg-red-600',
};

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
};

export const CoreButton = ({
  children,
  className,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  icon: Icon,
  ...props
}) => {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-colors',
        'focus:outline-none focus:ring-2 focus:ring-[#F5A623]/50',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        variants[variant],
        sizes[size],
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : Icon ? (
        <Icon className="h-4 w-4" />
      ) : null}
      {children}
    </button>
  );
};

export default CoreButton;
