/**
 * BionicDataDisplay - BIONIC TACTICAL Design System
 * Component for displaying data values with monospace typography
 */

import React from 'react';
import { cn } from '@/lib/utils';

// Data value with label
export const BionicDataValue = ({
  label,
  value,
  unit,
  size = 'md',
  variant = 'default',
  trend,
  className,
}) => {
  const sizeClasses = {
    sm: 'text-lg',
    md: 'text-2xl',
    lg: 'text-4xl',
    xl: 'text-5xl',
  };
  
  const variantClasses = {
    default: 'text-white',
    gold: 'text-[#F5A623]',
    tactical: 'text-[#10B981]',
    danger: 'text-red-500',
    muted: 'text-gray-400',
  };
  
  return (
    <div className={cn('space-y-1', className)}>
      {label && (
        <div className="text-xs text-gray-400 uppercase tracking-widest">
          {label}
        </div>
      )}
      <div className="flex items-baseline gap-2">
        <span className={cn(
          'font-mono font-bold',
          sizeClasses[size],
          variantClasses[variant]
        )}>
          {value}
        </span>
        {unit && (
          <span className="text-sm text-gray-500 font-medium">
            {unit}
          </span>
        )}
        {trend && (
          <span className={cn(
            'text-sm font-medium',
            trend > 0 ? 'text-emerald-500' : trend < 0 ? 'text-red-500' : 'text-gray-500'
          )}>
            {trend > 0 ? '+' : ''}{trend}%
          </span>
        )}
      </div>
    </div>
  );
};

// Coordinates display
export const BionicCoordinates = ({
  lat,
  lng,
  altitude,
  accuracy,
  className,
}) => {
  const formatCoord = (value, isLat) => {
    const dir = isLat ? (value >= 0 ? 'N' : 'S') : (value >= 0 ? 'E' : 'W');
    const abs = Math.abs(value);
    const deg = Math.floor(abs);
    const min = Math.floor((abs - deg) * 60);
    const sec = ((abs - deg - min / 60) * 3600).toFixed(1);
    return `${deg}°${min}'${sec}"${dir}`;
  };
  
  return (
    <div className={cn('font-mono text-sm', className)}>
      <div className="flex items-center gap-4">
        <div>
          <span className="text-gray-500">LAT </span>
          <span className="text-white">{formatCoord(lat, true)}</span>
        </div>
        <div>
          <span className="text-gray-500">LNG </span>
          <span className="text-white">{formatCoord(lng, false)}</span>
        </div>
      </div>
      {(altitude !== undefined || accuracy !== undefined) && (
        <div className="flex items-center gap-4 mt-1 text-xs">
          {altitude !== undefined && (
            <div>
              <span className="text-gray-500">ALT </span>
              <span className="text-gray-300">{altitude.toFixed(0)}m</span>
            </div>
          )}
          {accuracy !== undefined && (
            <div>
              <span className="text-gray-500">±</span>
              <span className="text-gray-300">{accuracy.toFixed(0)}m</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Score display with circular progress
export const BionicScore = ({
  value,
  max = 100,
  label,
  size = 'md',
  showValue = true,
  className,
}) => {
  const percentage = (value / max) * 100;
  
  const sizes = {
    sm: { size: 48, stroke: 4, fontSize: 'text-sm' },
    md: { size: 64, stroke: 5, fontSize: 'text-lg' },
    lg: { size: 96, stroke: 6, fontSize: 'text-2xl' },
  };
  
  const { size: svgSize, stroke, fontSize } = sizes[size];
  const radius = (svgSize - stroke) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percentage / 100) * circumference;
  
  // Color based on score
  const getColor = () => {
    if (percentage >= 80) return '#22C55E';
    if (percentage >= 60) return '#F5A623';
    if (percentage >= 40) return '#F59E0B';
    return '#EF4444';
  };
  
  return (
    <div className={cn('flex flex-col items-center', className)}>
      <div className="relative" style={{ width: svgSize, height: svgSize }}>
        <svg className="transform -rotate-90" width={svgSize} height={svgSize}>
          {/* Background circle */}
          <circle
            cx={svgSize / 2}
            cy={svgSize / 2}
            r={radius}
            fill="none"
            stroke="#262626"
            strokeWidth={stroke}
          />
          {/* Progress circle */}
          <circle
            cx={svgSize / 2}
            cy={svgSize / 2}
            r={radius}
            fill="none"
            stroke={getColor()}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-500"
          />
        </svg>
        {showValue && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={cn('font-mono font-bold text-white', fontSize)}>
              {value}
            </span>
          </div>
        )}
      </div>
      {label && (
        <div className="text-xs text-gray-400 uppercase tracking-wider mt-2">
          {label}
        </div>
      )}
    </div>
  );
};

// Status indicator
export const BionicStatus = ({
  status,
  label,
  pulse = false,
  className,
}) => {
  const statusConfig = {
    active: { color: '#22C55E', label: 'Actif' },
    inactive: { color: '#6B7280', label: 'Inactif' },
    warning: { color: '#F59E0B', label: 'Attention' },
    danger: { color: '#EF4444', label: 'Danger' },
    processing: { color: '#3B82F6', label: 'En cours' },
  };
  
  const config = statusConfig[status] || statusConfig.inactive;
  
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="relative">
        <div
          className={cn(
            'w-2 h-2 rounded-full',
            pulse && 'animate-pulse'
          )}
          style={{ backgroundColor: config.color }}
        />
        {pulse && (
          <div
            className="absolute inset-0 w-2 h-2 rounded-full animate-ping"
            style={{ backgroundColor: config.color, opacity: 0.5 }}
          />
        )}
      </div>
      <span className="text-sm text-gray-400">
        {label || config.label}
      </span>
    </div>
  );
};

// Stats grid
export const BionicStatsGrid = ({
  stats,
  columns = 4,
  className,
}) => {
  return (
    <div
      className={cn(
        'grid gap-4',
        `grid-cols-2 md:grid-cols-${columns}`,
        className
      )}
    >
      {stats.map((stat, index) => (
        <div
          key={index}
          className={cn(
            'bg-black/40 rounded-md p-4',
            'border border-white/5'
          )}
        >
          <BionicDataValue
            label={stat.label}
            value={stat.value}
            unit={stat.unit}
            trend={stat.trend}
            variant={stat.variant}
            size="md"
          />
        </div>
      ))}
    </div>
  );
};

export default {
  BionicDataValue,
  BionicCoordinates,
  BionicScore,
  BionicStatus,
  BionicStatsGrid,
};
