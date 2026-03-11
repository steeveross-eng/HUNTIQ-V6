/**
 * CoreModal - V5-ULTIME
 * =====================
 * 
 * Modal de base pour tous les modules.
 */

import React from 'react';
import { cn } from '@/lib/utils';
import { X } from 'lucide-react';

export const CoreModal = ({
  children,
  className,
  isOpen,
  onClose,
  title,
  size = 'md',
}) => {
  if (!isOpen) return null;

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-[90vw]',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />
      <div
        className={cn(
          'relative w-full bg-[#111] border border-white/10 rounded-xl shadow-2xl',
          sizes[size],
          className
        )}
      >
        {title && (
          <div className="flex items-center justify-between p-4 border-b border-white/10">
            <h2 className="text-lg font-semibold text-white">{title}</h2>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        )}
        <div className="p-4">{children}</div>
      </div>
    </div>
  );
};

export default CoreModal;
