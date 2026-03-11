/**
 * CoreLayout - V5-ULTIME
 * ======================
 * 
 * Layout de base pour tous les modules.
 * Seul layout autorisé à être utilisé par les modules.
 */

import React from 'react';
import { cn } from '@/lib/utils';

export const CoreLayout = ({ 
  children, 
  className,
  title,
  subtitle,
  actions,
  fullWidth = false 
}) => {
  return (
    <div className={cn(
      'min-h-screen bg-gradient-to-br from-[#0a0a0a] via-[#111] to-[#0a0a0a]',
      className
    )}>
      <div className={cn(
        'mx-auto py-6',
        fullWidth ? 'w-full px-4' : 'max-w-7xl px-4 sm:px-6 lg:px-8'
      )}>
        {(title || actions) && (
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
            <div>
              {title && (
                <h1 className="text-2xl sm:text-3xl font-bold text-white">
                  {title}
                </h1>
              )}
              {subtitle && (
                <p className="mt-1 text-sm text-gray-400">
                  {subtitle}
                </p>
              )}
            </div>
            {actions && (
              <div className="flex items-center gap-3">
                {actions}
              </div>
            )}
          </div>
        )}
        {children}
      </div>
    </div>
  );
};

export default CoreLayout;
