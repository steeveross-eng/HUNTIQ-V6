/**
 * CoreCard - V5-ULTIME
 * ====================
 * 
 * Carte de base pour tous les modules.
 */

import React from 'react';
import { cn } from '@/lib/utils';

export const CoreCard = ({
  children,
  className,
  title,
  subtitle,
  icon: Icon,
  actions,
  variant = 'default',
  ...props
}) => {
  const variants = {
    default: 'bg-black/40 border-white/10',
    highlight: 'bg-[#F5A623]/10 border-[#F5A623]/30',
    success: 'bg-green-500/10 border-green-500/30',
    warning: 'bg-yellow-500/10 border-yellow-500/30',
    danger: 'bg-red-500/10 border-red-500/30',
  };

  return (
    <div
      className={cn(
        'rounded-xl border backdrop-blur-sm',
        variants[variant],
        className
      )}
      {...props}
    >
      {(title || actions) && (
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            {Icon && (
              <div className="p-2 rounded-lg bg-white/10">
                <Icon className="h-5 w-5 text-[#F5A623]" />
              </div>
            )}
            <div>
              {title && (
                <h3 className="text-lg font-semibold text-white">{title}</h3>
              )}
              {subtitle && (
                <p className="text-sm text-gray-400">{subtitle}</p>
              )}
            </div>
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
};

export default CoreCard;
