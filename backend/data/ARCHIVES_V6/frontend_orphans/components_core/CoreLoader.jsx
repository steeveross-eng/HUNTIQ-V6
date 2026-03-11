/**
 * CoreLoader - V5-ULTIME
 * ======================
 * 
 * Indicateur de chargement pour tous les modules.
 */

import React from 'react';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

export const CoreLoader = ({
  className,
  size = 'md',
  text,
  fullScreen = false,
}) => {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  const content = (
    <div className={cn('flex flex-col items-center justify-center gap-3', className)}>
      <Loader2 className={cn('animate-spin text-[#F5A623]', sizes[size])} />
      {text && <p className="text-sm text-gray-400">{text}</p>}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
        {content}
      </div>
    );
  }

  return content;
};

export default CoreLoader;
