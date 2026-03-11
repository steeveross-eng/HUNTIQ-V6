/**
 * CoreError - V5-ULTIME
 * =====================
 * 
 * Affichage d'erreur pour tous les modules.
 */

import React from 'react';
import { cn } from '@/lib/utils';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import CoreButton from './CoreButton';

export const CoreError = ({
  className,
  title = 'Une erreur est survenue',
  message,
  onRetry,
  variant = 'default',
}) => {
  const variants = {
    default: 'bg-red-500/10 border-red-500/30 text-red-400',
    warning: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400',
    info: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
  };

  return (
    <div
      className={cn(
        'rounded-xl border p-6 flex flex-col items-center text-center',
        variants[variant],
        className
      )}
    >
      <AlertTriangle className="h-12 w-12 mb-4" />
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      {message && <p className="text-sm opacity-80 mb-4">{message}</p>}
      {onRetry && (
        <CoreButton
          variant="outline"
          size="sm"
          icon={RefreshCw}
          onClick={onRetry}
        >
          Réessayer
        </CoreButton>
      )}
    </div>
  );
};

export default CoreError;
