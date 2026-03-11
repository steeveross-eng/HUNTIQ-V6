/**
 * QuotaIndicator - V5-ULTIME Monétisation
 * ========================================
 * 
 * Indicateur visuel de quota/limite.
 */

import React from 'react';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, Infinity, Check } from 'lucide-react';

const QuotaIndicator = ({
  feature,
  label,
  used = 0,
  limit = 0,
  unlimited = false,
  showLabel = true,
  compact = false
}) => {
  const percentage = unlimited ? 100 : limit > 0 ? Math.min((used / limit) * 100, 100) : 0;
  const remaining = unlimited ? Infinity : Math.max(0, limit - used);
  const isLow = !unlimited && remaining <= Math.ceil(limit * 0.2);
  const isDepleted = !unlimited && remaining === 0;

  if (compact) {
    return (
      <div 
        data-testid={`quota-indicator-${feature}`}
        className="flex items-center gap-2"
      >
        {unlimited ? (
          <Badge className="bg-purple-500/20 text-purple-400 border-purple-500">
            <Infinity className="h-3 w-3 mr-1" />
            Illimité
          </Badge>
        ) : isDepleted ? (
          <Badge className="bg-red-500/20 text-red-400 border-red-500">
            <AlertTriangle className="h-3 w-3 mr-1" />
            Épuisé
          </Badge>
        ) : isLow ? (
          <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500">
            {remaining} restant{remaining > 1 ? 's' : ''}
          </Badge>
        ) : (
          <Badge className="bg-green-500/20 text-green-400 border-green-500">
            <Check className="h-3 w-3 mr-1" />
            {remaining}/{limit}
          </Badge>
        )}
      </div>
    );
  }

  return (
    <div 
      data-testid={`quota-indicator-${feature}`}
      className="space-y-2"
    >
      {showLabel && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-400">{label}</span>
          <span className={`text-sm font-medium ${
            isDepleted ? 'text-red-400' : 
            isLow ? 'text-yellow-400' : 
            'text-gray-300'
          }`}>
            {unlimited ? (
              <span className="flex items-center gap-1">
                <Infinity className="h-4 w-4" /> Illimité
              </span>
            ) : (
              `${used}/${limit}`
            )}
          </span>
        </div>
      )}
      
      {!unlimited && (
        <Progress 
          value={percentage} 
          className={`h-2 ${
            isDepleted ? '[&>div]:bg-red-500' : 
            isLow ? '[&>div]:bg-yellow-500' : 
            '[&>div]:bg-green-500'
          }`}
        />
      )}

      {isDepleted && (
        <p className="text-xs text-red-400 flex items-center gap-1">
          <AlertTriangle className="h-3 w-3" />
          Limite atteinte. Passez à Premium pour continuer.
        </p>
      )}
    </div>
  );
};

export default QuotaIndicator;
