/**
 * AlertToast - Alert notification toast
 */
import React, { useEffect, useState } from 'react';
import { Zap, MapPin, X } from 'lucide-react';

export const AlertToast = ({ alert, onDismiss }) => {
  const [visible, setVisible] = useState(true);
  
  // Auto-dismiss after duration
  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(onDismiss, 300); // Wait for fade out
    }, alert.duration_ms || 5000);
    
    return () => clearTimeout(timer);
  }, [alert.duration_ms, onDismiss]);
  
  // Priority colors
  const priorityColors = {
    low: 'border-slate-500 bg-slate-800',
    medium: 'border-blue-500 bg-blue-900/50',
    high: 'border-amber-500 bg-amber-900/50',
    critical: 'border-red-500 bg-red-900/50'
  };
  
  const priorityTextColors = {
    low: 'text-slate-400',
    medium: 'text-blue-400',
    high: 'text-amber-400',
    critical: 'text-red-400'
  };
  
  return (
    <div 
      className={`
        rounded-lg border-l-4 px-4 py-3 shadow-lg
        transition-all duration-300
        ${priorityColors[alert.priority] || priorityColors.medium}
        ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'}
      `}
      onClick={onDismiss}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <Zap className="h-5 w-5 text-amber-400" />
        
        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className={`font-medium ${priorityTextColors[alert.priority] || 'text-white'}`}>
            {alert.title}
          </div>
          <div className="text-sm text-slate-300 mt-0.5">
            {alert.message}
          </div>
          
          {/* Distance info */}
          {alert.distance_m && (
            <div className="text-xs text-slate-400 mt-1 flex items-center gap-1">
              <MapPin className="h-3 w-3" /> {Math.round(alert.distance_m)}m - Cap {Math.round(alert.bearing)}°
            </div>
          )}
        </div>
        
        {/* Dismiss button */}
        <button 
          className="text-slate-400 hover:text-white transition-colors"
          onClick={(e) => { e.stopPropagation(); onDismiss(); }}
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

export default AlertToast;
