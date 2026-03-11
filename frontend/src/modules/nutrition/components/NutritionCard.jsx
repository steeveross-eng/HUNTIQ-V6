/**
 * NutritionCard - Compact nutrition info card
 * Professional design - accepts Lucide icons or React components
 */
import React from 'react';

export const NutritionCard = ({ 
  title, 
  value, 
  unit = '', 
  icon = null,
  IconComponent = null,
  trend = null,
  color = 'emerald'
}) => {
  const colorClasses = {
    emerald: 'text-emerald-400 border-emerald-700 bg-emerald-900/20',
    blue: 'text-blue-400 border-blue-700 bg-blue-900/20',
    amber: 'text-amber-400 border-amber-700 bg-amber-900/20',
    red: 'text-red-400 border-red-700 bg-red-900/20',
    purple: 'text-purple-400 border-purple-700 bg-purple-900/20'
  };
  
  const iconColorClasses = {
    emerald: 'text-emerald-400',
    blue: 'text-blue-400',
    amber: 'text-amber-400',
    red: 'text-red-400',
    purple: 'text-purple-400'
  };

  return (
    <div className={`rounded-lg border p-3 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        {IconComponent ? (
          <IconComponent className={`h-5 w-5 ${iconColorClasses[color]}`} />
        ) : (
          <span className="text-lg">{icon}</span>
        )}
        {trend !== null && (
          <span className={`text-xs ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </span>
        )}
      </div>
      <div className="mt-2">
        <div className="text-2xl font-bold">
          {value}
          {unit && <span className="text-sm ml-1 opacity-70">{unit}</span>}
        </div>
        <div className="text-xs opacity-70 mt-1">{title}</div>
      </div>
    </div>
  );
};

export default NutritionCard;
